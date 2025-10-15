import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

import { initAnalytics, trackPageView, identifyUser } from '@/lib/analytics';

const AnalyticsListener = () => {
  const location = useLocation();
  const { user, isLoaded, isSignedIn } = useUser();

  useEffect(() => {
    initAnalytics();
  }, []);

  useEffect(() => {
    initAnalytics().then(() => {
      const title = typeof document !== 'undefined' ? document.title : undefined;
      trackPageView(location.pathname + location.search, {
        page_title: title,
      });
    });
  }, [location]);

  useEffect(() => {
    if (isLoaded && isSignedIn && user) {
      identifyUser(user);
    }
  }, [isLoaded, isSignedIn, user]);

  return null;
};

export default AnalyticsListener;
