"""Top-level orchestrator for the pet review-insights pipeline.

For each competitor in the dog-food / dog-treat JSONs:
  1. Fetch up to 30 Amazon reviews via Rainforest (3 pages = 3 credits).
  2. Add DTC reviews if the competitor's brand has a DTC handler.
  3. Add ~5–15 Reddit discussion items keyed by `<brand> <product>`.
  4. Write raw reviews to web/public/data/reviews_raw/<sku>.json.
  5. Either:
     a. If CURSOR_API_KEY is set → call Cursor SDK (Agent.prompt) and write insight JSON directly.
     b. Otherwise → append a manifest entry; user processes it via Cursor IDE chat.

Usage:
    python refresh_reviews.py                            # all categories
    python refresh_reviews.py --category dog-food        # one category
    python refresh_reviews.py --limit 3                  # spot-check
    python refresh_reviews.py --skus blue-buffalo-life-protection-adult greenies-regular-dental
    python refresh_reviews.py --skip-amazon              # only DTC + Reddit (0 credits)

Credit budget:
    Amazon — 3 credits per SKU (3 pages × 1 credit)
    DTC    — free
    Reddit — free
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from analyze import review_insights
from sources import amazon_rainforest, dtc_reviews, reddit_threads

ROOT = Path(__file__).resolve().parent
DATA_DIR = (ROOT / "../web/public/data").resolve()
INSIGHT_DIR = (DATA_DIR / "review_insights").resolve()
CATEGORIES = ("dog-food", "dog-treats")
console = Console()


def _load_category(cat: str) -> dict:
    return json.loads((DATA_DIR / f"{cat}.json").read_text(encoding="utf-8"))


async def collect_for_competitor(c: dict, category: str) -> Optional[dict]:
    sku = c.get("id")
    brand = c.get("brand", "")
    product = c.get("product", "")
    product_zh = c.get("productZh")
    asin = c.get("asin")

    all_reviews: list[dict] = []

    # Try Amazon for all SKUs that have a Rainforest key. Even subscription-led
    # pet brands often have a partial Amazon footprint, and that's frequently the
    # only structured public review surface we can normalise cheaply.
    if os.getenv("RAINFOREST_API_KEY"):
        if not asin:
            console.print(f"  [dim]→ search ASIN for {brand} {product[:40]}…[/dim]")
            asin = await amazon_rainforest.search_by_title(f"{brand} {product}")
        if asin:
            console.print(f"  [dim]→ amazon reviews × 3 pages for {asin}…[/dim]")
            amazon_rows = await amazon_rainforest.fetch_reviews(asin, pages=3)
            all_reviews.extend(amazon_rows)

    brand_key = brand.lower()
    if brand_key in dtc_reviews.DTC_HANDLERS:
        console.print(f"  [dim]→ DTC reviews for brand={brand_key}…[/dim]")
        dtc_rows = await dtc_reviews.fetch(brand_key, sku_id=sku, product_handle=sku)
        all_reviews.extend(dtc_rows)

    query = f"{brand} {product.split('(')[0].strip()}"[:80]
    console.print(f"  [dim]→ reddit threads for {query!r}…[/dim]")
    reddit_rows = await reddit_threads.fetch(query, limit=3)
    all_reviews.extend(reddit_rows)

    if not all_reviews:
        return None

    return review_insights.build_job(
        sku=sku,
        brand=brand,
        product=product,
        product_zh=product_zh,
        category=category,  # type: ignore[arg-type]
        asin=asin,
        reviews=all_reviews,
    )


def render_summary(jobs: list[dict]) -> None:
    table = Table(title="Reviews collected (raw, pre-LLM)", show_lines=False)
    table.add_column("sku", style="cyan", no_wrap=True)
    table.add_column("brand")
    table.add_column("amazon", justify="right")
    table.add_column("DTC", justify="right")
    table.add_column("reddit", justify="right")
    table.add_column("total", justify="right", style="bold")

    for j in jobs:
        counts = {"amazon": 0, "reddit": 0}
        dtc = 0
        for r in j["reviews"]:
            ch = r.get("channel")
            if ch == "amazon":
                counts["amazon"] += 1
            elif ch == "reddit":
                counts["reddit"] += 1
            else:
                dtc += 1
        table.add_row(
            j["sku"][:30],
            j["brand"],
            str(counts["amazon"]),
            str(dtc),
            str(counts["reddit"]),
            str(len(j["reviews"])),
        )
    console.print(table)


async def main(args: argparse.Namespace) -> int:
    load_dotenv()
    cats = [args.category] if args.category else list(CATEGORIES)
    sku_filter = set(args.skus) if args.skus else None

    jobs: list[dict] = []
    skipped: list[str] = []
    for cat in cats:
        payload = _load_category(cat)
        competitors = payload.get("competitors", [])
        if sku_filter:
            competitors = [c for c in competitors if c.get("id") in sku_filter]
        if args.skip_amazon:
            competitors = [c for c in competitors if c.get("platform") != "Amazon"]
        if not args.force:
            before = len(competitors)
            competitors = [
                c for c in competitors if not (INSIGHT_DIR / f"{c.get('id')}.json").exists()
            ]
            removed = before - len(competitors)
            if removed:
                skipped.extend([c.get("id", "?") for c in payload.get("competitors", []) if (INSIGHT_DIR / f"{c.get('id')}.json").exists()][:removed])
        if args.limit:
            competitors = competitors[: args.limit]

        console.print(f"\n[bold cyan]→ {cat}: {len(competitors)} competitor(s)[/bold cyan]")
        for c in competitors:
            console.print(f"[yellow]· {c.get('brand')} — {c.get('product')[:60]}[/yellow]")
            job = await collect_for_competitor(c, cat)
            if job:
                jobs.append(job)

    if skipped:
        console.print(
            f"\n[dim]Skipped {len(skipped)} SKU(s) that already have insight files. Use --force to re-process.[/dim]"
        )

    if not jobs:
        console.print("[yellow]No new SKUs to process.[/yellow]")
        return 0

    render_summary(jobs)

    console.print("\n[bold cyan]→ generating insights…[/bold cyan]")
    written, queued = review_insights.process(jobs)

    if written:
        console.print(f"[green]Wrote {written} insight file(s) via Cursor SDK.[/green]")
    if queued:
        console.print(
            f"[yellow]Queued {queued} SKU(s) to "
            f"`scraper/_insights_pending.md` for Cursor-in-the-loop processing.[/yellow]"
        )
        console.print(
            "[yellow]Open Cursor and tell me: '处理 _insights_pending.md'[/yellow]"
        )

    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--category", choices=CATEGORIES)
    p.add_argument("--limit", type=int)
    p.add_argument("--skus", nargs="+", help="filter to specific competitor IDs")
    p.add_argument("--skip-amazon", action="store_true", help="DTC + Reddit only (0 Rainforest credits)")
    p.add_argument("--force", action="store_true", help="re-process SKUs even if insight file already exists")
    sys.exit(asyncio.run(main(p.parse_args())))
