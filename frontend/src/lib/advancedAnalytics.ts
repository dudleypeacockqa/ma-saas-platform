import { trackEvent, pushDataLayerEvent, setUserProperties, trackPageView } from '@/lib/analytics';

export type BillingInterval = 'monthly' | 'yearly';

export type FunnelStage =
  | 'landing_view'
  | 'pricing_view'
  | 'cta_click'
  | 'checkout_start'
  | 'trial_start'
  | 'payment_submitted'
  | 'subscription_active';

export interface EcommerceItem {
  item_id: string;
  item_name: string;
  price: number;
  currency: string;
  tier: string;
  billing_interval: BillingInterval;
  quantity?: number;
  discount?: number;
}

export interface EcommerceEventPayload {
  items: EcommerceItem[];
  value?: number;
  currency?: string;
  coupon?: string;
  trial?: boolean;
  mrr?: number;
  ltv?: number;
  churn_probability?: number;
  customer_lifespan_months?: number;
  experiment?: string;
  variant?: string;
  attribution?: AttributionPayload;
}

export interface AttributionPayload {
  source: string;
  medium: string;
  campaign?: string;
  term?: string;
  content?: string;
  landingPage?: string;
  referrer?: string;
  timestamp?: number;
}

const ATTRIBUTION_STORAGE_KEY = 'ma_attribution_v1';

const persistAttribution = (attribution: AttributionPayload) => {
  try {
    localStorage.setItem(ATTRIBUTION_STORAGE_KEY, JSON.stringify(attribution));
  } catch (error) {
    console.warn('Unable to persist attribution data', error);
  }
};

export const loadAttribution = (): AttributionPayload | null => {
  try {
    const stored = localStorage.getItem(ATTRIBUTION_STORAGE_KEY);
    if (!stored) return null;
    return JSON.parse(stored) as AttributionPayload;
  } catch (error) {
    console.warn('Unable to load attribution data', error);
    return null;
  }
};

export const recordAttribution = (payload: AttributionPayload) => {
  const enriched: AttributionPayload = {
    ...payload,
    timestamp: payload.timestamp ?? Date.now(),
    landingPage: payload.landingPage ?? window.location.pathname + window.location.search,
    referrer: payload.referrer ?? document.referrer,
  };

  persistAttribution(enriched);
  trackEvent('attribution_recorded', enriched);
  pushDataLayerEvent('attribution_recorded', enriched);
};

const mapStageToEvent: Record<FunnelStage, string> = {
  landing_view: 'view_home',
  pricing_view: 'view_pricing',
  cta_click: 'select_pricing_cta',
  checkout_start: 'begin_checkout',
  trial_start: 'start_trial',
  payment_submitted: 'add_payment_info',
  subscription_active: 'subscription_active',
};

export const trackFunnelStage = (stage: FunnelStage, details: Record<string, unknown> = {}) => {
  const eventName = mapStageToEvent[stage];
  const payload = {
    stage,
    event: eventName,
    ...details,
  };

  trackEvent(eventName, payload);
  pushDataLayerEvent(eventName, payload);
};

export const trackEcommerceEvent = (eventName: string, payload: EcommerceEventPayload) => {
  const attribution = payload.attribution ?? loadAttribution();
  const eventPayload = {
    ...payload,
    attribution,
  };

  trackEvent(eventName, eventPayload);
  pushDataLayerEvent(eventName, eventPayload);
};

export interface TrialConversionPayload extends EcommerceEventPayload {
  trial_days?: number;
  activation_time_minutes?: number;
}

export const recordTrialConversion = (payload: TrialConversionPayload) => {
  trackFunnelStage('trial_start', {
    trial_days: payload.trial_days,
    activation_time_minutes: payload.activation_time_minutes,
    tier: payload.items[0]?.tier,
  });

  trackEcommerceEvent('start_trial', payload);
};

export interface SubscriptionActivationPayload extends EcommerceEventPayload {
  mrr: number;
  arr?: number;
  ltv?: number;
  churn_probability?: number;
  payback_period_months?: number;
}

export const recordSubscriptionActivation = (payload: SubscriptionActivationPayload) => {
  const primaryItem = payload.items[0];
  trackFunnelStage('subscription_active', {
    tier: primaryItem?.tier,
    billing_interval: primaryItem?.billing_interval,
    mrr: payload.mrr,
    arr: payload.arr,
    ltv: payload.ltv,
  });

  trackEcommerceEvent('purchase', payload);

  setUserProperties({
    subscription_tier: primaryItem?.tier ?? null,
    billing_interval: primaryItem?.billing_interval ?? null,
    customer_mrr: payload.mrr,
    customer_ltv: payload.ltv ?? null,
  });
};

export interface RevenueMetricsPayload {
  mrr: number;
  arr?: number;
  ltv?: number;
  cac?: number;
  churn_rate?: number;
  arpa?: number;
  customer_count?: number;
  tier?: string;
  segment?: string;
}

export const trackRevenueMetrics = (payload: RevenueMetricsPayload) => {
  trackEvent('revenue_metrics', payload);
  pushDataLayerEvent('revenue_metrics', payload);
};

export interface FeatureAdoptionPayload {
  feature_key: string;
  usage_count?: number;
  time_to_value_minutes?: number;
  tier?: string;
  segment?: string;
}

export const recordFeatureAdoption = (payload: FeatureAdoptionPayload) => {
  trackEvent('feature_adoption', payload);
  pushDataLayerEvent('feature_adoption', payload);
};

export const recordChurnSignal = (payload: { reason: string; risk_score: number; tier?: string }) => {
  trackEvent('churn_signal_detected', payload);
  pushDataLayerEvent('churn_signal_detected', payload);
};

export const hydrateAnalyticsFromUrl = () => {
  const params = new URLSearchParams(window.location.search);
  const utmSource = params.get('utm_source');
  const utmMedium = params.get('utm_medium');
  const utmCampaign = params.get('utm_campaign');
  const utmTerm = params.get('utm_term');
  const utmContent = params.get('utm_content');

  if (!utmSource && !utmMedium && !utmCampaign) return;

  recordAttribution({
    source: utmSource ?? 'direct',
    medium: utmMedium ?? 'none',
    campaign: utmCampaign ?? undefined,
    term: utmTerm ?? undefined,
    content: utmContent ?? undefined,
  });
};

export const trackRevenuePageView = () => {
  trackPageView(window.location.pathname + window.location.search, {
    page_category: 'revenue_optimization',
  });
};
