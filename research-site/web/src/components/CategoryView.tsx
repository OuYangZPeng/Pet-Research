import { useTranslation } from 'react-i18next';
import CategoryHero from './CategoryHero';
import SectionHeading from './SectionHeading';
import CompetitorTable from './CompetitorTable';
import AovChart from './AovChart';
import BundleList from './BundleList';
import InfluencerCard from './InfluencerCard';
import SeasonalityChart from './SeasonalityChart';
import SourceBadge from './SourceBadge';
import ShippingMatrix from './ShippingMatrix';
import { useInfluencers, useSeasonality, useShipping } from '../lib/loadData';
import type { CategoryDataset, CategorySlug } from '../lib/types';

type Props = {
  title: string;
  desc: string;
  category: CategorySlug;
  data: CategoryDataset | null;
  fitPlatforms: ('YouTube' | 'TikTok' | 'Instagram' | 'Reddit' | 'Facebook')[];
};

export default function CategoryView({ title, desc, category, data, fitPlatforms }: Props) {
  const { t, i18n } = useTranslation();
  const { data: influencers } = useInfluencers();
  const { data: season } = useSeasonality();
  const { data: shipping } = useShipping();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  if (!data) return <div className="text-ink-400">Loading…</div>;

  const categoryInfluencers = (influencers || [])
    .filter((i) => !i.categories?.length || i.categories.includes(category))
    .filter((i) => i.categoryFit >= 7)
    .filter((i) => fitPlatforms.includes(i.platform))
    .slice(0, 6);

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={title}
        desc={desc}
        chips={
          <>
            <span className="chip-accent">
              {data.competitors.length} {lang === 'zh' ? '竞品' : 'competitors'}
            </span>
            <span className="chip-accent">{data.aov.buckets.length} platforms</span>
            <span className="chip-accent">
              {data.bundles.length} {lang === 'zh' ? '销售形式样本' : 'bundle observations'}
            </span>
          </>
        }
      />

      <section className="mb-10">
        <SectionHeading
          title={t('sections.competitors')}
          subtitle={lang === 'zh' ? data.aov.insightZh : data.aov.insight}
        />
        {data.competitors.some((c) => c.pendingFields && c.pendingFields.length > 0) && (
          <div className="mb-3 rounded-xl border border-warn/30 bg-warn/5 p-3 text-xs text-ink-700">
            <span className="font-semibold text-warn">
              ⌛ {lang === 'zh' ? '数据透明声明' : 'Data transparency'}：
            </span>{' '}
            {lang === 'zh'
              ? '本表的「评分 / 评论数」字段在 seed 阶段未填入，避免任何估算误导。运行 '
              : 'The “rating / reviews” column is intentionally empty in the seed to avoid placeholder estimates. Run '}
            <code className="rounded bg-ink-900 px-1.5 py-0.5 font-mono text-[10px] text-ink-100">
              python scraper/run_all.py
            </code>{' '}
            {lang === 'zh'
              ? '（配 Amazon PA-API 凭证）后会从官方接口回填真实值。'
              : '(with Amazon PA-API credentials) to populate them from the official endpoint.'}
          </div>
        )}
        <CompetitorTable rows={data.competitors} category={category} />
      </section>

      <section className="mb-10">
        <SectionHeading title={t('sections.creators')} />
        {categoryInfluencers.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {categoryInfluencers.map((c) => (
              <InfluencerCard key={c.id} entry={c} />
            ))}
          </div>
        ) : (
          <div className="card p-6 text-sm text-ink-500">
            {lang === 'zh'
              ? '本品类无高匹配度达人，详见达人榜页全量名单。'
              : 'No high-fit creators in this category. See the Influencers page for the full list.'}
          </div>
        )}
      </section>

      <section className="mb-10">
        <SectionHeading title={t('sections.aov')} subtitle={lang === 'zh' ? data.aov.insightZh : data.aov.insight} />
        <AovChart aov={data.aov} />
      </section>

      {season?.points && (
        <section className="mb-10">
          <SectionHeading
            title={t('sections.season')}
            subtitle={lang === 'zh' ? season.insightZh : season.insight}
          />
          <SeasonalityChart points={season.points} />
        </section>
      )}

      <section className="mb-10">
        <SectionHeading title={t('sections.bundle')} />
        <BundleList items={data.bundles} />
      </section>

      <section className="mb-10">
        <SectionHeading
          title={t('sections.shipping')}
          subtitle={
            lang === 'zh'
              ? '运费、折扣、时效横向对比；US 仓速度更快但需要先备货，CN 直邮启动成本更低。'
              : 'Shipping, discount and lead-time matrix. US warehouse is faster but requires upfront inventory; ship-from-China has a lower startup cost.'
          }
        />
        {shipping?.modes && <ShippingMatrix modes={shipping.modes} />}

        <div className="mt-6 card p-5">
          <div className="mb-3 text-sm font-semibold text-ink-900">
            {lang === 'zh' ? '本品类竞品快照（含运费门槛）' : 'This category — pricing snapshot incl. shipping'}
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-ink-100">
              <thead className="bg-ink-50">
                <tr>
                  <th className="table-th">{t('common.brand')}</th>
                  <th className="table-th">{t('common.product')}</th>
                  <th className="table-th">{t('common.current')}</th>
                  <th className="table-th">{t('common.original')}</th>
                  <th className="table-th">{t('common.discount')}</th>
                  <th className="table-th">{t('common.warehouse')}</th>
                  <th className="table-th">{t('common.shipping')}</th>
                  <th className="table-th">{t('common.source')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100">
                {data.competitors.map((c) => {
                  const discount =
                    c.price.original && c.price.original > c.price.current
                      ? Math.round((1 - c.price.current / c.price.original) * 100)
                      : 0;
                  return (
                    <tr key={c.id}>
                      <td className="table-td font-semibold">{c.brand}</td>
                      <td className="table-td max-w-md text-xs">
                        {lang === 'zh' && c.productZh ? c.productZh : c.product}
                      </td>
                      <td className="table-td font-mono">${c.price.current.toFixed(0)}</td>
                      <td className="table-td font-mono text-ink-400">
                        {c.price.original ? `$${c.price.original.toFixed(0)}` : '—'}
                      </td>
                      <td className="table-td">
                        {discount > 0 ? (
                          <span className="chip-accent">-{discount}%</span>
                        ) : (
                          <span className="text-ink-300">—</span>
                        )}
                      </td>
                      <td className="table-td">
                        {c.shipFrom === 'US' ? '🇺🇸 US' : c.shipFrom === 'CN' ? '🇨🇳 CN' : '—'}
                      </td>
                      <td className="table-td text-xs">{c.shippingNote || '—'}</td>
                      <td className="table-td">
                        <SourceBadge source={c.source} compact />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </>
  );
}
