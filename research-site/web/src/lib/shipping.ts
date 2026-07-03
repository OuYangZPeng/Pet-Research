import type { Competitor, LeadTimeDays } from './types';

export type ShippingStatus = 'free' | 'conditional' | 'paid' | 'unknown';

export interface ShippingInfo {
  status: ShippingStatus;
  /** Threshold in USD when status === 'conditional'. */
  threshold?: number;
  /** Whether this competitor's `current` price already meets the threshold. */
  meetsThreshold?: boolean;
  /** Original note string for tooltip / debugging. */
  raw: string;
}

const FREE_RE = /\b(free|prime|包邮|免运)\b/i;
const OVER_RE = /(?:over|above|满)\s*\$?\s*(\d{1,5})|\$\s*(\d{1,5})\s*\+/i;
const PAID_RE = /\b(\$\s*\d+\s+(flat|shipping)|paid shipping|付费|运费\s*\$)\b/i;

/**
 * Classify a competitor's shipping situation from its free-form `shippingNote`
 * plus context (current price). Returns one of:
 *  - 'free':        unconditional free shipping (Prime, site-wide, etc.)
 *  - 'conditional': free above an order threshold; threshold returned
 *  - 'paid':        explicit paid-shipping signal
 *  - 'unknown':     no signal in the note — caller should label as "未确认"
 */
export function parseShipping(c: Pick<Competitor, 'shippingNote' | 'price'>): ShippingInfo {
  const raw = (c.shippingNote || '').trim();
  if (!raw || raw === '—' || raw === '-') {
    return { status: 'unknown', raw };
  }

  const overMatch = raw.match(OVER_RE);
  const free = FREE_RE.test(raw);

  if (overMatch && free) {
    const threshold = Number(overMatch[1] ?? overMatch[2]);
    return {
      status: 'conditional',
      threshold,
      meetsThreshold: c.price.current >= threshold,
      raw,
    };
  }
  if (free) return { status: 'free', raw };
  if (PAID_RE.test(raw)) return { status: 'paid', raw };

  // Promo-only notes ("Memorial Day 40% off") don't say anything about shipping
  return { status: 'unknown', raw };
}

export function shippingChipLabel(
  info: ShippingInfo,
  lang: 'zh' | 'en' = 'zh'
): { text: string; cls: string; title: string } {
  switch (info.status) {
    case 'free':
      return {
        text: lang === 'zh' ? '✅ 包邮' : '✅ Free ship',
        cls: 'bg-ok/10 text-ok ring-ok/20',
        title: info.raw,
      };
    case 'conditional': {
      const met = info.meetsThreshold;
      const zh = met
        ? `✅ 满 $${info.threshold} 包邮 (已达标)`
        : `📦 满 $${info.threshold} 包邮`;
      const en = met
        ? `✅ Free over $${info.threshold} (qualifies)`
        : `📦 Free over $${info.threshold}`;
      return {
        text: lang === 'zh' ? zh : en,
        cls: met
          ? 'bg-ok/10 text-ok ring-ok/20'
          : 'bg-accent/10 text-accent ring-accent/20',
        title: info.raw,
      };
    }
    case 'paid':
      return {
        text: lang === 'zh' ? '💰 付费运费' : '💰 Paid shipping',
        cls: 'bg-warn/10 text-warn ring-warn/20',
        title: info.raw,
      };
    case 'unknown':
    default:
      return {
        text: lang === 'zh' ? '❓ 未确认' : '❓ Unverified',
        cls: 'bg-ink-100 text-ink-500 ring-ink-200',
        title: info.raw || (lang === 'zh' ? '商家未公开运费政策' : 'No shipping note in source data'),
      };
  }
}

/**
 * Bucket a lead-time window into a speed tier:
 *  - 'overnight':  max ≤ 2 business days       (Amazon Prime small items)
 *  - 'fast':       max ≤ 5 business days       (FBA freight, fast DTC)
 *  - 'standard':   max ≤ 10 business days      (Home Depot, slower DTC)
 *  - 'slow':       max > 10 business days      (LTL freight, drop-ship)
 */
export type LeadTimeTier = 'overnight' | 'fast' | 'standard' | 'slow';

export function leadTimeTier(lt: LeadTimeDays): LeadTimeTier {
  if (lt.max <= 2) return 'overnight';
  if (lt.max <= 5) return 'fast';
  if (lt.max <= 10) return 'standard';
  return 'slow';
}

export function leadTimeChipLabel(
  lt: LeadTimeDays | undefined,
  note: string | undefined,
  lang: 'zh' | 'en' = 'zh'
): { text: string; cls: string; title: string } | null {
  if (!lt) return null;
  const tier = leadTimeTier(lt);
  const range = lt.min === lt.max ? `${lt.min}` : `${lt.min}–${lt.max}`;
  const days = lang === 'zh' ? '天' : 'd';
  const icon =
    tier === 'overnight' ? '⚡'
    : tier === 'fast' ? '🚀'
    : tier === 'standard' ? '📦'
    : '🚛';
  const tierLabel = lang === 'zh'
    ? { overnight: '极速', fast: '快', standard: '标准', slow: '慢' }[tier]
    : { overnight: 'Express', fast: 'Fast', standard: 'Standard', slow: 'Freight' }[tier];
  const cls =
    tier === 'overnight' ? 'bg-ok/10 text-ok ring-ok/20'
    : tier === 'fast' ? 'bg-accent/10 text-accent ring-accent/20'
    : tier === 'standard' ? 'bg-warn/10 text-warn ring-warn/20'
    : 'bg-ink-200 text-ink-700 ring-ink-300';
  return {
    text: `${icon} ${range} ${days} · ${tierLabel}`,
    cls,
    title: note || '',
  };
}
