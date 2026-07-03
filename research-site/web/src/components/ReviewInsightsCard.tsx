import { useTranslation } from 'react-i18next';
import type { InsightTheme, ReviewInsight } from '../lib/types';
import { fmtDate, fmtNumber } from '../lib/format';
import SourceBadge from './SourceBadge';
import { useReviewInsight } from '../lib/loadData';

const channelColor: Record<string, string> = {
  amazon: 'bg-orange-50 text-orange-600',
  chewy: 'bg-blue-50 text-blue-700',
  dtc: 'bg-teal-50 text-teal-700',
  trustpilot: 'bg-emerald-50 text-emerald-700',
  reddit: 'bg-orange-50 text-orange-700',
};

function ThemeRow({ theme, tone, lang }: { theme: InsightTheme; tone: 'good' | 'bad'; lang: 'zh' | 'en' }) {
  const accent = tone === 'good' ? 'text-ok' : 'text-danger';
  return (
    <li className="border-b border-ink-100 py-2 last:border-b-0">
      <div className="flex items-baseline gap-2">
        <span className={`text-base font-semibold ${accent}`}>
          {tone === 'good' ? '✓' : '✗'}
        </span>
        <span className="flex-1 text-sm font-semibold text-ink-900">
          {lang === 'zh' && theme.themeZh ? theme.themeZh : theme.theme}
          <span className="ml-2 rounded-full bg-ink-100 px-2 py-0.5 text-[10px] font-mono text-ink-500">
            ×{theme.count}
          </span>
        </span>
        <div className="flex flex-wrap gap-1">
          {theme.channels.map((ch) => (
            <span
              key={ch}
              className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                channelColor[ch] || 'bg-ink-100 text-ink-600'
              }`}
            >
              {ch}
            </span>
          ))}
        </div>
      </div>
      <a
        href={theme.quoteUrl || undefined}
        target="_blank"
        rel="noreferrer noopener"
        className="ml-6 mt-1 block text-xs italic text-ink-500 hover:text-accent"
      >
        “{theme.quote.length > 220 ? theme.quote.slice(0, 220) + '…' : theme.quote}”
      </a>
      <div className="ml-6 mt-1 flex flex-wrap items-center gap-2 text-[11px] text-ink-400">
        {typeof theme.quoteRating === 'number' && (
          <span>
            <span className="text-warn">★</span> {theme.quoteRating.toFixed(1)}
          </span>
        )}
        {theme.quoteVerified && (
          <span className="rounded-full bg-ok/10 px-1.5 py-0.5 font-semibold text-ok">
            ✓ {lang === 'zh' ? '已验证购买' : 'verified'}
          </span>
        )}
      </div>
    </li>
  );
}

export default function ReviewInsightsCard({ sku }: { sku: string }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const { data, state } = useReviewInsight(sku);

  if (state === 'loading' || state === 'idle') {
    return <div className="rounded-xl bg-ink-50 p-4 text-xs text-ink-400">…</div>;
  }
  if (state === 'missing') {
    return (
      <div className="rounded-xl border border-warn/30 bg-warn/5 p-4 text-xs text-ink-700">
        <span className="font-semibold text-warn">⌛ {lang === 'zh' ? '尚未生成' : 'Not generated'}：</span>{' '}
        {lang === 'zh' ? (
          <>
            还没跑过评论洞察。在 <code className="font-mono">scraper/</code> 目录跑{' '}
            <code className="rounded bg-ink-900 px-1.5 py-0.5 font-mono text-[10px] text-ink-100">
              python refresh_reviews.py --skus {sku}
            </code>{' '}
            然后告诉 Cursor 「处理 _insights_pending.md」就会自动生成。
          </>
        ) : (
          <>
            No insight file for this SKU yet. Run{' '}
            <code className="rounded bg-ink-900 px-1.5 py-0.5 font-mono text-[10px] text-ink-100">
              python refresh_reviews.py --skus {sku}
            </code>{' '}
            then ask Cursor to “process _insights_pending.md”.
          </>
        )}
      </div>
    );
  }
  if (state === 'error' || !data) {
    return (
      <div className="rounded-xl bg-danger/5 p-4 text-xs text-danger">
        Failed to load review insights.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-ink-100 bg-white p-4 shadow-sm">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <div className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {t('reviews.title') /* fallback handled */}
          </div>
          <div className="mt-0.5 flex items-center gap-2 text-sm">
            <span className="font-semibold text-ink-900">
              {lang === 'zh' ? '基于' : 'Based on'} {data.totalReviews}{' '}
              {lang === 'zh' ? '条评论' : 'reviews'}
            </span>
            {typeof data.averageRating === 'number' && (
              <span className="rounded-full bg-warn/10 px-2 py-0.5 text-xs font-semibold text-warn">
                ★ {data.averageRating.toFixed(1)}
              </span>
            )}
            <span className="text-xs text-ink-400">
              · {lang === 'zh' ? '由' : 'by'} {data.generator}
            </span>
          </div>
        </div>
        <div className="text-xs text-ink-400">
          {fmtDate(data.lastUpdated, lang)}
        </div>
      </div>

      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(data.channelBreakdown).map(([ch, n]) => (
          <span
            key={ch}
            className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
              channelColor[ch] || 'bg-ink-100 text-ink-600'
            }`}
            title={`${n} ${lang === 'zh' ? '条来自' : 'reviews from'} ${ch}`}
          >
            {ch} ×{fmtNumber(n)}
          </span>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-ok">
            ✓ {lang === 'zh' ? '优点' : 'Pros'} (top {data.pros.length})
          </div>
          <ul>
            {data.pros.map((p, i) => (
              <ThemeRow key={i} theme={p} tone="good" lang={lang} />
            ))}
            {data.pros.length === 0 && (
              <li className="py-2 text-xs text-ink-400">—</li>
            )}
          </ul>
        </div>
        <div>
          <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-danger">
            ✗ {lang === 'zh' ? '痛点' : 'Cons'} (top {data.cons.length})
          </div>
          <ul>
            {data.cons.map((c, i) => (
              <ThemeRow key={i} theme={c} tone="bad" lang={lang} />
            ))}
            {data.cons.length === 0 && (
              <li className="py-2 text-xs text-ink-400">—</li>
            )}
          </ul>
        </div>
      </div>

      {data.sourcesUsed && data.sourcesUsed.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-ink-100 pt-3 text-[11px]">
          <span className="text-ink-400">{lang === 'zh' ? '原始评论样本' : 'Sample sources'}:</span>
          {data.sourcesUsed.slice(0, 6).map((s, i) => (
            <SourceBadge key={i} source={s} compact />
          ))}
        </div>
      )}
    </div>
  );
}
