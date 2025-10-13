import { useEffect, useMemo, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useSubscription } from '@/hooks/useSubscription';
import {
  BillingInterval,
  recordFeatureAdoption,
  recordSubscriptionActivation,
  recordTrialConversion,
  trackRevenueMetrics,
  recordChurnSignal,
} from '@/lib/advancedAnalytics';
import {
  buildRevenueSnapshot,
  recommendUpgrades,
  SubscriptionRecord,
  UpgradeRecommendation,
} from '@/services/revenueMetrics';

export interface RevenueAnalyticsResult {
  snapshot: ReturnType<typeof buildRevenueSnapshot> | null;
  recommendations: UpgradeRecommendation[];
  trackFeatureUsage: (featureKey: string, count?: number) => void;
  reportChurnSignal: (reason: string, riskScore: number) => void;
}

const normalizeInterval = (interval?: string): BillingInterval => {
  if (interval === 'year' || interval === 'yearly' || interval === 'annual') return 'yearly';
  return 'monthly';
};

const defaultCurrency = 'GBP';

const buildSubscriptionRecord = (
  subscription: any,
  tier: string,
): SubscriptionRecord | null => {
  if (!subscription) return null;

  const amount = Number(subscription.amount ?? subscription.price ?? 0);
  const interval = normalizeInterval(subscription.interval ?? subscription.billingInterval);
  const status = (subscription.status ?? 'trialing') as SubscriptionRecord['status'];
  const startedAt = Number(subscription.startedAt ?? subscription.createdAt ?? Date.now());
  const currentPeriodEnd = Number(subscription.currentPeriodEnd ?? Date.now());

  return {
    tier,
    amount,
    currency: (subscription.currency ?? defaultCurrency).toUpperCase(),
    interval,
    status,
    startedAt,
    currentPeriodEnd,
    trialEndsAt: subscription.trialEndsAt ? Number(subscription.trialEndsAt) : undefined,
    canceledAt: subscription.canceledAt ? Number(subscription.canceledAt) : undefined,
    churnedAt: subscription.churnedAt ? Number(subscription.churnedAt) : undefined,
    seats: subscription.seats ? Number(subscription.seats) : undefined,
    usage: subscription.usageMetrics ?? [],
  };
};

export const useRevenueAnalytics = (): RevenueAnalyticsResult => {
  const { subscription, tier, status } = useSubscription();
  const { user, isSignedIn } = useUser();
  const hasTrackedActivation = useRef(false);
  const hasTrackedTrial = useRef(false);

  const subscriptionRecord = useMemo(() => buildSubscriptionRecord(subscription, tier), [
    subscription,
    tier,
  ]);

  const snapshot = useMemo(() => {
    if (!subscriptionRecord) return null;
    return buildRevenueSnapshot([subscriptionRecord], { logAnalytics: false });
  }, [subscriptionRecord]);

  const recommendations = useMemo(() => {
    if (!subscriptionRecord) return [];
    return recommendUpgrades(subscriptionRecord);
  }, [subscriptionRecord]);

  useEffect(() => {
    if (!subscriptionRecord) return;

    if ((status?.isTrialing || subscriptionRecord.status === 'trialing') && !hasTrackedTrial.current) {
      recordTrialConversion({
        items: [
          {
            item_id: subscription?.planId ?? subscription?.planSlug ?? subscriptionRecord.tier,
            item_name: subscriptionRecord.tier,
            price: subscriptionRecord.amount,
            currency: subscriptionRecord.currency,
            tier: subscriptionRecord.tier,
            billing_interval: subscriptionRecord.interval,
          },
        ],
        value: 0,
        currency: subscriptionRecord.currency,
        trial: true,
        trial_days: subscriptionRecord.trialEndsAt
          ? Math.ceil((subscriptionRecord.trialEndsAt - Date.now()) / (1000 * 60 * 60 * 24))
          : undefined,
      });
      hasTrackedTrial.current = true;
    }

    if (
      (status?.isActive || subscriptionRecord.status === 'active') &&
      !hasTrackedActivation.current &&
      subscriptionRecord.amount > 0
    ) {
      recordSubscriptionActivation({
        items: [
          {
            item_id: subscription?.planId ?? subscription?.planSlug ?? subscriptionRecord.tier,
            item_name: subscriptionRecord.tier,
            price: subscriptionRecord.amount,
            currency: subscriptionRecord.currency,
            tier: subscriptionRecord.tier,
            billing_interval: subscriptionRecord.interval,
          },
        ],
        value: subscriptionRecord.interval === 'monthly'
          ? subscriptionRecord.amount
          : subscriptionRecord.amount,
        currency: subscriptionRecord.currency,
        mrr: subscriptionRecord.interval === 'monthly'
          ? subscriptionRecord.amount
          : subscriptionRecord.amount / 12,
        arr: subscriptionRecord.interval === 'monthly'
          ? subscriptionRecord.amount * 12
          : subscriptionRecord.amount,
        ltv: snapshot?.ltv,
      });
      hasTrackedActivation.current = true;
    }
  }, [subscriptionRecord, subscription, status, snapshot]);

  useEffect(() => {
    if (!snapshot || !isSignedIn) return;

    trackRevenueMetrics({
      mrr: snapshot.mrr,
      arr: snapshot.arr,
      ltv: snapshot.ltv,
      churn_rate: snapshot.churnRate,
      arpa: snapshot.arpa,
      customer_count: snapshot.customerCount,
      tier,
    });
  }, [snapshot, isSignedIn, tier]);

  const trackFeatureUsage = (featureKey: string, count = 1) => {
    if (!subscriptionRecord) return;
    recordFeatureAdoption({
      feature_key: featureKey,
      usage_count: count,
      tier: subscriptionRecord.tier,
    });
  };

  const reportChurnSignal = (reason: string, riskScore: number) => {
    if (!subscriptionRecord) return;
    recordChurnSignal({
      reason,
      risk_score: riskScore,
      tier: subscriptionRecord.tier,
    });
  };

  return {
    snapshot,
    recommendations,
    trackFeatureUsage,
    reportChurnSignal,
  };
};
