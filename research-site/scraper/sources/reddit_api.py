"""Reddit (PRAW) — subscriber counts + top weekly threads for dog-food communities."""

from __future__ import annotations

import asyncio
import os

from ._schema import InfluencerEntry, SourceRef, now_iso

TARGETS = [
    {
        "id": "reddit-dogfood",
        "sub": "Dogfood",
        "fit": 10,
        "categories": ["dog-food"],
        "notes": "Dedicated dog-food subreddit: ingredient debates, recalls, and brand comparisons.",
        "notes_zh": "专注狗粮的社区，适合看成分争议、召回预警和品牌对比。",
    },
    {
        "id": "reddit-dogs",
        "sub": "dogs",
        "fit": 8,
        "categories": ["dog-food", "dog-treats"],
        "notes": "Broad dog-owner community with frequent feeding, picky-eater, and treat recommendation threads.",
        "notes_zh": "综合犬主社区，常见喂食、挑食和零食推荐讨论。",
    },
    {
        "id": "reddit-pets",
        "sub": "Pets",
        "fit": 7,
        "categories": ["dog-treats"],
        "notes": "Broader pet community useful for treat gifting and subscription-box discussions.",
        "notes_zh": "泛宠物社区，适合观察零食送礼和订阅礼盒讨论。",
    },
]


def _praw_client_or_none():
    try:
        import praw  # type: ignore[import]
    except Exception:
        return None
    cid = os.getenv("REDDIT_CLIENT_ID")
    csec = os.getenv("REDDIT_CLIENT_SECRET")
    ua = os.getenv("REDDIT_USER_AGENT", "shadowmeta/0.1")
    if not (cid and csec):
        return None
    return praw.Reddit(
        client_id=cid,
        client_secret=csec,
        user_agent=ua,
        check_for_async=False,
    )


def _fetch_sync() -> list[dict]:
    reddit = _praw_client_or_none()
    if not reddit:
        return []
    out: list[dict] = []
    for t in TARGETS:
        try:
            sub = reddit.subreddit(t["sub"])
            top = next(iter(sub.top(time_filter="week", limit=1)), None)
            entry = {
                "id": t["id"],
                "platform": "Reddit",
                "handle": f"r/{t['sub']}",
                "displayName": f"r/{t['sub']}",
                "url": f"https://www.reddit.com/r/{t['sub']}/",
                "audience": int(getattr(sub, "subscribers", 0) or 0),
                "audienceUnit": "followers",
                "categoryFit": t["fit"],
                "categories": t.get("categories"),
                "notes": t["notes"],
                "notesZh": t.get("notes_zh"),
                "topPieceTitle": getattr(top, "title", None) if top else None,
                "topPieceUrl": (
                    f"https://www.reddit.com{getattr(top, 'permalink', '')}" if top else None
                ),
                "source": SourceRef(
                    label=f"r/{t['sub']}",
                    url=f"https://www.reddit.com/r/{t['sub']}/",
                    fetchedAt=now_iso(),
                ).model_dump(),
            }
            out.append(InfluencerEntry.model_validate(entry).model_dump(exclude_none=True))
        except Exception:
            continue
    return out


async def fetch() -> list[dict]:
    return await asyncio.to_thread(_fetch_sync)


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(asyncio.run(fetch()), indent=2))
