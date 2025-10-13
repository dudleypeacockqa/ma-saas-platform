import { trackEvent, trackPageView } from '@/lib/analytics';

describe('analytics utility', () => {
  beforeEach(() => {
    window.gtag = jest.fn();
    window.analytics = {
      track: jest.fn(),
      page: jest.fn(),
    } as any;
    process.env.VITE_GA_MEASUREMENT_ID = 'GA-TEST';
    process.env.VITE_SEGMENT_WRITE_KEY = 'SEGMENT-TEST';
  });

  afterEach(() => {
    delete window.gtag;
    delete window.analytics;
    delete process.env.VITE_GA_MEASUREMENT_ID;
    delete process.env.VITE_SEGMENT_WRITE_KEY;
  });

  it('sends GA event when gtag is available', () => {
    trackEvent('test_event', { value: 42 });
    expect(window.gtag).toHaveBeenCalledWith('event', 'test_event', { value: 42 });
  });

  it('tracks page view in GA', () => {
    trackPageView('/pricing', { page_title: 'Pricing' });
    expect(window.gtag).toHaveBeenCalledWith('event', 'page_view', {
      page_path: '/pricing',
      page_title: 'Pricing',
    });
  });

  it('sends Segment event when analytics is available', () => {
    trackEvent('trial_started', { plan: 'Solo' });
    expect(window.analytics?.track).toHaveBeenCalledWith('trial_started', { plan: 'Solo' });
  });
});
