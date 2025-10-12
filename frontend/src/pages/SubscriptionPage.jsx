import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { SubscriptionManager } from '@/components/billing/SubscriptionManager';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { useSubscription } from '@/hooks/useSubscription';
import { useEffect } from 'react';

const SubscriptionPage = () => {
  const navigate = useNavigate();
  const { isSignedIn, isLoaded } = useUser();
  const { hasActiveSubscription } = useSubscription();

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      navigate('/sign-in');
    }
  }, [isSignedIn, isLoaded, navigate]);

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Button variant="ghost" onClick={() => navigate('/')} className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
              Subscription Management
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2">
              Manage your subscription, billing, and plan features
            </p>
          </div>
        </div>

        {/* Main Content */}
        <SubscriptionManager />

        {/* Upgrade CTA */}
        {hasActiveSubscription && (
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border-blue-200">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Sparkles className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <CardTitle>Looking for more features?</CardTitle>
              </div>
              <CardDescription>
                Upgrade your plan to unlock advanced capabilities and scale your M&A operations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => navigate('/pricing')} variant="default">
                View All Plans
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Help Section */}
        <Card>
          <CardHeader>
            <CardTitle>Need Help?</CardTitle>
            <CardDescription>Have questions about your subscription or billing?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Our support team is here to help you with any questions about your subscription,
              billing, or account management.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                onClick={() => (window.location.href = 'mailto:support@ma-platform.com')}
              >
                Contact Support
              </Button>
              <Button variant="outline" onClick={() => navigate('/pricing')}>
                View Pricing Plans
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SubscriptionPage;
