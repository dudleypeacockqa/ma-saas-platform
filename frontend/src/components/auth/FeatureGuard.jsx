import { useUser } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Lock, Crown } from 'lucide-react';

/**
 * FeatureGuard Component
 *
 * Guards features/routes based on subscription permissions using Clerk's has() helper.
 * Can be used for both route protection and inline feature gating.
 *
 * @param {Object} props
 * @param {string} props.permission - Clerk permission to check (e.g., "org:billing:manage")
 * @param {React.ReactNode} props.children - Content to show if user has permission
 * @param {React.ReactNode} props.fallback - Optional custom fallback content
 * @param {boolean} props.redirect - Whether to redirect to upgrade page (default: false)
 * @param {string} props.redirectTo - Path to redirect to (default: "/pricing")
 * @param {boolean} props.showAlert - Whether to show upgrade alert instead of hiding content (default: false)
 *
 * @example
 * // Route protection with redirect
 * <FeatureGuard permission="org:ai_analysis:use" redirect>
 *   <AIAnalysisPage />
 * </FeatureGuard>
 *
 * @example
 * // Inline feature with upgrade alert
 * <FeatureGuard permission="org:advanced_analytics:view" showAlert>
 *   <AdvancedAnalyticsDashboard />
 * </FeatureGuard>
 *
 * @example
 * // Simple feature toggle (hide if no access)
 * <FeatureGuard permission="org:export:unlimited">
 *   <Button>Export All Data</Button>
 * </FeatureGuard>
 */
export const FeatureGuard = ({
  permission,
  children,
  fallback = null,
  redirect = false,
  redirectTo = '/pricing',
  showAlert = false,
}) => {
  const { isLoaded, isSignedIn, user } = useUser();

  // Loading state
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-white" />
      </div>
    );
  }

  // Not signed in
  if (!isSignedIn) {
    if (redirect) {
      return <Navigate to="/sign-in" replace />;
    }
    return fallback;
  }

  // Check permission using Clerk's has() helper
  const hasPermission =
    user?.organizationMemberships?.[0]?.organization?.has?.({ permission }) ?? false;

  // User has permission - render children
  if (hasPermission) {
    return <>{children}</>;
  }

  // User doesn't have permission
  if (redirect) {
    return <Navigate to={redirectTo} replace />;
  }

  if (showAlert) {
    return (
      <div className="p-6">
        <Alert className="border-amber-200 bg-amber-50 dark:bg-amber-950 dark:border-amber-800">
          <div className="flex items-start space-x-3">
            <Lock className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-amber-900 dark:text-amber-100 mb-1">
                Premium Feature
              </h4>
              <AlertDescription className="text-amber-800 dark:text-amber-200 mb-3">
                This feature is available on higher-tier plans. Upgrade your subscription to unlock
                this capability.
              </AlertDescription>
              <Button
                variant="default"
                size="sm"
                className="bg-amber-600 hover:bg-amber-700 text-white"
                onClick={() => (window.location.href = redirectTo)}
              >
                <Crown className="h-4 w-4 mr-2" />
                Upgrade Plan
              </Button>
            </div>
          </div>
        </Alert>
      </div>
    );
  }

  // Return custom fallback or null
  return fallback;
};

/**
 * useFeatureAccess Hook
 *
 * Hook to check feature access in components without rendering guards.
 * Useful for conditional logic, button states, etc.
 *
 * @param {string} permission - Clerk permission to check
 * @returns {Object} { hasAccess: boolean, isLoading: boolean }
 *
 * @example
 * const { hasAccess, isLoading } = useFeatureAccess("org:export:unlimited");
 *
 * return (
 *   <Button disabled={!hasAccess || isLoading}>
 *     {hasAccess ? "Export All" : "Upgrade to Export All"}
 *   </Button>
 * );
 */
export const useFeatureAccess = (permission) => {
  const { isLoaded, isSignedIn, user } = useUser();

  if (!isLoaded) {
    return { hasAccess: false, isLoading: true };
  }

  if (!isSignedIn) {
    return { hasAccess: false, isLoading: false };
  }

  const hasAccess =
    user?.organizationMemberships?.[0]?.organization?.has?.({ permission }) ?? false;

  return { hasAccess, isLoading: false };
};

/**
 * Common Permissions Map
 *
 * Reference for permission strings to use with FeatureGuard.
 * These should match the permissions configured in Clerk Dashboard.
 */
export const PERMISSIONS = {
  // Deal Management
  DEALS_CREATE: 'org:deals:create',
  DEALS_VIEW: 'org:deals:view',
  DEALS_EDIT: 'org:deals:edit',
  DEALS_DELETE: 'org:deals:delete',
  DEALS_UNLIMITED: 'org:deals:unlimited',

  // AI Features
  AI_ANALYSIS: 'org:ai_analysis:use',
  AI_INSIGHTS: 'org:ai_insights:view',
  AI_UNLIMITED: 'org:ai:unlimited',

  // Analytics
  ANALYTICS_BASIC: 'org:analytics:basic',
  ANALYTICS_ADVANCED: 'org:analytics:advanced',
  ANALYTICS_CUSTOM: 'org:analytics:custom',

  // Collaboration
  TEAM_COLLABORATE: 'org:team:collaborate',
  TEAM_UNLIMITED: 'org:team:unlimited',

  // Integrations
  INTEGRATIONS_BASIC: 'org:integrations:basic',
  INTEGRATIONS_CUSTOM: 'org:integrations:custom',
  SSO: 'org:sso:use',

  // Export & Reports
  EXPORT_BASIC: 'org:export:basic',
  EXPORT_UNLIMITED: 'org:export:unlimited',
  REPORTS_GENERATE: 'org:reports:generate',

  // Storage
  STORAGE_BASIC: 'org:storage:50gb',
  STORAGE_MEDIUM: 'org:storage:200gb',
  STORAGE_LARGE: 'org:storage:1tb',

  // Support
  SUPPORT_EMAIL: 'org:support:email',
  SUPPORT_PRIORITY: 'org:support:priority',
  SUPPORT_DEDICATED: 'org:support:dedicated',

  // White Label
  WHITE_LABEL: 'org:white_label:use',

  // Billing
  BILLING_MANAGE: 'org:billing:manage',
};
