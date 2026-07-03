import { useTranslation } from 'react-i18next';
import type { BundleObservation } from '../lib/types';
import SourceBadge from './SourceBadge';

const typeChip: Record<string, string> = {
  single: 'chip',
  bundle: 'chip-accent',
  'trade-program': 'inline-flex items-center gap-1 rounded-full bg-ink-900 px-2.5 py-0.5 text-xs font-semibold text-white',
};

export default function BundleList({ items }: { items: BundleObservation[] }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  return (
    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
      {items.map((b, idx) => (
        <a
          key={idx}
          href={b.url}
          target="_blank"
          rel="noreferrer noopener"
          className="card group flex h-full flex-col p-4 transition hover:-translate-y-0.5 hover:shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold text-ink-900">{b.brand}</div>
            <span className={typeChip[b.type] || 'chip'}>
              {b.type === 'bundle'
                ? t('common.bundle')
                : b.type === 'trade-program'
                  ? t('common.tradeProgram')
                  : t('common.single')}
            </span>
          </div>
          <div className="mt-1 text-sm text-ink-700 group-hover:text-accent">
            {lang === 'zh' && b.productZh ? b.productZh : b.product}
          </div>
          <p className="mt-2 text-xs text-ink-500">{lang === 'zh' ? b.detailZh : b.detail}</p>
          <div className="mt-auto pt-3">
            <SourceBadge source={b.source} compact />
          </div>
        </a>
      ))}
    </div>
  );
}
