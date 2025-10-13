import { useUser } from '@clerk/clerk-react';

/**
 * Custom hook to access user subscription information
 * @returns {Object} subscription data and helper functions
 */
export function useSubscription() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return {
      isLoading: true,
      subscription: null,
      tier: null,
      hasFeature: () => false,
      isTrialing: false,
      isActive: false,
      trialDaysRemaining: 0,
    };
  }

  const subscription = user?.publicMetadata?.subscription || null;

  // Determine subscription tier
  const getTier = () => {
    if (!subscription?.planSlug) return null;

    const slug = subscription.planSlug.toLowerCase();
    if (slug.includes('community_leader')) return 'community_leader';
    if (slug.includes('enterprise')) return 'enterprise';
    if (slug.includes('growth_firm')) return 'growth_firm';
    if (slug.includes('solo_dealmaker')) return 'solo_dealmaker';
    return 'free';
  };

  const tier = getTier();

  // Check if user has a specific feature
  const hasFeature = (featureName) => {
    if (!subscription?.features) return false;
    return subscription.features.includes(featureName);
  };

  // Check subscription status
  const isTrialing = subscription?.status === 'trialing';
  const isActive = subscription?.status === 'active' || isTrialing;
  const isPastDue = subscription?.status === 'past_due';
  const isCanceled = subscription?.status === 'canceled';

  // Calculate trial days remaining
  const trialDaysRemaining = subscription?.trialEndsAt
    ? Math.max(0, Math.ceil((subscription.trialEndsAt - Date.now()) / (1000 * 60 * 60 * 24)))
    : 0;

  // Calculate days until subscription ends
  const daysUntilEnd = subscription?.currentPeriodEnd
    ? Math.max(0, Math.ceil((subscription.currentPeriodEnd - Date.now()) / (1000 * 60 * 60 * 24)))
    : 0;

  // Tier-specific checks
  const isSoloDealmaker = tier === 'solo_dealmaker';
  const isGrowthFirm = tier === 'growth_firm';
  const isEnterprise = tier === 'enterprise';
  const isCommunityLeader = tier === 'community_leader';
  const isFree = tier === 'free' || tier === null;

  // Feature access helpers
  const canAccessAI = hasFeature('ai_analysis') || !isFree;
  const canAccessCommunity =
    hasFeature('community_essential') ||
    hasFeature('community_professional') ||
    hasFeature('community_executive');
  const canAccessEvents = hasFeature('vip_events_access') || isEnterprise || isCommunityLeader;
  const canHostEvents = hasFeature('private_events_hosting') || isCommunityLeader;
  const hasRevenueShare = hasFeature('revenue_sharing_events');
  const hasWhiteLabel = hasFeature('white_label_platform');

  return {
    isLoading: false,
    subscription,
    tier,
    tierChecks: {
      isFree,
      isSoloDealmaker,
      isGrowthFirm,
      isEnterprise,
      isCommunityLeader,
    },
    status: {
      isActive,
      isTrialing,
      isPastDue,
      isCanceled,
    },
    features: {
      hasFeature,
      canAccessAI,
      canAccessCommunity,
      canAccessEvents,
      canHostEvents,
      hasRevenueShare,
      hasWhiteLabel,
    },
    trialDaysRemaining,
    daysUntilEnd,
  };
}

/**
 * Hook to get subscription tier display information
 */
export function useSubscriptionTierInfo() {
  const { tier } = useSubscription();

  const tierInfo = {
    free: {
      name: 'Free',
      color: 'gray',
      icon: '🆓',
      maxDeals: 1,
      maxTeamMembers: 1,
    },
    solo_dealmaker: {
      name: 'Solo Dealmaker',
      color: 'blue',
      icon: '⚡',
      maxDeals: 10,
      maxTeamMembers: 3,
    },
    growth_firm: {
      name: 'Growth Firm',
      color: 'green',
      icon: '🏢',
      maxDeals: 50,
      maxTeamMembers: 15,
    },
    enterprise: {
      name: 'Enterprise',
      color: 'purple',
      icon: '👥',
      maxDeals: -1, // unlimited
      maxTeamMembers: -1, // unlimited
    },
    community_leader: {
      name: 'Community Leader',
      color: 'amber',
      icon: '👑',
      maxDeals: -1, // unlimited
      maxTeamMembers: -1, // unlimited
      hasRevenueShare: true,
    },
  };

  return tierInfo[tier] || tierInfo.free;
}
