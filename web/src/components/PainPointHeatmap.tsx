import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { PainPointCategory } from '../lib/types';

function colorFor(count: number, max: number): string {
  if (count <= 0 || max <= 0) return 'bg-ink-50';
  const t = Math.min(1, count / max);
  if (t < 0.2) return 'bg-danger/15';
  if (t < 0.4) return 'bg-danger/30';
  if (t < 0.6) return 'bg-danger/50';
  if (t < 0.8) return 'bg-danger/70';
  return 'bg-danger/90';
}

export default function PainPointHeatmap({ data }: { data: PainPointCategory }) {
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const [hover, setHover] = useState<{ bid: string; sku: string } | null>(null);

  const skuToBrand: Record<string, { brand: string; product: string; productZh?: string }> = {};
  data.skuList.forEach((s) => (skuToBrand[s.sku] = s));

  const maxCount = Math.max(
    1,
    ...data.buckets.flatMap((b) => Object.values(data.matrix[b.id] || {}))
  );

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-0">
          <thead className="bg-ink-50">
            <tr>
              <th className="sticky left-0 z-10 bg-ink-50 px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-ink-400">
                {lang === 'zh' ? '痛点主题' : 'Pain point'}
              </th>
              {data.skuList.map((s) => (
                <th
                  key={s.sku}
                  className="px-1 py-2 text-[10px] font-mono text-ink-500"
                  style={{ writingMode: 'vertical-rl', minWidth: 32, height: 110 }}
                  title={`${s.brand} — ${lang === 'zh' && s.productZh ? s.productZh : s.product}`}
                >
                  <span className="block truncate" style={{ maxHeight: 96 }}>
                    {s.brand} · {s.sku}
                  </span>
                </th>
              ))}
              <th className="px-3 py-2 text-right text-xs font-semibold uppercase tracking-wider text-ink-400">
                {lang === 'zh' ? '覆盖' : 'Skus'}
              </th>
            </tr>
          </thead>
          <tbody>
            {data.buckets.map((b) => (
              <tr key={b.id} className="border-t border-ink-100">
                <td className="sticky left-0 z-10 max-w-xs bg-white px-3 py-2 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="text-base leading-none">{b.icon}</span>
                    <div>
                      <div className="font-semibold text-ink-900">
                        {lang === 'zh' ? b.labelZh : b.label}
                      </div>
                      <div className="text-[11px] text-ink-400">
                        {b.totalCount}{' '}
                        {lang === 'zh' ? '条提及' : 'mentions'}
                      </div>
                    </div>
                  </div>
                </td>
                {data.skuList.map((s) => {
                  const n = (data.matrix[b.id] || {})[s.sku] || 0;
                  const cls = colorFor(n, maxCount);
                  const active = hover?.bid === b.id && hover?.sku === s.sku;
                  return (
                    <td
                      key={s.sku}
                      onMouseEnter={() => setHover({ bid: b.id, sku: s.sku })}
                      onMouseLeave={() => setHover(null)}
                      className={`relative h-8 cursor-default border border-white ${cls} ${
                        active ? 'ring-2 ring-accent ring-offset-1' : ''
                      }`}
                      title={
                        n > 0
                          ? `${s.brand} ${s.sku}: ${n} ${
                              lang === 'zh' ? '条提及' : 'mentions'
                            }`
                          : ''
                      }
                    >
                      {n > 0 && (
                        <span className="absolute inset-0 grid place-items-center text-[10px] font-bold text-white drop-shadow">
                          {n}
                        </span>
                      )}
                    </td>
                  );
                })}
                <td className="bg-white px-3 py-2 text-right text-xs font-semibold text-ink-700">
                  {b.skuCount}/{data.skuList.length}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center gap-2 border-t border-ink-100 bg-ink-50 px-4 py-2 text-[11px] text-ink-400">
        <span>{lang === 'zh' ? '颜色深浅 = 该 SKU 提及次数' : 'Cell color = # mentions per SKU'}</span>
        <span className="ml-3 flex items-center gap-1">
          {[15, 30, 50, 70, 90].map((alpha) => (
            <span
              key={alpha}
              className="inline-block h-3 w-3 rounded-sm"
              style={{ background: `rgba(239,68,68,${alpha / 100})` }}
            />
          ))}
          <span className="ml-1">少 → 多</span>
        </span>
      </div>
    </div>
  );
}
