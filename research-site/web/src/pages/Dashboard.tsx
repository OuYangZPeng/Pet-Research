import { useTranslation } from 'react-i18next';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Link } from 'react-router-dom';
import CategoryHero from '../components/CategoryHero';
import Kpi from '../components/Kpi';
import SectionHeading from '../components/SectionHeading';
import {
  useDogFood,
  useDogTreats,
  useInfluencers,
  useMeta,
  useSeasonality,
} from '../lib/loadData';
import SeasonalityChart from '../components/SeasonalityChart';
import SourceBadge from '../components/SourceBadge';

export default function Dashboard() {
  const { t, i18n } = useTranslation();
  const { data: dogFood } = useDogFood();
  const { data: dogTreats } = useDogTreats();
  const { data: influencers } = useInfluencers();
  const { data: meta } = useMeta();
  const { data: season } = useSeasonality();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const aovData = [dogFood?.aov, dogTreats?.aov]
    .filter(Boolean)
    .map((a) => ({
      name: lang === 'zh' ? a!.categoryLabelZh : a!.categoryLabel,
      p25: Math.round(
        a!.buckets.reduce((s, b) => s + b.p25, 0) / a!.buckets.length
      ),
      median: Math.round(
        a!.buckets.reduce((s, b) => s + b.median, 0) / a!.buckets.length
      ),
      p75: Math.round(
        a!.buckets.reduce((s, b) => s + b.p75, 0) / a!.buckets.length
      ),
    }));

  const totalCompetitors =
    (dogFood?.competitors.length || 0) + (dogTreats?.competitors.length || 0);

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('dashboard.title')}
        desc={t('dashboard.intro')}
        chips={
          <>
            <span className="chip-accent">Amazon BSR Pet</span>
            <span className="chip-accent">Chewy · DTC</span>
            <span className="chip-accent">YouTube · TikTok · Reddit</span>
            <span className="chip-accent">APPA 2025</span>
            <span className="chip-accent">Subscribe & Save</span>
          </>
        }
      />

      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Kpi label={t('dashboard.kpi.categories')} value="2" hint={t('brand.subtitle')} />
        <Kpi
          label={t('dashboard.kpi.competitors')}
          value={totalCompetitors || '—'}
          hint="Amazon · Chewy · DTC"
        />
        <Kpi
          label={t('dashboard.kpi.creators')}
          value={influencers?.length || '—'}
          hint="YouTube · IG · Reddit"
        />
        <Kpi
          label={t('dashboard.kpi.sources')}
          value={meta?.sources.length || '—'}
          hint={t('common.lastFetched')}
          accent
        />
      </div>

      <div className="mb-8 grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 card p-5">
          <SectionHeading
            title={t('dashboard.aovByCat')}
            subtitle={t('dashboard.aovByCatDesc')}
          />
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aovData}>
                <CartesianGrid stroke="#eef1f5" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 13, fill: '#3f4753' }} />
                <YAxis
                  tick={{ fontSize: 12, fill: '#8a93a6' }}
                  tickFormatter={(v) => `$${v}`}
                />
                <Tooltip
                  contentStyle={{ borderRadius: 12, borderColor: '#dde2ea', fontSize: 12 }}
                  formatter={(v: number) => `$${v.toLocaleString()}`}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="p25" name="P25" fill="#bcc4d2" radius={[6, 6, 0, 0]} />
                <Bar dataKey="median" name={t('common.median')} fill="#0ea5a3" radius={[6, 6, 0, 0]} />
                <Bar dataKey="p75" name="P75" fill="#3f4753" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {t('dashboard.marketSize')}
          </div>
          <div className="mt-2 text-4xl font-bold tracking-tight text-accent">
            {t('dashboard.marketSizeValue')}
          </div>
          <p className="mt-2 text-sm text-ink-500">{t('dashboard.marketSizeNote')}</p>
          <div className="mt-4">
            <SourceBadge
              source={{
                label: 'APPA National Pet Owners Survey 2025',
                url: 'https://americanpetproducts.org/industry-trends-and-stats',
                fetchedAt: '2026-07-03T00:00:00Z',
              }}
            />
          </div>
        </div>
      </div>

      {season?.points && (
        <div className="mb-8">
          <SectionHeading
            title={t('nav.seasonality')}
            subtitle={lang === 'zh' ? season.insightZh : season.insight}
            action={
              <Link
                to="/insights/seasonality"
                className="text-sm font-semibold text-accent hover:underline"
              >
                →
              </Link>
            }
          />
          <SeasonalityChart points={season.points} />
        </div>
      )}

      <div>
        <SectionHeading title={t('dashboard.quickFacts')} />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card p-5">
              <div className="text-sm font-semibold text-ink-900">
                {t(`dashboard.fact${i}Title`)}
              </div>
              <p className="mt-2 text-sm text-ink-600">{t(`dashboard.fact${i}Body`)}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
