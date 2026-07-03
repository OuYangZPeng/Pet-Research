"""AOV (Average Order Value) per-platform analytics for pet categories."""

from __future__ import annotations

import math
import statistics
from typing import Sequence

from sources._schema import AovBucket, Category, CategoryAov


def quantile(values: Sequence[float], q: float) -> float:
    """Compute a quantile using linear interpolation; values must be non-empty."""
    if not values:
        return 0.0
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(s[int(pos)])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def bucket_for(platform: str, prices: list[float]) -> AovBucket | None:
    if not prices:
        return None
    return AovBucket(
        platform=platform,
        median=round(statistics.median(prices), 2),
        p25=round(quantile(prices, 0.25), 2),
        p75=round(quantile(prices, 0.75), 2),
        min=round(min(prices), 2),
        max=round(max(prices), 2),
        sample=len(prices),
    )


def analyze(competitors: list[dict], category: Category) -> CategoryAov:
    """Group by platform and derive one summary sentence per pet category."""
    by_platform: dict[str, list[float]] = {}
    for c in competitors:
        p = c.get("platform") or "Unknown"
        price = (c.get("price") or {}).get("current")
        if price is None:
            continue
        by_platform.setdefault(p, []).append(float(price))

    buckets: list[AovBucket] = []
    for plat, prices in sorted(by_platform.items(), key=lambda kv: -len(kv[1])):
        b = bucket_for(plat, prices)
        if b:
            buckets.append(b)

    labels = {
        "dog-food": ("Dog Food", "犬用主食"),
        "dog-treats": ("Dog Treats", "犬用零食"),
    }
    label_en, label_zh = labels[category]

    top = buckets[0] if buckets else None
    if top:
        if category == "dog-food":
            insight = (
                f"Across {top.sample} dog-food samples on {top.platform}, the median price is "
                f"${top.median:,.0f} (P25 ${top.p25:,.0f}, P75 ${top.p75:,.0f}). "
                "Amazon mass kibble and Chewy premium dry dominate the price ladder, while "
                "fresh-food subscriptions sit on a separate weekly-spend curve."
            )
            insight_zh = (
                f"在 {top.platform} 平台 {top.sample} 件犬用主食样本中，中位价 "
                f"${top.median:,.0f}（P25 ${top.p25:,.0f}，P75 ${top.p75:,.0f}）。"
                "Amazon 大众干粮与 Chewy 高端干粮形成主要价格梯度，鲜食订阅则是另一条周付费曲线。"
            )
        else:
            insight = (
                f"Across {top.sample} dog-treat samples on {top.platform}, the median price is "
                f"${top.median:,.0f} (P25 ${top.p25:,.0f}, P75 ${top.p75:,.0f}). "
                "Impulse treats stay under $15, while dental chews and subscriptions lift AOV sharply."
            )
            insight_zh = (
                f"在 {top.platform} 平台 {top.sample} 件犬用零食样本中，中位价 "
                f"${top.median:,.0f}（P25 ${top.p25:,.0f}，P75 ${top.p75:,.0f}）。"
                "冲动购买型零食多在 $15 以下，而洁齿零食与订阅礼盒会显著拉高客单价。"
            )
    else:
        insight = "No samples available."
        insight_zh = "暂无可用样本。"

    return CategoryAov(
        category=category,
        categoryLabel=label_en,
        categoryLabelZh=label_zh,
        buckets=buckets,
        insight=insight,
        insightZh=insight_zh,
    )


__all__ = ["analyze", "quantile", "bucket_for"]
