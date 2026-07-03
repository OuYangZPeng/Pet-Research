import { useTranslation } from 'react-i18next';
import { fmtDate } from '../lib/format';
import type { SourceRef } from '../lib/types';

export default function SourceBadge({
  source,
  compact = false,
}: {
  source: SourceRef;
  compact?: boolean;
}) {
  const { t, i18n } = useTranslation();
  const lang = (i18n.language as 'zh' | 'en') || 'zh';

  return (
    <a href={source.url} target="_blank" rel="noreferrer noopener" className="source-link">
      <span aria-hidden>↗</span>
      <span>{compact ? t('common.source') : source.label}</span>
      {source.fetchedAt ? <span className="text-ink-300">· {fmtDate(source.fetchedAt, lang)}</span> : null}
    </a>
  );
}
