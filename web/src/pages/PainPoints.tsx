import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from 'recharts';
import CategoryHero from '../components/CategoryHero';
import SectionHeading from '../components/SectionHeading';
import PainPointHeatmap from '../components/PainPointHeatmap';
import { usePainPoints } from '../lib/loadData';
import type { PainPointBucket, PainPointCategory } from '../lib/types';

import type { CategorySlug } from '../lib/types';

const CATEGORIES: { id: CategorySlug; emoji: string }[] = [
  { id: 'dog-food', emoji: '🦴' },
  { id: 'dog-treats', emoji: '🍖' },
];

function BucketBarChart({
  buckets,
  totalSkus,
  lang,
}: {
  buckets: PainPointBucket[];
  totalSkus: number;
  lang: 'en' | 'zh';
}) {
  const data = buckets.map((b) => ({
    id: b.id,
    label: `${b.icon} ${lang === 'zh' ? b.labelZh : b.label}`,
    skuCount: b.skuCount,
    mentions: b.totalCount,
    pctSkus: Math.round((b.skuCount / Math.max(1, totalSkus)) * 100),
  }));

  return (
    <div className="card p-5">
      <div className="h-[420px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24, top: 8, bottom: 8 }}>
            <CartesianGrid stroke="#eef1f5" horizontal={false} />
            <XAxis
              type="number"
              tick={{ fontSize: 12, fill: '#8a93a6' }}
              tickFormatter={(v) => String(v)}
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ fontSize: 11, fill: '#3f4753' }}
              width={280}
            />
            <Tooltip
              contentStyle={{ borderRadius: 12, borderColor: '#dde2ea', fontSize: 12 }}
              formatter={(value: number, key: string) => {
                if (key === 'mentions') return [`${value} ${lang === 'zh' ? '条提及' : 'mentions'}`, lang === 'zh' ? '总提及数' : 'Total mentions'];
                if (key === 'skuCount') return [`${value} / ${totalSkus} ${lang === 'zh' ? 'SKU' : 'SKUs'}`, lang === 'zh' ? '影响 SKU 数' : 'Affected SKUs'];
                return [value, key];
              }}
            />
            <Bar dataKey="skuCount" name={lang === 'zh' ? '影响 SKU 数' : 'Affected SKUs'} radius={[0, 6, 6, 0]}>
              {data.map((entry) => (
                <Cell
                  key={entry.id}
                  fill={
                    entry.pctSkus >= 70
                      ? '#ef4444'
                      : entry.pctSkus >= 40
                        ? '#f59e0b'
                        : '#0ea5a3'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function BucketDetail({
  bucket,
  category,
  lang,
}: {
  bucket: PainPointBucket;
  category: PainPointCategory;
  lang: 'en' | 'zh';
}) {
  return (
    <div className="card p-5">
      <div className="flex items-start gap-3">
        <span className="text-3xl">{bucket.icon}</span>
        <div className="flex-1">
          <div className="text-base font-semibold text-ink-900">
            {lang === 'zh' ? bucket.labelZh : bucket.label}
          </div>
          <div className="mt-1 text-xs text-ink-400">
            <span className="font-semibold text-danger">{bucket.skuCount}</span> /{' '}
            {category.skuList.length} {lang === 'zh' ? 'SKU 受影响 ·' : 'SKUs affected · '}
            <span className="font-semibold text-ink-700">{bucket.totalCount}</span>{' '}
            {lang === 'zh' ? '条总提及' : 'mentions total'}
          </div>
        </div>
      </div>

      {bucket.sampleQuote && (
        <blockquote className="mt-3 rounded-lg bg-ink-50 p-3 text-sm italic text-ink-600">
          "{bucket.sampleQuote.length > 360 ? bucket.sampleQuote.slice(0, 360) + '…' : bucket.sampleQuote}"
          <div className="mt-1 text-[11px] not-italic text-ink-400">
            — {bucket.quoteSku}
            {typeof bucket.quoteRating === 'number' ? (
              <span className="ml-2 text-warn">★ {bucket.quoteRating.toFixed(1)}</span>
            ) : null}
            {bucket.quoteUrl && (
              <>
                {' · '}
                <a
                  href={bucket.quoteUrl}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-accent hover:underline"
                >
                  {lang === 'zh' ? '原文' : 'source'}
                </a>
              </>
            )}
          </div>
        </blockquote>
      )}

      <div className="mt-3 flex flex-wrap gap-1">
        {bucket.skuBreakdown.slice(0, 12).map((s) => (
          <span
            key={s.sku}
            className="rounded-full bg-danger/10 px-2 py-0.5 text-[11px] font-mono text-danger"
            title={`${s.count} mentions in ${s.sku}`}
          >
            {s.sku} ×{s.count}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function PainPoints() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const { data } = usePainPoints();
  const [active, setActive] = useState<CategorySlug>('dog-food');

  if (!data) return <div className="text-ink-400">Loading…</div>;

  const categoriesWithData = CATEGORIES.filter((c) => data[c.id]?.buckets?.length);
  const current = data[active] || data[categoriesWithData[0]?.id || 'dog-food'];
  if (!current) {
    return (
      <div className="card p-5 text-sm text-ink-500">
        {lang === 'zh' ? '尚无聚合数据' : 'No aggregated pain-point data yet.'}
      </div>
    );
  }

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('painpoints.title')}
        desc={t('painpoints.desc')}
        chips={
          <>
            {categoriesWithData.map((c) => {
              const cat = data[c.id];
              return (
                <button
                  key={c.id}
                  onClick={() => setActive(c.id)}
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                    active === c.id
                      ? 'bg-accent text-white'
                      : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
                  }`}
                >
                  {c.emoji} {lang === 'zh' ? cat?.labelZh : cat?.label} ({cat?.buckets.length})
                </button>
              );
            })}
          </>
        }
      />

      <section className="mb-8">
        <SectionHeading
          title={t('painpoints.frequency')}
          subtitle={
            lang === 'zh'
              ? `按影响的 SKU 数排序 · 颜色：>70% 红 · 40–70% 黄 · <40% 青`
              : 'Sorted by affected SKUs · color: >70% red · 40–70% amber · <40% teal'
          }
        />
        <BucketBarChart
          buckets={current.buckets}
          totalSkus={current.skuList.length}
          lang={lang}
        />
      </section>

      <section className="mb-8">
        <SectionHeading
          title={t('painpoints.heatmap')}
          subtitle={
            lang === 'zh'
              ? '主题 × SKU 矩阵，色块深浅 = 该 SKU 中提及次数。鼠标悬停查看详情。'
              : 'Theme × SKU matrix. Darker = more mentions. Hover for details.'
          }
        />
        <PainPointHeatmap data={current} />
      </section>

      <section className="mb-8">
        <SectionHeading
          title={t('painpoints.details')}
          subtitle={
            lang === 'zh'
              ? `每个痛点的代表性原文引用 + 受影响 SKU 清单（${current.buckets.length} 个主题）`
              : `Sample quote + affected SKUs for each pain point (${current.buckets.length} themes)`
          }
        />
        <div className="grid gap-3 md:grid-cols-2">
          {current.buckets.map((b) => (
            <BucketDetail key={b.id} bucket={b} category={current} lang={lang} />
          ))}
        </div>
      </section>
    </>
  );
}
