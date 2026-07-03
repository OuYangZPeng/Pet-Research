"""Rainforest API adapter — fetches real Amazon product data without PA-API.

Sign up at https://rainforestapi.com to get a free key (100 requests / month).
Set `RAINFOREST_API_KEY` in your .env.

Two endpoints we use:
  - `type=search`  — find an ASIN by product title (1 credit / call)
  - `type=product` — fetch rating + ratings_total + buybox price + BSR (1 credit / call)

Public entry points:
  - `search_by_title(title)`      → top ASIN
  - `fetch_product(asin)`         → dict with rating/reviews/price/bsr
  - `enrich(competitors)`         → populate rating/reviews on Competitor rows
  - CLI: `python amazon_rainforest.py product B0999QB1TG`
         `python amazon_rainforest.py search "TOTO Drake CST776CSFG"`
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from ._schema import now_iso
from ._utils import http_client

API = "https://api.rainforestapi.com/request"


def _key() -> Optional[str]:
    k = os.getenv("RAINFOREST_API_KEY")
    return k if k and k.strip() else None


async def _call(params: dict) -> Optional[dict]:
    key = _key()
    if not key:
        return None
    full = {"api_key": key, "amazon_domain": "amazon.com", **params}
    async with http_client(timeout=30) as c:
        try:
            r = await c.get(API, params=full)
        except Exception:
            return None
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


def _normalise_review(asin: str, r: dict) -> dict:
    date_field = r.get("date")
    if isinstance(date_field, dict):
        date_val = date_field.get("utc") or date_field.get("raw")
    else:
        date_val = date_field
    return {
        "channel": "amazon",
        "productId": asin,
        "title": r.get("title"),
        "body": r.get("body") or "",
        "rating": r.get("rating"),
        "verified": r.get("verified_purchase"),
        "helpful": (r.get("helpful_votes") or 0),
        "date": date_val,
        "reviewer": (r.get("profile") or {}).get("name") if isinstance(r.get("profile"), dict) else None,
        "url": r.get("link"),
    }


async def _fetch_reviews_via_product(asin: str) -> list[dict]:
    """Fallback path: type=product returns up to 10 top_reviews for 1 credit.
    Used when the dedicated /reviews endpoint is 503 / unavailable.
    """
    data = await _call({"type": "product", "asin": asin})
    if not data:
        return []
    p = data.get("product") or {}
    reviews = p.get("top_reviews") or []
    return [_normalise_review(asin, r) for r in reviews]


async def fetch_reviews(asin: str, *, pages: int = 3, filter_by_star: Optional[str] = None) -> list[dict]:
    """Fetch reviews for an ASIN.

    Primary path: /request?type=reviews — 10 reviews per page, 1 credit each.
    Fallback:     /request?type=product — 10 top_reviews bundled for 1 credit,
                  used when the reviews endpoint returns 503 / empty (Rainforest
                  has been known to take that endpoint offline temporarily).
    """
    out: list[dict] = []
    primary_failed_on_first_page = False
    for page in range(1, pages + 1):
        params = {
            "type": "reviews",
            "asin": asin,
            "review_stars": filter_by_star or "all_stars",
            "sort_by": "helpful",
            "page": page,
        }
        data = await _call(params)
        if data is None and page == 1:
            primary_failed_on_first_page = True
            break
        if not data:
            break
        reviews = data.get("reviews") or []
        if not reviews:
            break
        out.extend(_normalise_review(asin, r) for r in reviews)
        if len(reviews) < 10:
            break

    if not out and primary_failed_on_first_page:
        out = await _fetch_reviews_via_product(asin)
    return out


async def search_by_title(title: str) -> Optional[str]:
    """Return the top ASIN for a free-text product title, or None."""
    data = await _call({"type": "search", "search_term": title})
    if not data:
        return None
    results = data.get("search_results") or []
    for r in results:
        asin = r.get("asin")
        if asin:
            return asin
    return None


async def fetch_product(asin: str) -> Optional[dict]:
    """Fetch a single product. Returns normalised fields or None on failure."""
    data = await _call({"type": "product", "asin": asin})
    if not data:
        return None
    p = data.get("product") or {}
    bsr_rank = None
    for entry in p.get("bestsellers_rank") or []:
        if isinstance(entry, dict) and "rank" in entry:
            bsr_rank = entry["rank"]
            break
    buybox = p.get("buybox_winner") or {}
    price_val = (buybox.get("price") or {}).get("value")
    return {
        "asin": asin,
        "title": p.get("title"),
        "brand": p.get("brand"),
        "rating": p.get("rating"),
        "reviews": p.get("ratings_total"),
        "price": price_val,
        "bsrRank": bsr_rank,
        "url": p.get("link") or f"https://www.amazon.com/dp/{asin}",
    }


async def enrich(competitors: list[dict], *, only_amazon: bool = True) -> list[dict]:
    """Fill rating / reviews / live price on existing Competitor rows.

    Strategy:
      - Skip rows without `platform == "Amazon"` if only_amazon=True
      - If row has `asin`, fetch directly (1 credit)
      - Otherwise resolve ASIN by title (2 credits total)
      - On success: clear `rating`/`reviews` from `pendingFields`

    No-op (returns input unchanged) when RAINFOREST_API_KEY is not set.
    """
    if not _key():
        return competitors

    out = []
    for c in competitors:
        if only_amazon and c.get("platform") != "Amazon":
            out.append(c)
            continue

        asin = c.get("asin")
        if not asin:
            asin = await search_by_title(c.get("product") or "")
        if not asin:
            out.append(c)
            continue

        info = await fetch_product(asin)
        if not info:
            out.append(c)
            continue

        c = dict(c)
        c["asin"] = asin
        if info.get("rating") is not None:
            c["rating"] = float(info["rating"])
        if info.get("reviews") is not None:
            c["reviews"] = int(info["reviews"])
        if info.get("bsrRank") and not c.get("bsrRank"):
            c["bsrRank"] = int(info["bsrRank"])
        if info.get("price"):
            price = c.get("price") or {}
            price["current"] = float(info["price"])
            c["price"] = price
        c["pendingFields"] = [
            f for f in (c.get("pendingFields") or []) if f not in ("rating", "reviews")
        ] or None
        c["source"] = {
            "label": "Rainforest API (Amazon)",
            "url": info.get("url") or f"https://www.amazon.com/dp/{asin}",
            "fetchedAt": now_iso(),
        }
        out.append(c)
    return out


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    from dotenv import load_dotenv

    load_dotenv()

    if len(sys.argv) < 3:
        print("Usage: python -m sources.amazon_rainforest [product ASIN | search TITLE | reviews ASIN [pages]]")
        sys.exit(1)
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "product":
        print(json.dumps(asyncio.run(fetch_product(arg)), indent=2, ensure_ascii=False))
    elif cmd == "search":
        print(json.dumps({"asin": asyncio.run(search_by_title(arg))}, indent=2))
    elif cmd == "reviews":
        pages = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        print(json.dumps(asyncio.run(fetch_reviews(arg, pages=pages)), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
