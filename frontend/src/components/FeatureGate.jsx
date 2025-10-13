import { Lock, Crown, Zap } from 'lucide-react';
import { useSubscription } from '@/hooks/useSubscription';
import { Link } from 'react-router-dom';

/**
 * FeatureGate Component
 * Conditionally renders children based on subscription feature access
 *
 * @param {string} feature - Feature name to check (e.g., 'ai_analysis')
 * @param {string} requiredTier - Minimum tier required (e.g., 'growth_firm')
 * @param {React.ReactNode} children - Content to render if user has access
 * @param {React.ReactNode} fallback - Custom fallback component
 * @param {boolean} showUpgrade - Whether to show upgrade prompt (default: true)
 */
export function FeatureGate({ feature, requiredTier, children, fallback, showUpgrade = true }) {
  const { features, tierChecks, isLoading } = useSubscription();

  // While loading, show nothing or a loading state
  if (isLoading) {
    return <div className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg h-32"></div>;
  }

  // Check feature access
  const hasAccess = feature
    ? features.hasFeature(feature)
    : checkTierAccess(tierChecks, requiredTier);

  if (hasAccess) {
    return <>{children}</>;
  }

  // If custom fallback provided, use it
  if (fallback) {
    return <>{fallback}</>;
  }

  // Default locked state
  if (!showUpgrade) {
    return null;
  }

  return <FeatureLockedMessage feature={feature} requiredTier={requiredTier} />;
}

/**
 * Check if user's tier meets the required tier
 */
function checkTierAccess(tierChecks, requiredTier) {
  const tierHierarchy = ['solo_dealmaker', 'growth_firm', 'enterprise', 'community_leader'];
  const userTierIndex = Object.keys(tierChecks).findIndex(
    (key) => tierChecks[key] && key !== 'isFree',
  );
  const requiredTierIndex = tierHierarchy.indexOf(requiredTier);

  return userTierIndex >= requiredTierIndex;
}

/**
 * FeatureLockedMessage Component
 * Default UI for locked features
 */
function FeatureLockedMessage({ feature, requiredTier }) {
  const tierNames = {
    solo_dealmaker: 'Solo Dealmaker',
    growth_firm: 'Growth Firm',
    enterprise: 'Enterprise',
    community_leader: 'Community Leader',
  };

  return (
    <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center bg-gray-50 dark:bg-gray-800/50">
      <div className="flex justify-center mb-4">
        <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-4">
          <Lock className="h-8 w-8 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        Premium Feature Locked
      </h3>
      <p className="text-gray-600 dark:text-gray-300 mb-4">
        {requiredTier
          ? `Upgrade to ${tierNames[requiredTier]} or higher to unlock this feature.`
          : 'This feature requires a paid subscription.'}
      </p>
      <div className="flex gap-3 justify-center">
        <Link
          to="/pricing"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors inline-flex items-center gap-2"
        >
          <Crown className="h-5 w-5" />
          View Plans & Upgrade
        </Link>
      </div>
    </div>
  );
}

/**
 * FeatureBadge Component
 * Shows a badge for features that require upgrade
 */
export function FeatureBadge({ feature, requiredTier, inline = false }) {
  const { features, tierChecks } = useSubscription();

  const hasAccess = feature
    ? features.hasFeature(feature)
    : checkTierAccess(tierChecks, requiredTier);

  if (hasAccess) {
    return null;
  }

  if (inline) {
    return (
      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        <Lock className="h-3 w-3 mr-1" />
        Pro
      </span>
    );
  }

  return (
    <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
      <Crown className="h-4 w-4 mr-1" />
      Premium Feature
    </div>
  );
}

/**
 * SubscriptionTierBadge Component
 * Displays user's current subscription tier
 */
export function SubscriptionTierBadge() {
  const { tier, status } = useSubscription();

  if (!tier || tier === 'free') {
    return null;
  }

  const tierConfig = {
    solo_dealmaker: {
      label: 'Solo Dealmaker',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      icon: '⚡',
    },
    growth_firm: {
      label: 'Growth Firm',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      icon: '🏢',
    },
    enterprise: {
      label: 'Enterprise',
      color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      icon: '👥',
    },
    community_leader: {
      label: 'Community Leader',
      color:
        'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-800 dark:from-amber-900 dark:to-orange-900 dark:text-amber-200',
      icon: '👑',
    },
  };

  const config = tierConfig[tier];

  return (
    <div
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}
    >
      <span className="mr-1">{config.icon}</span>
      {config.label}
      {status.isTrialing && (
        <span className="ml-2 text-xs bg-white dark:bg-gray-800 px-2 py-0.5 rounded">Trial</span>
      )}
    </div>
  );
}

/**
 * UpgradePrompt Component
 * Inline prompt to upgrade to access a feature
 */
export function UpgradePrompt({ feature, requiredTier, message, className = '' }) {
  const { features, tierChecks } = useSubscription();

  const hasAccess = feature
    ? features.hasFeature(feature)
    : checkTierAccess(tierChecks, requiredTier);

  if (hasAccess) {
    return null;
  }

  const tierNames = {
    solo_dealmaker: 'Solo Dealmaker',
    growth_firm: 'Growth Firm',
    enterprise: 'Enterprise',
    community_leader: 'Community Leader',
  };

  return (
    <div
      className={`bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start">
        <Zap className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
            {message || `Upgrade to ${tierNames[requiredTier]} to unlock this feature.`}
          </p>
          <Link
            to="/pricing"
            className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
          >
            View Pricing Plans →
          </Link>
        </div>
      </div>
    </div>
  );
}

export default FeatureGate;
