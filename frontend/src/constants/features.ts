/**
 * Clerk Subscription Feature Constants
 *
 * Single source of truth for all subscription features across the platform.
 * This file is generated from CLERK_FEATURE_REGISTRY_MASTER.md
 *
 * @see CLERK_FEATURE_REGISTRY_MASTER.md for complete feature registry
 */

// Feature Keys - Use these constants throughout the codebase
export const FEATURES = {
  // ============================================
  // SOLO DEALMAKER TIER (5 features)
  // ============================================
  PLATFORM_ACCESS_FULL: 'platform_access_full',
  COMMUNITY_ESSENTIAL: 'community_essential',
  WEBINARS_MONTHLY: 'webinars_monthly',
  AI_DEAL_ANALYSIS: 'ai_deal_analysis',
  MASTERCLASS_BASIC: 'masterclass_basic',

  // ============================================
  // GROWTH FIRM TIER (+6 features = 11 total)
  // ============================================
  TEAM_COLLABORATION: 'team_collaboration_advanced',
  COMMUNITY_PROFESSIONAL: 'community_professional',
  EVENTS_VIP_ALL: 'events_vip_all',
  AI_INTRODUCTIONS_PRIORITY: 'ai_introductions_priority',
  DEAL_OPPORTUNITIES_EXCLUSIVE: 'deal_opportunities_exclusive',
  MASTERMIND_MONTHLY: 'mastermind_monthly',

  // ============================================
  // ENTERPRISE TIER (+7 features = 18 total)
  // ============================================
  WHITE_LABEL_PLATFORM: 'white_label_platform',
  COMMUNITY_EXECUTIVE: 'community_executive',
  EVENTS_PRIVATE_HOSTING: 'events_private_hosting',
  CUSTOM_BRANDING_API: 'custom_branding_api',
  DEAL_SYNDICATION_DIRECT: 'deal_syndication_direct',
  INVESTMENT_COMMITTEE: 'investment_committee',
  DEDICATED_SUPPORT: 'dedicated_support',

  // ============================================
  // COMMUNITY LEADER TIER (+6 features = 24 total)
  // ============================================
  REVENUE_SHARE_EVENTS: 'revenue_share_events',
  PERSONAL_SHOWCASE: 'personal_showcase',
  MENTOR_LEADERSHIP: 'mentor_leadership',
  LP_INTRODUCTIONS: 'lp_introductions',
  COMMUNITY_INFLUENCE: 'community_influence',
  STREAMYARD_STUDIO: 'streamyard_studio',
} as const;

// TypeScript type for feature keys
export type FeatureKey = typeof FEATURES[keyof typeof FEATURES];

// Clerk Plan IDs - All 8 subscription plans
export const PLAN_IDS = {
  SOLO_DEALMAKER_MONTHLY: 'cplan_340FS0Pg3VnW8d69QgNm3k5AOIb',
  SOLO_DEALMAKER_ANNUAL: 'cplan_340JQ6Oh8d6LbEOSJRP2yr6bRYq',
  GROWTH_FIRM_MONTHLY: 'cplan_340JZGyoC9UPhbzzlpGsAT2Ch6t',
  GROWTH_FIRM_ANNUAL: 'cplan_340T7QLnHwXWvTH6RvJ0FWGfMvI',
  ENTERPRISE_MONTHLY: 'cplan_340TNhs30Zb8LmXJV0gLX8XLUMd',
  ENTERPRISE_ANNUAL: 'cplan_340TtyxUTg743EaRAKQh256zZRl',
  COMMUNITY_LEADER_MONTHLY: 'cplan_340UJfnihYI46wkzOr4f88Hi6fU',
  COMMUNITY_LEADER_ANNUAL: 'cplan_340Un8FeQFLP8Xqy8IxSdbE7elf',
} as const;

// Subscription Tiers
export const TIERS = {
  FREE: 'free',
  SOLO_DEALMAKER: 'solo_dealmaker',
  GROWTH_FIRM: 'growth_firm',
  ENTERPRISE: 'enterprise',
  COMMUNITY_LEADER: 'community_leader',
} as const;

export type TierKey = typeof TIERS[keyof typeof TIERS];

// Feature-to-Tier Mapping (for validation and display)
export const TIER_FEATURES: Record<TierKey, FeatureKey[]> = {
  [TIERS.FREE]: [],

  [TIERS.SOLO_DEALMAKER]: [
    FEATURES.PLATFORM_ACCESS_FULL,
    FEATURES.COMMUNITY_ESSENTIAL,
    FEATURES.WEBINARS_MONTHLY,
    FEATURES.AI_DEAL_ANALYSIS,
    FEATURES.MASTERCLASS_BASIC,
  ],

  [TIERS.GROWTH_FIRM]: [
    // Inherits all Solo Dealmaker features
    FEATURES.PLATFORM_ACCESS_FULL,
    FEATURES.COMMUNITY_ESSENTIAL,
    FEATURES.WEBINARS_MONTHLY,
    FEATURES.AI_DEAL_ANALYSIS,
    FEATURES.MASTERCLASS_BASIC,
    // Plus Growth Firm features
    FEATURES.TEAM_COLLABORATION,
    FEATURES.COMMUNITY_PROFESSIONAL,
    FEATURES.EVENTS_VIP_ALL,
    FEATURES.AI_INTRODUCTIONS_PRIORITY,
    FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE,
    FEATURES.MASTERMIND_MONTHLY,
  ],

  [TIERS.ENTERPRISE]: [
    // Inherits all Growth Firm features
    FEATURES.PLATFORM_ACCESS_FULL,
    FEATURES.COMMUNITY_ESSENTIAL,
    FEATURES.WEBINARS_MONTHLY,
    FEATURES.AI_DEAL_ANALYSIS,
    FEATURES.MASTERCLASS_BASIC,
    FEATURES.TEAM_COLLABORATION,
    FEATURES.COMMUNITY_PROFESSIONAL,
    FEATURES.EVENTS_VIP_ALL,
    FEATURES.AI_INTRODUCTIONS_PRIORITY,
    FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE,
    FEATURES.MASTERMIND_MONTHLY,
    // Plus Enterprise features
    FEATURES.WHITE_LABEL_PLATFORM,
    FEATURES.COMMUNITY_EXECUTIVE,
    FEATURES.EVENTS_PRIVATE_HOSTING,
    FEATURES.CUSTOM_BRANDING_API,
    FEATURES.DEAL_SYNDICATION_DIRECT,
    FEATURES.INVESTMENT_COMMITTEE,
    FEATURES.DEDICATED_SUPPORT,
  ],

  [TIERS.COMMUNITY_LEADER]: [
    // Inherits all Enterprise features
    FEATURES.PLATFORM_ACCESS_FULL,
    FEATURES.COMMUNITY_ESSENTIAL,
    FEATURES.WEBINARS_MONTHLY,
    FEATURES.AI_DEAL_ANALYSIS,
    FEATURES.MASTERCLASS_BASIC,
    FEATURES.TEAM_COLLABORATION,
    FEATURES.COMMUNITY_PROFESSIONAL,
    FEATURES.EVENTS_VIP_ALL,
    FEATURES.AI_INTRODUCTIONS_PRIORITY,
    FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE,
    FEATURES.MASTERMIND_MONTHLY,
    FEATURES.WHITE_LABEL_PLATFORM,
    FEATURES.COMMUNITY_EXECUTIVE,
    FEATURES.EVENTS_PRIVATE_HOSTING,
    FEATURES.CUSTOM_BRANDING_API,
    FEATURES.DEAL_SYNDICATION_DIRECT,
    FEATURES.INVESTMENT_COMMITTEE,
    FEATURES.DEDICATED_SUPPORT,
    // Plus Community Leader features
    FEATURES.REVENUE_SHARE_EVENTS,
    FEATURES.PERSONAL_SHOWCASE,
    FEATURES.MENTOR_LEADERSHIP,
    FEATURES.LP_INTRODUCTIONS,
    FEATURES.COMMUNITY_INFLUENCE,
    FEATURES.STREAMYARD_STUDIO,
  ],
};

// Feature Display Names (for UI)
export const FEATURE_DISPLAY_NAMES: Record<FeatureKey, string> = {
  [FEATURES.PLATFORM_ACCESS_FULL]: 'Full M&A Platform Access',
  [FEATURES.COMMUNITY_ESSENTIAL]: 'Essential Community Membership',
  [FEATURES.WEBINARS_MONTHLY]: 'Monthly Networking Webinars',
  [FEATURES.AI_DEAL_ANALYSIS]: 'AI-Powered Deal Analysis',
  [FEATURES.MASTERCLASS_BASIC]: 'Basic Masterclass Library',
  [FEATURES.TEAM_COLLABORATION]: 'Advanced Team Collaboration',
  [FEATURES.COMMUNITY_PROFESSIONAL]: 'Professional Community Membership',
  [FEATURES.EVENTS_VIP_ALL]: 'All Events + VIP Networking',
  [FEATURES.AI_INTRODUCTIONS_PRIORITY]: 'Priority AI-Powered Introductions',
  [FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE]: 'Exclusive Deal Opportunities',
  [FEATURES.MASTERMIND_MONTHLY]: 'Monthly Mastermind Sessions',
  [FEATURES.WHITE_LABEL_PLATFORM]: 'White-Label Platform Access',
  [FEATURES.COMMUNITY_EXECUTIVE]: 'Executive Community Membership',
  [FEATURES.EVENTS_PRIVATE_HOSTING]: 'Private Events + Hosting Rights',
  [FEATURES.CUSTOM_BRANDING_API]: 'Custom Branding & API Access',
  [FEATURES.DEAL_SYNDICATION_DIRECT]: 'Direct Deal Syndication',
  [FEATURES.INVESTMENT_COMMITTEE]: 'Investment Committee Access',
  [FEATURES.DEDICATED_SUPPORT]: 'Dedicated Success Manager',
  [FEATURES.REVENUE_SHARE_EVENTS]: 'Revenue Share on Hosted Events',
  [FEATURES.PERSONAL_SHOWCASE]: 'Personal Deal Showcase Platform',
  [FEATURES.MENTOR_LEADERSHIP]: 'Mentor Program Leadership',
  [FEATURES.LP_INTRODUCTIONS]: 'Direct LP and Investor Introductions',
  [FEATURES.COMMUNITY_INFLUENCE]: 'Community Influence and Recognition',
  [FEATURES.STREAMYARD_STUDIO]: 'StreamYard-Level Studio Access',
};

// Helper function to check if a tier has a specific feature
export function tierHasFeature(tier: TierKey, feature: FeatureKey): boolean {
  return TIER_FEATURES[tier]?.includes(feature) ?? false;
}

// Helper function to get all features for a tier
export function getFeaturesForTier(tier: TierKey): FeatureKey[] {
  return TIER_FEATURES[tier] ?? [];
}

// Helper function to get tier from plan ID
export function getTierFromPlanId(planId: string): TierKey {
  switch (planId) {
    case PLAN_IDS.SOLO_DEALMAKER_MONTHLY:
    case PLAN_IDS.SOLO_DEALMAKER_ANNUAL:
      return TIERS.SOLO_DEALMAKER;

    case PLAN_IDS.GROWTH_FIRM_MONTHLY:
    case PLAN_IDS.GROWTH_FIRM_ANNUAL:
      return TIERS.GROWTH_FIRM;

    case PLAN_IDS.ENTERPRISE_MONTHLY:
    case PLAN_IDS.ENTERPRISE_ANNUAL:
      return TIERS.ENTERPRISE;

    case PLAN_IDS.COMMUNITY_LEADER_MONTHLY:
    case PLAN_IDS.COMMUNITY_LEADER_ANNUAL:
      return TIERS.COMMUNITY_LEADER;

    default:
      return TIERS.FREE;
  }
}

// Pricing information - Updated with correct Clerk pricing
export const PRICING = {
  [TIERS.SOLO_DEALMAKER]: {
    monthly: 279,
    annual: 232.50, // $2,790/year
    annualTotal: 2790,
  },
  [TIERS.GROWTH_FIRM]: {
    monthly: 798,
    annual: 665, // $7,980/year
    annualTotal: 7980,
  },
  [TIERS.ENTERPRISE]: {
    monthly: 1598,
    annual: 1331.67, // $15,980.04/year (note: slight rounding difference)
    annualTotal: 15980.04,
  },
  [TIERS.COMMUNITY_LEADER]: {
    monthly: 2997,
    annual: 2497.50, // $29,970/year
    annualTotal: 29970,
  },
} as const;
