/**
 * Sentry integration for frontend error tracking and performance monitoring
 */

import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

/**
 * Initialize Sentry SDK
 * Call this in your main.tsx or App.tsx before mounting the app
 */
export function initSentry() {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN;

  if (!sentryDsn) {
    console.info('Sentry DSN not configured. Skipping Sentry initialization.');
    return;
  }

  const environment = import.meta.env.VITE_ENVIRONMENT || 'development';
  const release = import.meta.env.VITE_GIT_COMMIT_SHA || 'unknown';

  Sentry.init({
    dsn: sentryDsn,

    // Set environment
    environment,

    // Set release version
    release,

    // Enable integrations
    integrations: [
      // Browser tracing for performance monitoring
      new BrowserTracing({
        // Set tracing origins to match your API
        tracingOrigins: [
          'localhost',
          /^\//,  // Relative URLs
          /^https:\/\/[^/]*\.render\.com/,  // Render.com APIs
        ],

        // React Router integration
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          // Will be available after React Router setup
        ),
      }),

      // Replay integration for session recording
      new Sentry.Replay({
        // Mask all text content for privacy
        maskAllText: true,
        // Block all media (images, videos) for privacy
        blockAllMedia: true,
        // Sample rate for normal sessions
        sessionSampleRate: environment === 'production' ? 0.1 : 1.0,
        // Sample rate for sessions with errors
        errorSampleRate: 1.0,
      }),
    ],

    // Performance monitoring sample rate
    tracesSampleRate: getTracesSampleRate(environment),

    // Error sampling
    sampleRate: 1.0,  // Capture 100% of errors

    // Maximum breadcrumbs
    maxBreadcrumbs: 50,

    // Attach stack traces
    attachStacktrace: true,

    // Don't send default PII
    sendDefaultPII: false,

    // Debug mode (only in development)
    debug: environment === 'development',

    // Before send hook
    beforeSend: beforeSendHook,

    // Before send transaction hook
    beforeSendTransaction: beforeSendTransactionHook,

    // Ignore specific errors
    ignoreErrors: [
      // Browser extension errors
      'top.GLOBALS',
      'chrome-extension://',
      'moz-extension://',

      // Network errors
      'NetworkError',
      'Network request failed',
      'Failed to fetch',

      // Script loading errors
      'ResizeObserver loop limit exceeded',
      'ResizeObserver loop completed with undelivered notifications',

      // Common false positives
      'Non-Error promise rejection captured',
    ],

    // Deny URLs (don't report errors from these sources)
    denyUrls: [
      /extensions\//i,
      /^chrome:\/\//i,
      /^moz-extension:\/\//i,
    ],
  });

  console.info(`Sentry initialized for environment: ${environment}`);
}

/**
 * Get traces sample rate based on environment
 */
function getTracesSampleRate(environment: string): number {
  const rates: Record<string, number> = {
    production: 0.1,   // Sample 10% in production
    staging: 0.5,      // Sample 50% in staging
    development: 1.0,  // Sample 100% in development
  };
  return rates[environment] || 0.1;
}

/**
 * Before send hook - filter/modify events before sending
 */
function beforeSendHook(event: Sentry.Event, hint: Sentry.EventHint): Sentry.Event | null {
  // Filter out specific error types
  if (hint.originalException) {
    const error = hint.originalException;

    // Don't send network timeouts
    if (error instanceof Error && error.message.includes('timeout')) {
      return null;
    }

    // Don't send 404 errors
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
  }

  // Remove sensitive data from request
  if (event.request) {
    // Remove authorization headers
    if (event.request.headers) {
      if (event.request.headers['Authorization']) {
        event.request.headers['Authorization'] = '[Filtered]';
      }
      if (event.request.headers['X-API-Key']) {
        event.request.headers['X-API-Key'] = '[Filtered]';
      }
    }

    // Remove sensitive query parameters
    if (event.request.query_string) {
      const sensitiveParams = ['api_key', 'token', 'password', 'secret'];
      sensitiveParams.forEach(param => {
        if (event.request?.query_string?.includes(param)) {
          event.request.query_string = event.request.query_string.replace(
            new RegExp(`${param}=[^&]*`, 'gi'),
            `${param}=[Filtered]`
          );
        }
      });
    }
  }

  return event;
}

/**
 * Before send transaction hook - filter/modify transactions
 */
function beforeSendTransactionHook(
  event: Sentry.Event,
  hint: Sentry.EventHint
): Sentry.Event | null {
  // Don't send transactions for health checks
  if (event.transaction === '/health' || event.transaction === '/api/health') {
    return null;
  }

  // Don't send transactions for static assets
  if (event.transaction?.match(/\.(js|css|png|jpg|svg|woff|woff2)$/)) {
    return null;
  }

  return event;
}

/**
 * Set user context for Sentry
 */
export function setUserContext(
  userId: string,
  email?: string,
  organizationId?: string
) {
  Sentry.setUser({
    id: userId,
    email,
    organization_id: organizationId,
  });
}

/**
 * Clear user context (on logout)
 */
export function clearUserContext() {
  Sentry.setUser(null);
}

/**
 * Set custom context
 */
export function setContext(key: string, data: Record<string, any>) {
  Sentry.setContext(key, data);
}

/**
 * Add a breadcrumb
 */
export function addBreadcrumb(
  message: string,
  category: string = 'default',
  level: Sentry.SeverityLevel = 'info',
  data?: Record<string, any>
) {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    data,
  });
}

/**
 * Manually capture an exception
 */
export function captureException(error: Error, context?: Record<string, any>) {
  if (context) {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value);
      });
      Sentry.captureException(error);
    });
  } else {
    Sentry.captureException(error);
  }
}

/**
 * Manually capture a message
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info',
  context?: Record<string, any>
) {
  if (context) {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value);
      });
      Sentry.captureMessage(message, level);
    });
  } else {
    Sentry.captureMessage(message, level);
  }
}

/**
 * Start a transaction for performance monitoring
 */
export function startTransaction(name: string, op: string) {
  return Sentry.startTransaction({ name, op });
}

/**
 * Create an error boundary component
 * Use this to wrap your app or specific components
 */
export const SentryErrorBoundary = Sentry.ErrorBoundary;

/**
 * Fallback component for error boundary
 */
export function ErrorFallback({ error, resetError }: { error: Error; resetError: () => void }) {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Something went wrong</h1>
      <p>We've been notified and are looking into it.</p>
      <pre style={{ textAlign: 'left', padding: '1rem', background: '#f5f5f5' }}>
        {error.message}
      </pre>
      <button onClick={resetError} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>
        Try again
      </button>
    </div>
  );
}

/**
 * HOC to profile component performance
 */
export const withProfiler = Sentry.withProfiler;

// Export Sentry for direct access if needed
export { Sentry };

/**
 * Usage Example:
 *
 * // In main.tsx:
 * import { initSentry } from './lib/sentry';
 * initSentry();
 *
 * // In App.tsx:
 * import { SentryErrorBoundary, ErrorFallback } from './lib/sentry';
 *
 * function App() {
 *   return (
 *     <SentryErrorBoundary fallback={ErrorFallback}>
 *       <Router>
 *         <Routes>...</Routes>
 *       </Router>
 *     </SentryErrorBoundary>
 *   );
 * }
 *
 * // In auth context:
 * import { setUserContext, clearUserContext } from './lib/sentry';
 *
 * function login(user) {
 *   setUserContext(user.id, user.email, user.organizationId);
 * }
 *
 * function logout() {
 *   clearUserContext();
 * }
 *
 * // In API calls:
 * import { addBreadcrumb, captureException } from './lib/sentry';
 *
 * async function fetchData() {
 *   addBreadcrumb('Fetching deals', 'api', 'info');
 *   try {
 *     const response = await fetch('/api/deals');
 *     return await response.json();
 *   } catch (error) {
 *     captureException(error, { context: 'fetchDeals' });
 *     throw error;
 *   }
 * }
 *
 * // With profiler:
 * import { withProfiler } from './lib/sentry';
 *
 * export default withProfiler(MyExpensiveComponent);
 */
