"""Aggregate pain points across SKUs by category.

For each category we walk every `review_insights/<sku>.json`, group similar
themes by keyword buckets, and emit:

  web/public/data/painpoints.json
    {
      "<category>": {
        "buckets": [
          {
            "id":          "<kebab>",
            "label":       "<English summary>",
            "labelZh":     "<Chinese summary>",
            "icon":        "<emoji>",
            "totalCount":  <sum of theme counts>,
            "skuCount":    <distinct SKUs that mention this bucket>,
            "skuBreakdown":[{"sku":..., "count":...}, ...],
            "sampleQuote": "...",
            "quoteSku":    "...",
            "quoteUrl":    "..." | null
          }
        ],
        "skuList": [{"sku","brand","product","productZh"}],
        "matrix":  {<bucketId>: {<sku>: count}}   // for heatmap
      },
      ...
    }

Pure local processing, no network calls. Run with:
    python -m analyze.painpoints
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
INSIGHT_DIR = (ROOT / "../web/public/data/review_insights").resolve()
OUTPUT = (ROOT / "../web/public/data/painpoints.json").resolve()


# Each bucket: (id, label, labelZh, icon, [keyword/phrase needles for matching])
# Needles are lowercased and matched against `theme + themeZh + quote`.
# Order matters: more specific buckets first.
BUCKETS: list[dict] = [
    {
        "id": "digestive-upset",
        "label": "Digestive upset / loose stools after switching",
        "labelZh": "换粮后肠胃不适 / 软便",
        "icon": "🤢",
        "needles": [
            "digestive upset",
            "upset stomach",
            "loose stools",
            "loose stool",
            "diarrhea",
            "soft stool",
            "vomit",
            "胃",
            "肠胃",
            "软便",
            "腹泻",
        ],
    },
    {
        "id": "palatability-refusal",
        "label": "Dog refuses to eat / low palatability",
        "labelZh": "拒食 / 适口性差",
        "icon": "🙅",
        "needles": [
            "won't eat",
            "wouldn't eat",
            "refused to eat",
            "picky eater",
            "lost interest",
            "sniffed it and walked away",
            "doesn't like the taste",
            "适口性",
            "拒食",
            "不爱吃",
        ],
    },
    {
        "id": "allergen-reaction",
        "label": "Allergic reaction / itching / skin issues",
        "labelZh": "过敏反应 / 发痒 / 皮肤问题",
        "icon": "⚠️",
        "needles": [
            "allergic",
            "allergy",
            "itchy",
            "itching",
            "hives",
            "skin issue",
            "chicken allergy",
            "wheat allergy",
            "过敏",
            "皮肤",
            "发痒",
        ],
    },
    {
        "id": "price-value",
        "label": "Price too high for bag size / value",
        "labelZh": "单磅价格偏高 / 性价比低",
        "icon": "💰",
        "needles": [
            "too expensive",
            "pricey",
            "hard to justify",
            "overpriced",
            "costly",
            "$3/lb",
            "性价比",
            "太贵",
            "价格高",
        ],
    },
    {
        "id": "shipping-damage",
        "label": "Packaging damage / stale product on arrival",
        "labelZh": "运输破损 / 到货不新鲜",
        "icon": "📦",
        "needles": [
            "bag was torn",
            "arrived damaged",
            "damaged on arrival",
            "stale",
            "went stale",
            "broken seal",
            "crushed box",
            "包装破损",
            "受潮",
            "不新鲜",
        ],
    },
    {
        "id": "subscription-friction",
        "label": "Subscription hard to cancel / auto-renew surprise",
        "labelZh": "订阅难取消 / 自动续费",
        "icon": "🔒",
        "needles": [
            "cancel",
            "cancellation",
            "auto renew",
            "auto-renew",
            "subscription",
            "renewal",
            "订阅",
            "自动续费",
            "取消困难",
        ],
    },
    {
        "id": "too-hard",
        "label": "Treat too hard for seniors / small breeds",
        "labelZh": "零食太硬，不适合老年犬/小型犬",
        "icon": "🦷",
        "needles": [
            "too hard",
            "hard to chew",
            "couldn't chew",
            "senior dog",
            "small breed",
            "broken tooth",
            "太硬",
            "难咬",
            "小型犬",
            "老年犬",
        ],
    },
    {
        "id": "stale-fast",
        "label": "Treats go stale / soft quickly after opening",
        "labelZh": "开封后很快受潮变软",
        "icon": "💧",
        "needles": [
            "stale quickly",
            "got soft",
            "went soft",
            "lost crunch",
            "after opening",
            "受潮",
            "变软",
            "开封后",
        ],
    },
    {
        "id": "portion-calories",
        "label": "Easy to overfeed / calories too high",
        "labelZh": "容易过量喂食 / 热量偏高",
        "icon": "📈",
        "needles": [
            "too many calories",
            "gained weight",
            "gained 3 lbs",
            "easy to overfeed",
            "weight gain",
            "high calorie",
            "热量高",
            "发胖",
            "过量喂食",
        ],
    },
    {
        "id": "size-mismatch",
        "label": "Wrong size for dog weight class",
        "labelZh": "尺寸与犬体重等级不匹配",
        "icon": "📏",
        "needles": [
            "too big",
            "too small",
            "wrong size",
            "for my 15 lb",
            "weight class",
            "size is way too big",
            "尺寸不合适",
            "太大",
            "太小",
        ],
    },
    {
        "id": "customer-service",
        "label": "Customer service slow / no clear resolution",
        "labelZh": "客服响应慢 / 处理不清晰",
        "icon": "📞",
        "needles": [
            "customer service",
            "support",
            "no response",
            "unresponsive",
            "no resolution",
            "客服",
            "售后",
            "不回复",
        ],
    },
]


def _match_bucket(theme: str, theme_zh: str | None, quote: str | None) -> str | None:
    """Return the FIRST matching bucket id, else None."""
    haystack = " ".join(
        s.lower() for s in (theme or "", theme_zh or "", quote or "") if s
    )
    for b in BUCKETS:
        for needle in b["needles"]:
            if needle.lower() in haystack:
                return b["id"]
    return None


def _category_label(cat: str) -> tuple[str, str]:
    return {
        "dog-food": ("Dog Food", "犬用主食"),
        "dog-treats": ("Dog Treats", "犬用零食"),
    }.get(cat, (cat, cat))


def aggregate() -> dict:
    insights: list[dict] = []
    for path in sorted(INSIGHT_DIR.glob("*.json")):
        try:
            insights.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue

    by_category: dict[str, list[dict]] = defaultdict(list)
    for ins in insights:
        by_category[ins["category"]].append(ins)

    out: dict = {}
    for cat, items in by_category.items():
        bucket_acc: dict[str, dict] = {}
        matrix: dict[str, dict[str, int]] = defaultdict(dict)
        sku_list: list[dict] = []

        for ins in items:
            sku = ins["sku"]
            sku_list.append(
                {
                    "sku": sku,
                    "brand": ins.get("brand"),
                    "product": ins.get("product"),
                    "productZh": ins.get("productZh"),
                }
            )
            for con in ins.get("cons", []):
                bid = _match_bucket(con.get("theme"), con.get("themeZh"), con.get("quote"))
                if not bid:
                    continue
                bucket_acc.setdefault(
                    bid,
                    {
                        "id": bid,
                        "label": next(b["label"] for b in BUCKETS if b["id"] == bid),
                        "labelZh": next(b["labelZh"] for b in BUCKETS if b["id"] == bid),
                        "icon": next(b["icon"] for b in BUCKETS if b["id"] == bid),
                        "totalCount": 0,
                        "skuSet": set(),
                        "skuBreakdown": defaultdict(int),
                        "sampleQuote": None,
                        "quoteSku": None,
                        "quoteUrl": None,
                        "quoteRating": None,
                    },
                )
                acc = bucket_acc[bid]
                count = int(con.get("count") or 1)
                acc["totalCount"] += count
                acc["skuSet"].add(sku)
                acc["skuBreakdown"][sku] += count
                matrix[bid][sku] = matrix[bid].get(sku, 0) + count
                # Pick the longest quote we've seen so far as the canonical sample.
                quote = (con.get("quote") or "").strip()
                if quote and len(quote) > len(acc["sampleQuote"] or ""):
                    acc["sampleQuote"] = quote
                    acc["quoteSku"] = sku
                    acc["quoteUrl"] = con.get("quoteUrl")
                    acc["quoteRating"] = con.get("quoteRating")

        # Finalise: convert sets and sort buckets by skuCount desc, then totalCount desc.
        bucket_list: list[dict] = []
        for b in bucket_acc.values():
            b["skuCount"] = len(b["skuSet"])
            b["skuBreakdown"] = sorted(
                ({"sku": k, "count": v} for k, v in b["skuBreakdown"].items()),
                key=lambda x: -x["count"],
            )
            b.pop("skuSet")
            bucket_list.append(b)
        bucket_list.sort(key=lambda b: (-b["skuCount"], -b["totalCount"]))

        label_en, label_zh = _category_label(cat)
        out[cat] = {
            "category": cat,
            "label": label_en,
            "labelZh": label_zh,
            "buckets": bucket_list,
            "skuList": sku_list,
            "matrix": matrix,
        }

    return out


def main() -> None:
    data = aggregate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    for cat, blob in data.items():
        print(f"\n{cat}: {len(blob['buckets'])} buckets, {len(blob['skuList'])} SKUs")
        for b in blob["buckets"][:8]:
            print(f"  {b['icon']}  {b['label']:50s}  ({b['skuCount']} SKUs · {b['totalCount']} mentions)")


if __name__ == "__main__":
    main()
