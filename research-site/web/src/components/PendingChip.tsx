import { useTranslation } from 'react-i18next';

export default function PendingChip({ field }: { field?: string }) {
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  return (
    <span
      title={
        lang === 'zh'
          ? '该字段不在初始 seed 数据里，等抓取脚本跑过 Amazon / YouTube API 后会自动填上真实值。'
          : 'Not in the initial seed. Will populate after the scraper runs against Amazon / YouTube API.'
      }
      className="inline-flex items-center gap-1 rounded-full bg-warn/10 px-2 py-0.5 text-[10px] font-semibold text-warn"
    >
      <span aria-hidden>⌛</span>
      {lang === 'zh' ? '待抓取' : 'pending scrape'}
      {field ? <span className="font-mono text-warn/70">{field}</span> : null}
    </span>
  );
}
