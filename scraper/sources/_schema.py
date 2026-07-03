"""Shared pydantic models that match web/src/lib/types.ts.

Keep these in sync with the TypeScript types. If you add a field, add it on both
sides and bump `MetaInfo.scriptVersion` in run_all.py.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class SourceRef(BaseModel):
    label: str
    url: str
    fetchedAt: Optional[str] = Field(default_factory=now_iso)


class PriceInfo(BaseModel):
    current: float
    original: Optional[float] = None
    currency: Literal["USD"] = "USD"
    discountPct: Optional[float] = None


Platform = Literal["Amazon", "Wayfair", "Home Depot", "DTC", "Lowe's", "Chewy"]
ShipFrom = Literal["US", "CN", "Both"]


class LeadTimeDays(BaseModel):
    min: int
    max: int


class SupplierContact(BaseModel):
    company: str
    companyZh: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    wholesaleEmail: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    notesZh: Optional[str] = None


class Competitor(BaseModel):
    id: str
    brand: str
    product: str
    productZh: Optional[str] = None
    platform: Platform
    storeUrl: str
    bsrRank: Optional[int] = None
    asin: Optional[str] = None
    sku: Optional[str] = None
    price: PriceInfo
    rating: Optional[float] = None
    reviews: Optional[int] = None
    variant: Optional[str] = None
    shippingNote: Optional[str] = None
    shipFrom: Optional[ShipFrom] = None
    # Per-SKU delivery window once the order is placed (business days, US market).
    leadTimeDays: Optional[LeadTimeDays] = None
    leadTimeNote: Optional[str] = None
    leadTimeSource: Optional[SourceRef] = None
    supplier: Optional[SupplierContact] = None
    bundle: Optional[bool] = None
    pendingFields: Optional[list[str]] = None
    source: SourceRef


AudienceUnit = Literal["subscribers", "followers", "members"]
PlatformInfluencer = Literal["YouTube", "TikTok", "Instagram", "Reddit", "Facebook"]


class InfluencerEntry(BaseModel):
    id: str
    platform: PlatformInfluencer
    handle: str
    displayName: str
    url: str
    audience: int
    audienceUnit: AudienceUnit
    totalViews: Optional[int] = None
    categoryFit: int = Field(ge=0, le=10)
    categories: Optional[list[str]] = None
    notes: str
    notesZh: Optional[str] = None
    topPieceTitle: Optional[str] = None
    topPieceUrl: Optional[str] = None
    source: SourceRef


class SeasonalityPoint(BaseModel):
    month: str
    monthZh: str
    demandIndex: float
    discountPctTypical: float
    band: Literal["peak", "shoulder", "off"]


class ShippingMode(BaseModel):
    id: str
    method: str
    methodZh: str
    transit: str
    cost: str
    useCase: str
    useCaseZh: str
    shipFrom: Literal["CN", "US"]
    source: SourceRef


class FreeShippingBenchmark(BaseModel):
    brand: str
    threshold: float
    note: str
    noteZh: Optional[str] = None
    source: SourceRef


class AovBucket(BaseModel):
    platform: str
    median: float
    p25: float
    p75: float
    min: float
    max: float
    sample: int


Category = Literal["dog-food", "dog-treats"]


class CategoryAov(BaseModel):
    category: Category
    categoryLabel: str
    categoryLabelZh: str
    buckets: list[AovBucket]
    insight: str
    insightZh: str


class InstallProfile(BaseModel):
    category: Category
    scenario: str
    scenarioZh: str
    diyTime: str
    proTime: str
    laborCost: str
    difficulty: Literal["easy", "moderate", "hard", "pro-only"]
    needsElectrician: bool
    needsLicensedPlumber: bool
    notes: str
    notesZh: str
    videoUrl: Optional[str] = None
    source: SourceRef


class BundleObservation(BaseModel):
    brand: str
    product: str
    productZh: Optional[str] = None
    type: Literal["single", "bundle", "trade-program"]
    detail: str
    detailZh: str
    url: str
    source: SourceRef


class CategoryDataset(BaseModel):
    category: Category
    competitors: list[Competitor]
    aov: CategoryAov
    bundles: list[BundleObservation]
    installs: list[InstallProfile]


class MetaInfo(BaseModel):
    generatedAt: str
    scriptVersion: str
    sources: list[SourceRef]


# ---- Review insights ---------------------------------------------------------

ReviewChannel = Literal["amazon", "chewy", "dtc", "trustpilot", "reddit"]


class RawReview(BaseModel):
    channel: ReviewChannel
    productId: str
    title: Optional[str] = None
    body: str
    rating: Optional[float] = None
    verified: Optional[bool] = None
    helpful: Optional[int] = None
    date: Optional[str] = None
    reviewer: Optional[str] = None
    url: Optional[str] = None


class InsightTheme(BaseModel):
    theme: str
    themeZh: Optional[str] = None
    count: int
    quote: str
    quoteRating: Optional[float] = None
    quoteVerified: Optional[bool] = None
    quoteUrl: Optional[str] = None
    channels: list[ReviewChannel]


class ReviewInsight(BaseModel):
    sku: str
    brand: str
    product: str
    productZh: Optional[str] = None
    category: Category
    asin: Optional[str] = None
    totalReviews: int
    averageRating: Optional[float] = None
    pros: list[InsightTheme]
    cons: list[InsightTheme]
    channelBreakdown: dict[str, int] = Field(default_factory=dict)
    generator: Literal["cursor", "gemini", "openai", "anthropic", "manual"] = "cursor"
    lastUpdated: str
    sourcesUsed: list[SourceRef]


# ---- YouTube videos --------------------------------------------------------

VideoIntent = Literal["review", "install", "unboxing", "compare", "general"]
RecencyTier = Literal["1y", "2y", "3y", "older"]


class VideoItem(BaseModel):
    videoId: str
    title: str
    channel: str
    channelId: Optional[str] = None
    channelSubs: Optional[int] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    publishedAt: Optional[str] = None
    duration: Optional[str] = None      # ISO-8601 (PT8M40S)
    durationSec: Optional[int] = None
    thumbnail: Optional[str] = None
    url: str
    query: str                          # the search query that surfaced this video
    intent: VideoIntent = "general"
    publishedWithin: RecencyTier = "older"   # which cascade tier surfaced this video
    score: Optional[float] = None       # log(subs) * log(views) — creator value


class SkuVideoBundle(BaseModel):
    sku: str
    brand: str
    product: str
    productZh: Optional[str] = None
    category: Category
    videos: list[VideoItem]
    lastUpdated: str


class CategoryVideos(BaseModel):
    category: Category
    generatedAt: str
    items: list[SkuVideoBundle]


__all__ = [
    "AovBucket",
    "BundleObservation",
    "CategoryAov",
    "CategoryDataset",
    "CategoryVideos",
    "Competitor",
    "FreeShippingBenchmark",
    "InfluencerEntry",
    "InsightTheme",
    "InstallProfile",
    "MetaInfo",
    "PriceInfo",
    "RawReview",
    "ReviewChannel",
    "ReviewInsight",
    "SeasonalityPoint",
    "ShippingMode",
    "LeadTimeDays",
    "RecencyTier",
    "SkuVideoBundle",
    "SourceRef",
    "VideoItem",
    "VideoIntent",
    "now_iso",
]
