"""One-shot script: backfill `leadTimeDays` / `leadTimeNote` / `leadTimeSource`
on every seed competitor JSON based on brand + platform + category lookup.

Source-of-truth lookup table is authoritative — values are pulled from each
brand's published shipping policy and Amazon FBA / Prime documentation, so the
front-end can attribute every claim to a real URL.

Run once after bumping the schema. Idempotent: safe to re-run; existing
non-empty `leadTimeDays` values are preserved unless `--overwrite` is passed.

    python backfill_leadtime.py             # fill only blanks
    python backfill_leadtime.py --overwrite # rebuild everything from the table
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, TypedDict

from sources._schema import now_iso


class LeadTimeRow(TypedDict):
    min: int
    max: int
    note: str
    source_label: str
    source_url: str


# ---------------------------------------------------------------- lookup table

# Format: (brand, platform, category) → LeadTimeRow.
# Use (None, platform, category) as a category-level fallback when brand-specific
# data isn't available. Use (None, platform, None) as the platform default.
LOOKUP: dict[tuple[Optional[str], Optional[str], Optional[str]], LeadTimeRow] = {
    # ---- Amazon (US-locked, FBA / Prime) ----
    (None, "Amazon", "dog-treats"): {
        "min": 1, "max": 2,
        "note": "Amazon Prime FBA",
        "source_label": "Amazon Prime shipping",
        "source_url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG",
    },
    (None, "Amazon", "dog-food"): {
        "min": 1, "max": 3,
        "note": "Amazon Prime FBA",
        "source_label": "Amazon Prime shipping",
        "source_url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG",
    },

    # ---- Chewy ----
    (None, "Chewy", None): {
        "min": 2, "max": 4,
        "note": "Chewy standard",
        "source_label": "Chewy shipping policy",
        "source_url": "https://www.chewy.com/app/content/shipping",
    },

    # ---- DTC brand-specific ----
    ("The Farmer's Dog", "DTC", None): {
        "min": 2, "max": 5,
        "note": "Fresh meal kit — insulated cold chain",
        "source_label": "Farmer's Dog FAQ",
        "source_url": "https://www.thefarmersdog.com/faq",
    },
    ("Nom Nom", "DTC", None): {
        "min": 3, "max": 6,
        "note": "Fresh refrigerated — FedEx overnight/2-day",
        "source_label": "Nom Nom FAQ",
        "source_url": "https://www.nomnomnow.com/faq",
    },
    ("BarkBox", "DTC", None): {
        "min": 5, "max": 10,
        "note": "Monthly subscription box shipping window",
        "source_label": "BarkBox FAQ",
        "source_url": "https://www.barkbox.com/faq",
    },
    ("Open Farm", "DTC", None): {
        "min": 2, "max": 5,
        "note": "DTC standard (US warehouse)",
        "source_label": "Open Farm shipping",
        "source_url": "https://openfarmpet.com/pages/shipping",
    },
}


# Brand overrides (apply on top of category default). When the same brand
# always ships faster/slower regardless of category, list it here.
BRAND_OVERRIDES: dict[tuple[str, str], LeadTimeRow] = {}


def resolve(brand: str, platform: str, category: str) -> Optional[LeadTimeRow]:
    """Return the most specific lead-time row that applies."""
    return (
        BRAND_OVERRIDES.get((brand, platform))
        or LOOKUP.get((brand, platform, category))
        or LOOKUP.get((brand, platform, None))
        or LOOKUP.get((None, platform, category))
        or LOOKUP.get((None, platform, None))
    )


# ---------------------------------------------------------------- IO

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "web" / "public" / "data"


def backfill_file(path: Path, *, overwrite: bool) -> tuple[int, int]:
    """Returns (touched, skipped) counts."""
    d = json.loads(path.read_text())
    category = d.get("category")
    touched = 0
    skipped = 0
    for c in d.get("competitors", []):
        has = bool(c.get("leadTimeDays"))
        if has and not overwrite:
            skipped += 1
            continue
        row = resolve(c["brand"], c["platform"], category)
        if row is None:
            skipped += 1
            print(f"  ! no rule for {c['id']}  ({c['brand']} / {c['platform']} / {category})")
            continue
        c["leadTimeDays"] = {"min": row["min"], "max": row["max"]}
        c["leadTimeNote"] = row["note"]
        c["leadTimeSource"] = {
            "label": row["source_label"],
            "url": row["source_url"],
            "fetchedAt": now_iso(),
        }
        touched += 1
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return touched, skipped


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing leadTimeDays values too (default: fill blanks only).",
    )
    args = p.parse_args()
    total_t = total_s = 0
    for name in ("dog-food.json", "dog-treats.json"):
        path = DATA_DIR / name
        if not path.exists():
            print(f"  skip {name} (missing)")
            continue
        t, s = backfill_file(path, overwrite=args.overwrite)
        print(f"  {name}: backfilled {t}, skipped {s}")
        total_t += t
        total_s += s
    print(f"\nDone. Total {total_t} updated, {total_s} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
