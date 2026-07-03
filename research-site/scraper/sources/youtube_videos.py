"""Per-SKU YouTube video discovery via YouTube Data API v3.

Different from `youtube_api.py` (curated influencer roster). This module:
  1. Searches YouTube for product-specific queries (review/compare/unboxing).
  2. Enriches results with channel subscriber counts and video stats.
  3. Computes a "creator value" score: log10(subs+1) * log10(views+1).

Quota budget (free tier = 10K units/day):
  - search.list      = 100 units / query
  - videos.list      =   1 unit  / call (≤ 50 IDs)
  - channels.list    =   1 unit  / call (≤ 50 IDs)

For 26 SKUs × 3 intents (review/install/unboxing) = 78 search calls = 7800 units.
Plus 2 enrichment calls. Total ≈ 7802 / 10K. Fits in a single day, comfortably.

Set `YOUTUBE_API_KEY` in the environment. Quietly returns [] without one.
"""

from __future__ import annotations

import asyncio
import html
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, Sequence

from ._schema import RecencyTier, SkuVideoBundle, VideoIntent, VideoItem, now_iso


# Cascade order: try last 1 year first, fall back progressively. `None` = no
# date filter (any age). Used per-intent: if 1y returns 0 hits we widen to 2y,
# then 3y, then "all time", until something is found.
DEFAULT_LOOKBACK_YEARS: tuple[Optional[int], ...] = (1, 2, 3, None)


def _published_after(years: Optional[int]) -> Optional[str]:
    """Convert a `years` value to an RFC-3339 publishedAfter timestamp."""
    if years is None or years <= 0:
        return None
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=int(365.25 * years))
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def _years_to_tier(years: Optional[int]) -> RecencyTier:
    if years is None:
        return "older"
    if years <= 1:
        return "1y"
    if years <= 2:
        return "2y"
    if years <= 3:
        return "3y"
    return "older"

DEFAULT_INTENTS_BY_CATEGORY: dict[str, dict[VideoIntent, str]] = {
    "dog-food": {
        "review": "{brand} {short} dog food review",
        "compare": "{brand} {short} vs review",
        "unboxing": "{brand} {short} unboxing",
    },
    "dog-treats": {
        "review": "{brand} {short} dog treats review",
        "compare": "{brand} {short} treats review",
        "unboxing": "{brand} {short} unboxing",
    },
}


_MODEL_RE = re.compile(r"\b([A-Z][A-Z0-9-]*\d[A-Z0-9-]*)\b")


def _short_name(product: str, max_words: int = 3) -> str:
    """Return the first `max_words` words of `product`, dropping parentheticals.

    Long marketing names ("Wave Electric Bidet Toilet Seat Cotton White") rarely
    appear verbatim in YouTube titles. Keeping the leading 2-3 words ("Wave Electric
    Bidet") yields much better recall.
    """
    cleaned = re.sub(r"\([^)]*\)", " ", product)
    words = re.split(r"\s+", cleaned.strip())
    short = " ".join(w for w in words[:max_words] if w)
    return short.strip()


def _extract_model(brand: str, product: str) -> str:
    """Pull out a model code like CST776CSFG, B1702-54, SE400, K3999.

    Looks at both the bare product string and any parenthetical (where TOTO
    typically stashes the SKU). Returns "" if nothing matches — query template
    handles the empty token cleanly.
    """
    candidates: list[str] = []
    for chunk in re.findall(r"\(([^)]*)\)", product) or [product]:
        for m in _MODEL_RE.finditer(chunk):
            tok = m.group(1)
            if tok == brand.upper() or len(tok) < 3:
                continue
            candidates.append(tok)
    return candidates[0] if candidates else ""


def _format_query(template: str, *, brand: str, product: str) -> str:
    """Render an intent template, collapsing whitespace and dedupping model echo."""
    short = _short_name(product)
    model = _extract_model(brand, product)
    if model and model.lower() in short.lower().split():
        model = ""  # model already appears in short — don't duplicate
    q = template.format(brand=brand, product=product, short=short, model=model)
    return re.sub(r"\s+", " ", q).strip()

# Cap per-query result count. Combined with intent count keeps quota predictable.
DEFAULT_RESULTS_PER_QUERY = 5
# Per-SKU dedup cap after merging all queries.
DEFAULT_MAX_PER_SKU = 12


def _client_or_none():
    try:
        from googleapiclient.discovery import build  # type: ignore[import]
    except Exception:
        return None
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return None
    return build("youtube", "v3", developerKey=key, cache_discovery=False)


# ------------------------------------------------------------------ helpers

_ISO_DURATION_RE = re.compile(
    r"^PT(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?$"
)


def parse_iso_duration(iso: Optional[str]) -> Optional[int]:
    """Convert ISO-8601 duration (e.g. PT8M40S) to seconds."""
    if not iso:
        return None
    m = _ISO_DURATION_RE.match(iso)
    if not m:
        return None
    h = int(m.group("h") or 0)
    mn = int(m.group("m") or 0)
    s = int(m.group("s") or 0)
    return h * 3600 + mn * 60 + s


def _score(channel_subs: Optional[int], views: Optional[int]) -> Optional[float]:
    if channel_subs is None or views is None:
        return None
    if channel_subs <= 0 or views <= 0:
        return 0.0
    return round(math.log10(channel_subs + 1) * math.log10(views + 1), 3)


# ------------------------------------------------------------------ network


class QuotaExceededError(RuntimeError):
    """Raised when YouTube returns a 403/429 quota error. Lets callers stop early."""


def _classify_quota_error(err: Exception) -> Optional[str]:
    """Returns 'per_minute', 'daily', or None for non-quota errors."""
    try:
        from googleapiclient.errors import HttpError  # type: ignore[import]
    except Exception:
        return None
    if not isinstance(err, HttpError):
        return None
    status = getattr(err, "resp", None)
    code = getattr(status, "status", None) if status is not None else None
    msg = str(err).lower()
    if "per minute" in msg or "rate" in msg or code == 429:
        return "per_minute"
    if "quota" in msg or code == 403:
        return "daily"
    return None


def _search_videos_sync(
    client,
    query: str,
    *,
    max_results: int,
    region: str,
    lang: str,
    published_after: Optional[str] = None,
) -> list[dict]:
    """One search.list call with adaptive backoff.

    On 429 (per-minute throttle) we sleep 65 s and retry up to 2 times, since
    YouTube's per-minute window flushes ~every 60 s. On 403 (daily quota
    exhausted) we raise immediately so the orchestrator can bail.
    """
    kwargs = dict(
        part="snippet",
        q=query,
        type="video",
        order="relevance",
        maxResults=max_results,
        regionCode=region,
        relevanceLanguage=lang,
        safeSearch="none",
    )
    if published_after:
        kwargs["publishedAfter"] = published_after

    backoff_s = 65.0
    for attempt in range(3):  # 1 try + up to 2 retries
        try:
            resp = client.search().list(**kwargs).execute()
            return resp.get("items", []) or []
        except Exception as e:
            kind = _classify_quota_error(e)
            if kind == "per_minute" and attempt < 2:
                # Per-minute throttle — sleep one window and retry once or twice.
                time.sleep(backoff_s)
                backoff_s *= 1.5  # 65s, 97s, 146s
                continue
            if kind == "daily" or kind == "per_minute":
                raise QuotaExceededError(f"{kind}: {str(e)[:160]}") from e
            raise
    return []


def _enrich_videos_sync(client, video_ids: list[str]) -> dict[str, dict]:
    """Returns {videoId: video resource} for stats + contentDetails."""
    out: dict[str, dict] = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        resp = (
            client.videos()
            .list(part="contentDetails,statistics", id=",".join(chunk))
            .execute()
        )
        for item in resp.get("items", []) or []:
            out[item["id"]] = item
    return out


def _enrich_channels_sync(client, channel_ids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    uniq = list(dict.fromkeys(channel_ids))
    for i in range(0, len(uniq), 50):
        chunk = uniq[i : i + 50]
        resp = (
            client.channels()
            .list(part="statistics", id=",".join(chunk))
            .execute()
        )
        for item in resp.get("items", []) or []:
            out[item["id"]] = item
    return out


# ------------------------------------------------------------------ public


async def discover_videos_for_sku(
    *,
    sku: str,
    brand: str,
    product: str,
    product_zh: Optional[str],
    category: str,
    intents: Optional[dict[VideoIntent, str]] = None,
    results_per_query: int = DEFAULT_RESULTS_PER_QUERY,
    max_per_sku: int = DEFAULT_MAX_PER_SKU,
    region: str = "US",
    lang: str = "en",
    lookback_years: Sequence[Optional[int]] = DEFAULT_LOOKBACK_YEARS,
) -> Optional[dict]:
    """Returns a SkuVideoBundle as dict (suitable for JSON), or None if no API key.

    Date-cascade behaviour: for each intent we try `lookback_years[0]` first
    (e.g. last 12 months). If that returns 0 hits we widen to the next entry
    (e.g. 24 months), and so on. The narrowest tier that returned the video is
    recorded on each `VideoItem.publishedWithin` so the UI can flag freshness.

    Dedups by videoId across all queries/tiers. Sorts by score desc.
    """
    client = _client_or_none()
    if client is None:
        return None

    queries = intents or DEFAULT_INTENTS_BY_CATEGORY.get(
        category,
        {
            "review": "{brand} {short} review",
            "compare": "{brand} {short} compare",
            "unboxing": "{brand} {short} unboxing",
        },
    )
    tiers: list[Optional[int]] = list(lookback_years) or [None]

    # Phase 1: per-intent cascaded search
    raw_by_id: dict[str, dict] = {}
    raw_query: dict[str, tuple[str, VideoIntent]] = {}
    raw_tier: dict[str, RecencyTier] = {}

    def _do_searches() -> None:
        first = True
        for intent, template in queries.items():
            q = _format_query(template, brand=brand, product=product)
            for years in tiers:
                published_after = _published_after(years)
                tier_label = _years_to_tier(years)
                # Throttle: ~2s between every search.list call keeps us under
                # YouTube's "Search Queries per minute" cap (≈30/min). The
                # first call of the SKU runs immediately.
                if not first:
                    time.sleep(2.0)
                first = False
                items = _search_videos_sync(
                    client,
                    q,
                    max_results=results_per_query,
                    region=region,
                    lang=lang,
                    published_after=published_after,
                )
                added_any = False
                for item in items:
                    vid = item.get("id", {}).get("videoId")
                    if not vid:
                        continue
                    if vid not in raw_by_id:
                        raw_by_id[vid] = item
                        raw_query[vid] = (q, intent)
                        raw_tier[vid] = tier_label
                        added_any = True
                # Stop cascading on this intent the moment any tier brings
                # results — broader tiers would just add older noise.
                if added_any:
                    break

    try:
        await asyncio.to_thread(_do_searches)
    except QuotaExceededError:
        # Re-raise so the orchestrator can stop early and avoid wasting time.
        raise
    if not raw_by_id:
        return SkuVideoBundle(
            sku=sku,
            brand=brand,
            product=product,
            productZh=product_zh,
            category=category,  # type: ignore[arg-type]
            videos=[],
            lastUpdated=now_iso(),
        ).model_dump(exclude_none=True)

    # Phase 2: enrich videos + channels
    vid_ids = list(raw_by_id.keys())
    vid_meta = await asyncio.to_thread(_enrich_videos_sync, client, vid_ids)

    channel_ids = [
        item.get("snippet", {}).get("channelId") for item in raw_by_id.values()
    ]
    channel_meta = await asyncio.to_thread(
        _enrich_channels_sync, client, [c for c in channel_ids if c]
    )

    videos: list[VideoItem] = []
    for vid, item in raw_by_id.items():
        sn = item.get("snippet", {})
        ch_id = sn.get("channelId")
        ch_node = channel_meta.get(ch_id, {}) if ch_id else {}
        ch_stats = ch_node.get("statistics", {})
        v_node = vid_meta.get(vid, {})
        v_stats = v_node.get("statistics", {})
        v_content = v_node.get("contentDetails", {})

        subs = int(ch_stats["subscriberCount"]) if ch_stats.get("subscriberCount") else None
        views = int(v_stats["viewCount"]) if v_stats.get("viewCount") else None
        likes = int(v_stats["likeCount"]) if v_stats.get("likeCount") else None
        comments = int(v_stats["commentCount"]) if v_stats.get("commentCount") else None
        duration_iso = v_content.get("duration")
        thumbs = sn.get("thumbnails", {})
        thumb = (
            thumbs.get("medium")
            or thumbs.get("high")
            or thumbs.get("default")
            or {}
        ).get("url")
        q, intent = raw_query.get(vid, ("", "general"))
        tier = raw_tier.get(vid, "older")

        videos.append(
            VideoItem(
                videoId=vid,
                title=html.unescape(sn.get("title", "")),
                channel=html.unescape(sn.get("channelTitle", "")),
                channelId=ch_id,
                channelSubs=subs,
                views=views,
                likes=likes,
                comments=comments,
                publishedAt=sn.get("publishedAt"),
                duration=duration_iso,
                durationSec=parse_iso_duration(duration_iso),
                thumbnail=thumb,
                url=f"https://youtu.be/{vid}",
                query=q,
                intent=intent,  # type: ignore[arg-type]
                publishedWithin=tier,
                score=_score(subs, views),
            )
        )

    # Sort: fresher tier first, then creator-value score within the same tier.
    _TIER_ORDER: dict[RecencyTier, int] = {"1y": 3, "2y": 2, "3y": 1, "older": 0}
    videos.sort(
        key=lambda v: (_TIER_ORDER.get(v.publishedWithin, 0), v.score or 0),
        reverse=True,
    )
    videos = videos[:max_per_sku]

    bundle = SkuVideoBundle(
        sku=sku,
        brand=brand,
        product=product,
        productZh=product_zh,
        category=category,  # type: ignore[arg-type]
        videos=videos,
        lastUpdated=now_iso(),
    )
    return bundle.model_dump(exclude_none=True)


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    brand = sys.argv[1] if len(sys.argv) > 1 else "Blue Buffalo"
    product = sys.argv[2] if len(sys.argv) > 2 else "Life Protection Formula Adult Chicken & Brown Rice Dry Dog Food"

    result = asyncio.run(
        discover_videos_for_sku(
            sku="cli-test",
            brand=brand,
            product=product,
            product_zh=None,
            category="dog-food",
            results_per_query=3,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
