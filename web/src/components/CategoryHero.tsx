import type { ReactNode } from 'react';

export default function CategoryHero({
  eyebrow,
  title,
  desc,
  chips,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  desc?: ReactNode;
  chips?: ReactNode;
}) {
  return (
    <div className="mb-8 rounded-3xl bg-gradient-to-br from-accent/15 via-white to-ink-50 p-6 ring-1 ring-ink-100 lg:p-8">
      {eyebrow && (
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent">
          {eyebrow}
        </div>
      )}
      <h1 className="text-3xl font-bold tracking-tight text-ink-900 lg:text-4xl">{title}</h1>
      {desc && <p className="mt-3 max-w-2xl text-sm text-ink-600 lg:text-base">{desc}</p>}
      {chips && <div className="mt-4 flex flex-wrap gap-2">{chips}</div>}
    </div>
  );
}
