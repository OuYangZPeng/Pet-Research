import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';
import { useTranslation } from 'react-i18next';
import type { SeasonalityPoint } from '../lib/types';

export default function SeasonalityChart({ points }: { points: SeasonalityPoint[] }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const data = points.map((p) => ({
    month: lang === 'zh' ? p.monthZh : p.month,
    demand: p.demandIndex,
    discount: p.discountPctTypical,
    band: p.band,
  }));

  return (
    <div className="card p-5">
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid stroke="#eef1f5" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#5e6776' }} />
            <YAxis
              yAxisId="left"
              tick={{ fontSize: 12, fill: '#8a93a6' }}
              domain={[0, 100]}
              label={{
                value: t('seasonality.demandIndex'),
                angle: -90,
                position: 'insideLeft',
                style: { fill: '#8a93a6', fontSize: 11 },
              }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              tick={{ fontSize: 12, fill: '#8a93a6' }}
              tickFormatter={(v) => `${v}%`}
              domain={[0, 30]}
              label={{
                value: t('seasonality.discountDepth'),
                angle: 90,
                position: 'insideRight',
                style: { fill: '#8a93a6', fontSize: 11 },
              }}
            />
            <Tooltip
              contentStyle={{ borderRadius: 12, borderColor: '#dde2ea', fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar
              yAxisId="left"
              dataKey="demand"
              name={t('seasonality.demandIndex')}
              fill="#0ea5a3"
              radius={[6, 6, 0, 0]}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="discount"
              name={t('seasonality.discountDepth')}
              stroke="#f59e0b"
              strokeWidth={2.5}
              dot={{ r: 3 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
