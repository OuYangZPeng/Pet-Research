import type { ReactNode } from 'react';

export default function Kpi({
  label,
  value,
  hint,
  accent = false,
}: {
  label: ReactNode;
  value: ReactNode;
  hint?: ReactNode;
  accent?: boolean;
}) {
  return (
    <div className="card p-5">
      <div className="text-xs font-medium uppercase tracking-wider text-ink-400">{label}</div>
      <div
        className={`mt-2 text-2xl font-bold tracking-tight ${
          accent ? 'text-accent' : 'text-ink-900'
        }`}
      >
        {value}
      </div>
      {hint && <div className="mt-1 text-xs text-ink-500">{hint}</div>}
    </div>
  );
}
