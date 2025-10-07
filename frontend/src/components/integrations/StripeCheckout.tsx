import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  CreditCard,
  Check,
  Loader2,
  ExternalLink,
  AlertCircle,
  Crown,
  Rocket,
  Building2,
  Sparkles
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface PlanFeature {
  name: string;
  included: boolean;
}

interface Plan {
  tier: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: {
    max_deals: number;
    max_users: number;
    max_storage_gb: number;
    ai_credits_per_month: number;
    features: string[];
  };
}

interface Subscription {
  id: number;
  plan_tier: string;
  status: string;
  amount: number;
  currency: string;
  interval: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

const PLAN_ICONS: Record<string, React.ReactNode> = {
  'free': <Sparkles className="h-6 w-6" />,
  'starter': <Rocket className="h-6 w-6" />,
  'professional': <Crown className="h-6 w-6" />,
  'enterprise': <Building2 className="h-6 w-6" />
};

const PLAN_COLORS: Record<string, string> = {
  'free': 'text-gray-600',
  'starter': 'text-blue-600',
  'professional': 'text-purple-600',
  'enterprise': 'text-orange-600'
};

export const StripeCheckout: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/plans`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('clerk_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPlans(data);
      }
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError('Failed to load subscription plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/subscription/current`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('clerk_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (err) {
      console.error('Error fetching subscription:', err);
    }
  };

  const handleCheckout = async (priceId: string, planTier: string) => {
    setCheckoutLoading(planTier);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/payments/checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('clerk_token')}`
        },
        body: JSON.stringify({
          price_id: priceId,
          success_url: `${window.location.origin}/subscription/success`,
          cancel_url: `${window.location.origin}/subscription`,
          mode: 'subscription'
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to Stripe Checkout
        window.location.href = data.session_url;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create checkout session');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handleManageBilling = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/payments/portal-session?return_url=${encodeURIComponent(window.location.href)}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('clerk_token')}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.url;
      } else {
        setError('Failed to open billing portal');
      }
    } catch (err) {
      console.error('Billing portal error:', err);
      setError('An error occurred. Please try again.');
    }
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
      minimumFractionDigits: 0
    }).format(price / 100);
  };

  const isCurrentPlan = (tier: string) => {
    return currentSubscription?.plan_tier === tier;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Subscription Banner */}
      {currentSubscription && (
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Current Subscription</CardTitle>
                <CardDescription>
                  {currentSubscription.plan_tier.charAt(0).toUpperCase() + currentSubscription.plan_tier.slice(1)} Plan
                  {' - '}
                  {formatPrice(currentSubscription.amount, currentSubscription.currency)}/{currentSubscription.interval}
                </CardDescription>
              </div>
              <Button variant="outline" onClick={handleManageBilling}>
                <ExternalLink className="h-4 w-4 mr-2" />
                Manage Billing
              </Button>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Pricing Plans */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((plan) => {
          const isCurrent = isCurrentPlan(plan.tier);
          const isUpgrade = currentSubscription &&
            ['starter', 'professional', 'enterprise'].indexOf(plan.tier) >
            ['free', 'starter', 'professional', 'enterprise'].indexOf(currentSubscription.plan_tier);

          return (
            <Card
              key={plan.tier}
              className={`relative ${isCurrent ? 'ring-2 ring-purple-500 shadow-lg' : ''}`}
            >
              {plan.tier === 'professional' && (
                <div className="absolute -top-3 left-0 right-0 flex justify-center">
                  <Badge className="bg-gradient-to-r from-purple-600 to-blue-600">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader>
                <div className={`mb-4 ${PLAN_COLORS[plan.tier]}`}>
                  {PLAN_ICONS[plan.tier]}
                </div>
                <CardTitle>{plan.name}</CardTitle>
                <div className="flex items-baseline mt-4">
                  <span className="text-4xl font-bold">
                    {formatPrice(plan.price, plan.currency)}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-muted-foreground ml-1">/{plan.interval}</span>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <Check className="h-4 w-4 text-green-600 mr-2" />
                    <span>
                      {plan.features.max_deals === -1 ? 'Unlimited' : plan.features.max_deals} Deals
                    </span>
                  </div>
                  <div className="flex items-center">
                    <Check className="h-4 w-4 text-green-600 mr-2" />
                    <span>
                      {plan.features.max_users === -1 ? 'Unlimited' : plan.features.max_users} Users
                    </span>
                  </div>
                  <div className="flex items-center">
                    <Check className="h-4 w-4 text-green-600 mr-2" />
                    <span>{plan.features.max_storage_gb}GB Storage</span>
                  </div>
                  <div className="flex items-center">
                    <Check className="h-4 w-4 text-green-600 mr-2" />
                    <span>
                      {plan.features.ai_credits_per_month === -1 ? 'Unlimited' : plan.features.ai_credits_per_month} AI Credits
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    {plan.features.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                        <span>{feature.replace(/_/g, ' ')}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>

              <CardFooter>
                {isCurrent ? (
                  <Button className="w-full" variant="outline" disabled>
                    <Check className="h-4 w-4 mr-2" />
                    Current Plan
                  </Button>
                ) : (
                  <Button
                    className="w-full"
                    variant={plan.tier === 'professional' ? 'default' : 'outline'}
                    onClick={() => handleCheckout(`price_${plan.tier}`, plan.tier)}
                    disabled={checkoutLoading === plan.tier || plan.tier === 'free'}
                  >
                    {checkoutLoading === plan.tier ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <CreditCard className="h-4 w-4 mr-2" />
                        {isUpgrade ? 'Upgrade' : plan.tier === 'free' ? 'Free' : 'Subscribe'}
                      </>
                    )}
                  </Button>
                )}
              </CardFooter>
            </Card>
          );
        })}
      </div>

      {/* FAQ or Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle>Subscription Information</CardTitle>
          <CardDescription>
            All plans include 14-day money-back guarantee. Cancel anytime.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>All subscriptions are billed monthly and can be cancelled at any time.</p>
          <p>Enterprise plan includes dedicated support and custom integrations.</p>
          <p>AI credits replenish monthly and do not roll over.</p>
        </CardContent>
      </Card>
    </div>
  );
};
