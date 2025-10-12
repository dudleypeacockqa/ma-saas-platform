import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { XCircle, ArrowLeft, HelpCircle, MessageCircle } from 'lucide-react';

const SubscriptionCancelPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <Card className="max-w-2xl w-full">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-orange-100 dark:bg-orange-950 rounded-full">
              <XCircle className="h-16 w-16 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          <CardTitle className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
            Checkout Canceled
          </CardTitle>
          <CardDescription className="text-lg mt-2">
            Your subscription checkout was not completed
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert>
            <AlertDescription>
              No charges were made to your account. You can return to pricing and try again whenever
              you're ready.
            </AlertDescription>
          </Alert>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 className="font-semibold text-lg mb-3 flex items-center">
              <HelpCircle className="h-5 w-5 mr-2 text-blue-600 dark:text-blue-400" />
              Common Questions
            </h3>
            <div className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Can I try a different plan?
                </p>
                <p>
                  Yes! You can return to the pricing page and select any plan that fits your needs.
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Is there a free trial?</p>
                <p>
                  All our plans include a 14-day free trial. You won't be charged until the trial
                  ends.
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Can I cancel anytime?</p>
                <p>
                  Absolutely! You can cancel your subscription at any time from the billing portal.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <Button size="lg" className="flex-1" onClick={() => navigate('/pricing')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Pricing
              </Button>
              <Button size="lg" variant="outline" className="flex-1" onClick={() => navigate('/')}>
                Go to Dashboard
              </Button>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg border">
            <div className="flex items-start space-x-3">
              <MessageCircle className="h-6 w-6 text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-lg mb-2">Need Help Choosing?</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                  Our team is here to help you find the perfect plan for your needs. We can answer
                  questions about features, pricing, or help with technical issues.
                </p>
                <Button
                  variant="outline"
                  onClick={() => (window.location.href = 'mailto:support@ma-platform.com')}
                >
                  Contact Support
                </Button>
              </div>
            </div>
          </div>

          <div className="text-center pt-4 border-t">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Questions about our pricing or features?{' '}
              <button
                onClick={() => navigate('/pricing')}
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                View detailed plan comparison
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionCancelPage;
