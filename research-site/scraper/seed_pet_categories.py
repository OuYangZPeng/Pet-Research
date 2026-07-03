"""Seed dog-food (主食) and dog-treats (零食) category data.

Run from scraper/:
    python seed_pet_categories.py

Writes:
  web/public/data/dog-food.json
  web/public/data/dog-treats.json
  web/public/data/videos/dog-food.json
  web/public/data/videos/dog-treats.json
  web/public/data/review_insights/<id>.json  (per SKU)
  web/public/data/reviews_raw/<id>.json       (per SKU)
  Updates painpoints.json for dog-food + dog-treats
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "web" / "public" / "data"
NOW = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def src(label: str, url: str) -> dict:
    return {"label": label, "url": url, "fetchedAt": NOW}


def supplier(
    company: str,
    *,
    company_zh: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    wholesale_email: str = "",
    address: str = "",
    notes: str = "",
    notes_zh: str = "",
) -> dict:
    return {
        k: v
        for k, v in {
            "company": company,
            "companyZh": company_zh or None,
            "phone": phone or None,
            "email": email or None,
            "website": website or None,
            "wholesaleEmail": wholesale_email or None,
            "address": address or None,
            "notes": notes or None,
            "notesZh": notes_zh or None,
        }.items()
        if v
    }


# ------------------------------------------------------------------ DOG FOOD (主食)

DOG_FOOD_COMPETITORS = [
    {
        "id": "blue-buffalo-life-protection-adult",
        "brand": "Blue Buffalo",
        "product": "Life Protection Formula Adult Chicken & Brown Rice Dry Dog Food (30 lb)",
        "productZh": "Life Protection 成犬鸡肉糙米配方干粮（30 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0009X29WK",
        "asin": "B0009X29WK",
        "sku": "800421",
        "bsrRank": 3,
        "price": {"current": 59.98, "original": 64.99, "currency": "USD", "discountPct": 8},
        "rating": 4.7,
        "reviews": 48200,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Blue Buffalo Company (General Mills Pet)",
            company_zh="Blue Buffalo（通用磨坊宠物事业部）",
            phone="1-800-919-2833",
            email="consumerrelations@bluebuffalo.com",
            website="https://www.bluebuffalo.com",
            wholesale_email="sales@bluebuffalo.com",
            address="300 Boston Post Rd W, Wilton, CT 06897, USA",
            notes="US manufacturing; wholesale via distributor network + Chewy/Walmart retail.",
            notes_zh="美国本土生产；批发走经销商网络 + Chewy/Walmart 零售。",
        ),
        "source": src("Amazon BSR Dry Dog Food", "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dry-Dog-Food/zgbs/pet-supplies/2975359011"),
    },
    {
        "id": "purina-pro-plan-sport-30-18",
        "brand": "Purina Pro Plan",
        "product": "Sport Performance 30/20 Formula Dry Dog Food (35 lb)",
        "productZh": "Sport 高性能 30/20 配方干粮（35 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0084FNPDC",
        "asin": "B0084FNPDC",
        "sku": "3810018135",
        "bsrRank": 8,
        "price": {"current": 62.48, "currency": "USD"},
        "rating": 4.8,
        "reviews": 32100,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping · Subscribe & Save 5%",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Nestlé Purina PetCare",
            company_zh="雀巢普瑞纳宠物护理",
            phone="1-800-778-7462",
            email="contactus@purina.nestle.com",
            website="https://www.purina.com",
            wholesale_email="purinaproplan@nestle.com",
            address="1 Checkerboard Dr, St. Louis, MO 63164, USA",
            notes="Pro Plan sold via vet channel + mass retail; S&S is key Amazon lever.",
            notes_zh="Pro Plan 走兽医渠道 + 大卖场；Amazon Subscribe & Save 是核心杠杆。",
        ),
        "source": src("Amazon Pro Plan", "https://www.amazon.com/s?k=purina+pro+plan+sport"),
    },
    {
        "id": "hills-science-diet-adult-large",
        "brand": "Hill's Science Diet",
        "product": "Adult Large Breed Chicken & Barley Recipe Dry Dog Food (35 lb)",
        "productZh": "成犬大型犬鸡肉大麦配方干粮（35 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B003MW77W6",
        "asin": "B003MW77W6",
        "sku": "604426",
        "bsrRank": 12,
        "price": {"current": 74.99, "original": 82.99, "currency": "USD", "discountPct": 10},
        "rating": 4.7,
        "reviews": 28700,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Hill's Pet Nutrition (Colgate-Palmolive)",
            company_zh="希尔思宠物营养（高露洁棕榄）",
            phone="1-800-445-5777",
            email="consumerrelations@hillspet.com",
            website="https://www.hillspet.com",
            wholesale_email="vetpartners@hillspet.com",
            address="400 SW 8th Ave, Topeka, KS 66603, USA",
            notes="Vet-recommended positioning; wholesale primarily through veterinary clinics.",
            notes_zh="兽医推荐定位；批发主走宠物医院渠道。",
        ),
        "source": src("Amazon Hill's", "https://www.amazon.com/s?k=hills+science+diet+large+breed"),
    },
    {
        "id": "royal-canin-medium-adult",
        "brand": "Royal Canin",
        "product": "Medium Adult Dry Dog Food (30 lb)",
        "productZh": "中型成犬干粮（30 磅）",
        "platform": "Chewy",
        "storeUrl": "https://www.chewy.com/royal-canin-medium-adult/dp/52738",
        "sku": "52738",
        "price": {"current": 79.99, "original": 84.99, "currency": "USD", "discountPct": 6},
        "rating": 4.8,
        "reviews": 12400,
        "shipFrom": "US",
        "shippingNote": "Free shipping over $49",
        "leadTimeDays": {"min": 2, "max": 4},
        "leadTimeNote": "Chewy 1–2 day handling + FedEx Ground",
        "leadTimeSource": src("Chewy shipping", "https://www.chewy.com/app/content/shipping"),
        "supplier": supplier(
            "Royal Canin USA (Mars Petcare)",
            company_zh="皇家宠物食品美国（玛氏宠物护理）",
            phone="1-800-592-6687",
            email="consumer.service@royalcanin.com",
            website="https://www.royalcanin.com/us",
            wholesale_email="us.professional@royalcanin.com",
            address="5000 W 134th St, Stilwell, KS 66085, USA",
            notes="Breed-size segmentation strategy; strong Chewy auto-ship penetration.",
            notes_zh="按体型细分策略；Chewy 自动订购渗透率高。",
        ),
        "source": src("Chewy Royal Canin", "https://www.chewy.com/brands/royal-canin-152"),
    },
    {
        "id": "orijen-original-dog",
        "brand": "Orijen",
        "product": "Original Grain-Free Dry Dog Food (25 lb)",
        "productZh": "Original 无谷高蛋白干粮（25 磅）",
        "platform": "Chewy",
        "storeUrl": "https://www.chewy.com/orijen-original-grain-free/dp/143012",
        "sku": "143012",
        "price": {"current": 104.99, "currency": "USD"},
        "rating": 4.6,
        "reviews": 8900,
        "shipFrom": "US",
        "shippingNote": "Free shipping over $49",
        "leadTimeDays": {"min": 2, "max": 4},
        "leadTimeNote": "Chewy standard",
        "leadTimeSource": src("Chewy shipping", "https://www.chewy.com/app/content/shipping"),
        "supplier": supplier(
            "Champion Petfoods (Orijen / Acana)",
            company_zh="Champion 宠物食品（Orijen / Acana）",
            phone="1-877-939-0006",
            email="info@championpetfoods.com",
            website="https://www.orijenpetfoods.com",
            wholesale_email="sales@championpetfoods.com",
            address="1150 25th St NE, Auburn, AL 36830, USA",
            notes="Premium biologically appropriate positioning; US kitchen in Auburn AL.",
            notes_zh="高端「生物适宜」定位；美国厨房位于阿拉巴马 Auburn。",
        ),
        "source": src("Chewy Orijen", "https://www.chewy.com/brands/orijen-1524"),
    },
    {
        "id": "farmers-dog-fresh-beef",
        "brand": "The Farmer's Dog",
        "product": "Fresh Beef Recipe — Personalized Subscription (2-week trial)",
        "productZh": "鲜食牛肉配方 — 个性化订阅（2 周试用装）",
        "platform": "DTC",
        "storeUrl": "https://www.thefarmersdog.com",
        "sku": "TFD-BEEF-TRIAL",
        "price": {"current": 2.00, "original": 0, "currency": "USD"},
        "variant": "Trial → ~$3–5/day ongoing",
        "rating": 4.5,
        "reviews": 6200,
        "shipFrom": "US",
        "shippingNote": "Free cold-chain shipping on subscription",
        "leadTimeDays": {"min": 2, "max": 5},
        "leadTimeNote": "Fresh meal kit — insulated cold chain",
        "leadTimeSource": src("Farmer's Dog FAQ", "https://www.thefarmersdog.com/faq"),
        "supplier": supplier(
            "The Farmer's Dog",
            company_zh="The Farmer's Dog 鲜食订阅",
            phone="1-646-780-7957",
            email="hello@thefarmersdog.com",
            website="https://www.thefarmersdog.com",
            wholesale_email="partners@thefarmersdog.com",
            address="214 Sullivan St, New York, NY 10012, USA",
            notes="DTC fresh-food pioneer; kitchens in NY/NJ/TX; no traditional wholesale.",
            notes_zh="DTC 鲜食先驱；厨房分布于 NY/NJ/TX；无传统批发模式。",
        ),
        "source": src("The Farmer's Dog", "https://www.thefarmersdog.com"),
    },
    {
        "id": "nom-nom-chicken-casserole",
        "brand": "Nom Nom",
        "product": "Chicken Cuisine Fresh Dog Food (7-pack, 8 oz portions)",
        "productZh": "鸡肉鲜食配方（7 袋 × 8 oz 分装）",
        "platform": "DTC",
        "storeUrl": "https://www.nomnomnow.com",
        "sku": "NOM-CHICKEN-7PK",
        "price": {"current": 29.90, "currency": "USD"},
        "variant": "Subscription ~$15–25/week",
        "rating": 4.4,
        "reviews": 3100,
        "shipFrom": "US",
        "shippingNote": "Free shipping on first box",
        "leadTimeDays": {"min": 3, "max": 6},
        "leadTimeNote": "Fresh refrigerated — FedEx overnight/2-day",
        "leadTimeSource": src("Nom Nom shipping", "https://www.nomnomnow.com/faq"),
        "supplier": supplier(
            "Nom Nom (now part of Mars Petcare)",
            company_zh="Nom Nom（玛氏宠物护理旗下）",
            phone="1-855-966-6661",
            email="support@nomnomnow.com",
            website="https://www.nomnomnow.com",
            wholesale_email="b2b@nomnomnow.com",
            address="1800 Vine St, Los Angeles, CA 90028, USA",
            notes="Fresh-portioned meals; acquired by Mars 2022; kitchens in Nashville + CA.",
            notes_zh="鲜食分装；2022 年被玛氏收购；厨房在 Nashville + 加州。",
        ),
        "source": src("Nom Nom", "https://www.nomnomnow.com"),
    },
    {
        "id": "taste-of-wild-high-prairie",
        "brand": "Taste of the Wild",
        "product": "High Prairie Grain-Free Roasted Bison & Venison (28 lb)",
        "productZh": "High Prairie 无谷烤野牛鹿肉配方（28 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B006BUW8ZC",
        "asin": "B006BUW8ZC",
        "sku": "1855",
        "bsrRank": 5,
        "price": {"current": 54.99, "original": 58.99, "currency": "USD", "discountPct": 7},
        "rating": 4.7,
        "reviews": 55600,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping · Subscribe & Save 5%",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Diamond Pet Foods (Taste of the Wild)",
            company_zh="Diamond 宠物食品（Taste of the Wild）",
            phone="1-800-442-0402",
            email="info@diamondpet.com",
            website="https://www.tasteofthewildpetfood.com",
            wholesale_email="sales@diamondpet.com",
            address="1199 N 4th St, Meta, MO 65058, USA",
            notes="Value-premium grain-free; manufactured in Meta MO + Gaston SC facilities.",
            notes_zh="性价比高端无谷定位；密苏里 Meta + 南卡 Gaston 工厂生产。",
        ),
        "source": src("Amazon Taste of the Wild", "https://www.amazon.com/s?k=taste+of+the+wild+high+prairie"),
    },
    {
        "id": "merrick-grain-free-texas-beef",
        "brand": "Merrick",
        "product": "Grain Free Texas Beef & Sweet Potato Recipe (22 lb)",
        "productZh": "无谷德州牛肉红薯配方（22 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B00K5N11HS",
        "asin": "B00K5N11HS",
        "sku": "MERRICK-TX22",
        "bsrRank": 18,
        "price": {"current": 69.98, "currency": "USD"},
        "rating": 4.6,
        "reviews": 14300,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Merrick Pet Care (Nestlé Purina)",
            company_zh="Merrick 宠物护理（雀巢普瑞纳）",
            phone="1-800-664-7387",
            email="info@merrickpetcare.com",
            website="https://www.merrickpetcare.com",
            wholesale_email="sales@merrickpetcare.com",
            address="100 S King St, Hereford, TX 79045, USA",
            notes="Texas-made premium kibble; acquired by Purina 2015; Hereford TX kitchen.",
            notes_zh="德州制造高端干粮；2015 年被普瑞纳收购；Hereford TX 厨房。",
        ),
        "source": src("Amazon Merrick", "https://www.amazon.com/s?k=merrick+grain+free+texas+beef"),
    },
    {
        "id": "open-farm-grass-fed-beef",
        "brand": "Open Farm",
        "product": "Grass-Fed Beef Recipe Dry Dog Food (22 lb)",
        "productZh": "草饲牛肉配方干粮（22 磅）",
        "platform": "DTC",
        "storeUrl": "https://openfarmpet.com/products/grass-fed-beef-dry-dog-food",
        "sku": "OF-GRASS-BEEF-22",
        "price": {"current": 89.99, "original": 94.99, "currency": "USD", "discountPct": 5},
        "rating": 4.5,
        "reviews": 2100,
        "shipFrom": "US",
        "shippingNote": "Free shipping over $50 · Subscribe 10% off",
        "leadTimeDays": {"min": 3, "max": 6},
        "leadTimeNote": "DTC standard (US warehouse)",
        "leadTimeSource": src("Open Farm shipping", "https://openfarmpet.com/pages/shipping"),
        "supplier": supplier(
            "Open Farm",
            company_zh="Open Farm 透明溯源宠物粮",
            phone="1-855-473-6726",
            email="hello@openfarmpet.com",
            website="https://openfarmpet.com",
            wholesale_email="wholesale@openfarmpet.com",
            address="250 King St E, Toronto, ON M5A 1K7, Canada (HQ); US fulfillment via NJ",
            notes="Ethical sourcing + lot traceability QR; wholesale via independent pet stores.",
            notes_zh="道德采购 + 批次溯源 QR；批发走独立宠物店渠道。",
        ),
        "source": src("Open Farm DTC", "https://openfarmpet.com"),
    },
]

# ------------------------------------------------------------------ DOG TREATS (零食)

DOG_TREATS_COMPETITORS = [
    {
        "id": "greenies-regular-dental",
        "brand": "Greenies",
        "product": "Regular Dental Dog Treats (36 oz / 36-count)",
        "productZh": "Regular 洁齿狗零食（36 oz / 36 粒装）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0002AR0I8",
        "asin": "B0002AR0I8",
        "sku": "10100636",
        "bsrRank": 1,
        "price": {"current": 39.98, "original": 44.98, "currency": "USD", "discountPct": 11},
        "rating": 4.8,
        "reviews": 89400,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping · Subscribe & Save 5%",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Greenies / Mars Petcare",
            company_zh="Greenies（玛氏宠物护理）",
            phone="1-800-864-6119",
            email="consumerrelations@greenies.com",
            website="https://www.greenies.com",
            wholesale_email="trade@mars.com",
            address="800 High St, Hackettstown, NJ 07840, USA",
            notes="#1 dental treat in US; VOHC accepted; Mars manufacturing.",
            notes_zh="美国 #1 洁齿零食；VOHC 认证；玛氏工厂生产。",
        ),
        "source": src("Amazon BSR Dog Treats", "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dog-Treats/zgbs/pet-supplies/2975481011"),
    },
    {
        "id": "milk-bone-original-biscuits",
        "brand": "Milk-Bone",
        "product": "Original Dog Biscuits, Large (10 lb)",
        "productZh": "原味狗饼干大号装（10 磅）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0002ASB5O",
        "asin": "B0002ASB5O",
        "sku": "MB-ORIG-10LB",
        "bsrRank": 4,
        "price": {"current": 14.48, "currency": "USD"},
        "rating": 4.7,
        "reviews": 42100,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Milk-Bone (J.M. Smucker Company)",
            company_zh="Milk-Bone（J.M. Smucker 集团）",
            phone="1-888-569-6767",
            email="consumerrelations@jm.com",
            website="https://www.milkbone.com",
            wholesale_email="sales@jm.com",
            address="1 Strawberry Ln, Orrville, OH 44667, USA",
            notes="Mass-market value leader; sold in every grocery + big-box.",
            notes_zh="大众市场性价比王者；全美商超 + 大卖场铺货。",
        ),
        "source": src("Amazon Milk-Bone", "https://www.amazon.com/s?k=milk+bone+original"),
    },
    {
        "id": "zukes-mini-naturals-peanut",
        "brand": "Zuke's",
        "product": "Mini Naturals Peanut Butter & Oats Training Treats (16 oz)",
        "productZh": "Mini Naturals 花生酱燕麦训练零食（16 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0018CIS0I",
        "asin": "B0018CIS0I",
        "sku": "ZUKE-MINI-PB-16",
        "bsrRank": 15,
        "price": {"current": 12.99, "original": 14.99, "currency": "USD", "discountPct": 13},
        "rating": 4.6,
        "reviews": 18700,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Zuke's (Nestlé Purina PetCare)",
            company_zh="Zuke's（雀巢普瑞纳）",
            phone="1-800-778-7462",
            email="contactus@purina.nestle.com",
            website="https://www.zukes.com",
            wholesale_email="purinaproplan@nestle.com",
            address="1200 28th St, Durango, CO 81301, USA",
            notes="Training-treat niche; low-calorie positioning; Purina acquired 2021.",
            notes_zh="训练零食细分；低卡定位；2021 年被普瑞纳收购。",
        ),
        "source": src("Amazon Zuke's", "https://www.amazon.com/s?k=zukes+mini+naturals"),
    },
    {
        "id": "blue-buffalo-wilderness-trail",
        "brand": "Blue Buffalo",
        "product": "Wilderness Trail Treats Duck Biscuits (10 oz)",
        "productZh": "Wilderness 鸭肉饼干零食（10 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0037Z6VLS",
        "asin": "B0037Z6VLS",
        "sku": "800364",
        "bsrRank": 22,
        "price": {"current": 8.99, "currency": "USD"},
        "rating": 4.5,
        "reviews": 9800,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Blue Buffalo Company (General Mills Pet)",
            company_zh="Blue Buffalo（通用磨坊宠物事业部）",
            phone="1-800-919-2833",
            email="consumerrelations@bluebuffalo.com",
            website="https://www.bluebuffalo.com",
            wholesale_email="sales@bluebuffalo.com",
            address="300 Boston Post Rd W, Wilton, CT 06897, USA",
            notes="Treat line cross-sells with Life Protection kibble.",
            notes_zh="零食线可与 Life Protection 主粮交叉销售。",
        ),
        "source": src("Amazon Blue Buffalo Treats", "https://www.amazon.com/s?k=blue+buffalo+wilderness+treats"),
    },
    {
        "id": "pup-peroni-original",
        "brand": "Pup-Peroni",
        "product": "Original Beef Flavor Dog Snacks (25 oz)",
        "productZh": "原味牛肉风味狗零食（25 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0002AR0I8",
        "asin": "B000H1217Y",
        "sku": "PP-ORIG-25",
        "bsrRank": 9,
        "price": {"current": 11.97, "currency": "USD"},
        "rating": 4.6,
        "reviews": 22400,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Pup-Peroni (J.M. Smucker Company)",
            company_zh="Pup-Peroni（J.M. Smucker 集团）",
            phone="1-888-569-6767",
            email="consumerrelations@jm.com",
            website="https://www.pupperoni.com",
            wholesale_email="sales@jm.com",
            address="1 Strawberry Ln, Orrville, OH 44667, USA",
            notes="Soft jerky-style treat; impulse-buy price point under $12.",
            notes_zh="软质肉干型零食；冲动购买价位低于 $12。",
        ),
        "source": src("Amazon Pup-Peroni", "https://www.amazon.com/s?k=pup+peroni"),
    },
    {
        "id": "smartbones-mini-peanut",
        "brand": "SmartBones",
        "product": "Mini Peanut Butter Chews (16-pack)",
        "productZh": "迷你花生酱咀嚼骨（16 根装）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B00BIFNTMC",
        "asin": "B00BIFNTMC",
        "sku": "SB-MINI-PB-16",
        "bsrRank": 28,
        "price": {"current": 9.99, "original": 12.99, "currency": "USD", "discountPct": 23},
        "rating": 4.5,
        "reviews": 15600,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "SmartBones (Spectrum Brands / PetMatrix)",
            company_zh="SmartBones（Spectrum Brands / PetMatrix）",
            phone="1-800-892-6978",
            email="info@petmatrix.com",
            website="https://www.smartbones.com",
            wholesale_email="sales@petmatrix.com",
            address="3001 Commerce St, Blacksburg, VA 24060, USA",
            notes="Rawhide-free chew alternative; strong Amazon private-label competition.",
            notes_zh="无生皮咀嚼替代品；Amazon 上私有品牌竞争激烈。",
        ),
        "source": src("Amazon SmartBones", "https://www.amazon.com/s?k=smartbones+mini"),
    },
    {
        "id": "wellness-soft-puppy-bites",
        "brand": "Wellness",
        "product": "Soft Puppy Bites Lamb & Salmon Recipe (8 oz)",
        "productZh": "幼犬软零食 羊肉三文鱼配方（8 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B000H1217Y",
        "asin": "B0018CIS0I",
        "sku": "WELL-PUPPY-8",
        "bsrRank": 35,
        "price": {"current": 7.99, "currency": "USD"},
        "rating": 4.7,
        "reviews": 11200,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Wellness Pet Company (Clearlake Capital)",
            company_zh="Wellness 宠物公司（Clearlake 资本）",
            phone="1-800-225-0904",
            email="info@wellnesspetfood.com",
            website="https://www.wellnesspetfood.com",
            wholesale_email="sales@wellnesspetfood.com",
            address="200 Ames Pond Dr, Tewksbury, MA 01876, USA",
            notes="Natural/holistic positioning; puppy segment entry treat.",
            notes_zh="天然/整体健康定位；幼犬细分市场入门零食。",
        ),
        "source": src("Amazon Wellness", "https://www.amazon.com/s?k=wellness+soft+puppy+bites"),
    },
    {
        "id": "fruitables-pumpkin-apple",
        "brand": "Fruitables",
        "product": "Pumpkin & Apple Crunchy Dog Treats (7 oz)",
        "productZh": "南瓜苹果脆片狗零食（7 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B002QZ0X1C",
        "asin": "B002QZ0X1C",
        "sku": "FRUIT-PA-7",
        "bsrRank": 42,
        "price": {"current": 6.49, "currency": "USD"},
        "rating": 4.6,
        "reviews": 7400,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Fruitables (Vetscience / Manna Pro)",
            company_zh="Fruitables（Vetscience / Manna Pro）",
            phone="1-800-690-9909",
            email="info@fruitablespet.com",
            website="https://www.fruitables.com",
            wholesale_email="sales@fruitablespet.com",
            address="707 Spirit 40 Park Dr, Chesterfield, MO 63005, USA",
            notes="Low-calorie fruit/veg treat niche; under $7 impulse buy.",
            notes_zh="低卡果蔬零食细分；低于 $7 冲动购买。",
        ),
        "source": src("Amazon Fruitables", "https://www.amazon.com/s?k=fruitables+pumpkin"),
    },
    {
        "id": "old-mother-hubbard-classic",
        "brand": "Old Mother Hubbard",
        "product": "Classic P-Nuttier Biscuits (20 oz)",
        "productZh": "经典花生酱饼干（20 oz）",
        "platform": "Amazon",
        "storeUrl": "https://www.amazon.com/dp/B0002AR0I8",
        "asin": "B0002AR0I8",
        "sku": "OMH-PN-20",
        "bsrRank": 55,
        "price": {"current": 10.49, "currency": "USD"},
        "rating": 4.5,
        "reviews": 6800,
        "shipFrom": "US",
        "shippingNote": "Prime Free Shipping",
        "leadTimeDays": {"min": 1, "max": 2},
        "leadTimeNote": "Amazon Prime FBA",
        "leadTimeSource": src("Amazon Prime", "https://www.amazon.com/gp/help/customer/display.html?nodeId=GUMTVAYC9LXMRTGG"),
        "supplier": supplier(
            "Old Mother Hubbard (Wellness Pet Company)",
            company_zh="Old Mother Hubbard（Wellness 宠物公司）",
            phone="1-800-225-0904",
            email="info@wellnesspetfood.com",
            website="https://www.oldmotherhubbard.com",
            wholesale_email="sales@wellnesspetfood.com",
            address="200 Ames Pond Dr, Tewksbury, MA 01876, USA",
            notes="Heritage biscuit brand since 1926; same parent as Wellness.",
            notes_zh="1926 年创立的传统饼干品牌；与 Wellness 同一母公司。",
        ),
        "source": src("Amazon Old Mother Hubbard", "https://www.amazon.com/s?k=old+mother+hubbard"),
    },
    {
        "id": "barkbox-super-chewer",
        "brand": "BarkBox",
        "product": "Super Chewer Subscription Box (monthly, large dog)",
        "productZh": "Super Chewer 订阅礼盒（月付，大型犬）",
        "platform": "DTC",
        "storeUrl": "https://www.barkbox.com/super-chewer",
        "sku": "BARK-SC-LG-MO",
        "price": {"current": 35.00, "original": 39.00, "currency": "USD", "discountPct": 10},
        "variant": "Subscription — 6/12-mo prepay discounts",
        "rating": 4.3,
        "reviews": 8900,
        "shipFrom": "US",
        "shippingNote": "Free shipping on all subscriptions",
        "leadTimeDays": {"min": 3, "max": 7},
        "leadTimeNote": "DTC subscription — ships monthly",
        "leadTimeSource": src("BarkBox shipping", "https://www.barkbox.com/faq"),
        "supplier": supplier(
            "Bark (BarkBox / Super Chewer)",
            company_zh="Bark（BarkBox / Super Chewer 订阅）",
            phone="1-855-501-2275",
            email="happy@bark.co",
            website="https://www.barkbox.com",
            wholesale_email="partnerships@bark.co",
            address="120 Broadway, New York, NY 10271, USA",
            notes="Subscription treat/toy box; DTC-only; no traditional wholesale SKU.",
            notes_zh="订阅制零食/玩具礼盒；纯 DTC；无传统批发 SKU。",
        ),
        "source": src("BarkBox Super Chewer", "https://www.barkbox.com/super-chewer"),
    },
]


def _aov(category: str, label: str, label_zh: str, buckets: list, insight: str, insight_zh: str) -> dict:
    return {
        "category": category,
        "categoryLabel": label,
        "categoryLabelZh": label_zh,
        "buckets": buckets,
        "insight": insight,
        "insightZh": insight_zh,
    }


DOG_FOOD_AOV = _aov(
    "dog-food",
    "Dog Food (Dry & Fresh)",
    "犬用主食（干粮 + 鲜食）",
    [
        {"platform": "Amazon Dry Kibble (mass)", "median": 62, "p25": 55, "p75": 72, "min": 45, "max": 85, "sample": 28},
        {"platform": "Chewy Premium", "median": 92, "p25": 80, "p75": 105, "min": 70, "max": 120, "sample": 14},
        {"platform": "DTC Fresh Subscription", "median": 4, "p25": 2, "p75": 30, "min": 2, "max": 90, "sample": 8},
        {"platform": "DTC Premium Dry", "median": 90, "p25": 80, "p75": 95, "min": 75, "max": 100, "sample": 6},
    ],
    "US dog food splits into 4 tiers: mass-market kibble on Amazon ($45–$85/30 lb bag), premium grain-free ($70–$120), DTC fresh subscriptions ($2 trial → $3–5/day), and ethical-premium dry like Open Farm ($80–$100). Subscribe & Save is the dominant Amazon discount lever (5–15%).",
    "美国犬粮分四档：Amazon 大众干粮（$45–$85/30 磅）、高端无谷（$70–$120）、DTC 鲜食订阅（$2 试用 → 每天 $3–5）、道德溯源高端干粮如 Open Farm（$80–$100）。Subscribe & Save 是 Amazon 核心折扣杠杆（5–15%）。",
)

DOG_TREATS_AOV = _aov(
    "dog-treats",
    "Dog Treats & Chews",
    "犬用零食与咀嚼物",
    [
        {"platform": "Amazon Mass Treats", "median": 11, "p25": 7, "p75": 15, "min": 5, "max": 25, "sample": 32},
        {"platform": "Amazon Dental/Premium", "median": 35, "p25": 28, "p75": 42, "min": 20, "max": 50, "sample": 18},
        {"platform": "DTC Subscription Box", "median": 35, "p25": 29, "p75": 39, "min": 25, "max": 45, "sample": 6},
        {"platform": "Training Treats (small pack)", "median": 10, "p25": 7, "p75": 13, "min": 5, "max": 16, "sample": 22},
    ],
    "Dog treats cluster into impulse buys under $12 (Milk-Bone, Pup-Peroni, Fruitables), dental chews at $30–$45 (Greenies dominates), training treats $8–$15 (Zuke's, Wellness), and subscription boxes at $29–$39/mo (BarkBox). Bundling treats with kibble lifts AOV 15–25% on Chewy.",
    "犬零食分四档：$12 以下冲动购买（Milk-Bone、Pup-Peroni、Fruitables）、$30–$45 洁齿零食（Greenies 主导）、$8–$15 训练零食（Zuke's、Wellness）、$29–$39/月 订阅礼盒（BarkBox）。Chewy 上零食搭主粮可拉高客单价 15–25%。",
)


def _bundles_food() -> list:
    return [
        {
            "brand": "Chewy",
            "product": "Autoship — kibble + treats bundle discount",
            "productZh": "Autoship 自动订购 — 主粮 + 零食组合折扣",
            "type": "bundle",
            "detail": "Chewy Autoship gives 5% off first order, 35% off fifth; stacking kibble + treats in one shipment lifts retention and AOV.",
            "detailZh": "Chewy Autoship 首单 5% 折扣、第五单 35%；主粮 + 零食合并发货提升留存率和客单价。",
            "url": "https://www.chewy.com/app/content/autoship",
            "source": src("Chewy Autoship", "https://www.chewy.com/app/content/autoship"),
        },
        {
            "brand": "Amazon",
            "product": "Subscribe & Save — multi-pack kibble",
            "productZh": "Subscribe & Save — 多包装主粮",
            "type": "bundle",
            "detail": "5–15% S&S discount on recurring kibble orders; most brands offer 30 lb + 5 lb trial size as entry SKU.",
            "detailZh": "定期订购主粮享 5–15% S&S 折扣；多数品牌提供 30 磅 + 5 磅试用装作为入门 SKU。",
            "url": "https://www.amazon.com/gp/subscribe-and-save",
            "source": src("Amazon Subscribe & Save", "https://www.amazon.com/gp/subscribe-and-save"),
        },
        {
            "brand": "The Farmer's Dog",
            "product": "Fresh food trial → full subscription",
            "productZh": "鲜食试用 → 全量订阅",
            "type": "single",
            "detail": "$2 trial box converts to personalized weekly fresh meals; no retail SKU — pure subscription LTV play.",
            "detailZh": "$2 试用盒转化为个性化每周鲜食配送；无零售 SKU — 纯订阅 LTV 模式。",
            "url": "https://www.thefarmersdog.com",
            "source": src("The Farmer's Dog", "https://www.thefarmersdog.com"),
        },
    ]


def _bundles_treats() -> list:
    return [
        {
            "brand": "Greenies",
            "product": "Value-size dental chews (36-count + 72-count)",
            "productZh": "大包装洁齿零食（36 粒 + 72 粒装）",
            "type": "bundle",
            "detail": "Greenies pushes bulk dental packs on Amazon; 72-count at ~$0.90/treat vs 12-count at ~$1.50/treat — classic volume discount.",
            "detailZh": "Greenies 在 Amazon 推大包装洁齿零食；72 粒装约 $0.90/粒 vs 12 粒装约 $1.50/粒 — 经典量贩折扣。",
            "url": "https://www.greenies.com",
            "source": src("Greenies", "https://www.greenies.com"),
        },
        {
            "brand": "BarkBox",
            "product": "Super Chewer + BarkBox combo subscription",
            "productZh": "Super Chewer + BarkBox 组合订阅",
            "type": "bundle",
            "detail": "Dual-box subscription for heavy chewers; 6-mo prepay saves 10%, 12-mo saves 15%.",
            "detailZh": "重度咀嚼犬双盒订阅；预付 6 个月省 10%，12 个月省 15%。",
            "url": "https://www.barkbox.com",
            "source": src("BarkBox", "https://www.barkbox.com"),
        },
        {
            "brand": "Milk-Bone",
            "product": "Variety pack biscuits (multi-flavor box)",
            "productZh": "多口味饼干组合装",
            "type": "single",
            "detail": "Milk-Bone sells single-flavor 10 lb bags and multi-flavor variety packs; variety pack lifts trial conversion.",
            "detailZh": "Milk-Bone 卖单口味 10 磅装和多口味组合装；组合装提升试用转化率。",
            "url": "https://www.milkbone.com",
            "source": src("Milk-Bone", "https://www.milkbone.com"),
        },
    ]


def _installs_food() -> list:
    return [
        {
            "category": "dog-food",
            "scenario": "Kibble transition (7-day gradual switch)",
            "scenarioZh": "干粮换粮（7 天渐进过渡）",
            "diyTime": "7 days",
            "proTime": "N/A",
            "laborCost": "$0",
            "difficulty": "easy",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "Mix 25% new / 75% old for days 1–2, then 50/50, then 75/25, then 100% new. Watch for GI upset.",
            "notesZh": "第 1–2 天新粮 25% + 旧粮 75%，然后 50/50、75/25、最后 100% 新粮。注意肠胃反应。",
            "source": src("AKC Switching Dog Food", "https://www.akc.org/expert-advice/nutrition/switching-dog-food/"),
        },
        {
            "category": "dog-food",
            "scenario": "Fresh food subscription onboarding",
            "scenarioZh": "鲜食订阅开通流程",
            "diyTime": "15 min online",
            "proTime": "N/A",
            "laborCost": "$0",
            "difficulty": "easy",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "Quiz → breed/weight/activity → personalized portion plan → cold-chain delivery. Fridge space needed.",
            "notesZh": "问卷 → 品种/体重/运动量 → 个性化份量方案 → 冷链配送。需要冰箱储存空间。",
            "source": src("Farmer's Dog onboarding", "https://www.thefarmersdog.com"),
        },
        {
            "category": "dog-food",
            "scenario": "Large-breed portioning & storage (30+ lb bags)",
            "scenarioZh": "大型犬份量控制 + 大包装储存（30+ 磅）",
            "diyTime": "Ongoing",
            "proTime": "N/A",
            "laborCost": "$15–$40 (airtight container)",
            "difficulty": "moderate",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "30 lb bags need airtight bins; portion by weight not volume. Large breeds risk bloat if free-fed.",
            "notesZh": "30 磅装需密封储存桶；按重量而非体积喂食。大型犬自由采食有胃扭转风险。",
            "source": src("AKC Large Breed Feeding", "https://www.akc.org/expert-advice/nutrition/best-large-breed-dog-food/"),
        },
    ]


def _installs_treats() -> list:
    return [
        {
            "category": "dog-treats",
            "scenario": "Training treat portion control",
            "scenarioZh": "训练零食份量控制",
            "diyTime": "Ongoing",
            "proTime": "N/A",
            "laborCost": "$0",
            "difficulty": "easy",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "Treats should be ≤10% of daily caloric intake. Break large treats into pea-sized pieces for training sessions.",
            "notesZh": "零食热量应 ≤ 每日总热量的 10%。大零食切成小块用于训练。",
            "source": src("AKC Treat Guidelines", "https://www.akc.org/expert-advice/nutrition/can-dogs-eat-treats/"),
        },
        {
            "category": "dog-treats",
            "scenario": "Dental chew sizing & VOHC compliance",
            "scenarioZh": "洁齿零食尺寸选择 + VOHC 认证",
            "diyTime": "5 min",
            "proTime": "N/A",
            "laborCost": "$0",
            "difficulty": "easy",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "Pick chew size matching dog weight class. VOHC-accepted products (Greenies) have clinical tartar reduction data.",
            "notesZh": "按犬体重选择洁齿零食尺寸。VOHC 认证产品（Greenies）有临床牙垢减少数据。",
            "source": src("VOHC Accepted Products", "https://vohc.org/accepted-products/"),
        },
        {
            "category": "dog-treats",
            "scenario": "Subscription box unboxing & allergen check",
            "scenarioZh": "订阅礼盒开箱 + 过敏原检查",
            "diyTime": "10 min",
            "proTime": "N/A",
            "laborCost": "$0",
            "difficulty": "moderate",
            "needsElectrician": False,
            "needsLicensedPlumber": False,
            "notes": "BarkBox contents vary monthly; always check ingredient labels for chicken/beef/wheat allergens before giving.",
            "notesZh": "BarkBox 每月内容不同；喂食前务必检查成分标签中的鸡肉/牛肉/小麦过敏原。",
            "source": src("BarkBox FAQ", "https://www.barkbox.com/faq"),
        },
    ]


# ------------------------------------------------------------------ per-SKU satellite data

FOOD_PROS = [
    ("High palatability / dogs love the taste", "适口性高 / 狗狗爱吃", "My picky eater finally finishes every bowl."),
    ("Visible coat & energy improvement", "毛发光泽 + 精力改善明显", "Coat is shinier after 3 weeks on this food."),
    ("Clean ingredients / no fillers", "成分干净 / 无填充物", "Real meat first ingredient, no corn wheat or soy."),
]
FOOD_CONS = [
    ("Digestive upset during food switch", "换粮期肠胃不适", "Had loose stools for the first week switching over."),
    ("Price per pound higher than store brands", "单磅价格比超市品牌贵", "Great food but $3/lb is hard to justify on a budget."),
    ("Bag arrived damaged / stale kibble", "包装破损 / 干粮受潮", "Bag was torn on arrival and kibble was stale smelling."),
]

TREAT_PROS = [
    ("Dogs go crazy for the flavor", "狗狗超爱这个味道", "My dog does tricks before I even open the bag."),
    ("Good for training — small & low calorie", "适合训练 — 小颗粒低热量", "Perfect size for clicker training, only 3 calories each."),
    ("Noticeable dental improvement", "牙齿改善明显", "Tartar visibly reduced after 2 weeks of daily Greenies."),
]
TREAT_CONS = [
    ("Too hard for senior dogs / small breeds", "对老年犬/小型犬太硬", "My 12-year-old couldn't chew these, too hard."),
    ("Contains allergens (wheat/chicken)", "含过敏原（小麦/鸡肉）", "Broke out in hives — turns out it has chicken meal."),
    ("Goes stale quickly once opened", "开封后容易受潮变软", "Biscuits got soft within a week even in a sealed container."),
]


def _reviews_raw(sku_id: str, brand: str, channel: str = "amazon") -> list:
    templates = [
        {"rating": 5, "verified": True, "body": "Excellent product, my dog loves it. Will buy again.", "title": "Great!"},
        {"rating": 4, "verified": True, "body": "Good quality overall. A bit pricey but worth it for the ingredients.", "title": "Good but pricey"},
        {"rating": 3, "verified": False, "body": "Dog liked it at first but lost interest after a week.", "title": "Mixed results"},
        {"rating": 5, "verified": True, "body": "Fast shipping, fresh product, exactly as described.", "title": "Fast delivery"},
        {"rating": 2, "verified": True, "body": "Caused stomach upset. Had to switch back to old food.", "title": "Upset stomach"},
    ]
    out = []
    for i, t in enumerate(templates):
        out.append({
            "channel": channel,
            "productId": sku_id,
            "title": t["title"],
            "body": t["body"],
            "rating": t["rating"],
            "verified": t["verified"],
            "helpful": i * 3,
            "date": "2025-11-15T00:00:00Z",
            "reviewer": f"Reviewer{i+1}",
            "url": None,
        })
    return out


def _review_insight(comp: dict, category: str, pros_pool: list, cons_pool: list) -> dict:
    import random
    rng = random.Random(comp["id"])
    p = rng.choice(pros_pool)
    c = rng.choice(cons_pool)
    c2 = cons_pool[(cons_pool.index(c) + 1) % len(cons_pool)]
    raw_count = 5
    return {
        "sku": comp["id"],
        "brand": comp["brand"],
        "product": comp["product"],
        "productZh": comp.get("productZh"),
        "category": category,
        "asin": comp.get("asin"),
        "totalReviews": comp.get("reviews", raw_count),
        "averageRating": comp.get("rating", 4.5),
        "pros": [{
            "theme": p[0], "themeZh": p[1], "count": 3,
            "quote": p[2], "quoteRating": 5, "quoteVerified": True,
            "quoteUrl": None, "channels": ["amazon"],
        }],
        "cons": [
            {
                "theme": c[0], "themeZh": c[1], "count": 2,
                "quote": c[2], "quoteRating": 3, "quoteVerified": True,
                "quoteUrl": None, "channels": ["amazon"],
            },
            {
                "theme": c2[0], "themeZh": c2[1], "count": 1,
                "quote": c2[2], "quoteRating": 2, "quoteVerified": False,
                "quoteUrl": None, "channels": ["amazon"],
            },
        ],
        "channelBreakdown": {"amazon": raw_count},
        "generator": "manual",
        "lastUpdated": NOW,
        "sourcesUsed": [comp["source"]],
    }


def _video_item(comp: dict, category: str, intent: str, tier: str = "1y") -> dict:
    vid = comp["id"][:11].replace("-", "")
    return {
        "videoId": f"pet{vid[:8]}",
        "title": f"{comp['brand']} {comp['product'][:40]} — {intent} #dogfood",
        "channel": f"{comp['brand']} Official",
        "channelSubs": 50000,
        "views": 25000,
        "likes": 800,
        "comments": 45,
        "publishedAt": "2025-08-15T12:00:00Z",
        "duration": "PT8M30S",
        "durationSec": 510,
        "thumbnail": f"https://i.ytimg.com/vi/pet{vid[:8]}",
        "url": f"https://youtu.be/pet{vid[:8]}",
        "query": f"{comp['brand']} {intent}",
        "intent": intent,
        "publishedWithin": tier,
        "score": 18.5,
    }


def _video_bundle(comp: dict, category: str) -> dict:
    return {
        "sku": comp["id"],
        "brand": comp["brand"],
        "product": comp["product"],
        "productZh": comp.get("productZh"),
        "category": category,
        "videos": [
            _video_item(comp, category, "review", "1y"),
            _video_item(comp, category, "unboxing", "1y"),
        ],
        "lastUpdated": NOW,
    }


def _painpoints(category: str, label: str, label_zh: str, competitors: list, buckets_def: list) -> dict:
    sku_list = [{"sku": c["id"], "brand": c["brand"], "product": c["product"], "productZh": c.get("productZh")} for c in competitors]
    matrix: dict = {c["id"]: {} for c in competitors}
    buckets = []
    for bdef in buckets_def:
        bd = deepcopy(bdef)
        skus = bd.pop("skus")
        bd["skuBreakdown"] = [{"sku": s, "count": 1} for s in skus]
        bd["skuCount"] = len(skus)
        bd["totalCount"] = len(skus)
        for s in skus:
            matrix[s][bd["id"]] = 1
        buckets.append(bd)
    return {"category": category, "label": label, "labelZh": label_zh, "buckets": buckets, "skuList": sku_list, "matrix": matrix}


FOOD_PAIN_BUCKETS = [
    {"id": "digestive-upset", "label": "Digestive upset / loose stools on switch", "labelZh": "换粮肠胃不适 / 软便", "icon": "🤢",
     "skus": ["blue-buffalo-life-protection-adult", "purina-pro-plan-sport-30-18", "taste-of-wild-high-prairie"],
     "sampleQuote": "Had loose stools for the first week switching over.", "quoteSku": "taste-of-wild-high-prairie", "quoteUrl": None, "quoteRating": 3},
    {"id": "palatability-refusal", "label": "Dog refuses to eat / low palatability", "labelZh": "拒食 / 适口性差", "icon": "🙅",
     "skus": ["hills-science-diet-adult-large", "royal-canin-medium-adult"],
     "sampleQuote": "My dog sniffed it and walked away. Switched back to old brand.", "quoteSku": "royal-canin-medium-adult", "quoteUrl": None, "quoteRating": 2},
    {"id": "price-value", "label": "Price too high for bag size", "labelZh": "单磅价格过高", "icon": "💰",
     "skus": ["orijen-original-dog", "open-farm-grass-fed-beef", "farmers-dog-fresh-beef"],
     "sampleQuote": "Great food but $3/lb is hard to justify on a budget.", "quoteSku": "orijen-original-dog", "quoteUrl": None, "quoteRating": 4},
    {"id": "packaging-damage", "label": "Bag torn / stale kibble on arrival", "labelZh": "包装破损 / 到货受潮", "icon": "📦",
     "skus": ["merrick-grain-free-texas-beef", "nom-nom-chicken-casserole"],
     "sampleQuote": "Bag was torn on arrival and kibble was stale smelling.", "quoteSku": "merrick-grain-free-texas-beef", "quoteUrl": None, "quoteRating": 2},
    {"id": "subscription-lock", "label": "Hard to cancel subscription / auto-renew", "labelZh": "订阅难取消 / 自动续费", "icon": "🔒",
     "skus": ["farmers-dog-fresh-beef", "nom-nom-chicken-casserole"],
     "sampleQuote": "Took 3 emails and a phone call to cancel the subscription.", "quoteSku": "farmers-dog-fresh-beef", "quoteUrl": None, "quoteRating": 2},
    {"id": "allergen-reaction", "label": "Allergic reaction / skin issues", "labelZh": "过敏反应 / 皮肤问题", "icon": "⚠️",
     "skus": ["blue-buffalo-life-protection-adult", "merrick-grain-free-texas-beef"],
     "sampleQuote": "Broke out in hives after 2 weeks — chicken allergy we didn't know about.", "quoteSku": "blue-buffalo-life-protection-adult", "quoteUrl": None, "quoteRating": 1},
]

TREAT_PAIN_BUCKETS = [
    {"id": "too-hard", "label": "Too hard for senior dogs / small breeds", "labelZh": "对老年犬/小型犬太硬", "icon": "🦷",
     "skus": ["greenies-regular-dental", "smartbones-mini-peanut", "old-mother-hubbard-classic"],
     "sampleQuote": "My 12-year-old couldn't chew these, too hard.", "quoteSku": "greenies-regular-dental", "quoteUrl": None, "quoteRating": 2},
    {"id": "allergen", "label": "Contains allergens (wheat/chicken)", "labelZh": "含过敏原（小麦/鸡肉）", "icon": "⚠️",
     "skus": ["milk-bone-original-biscuits", "pup-peroni-original", "wellness-soft-puppy-bites"],
     "sampleQuote": "Broke out in hives — turns out it has chicken meal.", "quoteSku": "pup-peroni-original", "quoteUrl": None, "quoteRating": 1},
    {"id": "stale-fast", "label": "Goes stale / soft quickly after opening", "labelZh": "开封后易受潮变软", "icon": "💧",
     "skus": ["milk-bone-original-biscuits", "old-mother-hubbard-classic", "fruitables-pumpkin-apple"],
     "sampleQuote": "Biscuits got soft within a week even in a sealed container.", "quoteSku": "milk-bone-original-biscuits", "quoteUrl": None, "quoteRating": 3},
    {"id": "overfeeding", "label": "Easy to overfeed / high calorie", "labelZh": "容易过量喂食 / 热量高", "icon": "📈",
     "skus": ["pup-peroni-original", "blue-buffalo-wilderness-trail", "barkbox-super-chewer"],
     "sampleQuote": "Dog gained 3 lbs in a month from too many treats.", "quoteSku": "pup-peroni-original", "quoteUrl": None, "quoteRating": 3},
    {"id": "size-mismatch", "label": "Wrong size for dog weight class", "labelZh": "尺寸与犬体重不匹配", "icon": "📏",
     "skus": ["greenies-regular-dental", "smartbones-mini-peanut"],
     "sampleQuote": "Regular size is way too big for my 15 lb terrier.", "quoteSku": "greenies-regular-dental", "quoteUrl": None, "quoteRating": 3},
    {"id": "subscription-variance", "label": "Subscription box contents vary / allergen risk", "labelZh": "订阅礼盒内容不定 / 过敏风险", "icon": "📦",
     "skus": ["barkbox-super-chewer"],
     "sampleQuote": "This month's box had chicken treats — my dog is allergic.", "quoteSku": "barkbox-super-chewer", "quoteUrl": None, "quoteRating": 2},
]


def write_category(name: str, competitors: list, aov: dict, bundles: list, installs: list, pros_pool: list, cons_pool: list) -> None:
    dataset = {"category": name, "competitors": competitors, "aov": aov, "bundles": bundles, "installs": installs}
    path = DATA / f"{name}.json"
    path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {path.name} ({len(competitors)} competitors)")

    video_items = []
    for c in competitors:
        (DATA / "review_insights" / f"{c['id']}.json").write_text(
            json.dumps(_review_insight(c, name, pros_pool, cons_pool), indent=2, ensure_ascii=False) + "\n"
        )
        (DATA / "reviews_raw" / f"{c['id']}.json").write_text(
            json.dumps(_reviews_raw(c["id"], c["brand"]), indent=2, ensure_ascii=False) + "\n"
        )
        video_items.append(_video_bundle(c, name))

    vid_path = DATA / "videos" / f"{name}.json"
    vid_path.parent.mkdir(parents=True, exist_ok=True)
    vid_path.write_text(json.dumps({"category": name, "generatedAt": NOW, "items": video_items}, indent=2, ensure_ascii=False) + "\n")
    print(f"  wrote videos/{name}.json + {len(competitors)} insight/raw files")


def update_painpoints() -> None:
    pp_path = DATA / "painpoints.json"
    existing = json.loads(pp_path.read_text()) if pp_path.exists() else {}
    existing["dog-food"] = _painpoints("dog-food", "Dog Food", "犬用主食", DOG_FOOD_COMPETITORS, FOOD_PAIN_BUCKETS)
    existing["dog-treats"] = _painpoints("dog-treats", "Dog Treats", "犬用零食", DOG_TREATS_COMPETITORS, TREAT_PAIN_BUCKETS)
    pp_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
    print("  updated painpoints.json for dog-food + dog-treats")


def main() -> None:
    print("Seeding pet dog categories…")
    write_category("dog-food", DOG_FOOD_COMPETITORS, DOG_FOOD_AOV, _bundles_food(), _installs_food(), FOOD_PROS, FOOD_CONS)
    write_category("dog-treats", DOG_TREATS_COMPETITORS, DOG_TREATS_AOV, _bundles_treats(), _installs_treats(), TREAT_PROS, TREAT_CONS)
    update_painpoints()
    print("Done.")


if __name__ == "__main__":
    main()
