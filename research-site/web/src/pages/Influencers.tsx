import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import CategoryHero from '../components/CategoryHero';
import InfluencerCard from '../components/InfluencerCard';
import { useInfluencers } from '../lib/loadData';

const allPlatforms = ['All', 'YouTube', 'Instagram', 'Reddit', 'TikTok', 'Facebook'] as const;
type PlatformFilter = (typeof allPlatforms)[number];

export default function Influencers() {
  const { t, i18n } = useTranslation();
  const { data } = useInfluencers();
  const [filter, setFilter] = useState<PlatformFilter>('All');
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const rows = (data || []).filter((d) => filter === 'All' || d.platform === filter);
  rows.sort((a, b) => b.categoryFit * 100000 + b.audience - (a.categoryFit * 100000 + a.audience));

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('influencers.title')}
        desc={t('influencers.desc')}
        chips={
          <>
            {allPlatforms.map((p) => (
              <button
                key={p}
                onClick={() => setFilter(p)}
                className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                  filter === p
                    ? 'bg-accent text-white'
                    : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
                }`}
              >
                {p === 'All' ? (lang === 'zh' ? '全部' : 'All') : p}
              </button>
            ))}
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {rows.map((r) => (
          <InfluencerCard key={r.id} entry={r} />
        ))}
      </div>
    </>
  );
}
