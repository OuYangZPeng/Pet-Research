"""Reddit thread fetcher for product-specific qualitative discussion.

Uses PRAW with the REDDIT_CLIENT_ID/SECRET creds from .env. Looks up the top
threads + most-upvoted comments matching a product query (e.g. "Farmer's Dog
review", "Greenies dental treats"). Each comment becomes a RawReview.

If creds are missing, falls back to Reddit's public JSON endpoint
(https://www.reddit.com/search.json) which works unauthenticated for low-volume
use (~60 reqs/min).
"""

from __future__ import annotations

import os
import urllib.parse
from typing import Optional

from ._utils import http_client


SUBS = ["Dogfood", "dogs", "Pets", "puppy101"]


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
    return praw.Reddit(client_id=cid, client_secret=csec, user_agent=ua, check_for_async=False)


_unauth_blocked_warned = False


async def _fetch_public_json(query: str, limit: int = 10) -> list[dict]:
    """Use per-subreddit search.json with restrict_sr=1. Unauthenticated, free.

    NOTE: Reddit (as of 2024+) blocks ALL unauthenticated requests from server
    IPs with 403 'whoa there, pardner!'. This function is kept as a no-op
    fallback that prints a clear, actionable warning ONCE per process. To get
    actual Reddit data, register at https://www.reddit.com/prefs/apps and set
    REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET — then PRAW will be used instead.
    """
    global _unauth_blocked_warned
    if not _unauth_blocked_warned:
        print(
            "\n[reddit] Unauthenticated Reddit access is blocked by their network policy "
            "(403 'whoa there, pardner!'). To enable Reddit data, register a free app at "
            "https://www.reddit.com/prefs/apps (type 'script', 2 min) and add "
            "REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET to scraper/.env. "
            "Skipping Reddit collection for now."
        )
        _unauth_blocked_warned = True
    return []
    import asyncio

    out: list[dict] = []
    seen_urls: set[str] = set()
    # Smaller per-sub limit so we get a balanced spread across subs.
    per_sub = max(2, limit // len(SUBS))
    async with http_client() as c:
        for sub in SUBS:
            url = f"https://www.reddit.com/r/{sub}/search.json"
            params = {
                "q": query,
                "restrict_sr": 1,
                "sort": "top",
                "t": "year",
                "limit": per_sub,
            }
            try:
                r = await c.get(
                    url,
                    params=params,
                    headers={"User-Agent": "shadowmeta/0.2 (pet category analysis)"},
                )
            except Exception:
                continue
            if r.status_code == 429:
                # Polite backoff if Reddit throttles us.
                await asyncio.sleep(2)
                continue
            if r.status_code != 200:
                continue
            data = r.json() or {}
            children = (data.get("data") or {}).get("children") or []
            for ch in children:
                d = ch.get("data") or {}
                body = d.get("selftext") or ""
                combined = (d.get("title") or "") + ("\n\n" + body if body else "")
                if not combined.strip():
                    continue
                permalink = d.get("permalink", "")
                url_full = f"https://www.reddit.com{permalink}"
                if url_full in seen_urls:
                    continue
                seen_urls.add(url_full)
                out.append(
                    {
                        "channel": "reddit",
                        "productId": query,
                        "title": d.get("title"),
                        "body": combined,
                        "rating": None,
                        "verified": None,
                        "helpful": d.get("ups"),
                        "date": None,
                        "reviewer": f"r/{sub}",
                        "url": url_full,
                    }
                )
            await asyncio.sleep(0.4)  # be polite, unauth limit is 60 req/min
    return out


def _fetch_with_praw_sync(query: str, limit: int = 5) -> list[dict]:
    reddit = _praw_client_or_none()
    if not reddit:
        return []
    out: list[dict] = []
    for sub_name in SUBS:
        try:
            sub = reddit.subreddit(sub_name)
            for post in sub.search(query, sort="top", time_filter="year", limit=limit):
                body = post.selftext or ""
                combined = (post.title or "") + ("\n\n" + body if body else "")
                out.append(
                    {
                        "channel": "reddit",
                        "productId": query,
                        "title": post.title,
                        "body": combined,
                        "rating": None,
                        "verified": None,
                        "helpful": post.score,
                        "date": None,
                        "reviewer": f"r/{sub_name}",
                        "url": f"https://www.reddit.com{post.permalink}",
                    }
                )
                # Pull the top 3 comments too so themes get richer.
                try:
                    post.comments.replace_more(limit=0)
                    for cmt in list(post.comments)[:3]:
                        if not cmt.body or cmt.body in ("[deleted]", "[removed]"):
                            continue
                        out.append(
                            {
                                "channel": "reddit",
                                "productId": query,
                                "title": None,
                                "body": cmt.body,
                                "rating": None,
                                "verified": None,
                                "helpful": cmt.score,
                                "date": None,
                                "reviewer": f"u/{cmt.author}" if cmt.author else None,
                                "url": f"https://www.reddit.com{cmt.permalink}",
                            }
                        )
                except Exception:
                    pass
        except Exception:
            continue
    return out


async def fetch(query: str, *, limit: int = 5) -> list[dict]:
    """Fetch product-related Reddit content. Combines title+body into `body` so
    that link-only posts still surface their title to the LLM."""
    import asyncio

    if _praw_client_or_none() is not None:
        return await asyncio.to_thread(_fetch_with_praw_sync, query, limit)
    return await _fetch_public_json(query, limit=limit * 3)


if __name__ == "__main__":  # pragma: no cover
    import asyncio
    import json
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m sources.reddit_threads "Farmer\'s Dog review"')
        sys.exit(1)
    q = " ".join(sys.argv[1:])
    rows = asyncio.run(fetch(q))
    print(f"{len(rows)} items")
    print(json.dumps(rows[:3], indent=2, ensure_ascii=False))
