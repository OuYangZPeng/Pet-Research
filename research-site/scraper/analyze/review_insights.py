"""Aggregate raw reviews → structured ReviewInsight per SKU.

Two operating modes (in priority order):

  1. **Cursor SDK auto** (cron-friendly, default when `CURSOR_API_KEY` is set):
     Uses your existing Cursor subscription via the `cursor-sdk` Python
     package (`Agent.prompt(...)` one-shot pattern). No extra spend, no
     third-party LLM key, works from anywhere.

     Get your key:    https://cursor.com/dashboard/integrations
     Then set in .env: CURSOR_API_KEY=cursor_xxxxx

  2. **Cursor IDE manual fallback** (no API key needed):
     Writes the raw reviews + an LLM prompt into a single manifest file at
     `scraper/_insights_pending.md`. Open Cursor IDE and ask the agent to
     process the manifest; the agent reads it, generates structured insight
     JSON, and writes them to `web/public/data/review_insights/<sku>.json`.

Both modes use the same prompt and output schema, so files are interchangeable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from sources._schema import (
    Category,
    InsightTheme,
    RawReview,
    ReviewInsight,
    SourceRef,
    now_iso,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = (ROOT / "../web/public/data/reviews_raw").resolve()
INSIGHT_DIR = (ROOT / "../web/public/data/review_insights").resolve()
MANIFEST = (ROOT / "_insights_pending.md").resolve()


SYSTEM_PROMPT = """You are a senior product analyst summarising dog-food and dog-treat customer
reviews for cross-border e-commerce buyers. Output STRICT JSON only, matching this schema:

{
  "pros": [
    {
      "theme":      "<short English noun phrase, e.g. 'High palatability'>",
      "themeZh":    "<short Chinese, e.g. '适口性高'>",
      "count":      <int — how many of the supplied reviews back this theme>,
      "quote":      "<verbatim quote from one of the supplied reviews>",
      "quoteRating":<float | null>,
      "quoteVerified":<bool | null>,
      "quoteUrl":   "<url | null>",
      "channels":   [<lowercase channel name(s) e.g. 'amazon','trustpilot','reddit'>]
    }
  ],
  "cons": [...same shape...]
}

Rules:
- Cluster semantically equivalent phrases ("dogs love it" / "finished every bowl" → one theme).
- Output at most 6 pros and 6 cons; sort each list by count descending.
- Quote must be a true verbatim substring of a supplied review body (no paraphrasing).
- Themes must be specific and actionable for an e-commerce buyer; avoid generic words like "great", "good".
- Prefer pet-food concerns such as palatability, digestive tolerance, allergens, freshness, pack size, portioning, subscription friction, and shipping damage when supported by the reviews.
- If there are fewer than 3 reviews total, still return JSON but with whatever signal exists.
"""


def render_user_prompt(sku: str, brand: str, product: str, reviews: list[dict]) -> str:
    lines = [
        f"SKU: {sku}",
        f"Brand: {brand}",
        f"Product: {product}",
        f"Reviews: {len(reviews)}",
        "",
        "REVIEWS (one per block):",
    ]
    for i, r in enumerate(reviews, 1):
        rating = r.get("rating")
        verified = r.get("verified")
        ch = r.get("channel")
        body = (r.get("body") or "").strip()
        lines.append(f"\n[#{i}] channel={ch} rating={rating} verified={verified}")
        lines.append(f"URL: {r.get('url') or '—'}")
        lines.append(body[:1500])
    return "\n".join(lines)


def _slug(s: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:64]


def _write_manifest(jobs: list[dict]) -> None:
    """Generate _insights_pending.md so Cursor can batch-process all SKUs."""
    out_path = MANIFEST
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pending review insights — Cursor processing manifest",
        "",
        "**You (Cursor agent) should read each block below and, for each SKU,**",
        "write a file at `web/public/data/review_insights/<sku>.json` matching",
        "the `ReviewInsight` schema in `scraper/sources/_schema.py`.",
        "",
        "Use the same prompt rules as `SYSTEM_PROMPT` in",
        "`scraper/analyze/review_insights.py` — cluster themes, max 6 pros/cons,",
        "verbatim quotes only, sort by count desc.",
        "",
        f"Total SKUs queued: **{len(jobs)}**",
        "",
        "---",
        "",
    ]
    for job in jobs:
        lines.append(f"## {job['brand']} — {job['product']}")
        lines.append(f"- sku: `{job['sku']}`")
        lines.append(f"- category: `{job['category']}`")
        lines.append(f"- asin: `{job.get('asin') or '—'}`")
        lines.append(f"- raw file: `web/public/data/reviews_raw/{job['raw_file']}`")
        lines.append(f"- target file: `web/public/data/review_insights/{job['sku']}.json`")
        lines.append(f"- channels present: {sorted(set(r.get('channel') for r in job['reviews']))}")
        lines.append(f"- review count: {len(job['reviews'])}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _extract_json(text: str) -> Optional[dict]:
    """Pull the first JSON object out of LLM output (handles fences, prose preamble)."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].lstrip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _try_cursor(sku: str, brand: str, product: str, reviews: list[dict]) -> Optional[dict]:
    """Auto-summarise reviews via Cursor SDK (one-shot Agent.prompt pattern).

    Uses your Cursor subscription — no separate LLM provider key needed.
    Model defaults to `composer-2.5`; override via `CURSOR_MODEL` env var.
    """
    key = os.getenv("CURSOR_API_KEY")
    if not key:
        return None
    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions, CursorAgentError  # type: ignore[import]
    except Exception:
        print(f"  [cursor] {sku}: cursor-sdk not installed; pip install cursor-sdk")
        return None

    model = os.getenv("CURSOR_MODEL", "composer-2.5")
    user_prompt = render_user_prompt(sku, brand, product, reviews)
    combined = (
        SYSTEM_PROMPT
        + "\n\n---\n\n"
        + "Below is the raw input. Do NOT use any tools, do NOT read or write any files, "
        + "do NOT search the web. Respond with the JSON object only — no prose, no code fences.\n\n"
        + user_prompt
    )
    try:
        result = Agent.prompt(
            combined,
            AgentOptions(
                api_key=key,
                model=model,
                local=LocalAgentOptions(cwd=str(ROOT)),
            ),
        )
    except CursorAgentError as e:
        print(f"  [cursor] {sku}: startup failed ({e.message[:120]}); falling back to manifest mode.")
        return None
    except Exception as e:
        print(f"  [cursor] {sku}: {type(e).__name__}: {str(e)[:120]}; falling back to manifest mode.")
        return None

    if getattr(result, "status", None) == "error":
        print(f"  [cursor] {sku}: run errored; falling back to manifest mode.")
        return None
    text = getattr(result, "result", None) or ""
    parsed = _extract_json(text)
    if not parsed:
        print(f"  [cursor] {sku}: no JSON in response; falling back to manifest mode.")
        return None
    return parsed


def _build_insight(
    *,
    sku: str,
    brand: str,
    product: str,
    product_zh: Optional[str],
    category: Category,
    asin: Optional[str],
    reviews: list[dict],
    pros_cons: dict,
    generator: str,
) -> dict:
    channel_breakdown: dict[str, int] = {}
    for r in reviews:
        ch = r.get("channel") or "unknown"
        channel_breakdown[ch] = channel_breakdown.get(ch, 0) + 1

    rated = [r.get("rating") for r in reviews if isinstance(r.get("rating"), (int, float))]
    avg = round(sum(rated) / len(rated), 2) if rated else None

    sources_used: list[SourceRef] = []
    seen_urls: set[str] = set()
    for r in reviews:
        url = r.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources_used.append(
            SourceRef(label=f"{r.get('channel','?')} review", url=url, fetchedAt=now_iso())
        )
        if len(sources_used) >= 6:
            break

    insight = ReviewInsight(
        sku=sku,
        brand=brand,
        product=product,
        productZh=product_zh,
        category=category,
        asin=asin,
        totalReviews=len(reviews),
        averageRating=avg,
        pros=[InsightTheme.model_validate(p) for p in (pros_cons.get("pros") or [])],
        cons=[InsightTheme.model_validate(c) for c in (pros_cons.get("cons") or [])],
        channelBreakdown=channel_breakdown,
        generator=generator,  # type: ignore[arg-type]
        lastUpdated=now_iso(),
        sourcesUsed=sources_used,
    )
    return insight.model_dump(exclude_none=True)


def process(jobs: list[dict]) -> tuple[int, int]:
    """Process one or more jobs. Returns (written, queued_to_manifest)."""
    INSIGHT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    pending: list[dict] = []
    for job in jobs:
        out = _try_cursor(job["sku"], job["brand"], job["product"], job["reviews"])
        if out:
            insight = _build_insight(
                sku=job["sku"],
                brand=job["brand"],
                product=job["product"],
                product_zh=job.get("productZh"),
                category=job["category"],
                asin=job.get("asin"),
                reviews=job["reviews"],
                pros_cons=out,
                generator="cursor",
            )
            (INSIGHT_DIR / f"{job['sku']}.json").write_text(
                json.dumps(insight, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            written += 1
        else:
            pending.append(job)
    if pending:
        _write_manifest(pending)
    return written, len(pending)


def build_job(
    *,
    sku: str,
    brand: str,
    product: str,
    product_zh: Optional[str],
    category: Category,
    asin: Optional[str],
    reviews: list[dict],
) -> dict:
    """Wrap a SKU + its raw reviews in the job-dict shape `process` expects."""
    raw_file = f"{sku}.json"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / raw_file).write_text(
        json.dumps([RawReview.model_validate(r).model_dump(exclude_none=True) for r in reviews], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "sku": sku,
        "brand": brand,
        "product": product,
        "productZh": product_zh,
        "category": category,
        "asin": asin,
        "raw_file": raw_file,
        "reviews": reviews,
    }


__all__ = ["process", "build_job", "render_user_prompt", "SYSTEM_PROMPT"]
