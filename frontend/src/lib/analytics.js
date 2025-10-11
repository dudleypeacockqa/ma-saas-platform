/**
 * Simple analytics utility for tracking user events
 * Sends events to our own server for privacy-focused analytics
 */

const ANALYTICS_ENABLED = import.meta.env.PROD;
const ANALYTICS_ENDPOINT = '/api/analytics';

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
 * @param {string} pageName - Name of the page
 */
export function trackPageView(pageName) {
  trackEvent('page_view', {
    page: pageName,
    path: window.location.pathname,
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
