import { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CreditCard, Calendar, DollarSign, Users, Database, Zap, AlertCircle, ExternalLink } from 'lucide-react';
import { useSubscription, Subscription } from '@/hooks/useSubscription';
import { toast } from 'sonner';
import { format } from 'date-fns';

export const SubscriptionManager = () => {
  const { getToken } = useAuth();
  const { subscription, isLoading, error, hasActiveSubscription } = useSubscription();
  const [portalLoading, setPortalLoading] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleManageBilling = async () => {
    setPortalLoading(true);

    try {
      const token = await getToken();

      if (!token) {
        toast.error('Authentication failed. Please sign in again.');
        return;
      }

      // Create portal session
      const response = await fetch(`${API_BASE_URL}/api/payments/portal-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          return_url: `${window.location.origin}/subscription`
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create portal session');
      }

      const data = await response.json();

      // Redirect to Stripe Customer Portal
      if (data.portal_url) {
        window.location.href = data.portal_url;
      } else {
        throw new Error('No portal URL received');
      }

    } catch (error) {
      console.error('Portal error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to open billing portal. Please try again.');
      setPortalLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline', label: string }> = {
      active: { variant: 'default', label: 'Active' },
      trialing: { variant: 'secondary', label: 'Trial' },
      past_due: { variant: 'destructive', label: 'Past Due' },
      canceled: { variant: 'destructive', label: 'Canceled' },
      incomplete: { variant: 'outline', label: 'Incomplete' },
      incomplete_expired: { variant: 'destructive', label: 'Expired' },
      unpaid: { variant: 'destructive', label: 'Unpaid' }
    };

    const config = statusConfig[status] || { variant: 'outline' as const, label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const formatPlanName = (planTier: string): string => {
    return planTier.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!hasActiveSubscription || !subscription) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Active Subscription</CardTitle>
          <CardDescription>
            You don't have an active subscription yet. Choose a plan to get started.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => window.location.href = '/pricing'}>
            View Pricing Plans
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Subscription Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">
                {formatPlanName(subscription.plan_tier)} Plan
              </CardTitle>
              <CardDescription className="mt-2">
                Manage your subscription and billing information
              </CardDescription>
            </div>
            {getStatusBadge(subscription.status)}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Billing Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <DollarSign className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Amount</p>
                <p className="font-semibold">
                  ${(subscription.amount / 100).toFixed(2)} {subscription.currency.toUpperCase()}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-50 dark:bg-green-950 rounded-lg">
                <Calendar className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Billing Cycle</p>
                <p className="font-semibold capitalize">{subscription.interval}ly</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-50 dark:bg-purple-950 rounded-lg">
                <CreditCard className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Next Billing</p>
                <p className="font-semibold">
                  {format(new Date(subscription.current_period_end), 'MMM d, yyyy')}
                </p>
              </div>
            </div>
          </div>

          {/* Cancellation Warning */}
          {subscription.cancel_at_period_end && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Your subscription will be canceled on {format(new Date(subscription.current_period_end), 'MMMM d, yyyy')}.
                You'll continue to have access until then.
              </AlertDescription>
            </Alert>
          )}

          {/* Manage Button */}
          <Button
            onClick={handleManageBilling}
            disabled={portalLoading}
            className="w-full md:w-auto"
            size="lg"
          >
            {portalLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Opening Portal...
              </>
            ) : (
              <>
                <ExternalLink className="h-4 w-4 mr-2" />
                Manage Billing
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Plan Features */}
      <Card>
        <CardHeader>
          <CardTitle>Plan Features</CardTitle>
          <CardDescription>Your current plan includes the following</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Team Members</p>
                <p className="font-semibold">
                  {subscription.features.max_users === -1
                    ? 'Unlimited'
                    : `Up to ${subscription.features.max_users}`}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Database className="h-5 w-5 text-green-600 dark:text-green-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Active Deals</p>
                <p className="font-semibold">
                  {subscription.features.max_deals === -1
                    ? 'Unlimited'
                    : `Up to ${subscription.features.max_deals}`}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Database className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Storage</p>
                <p className="font-semibold">
                  {subscription.features.max_storage_gb === -1
                    ? 'Unlimited'
                    : `${subscription.features.max_storage_gb} GB`}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Zap className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI Credits</p>
                <p className="font-semibold">
                  {subscription.features.ai_credits_per_month === -1
                    ? 'Unlimited'
                    : `${subscription.features.ai_credits_per_month}/month`}
                </p>
              </div>
            </div>
          </div>

          {subscription.features.features && subscription.features.features.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Additional Features</h4>
              <ul className="space-y-2">
                {subscription.features.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionManager;
