import { useUser } from '@clerk/clerk-react';
import { FEATURES, TIERS, getTierFromPlanId } from '../constants/features';

/**
 * Custom hook to access user subscription information
 * Uses feature constants from CLERK_FEATURE_REGISTRY_MASTER.md
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

  // Determine subscription tier from plan ID or slug
  const getTier = () => {
    if (!subscription) return TIERS.FREE;

    // Try to get tier from plan ID first (most reliable)
    if (subscription.planId) {
      return getTierFromPlanId(subscription.planId);
    }

    // Fallback to slug-based detection
    if (!subscription.planSlug) return TIERS.FREE;

    const slug = subscription.planSlug.toLowerCase();
    if (slug.includes('community_leader')) return TIERS.COMMUNITY_LEADER;
    if (slug.includes('enterprise')) return TIERS.ENTERPRISE;
    if (slug.includes('growth_firm')) return TIERS.GROWTH_FIRM;
    if (slug.includes('solo_dealmaker')) return TIERS.SOLO_DEALMAKER;
    return TIERS.FREE;
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

  // Tier-specific checks using constants
  const isSoloDealmaker = tier === TIERS.SOLO_DEALMAKER;
  const isGrowthFirm = tier === TIERS.GROWTH_FIRM;
  const isEnterprise = tier === TIERS.ENTERPRISE;
  const isCommunityLeader = tier === TIERS.COMMUNITY_LEADER;
  const isFree = tier === TIERS.FREE || tier === null;

  // Feature access helpers - using constants from registry
  const canAccessPlatform = hasFeature(FEATURES.PLATFORM_ACCESS_FULL);
  const canAccessAI = hasFeature(FEATURES.AI_DEAL_ANALYSIS);
  const canAccessBasicCommunity = hasFeature(FEATURES.COMMUNITY_ESSENTIAL);
  const canAccessProCommunity = hasFeature(FEATURES.COMMUNITY_PROFESSIONAL);
  const canAccessExecutiveCommunity = hasFeature(FEATURES.COMMUNITY_EXECUTIVE);
  const canAccessCommunity =
    canAccessBasicCommunity || canAccessProCommunity || canAccessExecutiveCommunity;
  const canAccessWebinars = hasFeature(FEATURES.WEBINARS_MONTHLY);
  const canAccessMasterclass = hasFeature(FEATURES.MASTERCLASS_BASIC);
  const canAccessTeamCollaboration = hasFeature(FEATURES.TEAM_COLLABORATION);
  const canAccessVIPEvents = hasFeature(FEATURES.EVENTS_VIP_ALL);
  const canAccessAIIntros = hasFeature(FEATURES.AI_INTRODUCTIONS_PRIORITY);
  const canAccessExclusiveDeals = hasFeature(FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE);
  const canAccessMasterminds = hasFeature(FEATURES.MASTERMIND_MONTHLY);
  const hasWhiteLabel = hasFeature(FEATURES.WHITE_LABEL_PLATFORM);
  const canHostPrivateEvents = hasFeature(FEATURES.EVENTS_PRIVATE_HOSTING);
  const hasCustomBranding = hasFeature(FEATURES.CUSTOM_BRANDING_API);
  const canAccessDealSyndication = hasFeature(FEATURES.DEAL_SYNDICATION_DIRECT);
  const hasInvestmentCommitteeAccess = hasFeature(FEATURES.INVESTMENT_COMMITTEE);
  const hasDedicatedSupport = hasFeature(FEATURES.DEDICATED_SUPPORT);
  const hasRevenueShare = hasFeature(FEATURES.REVENUE_SHARE_EVENTS);
  const hasPersonalShowcase = hasFeature(FEATURES.PERSONAL_SHOWCASE);
  const canLeadMentorProgram = hasFeature(FEATURES.MENTOR_LEADERSHIP);
  const hasLPIntroductions = hasFeature(FEATURES.LP_INTRODUCTIONS);
  const hasCommunityInfluence = hasFeature(FEATURES.COMMUNITY_INFLUENCE);
  const hasStreamYardAccess = hasFeature(FEATURES.STREAMYARD_STUDIO);

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
      // Core platform features
      canAccessPlatform,
      canAccessAI,
      // Community access by tier
      canAccessCommunity,
      canAccessBasicCommunity,
      canAccessProCommunity,
      canAccessExecutiveCommunity,
      // Solo Dealmaker features
      canAccessWebinars,
      canAccessMasterclass,
      // Growth Firm features
      canAccessTeamCollaboration,
      canAccessVIPEvents,
      canAccessAIIntros,
      canAccessExclusiveDeals,
      canAccessMasterminds,
      // Enterprise features
      hasWhiteLabel,
      canHostPrivateEvents,
      hasCustomBranding,
      canAccessDealSyndication,
      hasInvestmentCommitteeAccess,
      hasDedicatedSupport,
      // Community Leader features
      hasRevenueShare,
      hasPersonalShowcase,
      canLeadMentorProgram,
      hasLPIntroductions,
      hasCommunityInfluence,
      hasStreamYardAccess,
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
    [TIERS.FREE]: {
      name: 'Free',
      color: 'gray',
      icon: '🆓',
      maxDeals: 1,
      maxTeamMembers: 1,
    },
    [TIERS.SOLO_DEALMAKER]: {
      name: 'Solo Dealmaker',
      color: 'blue',
      icon: '⚡',
      maxDeals: 10,
      maxTeamMembers: 3,
    },
    [TIERS.GROWTH_FIRM]: {
      name: 'Growth Firm',
      color: 'green',
      icon: '🏢',
      maxDeals: 50,
      maxTeamMembers: 15,
    },
    [TIERS.ENTERPRISE]: {
      name: 'Enterprise',
      color: 'purple',
      icon: '👥',
      maxDeals: -1, // unlimited
      maxTeamMembers: -1, // unlimited
    },
    [TIERS.COMMUNITY_LEADER]: {
      name: 'Community Leader',
      color: 'amber',
      icon: '👑',
      maxDeals: -1, // unlimited
      maxTeamMembers: -1, // unlimited
      hasRevenueShare: true,
    },
  };

  return tierInfo[tier] || tierInfo[TIERS.FREE];
}
