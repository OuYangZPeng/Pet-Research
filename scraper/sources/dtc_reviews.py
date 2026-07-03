"""DTC store review fetchers for the current pet brands.

Right now all supported pet DTC brands use Trustpilot as the consistent
cross-brand review surface. This keeps the scraper simple and avoids dragging
unused legacy adapters forward.
"""

from __future__ import annotations

from typing import Optional


async def _trustpilot(brand_domain: str, *, max_reviews: int = 40) -> list[dict]:
    """Delegate to the Playwright-based Trustpilot scraper."""
    try:
        from . import trustpilot as tp
    except Exception:
        return []
    try:
        return await tp.fetch(brand_domain, max_reviews=max_reviews)
    except Exception:
        return []


DTC_HANDLERS: dict[str, dict[str, str]] = {
    "the farmer's dog": {"trustpilot_domain": "thefarmersdog.com"},
    "nom nom": {"trustpilot_domain": "nomnomnow.com"},
    "barkbox": {"trustpilot_domain": "barkbox.com"},
    "open farm": {"trustpilot_domain": "openfarmpet.com"},
}


async def fetch(
    brand: str,
    *,
    product_handle: Optional[str] = None,
    sku_id: Optional[str] = None,
) -> list[dict]:
    """Fetch DTC reviews for a brand.

    `product_handle` and `sku_id` stay on the signature so existing callers do
    not need to change, but the current pet pipeline resolves DTC reviews at the
    brand/domain level only.
    """
    _ = product_handle, sku_id
    cfg = DTC_HANDLERS.get(brand.lower())
    if not cfg:
        return []
    return await _trustpilot(cfg["trustpilot_domain"])


if __name__ == "__main__":  # pragma: no cover
    import asyncio
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m sources.dtc_reviews <brand> [product_handle_or_sku]")
        sys.exit(1)
    brand = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    rows = asyncio.run(fetch(brand, product_handle=arg, sku_id=arg))
    print(f"{len(rows)} reviews")
    print(json.dumps(rows[:3], indent=2, ensure_ascii=False))
