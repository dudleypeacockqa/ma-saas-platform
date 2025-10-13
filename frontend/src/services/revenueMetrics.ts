import { BillingInterval, trackRevenueMetrics } from '@/lib/advancedAnalytics';

export interface SubscriptionRecord {
  tier: string;
  amount: number;
  currency: string;
  interval: BillingInterval;
  status: 'trialing' | 'active' | 'past_due' | 'canceled';
  startedAt: number;
  currentPeriodEnd: number;
  trialEndsAt?: number;
  canceledAt?: number;
  churnedAt?: number;
  seats?: number;
  usage?: {
    featureKey: string;
    count: number;
  }[];
}

export interface RevenueSnapshot {
  mrr: number;
  arr: number;
  ltv: number;
  churnRate: number;
  arpa: number;
  customerCount: number;
}

export const calculateMRR = (subscription: SubscriptionRecord): number => {
  if (subscription.interval === 'monthly') return subscription.amount;
  return subscription.amount / 12;
};

export const calculateARR = (subscription: SubscriptionRecord): number => {
  if (subscription.interval === 'monthly') return subscription.amount * 12;
  return subscription.amount;
};

export const calculateLTV = (mrr: number, grossMargin = 0.8, churnRate = 0.05): number => {
  if (churnRate <= 0) {
    return mrr * 60 * grossMargin; // assume 5 year lifetime when churn unknown
  }
  return (mrr * grossMargin) / churnRate;
};

export const calculateChurnRate = (
  activeSubscriptions: SubscriptionRecord[],
  churnedSubscriptions: SubscriptionRecord[],
): number => {
  const activeCount = activeSubscriptions.length;
  if (activeCount === 0) return 0;
  const churnedCount = churnedSubscriptions.length;
  return churnedCount / activeCount;
};

export const buildRevenueSnapshot = (
  subscriptions: SubscriptionRecord[],
  options: {
    grossMargin?: number;
    logAnalytics?: boolean;
  } = {},
): RevenueSnapshot => {
  const grossMargin = options.grossMargin ?? 0.8;
  const logAnalytics = options.logAnalytics ?? true;
  const active = subscriptions.filter((subscription) => subscription.status === 'active');
  const churned = subscriptions.filter((subscription) => subscription.status === 'canceled');

  const totalMRR = active.reduce((sum, subscription) => sum + calculateMRR(subscription), 0);
  const totalARR = active.reduce((sum, subscription) => sum + calculateARR(subscription), 0);
  const churnRate = calculateChurnRate(active, churned);
  const arpa = active.length ? totalMRR / active.length : 0;
  const ltv = calculateLTV(arpa, grossMargin, churnRate === 0 ? 0.05 : churnRate);

  const snapshot: RevenueSnapshot = {
    mrr: Number(totalMRR.toFixed(2)),
    arr: Number(totalARR.toFixed(2)),
    ltv: Number(ltv.toFixed(2)),
    churnRate: Number(churnRate.toFixed(4)),
    arpa: Number(arpa.toFixed(2)),
    customerCount: active.length,
  };

  if (logAnalytics) {
    trackRevenueMetrics({
      mrr: snapshot.mrr,
      arr: snapshot.arr,
      ltv: snapshot.ltv,
      churn_rate: snapshot.churnRate,
      arpa: snapshot.arpa,
      customer_count: snapshot.customerCount,
    });
  }

  return snapshot;
};

export interface UpgradeRecommendation {
  tier: string;
  reason: string;
  projectedMRR: number;
  probability: number;
}

export const recommendUpgrades = (subscription: SubscriptionRecord): UpgradeRecommendation[] => {
  const recommendations: UpgradeRecommendation[] = [];

  const usage = subscription.usage ?? [];
  const totalUsage = usage.reduce((sum, metric) => sum + metric.count, 0);

  if (subscription.tier === 'solo' && totalUsage > 50) {
    recommendations.push({
      tier: 'growth',
      reason: 'High feature engagement indicates readiness for collaborative tools.',
      projectedMRR: subscription.amount * 1.8,
      probability: 0.65,
    });
  }

  if (subscription.tier === 'growth' && (subscription.seats ?? 0) >= 10) {
    recommendations.push({
      tier: 'enterprise',
      reason: 'Team size exceeds Growth plan limits. Enterprise unlocks unlimited seats.',
      projectedMRR: subscription.amount * 1.4,
      probability: 0.55,
    });
  }

  return recommendations;
};
