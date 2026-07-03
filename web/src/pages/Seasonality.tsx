import { useTranslation } from 'react-i18next';
import CategoryHero from '../components/CategoryHero';
import SectionHeading from '../components/SectionHeading';
import SeasonalityChart from '../components/SeasonalityChart';
import SourceBadge from '../components/SourceBadge';
import { useSeasonality } from '../lib/loadData';

export default function Seasonality() {
  const { t, i18n } = useTranslation();
  const { data } = useSeasonality();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  if (!data) return <div className="text-ink-400">Loading…</div>;

  const peakMonths = data.points.filter((p) => p.band === 'peak');
  const offMonths = data.points.filter((p) => p.band === 'off');

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('seasonality.title')}
        desc={t('seasonality.desc')}
        chips={
          <>
            <span className="chip" style={{ background: '#0ea5a3', color: '#fff' }}>
              {t('seasonality.peakLabel')} · {peakMonths.length} mo
            </span>
            <span className="chip">{t('seasonality.shoulderLabel')}</span>
            <span className="chip" style={{ background: '#f59e0b', color: '#fff' }}>
              {t('seasonality.offLabel')} · {offMonths.length} mo
            </span>
          </>
        }
      />

      <SectionHeading
        title={lang === 'zh' ? '需求强度 + 折扣深度 · 全年曲线' : 'Demand index + discount depth · annual curve'}
        subtitle={lang === 'zh' ? data.insightZh : data.insight}
      />
      <SeasonalityChart points={data.points} />

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-accent">
            {t('seasonality.peakLabel')} · Oct–Jan
          </div>
          <div className="mt-2 text-base font-semibold text-ink-900">
            {lang === 'zh' ? '节日囤货 · 换粮高峰' : 'Holiday stock-up · diet switches'}
          </div>
          <p className="mt-2 text-sm text-ink-600">
            {lang === 'zh'
              ? 'Q4 零食礼盒与主粮囤货；1 月「健康决议」换粮 campaign 密集；折扣相对较浅但转化最高。'
              : 'Q4 treat gifting and kibble stock-ups; January diet-switch campaigns peak; thinner discounts but highest conversion.'}
          </p>
        </div>
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-warn">
            {t('seasonality.shoulderLabel')} · Mar–May · Sep
          </div>
          <div className="mt-2 text-base font-semibold text-ink-900">
            {lang === 'zh' ? '平稳上新 · 订阅拉新' : 'Steady launches · subscription growth'}
          </div>
          <p className="mt-2 text-sm text-ink-600">
            {lang === 'zh'
              ? '春季新品口味上市；秋季为 Q4 礼盒备货期。Chewy Autoship 和 Amazon S&S 是拉新核心。'
              : 'Spring flavor launches; fall is the lead-up to Q4 gift boxes. Chewy Autoship and Amazon S&S drive acquisition.'}
          </p>
        </div>
        <div className="card p-5">
          <div className="text-xs font-medium uppercase tracking-wider text-danger">
            {t('seasonality.offLabel')} · Jun–Aug · Feb
          </div>
          <div className="mt-2 text-base font-semibold text-ink-900">
            {lang === 'zh' ? '夏季略淡 · BFCM 前蓄力' : 'Summer lull · pre-BFCM buildup'}
          </div>
          <p className="mt-2 text-sm text-ink-600">
            {lang === 'zh'
              ? '夏季出行导致冲动零食购买下降；鲜食冷链成本略升。2 月是清库存和测款窗口，11 月黑五折扣最深。'
              : 'Summer travel softens impulse treat buys; fresh-food cold-chain costs tick up. February is a clearance/test window; November BFCM has the deepest discounts.'}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <SectionHeading title={t('common.sources')} />
        <div className="card p-5">
          <ul className="space-y-2">
            <li>
              <SourceBadge
                source={{
                  label: 'APPA National Pet Owners Survey 2025',
                  url: 'https://americanpetproducts.org/industry-trends-and-stats',
                  fetchedAt: '2026-07-03T15:00:00Z',
                }}
              />
            </li>
            <li>
              <SourceBadge
                source={{
                  label: 'Chewy — pet food shopping trends & Autoship data',
                  url: 'https://www.chewy.com/app/content/shipping',
                  fetchedAt: '2026-07-03T15:00:00Z',
                }}
              />
            </li>
            <li>
              <SourceBadge
                source={{
                  label: 'AKC — dog nutrition & food-switching guidance',
                  url: 'https://www.akc.org/expert-advice/nutrition/switching-dog-food/',
                  fetchedAt: '2026-07-03T15:00:00Z',
                }}
              />
            </li>
          </ul>
        </div>
      </div>
    </>
  );
}
