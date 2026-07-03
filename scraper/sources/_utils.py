"""Shared HTTP + parsing helpers."""

from __future__ import annotations

import asyncio
import re
from contextlib import asynccontextmanager
from typing import Optional

import httpx

DEFAULT_HEADERS = {
    # Safari on macOS — empirically passes most Cloudflare / DTC bot checks
    # that block plain Chrome UA strings.
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


@asynccontextmanager
async def http_client(
    proxy: Optional[str] = None,
    timeout: float = 30.0,
) -> httpx.AsyncClient:
    """Async client with sensible defaults and optional proxy."""
    async with httpx.AsyncClient(
        headers=DEFAULT_HEADERS,
        timeout=timeout,
        follow_redirects=True,
        proxy=proxy,
    ) as client:
        yield client


PRICE_RE = re.compile(r"\$\s?([0-9][0-9,]*\.?[0-9]{0,2})")


def parse_price(text: str) -> Optional[float]:
    """Pull the first plausible USD price out of arbitrary text."""
    if not text:
        return None
    m = PRICE_RE.search(text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def slugify(s: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:max_len]


async def retry(coro_factory, attempts: int = 3, backoff: float = 1.5):
    """Retry an async coro factory with exponential backoff."""
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            return await coro_factory()
        except Exception as e:  # noqa: BLE001
            last_err = e
            await asyncio.sleep(backoff ** i)
    raise last_err  # type: ignore[misc]
