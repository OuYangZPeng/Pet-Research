"""YouTube Data API v3 wrapper for curated dog-food / dog-treat creators."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from ._schema import InfluencerEntry, SourceRef, now_iso

TARGETS: list[dict[str, object]] = [
    {
        "id": "zak-george",
        "channel_id": "UCZzFRKsgVMhGTxffpzgTJlQ",
        "handle": "zakgeorge",
        "url": "https://www.youtube.com/@zakgeorge",
        "category_fit": 10,
        "categories": ["dog-food", "dog-treats"],
        "notes": "Major dog-training creator. Strong fit for training treats, feeding routines, and product demos.",
        "notes_zh": "头部犬类训练创作者，适合训练零食、喂食日常与产品演示。",
    },
    {
        "id": "rachel-fusaro",
        "channel_id": "UCn-ln_D0kR3Qq6eWkcyayxA",
        "handle": "RachelFusaro",
        "url": "https://www.youtube.com/@RachelFusaro",
        "category_fit": 10,
        "categories": ["dog-food"],
        "notes": "Dog nutrition educator focused on ingredient labels, kibble, and fresh-food comparisons.",
        "notes_zh": "犬类营养教育创作者，擅长成分表解读、干粮与鲜食对比。",
    },
    {
        "id": "tucker-budzyn",
        "channel_id": "UCNSzfesc7IgWZwg4n6uXr1A",
        "handle": "tuckerbudzyn",
        "url": "https://www.youtube.com/@tuckerbudzyn",
        "category_fit": 9,
        "categories": ["dog-treats"],
        "notes": "High-reach dog lifestyle channel; ideal for treat launches, gifting, and impulse-buy SKUs.",
        "notes_zh": "高流量犬类生活方式频道，适合零食上新、礼盒和冲动型 SKU。",
    },
    {
        "id": "gone-to-the-snow-dogs",
        "channel_id": "UCJDSFaLJsLt2yHEKp3JM4_g",
        "handle": "gonetothesnowdogs",
        "url": "https://www.youtube.com/@gonetothesnowdogs",
        "category_fit": 8,
        "categories": ["dog-food", "dog-treats"],
        "notes": "Multi-dog household; strong fit for kibble taste tests, treat hauls, and Chewy-centered content.",
        "notes_zh": "多犬家庭频道，适合狗粮试吃、零食开箱和 Chewy 购物内容。",
    },
    {
        "id": "rocky-kanaka",
        "channel_id": "UCBzSOMn4P3L3s8l5UZTqN0w",
        "handle": "RockyKanaka",
        "url": "https://www.youtube.com/@RockyKanaka",
        "category_fit": 8,
        "categories": ["dog-treats"],
        "notes": "Rescue storytelling with strong emotional conversion; good for treats and donation-led brand campaigns.",
        "notes_zh": "救助故事型频道，情感转化强，适合零食和公益捐赠式营销。",
    },
]


def _client_or_none():
    try:
        from googleapiclient.discovery import build  # type: ignore[import]
    except Exception:
        return None
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return None
    return build("youtube", "v3", developerKey=key, cache_discovery=False)


def _fetch_channel_stats_sync(channel_ids: list[str]) -> dict[str, dict]:
    client = _client_or_none()
    if not client:
        return {}
    out: dict[str, dict] = {}
    # API allows up to 50 IDs per call.
    for i in range(0, len(channel_ids), 50):
        chunk = channel_ids[i : i + 50]
        resp = (
            client.channels()
            .list(part="snippet,statistics", id=",".join(chunk))
            .execute()
        )
        for item in resp.get("items", []):
            out[item["id"]] = item
    return out


async def fetch() -> list[dict]:
    """Return InfluencerEntry-shaped dicts. Empty if no API key."""
    channel_ids = [t["channel_id"] for t in TARGETS]
    stats = await asyncio.to_thread(_fetch_channel_stats_sync, channel_ids)
    if not stats:
        return []

    entries: list[dict] = []
    for t in TARGETS:
        node = stats.get(t["channel_id"])
        if not node:
            continue
        st = node.get("statistics", {})
        sn = node.get("snippet", {})
        entry = {
            "id": t["id"],
            "platform": "YouTube",
            "handle": t["handle"],
            "displayName": sn.get("title", t["handle"]),
            "url": t["url"],
            "audience": int(st.get("subscriberCount") or 0),
            "audienceUnit": "subscribers",
            "totalViews": int(st.get("viewCount") or 0),
            "categoryFit": t["category_fit"],
            "categories": t.get("categories"),
            "notes": t["notes"],
            "notesZh": t.get("notes_zh"),
            "source": SourceRef(
                label="YouTube Data API",
                url=t["url"],
                fetchedAt=now_iso(),
            ).model_dump(),
        }
        entries.append(InfluencerEntry.model_validate(entry).model_dump(exclude_none=True))
    return entries


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(asyncio.run(fetch()), indent=2))
