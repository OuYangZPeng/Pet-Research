import { useEffect, useState } from 'react';
import type {
  CategoryDataset,
  CategorySlug,
  CategoryVideos,
  InfluencerEntry,
  SeasonalityPoint,
  ShippingMode,
  FreeShippingBenchmark,
  MetaInfo,
  ReviewInsight,
  PainPointData,
  SkuVideoBundle,
} from './types';

const dataUrl = (name: string) => `${import.meta.env.BASE_URL}data/${name}`;

async function getJson<T>(name: string): Promise<T> {
  const res = await fetch(dataUrl(name), { cache: 'no-cache' });
  if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`);
  return (await res.json()) as T;
}

export function useJson<T>(name: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getJson<T>(name)
      .then((d) => active && setData(d))
      .catch((e) => active && setError(String(e)));
    return () => {
      active = false;
    };
  }, [name]);

  return { data, error };
}

export const useDogFood = () => useJson<CategoryDataset>('dog-food.json');
export const useDogTreats = () => useJson<CategoryDataset>('dog-treats.json');
export const useInfluencers = () => useJson<InfluencerEntry[]>('influencers.json');
export const useSeasonality = () =>
  useJson<{
    points: SeasonalityPoint[];
    insight: string;
    insightZh: string;
  }>('seasonality.json');
export const useShipping = () =>
  useJson<{
    modes: ShippingMode[];
    thresholds: FreeShippingBenchmark[];
  }>('shipping.json');
export const useMeta = () => useJson<MetaInfo>('meta.json');
export const usePainPoints = () => useJson<PainPointData>('painpoints.json');

export const useCategoryVideos = (category: CategorySlug) =>
  useJson<CategoryVideos>(`videos/${category}.json`);

export function useSkuVideos(
  category: CategorySlug | null,
  sku: string | null
): { data: SkuVideoBundle | null; state: 'idle' | 'loading' | 'missing' | 'error' | 'ok' } {
  const { data: catData } = useCategoryVideos((category ?? 'dog-food') as CategorySlug);
  if (!category || !sku) return { data: null, state: 'idle' };
  if (!catData) return { data: null, state: 'loading' };
  const match = catData.items.find((i) => i.sku === sku);
  if (!match) return { data: null, state: 'missing' };
  return { data: match, state: 'ok' };
}

export function useReviewInsight(sku: string | null) {
  const [data, setData] = useState<ReviewInsight | null>(null);
  const [state, setState] = useState<'idle' | 'loading' | 'missing' | 'error' | 'ok'>('idle');

  useEffect(() => {
    if (!sku) {
      setState('idle');
      setData(null);
      return;
    }
    let active = true;
    setState('loading');
    fetch(`${import.meta.env.BASE_URL}data/review_insights/${sku}.json`, { cache: 'no-cache' })
      .then((r) => {
        if (!active) return;
        if (r.status === 404) {
          setState('missing');
          setData(null);
          return;
        }
        if (!r.ok) throw new Error(String(r.status));
        return r.json().then((j: ReviewInsight) => {
          if (!active) return;
          setData(j);
          setState('ok');
        });
      })
      .catch(() => {
        if (active) setState('error');
      });
    return () => {
      active = false;
    };
  }, [sku]);

  return { data, state };
}
