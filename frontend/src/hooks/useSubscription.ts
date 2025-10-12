import { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';

export interface Subscription {
  id: number;
  stripe_subscription_id: string;
  plan_tier: string;
  status: string;
  amount: number;
  currency: string;
  interval: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  features: {
    max_deals: number;
    max_users: number;
    max_storage_gb: number;
    ai_credits_per_month: number;
    features: string[];
  };
}

interface UseSubscriptionReturn {
  subscription: Subscription | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  hasActiveSubscription: boolean;
  isCurrentPlan: (planTier: string) => boolean;
}

export const useSubscription = (): UseSubscriptionReturn => {
  const { isSignedIn } = useUser();
  const { getToken } = useAuth();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchSubscription = async () => {
    if (!isSignedIn) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const token = await getToken();

      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${API_BASE_URL}/api/payments/subscription/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      } else if (response.status === 404) {
        // No subscription found - this is ok
        setSubscription(null);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch subscription');
      }
    } catch (err) {
      console.error('Error fetching subscription:', err);
      setError(err instanceof Error ? err.message : 'Failed to load subscription');
      setSubscription(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, [isSignedIn]);

  const isCurrentPlan = (planTier: string): boolean => {
    if (!subscription) return false;
    return subscription.plan_tier === planTier &&
           (subscription.status === 'active' || subscription.status === 'trialing');
  };

  const hasActiveSubscription =
    subscription !== null &&
    (subscription.status === 'active' || subscription.status === 'trialing');

  return {
    subscription,
    isLoading,
    error,
    refetch: fetchSubscription,
    hasActiveSubscription,
    isCurrentPlan
  };
};

export default useSubscription;
