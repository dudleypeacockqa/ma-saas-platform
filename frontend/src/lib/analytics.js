/**
 * Simple analytics utility for tracking user events
 * Sends events to our own server for privacy-focused analytics
 */

const ANALYTICS_ENABLED = import.meta.env.PROD;
const ANALYTICS_ENDPOINT = '/api/analytics';

let analyticsInitialized = false;

/**
 * Initialise analytics (idempotent so callers can invoke freely)
 */
export function initAnalytics() {
  if (analyticsInitialized) return;

  analyticsInitialized = true;

  if (!ANALYTICS_ENABLED) {
    console.log('📊 [DEV] Analytics initialised');
  }
}

/**
 * Track a custom event
 * @param {string} eventName - Name of the event (e.g., 'page_view', 'button_click')
 * @param {object} data - Additional data to track with the event
 */
export async function trackEvent(eventName, data = {}) {
  if (!ANALYTICS_ENABLED) {
    console.log('📊 [DEV] Analytics event:', eventName, data);
    return;
  }

  try {
    await fetch(ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event: eventName,
        data: {
          ...data,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          referrer: document.referrer,
        },
      }),
    });
  } catch (error) {
    console.error('Failed to track event:', error);
  }
}

/**
 * Track page view
 * @param {string} pagePath - Path of the page being viewed
 * @param {object} metadata - Additional metadata to attach
 */
export function trackPageView(pagePath, metadata = {}) {
  const path = typeof pagePath === 'string' ? pagePath : window.location.pathname;

  trackEvent('page_view', {
    page: path,
    path,
    title: typeof document !== 'undefined' ? document.title : undefined,
    ...metadata,
  });
}

/**
 * Track user interaction
 * @param {string} element - Element that was interacted with
 * @param {string} action - Action taken (click, hover, etc.)
 */
export function trackInteraction(element, action = 'click') {
  trackEvent('interaction', {
    element,
    action,
  });
}

/**
 * Track error
 * @param {Error} error - Error object
 * @param {string} context - Context where error occurred
 */
export function trackError(error, context) {
  trackEvent('error', {
    message: error.message,
    stack: error.stack,
    context,
  });
}

/**
 * Track performance metric
 * @param {string} metric - Name of the metric
 * @param {number} value - Value of the metric
 */
export function trackPerformance(metric, value) {
  trackEvent('performance', {
    metric,
    value,
  });
}

/**
 * Identify the current user for analytics purposes
 * @param {import('@clerk/types').UserResource | { id: string; emailAddress?: string; fullName?: string }} user
 */
export function identifyUser(user) {
  if (!user) return;

  const userId = user.id || user.userId;
  const email =
    user.primaryEmailAddress?.emailAddress ||
    user.emailAddress ||
    user.emailAddresses?.[0]?.emailAddress;
  const name =
    user.fullName ||
    (user.firstName || user.lastName
      ? `${user.firstName ?? ''} ${user.lastName ?? ''}`.trim()
      : undefined);

  trackEvent('identify_user', {
    user_id: userId,
    email,
    name,
  });
}

// Auto-track page views on navigation
if (typeof window !== 'undefined') {
  // Track initial page load
  window.addEventListener('load', () => {
    trackPageView(document.title);

    // Track Core Web Vitals
    if ('PerformanceObserver' in window) {
      // Largest Contentful Paint
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        trackPerformance('lcp', lastEntry.renderTime || lastEntry.loadTime);
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // First Input Delay
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          trackPerformance('fid', entry.processingStart - entry.startTime);
        });
      }).observe({ entryTypes: ['first-input'] });

      // Cumulative Layout Shift
      let clsValue = 0;
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
        trackPerformance('cls', clsValue);
      }).observe({ entryTypes: ['layout-shift'] });
    }
  });

  // Track page visibility changes
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      trackEvent('page_hidden', {
        timeOnPage: performance.now(),
      });
    }
  });
}
