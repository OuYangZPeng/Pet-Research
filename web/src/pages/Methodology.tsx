import { useTranslation } from 'react-i18next';
import CategoryHero from '../components/CategoryHero';
import SectionHeading from '../components/SectionHeading';
import SourceBadge from '../components/SourceBadge';
import { useMeta } from '../lib/loadData';

export default function Methodology() {
  const { t, i18n } = useTranslation();
  const { data: meta } = useMeta();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const stackItems = t('methodology.stackItems', { returnObjects: true }) as string[];
  const limitItems = t('methodology.limitItems', { returnObjects: true }) as string[];

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('methodology.title')}
        desc={t('methodology.desc')}
      />

      <section className="mb-10">
        <SectionHeading
          title={lang === 'zh' ? '调研口径与过滤规则' : 'Scope & filter rules'}
          subtitle={
            lang === 'zh'
              ? '为保证可对标性，全部数据围绕「美国市场 + 新鲜信号 + 显性价格」三个轴线收口'
              : 'Three axes lock the dataset: US marketplace, recency-first signals, transparent pricing'
          }
        />
        <div className="grid gap-3 lg:grid-cols-3">
          <div className="card border-l-4 border-ok p-4">
            <div className="text-xs font-semibold uppercase tracking-wider text-ok">
              🇺🇸 {lang === 'zh' ? '亚马逊美国市场' : 'Amazon US marketplace'}
            </div>
            <p className="mt-2 text-sm text-ink-700">
              {lang === 'zh' ? (
                <>
                  所有 Rainforest API 调用硬编码 <code className="rounded bg-ink-100 px-1">amazon_domain=amazon.com</code>；
                  ASIN、价格、评分、BSR 全部来自 amazon.com（不混入 .ca / .co.uk / .de）。
                  竞品表中带 <span className="rounded bg-ink-900 px-1 text-white">🇺🇸 US</span> 徽章的行均为已锁定的美国 listing。
                </>
              ) : (
                <>
                  All Rainforest calls hard-code <code className="rounded bg-ink-100 px-1">amazon_domain=amazon.com</code>;
                  every ASIN, price, rating, BSR comes from amazon.com (never mixed with .ca / .co.uk / .de).
                  Rows tagged <span className="rounded bg-ink-900 px-1 text-white">🇺🇸 US</span> in the competitor table are US-locked listings.
                </>
              )}
            </p>
          </div>
          <div className="card border-l-4 border-accent p-4">
            <div className="text-xs font-semibold uppercase tracking-wider text-accent">
              🎬 {lang === 'zh' ? 'YouTube 新鲜度级联' : 'YouTube freshness cascade'}
            </div>
            <p className="mt-2 text-sm text-ink-700">
              {lang === 'zh'
                ? '每个 SKU 的 review/setup/unboxing 三类视频按「近 12 个月 → 24 个月 → 36 个月 → 全部」级联抓取——上一档命中即停止，保证返回的视频是该 SKU 现存最新的内容。每条视频带「近 1/2/3 年」徽章可一眼识别。'
                : 'For each SKU we cascade 12 → 24 → 36 → any-age windows across review/setup/unboxing queries — first hit wins, so results are the freshest content that actually exists for the SKU. Every card carries an explicit <1y / <2y / <3y / >3y badge.'}
            </p>
            <pre className="mt-2 rounded bg-ink-900 p-2 font-mono text-[11px] text-ink-100">
              python refresh_videos.py --lookback 1,2,3,all
            </pre>
          </div>
          <div className="card border-l-4 border-warn p-4">
            <div className="text-xs font-semibold uppercase tracking-wider text-warn">
              💰 {lang === 'zh' ? '售价 + 折扣 + 包邮 + 送达' : 'Price + Discount + Shipping + Lead time'}
            </div>
            <p className="mt-2 text-sm text-ink-700">
              {lang === 'zh' ? (
                <>
                  每行强制展示「售价 / 划线原价 / 折扣 % / 省金额」；
                  运费基于 <code className="rounded bg-ink-100 px-1">shippingNote</code> 自动归类为
                  <span className="mx-1 rounded bg-ok/10 px-1 text-ok">✅ 包邮</span>
                  <span className="mx-1 rounded bg-accent/10 px-1 text-accent">📦 满 $X 包邮</span>
                  <span className="mx-1 rounded bg-warn/10 px-1 text-warn">💰 付费</span>
                  <span className="mx-1 rounded bg-ink-100 px-1">❓ 未确认</span>
                  ；不允许「-」式空值蒙混过关。
                </>
              ) : (
                <>
                  Every row exposes current price / strike-through MSRP / discount % / savings amount;
                  shipping is auto-classified from <code className="rounded bg-ink-100 px-1">shippingNote</code> into
                  <span className="mx-1 rounded bg-ok/10 px-1 text-ok">✅ Free</span>
                  <span className="mx-1 rounded bg-accent/10 px-1 text-accent">📦 Free over $X</span>
                  <span className="mx-1 rounded bg-warn/10 px-1 text-warn">💰 Paid</span>
                  <span className="mx-1 rounded bg-ink-100 px-1">❓ Unverified</span>
                  ; no silent "—" placeholders.
                </>
              )}
            </p>
            <p className="mt-2 text-sm text-ink-700">
              {lang === 'zh' ? (
                <>
                  <b>送达时效</b>分四档（
                  <span className="mx-1 rounded bg-ok/10 px-1 text-ok">⚡ 极速 ≤2 天</span>
                  <span className="mx-1 rounded bg-accent/10 px-1 text-accent">🚀 快 ≤5 天</span>
                  <span className="mx-1 rounded bg-warn/10 px-1 text-warn">📦 标准 ≤10 天</span>
                  <span className="mx-1 rounded bg-ink-200 px-1 text-ink-700">🚛 货运 &gt;10 天</span>
                  ），数据来自各品牌官方运输政策（Chewy、Amazon Prime、Farmer's Dog、BarkBox）+ 冷链/FBA 文档，
                  每行 chip 可点击直达数据源。表头也新增「送达 (最快优先)」排序键。
                </>
              ) : (
                <>
                  <b>Lead times</b> are bucketed into four tiers (
                  <span className="mx-1 rounded bg-ok/10 px-1 text-ok">⚡ Express ≤2d</span>
                  <span className="mx-1 rounded bg-accent/10 px-1 text-accent">🚀 Fast ≤5d</span>
                  <span className="mx-1 rounded bg-warn/10 px-1 text-warn">📦 Standard ≤10d</span>
                  <span className="mx-1 rounded bg-ink-200 px-1 text-ink-700">🚛 Freight &gt;10d</span>
                  ) sourced from each brand's published shipping policy (Chewy, Amazon Prime, Farmer's Dog, BarkBox)
                  plus cold-chain and FBA documentation. Every chip links back to the source,
                  and a new "Delivery (fastest)" sort key is available in the table header.
                </>
              )}
            </p>
          </div>
        </div>
      </section>

      <section className="mb-10">
        <SectionHeading title={t('methodology.loopTitle')} />
        <div className="card border-l-4 border-accent p-5">
          <p className="text-sm text-ink-700">{t('methodology.loopBody')}</p>
          <pre className="mt-3 overflow-x-auto rounded-lg bg-ink-900 p-3 font-mono text-xs text-ink-100">
{`# 1. Collect raw reviews (Amazon + DTC + Reddit)
python refresh_reviews.py --skus blue-buffalo-life-protection-adult greenies-regular-dental barkbox-super-chewer

# 2a. Cursor SDK auto (cron-friendly; uses your Cursor subscription)
#     Get key at https://cursor.com/dashboard/integrations
echo "CURSOR_API_KEY=cursor_…" >> scraper/.env
python refresh_reviews.py

# 2b. Or no key — manifest mode
#     Skip step 2a; open this repo in Cursor IDE and ask:
#     "处理 scraper/_insights_pending.md"`}
          </pre>
        </div>
      </section>

      <section className="mb-10">
        <SectionHeading
          title={t('methodology.dataQualityTitle')}
          subtitle={t('methodology.dataQualityNote')}
        />
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="card border-l-4 border-ok p-5">
            <div className="flex items-center gap-2">
              <span className="inline-flex rounded-full bg-ok/10 px-2 py-0.5 text-xs font-semibold text-ok">
                ✓ {t('methodology.dataQualityVerified')}
              </span>
            </div>
            <p className="mt-3 text-sm text-ink-700">
              {t('methodology.dataQualityVerifiedDesc')}
            </p>
          </div>
          <div className="card border-l-4 border-warn p-5">
            <div className="flex items-center gap-2">
              <span className="inline-flex rounded-full bg-warn/10 px-2 py-0.5 text-xs font-semibold text-warn">
                ⌛ {t('methodology.dataQualityPending')}
              </span>
            </div>
            <p className="mt-3 text-sm text-ink-700">
              {t('methodology.dataQualityPendingDesc')}
            </p>
          </div>
        </div>
      </section>

      <section className="mb-10 grid gap-4 lg:grid-cols-3">
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {t('methodology.stack')}
          </div>
          <ul className="mt-3 space-y-2 text-sm text-ink-700">
            {stackItems.map((s, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-accent">•</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {t('methodology.freq')}
          </div>
          <p className="mt-3 text-sm text-ink-700">{t('methodology.freqDesc')}</p>
          <pre className="mt-3 rounded-lg bg-ink-900 p-3 font-mono text-xs text-ink-100">
{`# crontab -e
0 6 * * 1  cd ~/research-site/scraper && python run_all.py >> run.log 2>&1`}
          </pre>
        </div>
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {t('methodology.limits')}
          </div>
          <ul className="mt-3 space-y-2 text-sm text-ink-700">
            {limitItems.map((s, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-warn">!</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <SectionHeading
          title={lang === 'zh' ? '已使用的权威数据源（全量）' : 'All authoritative sources used'}
        />
        <div className="card p-5">
          <ul className="grid gap-2 md:grid-cols-2">
            {(meta?.sources || []).map((s, i) => (
              <li key={i} className="text-sm">
                <SourceBadge source={s} />
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
