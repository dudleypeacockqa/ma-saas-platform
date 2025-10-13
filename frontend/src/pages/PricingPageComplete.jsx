import { useState } from 'react';
import { PricingTable } from '@clerk/clerk-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Crown, Zap, Building2, Users } from 'lucide-react';

const PricingPageComplete = () => {
  const [billingInterval, setBillingInterval] = useState('monthly'); // 'monthly' or 'yearly'

  // Actual pricing from Clerk plans
  const pricingInfo = {
    monthly: {
      solo: { price: 279, display: '$279', planId: 'cplan_340…Nm3k5AOIb' },
      growth: { price: 798, display: '$798', planId: 'cplan_340…GsAT2Ch6t' },
      enterprise: { price: 1598, display: '$1,598', planId: 'cplan_340…gLX8XLUMd' },
      community: { price: 2997, display: '$2,997', planId: 'cplan_340…4f88Hi6fU' },
    },
    yearly: {
      solo: {
        price: 2790,
        display: '$2,790',
        monthly: '$232.50',
        savings: '$558',
        planId: 'cplan_340…P2yr6bRYq',
      },
      growth: {
        price: 7980,
        display: '$7,980',
        monthly: '$665',
        savings: '$1,596',
        planId: 'cplan_340…J0FWGfMvI',
      },
      enterprise: {
        price: 15980,
        display: '$15,980',
        monthly: '$1,331.67',
        savings: '$3,196',
        planId: 'cplan_340…Qh256zZRl',
      },
      community: {
        price: 29970,
        display: '$29,970',
        monthly: '$2,497.50',
        savings: '$5,994',
        planId: 'cplan_340…xSdbE7elf',
      },
    },
  };

  // Actual features from Clerk plans
  const features = {
    solo: [
      'Full M&A Platform Access',
      'Essential Community Membership',
      'Monthly Networking Webinars',
      'AI-Powered Deal Analysis',
      'Basic Masterclass Library',
    ],
    growth: [
      'Everything in Solo Dealmaker',
      'Advanced Team Collaboration',
      'Professional Community Membership',
      'All Events + VIP Networking',
      'Priority AI-Powered Introductions',
      'Exclusive Deal Opportunities',
      'Monthly Mastermind Sessions',
    ],
    enterprise: [
      'Everything in Growth Firm',
      'White-Label Platform Access',
      'Executive Community Membership',
      'Private Events + Hosting Rights',
      'Custom Branding & API Access',
      'Direct Deal Syndication',
      'Investment Committee Access',
    ],
    community: [
      'Everything in Enterprise',
      'Revenue Share on Hosted Events (20%)',
      'Personal Deal Showcase Platform',
      'Mentor Program Leadership',
      'Direct LP and Investor Introductions',
      'Community Influence and Recognition',
    ],
  };

  const tierIcons = {
    solo: <Zap className="h-6 w-6" />,
    growth: <Building2 className="h-6 w-6" />,
    enterprise: <Users className="h-6 w-6" />,
    community: <Crown className="h-6 w-6" />,
  };

  const tierDescriptions = {
    solo: 'Perfect for individual M&A professionals',
    growth: 'For growing M&A teams and advisors',
    enterprise: 'White-label solutions for large firms',
    community: 'Premium tier with revenue sharing & leadership',
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Choose Your M&A Success Plan
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-2">
            Integrated SaaS + Community + Events ecosystem. All plans include a 14-day free trial.
          </p>
          <p className="text-lg text-green-600 dark:text-green-400 font-semibold">
            💰 Save 17% with annual billing (~2 months free)
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

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-8 mb-12">
          {/* Solo Dealmaker */}
          <Card className="relative border-gray-200 dark:border-gray-700 hover:border-blue-300 transition-all">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="flex justify-center items-center mb-3 text-blue-600 dark:text-blue-400">
                  {tierIcons.solo}
                </div>
                <h3 className="text-2xl font-bold mb-2">Solo Dealmaker</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {billingInterval === 'monthly'
                      ? pricingInfo.monthly.solo.display
                      : pricingInfo.yearly.solo.monthly}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">/month</span>
                  {billingInterval === 'yearly' && (
                    <div className="mt-2">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Billed as {pricingInfo.yearly.solo.display}/year
                      </div>
                      <div className="text-sm text-green-600 dark:text-green-400 font-semibold">
                        💰 Save {pricingInfo.yearly.solo.savings} annually
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  {tierDescriptions.solo}
                </p>
                <ul className="space-y-2 text-left mb-6">
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
          <Card className="relative border-blue-500 shadow-xl lg:scale-105 z-10">
            <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
              Most Popular
            </Badge>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="flex justify-center items-center mb-3 text-blue-600 dark:text-blue-400">
                  {tierIcons.growth}
                </div>
                <h3 className="text-2xl font-bold mb-2">Growth Firm</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {billingInterval === 'monthly'
                      ? pricingInfo.monthly.growth.display
                      : pricingInfo.yearly.growth.monthly}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">/month</span>
                  {billingInterval === 'yearly' && (
                    <div className="mt-2">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Billed as {pricingInfo.yearly.growth.display}/year
                      </div>
                      <div className="text-sm text-green-600 dark:text-green-400 font-semibold">
                        💰 Save {pricingInfo.yearly.growth.savings} annually
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  {tierDescriptions.growth}
                </p>
                <ul className="space-y-2 text-left mb-6">
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
          <Card className="relative border-gray-200 dark:border-gray-700 hover:border-purple-300 transition-all">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="flex justify-center items-center mb-3 text-purple-600 dark:text-purple-400">
                  {tierIcons.enterprise}
                </div>
                <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {billingInterval === 'monthly'
                      ? pricingInfo.monthly.enterprise.display
                      : pricingInfo.yearly.enterprise.monthly}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">/month</span>
                  {billingInterval === 'yearly' && (
                    <div className="mt-2">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Billed as {pricingInfo.yearly.enterprise.display}/year
                      </div>
                      <div className="text-sm text-green-600 dark:text-green-400 font-semibold">
                        💰 Save {pricingInfo.yearly.enterprise.savings} annually
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  {tierDescriptions.enterprise}
                </p>
                <ul className="space-y-2 text-left mb-6">
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

          {/* Community Leader */}
          <Card className="relative border-amber-500 shadow-xl lg:scale-105 bg-gradient-to-br from-amber-50 to-white dark:from-amber-950 dark:to-gray-900">
            <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-500 to-orange-500">
              👑 Premium
            </Badge>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="flex justify-center items-center mb-3 text-amber-600 dark:text-amber-400">
                  {tierIcons.community}
                </div>
                <h3 className="text-2xl font-bold mb-2">Community Leader</h3>
                <div className="text-center mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    {billingInterval === 'monthly'
                      ? pricingInfo.monthly.community.display
                      : pricingInfo.yearly.community.monthly}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">/month</span>
                  {billingInterval === 'yearly' && (
                    <div className="mt-2">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Billed as {pricingInfo.yearly.community.display}/year
                      </div>
                      <div className="text-sm text-green-600 dark:text-green-400 font-semibold">
                        💰 Save {pricingInfo.yearly.community.savings} annually
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  {tierDescriptions.community}
                </p>
                <ul className="space-y-2 text-left mb-6">
                  {features.community.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-amber-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Clerk Pricing Table (for actual subscription buttons) */}
        <div className="max-w-7xl mx-auto mb-12">
          <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
            <p className="text-center text-sm text-gray-600 dark:text-gray-300">
              👇 Click the Subscribe button below to start your 14-day free trial
            </p>
          </div>
          <PricingTable
            appearance={{
              elements: {
                card: 'transition-all hover:shadow-lg border-2',
                cardHeader: 'text-center pb-4',
                priceText: 'text-3xl font-bold',
                intervalText: 'text-gray-500',
                featuresContainer: 'space-y-3 my-6',
                featureItem: 'flex items-start text-sm',
                subscribeButton:
                  'w-full py-3 rounded-md font-semibold transition-all hover:scale-105',
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
          <div className="bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-950 dark:to-green-950 border border-blue-200 dark:border-blue-800 rounded-lg p-8">
            <h3 className="text-2xl font-semibold mb-6 text-center">
              What's included in all plans?
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">14-day free trial (no credit card required)</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">Cancel anytime, no questions asked</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">Secure payment processing by Stripe</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">No setup or hidden fees</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">Instant access to all plan features</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <span className="font-medium">Easy upgrade or downgrade anytime</span>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ or Contact Section */}
        <div className="mt-12 text-center">
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
            Need help choosing a plan or have questions about Enterprise/Community Leader tiers?
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="mailto:support@100daysandbeyond.com"
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium text-lg"
            >
              📧 Contact Sales Team
            </a>
            <span className="text-gray-400">|</span>
            <a
              href="/schedule-demo"
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium text-lg"
            >
              📅 Schedule a Demo
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPageComplete;
