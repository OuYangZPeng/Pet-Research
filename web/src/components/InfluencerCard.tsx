import { useTranslation } from 'react-i18next';
import type { InfluencerEntry } from '../lib/types';
import SourceBadge from './SourceBadge';
import { fmtNumber } from '../lib/format';

const platformColor: Record<string, string> = {
  YouTube: 'bg-red-50 text-red-600',
  TikTok: 'bg-ink-900 text-white',
  Instagram: 'bg-pink-50 text-pink-600',
  Reddit: 'bg-orange-50 text-orange-600',
  Facebook: 'bg-blue-50 text-blue-600',
};

export default function InfluencerCard({ entry }: { entry: InfluencerEntry }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  return (
    <div className="card flex h-full flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <span
            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
              platformColor[entry.platform] || 'bg-ink-100 text-ink-700'
            }`}
          >
            {entry.platform}
          </span>
          <h3 className="mt-2 text-lg font-semibold text-ink-900">
            <a href={entry.url} target="_blank" rel="noreferrer noopener" className="hover:text-accent">
              {entry.displayName}
            </a>
          </h3>
          <div className="text-xs text-ink-400">@{entry.handle}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-accent">{fmtNumber(entry.audience)}</div>
          <div className="text-xs text-ink-400">{t(`common.${entry.audienceUnit}`)}</div>
        </div>
      </div>

      <p className="mt-3 text-sm text-ink-600">
        {lang === 'zh' && entry.notesZh ? entry.notesZh : entry.notes}
      </p>

      <div className="mt-3 flex items-center justify-between gap-2 text-xs">
        <div>
          <span className="text-ink-400">{t('influencers.fitScore')}: </span>
          <span className="font-semibold text-ink-800">{entry.categoryFit} / 10</span>
        </div>
        {typeof entry.totalViews === 'number' && (
          <div>
            <span className="text-ink-400">{t('common.views')}: </span>
            <span className="font-semibold text-ink-800">{fmtNumber(entry.totalViews)}</span>
          </div>
        )}
      </div>

      {entry.topPieceUrl && entry.topPieceTitle && (
        <a
          href={entry.topPieceUrl}
          target="_blank"
          rel="noreferrer noopener"
          className="mt-3 line-clamp-2 rounded-lg bg-ink-50 px-3 py-2 text-xs text-ink-600 hover:bg-accent/10 hover:text-accent"
        >
          ▶ {entry.topPieceTitle}
        </a>
      )}

      <div className="mt-auto pt-3">
        <SourceBadge source={entry.source} />
      </div>
    </div>
  );
}
