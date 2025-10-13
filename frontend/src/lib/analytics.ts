import type { UserResource } from '@clerk/types';

type AnalyticsConfig = {
  gaMeasurementId?: string;
  segmentWriteKey?: string;
};

export type AnalyticsUserProperties = Record<string, string | number | boolean | null | undefined>;

export type AnalyticsEventPayload = Record<string, unknown>;

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
    analytics?: {
      load?: (key: string) => void;
      track?: (event: string, properties?: Record<string, unknown>) => void;
      identify?: (id?: string, traits?: Record<string, unknown>) => void;
      page?: (category?: string | null, name?: string, properties?: Record<string, unknown>) => void;
    };
  }
}

let initialized = false;
let lastIdentifiedUserId: string | null = null;

const getEnv = (): AnalyticsConfig => {
  const env = (typeof import.meta !== 'undefined' && (import.meta as any).env) || process.env;
  return {
    gaMeasurementId: env.VITE_GA_MEASUREMENT_ID as string | undefined,
    segmentWriteKey: env.VITE_SEGMENT_WRITE_KEY as string | undefined,
  };
};

const loadScript = (src: string, attributes: Record<string, string> = {}): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = src;
    Object.entries(attributes).forEach(([key, value]) => {
      script.setAttribute(key, value);
    });
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load script ${src}`));
    document.head.appendChild(script);
  });
};

const initGA = async (measurementId: string) => {
  if (window.gtag) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer?.push(arguments);
  };

  await loadScript(`https://www.googletagmanager.com/gtag/js?id=${measurementId}`);
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
};

const initSegment = async (writeKey: string) => {
  if (window.analytics && typeof window.analytics.load === 'function') return;

  await loadScript('https://cdn.segment.com/analytics.js/v1/' + writeKey + '/analytics.min.js');
  window.analytics?.load?.(writeKey);
};

export const initAnalytics = async () => {
  if (initialized || typeof window === 'undefined') return;

  const { gaMeasurementId, segmentWriteKey } = getEnv();

  const loaders: Promise<void>[] = [];

  if (gaMeasurementId) {
    loaders.push(initGA(gaMeasurementId));
  }

  if (segmentWriteKey) {
    loaders.push(initSegment(segmentWriteKey));
  }

  if (loaders.length) {
    try {
      await Promise.all(loaders);
      initialized = true;
    } catch (error) {
      console.warn('Analytics initialization failed', error);
    }
  }
};

export const trackEvent = (event: string, properties: Record<string, unknown> = {}) => {
  const { gaMeasurementId } = getEnv();

  if (gaMeasurementId && window.gtag) {
    window.gtag('event', event, properties);
  }

  if (window.analytics?.track) {
    window.analytics.track(event, properties);
  }
};

export const pushDataLayerEvent = (event: string, payload: AnalyticsEventPayload = {}) => {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...payload });
};

export const trackPageView = (path: string, properties: Record<string, unknown> = {}) => {
  const { gaMeasurementId } = getEnv();
  const mergedProps = { page_path: path, ...properties };

  if (gaMeasurementId && window.gtag) {
    window.gtag('event', 'page_view', mergedProps);
  }

  if (window.analytics?.page) {
    window.analytics.page(undefined, undefined, properties);
  }
};

export const identifyUser = (user: Pick<UserResource, 'id'> & Partial<UserResource>) => {
  if (window.analytics?.identify) {
    const traits: Record<string, unknown> = {
      email: user.emailAddresses?.[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      organizationIds: user.organizationMemberships?.map((membership) => membership.organization.id),
    };
    window.analytics.identify(user.id, traits);
  }

  lastIdentifiedUserId = user.id;

  const { gaMeasurementId } = getEnv();
  if (gaMeasurementId && window.gtag) {
    const properties: AnalyticsUserProperties = {
      email: user.emailAddresses?.[0]?.emailAddress ?? null,
      organization_count: user.organizationMemberships?.length ?? 0,
    };
    window.gtag('set', 'user_properties', properties);
  }
};

export const resetAnalytics = () => {
  initialized = false;
};

export const setUserProperties = (properties: AnalyticsUserProperties) => {
  const sanitized = Object.keys(properties).reduce<AnalyticsUserProperties>((acc, key) => {
    const value = properties[key];
    if (value !== undefined) {
      acc[key] = value;
    }
    return acc;
  }, {});

  if (Object.keys(sanitized).length === 0) return;

  const { gaMeasurementId } = getEnv();
  if (gaMeasurementId && window.gtag) {
    window.gtag('set', 'user_properties', sanitized);
  }

  if (window.analytics?.identify) {
    window.analytics.identify(lastIdentifiedUserId ?? undefined, sanitized);
  }
};

export const trackTiming = (event: string, durationMs: number, payload: AnalyticsEventPayload = {}) => {
  const eventPayload = { value: durationMs, event_category: 'timing', ...payload };
  trackEvent(event, eventPayload);
};
