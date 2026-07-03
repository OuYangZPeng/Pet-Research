import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';
import { useTranslation } from 'react-i18next';
import type { CategoryAov } from '../lib/types';

export default function AovChart({ aov }: { aov: CategoryAov }) {
  const { t } = useTranslation();
  const data = aov.buckets.map((b) => ({
    platform: b.platform,
    median: b.median,
    p25: b.p25,
    p75: b.p75,
  }));

  return (
    <div className="card p-5">
      <div className="mb-2 flex items-baseline justify-between">
        <div>
          <h3 className="text-base font-semibold text-ink-900">
            {t('common.median')} / P25 / P75
          </h3>
        </div>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="#eef1f5" vertical={false} />
            <XAxis dataKey="platform" tick={{ fontSize: 12, fill: '#5e6776' }} />
            <YAxis tick={{ fontSize: 12, fill: '#8a93a6' }} tickFormatter={(v) => `$${v}`} />
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
  );
}
