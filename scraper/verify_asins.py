"""Verify the pet-category JSON against Rainforest API.

Reads competitors from ../web/public/data/{dog-food,dog-treats}.json, calls
Rainforest for each Amazon row (skipping DTC), and prints a side-by-side
comparison table so you can confirm prices / ratings / review counts before
deciding whether to commit the enrichment.

Usage:
    python verify_asins.py                       # check all Amazon rows
    python verify_asins.py --category dog-food   # one category
    python verify_asins.py --limit 3             # spot-check the first 3
    python verify_asins.py --apply               # write changes back to JSON
    python verify_asins.py --dry-run             # show what would change, no writes

Cost (Rainforest credits):
    - Row WITH asin set        → 1 credit per row
    - Row WITHOUT asin set     → 2 credits per row (search + product)
    - DTC rows are always skipped

Free tier = 100 credits / month. The current pet seed has ~12 Amazon rows.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from sources import amazon_rainforest

ROOT = Path(__file__).resolve().parent
DATA_DIR = (ROOT / "../web/public/data").resolve()
CATEGORIES = ("dog-food", "dog-treats")

console = Console()


def _load(category: str) -> dict[str, Any]:
    return json.loads((DATA_DIR / f"{category}.json").read_text(encoding="utf-8"))


def _save(category: str, payload: dict[str, Any]) -> None:
    (DATA_DIR / f"{category}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _fmt(v: Any) -> str:
    if v is None:
        return "[dim]—[/dim]"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def _delta(seed: Any, live: Any) -> str:
    if seed is None or live is None:
        return "[dim]n/a[/dim]"
    try:
        s = float(seed)
        l = float(live)
    except (TypeError, ValueError):
        return "[dim]n/a[/dim]"
    if s == 0:
        return "[yellow]n/a[/yellow]"
    pct = (l - s) / s * 100
    color = "green" if abs(pct) < 15 else "red"
    sign = "+" if pct >= 0 else ""
    return f"[{color}]{sign}{pct:.1f}%[/{color}]"


async def verify_category(
    category: str,
    *,
    limit: int | None = None,
) -> tuple[list[dict], list[dict]]:
    """Returns (rows_for_table, enriched_competitors)."""
    payload = _load(category)
    competitors = payload.get("competitors", [])

    amazon_rows = [c for c in competitors if c.get("platform") == "Amazon"]
    if limit:
        amazon_rows = amazon_rows[:limit]

    rows: list[dict] = []
    asin_index: dict[str, dict] = {}

    for c in amazon_rows:
        seed_price = (c.get("price") or {}).get("current")
        seed_rating = c.get("rating")
        seed_reviews = c.get("reviews")

        asin = c.get("asin")
        if not asin:
            console.print(f"  [dim]search[/dim] {c['product'][:60]}…")
            asin = await amazon_rainforest.search_by_title(c.get("product") or "")
        info = await amazon_rainforest.fetch_product(asin) if asin else None

        rows.append(
            {
                "brand": c.get("brand"),
                "product": (c.get("productZh") or c.get("product") or "")[:42],
                "asin": asin or "—",
                "seed_price": seed_price,
                "live_price": info.get("price") if info else None,
                "seed_rating": seed_rating,
                "live_rating": info.get("rating") if info else None,
                "seed_reviews": seed_reviews,
                "live_reviews": info.get("reviews") if info else None,
            }
        )
        if asin and info:
            asin_index[c["id"]] = {"asin": asin, **info}

    # Mutate competitors with live data (for --apply path).
    enriched = []
    for c in competitors:
        merged = dict(c)
        live = asin_index.get(c.get("id"))
        if live:
            merged["asin"] = live["asin"]
            if live.get("rating") is not None:
                merged["rating"] = float(live["rating"])
            if live.get("reviews") is not None:
                merged["reviews"] = int(live["reviews"])
            if live.get("price"):
                price = dict(merged.get("price") or {})
                price["current"] = float(live["price"])
                merged["price"] = price
            merged["pendingFields"] = [
                f
                for f in (merged.get("pendingFields") or [])
                if f not in ("rating", "reviews")
            ] or None
            if merged.get("pendingFields") is None:
                merged.pop("pendingFields", None)
            merged["source"] = {
                "label": "Rainforest API (Amazon)",
                "url": live.get("url") or f"https://www.amazon.com/dp/{live['asin']}",
                "fetchedAt": amazon_rainforest.now_iso(),
            }
        enriched.append(merged)

    payload_out = dict(payload)
    payload_out["competitors"] = enriched
    return rows, payload_out


def render(category: str, rows: list[dict]) -> None:
    if not rows:
        console.print(f"[yellow]{category}: no Amazon rows to check.[/yellow]")
        return
    table = Table(title=f"[bold]{category}[/bold] · seed vs Rainforest", expand=True, show_lines=False)
    table.add_column("brand", style="cyan", no_wrap=True)
    table.add_column("product", overflow="ellipsis")
    table.add_column("asin", style="dim")
    table.add_column("price seed", justify="right")
    table.add_column("price live", justify="right")
    table.add_column("Δ price", justify="right")
    table.add_column("rating seed", justify="right")
    table.add_column("rating live", justify="right")
    table.add_column("reviews seed", justify="right")
    table.add_column("reviews live", justify="right", style="bold")
    for r in rows:
        table.add_row(
            r["brand"] or "?",
            r["product"],
            r["asin"],
            _fmt(r["seed_price"]),
            _fmt(r["live_price"]),
            _delta(r["seed_price"], r["live_price"]),
            _fmt(r["seed_rating"]),
            _fmt(r["live_rating"]),
            _fmt(r["seed_reviews"]),
            _fmt(r["live_reviews"]),
        )
    console.print(table)


async def main(args: argparse.Namespace) -> int:
    load_dotenv()
    if not os.getenv("RAINFOREST_API_KEY"):
        console.print(
            "[red bold]Missing RAINFOREST_API_KEY.[/red bold]\n"
            "Sign up at https://rainforestapi.com (100 req/month free), put the key "
            "in scraper/.env as `RAINFOREST_API_KEY=…`, then re-run."
        )
        return 1

    cats = [args.category] if args.category else list(CATEGORIES)
    total_changed = 0

    for cat in cats:
        console.print(f"\n[bold cyan]→ verifying {cat}…[/bold cyan]")
        rows, enriched_payload = await verify_category(cat, limit=args.limit)
        render(cat, rows)

        if args.apply and not args.dry_run:
            _save(cat, enriched_payload)
            console.print(f"  [green]wrote {cat}.json[/green]")
            total_changed += 1

    if args.apply and not args.dry_run:
        console.print(f"\n[bold green]done — {total_changed} file(s) updated.[/bold green]")
    elif args.apply and args.dry_run:
        console.print("\n[dim]--dry-run: no files written.[/dim]")
    else:
        console.print(
            "\n[dim]Read-only run. Pass --apply to write the live values back to JSON.[/dim]"
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=CATEGORIES, help="limit to one category")
    parser.add_argument("--limit", type=int, help="only check the first N Amazon rows in each category")
    parser.add_argument("--apply", action="store_true", help="write live values back to JSON")
    parser.add_argument("--dry-run", action="store_true", help="with --apply: show but don't write")
    sys.exit(asyncio.run(main(parser.parse_args())))
