import { useState } from 'react';
import { PricingTable } from '@clerk/clerk-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle } from 'lucide-react';

const PricingPage = () => {
  const [billingInterval, setBillingInterval] = useState('monthly'); // 'monthly' or 'yearly'

  // Pricing information for display
  const pricingInfo = {
    monthly: {
      solo: { price: 279, display: '$279' },
      growth: { price: 798, display: '$798' },
      enterprise: { price: 1598, display: '$1,598' },
    },
    yearly: {
      solo: { price: 2790, display: '$2,790', savings: '$558' },
      growth: { price: 7980, display: '$7,980', savings: '$1,596' },
      enterprise: { price: 15980, display: '$15,980', savings: '$3,196' },
    },
  };

  const features = {
    solo: [
      'Up to 3 team members',
      '10 active deals',
      '50GB storage',
      'Basic analytics',
      'Email support',
      'Deal pipeline management',
      'Document management',
    ],
    growth: [
      'Up to 15 team members',
      '50 active deals',
      '200GB storage',
      'Advanced analytics',
      'Priority support',
      'AI-powered insights',
      'Team collaboration tools',
      'Workflow automation',
      'Due diligence management',
    ],
    enterprise: [
      'Unlimited team members',
      'Unlimited deals',
      '1TB storage',
      'Custom analytics',
      'Dedicated support',
      'White labeling',
      'SSO integration',
      'Custom integrations',
      'Audit logs',
      'Advanced security features',
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-2">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
          <p className="text-lg text-green-600 dark:text-green-400 font-semibold">
            Save 17% with annual billing (~2 months free)
          </p>
        </div>

        {/* Billing Interval Toggle */}
        <div className="flex justify-center mb-12">
          <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1 inline-flex">
            <button
              onClick={() => setBillingInterval('monthly')}
              className={`px-6 py-3 rounded-md font-medium transition-all ${
                billingInterval === 'monthly'
                  ? 'bg-white dark:bg-gray-700 shadow-md text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingInterval('yearly')}
              className={`px-6 py-3 rounded-md font-medium transition-all relative ${
                billingInterval === 'yearly'
                  ? 'bg-white dark:bg-gray-700 shadow-md text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Annual
              <span className="ml-2 text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded-full font-semibold">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* Custom Pricing Preview (Above Clerk's PricingTable) */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Solo Dealmaker */}
          <Card className="relative border-gray-200 dark:border-gray-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Solo Dealmaker</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {pricingInfo[billingInterval].solo.display}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {billingInterval === 'monthly' ? '/month' : '/year'}
                  </span>
                  {billingInterval === 'yearly' && (
                    <div className="text-sm text-green-600 dark:text-green-400 font-semibold mt-1">
                      Save {pricingInfo.yearly.solo.savings}
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  Perfect for individual professionals starting their M&A journey
                </p>
                <ul className="space-y-2 text-left">
                  {features.solo.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Growth Firm */}
          <Card className="relative border-blue-500 shadow-xl scale-105 z-10">
            <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
              Most Popular
            </Badge>
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Growth Firm</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {pricingInfo[billingInterval].growth.display}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {billingInterval === 'monthly' ? '/month' : '/year'}
                  </span>
                  {billingInterval === 'yearly' && (
                    <div className="text-sm text-green-600 dark:text-green-400 font-semibold mt-1">
                      Save {pricingInfo.yearly.growth.savings}
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  For growing M&A teams and mid-size firms
                </p>
                <ul className="space-y-2 text-left">
                  {features.growth.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Enterprise */}
          <Card className="relative border-gray-200 dark:border-gray-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {pricingInfo[billingInterval].enterprise.display}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {billingInterval === 'monthly' ? '/month' : '/year'}
                  </span>
                  {billingInterval === 'yearly' && (
                    <div className="text-sm text-green-600 dark:text-green-400 font-semibold mt-1">
                      Save {pricingInfo.yearly.enterprise.savings}
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  For large firms and investment banks
                </p>
                <ul className="space-y-2 text-left">
                  {features.enterprise.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Clerk Pricing Table */}
        <div className="max-w-6xl mx-auto">
          <PricingTable
            appearance={{
              elements: {
                card: 'transition-all hover:shadow-lg',
                cardHeader: 'text-center pb-4',
                priceText: 'text-3xl font-bold',
                intervalText: 'text-gray-500',
                featuresContainer: 'space-y-3 my-6',
                featureItem: 'flex items-start text-sm',
                subscribeButton: 'w-full py-3 rounded-md font-semibold transition-all',
              },
              variables: {
                colorPrimary: '#3b82f6',
                colorSuccess: '#10b981',
                colorDanger: '#ef4444',
                fontFamily: 'Inter, system-ui, sans-serif',
              },
            }}
          />
        </div>

        {/* Additional Information */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-center">
              What's included in all plans?
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">14-day free trial</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">Cancel anytime</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">Secure payment by Stripe</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">No setup fees</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">Instant access to all features</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm">Easy upgrade or downgrade</span>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ or Contact Section */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Need help choosing a plan or have questions?
          </p>
          <a
            href="mailto:support@ma-platform.com"
            className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
          >
            Contact our sales team
          </a>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
