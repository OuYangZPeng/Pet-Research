"""Discover YouTube creator videos for every pet-category competitor.

Pulls product-specific videos (review / compare / unboxing) per SKU, enriches
with channel subscriber counts, scores by creator value, and writes per-category
JSON for the frontend:

    web/public/data/videos/dog-food.json
    web/public/data/videos/dog-treats.json

Each intent (review/compare/unboxing) cascades through a date filter: we try
"last 1 year" first, fall back to 2 years, then 3 years, then "any age" if
nothing surfaced. Every video carries its actual `publishedWithin` tag so the
UI can highlight freshness. Sort is fresher-tier first, then creator value.

Usage:
    python refresh_videos.py                              # all categories
    python refresh_videos.py --category dog-food          # one category
    python refresh_videos.py --skus blue-buffalo-life-protection-adult
    python refresh_videos.py --limit 3                    # spot-check first N per category
    python refresh_videos.py --per-query 8                # bigger per-query window
    python refresh_videos.py --lookback 1,2,3,all         # custom date cascade
    python refresh_videos.py --lookback 1                 # only last 12 months (strictest)
    python refresh_videos.py --lookback all               # no date filter

Quota:
    Best case: 1 hit on tier 1 → 3 search.list + 2 enrichment = ~302 units/SKU.
    Worst case: cascade to all 4 tiers per intent → ~1202 units/SKU.
    32 SKUs typical: 6 000–15 000 units; YouTube free tier is 10 000/day so
    a full refresh occasionally bleeds into the next day.
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

load_dotenv()

# Allow `python refresh_videos.py` from anywhere by ensuring our local
# package roots are importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from sources._schema import CategoryVideos, now_iso
from sources.youtube_videos import (
    DEFAULT_LOOKBACK_YEARS,
    QuotaExceededError,
    discover_videos_for_sku,
)

console = Console()

ROOT = Path(__file__).resolve().parent
SEED_DIR = (ROOT / ".." / "web" / "public" / "data").resolve()
OUT_DIR = SEED_DIR / "videos"

CATEGORY_FILES = {
    "dog-food": "dog-food.json",
    "dog-treats": "dog-treats.json",
}


def load_seed(category: str) -> list[dict]:
    path = SEED_DIR / CATEGORY_FILES[category]
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    # competitors live at top-level "competitors" array
    if isinstance(raw, dict):
        return raw.get("competitors", []) or []
    return raw or []


def sku_filter(competitor: dict, allow: Optional[set[str]]) -> bool:
    if not allow:
        return True
    sku = competitor.get("id") or competitor.get("sku") or ""
    return sku in allow


async def process_category(
    category: str,
    *,
    skus: Optional[set[str]],
    limit: Optional[int],
    per_query: int,
    max_per_sku: int,
    lookback_years: tuple[Optional[int], ...],
) -> dict:
    seed = load_seed(category)
    if skus:
        seed = [c for c in seed if sku_filter(c, skus)]
    if limit:
        seed = seed[:limit]

    if not seed:
        console.print(f"[yellow]  {category}: no matching seeds, skipping[/yellow]")
        return {"category": category, "generatedAt": now_iso(), "items": []}

    items: list[dict] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.fields[name]:32s}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task_id = progress.add_task(category, total=len(seed), name="(starting)")
        for competitor in seed:
            sku = competitor.get("id") or competitor.get("sku") or "unknown"
            brand = competitor.get("brand") or ""
            product = competitor.get("product") or ""
            product_zh = competitor.get("productZh")
            progress.update(task_id, name=f"{brand} {product}"[:32])

            try:
                bundle = await discover_videos_for_sku(
                    sku=sku,
                    brand=brand,
                    product=product,
                    product_zh=product_zh,
                    category=category,
                    results_per_query=per_query,
                    max_per_sku=max_per_sku,
                    lookback_years=lookback_years,
                )
            except QuotaExceededError as e:
                console.print(
                    f"[red]  {sku}: YouTube quota exceeded — {str(e)[:140]}.[/red]\n"
                    "[red]  Stopping early; existing data preserved. "
                    "Re-run after the quota resets (midnight Pacific).[/red]"
                )
                break  # stop processing this category to save time
            except Exception as e:
                # Transient per-SKU error (network timeout, malformed response,
                # etc.) — log it and move on. Distinguishing this from the
                # "missing API key" case below is critical: one bad SKU should
                # NOT abort the whole category, but a missing key should.
                console.print(f"[red]  {sku}: {type(e).__name__}: {str(e)[:140]}[/red]")
                progress.advance(task_id)
                await asyncio.sleep(1.0)
                continue

            if bundle is None:
                # `discover_videos_for_sku` returns None only when the YouTube
                # client cannot be constructed (missing api key / library).
                # That's an unrecoverable startup error — abort the category.
                console.print(
                    "[red]  YOUTUBE_API_KEY missing or library unavailable; aborting.[/red]"
                )
                return {"category": category, "generatedAt": now_iso(), "items": []}

            videos = bundle.get("videos") or []
            # Distribution of recency tiers for visibility (e.g. "5×1y · 3×2y")
            tier_counts: dict[str, int] = {}
            for v in videos:
                t = v.get("publishedWithin") or "older"
                tier_counts[t] = tier_counts.get(t, 0) + 1
            tier_str = (
                "  " + " · ".join(f"{n}×{t}" for t, n in sorted(tier_counts.items()))
                if tier_counts
                else ""
            )
            console.print(
                f"  [green]✓[/green] {sku}  {len(videos)} video(s)"
                + (
                    f"  top={videos[0]['channel'][:24]!r}@{videos[0].get('channelSubs',0):,}"
                    if videos
                    else ""
                )
                + tier_str
            )
            items.append(bundle)
            progress.advance(task_id)
            # Gentle pacing to stay under YouTube's per-minute search quota
            # (free tier ≈ 30 queries / min). Each SKU = 3 searches, so 1s
            # between SKUs keeps us at ~3 searches/s avg.
            await asyncio.sleep(1.0)

    bundle_doc = CategoryVideos(
        category=category,  # type: ignore[arg-type]
        generatedAt=now_iso(),
        items=[],
    ).model_dump()
    bundle_doc["items"] = items
    return bundle_doc


def write_output(category: str, payload: dict, *, merge: bool) -> Path:
    """Write per-category JSON.

    `merge` is always treated as `True` for safety: a full-category refresh that
    aborts mid-way (e.g. YouTube daily quota exhausted) would otherwise nuke
    every SKU that wasn't reached. We always union the newly-fetched SKUs over
    whatever was on disk, so a partial run can only ever improve the dataset.
    To force a clean rebuild, manually delete the JSON file before running.
    The `merge` parameter is kept on the signature for backwards compatibility
    with older call sites.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{category}.json"
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = None
        if isinstance(existing, dict) and existing.get("items"):
            new_ids = {item.get("sku") for item in payload.get("items", [])}
            kept = [item for item in existing["items"] if item.get("sku") not in new_ids]
            payload["items"] = payload.get("items", []) + kept
    # Silence the unused-parameter warning.
    _ = merge
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


async def main() -> int:
    p = argparse.ArgumentParser(description="Discover YouTube videos per SKU.")
    p.add_argument(
        "--category",
        choices=list(CATEGORY_FILES.keys()),
        help="Restrict to a single category.",
    )
    p.add_argument(
        "--skus",
        nargs="*",
        help="Restrict to specific SKU ids (matches Competitor.id).",
    )
    p.add_argument("--limit", type=int, help="Stop after N competitors per category.")
    p.add_argument(
        "--per-query",
        type=int,
        default=5,
        help="Max results per YouTube search query (default 5).",
    )
    p.add_argument(
        "--max-per-sku",
        type=int,
        default=12,
        help="Max unique videos to keep after merging all queries (default 12).",
    )
    p.add_argument(
        "--lookback",
        type=str,
        default="1,2,3,all",
        help=(
            "Date-cascade tiers in years, comma-separated. Use 'all' for the "
            "any-age fallback. Default '1,2,3,all' means: try last 12 months, "
            "then 24, then 36, then everything. Pass a single value like '1' "
            "to force strict recency."
        ),
    )
    args = p.parse_args()

    # Parse --lookback into a tuple matching DEFAULT_LOOKBACK_YEARS' shape
    try:
        lookback_years: tuple[Optional[int], ...] = tuple(
            (None if tok.strip().lower() in {"all", "any", "none", ""} else int(tok.strip()))
            for tok in args.lookback.split(",")
        )
    except ValueError:
        console.print(
            "[red]--lookback must be a comma list of integers or 'all'. "
            f"Got {args.lookback!r}.[/red]"
        )
        return 1
    if not lookback_years:
        lookback_years = DEFAULT_LOOKBACK_YEARS

    if not os.getenv("YOUTUBE_API_KEY"):
        console.print(
            "[red]YOUTUBE_API_KEY missing in environment / .env. "
            "Get one at https://console.cloud.google.com → enable YouTube Data API v3 → "
            "credentials → API key.[/red]"
        )
        return 1

    categories = [args.category] if args.category else list(CATEGORY_FILES.keys())
    skus = set(args.skus) if args.skus else None
    merge = bool(skus) or bool(args.limit)

    pretty_tiers = " → ".join(f"{y}y" if y else "all" for y in lookback_years)
    console.print(
        f"[dim]lookback cascade: {pretty_tiers}  ·  per-query: {args.per_query}  ·  "
        f"max/SKU: {args.max_per_sku}[/dim]"
    )

    overall: dict[str, dict] = {}
    for cat in categories:
        console.print(f"\n[bold cyan]→ {cat}[/bold cyan]")
        payload = await process_category(
            cat,
            skus=skus,
            limit=args.limit,
            per_query=args.per_query,
            max_per_sku=args.max_per_sku,
            lookback_years=lookback_years,
        )
        path = write_output(cat, payload, merge=merge)
        overall[cat] = payload
        console.print(
            f"[green]  wrote {path.relative_to(ROOT.parent)} "
            f"({len(payload.get('items', []))} SKUs)[/green]"
        )

    # Totals summary
    total_videos = sum(
        len(item.get("videos", []))
        for payload in overall.values()
        for item in payload.get("items", [])
    )
    total_skus = sum(len(p.get("items", [])) for p in overall.values())
    console.print(
        f"\n[bold green]done. {total_skus} SKU(s), {total_videos} unique video(s) "
        f"across {len(overall)} categor{'y' if len(overall)==1 else 'ies'}.[/bold green]"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(asyncio.run(main()))
