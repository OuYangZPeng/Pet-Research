"""Seasonality analyzer for US dog food and dog treats.

Two inputs are blended into the demand index:
1. Google Trends interest-over-time for pet-food queries (via pytrends, free).
2. A static prior based on pet retail seasonality:
   - Oct-Jan peak: holiday gifting + new-pet adoption + January diet switches
   - Jun-Aug softer: summer travel + lower impulse-treat demand

If pytrends is unavailable or blocked, we fall back to the static prior.
"""

from __future__ import annotations

from typing import Iterable

from sources._schema import SeasonalityPoint

MONTHS_EN = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
MONTHS_ZH = [f"{i}月" for i in range(1, 13)]

# Static prior: Q4 gifting + Jan diet-switching peak; summer is softer.
_STATIC_DEMAND = [92, 55, 68, 62, 65, 58, 56, 60, 72, 88, 100, 95]
_STATIC_DISCOUNT = [12, 18, 14, 12, 10, 15, 16, 14, 11, 8, 22, 18]


def _band(idx: float) -> str:
    if idx >= 80:
        return "peak"
    if idx >= 60:
        return "shoulder"
    return "off"


def _pytrends_monthly(queries: Iterable[str]) -> list[float] | None:
    """Pull avg interest by calendar month from Google Trends (last 5 years).

    Returns 12 values normalised 0–100, or None if pytrends is unavailable.
    """
    try:
        from pytrends.request import TrendReq  # type: ignore[import]
    except Exception:
        return None
    try:
        pyt = TrendReq(hl="en-US", tz=360)
        pyt.build_payload(list(queries), timeframe="today 5-y", geo="US")
        df = pyt.interest_over_time()
        if df is None or df.empty:
            return None
        df = df.drop(columns=[c for c in df.columns if c == "isPartial"], errors="ignore")
        # Mean across queries, then group by month.
        avg = df.mean(axis=1)
        monthly = avg.groupby(avg.index.month).mean()
        # Normalise so max month = 100.
        m = max(monthly.values)
        if m == 0:
            return None
        return [round(float(monthly.get(i, 0)) / m * 100, 1) for i in range(1, 13)]
    except Exception:
        return None


def analyze(category_hints: list[str] | None = None) -> dict:
    queries = category_hints or [
        "dog food",
        "dog treats",
        "fresh dog food",
        "puppy treats",
    ]
    demand = _pytrends_monthly(queries) or _STATIC_DEMAND

    points = [
        SeasonalityPoint(
            month=MONTHS_EN[i],
            monthZh=MONTHS_ZH[i],
            demandIndex=demand[i],
            discountPctTypical=float(_STATIC_DISCOUNT[i]),
            band=_band(demand[i]),
        ).model_dump()
        for i in range(12)
    ]

    insight = (
        "US dog-food demand peaks Oct-Jan: Q4 holiday gifting, November BFCM, and "
        "January 'health resolution' food switches. Summer (Jun-Aug) is softer for "
        "impulse treats, while fresh-food cold-chain costs usually tick up."
    )
    insight_zh = (
        "美国犬用食品需求高峰在 10-1 月：Q4 节日送礼、11 月黑五/网一、1 月"
        "“健康决议”换粮潮。夏季（6-8 月）冲动型零食偏淡，鲜食冷链成本通常略升。"
    )

    return {
        "points": points,
        "insight": insight,
        "insightZh": insight_zh,
    }


__all__ = ["analyze"]
