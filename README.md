# Shadowmeta Pet Research — 美国犬粮与犬零食市场调研

A bilingual (中文 / English) static research site backed by Python scrapers
that refresh the underlying JSON data on a schedule.

For Ubuntu deployment and cron automation, see `ops/ubuntu/README.md`.

## 1. What's inside

```
Pet-Research/                     # git root (flat)
├── web/                          Static front-end (Vite + React + TS + Tailwind + Recharts + i18next)
│   ├── src/                      Pages + components + i18n
│   └── public/data/              ← JSON consumed by the front-end
│       ├── dog-food.json
│       ├── dog-treats.json
│       ├── influencers.json
│       ├── seasonality.json
│       ├── shipping.json
│       └── meta.json             generatedAt + scriptVersion + flat source list
├── ops/ubuntu/                   Ubuntu deploy + cron scripts
└── scraper/                      Python pipeline
    ├── sources/                  Per-channel scrapers (one file per source)
    │   ├── _schema.py            Pydantic models — keep in sync with web/src/lib/types.ts
    │   ├── amazon_rainforest.py  Verified Amazon product/review enrichment
    │   ├── youtube_api.py        Curated pet creator stats
    │   ├── reddit_api.py         Pet subreddit audience stats
    │   ├── dtc_reviews.py        Trustpilot-backed DTC review fetcher
    │   └── trustpilot.py         Playwright Trustpilot scraper
    ├── analyze/
    │   ├── aov.py                Per-platform median / P25 / P75
    │   ├── seasonality.py        Pet-food Google Trends + static retail prior
    │   ├── review_insights.py    Cursor-powered pros/cons synthesis
    │   └── painpoints.py         Category pain-point aggregation
    ├── seed_pet_categories.py    Pet baseline seed data generator
    └── run_all.py                One-shot pet-only pipeline → writes web/public/data/*.json
```

The 8 site pages are:

| Path | Purpose |
| --- | --- |
| `/` | Dashboard — KPI strip, category AOV bars, seasonality snippet, market size |
| `/dog-food` `/dog-treats` | Per-category deep dive |
| `/insights/seasonality` | Annual demand + discount curve |
| `/insights/influencers` | YouTube / IG / Reddit / TikTok creators with category fit |
| `/insights/logistics` | Shipping modes, free-shipping thresholds |
| `/methodology` | Stack, refresh cadence, known limitations, full source list |

Every figure on the site carries a clickable source link + a fetched-at
timestamp. The footer also shows the last-refresh date pulled from `meta.json`.

## 2. Local preview

```bash
cd web
npm install
npm run dev          # http://localhost:5190 with HMR
# or
npm run build && npm run preview   # production-style preview at http://localhost:4190
```

The default `vite.config.ts` uses `base: './'` so the production build can be
opened directly by double-clicking `dist/index.html` (no server needed).

## 3. Running the scraper

### 3.1 Install

```bash
cd scraper
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium     # needed for Trustpilot scraping
```

### 3.2 Configure API keys

```bash
cp .env.example .env
$EDITOR .env                    # fill in YOUTUBE_API_KEY at minimum
```

| Variable | Required? | What to do without it |
| --- | --- | --- |
| `RAINFOREST_API_KEY` | Recommended | Amazon rating/reviews stay marked "pending scrape" in the UI |
| `YOUTUBE_API_KEY` | Recommended | Influencer data falls back to the curated seed file |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Optional | Reddit subscriber counts won't refresh |
| `AMAZON_PROXY_URL` | Optional | Amazon BSR will likely get CAPTCHA-walled; the previous JSON is kept |
| `AMAZON_PAAPI_*` | Future | Slot ready for swapping to PA-API later |

#### 3.2.1 Verifying Amazon data with the Rainforest free tier

If you don't want to commit to a paid Amazon API yet, the cheapest verified path
is **Rainforest API** (https://rainforestapi.com — 100 requests/month free, no
card required). It returns the same `rating`, `ratings_total` (review count),
`buybox_winner.price` and `bestsellers_rank` you would have gotten from PA-API.

1. Sign up at https://rainforestapi.com → copy your API key.
2. `echo "RAINFOREST_API_KEY=…" >> scraper/.env`
3. Spot-check 3 SKUs first (uses 6 credits) before committing:

```bash
cd scraper && source .venv/bin/activate
python verify_asins.py --category dog-food --limit 3      # read-only preview
```

You'll see a `seed vs Rainforest` table with `Δ price`, `rating live`,
`reviews live` columns. Anything >15% off the seed value will be coloured red.

4. Apply the full refresh and write changes back into `web/public/data/*.json`:

```bash
python verify_asins.py --apply
```

5. After the apply, the UI's "⌛ pending scrape" chips will disappear for the
   rows that were filled in.

Credit budget for the current seed:
- dog-food Amazon rows: ~5 × 2 credits on first verification
- dog-treats Amazon rows: ~7 × 2 credits on first verification
- **Total first run ≈ 24 credits.** After ASINs are confirmed, weekly verification
  usually drops to 1 credit per Amazon row.

Single-shot lookup helper (for ad-hoc spot checks):

```bash
python -m sources.amazon_rainforest product B0009X29WK
python -m sources.amazon_rainforest search "Blue Buffalo Life Protection Adult"
python -m sources.amazon_rainforest reviews B0009X29WK 3      # 3 pages of reviews
```

#### 3.2.2 Review insights (pros / cons cards per SKU)

This is the *most commercially actionable* layer — what real users praise and
complain about, clustered into structured themes with verbatim quotes.

Pipeline:

1. **Collect raw reviews** from Amazon (Rainforest, 3 pages × 1 credit per SKU),
   DTC stores (Yotpo / Shopify-native / Trustpilot — all free), and Reddit
   (PRAW or public JSON — free):

   ```bash
   cd scraper && source .venv/bin/activate
   python refresh_reviews.py --skus blue-buffalo-life-protection-adult greenies-regular-dental barkbox-super-chewer
   # or
   python refresh_reviews.py --category dog-food --limit 3
   ```

   Raw data lands in `web/public/data/reviews_raw/<sku>.json` and a manifest is
   queued at `scraper/_insights_pending.md`.

2. **Generate insights — pick one of two modes**:

   **Mode A: Cursor SDK auto (cron-friendly, uses your Cursor subscription)**

   Get a key at https://cursor.com/dashboard/integrations, then:

   ```bash
   echo "CURSOR_API_KEY=cursor_…" >> scraper/.env
   python refresh_reviews.py   # Agent.prompt() writes insight JSON directly
   ```

   No third-party LLM key required; uses your existing Cursor seat.

   **Mode B: Cursor IDE manual (no key, fully free)**

   Skip the env var. Then open this repo in Cursor IDE and say:

   > 处理 scraper/_insights_pending.md

   The Cursor agent will read each SKU's raw reviews and write a structured
   `web/public/data/review_insights/<sku>.json` file. Cost: zero, uses your
   Cursor subscription's normal chat quota.

3. **View in the UI**: every row in the competitor table is now clickable.
   Click → an expandable card slides open with pros / cons / quotes / star
   ratings / verified-purchase badges, plus a channel breakdown chip strip.

Cost for a full refresh across all 21 Amazon SKUs:
- Reviews: 21 × 3 = **63 Rainforest credits**
- DTC: free
- Reddit: free
- LLM: free (Cursor — either mode)

#### 3.2.3 YouTube creator videos (per-SKU, freshness-cascaded)

For every seed SKU we surface the top reviewer / comparison / unboxing videos
on YouTube via the official Data API v3. The discovery uses a **freshness
cascade**: each intent query first runs `publishedAfter = -12 months`; only if
that window returns zero hits do we widen to 24 months, then 36 months, then
"any age". The narrowest tier each video actually matched is stamped onto the
row as `publishedWithin`, which the UI renders as a `<1y / <2y / <3y / >3y`
badge. Sort order is fresher tier first, then channel-subs × view-count score.

```bash
cd scraper && source .venv/bin/activate
echo "YOUTUBE_API_KEY=AIza…" >> .env

# Default cascade (recommended):
python refresh_videos.py --lookback 1,2,3,all

# Strict last-12-months mode:
python refresh_videos.py --lookback 1

# Force a single SKU only (existing data for other SKUs is preserved):
python refresh_videos.py --skus blue-buffalo-life-protection-adult
```

**Quota math**: YouTube Free Tier = 10 000 units/day, each `search.list` = 100
units. Best case (tier-1 hits on all intents) ≈ 300 u/SKU. Worst case
(cascade to all 4 tiers per intent) ≈ 1 200 u/SKU. A full 32-SKU refresh
typically lands around 6 000–15 000 u, so very deep cascades can occasionally
bleed into the next day. The script detects quota exhaustion (`429` / `403
quotaExceeded`) and stops early, preserving existing JSON.

### 3.3 Run

```bash
# inside scraper/ with .venv active
python run_all.py                # writes to ../web/public/data/*.json
python run_all.py --dry-run      # writes to ./scraper/_out/ for inspection

# After a refresh, rebuild the site:
cd ../web && npm run build
```

If a single source fails (e.g. Amazon CAPTCHA), `run_all.py` keeps the existing
JSON for that category instead of overwriting with empty data.

### 3.4 Schedule (cron)

```cron
# Recommended: use ops/ubuntu/shadowmeta.cron.example
10 6 * * 1  /srv/shadowmeta/research-site/ops/ubuntu/refresh_shadowmeta.sh >> /var/log/shadowmeta-refresh.log 2>&1
```

## 4. Data schema (selected)

`web/src/lib/types.ts` and `scraper/sources/_schema.py` are the source of truth
and intentionally mirror each other. The main shapes:

```ts
Competitor {
  id, brand, product, productZh?, platform, storeUrl,
  bsrRank?, asin?, sku?, price{current, original?, currency, discountPct?},
  rating?, reviews?, variant?, shippingNote?, shipFrom?, bundle?,
  source{label, url, fetchedAt}
}

CategoryDataset { category, competitors[], aov{buckets[], insight, insightZh}, bundles[], installs[] }

InfluencerEntry { id, platform, handle, displayName, url, audience, audienceUnit,
                  totalViews?, categoryFit (0–10), notes, notesZh?, source }

SeasonalityPoint { month, monthZh, demandIndex (0–100), discountPctTypical (%), band }

ShippingMode    { id, method, methodZh, transit, cost, useCase, useCaseZh, shipFrom, source }

FreeShippingBenchmark { brand, threshold (USD), note, noteZh?, source }
```

## 5. Authoritative sources currently wired in

- Amazon Best Sellers — [Toilets](https://www.amazon.com/Best-Sellers-Toilets/zgbs/hi/680355011) · [Two-Piece Toilets](https://www.amazon.com/Best-Sellers-Two-Piece-Toilets/zgbs/hi/542639011) · [Bidet Seats](https://www.amazon.com/Best-Sellers-Bidet-Seats/zgbs/hi/6810566011)
- DTC: [HOROW](https://horow.com/) · [TUSHY](https://hellotushy.com/) · [Woodbridge Bath](https://woodbridgebath.com/) · [KZG](https://thekzg.com/) · [Elemento Bath](https://elementobath.com/) · [Soaque](https://kbbfocus.com/news/6077-soaques-sam-brindle-building-a-luxury-bathroom-retailer-without-a-showroom)
- Industry: [NKBA 2026 Outlook](https://nkba.org/research/2026-kitchen-bath-industry-outlook/) · [Contractor Magazine 2026](https://www.contractormag.com/bath-kitchen/article/55366341/bath-and-kitchen-remodeling-trends-2026)
- Evaluations: [The Spruce 2026](https://www.thespruce.com/best-toilets-4176673) · [BHG 2026](https://www.bhg.com/best-toilets-6824634)
- Logistics: [ExFreight](https://www.exfreight.com/how-long-does-it-take-to-ship-from-china-to-the-us/) · [DFH Logistics 2026](https://dfhlogistics.com/how-to-ship-bathroom-products-and-fittings-from-china-to-usa/) · [King-Hor 2026](https://king-hor.com/ddp-shipping-from-china-to-usa-complete-guide-2026/)
- Install: [Plumbing Sniper 2026](https://plumbingsniper.com/toilet-installation-cost-2026/) · [Builds and Buys 2026](https://buildsandbuys.com/toilet-installation-cost-guide/)
- Creators: [Roger Wakefield](https://www.youtube.com/c/RogerWakefield) · [Matt Risinger](https://www.youtube.com/c/MattRisinger) · [Perkins Builder Brothers](https://www.youtube.com/@PerkinsBuilderBrothers) · [This Old House](https://www.youtube.com/@thisoldhouse) · `r/Plumbing` · `r/bidets` · `r/HomeImprovement`

## 6. Adding a new source

1. Drop a new file in `scraper/sources/your_source.py` exposing
   `async def fetch(category: str) -> list[dict]`. Use `_shopify.py` as a
   template if the target site is on Shopify.
2. Validate each row with `Competitor.model_validate(...)` before returning.
3. Wire it into `fetch_category_competitors()` in `run_all.py`.
4. Add the brand's free-shipping policy into `CURATED_FREE_SHIPPING` if relevant.
5. `python run_all.py --dry-run` and inspect `scraper/_out/`.

## 7. Known limitations

- **Amazon anti-bot**: server-side HTML scraping is best-effort. For reliable
  production scraping use Amazon PA-API (slots already in `.env.example`) or a
  residential proxy pool.
- **TikTok**: no official API. The TikTok column on the influencer page is
  currently populated from manual research; add a third-party service (e.g.
  TikTok Creator Marketplace / RapidAPI scrapers) when needed.
- **Reddit**: PRAW returns subscriber counts + top-of-week threads only; we do
  not run sentiment analysis.
- **Wayfair / Home Depot / Lowe's**: prices on these are pulled once at curation
  time (visible in `meta.json` sources) — refreshing them programmatically
  requires extra adapters; placeholders are in `_schema.py` ready to receive them.

## 8. Disclaimer

Data on this site is for internal research use only. Prices, ratings and
subscriber counts move; always check the source link before quoting figures in
commercial pitches.
