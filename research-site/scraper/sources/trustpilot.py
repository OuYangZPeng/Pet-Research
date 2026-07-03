"""Trustpilot review scraper via Playwright (stealth).

Trustpilot is fronted by Cloudflare and rejects plain httpx requests with a 403
'Blocked by network policy' page. We use Playwright with a real Chromium binary
plus a few well-known anti-detection touches (UA, viewport, navigator overrides,
en-US locale) to render the review page and extract reviews from:

  1. JSON-LD `<script type="application/ld+json">` blocks (structured, preferred)
  2. The visible `<article>` cards (fallback when JSON-LD is missing/truncated)

Returns RawReview-shaped dicts so it slots straight into the existing pipeline.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Optional

from bs4 import BeautifulSoup


_PW_LOCK = asyncio.Lock()


# Common Cloudflare-friendly fingerprint we'll re-use across calls.
_STEALTH_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
)
_STEALTH_SCRIPT = """
// Hide the obvious automation tells.
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
window.chrome = { runtime: {} };
"""


def _parse_rating(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"([0-9]+(?:\.[0-9])?)", text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _from_jsonld(html: str, domain: str) -> list[dict]:
    """Trustpilot embeds an aggregate plus a `review` array in JSON-LD."""
    out: list[dict] = []
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            blob = json.loads(tag.string or "")
        except Exception:
            continue
        blobs = blob if isinstance(blob, list) else [blob]
        for b in blobs:
            # Trustpilot's review array sits under "@graph"/"review" depending on
            # page version; flatten any "review" or "reviews" key we find.
            graphs = b.get("@graph") if isinstance(b, dict) else None
            sources = graphs if graphs else ([b] if isinstance(b, dict) else [])
            for s in sources:
                if not isinstance(s, dict):
                    continue
                rvs = s.get("review") or s.get("reviews") or []
                if isinstance(rvs, dict):
                    rvs = [rvs]
                for rv in rvs:
                    if not isinstance(rv, dict):
                        continue
                    body = rv.get("reviewBody") or rv.get("description") or ""
                    if not body:
                        continue
                    rating_val = None
                    rating_obj = rv.get("reviewRating")
                    if isinstance(rating_obj, dict):
                        rating_val = rating_obj.get("ratingValue")
                        try:
                            rating_val = float(rating_val) if rating_val else None
                        except (TypeError, ValueError):
                            rating_val = None
                    author = rv.get("author") or {}
                    if isinstance(author, dict):
                        author = author.get("name")
                    out.append(
                        {
                            "channel": "trustpilot",
                            "productId": domain,
                            "title": rv.get("headline") or rv.get("name"),
                            "body": body.strip(),
                            "rating": rating_val,
                            "verified": True,
                            "helpful": None,
                            "date": rv.get("datePublished"),
                            "reviewer": author if isinstance(author, str) else None,
                            "url": rv.get("url"),
                        }
                    )
    return out


def _from_articles(html: str, domain: str) -> list[dict]:
    """Fallback: pull from rendered review article cards."""
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []
    cards = soup.select("article[data-service-review-card-paper], article[itemprop='review']")
    if not cards:
        cards = soup.select("article")
    for c in cards:
        body_el = c.select_one(
            "[data-service-review-text-typography], "
            "p[data-service-review-text-typography], "
            "[itemprop='reviewBody'], p"
        )
        if not body_el:
            continue
        body = body_el.get_text(" ", strip=True)
        if not body or len(body) < 8:
            continue
        title_el = c.select_one(
            "[data-service-review-title-typography], h2, [itemprop='headline']"
        )
        rating = None
        img = c.select_one("img[alt*='Rated']")
        if img:
            rating = _parse_rating(img.get("alt", "")[6:])
        if rating is None:
            sr = c.select_one("[data-service-review-rating]")
            if sr:
                rating = _parse_rating(sr.get("data-service-review-rating", "") or "")
        author_el = c.select_one(
            "[data-consumer-name-typography], [itemprop='author']"
        )
        date_el = c.select_one("time")
        out.append(
            {
                "channel": "trustpilot",
                "productId": domain,
                "title": title_el.get_text(strip=True) if title_el else None,
                "body": body,
                "rating": rating,
                "verified": True,
                "helpful": None,
                "date": date_el.get("datetime") if date_el else None,
                "reviewer": author_el.get_text(strip=True) if author_el else None,
                "url": None,
            }
        )
    return out


async def fetch_html(
    domain: str,
    *,
    pages: int = 2,
    sort: str = "recency",
    headless: bool = True,
) -> str:
    """Render Trustpilot review pages and concatenate the HTML. Page 1 + page 2
    by default ≈ 40 reviews."""
    from playwright.async_api import async_playwright

    async with _PW_LOCK:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent=_STEALTH_UA,
                locale="en-US",
                viewport={"width": 1440, "height": 900},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            await context.add_init_script(_STEALTH_SCRIPT)
            page = await context.new_page()

            chunks: list[str] = []
            for page_idx in range(1, pages + 1):
                url = f"https://www.trustpilot.com/review/{domain}"
                params = {"languages": "en", "sort": sort}
                if page_idx > 1:
                    params["page"] = str(page_idx)
                qs = "&".join(f"{k}={v}" for k, v in params.items())
                try:
                    await page.goto(
                        f"{url}?{qs}",
                        wait_until="domcontentloaded",
                        timeout=45_000,
                    )
                    # Wait for the review list to render (or timeout silently).
                    try:
                        await page.wait_for_selector("article", timeout=10_000)
                    except Exception:
                        pass
                    chunks.append(await page.content())
                except Exception:
                    break
            await browser.close()
            return "\n<!-- PAGE BREAK -->\n".join(chunks)


async def fetch(domain: str, *, max_reviews: int = 40) -> list[dict]:
    """Fetch and parse Trustpilot reviews for a brand domain.

    Examples:
        await fetch("thefarmersdog.com")
        await fetch("barkbox.com")
    """
    html = await fetch_html(domain, pages=2)
    if not html:
        return []

    reviews = _from_jsonld(html, domain)
    if not reviews:
        reviews = _from_articles(html, domain)

    # Dedupe by body + author
    seen: set[tuple] = set()
    out: list[dict] = []
    for r in reviews:
        key = ((r.get("body") or "")[:120], (r.get("reviewer") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= max_reviews:
            break
    return out


if __name__ == "__main__":  # pragma: no cover
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m sources.trustpilot <domain> [--pages N] [--headed]")
        sys.exit(1)
    args = sys.argv[1:]
    headed = "--headed" in args
    pages = 2
    if "--pages" in args:
        i = args.index("--pages")
        pages = int(args[i + 1])
    domain = args[0]

    async def main() -> None:
        html = await fetch_html(domain, pages=pages, headless=not headed)
        reviews = _from_jsonld(html, domain) or _from_articles(html, domain)
        print(f"Domain: {domain}")
        print(f"Found {len(reviews)} reviews")
        for r in reviews[:5]:
            stars = "★" * int(r.get("rating") or 0)
            title = (r.get("title") or "").strip()
            body = (r.get("body") or "").strip()
            print(f"\n{stars}  {title}")
            print(f"   by {r.get('reviewer')} on {r.get('date')}")
            print(f"   {body[:220]}…")

    asyncio.run(main())
