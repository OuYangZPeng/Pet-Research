import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSkuVideos } from '../lib/loadData';
import { fmtDate, fmtNumber } from '../lib/format';
import type { RecencyTier, VideoIntent } from '../lib/types';

import type { CategorySlug } from '../lib/types';

type Props = {
  category: CategorySlug | null;
  sku: string;
};

const INTENT_LABELS: Record<VideoIntent, { en: string; zh: string; emoji: string }> = {
  review: { en: 'Review', zh: '评测', emoji: '⭐' },
  install: { en: 'Setup', zh: '开封/喂食', emoji: '🦴' },
  unboxing: { en: 'Unboxing', zh: '开箱', emoji: '📦' },
  compare: { en: 'Compare', zh: '对比', emoji: '⚖️' },
  general: { en: 'General', zh: '其他', emoji: '🎬' },
};

const RECENCY_LABELS: Record<RecencyTier, { en: string; zh: string; cls: string }> = {
  '1y': { en: '< 1 yr', zh: '近 1 年', cls: 'bg-ok/10 text-ok ring-ok/20' },
  '2y': { en: '< 2 yr', zh: '近 2 年', cls: 'bg-accent/10 text-accent ring-accent/20' },
  '3y': { en: '< 3 yr', zh: '近 3 年', cls: 'bg-warn/10 text-warn ring-warn/20' },
  older: { en: '> 3 yr', zh: '3 年以上', cls: 'bg-ink-100 text-ink-500 ring-ink-200' },
};

function fmtDurationSec(sec?: number): string {
  if (!sec) return '';
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (sec >= 3600) {
    const h = Math.floor(sec / 3600);
    return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return `${m}:${String(s).padStart(2, '0')}`;
}

export default function VideoGrid({ category, sku }: Props) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';
  const [intentFilter, setIntentFilter] = useState<VideoIntent | 'all'>('all');
  const { data, state } = useSkuVideos(category, sku);

  const filtered = useMemo(() => {
    if (!data) return [];
    if (intentFilter === 'all') return data.videos;
    return data.videos.filter((v) => v.intent === intentFilter);
  }, [data, intentFilter]);

  if (state === 'idle' || state === 'loading') {
    return (
      <div className="text-xs text-ink-400">
        {lang === 'zh' ? '加载中…' : 'Loading creator videos…'}
      </div>
    );
  }

  if (state === 'missing' || !data) {
    return (
      <div className="rounded-lg border border-dashed border-ink-200 bg-white p-3 text-xs text-ink-500">
        {lang === 'zh' ? (
          <>
            尚未抓取该 SKU 的 YouTube 视频。运行{' '}
            <code className="rounded bg-ink-900 px-1.5 py-0.5 font-mono text-[10px] text-ink-100">
              python scraper/refresh_videos.py --skus {sku}
            </code>{' '}
            后此处会显示相关达人视频。
          </>
        ) : (
          <>
            No creator videos cached for this SKU yet. Run{' '}
            <code className="rounded bg-ink-900 px-1.5 py-0.5 font-mono text-[10px] text-ink-100">
              python scraper/refresh_videos.py --skus {sku}
            </code>{' '}
            to discover relevant creators.
          </>
        )}
      </div>
    );
  }

  if (state === 'error') {
    return (
      <div className="text-xs text-rose-600">
        {lang === 'zh' ? '加载视频失败' : 'Failed to load videos'}
      </div>
    );
  }

  if (!data.videos.length) {
    return (
      <div className="text-xs text-ink-500">
        {lang === 'zh' ? '未找到相关 YouTube 视频。' : 'No relevant YouTube videos found.'}
      </div>
    );
  }

  const intents = Array.from(new Set(data.videos.map((v) => v.intent))) as VideoIntent[];
  const tierCounts = data.videos.reduce<Record<string, number>>((acc, v) => {
    const t = v.publishedWithin ?? 'older';
    acc[t] = (acc[t] || 0) + 1;
    return acc;
  }, {});
  const tierBadgesOrder: RecencyTier[] = ['1y', '2y', '3y', 'older'];

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-ink-700">
          {lang === 'zh' ? 'YouTube 相关视频' : 'Related YouTube videos'}
        </span>
        <span className="text-[11px] text-ink-400">
          {data.videos.length}
          {lang === 'zh' ? ' 个，按新鲜度+达人价值排序' : ' videos · ranked by freshness + creator value'}
        </span>
        <div className="flex flex-wrap gap-1">
          {tierBadgesOrder
            .filter((t) => (tierCounts[t] ?? 0) > 0)
            .map((t) => (
              <span
                key={t}
                className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold ring-1 ${RECENCY_LABELS[t].cls}`}
                title={lang === 'zh' ? '该视频是发布日期的级联匹配窗口' : 'Cascade tier this video matched'}
              >
                {tierCounts[t]} × {lang === 'zh' ? RECENCY_LABELS[t].zh : RECENCY_LABELS[t].en}
              </span>
            ))}
        </div>
        <div className="ml-auto flex flex-wrap gap-1">
          <button
            onClick={() => setIntentFilter('all')}
            className={`rounded-full px-2 py-0.5 text-[11px] font-semibold transition ${
              intentFilter === 'all'
                ? 'bg-accent text-white'
                : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
            }`}
          >
            {lang === 'zh' ? '全部' : 'All'}
          </button>
          {intents.map((i) => (
            <button
              key={i}
              onClick={() => setIntentFilter(i)}
              className={`rounded-full px-2 py-0.5 text-[11px] font-semibold transition ${
                intentFilter === i
                  ? 'bg-accent text-white'
                  : 'bg-white text-ink-600 ring-1 ring-ink-200 hover:bg-ink-100'
              }`}
            >
              {INTENT_LABELS[i].emoji} {lang === 'zh' ? INTENT_LABELS[i].zh : INTENT_LABELS[i].en}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((v) => (
          <a
            key={v.videoId}
            href={v.url}
            target="_blank"
            rel="noreferrer noopener"
            onClick={(e) => e.stopPropagation()}
            className="group flex flex-col overflow-hidden rounded-xl border border-ink-200 bg-white transition hover:border-accent hover:shadow-md"
          >
            <div className="relative aspect-video w-full overflow-hidden bg-ink-100">
              {v.thumbnail ? (
                <img
                  src={v.thumbnail}
                  alt={v.title}
                  loading="lazy"
                  className="h-full w-full object-cover transition group-hover:scale-105"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-ink-300">▶</div>
              )}
              <div className="absolute right-1.5 top-1.5 flex flex-col items-end gap-1">
                <span className="rounded bg-ink-900/80 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                  {INTENT_LABELS[v.intent].emoji} {lang === 'zh' ? INTENT_LABELS[v.intent].zh : INTENT_LABELS[v.intent].en}
                </span>
                {v.publishedWithin && (
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ring-1 ${
                      RECENCY_LABELS[v.publishedWithin].cls
                    }`}
                    title={lang === 'zh' ? '发布时间窗口' : 'Publish recency tier'}
                  >
                    {lang === 'zh' ? RECENCY_LABELS[v.publishedWithin].zh : RECENCY_LABELS[v.publishedWithin].en}
                  </span>
                )}
              </div>
              {typeof v.durationSec === 'number' && v.durationSec > 0 && (
                <div className="absolute right-1.5 bottom-1.5 rounded bg-ink-900/85 px-1.5 py-0.5 font-mono text-[10px] text-white">
                  {fmtDurationSec(v.durationSec)}
                </div>
              )}
            </div>
            <div className="flex flex-1 flex-col gap-1 p-3">
              <h4 className="line-clamp-2 text-sm font-semibold text-ink-900 group-hover:text-accent">
                {v.title}
              </h4>
              <div className="text-xs text-ink-600">{v.channel}</div>
              <div className="mt-auto flex flex-wrap items-center gap-x-3 gap-y-1 pt-1 text-[11px] text-ink-500">
                {typeof v.channelSubs === 'number' && (
                  <span title={lang === 'zh' ? '频道订阅数' : 'channel subscribers'}>
                    👥 {fmtNumber(v.channelSubs)}
                  </span>
                )}
                {typeof v.views === 'number' && (
                  <span title={lang === 'zh' ? '视频播放量' : 'video views'}>
                    ▶ {fmtNumber(v.views)}
                  </span>
                )}
                {typeof v.likes === 'number' && v.likes > 0 && (
                  <span title={lang === 'zh' ? '点赞数' : 'likes'}>
                    👍 {fmtNumber(v.likes)}
                  </span>
                )}
                {v.publishedAt && (
                  <span className="text-ink-400">{fmtDate(v.publishedAt, lang)}</span>
                )}
                {typeof v.score === 'number' && v.score > 0 && (
                  <span
                    className="ml-auto rounded bg-accent/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-accent"
                    title={
                      lang === 'zh'
                        ? '达人价值分 = log(订阅)×log(播放)'
                        : 'creator value = log(subs)×log(views)'
                    }
                  >
                    {v.score.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
          </a>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="mt-2 text-xs text-ink-400">
          {lang === 'zh' ? '当前过滤无匹配视频。' : 'No videos match the current filter.'}
        </div>
      )}

      <div className="mt-2 text-[11px] text-ink-400">
        {lang === 'zh' ? '点击卡片直接跳转 YouTube。最后更新：' : 'Click any card to open YouTube. Last updated: '}
        {fmtDate(data.lastUpdated, lang)}
      </div>
    </div>
  );
}
