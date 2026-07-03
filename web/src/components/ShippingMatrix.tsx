import { useTranslation } from 'react-i18next';
import type { ShippingMode } from '../lib/types';
import SourceBadge from './SourceBadge';

export default function ShippingMatrix({ modes }: { modes: ShippingMode[] }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const grouped = {
    CN: modes.filter((m) => m.shipFrom === 'CN'),
    US: modes.filter((m) => m.shipFrom === 'US'),
  };

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {(['CN', 'US'] as const).map((origin) => (
        <div key={origin} className="card overflow-hidden">
          <div className="border-b border-ink-100 bg-ink-50 px-4 py-3">
            <div className="text-sm font-semibold text-ink-900">
              {origin === 'CN' ? t('logistics.fromCN') : t('logistics.fromUS')}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-ink-100">
              <thead className="bg-white">
                <tr>
                  <th className="table-th">{t('logistics.modeMethod')}</th>
                  <th className="table-th">{t('logistics.modeTransit')}</th>
                  <th className="table-th">{t('logistics.modeCost')}</th>
                  <th className="table-th">{t('logistics.modeUseCase')}</th>
                  <th className="table-th">{t('common.source')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100">
                {grouped[origin].map((m) => (
                  <tr key={m.id}>
                    <td className="table-td font-semibold text-ink-900">
                      {lang === 'zh' ? m.methodZh : m.method}
                    </td>
                    <td className="table-td">{m.transit}</td>
                    <td className="table-td font-mono text-xs">{m.cost}</td>
                    <td className="table-td">{lang === 'zh' ? m.useCaseZh : m.useCase}</td>
                    <td className="table-td">
                      <SourceBadge source={m.source} compact />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
