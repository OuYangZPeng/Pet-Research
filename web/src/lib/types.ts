export interface SourceRef {
  label: string;
  url: string;
  fetchedAt?: string;
}

export interface PriceInfo {
  current: number;
  original?: number;
  currency: 'USD';
  discountPct?: number;
}

export interface LeadTimeDays {
  min: number;
  max: number;
}

export type CategorySlug = 'dog-food' | 'dog-treats';

export interface SupplierContact {
  company: string;
  companyZh?: string;
  phone?: string;
  email?: string;
  website?: string;
  wholesaleEmail?: string;
  address?: string;
  notes?: string;
  notesZh?: string;
}

export interface Competitor {
  id: string;
  brand: string;
  product: string;
  productZh?: string;
  platform: 'Amazon' | 'Wayfair' | 'Home Depot' | 'DTC' | 'Lowe\'s' | 'Chewy';
  storeUrl: string;
  bsrRank?: number;
  asin?: string;
  sku?: string;
  price: PriceInfo;
  rating?: number;
  reviews?: number;
  variant?: string;
  shippingNote?: string;
  shipFrom?: 'US' | 'CN' | 'Both';
  /** Estimated business-day delivery window once the order is placed. */
  leadTimeDays?: LeadTimeDays;
  /** Short label for the speed tier ("Prime", "FBA freight", "DTC standard", etc.) */
  leadTimeNote?: string;
  /** Source for the lead-time claim (link to the brand's shipping policy). */
  leadTimeSource?: SourceRef;
  /** Manufacturer / wholesaler contact for B2B sourcing. */
  supplier?: SupplierContact;
  bundle?: boolean;
  pendingFields?: string[];
  source: SourceRef;
}

export interface InfluencerEntry {
  id: string;
  platform: 'YouTube' | 'TikTok' | 'Instagram' | 'Reddit' | 'Facebook';
  handle: string;
  displayName: string;
  url: string;
  audience: number;
  audienceUnit: 'subscribers' | 'followers' | 'members';
  totalViews?: number;
  categoryFit: number;
  /** When set, only shown on matching category pages. */
  categories?: CategorySlug[];
  notes: string;
  notesZh?: string;
  topPieceTitle?: string;
  topPieceUrl?: string;
  source: SourceRef;
}

export interface SeasonalityPoint {
  month: string;
  monthZh: string;
  demandIndex: number;
  discountPctTypical: number;
  band: 'peak' | 'shoulder' | 'off';
}

export interface ShippingMode {
  id: string;
  method: string;
  methodZh: string;
  transit: string;
  cost: string;
  useCase: string;
  useCaseZh: string;
  shipFrom: 'CN' | 'US';
  source: SourceRef;
}

export interface FreeShippingBenchmark {
  brand: string;
  threshold: number;
  note: string;
  noteZh?: string;
  source: SourceRef;
}

export interface AovBucket {
  platform: string;
  median: number;
  p25: number;
  p75: number;
  min: number;
  max: number;
  sample: number;
}

export interface CategoryAov {
  category: CategorySlug;
  categoryLabel: string;
  categoryLabelZh: string;
  buckets: AovBucket[];
  insight: string;
  insightZh: string;
}

export interface InstallProfile {
  category: CategorySlug;
  scenario: string;
  scenarioZh: string;
  diyTime: string;
  proTime: string;
  laborCost: string;
  difficulty: 'easy' | 'moderate' | 'hard' | 'pro-only';
  needsElectrician: boolean;
  needsLicensedPlumber: boolean;
  notes: string;
  notesZh: string;
  videoUrl?: string;
  source: SourceRef;
}

export interface BundleObservation {
  brand: string;
  product: string;
  productZh?: string;
  type: 'single' | 'bundle' | 'trade-program';
  detail: string;
  detailZh: string;
  url: string;
  source: SourceRef;
}

export interface MetaInfo {
  generatedAt: string;
  scriptVersion: string;
  sources: SourceRef[];
}

export interface CategoryDataset {
  category: CategorySlug;
  competitors: Competitor[];
  aov: CategoryAov;
  bundles: BundleObservation[];
  installs: InstallProfile[];
}

export type ReviewChannel =
  | 'amazon'
  | 'chewy'
  | 'dtc'
  | 'trustpilot'
  | 'reddit';

export interface InsightTheme {
  theme: string;
  themeZh?: string;
  count: number;
  quote: string;
  quoteRating?: number;
  quoteVerified?: boolean;
  quoteUrl?: string;
  channels: ReviewChannel[];
}

export interface ReviewInsight {
  sku: string;
  brand: string;
  product: string;
  productZh?: string;
  category: CategorySlug;
  asin?: string;
  totalReviews: number;
  averageRating?: number;
  pros: InsightTheme[];
  cons: InsightTheme[];
  channelBreakdown: Record<string, number>;
  generator: 'cursor' | 'gemini' | 'openai' | 'anthropic' | 'manual';
  lastUpdated: string;
  sourcesUsed: SourceRef[];
}

export interface PainPointBucket {
  id: string;
  label: string;
  labelZh: string;
  icon: string;
  totalCount: number;
  skuCount: number;
  skuBreakdown: { sku: string; count: number }[];
  sampleQuote: string | null;
  quoteSku: string | null;
  quoteUrl: string | null;
  quoteRating: number | null;
}

export interface PainPointCategory {
  category: CategorySlug;
  label: string;
  labelZh: string;
  buckets: PainPointBucket[];
  skuList: { sku: string; brand: string; product: string; productZh?: string }[];
  matrix: Record<string, Record<string, number>>;
}

export type PainPointData = Record<string, PainPointCategory>;

export type VideoIntent = 'review' | 'install' | 'unboxing' | 'compare' | 'general';
export type RecencyTier = '1y' | '2y' | '3y' | 'older';

export interface VideoItem {
  videoId: string;
  title: string;
  channel: string;
  channelId?: string;
  channelSubs?: number;
  views?: number;
  likes?: number;
  comments?: number;
  publishedAt?: string;
  duration?: string;
  durationSec?: number;
  thumbnail?: string;
  url: string;
  query: string;
  intent: VideoIntent;
  publishedWithin?: RecencyTier;
  score?: number;
}

export interface SkuVideoBundle {
  sku: string;
  brand: string;
  product: string;
  productZh?: string;
  category: CategorySlug;
  videos: VideoItem[];
  lastUpdated: string;
}

export interface CategoryVideos {
  category: CategorySlug;
  generatedAt: string;
  items: SkuVideoBundle[];
}
