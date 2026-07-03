import { useTranslation } from 'react-i18next';
import CategoryHero from '../components/CategoryHero';
import SectionHeading from '../components/SectionHeading';
import ShippingMatrix from '../components/ShippingMatrix';
import SourceBadge from '../components/SourceBadge';
import { useShipping } from '../lib/loadData';
import { fmtUSD } from '../lib/format';

export default function Logistics() {
  const { t, i18n } = useTranslation();
  const { data } = useShipping();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  if (!data) return <div className="text-ink-400">Loading…</div>;

  const sortedThresholds = [...data.thresholds].sort((a, b) => a.threshold - b.threshold);

  return (
    <>
      <CategoryHero
        eyebrow={t('brand.subtitle')}
        title={t('logistics.title')}
        desc={t('logistics.desc')}
        chips={
          <>
            <span className="chip-accent">CN→US 国内直邮 2–35d</span>
            <span className="chip-accent">US 仓 Prime/Chewy 1–3d</span>
            <span className="chip-accent">$0 / $35 / $49 免运门槛</span>
          </>
        }
      />

      <section className="mb-10">
        <SectionHeading title={t('logistics.modes')} />
        <ShippingMatrix modes={data.modes} />
      </section>

      <section className="mb-10">
        <SectionHeading title={t('logistics.shippingThreshold')} subtitle={t('logistics.thresholdNote')} />
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-ink-100">
              <thead className="bg-ink-50">
                <tr>
                  <th className="table-th">{t('common.brand')}</th>
                  <th className="table-th">{t('common.freeShipping')}</th>
                  <th className="table-th">{lang === 'zh' ? '说明' : 'Note'}</th>
                  <th className="table-th">{t('common.source')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 bg-white">
                {sortedThresholds.map((b, idx) => {
                  const yours = b.brand.toLowerCase().includes('your');
                  return (
                    <tr
                      key={idx}
                      className={yours ? 'bg-warn/5 ring-2 ring-warn/20' : ''}
                    >
                      <td className="table-td font-semibold text-ink-900">
                        {b.brand}
                        {yours && (
                          <span className="ml-2 inline-flex rounded-full bg-warn/20 px-2 py-0.5 text-xs font-bold text-warn">
                            ⚠ {lang === 'zh' ? '需复盘' : 'review'}
                          </span>
                        )}
                      </td>
                      <td className="table-td font-mono">
                        {b.threshold === 0
                          ? lang === 'zh'
                            ? '全场包邮'
                            : 'Free site-wide'
                          : fmtUSD(b.threshold) + '+'}
                      </td>
                      <td className="table-td text-xs">{lang === 'zh' ? b.noteZh : b.note}</td>
                      <td className="table-td">
                        <SourceBadge source={b.source} compact />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="mb-10">
        <SectionHeading
          title={lang === 'zh' ? '推荐组合：客单价 × 仓储模式' : 'Recommended combos: AOV × fulfillment'}
        />
        <div className="grid gap-4 md:grid-cols-3">
          <div className="card p-5">
            <div className="text-xs font-medium uppercase tracking-wider text-accent">
              {lang === 'zh' ? '低客单价 < $15' : 'Low AOV < $15'}
            </div>
            <div className="mt-2 text-base font-semibold text-ink-900">
              {lang === 'zh' ? 'Amazon FBA 美仓 + Prime' : 'Amazon FBA + Prime'}
            </div>
            <p className="mt-2 text-sm text-ink-600">
              {lang === 'zh'
                ? '训练零食、小包装饼干（Zuke\'s Mini、Fruitables）走 Amazon Prime，1–2 天到，单件包邮不需阈值。'
                : "Training treats and small packs (Zuke's Mini, Fruitables) ship via Amazon Prime — 1–2 day delivery, no threshold."}
            </p>
          </div>
          <div className="card p-5">
            <div className="text-xs font-medium uppercase tracking-wider text-accent">
              {lang === 'zh' ? '中客单价 $15–$80' : 'Mid AOV $15–$80'}
            </div>
            <div className="mt-2 text-base font-semibold text-ink-900">
              {lang === 'zh' ? 'Amazon FBA + Chewy $49 免运' : 'Amazon FBA + Chewy free over $49'}
            </div>
            <p className="mt-2 text-sm text-ink-600">
              {lang === 'zh'
                ? '30 磅主粮、洁齿零食大包装。Chewy Autoship 和 Amazon S&S 是留存核心杠杆。'
                : '30 lb kibble bags and bulk dental chews. Chewy Autoship and Amazon S&S are the core retention levers.'}
            </p>
          </div>
          <div className="card p-5">
            <div className="text-xs font-medium uppercase tracking-wider text-accent">
              {lang === 'zh' ? '订阅制 / 鲜食' : 'Subscription / fresh'}
            </div>
            <div className="mt-2 text-base font-semibold text-ink-900">
              {lang === 'zh' ? '冷链配送 + 月付订阅' : 'Cold-chain + monthly subscription'}
            </div>
            <p className="mt-2 text-sm text-ink-600">
              {lang === 'zh'
                ? 'The Farmer\'s Dog、Nom Nom 鲜食和 BarkBox 礼盒走冷链/月付模式，无传统批发 SKU。'
                : "The Farmer's Dog, Nom Nom fresh meals and BarkBox use cold-chain / monthly billing — no traditional wholesale SKU."}
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
