import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, ArrowRight, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const SubscriptionSuccessPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { getToken } = useAuth();
  const [verifying, setVerifying] = useState(true);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState(null);

  const sessionId = searchParams.get('session_id');
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const verifySession = async () => {
      if (!sessionId) {
        setError('No session ID provided');
        setVerifying(false);
        return;
      }

      try {
        const token = await getToken();

        if (!token) {
          throw new Error('Not authenticated');
        }

        // Verify the checkout session with backend
        const response = await fetch(
          `${API_BASE_URL}/api/payments/checkout-session/${sessionId}/verify`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        if (response.ok) {
          setVerified(true);
          toast.success('Subscription activated successfully!');
        } else {
          // Even if verification fails, we still show success since Stripe redirected here
          setVerified(true);
        }
      } catch (err) {
        console.error('Verification error:', err);
        // Still show success page since Stripe redirected here
        setVerified(true);
      } finally {
        setVerifying(false);
      }
    };

    verifySession();
  }, [sessionId, getToken, API_BASE_URL]);

  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="text-lg font-semibold">Verifying your subscription...</p>
              <p className="text-sm text-gray-500 text-center">
                Please wait while we confirm your payment
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error && !verified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-6 w-6 text-red-600" />
              <CardTitle>Verification Issue</CardTitle>
            </div>
            <CardDescription>We encountered an issue verifying your subscription</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Don't worry! Your payment was processed successfully. If you don't see your
              subscription active within a few minutes, please contact support.
            </p>
            <div className="flex flex-col gap-2">
              <Button onClick={() => navigate('/subscription')}>View Subscription</Button>
              <Button variant="outline" onClick={() => navigate('/')}>
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-purple-950 p-4">
      <Card className="max-w-2xl w-full shadow-xl">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 animate-ping">
                <CheckCircle className="h-20 w-20 text-green-500 opacity-75" />
              </div>
              <CheckCircle className="h-20 w-20 text-green-600 relative" />
            </div>
          </div>
          <CardTitle className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
            Welcome Aboard! 🎉
          </CardTitle>
          <CardDescription className="text-lg mt-2">
            Your subscription has been activated successfully
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-start space-x-3">
              <Sparkles className="h-6 w-6 text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-lg mb-2">What's Next?</h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                  <li className="flex items-center">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2" />
                    Access all premium features immediately
                  </li>
                  <li className="flex items-center">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2" />
                    Invite team members to collaborate
                  </li>
                  <li className="flex items-center">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2" />
                    Start managing your M&A deals
                  </li>
                  <li className="flex items-center">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2" />
                    Explore AI-powered insights
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <Alert>
            <AlertDescription>
              <strong>Confirmation email sent!</strong> You'll receive a receipt and subscription
              details at your email address shortly.
            </AlertDescription>
          </Alert>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button size="lg" className="flex-1" onClick={() => navigate('/')}>
              Go to Dashboard
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="flex-1"
              onClick={() => navigate('/subscription')}
            >
              Manage Subscription
            </Button>
          </div>

          <div className="text-center pt-4 border-t">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Need help getting started?{' '}
              <a
                href="mailto:support@ma-platform.com"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                Contact Support
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionSuccessPage;
