import { useTranslation } from 'react-i18next';
import { fmtUSDPrecise } from '../lib/format';
import type { PriceInfo } from '../lib/types';

export default function PriceCard({
  price,
  compact = false,
}: {
  price: PriceInfo;
  compact?: boolean;
}) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const hasDiscount = price.original && price.original > price.current;
  const pct = price.discountPct
    ? price.discountPct
    : hasDiscount
      ? Math.round((1 - price.current / (price.original as number)) * 100)
      : 0;
  const savings = hasDiscount ? (price.original as number) - price.current : 0;

  return (
    <div className={`flex ${compact ? 'flex-col items-start gap-0.5' : 'flex-col gap-0.5'}`}>
      <div className="flex items-baseline gap-2">
        <span className="text-base font-bold text-ink-900">{fmtUSDPrecise(price.current)}</span>
        {hasDiscount && (
          <span className="text-xs text-ink-400 line-through">
            {fmtUSDPrecise(price.original as number)}
          </span>
        )}
      </div>
      {hasDiscount && (
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          {pct > 0 && (
            <span className="rounded-full bg-danger/10 px-1.5 py-0.5 font-semibold text-danger ring-1 ring-danger/20">
              -{pct}%
            </span>
          )}
          <span className="font-semibold text-danger">
            {lang === 'zh' ? `省 ${fmtUSDPrecise(savings)}` : `${t('common.savings')} ${fmtUSDPrecise(savings)}`}
          </span>
        </div>
      )}
      {!hasDiscount && (
        <span className="text-[10px] text-ink-400">
          {lang === 'zh' ? '原价' : 'Regular price'}
        </span>
      )}
    </div>
  );
}
