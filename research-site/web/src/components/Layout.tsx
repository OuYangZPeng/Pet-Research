import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useMeta } from '../lib/loadData';
import { fmtDate } from '../lib/format';
import type { ReactNode } from 'react';

const navItems = [
  { to: '/', key: 'dashboard', end: true },
  { to: '/dog-food', key: 'dogFood' },
  { to: '/dog-treats', key: 'dogTreats' },
  { to: '/insights/painpoints', key: 'painpoints' },
  { to: '/insights/seasonality', key: 'seasonality' },
  { to: '/insights/influencers', key: 'influencers' },
  { to: '/insights/logistics', key: 'logistics' },
  { to: '/methodology', key: 'methodology' },
];

export default function Layout({ children }: { children: ReactNode }) {
  const { t, i18n } = useTranslation();
  const { data: meta } = useMeta();
  const lang = (i18n.language as 'zh' | 'en') || 'zh';

  const toggleLang = () => {
    const next = lang === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
    if (typeof window !== 'undefined') window.localStorage.setItem('lang', next);
    document.documentElement.lang = next === 'zh' ? 'zh-CN' : 'en';
  };

  return (
    <div className="min-h-full bg-ink-50">
      <header className="sticky top-0 z-30 border-b border-ink-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-white shadow-card">
              <span className="text-lg font-bold">🐕</span>
            </div>
            <div>
              <div className="text-sm font-semibold leading-tight text-ink-800">
                {t('brand.title')}
              </div>
              <div className="text-xs leading-tight text-ink-400">
                {t('brand.subtitle')}
              </div>
            </div>
          </div>
          <nav className="hidden flex-wrap items-center gap-1 lg:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.key}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'nav-link-active' : ''}`
                }
              >
                {t(`nav.${item.key}`)}
              </NavLink>
            ))}
          </nav>
          <button
            onClick={toggleLang}
            className="rounded-lg border border-ink-200 px-3 py-1.5 text-xs font-semibold text-ink-600 transition hover:border-accent hover:text-accent"
          >
            {t('lang.switch')}
          </button>
        </div>
        <nav className="flex gap-1 overflow-x-auto border-t border-ink-100 bg-white px-4 py-2 lg:hidden">
          {navItems.map((item) => (
            <NavLink
              key={item.key}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `nav-link whitespace-nowrap ${isActive ? 'nav-link-active' : ''}`
              }
            >
              {t(`nav.${item.key}`)}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 lg:px-8 lg:py-10">{children}</main>

      <footer className="mt-12 border-t border-ink-100 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-2 px-4 py-6 text-xs text-ink-400 lg:flex-row lg:items-center lg:px-8">
          <div>
            {t('brand.title')} · {t('brand.subtitle')}
          </div>
          <div>
            {meta?.generatedAt
              ? `${t('common.lastFetched')}: ${fmtDate(meta.generatedAt, lang)}`
              : ''}
          </div>
        </div>
      </footer>
    </div>
  );
}
