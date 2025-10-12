import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { CheckoutButton } from '@/components/billing/CheckoutButton';
import { useSubscription } from '@/hooks/useSubscription';
import { Alert, AlertDescription } from '@/components/ui/alert';

const PricingPage = () => {
  const { subscription, isLoading: subscriptionLoading, error, isCurrentPlan } = useSubscription();
  const pricingPlans = [
    {
      name: 'Solo Dealmaker',
      tier: 'solo_dealmaker',
      price: '$279',
      period: '/month',
      description: 'Perfect for individual professionals starting their M&A journey',
      features: [
        'Up to 3 team members',
        '10 active deals',
        '50GB storage',
        'Basic analytics',
        'Email support',
        'Deal pipeline management',
      ],
      popular: false,
    },
    {
      name: 'Growth Firm',
      tier: 'growth_firm',
      price: '$798',
      period: '/month',
      description: 'For growing M&A teams and mid-size firms',
      features: [
        'Up to 15 team members',
        '50 active deals',
        '200GB storage',
        'Advanced analytics',
        'Priority support',
        'AI-powered insights',
        'Team collaboration tools',
        'Workflow automation',
      ],
      popular: true,
    },
    {
      name: 'Enterprise',
      tier: 'enterprise',
      price: '$1,598',
      period: '/month',
      description: 'For large firms and investment banks',
      features: [
        'Unlimited team members',
        'Unlimited deals',
        '1TB storage',
        'Custom analytics',
        'Dedicated support',
        'White labeling',
        'SSO integration',
        'Custom integrations',
        'Audit logs',
      ],
      popular: false,
    },
  ];

  return (
    <div className="p-8">
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
          Simple, transparent pricing
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Choose the plan that fits your needs. All plans include a 14-day free trial.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="max-w-3xl mx-auto mb-8">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Current Subscription Banner */}
      {subscription && (
        <div className="max-w-3xl mx-auto mb-8">
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg">Current Subscription</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {subscription.plan_tier
                      .split('_')
                      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                      .join(' ')}{' '}
                    Plan
                    {subscription.status === 'trialing' && ' (Trial)'}
                  </p>
                </div>
                {subscription.cancel_at_period_end && (
                  <Badge variant="destructive">Cancels at period end</Badge>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {pricingPlans.map((plan, index) => (
          <Card
            key={index}
            className={`relative h-full ${
              plan.popular
                ? 'border-blue-500 shadow-lg scale-105'
                : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            {plan.popular && (
              <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
                Most Popular
              </Badge>
            )}
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
              <div className="mt-4">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-gray-500 dark:text-gray-400">{plan.period}</span>
              </div>
              <CardDescription className="mt-2">{plan.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                    <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>

              {subscriptionLoading ? (
                <Button className="w-full" disabled>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading...
                </Button>
              ) : (
                <CheckoutButton
                  planName={plan.name}
                  planTier={plan.tier}
                  price={plan.price}
                  interval="month"
                  isCurrentPlan={isCurrentPlan(plan.tier)}
                  variant={plan.popular ? 'default' : 'outline'}
                />
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default PricingPage;
