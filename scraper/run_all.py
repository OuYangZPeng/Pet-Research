"""One-shot pet-only pipeline: refresh shared JSON and keep dog datasets current.

`run_all.py` now:
1. Loads the current pet datasets (`dog-food`, `dog-treats`) or pet seed fallbacks
2. Optionally enriches Amazon rows through Rainforest when a key is present
3. Recomputes AOV summaries
4. Refreshes seasonality / influencers / shipping / meta / painpoints

Usage:
    python run_all.py
    python run_all.py --dry-run
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

from analyze import aov as aov_mod
from analyze import painpoints as painpoints_mod
from analyze import seasonality as seasonality_mod
from seed_pet_categories import (
    DOG_FOOD_COMPETITORS,
    DOG_TREATS_COMPETITORS,
    _bundles_food,
    _bundles_treats,
    _installs_food,
    _installs_treats,
)
from sources import amazon_rainforest, reddit_api, youtube_api
from sources._schema import (
    BundleObservation,
    CategoryDataset,
    Competitor,
    FreeShippingBenchmark,
    InfluencerEntry,
    InstallProfile,
    MetaInfo,
    ShippingMode,
    SourceRef,
    now_iso,
)

SCRIPT_VERSION = "0.3.0-pet"
ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (ROOT / "../web/public/data").resolve()
PET_CATEGORIES = ("dog-food", "dog-treats")


def _load_existing(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _category_fallback(category: str) -> dict[str, Any]:
    if category == "dog-food":
        return {
            "category": category,
            "competitors": DOG_FOOD_COMPETITORS,
            "bundles": _bundles_food(),
            "installs": _installs_food(),
        }
    if category == "dog-treats":
        return {
            "category": category,
            "competitors": DOG_TREATS_COMPETITORS,
            "bundles": _bundles_treats(),
            "installs": _installs_treats(),
        }
    raise KeyError(category)


def _load_category_baseline(category: str) -> dict[str, Any]:
    existing = _load_existing(DEFAULT_OUTPUT / f"{category}.json")
    if existing:
        return existing
    return _category_fallback(category)


def _merge_by_id(existing: list[dict], fresh: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for row in existing:
        if row.get("id"):
            merged[row["id"]] = row
    for row in fresh:
        if not row.get("id"):
            continue
        merged[row["id"]] = {**merged.get(row["id"], {}), **row}
    return sorted(
        merged.values(),
        key=lambda r: (
            {"YouTube": 0, "TikTok": 1, "Instagram": 2, "Reddit": 3, "Facebook": 4}.get(
                r.get("platform", ""), 9
            ),
            -(r.get("categoryFit") or 0),
            r.get("displayName", ""),
        ),
    )


def _collect_sources_from_payload(blob: Any) -> list[SourceRef]:
    out: list[SourceRef] = []
    if isinstance(blob, dict):
        if blob.get("source"):
            try:
                out.append(SourceRef.model_validate(blob["source"]))
            except Exception:
                pass
        if blob.get("source") is None and {"label", "url"}.issubset(blob.keys()):
            try:
                out.append(SourceRef.model_validate(blob))
            except Exception:
                pass
        for value in blob.values():
            out.extend(_collect_sources_from_payload(value))
    elif isinstance(blob, list):
        for item in blob:
            out.extend(_collect_sources_from_payload(item))
    return out


async def _refresh_category(category: str) -> dict[str, Any]:
    baseline = _load_category_baseline(category)
    competitors = list(baseline.get("competitors") or _category_fallback(category)["competitors"])
    bundles = list(baseline.get("bundles") or _category_fallback(category)["bundles"])
    installs = list(baseline.get("installs") or _category_fallback(category)["installs"])

    if os.getenv("RAINFOREST_API_KEY"):
        print(f"[run_all] {category}: enriching Amazon rows via Rainforest…")
        competitors = await amazon_rainforest.enrich(competitors, only_amazon=True)

    dataset = CategoryDataset(
        category=category,  # type: ignore[arg-type]
        competitors=[Competitor.model_validate(c) for c in competitors],
        aov=aov_mod.analyze(competitors, category),  # type: ignore[arg-type]
        bundles=[BundleObservation.model_validate(b) for b in bundles],
        installs=[InstallProfile.model_validate(p) for p in installs],
    ).model_dump(exclude_none=True)
    return dataset


async def main(args: argparse.Namespace) -> int:
    load_dotenv()

    output_dir = (
        (ROOT / "_out").resolve() if args.dry_run else DEFAULT_OUTPUT
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[run_all] writing to {output_dir}")

    sources_used: list[SourceRef] = []

    for category in PET_CATEGORIES:
        print(f"[run_all] {category}: refreshing dataset…")
        dataset = await _refresh_category(category)
        _write(output_dir / f"{category}.json", dataset)
        sources_used.extend(_collect_sources_from_payload(dataset.get("competitors", [])))

    print("[run_all] seasonality…")
    season = seasonality_mod.analyze()
    _write(output_dir / "seasonality.json", season)
    sources_used.extend(_collect_sources_from_payload(season))

    print("[run_all] influencers (YouTube + Reddit)…")
    existing_influencers = _load_existing(DEFAULT_OUTPUT / "influencers.json") or []
    fresh_influencers: list[dict] = []
    try:
        fresh_influencers.extend(await asyncio.wait_for(youtube_api.fetch(), timeout=45))
    except Exception as e:
        print(f"[run_all] youtube influencers unavailable: {type(e).__name__}")
    try:
        fresh_influencers.extend(await asyncio.wait_for(reddit_api.fetch(), timeout=30))
    except Exception as e:
        print(f"[run_all] reddit influencers unavailable: {type(e).__name__}")
    influencers = _merge_by_id(existing_influencers, fresh_influencers) if fresh_influencers else existing_influencers
    influencers = [InfluencerEntry.model_validate(row).model_dump(exclude_none=True) for row in influencers]
    _write(output_dir / "influencers.json", influencers)
    sources_used.extend(_collect_sources_from_payload(influencers))

    print("[run_all] shipping…")
    existing_shipping = _load_existing(DEFAULT_OUTPUT / "shipping.json") or {"modes": [], "thresholds": []}
    shipping = {
        "modes": [
            ShippingMode.model_validate(m).model_dump(exclude_none=True)
            for m in (existing_shipping.get("modes") or [])
        ],
        "thresholds": [
            FreeShippingBenchmark.model_validate(t).model_dump(exclude_none=True)
            for t in (existing_shipping.get("thresholds") or [])
        ],
    }
    _write(output_dir / "shipping.json", shipping)
    sources_used.extend(_collect_sources_from_payload(shipping))

    print("[run_all] painpoints…")
    painpoints = painpoints_mod.aggregate()
    _write(output_dir / "painpoints.json", painpoints)

    seen_urls: set[str] = set()
    unique_sources: list[SourceRef] = []
    for s in sources_used:
        if s.url in seen_urls:
            continue
        seen_urls.add(s.url)
        unique_sources.append(s)

    meta = MetaInfo(
        generatedAt=now_iso(),
        scriptVersion=SCRIPT_VERSION,
        sources=unique_sources,
    ).model_dump(exclude_none=True)
    _write(output_dir / "meta.json", meta)

    print("[run_all] done.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Write to ./_out instead of public/data")
    sys.exit(asyncio.run(main(parser.parse_args())))
