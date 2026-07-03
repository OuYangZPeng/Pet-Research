import { Fragment, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { CategorySlug, Competitor } from '../lib/types';
import PriceCard from './PriceCard';
import SourceBadge from './SourceBadge';
import PendingChip from './PendingChip';
import ReviewInsightsCard from './ReviewInsightsCard';
import VideoGrid from './VideoGrid';
import { parseShipping, shippingChipLabel, leadTimeChipLabel } from '../lib/shipping';

type SortKey =
  | 'bsr'
  | 'price-asc'
  | 'price-desc'
  | 'discount'
  | 'rating'
  | 'reviews'
  | 'lead-time';

const sortKeys: { value: SortKey; labelEn: string; labelZh: string }[] = [
  { value: 'bsr', labelEn: 'BSR rank', labelZh: '榜单排名' },
  { value: 'price-asc', labelEn: 'Price ↑', labelZh: '价格 ↑' },
  { value: 'price-desc', labelEn: 'Price ↓', labelZh: '价格 ↓' },
  { value: 'discount', labelEn: 'Discount %', labelZh: '折扣 %' },
  { value: 'rating', labelEn: 'Rating', labelZh: '评分' },
  { value: 'reviews', labelEn: 'Reviews', labelZh: '评论数' },
  { value: 'lead-time', labelEn: 'Delivery (fastest)', labelZh: '送达 (最快优先)' },
];

function discountPct(c: Competitor): number {
  if (!c.price.original || c.price.original <= c.price.current) return 0;
  return Math.round((1 - c.price.current / c.price.original) * 100);
}

function sortRows(rows: Competitor[], key: SortKey): Competitor[] {
  const r = [...rows];
  switch (key) {
    case 'bsr':
      r.sort((a, b) => (a.bsrRank ?? 999) - (b.bsrRank ?? 999));
      break;
    case 'price-asc':
      r.sort((a, b) => a.price.current - b.price.current);
      break;
    case 'price-desc':
      r.sort((a, b) => b.price.current - a.price.current);
      break;
    case 'discount':
      r.sort((a, b) => discountPct(b) - discountPct(a));
      break;
    case 'rating':
      r.sort((a, b) => (b.rating ?? -1) - (a.rating ?? -1));
      break;
    case 'reviews':
      r.sort((a, b) => (b.reviews ?? -1) - (a.reviews ?? -1));
      break;
    case 'lead-time':
      // Sort by max-day window asc (fastest first), then min-day asc as tiebreaker.
      // Unknown lead time pushed to the bottom.
      r.sort((a, b) => {
        const am = a.leadTimeDays?.max ?? 999;
        const bm = b.leadTimeDays?.max ?? 999;
        if (am !== bm) return am - bm;
        return (a.leadTimeDays?.min ?? 999) - (b.leadTimeDays?.min ?? 999);
      });
      break;
  }
  return r;
}

export default function CompetitorTable({
  rows,
  category,
}: {
  rows: Competitor[];
  category?: CategorySlug;
}) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const [expanded, setExpanded] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState<string | 'all'>('all');
  const [sortKey, setSortKey] = useState<SortKey>('bsr');

  const platforms = useMemo(() => {
    const s = new Set<string>();
    rows.forEach((r) => s.add(r.platform));
    return Array.from(s);
  }, [rows]);

  const filteredRows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = rows.filter((r) => {
      if (platformFilter !== 'all' && r.platform !== platformFilter) return false;
      if (!q) return true;
      const hay = [
        r.brand,
        r.product,
        r.productZh,
        r.asin,
        r.sku,
        r.variant,
        r.shippingNote,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return hay.includes(q);
    });
    return sortRows(filtered, sortKey);
  }, [rows, query, platformFilter, sortKey]);

  return (
    <div className="card overflow-hidden">
      <div className="flex flex-wrap items-center gap-3 border-b border-ink-100 bg-ink-50 px-4 py-3">
        <div className="relative flex-1 min-w-[200px]">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400">
            ⌕
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              lang === 'zh'
                ? '搜索品牌 / 型号 / ASIN / SKU…'
                : 'Search brand / model / ASIN / SKU…'
            }
            className="w-full rounded-lg border border-ink-200 bg-white py-1.5 pl-8 pr-3 text-sm placeholder:text-ink-400 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
        </div>

        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setPlatformFilter('all')}
            className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
              platformFilter === 'all'
                ? 'bg-accent text-white'
                : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
            }`}
          >
            {lang === 'zh' ? '全部' : 'All'}
          </button>
          {platforms.map((p) => (
            <button
              key={p}
              onClick={() => setPlatformFilter(p)}
              className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
                platformFilter === p
                  ? 'bg-accent text-white'
                  : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-ink-400">{lang === 'zh' ? '排序' : 'Sort'}:</span>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
            className="rounded-lg border border-ink-200 bg-white px-2 py-1 font-semibold text-ink-700 focus:border-accent focus:outline-none"
          >
            {sortKeys.map((k) => (
              <option key={k.value} value={k.value}>
                {lang === 'zh' ? k.labelZh : k.labelEn}
              </option>
            ))}
          </select>
        </div>

        <div className="text-xs text-ink-400">
          {filteredRows.length} / {rows.length}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-ink-100">
          <thead className="bg-white">
            <tr>
              <th className="table-th"></th>
              <th className="table-th">#</th>
              <th className="table-th">{t('common.brand')}</th>
              <th className="table-th">{t('common.product')}</th>
              <th className="table-th">SKU</th>
              <th className="table-th">{lang === 'zh' ? '供应商' : 'Supplier'}</th>
              <th className="table-th">{lang === 'zh' ? '联系方式' : 'Contact'}</th>
              <th className="table-th">{t('common.platform')}</th>
              <th className="table-th">{t('common.price')}</th>
              <th className="table-th">{t('common.rating')}</th>
              <th className="table-th">{t('common.shipping')}</th>
              <th className="table-th">{t('common.source')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100 bg-white">
            {filteredRows.length === 0 && (
              <tr>
                <td colSpan={12} className="px-4 py-6 text-center text-sm text-ink-400">
                  {lang === 'zh' ? '没有匹配的竞品' : 'No competitors match the current filter.'}
                </td>
              </tr>
            )}
            {filteredRows.map((r, idx) => {
              const isOpen = expanded === r.id;
              return (
                <Fragment key={r.id}>
                  <tr
                    className={`cursor-pointer hover:bg-ink-50/60 ${isOpen ? 'bg-accent/5' : ''}`}
                    onClick={() => setExpanded(isOpen ? null : r.id)}
                  >
                    <td className="table-td w-6 text-center text-ink-300">
                      <span
                        className={`inline-block transition-transform ${
                          isOpen ? 'rotate-90 text-accent' : ''
                        }`}
                      >
                        ▸
                      </span>
                    </td>
                    <td className="table-td font-mono text-ink-400">
                      {r.bsrRank ? `#${r.bsrRank}` : idx + 1}
                    </td>
                    <td className="table-td font-semibold text-ink-900">{r.brand}</td>
                    <td className="table-td max-w-md">
                      <a
                        href={r.storeUrl}
                        target="_blank"
                        rel="noreferrer noopener"
                        onClick={(e) => e.stopPropagation()}
                        className="font-medium text-ink-800 hover:text-accent"
                      >
                        {lang === 'zh' && r.productZh ? r.productZh : r.product}
                      </a>
                      <div className="mt-0.5 flex flex-wrap gap-1">
                        {r.asin && <span className="chip">ASIN {r.asin}</span>}
                        {r.variant && <span className="chip">{r.variant}</span>}
                        {r.bundle && <span className="chip-accent">{t('common.bundle')}</span>}
                      </div>
                    </td>
                    <td className="table-td font-mono text-xs text-ink-700">
                      {r.sku || <span className="text-ink-300">—</span>}
                    </td>
                    <td className="table-td text-xs">
                      {r.supplier ? (
                        <div>
                          <div className="font-semibold text-ink-800">
                            {lang === 'zh' && r.supplier.companyZh
                              ? r.supplier.companyZh
                              : r.supplier.company}
                          </div>
                          {r.supplier.website && (
                            <a
                              href={r.supplier.website}
                              target="_blank"
                              rel="noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="text-accent hover:underline"
                            >
                              {lang === 'zh' ? '官网' : 'Website'}
                            </a>
                          )}
                        </div>
                      ) : (
                        <span className="text-ink-300">—</span>
                      )}
                    </td>
                    <td className="table-td text-xs">
                      {r.supplier ? (
                        <div className="space-y-0.5 text-ink-600">
                          {r.supplier.phone && (
                            <div>
                              <span className="text-ink-400">{lang === 'zh' ? '电话' : 'Tel'}:</span>{' '}
                              <a
                                href={`tel:${r.supplier.phone.replace(/[^\d+]/g, '')}`}
                                onClick={(e) => e.stopPropagation()}
                                className="hover:text-accent"
                              >
                                {r.supplier.phone}
                              </a>
                            </div>
                          )}
                          {r.supplier.email && (
                            <div>
                              <span className="text-ink-400">{lang === 'zh' ? '邮箱' : 'Email'}:</span>{' '}
                              <a
                                href={`mailto:${r.supplier.email}`}
                                onClick={(e) => e.stopPropagation()}
                                className="hover:text-accent"
                              >
                                {r.supplier.email}
                              </a>
                            </div>
                          )}
                          {r.supplier.wholesaleEmail && (
                            <div>
                              <span className="text-ink-400">{lang === 'zh' ? '批发' : 'B2B'}:</span>{' '}
                              <a
                                href={`mailto:${r.supplier.wholesaleEmail}`}
                                onClick={(e) => e.stopPropagation()}
                                className="hover:text-accent"
                              >
                                {r.supplier.wholesaleEmail}
                              </a>
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-ink-300">—</span>
                      )}
                    </td>
                    <td className="table-td whitespace-nowrap">
                      <span className="chip">{r.platform}</span>
                      {r.platform === 'Amazon' && (
                        <span
                          className="chip ml-1 bg-ink-900 text-white"
                          title={lang === 'zh' ? '锁定 amazon.com（美国市场）' : 'Locked to amazon.com (US marketplace)'}
                        >
                          🇺🇸 US
                        </span>
                      )}
                    </td>
                    <td className="table-td">
                      <PriceCard price={r.price} compact />
                    </td>
                    <td className="table-td whitespace-nowrap">
                      {r.rating ? (
                        <span>
                          <span className="font-semibold text-ink-900">{r.rating.toFixed(1)}</span>
                          <span className="ml-1 text-ink-400">/ 5</span>
                          {typeof r.reviews === 'number' && (
                            <span className="ml-1 text-xs text-ink-400">
                              ({r.reviews.toLocaleString()})
                            </span>
                          )}
                        </span>
                      ) : r.pendingFields?.some((f) => f === 'rating' || f === 'reviews') ? (
                        <PendingChip />
                      ) : (
                        <span className="text-ink-300">—</span>
                      )}
                    </td>
                    <td className="table-td whitespace-nowrap text-xs">
                      {(() => {
                        const info = parseShipping(r);
                        const chip = shippingChipLabel(info, lang);
                        const lead = leadTimeChipLabel(r.leadTimeDays, r.leadTimeNote, lang);
                        return (
                          <div className="flex flex-col gap-1">
                            <div className="flex flex-wrap items-center gap-1">
                              <span
                                className={`rounded-full px-1.5 py-0.5 text-[11px] font-semibold ring-1 ${chip.cls}`}
                                title={chip.title}
                              >
                                {chip.text}
                              </span>
                              {r.shipFrom && (
                                <span
                                  className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold ring-1 ${
                                    r.shipFrom === 'US'
                                      ? 'bg-ok/5 text-ok ring-ok/20'
                                      : 'bg-warn/5 text-warn ring-warn/20'
                                  }`}
                                >
                                  {r.shipFrom === 'US' ? '🇺🇸 US 仓' : r.shipFrom === 'CN' ? '🇨🇳 CN 直邮' : '🇺🇸+🇨🇳'}
                                </span>
                              )}
                            </div>
                            {lead && (
                              <a
                                href={r.leadTimeSource?.url}
                                target="_blank"
                                rel="noreferrer"
                                className={`inline-flex w-fit items-center rounded-full px-1.5 py-0.5 text-[11px] font-semibold ring-1 transition hover:underline ${lead.cls}`}
                                title={
                                  (lang === 'zh' ? '送达时效来源：' : 'Lead time source: ') +
                                  (r.leadTimeSource?.label || '—') +
                                  (lead.title ? ` · ${lead.title}` : '')
                                }
                              >
                                {lead.text}
                              </a>
                            )}
                            {info.raw && info.raw !== '—' && (
                              <span className="text-[10px] text-ink-400">{info.raw}</span>
                            )}
                          </div>
                        );
                      })()}
                    </td>
                    <td className="table-td" onClick={(e) => e.stopPropagation()}>
                      <SourceBadge source={r.source} compact />
                    </td>
                  </tr>
                  {isOpen && (
                    <tr className="bg-ink-50/30">
                      <td colSpan={12} className="px-4 py-4">
                        <ReviewInsightsCard sku={r.id} />
                        <div className="mt-6 border-t border-ink-200 pt-5">
                          <VideoGrid category={category ?? null} sku={r.id} />
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="border-t border-ink-100 bg-ink-50 px-4 py-2 text-[11px] leading-relaxed text-ink-500">
        {lang === 'zh' ? (
          <>
            <div>
              <b>🇺🇸 Amazon US</b> 标记表示该行已锁定 amazon.com（Rainforest API
              强制 <code>amazon_domain=amazon.com</code>）。运费分类：
              <span className="mx-1 rounded bg-ok/10 px-1 text-ok">✅ 包邮</span>
              <span className="mx-1 rounded bg-accent/10 px-1 text-accent">📦 满 $X 包邮</span>
              <span className="mx-1 rounded bg-warn/10 px-1 text-warn">💰 付费</span>
              <span className="mx-1 rounded bg-ink-100 px-1">❓ 未确认</span>
              ；折扣率自动从「售价 vs 原价」推算。
            </div>
            <div className="mt-1">
              送达时效来自各品牌官方运输政策 / Amazon Prime &amp; FBA 文档，分四档：
              <span className="mx-1 rounded bg-ok/10 px-1 text-ok">⚡ 极速 ≤2 天</span>
              <span className="mx-1 rounded bg-accent/10 px-1 text-accent">🚀 快 ≤5 天</span>
              <span className="mx-1 rounded bg-warn/10 px-1 text-warn">📦 标准 ≤10 天</span>
              <span className="mx-1 rounded bg-ink-200 px-1 text-ink-700">🚛 货运 &gt;10 天</span>
              ；点击 chip 跳转该品牌的官方运输页。
            </div>
            <div className="mt-1">
              YouTube 视频按「近 1 年优先 → 2 年 → 3 年 → 全部」级联抓取，每段视频带「
              <span className="text-ok">近 1 年</span> /{' '}
              <span className="text-accent">近 2 年</span> /{' '}
              <span className="text-warn">近 3 年</span> /{' '}
              <span className="text-ink-500">3 年以上</span>」徽章。
            </div>
            <div className="mt-1">点击任意行展开「优点 / 痛点」洞察卡片 + 相关 YouTube 达人视频。</div>
          </>
        ) : (
          <>
            <div>
              <b>🇺🇸 Amazon US</b> tag means the row is locked to amazon.com (Rainforest API
              hard-coded to <code>amazon_domain=amazon.com</code>). Shipping classification:
              <span className="mx-1 rounded bg-ok/10 px-1 text-ok">✅ Free</span>
              <span className="mx-1 rounded bg-accent/10 px-1 text-accent">📦 Free over $X</span>
              <span className="mx-1 rounded bg-warn/10 px-1 text-warn">💰 Paid</span>
              <span className="mx-1 rounded bg-ink-100 px-1">❓ Unverified</span>
              ; discount % auto-derived from current vs original price.
            </div>
            <div className="mt-1">
              Lead times come from each brand's published shipping policy and Amazon Prime / FBA docs:
              <span className="mx-1 rounded bg-ok/10 px-1 text-ok">⚡ Express ≤2d</span>
              <span className="mx-1 rounded bg-accent/10 px-1 text-accent">🚀 Fast ≤5d</span>
              <span className="mx-1 rounded bg-warn/10 px-1 text-warn">📦 Standard ≤10d</span>
              <span className="mx-1 rounded bg-ink-200 px-1 text-ink-700">🚛 Freight &gt;10d</span>
              ; click the chip to open the brand's shipping policy.
            </div>
            <div className="mt-1">
              YouTube videos use a cascade — last 12 mo → 24 mo → 36 mo → any age. Each
              card carries a{' '}
              <span className="text-ok">&lt;1 yr</span> /{' '}
              <span className="text-accent">&lt;2 yr</span> /{' '}
              <span className="text-warn">&lt;3 yr</span> /{' '}
              <span className="text-ink-500">&gt;3 yr</span> badge.
            </div>
            <div className="mt-1">Click any row to expand "pros / cons" insights and related creator videos.</div>
          </>
        )}
      </div>
    </div>
  );
}
