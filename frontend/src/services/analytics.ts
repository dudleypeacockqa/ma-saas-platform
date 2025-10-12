/**
 * Analytics and Usage Tracking Service
 * Sprint 25: Privacy-focused analytics for performance optimization and user experience
 */

interface AnalyticsEvent {
  category: string;
  action: string;
  label?: string;
  value?: number;
  customProperties?: Record<string, any>;
}

interface UserSession {
  sessionId: string;
  userId?: string;
  organizationId?: string;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  userAgent: string;
  screenResolution: string;
  startTime: number;
  lastActivity: number;
  pageViews: number;
  interactions: number;
}

interface PerformanceMetric {
  metric: string;
  value: number;
  timestamp: number;
  route: string;
  deviceType: string;
  connectionType?: string;
}

class AnalyticsService {
  private session: UserSession;
  private eventQueue: AnalyticsEvent[] = [];
  private performanceQueue: PerformanceMetric[] = [];
  private isEnabled: boolean;
  private batchSize: number = 10;
  private flushInterval: number = 30000; // 30 seconds
  private flushTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.isEnabled = this.shouldEnableAnalytics();
    this.session = this.createSession();

    if (this.isEnabled) {
      this.startSession();
      this.setupEventListeners();
      this.startPerformanceMonitoring();
    }
  }

  /**
   * Check if analytics should be enabled (respecting privacy)
   */
  private shouldEnableAnalytics(): boolean {
    // Check for Do Not Track header
    if (navigator.doNotTrack === '1') {
      return false;
    }

    // Check for user consent (could be set by cookie banner)
    const consent = localStorage.getItem('analytics-consent');
    if (consent === 'false') {
      return false;
    }

    // Default to enabled for internal analytics (no external services)
    return true;
  }

  /**
   * Create a new user session
   */
  private createSession(): UserSession {
    const deviceType = this.getDeviceType();

    return {
      sessionId: this.generateSessionId(),
      deviceType,
      userAgent: navigator.userAgent,
      screenResolution: `${screen.width}x${screen.height}`,
      startTime: Date.now(),
      lastActivity: Date.now(),
      pageViews: 0,
      interactions: 0,
    };
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Determine device type from screen size and user agent
   */
  private getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
    const width = screen.width;
    const userAgent = navigator.userAgent.toLowerCase();

    if (width <= 768 || /mobile|android|iphone|ipod/.test(userAgent)) {
      return 'mobile';
    } else if (width <= 1024 || /ipad|tablet/.test(userAgent)) {
      return 'tablet';
    }
    return 'desktop';
  }

  /**
   * Start the analytics session
   */
  private startSession(): void {
    this.track('session', 'start', this.session.deviceType);
    this.startFlushTimer();
  }

  /**
   * Setup event listeners for automatic tracking
   */
  private setupEventListeners(): void {
    // Page navigation
    window.addEventListener('popstate', () => {
      this.trackPageView();
    });

    // User activity
    document.addEventListener('click', () => {
      this.session.interactions++;
      this.session.lastActivity = Date.now();
    });

    document.addEventListener('keydown', () => {
      this.session.interactions++;
      this.session.lastActivity = Date.now();
    });

    // Page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.track('session', 'blur');
      } else {
        this.track('session', 'focus');
        this.session.lastActivity = Date.now();
      }
    });

    // Before page unload
    window.addEventListener('beforeunload', () => {
      this.endSession();
    });

    // Network status changes
    window.addEventListener('online', () => {
      this.track('connectivity', 'online');
      this.flush(); // Flush queued events when back online
    });

    window.addEventListener('offline', () => {
      this.track('connectivity', 'offline');
    });
  }

  /**
   * Start performance monitoring
   */
  private startPerformanceMonitoring(): void {
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      // Largest Contentful Paint (LCP)
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.trackPerformance('lcp', lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        console.warn('LCP observer not supported');
      }

      // First Input Delay (FID)
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry) => {
            this.trackPerformance('fid', entry.processingStart - entry.startTime);
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        console.warn('FID observer not supported');
      }

      // Cumulative Layout Shift (CLS)
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          });
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });

        // Report CLS periodically
        setInterval(() => {
          this.trackPerformance('cls', clsValue);
          clsValue = 0;
        }, 10000);
      } catch (e) {
        console.warn('CLS observer not supported');
      }
    }

    // Monitor navigation timing
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          this.trackPerformance('load_time', navigation.loadEventEnd - navigation.navigationStart);
          this.trackPerformance('dom_content_loaded', navigation.domContentLoadedEventEnd - navigation.navigationStart);
          this.trackPerformance('first_byte', navigation.responseStart - navigation.navigationStart);
        }
      }, 0);
    });
  }

  /**
   * Track a custom event
   */
  track(category: string, action: string, label?: string, value?: number, customProperties?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      category,
      action,
      label,
      value,
      customProperties: {
        ...customProperties,
        sessionId: this.session.sessionId,
        deviceType: this.session.deviceType,
        timestamp: Date.now(),
        route: window.location.pathname,
      },
    };

    this.eventQueue.push(event);
    this.session.lastActivity = Date.now();

    // Flush immediately for important events
    if (category === 'error' || category === 'conversion') {
      this.flush();
    } else if (this.eventQueue.length >= this.batchSize) {
      this.flush();
    }
  }

  /**
   * Track page view
   */
  trackPageView(route?: string): void {
    const currentRoute = route || window.location.pathname;
    this.session.pageViews++;
    this.track('navigation', 'page_view', currentRoute);
  }

  /**
   * Track performance metric
   */
  trackPerformance(metric: string, value: number): void {
    if (!this.isEnabled) return;

    const performanceMetric: PerformanceMetric = {
      metric,
      value,
      timestamp: Date.now(),
      route: window.location.pathname,
      deviceType: this.session.deviceType,
      connectionType: this.getConnectionType(),
    };

    this.performanceQueue.push(performanceMetric);

    if (this.performanceQueue.length >= this.batchSize) {
      this.flushPerformance();
    }
  }

  /**
   * Get connection type if available
   */
  private getConnectionType(): string | undefined {
    const connection = (navigator as any).connection;
    return connection?.effectiveType;
  }

  /**
   * Track user interaction
   */
  trackInteraction(element: string, action: string, context?: Record<string, any>): void {
    this.track('interaction', action, element, undefined, context);
  }

  /**
   * Track business events
   */
  trackBusinessEvent(event: string, properties?: Record<string, any>): void {
    this.track('business', event, undefined, undefined, properties);
  }

  /**
   * Track errors
   */
  trackError(error: Error, context?: Record<string, any>): void {
    this.track('error', 'javascript_error', error.message, undefined, {
      stack: error.stack,
      ...context,
    });
  }

  /**
   * Track feature usage
   */
  trackFeature(feature: string, action: string, properties?: Record<string, any>): void {
    this.track('feature', action, feature, undefined, properties);
  }

  /**
   * Flush events to server
   */
  private async flush(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    const events = [...this.eventQueue];
    this.eventQueue = [];

    try {
      // Send to your analytics endpoint
      await this.sendEvents(events);
    } catch (error) {
      console.warn('Failed to send analytics events:', error);
      // Re-queue events for retry (with limit to prevent memory issues)
      if (this.eventQueue.length < 100) {
        this.eventQueue.unshift(...events);
      }
    }
  }

  /**
   * Flush performance metrics
   */
  private async flushPerformance(): Promise<void> {
    if (this.performanceQueue.length === 0) return;

    const metrics = [...this.performanceQueue];
    this.performanceQueue = [];

    try {
      await this.sendPerformanceMetrics(metrics);
    } catch (error) {
      console.warn('Failed to send performance metrics:', error);
    }
  }

  /**
   * Send events to analytics endpoint
   */
  private async sendEvents(events: AnalyticsEvent[]): Promise<void> {
    if (!navigator.onLine) {
      // Queue for later when online
      return;
    }

    const response = await fetch('/api/analytics/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        events,
        session: this.session,
      }),
    });

    if (!response.ok) {
      throw new Error(`Analytics request failed: ${response.status}`);
    }
  }

  /**
   * Send performance metrics to analytics endpoint
   */
  private async sendPerformanceMetrics(metrics: PerformanceMetric[]): Promise<void> {
    if (!navigator.onLine) {
      return;
    }

    const response = await fetch('/api/analytics/performance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        metrics,
        session: this.session,
      }),
    });

    if (!response.ok) {
      throw new Error(`Performance metrics request failed: ${response.status}`);
    }
  }

  /**
   * Start the flush timer
   */
  private startFlushTimer(): void {
    this.flushTimer = setInterval(() => {
      this.flush();
      this.flushPerformance();
    }, this.flushInterval);
  }

  /**
   * End the current session
   */
  private endSession(): void {
    const sessionDuration = Date.now() - this.session.startTime;
    this.track('session', 'end', undefined, sessionDuration, {
      pageViews: this.session.pageViews,
      interactions: this.session.interactions,
    });

    // Flush immediately before page unload
    this.flush();
    this.flushPerformance();

    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
  }

  /**
   * Update user information
   */
  setUser(userId: string, organizationId?: string): void {
    this.session.userId = userId;
    this.session.organizationId = organizationId;
    this.track('user', 'identify', userId);
  }

  /**
   * Enable or disable analytics
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    localStorage.setItem('analytics-consent', enabled.toString());

    if (enabled) {
      this.startSession();
    } else {
      this.endSession();
    }
  }

  /**
   * Get current session information
   */
  getSession(): UserSession {
    return { ...this.session };
  }
}

// Export singleton instance
export const analytics = new AnalyticsService();

// React hook for analytics
export function useAnalytics() {
  return {
    track: analytics.track.bind(analytics),
    trackPageView: analytics.trackPageView.bind(analytics),
    trackPerformance: analytics.trackPerformance.bind(analytics),
    trackInteraction: analytics.trackInteraction.bind(analytics),
    trackBusinessEvent: analytics.trackBusinessEvent.bind(analytics),
    trackError: analytics.trackError.bind(analytics),
    trackFeature: analytics.trackFeature.bind(analytics),
    setUser: analytics.setUser.bind(analytics),
    setEnabled: analytics.setEnabled.bind(analytics),
    getSession: analytics.getSession.bind(analytics),
  };
}

export default analytics;