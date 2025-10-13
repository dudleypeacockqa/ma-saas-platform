import { useState } from 'react';
import { PricingTable, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle } from 'lucide-react';
import { FEATURE_DISPLAY_NAMES, FEATURES } from '@/constants/features';

const PricingPage = () => {
  const [billingInterval, setBillingInterval] = useState('monthly'); // 'monthly' or 'yearly'

  // Subscription completion callback for analytics
  const handleSubscriptionComplete = (planName) => {
    console.log(`Subscription completed: ${planName}`);
    // Track conversion in analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'subscription_complete', {
        plan_name: planName,
        billing_interval: billingInterval,
      });
    }
  };

  // Correct pricing structure from Clerk subscription plans
  const pricingInfo = {
    monthly: {
      solo: { price: 279, display: '$279', originalPrice: null },
      growth: { price: 798, display: '$798', originalPrice: null },
      enterprise: { price: 1598, display: '$1,598', originalPrice: null },
      community_leader: { price: 2997, display: '$2,997', originalPrice: null },
    },
    yearly: {
      solo: { price: 2790, display: '$2,790', savings: '$558', originalPrice: 3348 },
      growth: { price: 7980, display: '$7,980', savings: '$1,596', originalPrice: 9576 },
      enterprise: {
        price: 15980.04,
        display: '$15,980',
        savings: '$3,195.96',
        originalPrice: 19176,
      },
      community_leader: {
        price: 29970,
        display: '$29,970',
        savings: '$5,994',
        originalPrice: 35964,
      },
    },
  };

  // Features from CLERK_FEATURE_REGISTRY_MASTER.md
  const features = {
    solo: [
      FEATURE_DISPLAY_NAMES[FEATURES.PLATFORM_ACCESS_FULL],
      FEATURE_DISPLAY_NAMES[FEATURES.COMMUNITY_ESSENTIAL],
      FEATURE_DISPLAY_NAMES[FEATURES.WEBINARS_MONTHLY],
      FEATURE_DISPLAY_NAMES[FEATURES.AI_DEAL_ANALYSIS],
      FEATURE_DISPLAY_NAMES[FEATURES.MASTERCLASS_BASIC],
    ],
    growth: [
      'Everything in Solo Dealmaker',
      FEATURE_DISPLAY_NAMES[FEATURES.TEAM_COLLABORATION],
      FEATURE_DISPLAY_NAMES[FEATURES.COMMUNITY_PROFESSIONAL],
      FEATURE_DISPLAY_NAMES[FEATURES.EVENTS_VIP_ALL],
      FEATURE_DISPLAY_NAMES[FEATURES.AI_INTRODUCTIONS_PRIORITY],
      FEATURE_DISPLAY_NAMES[FEATURES.DEAL_OPPORTUNITIES_EXCLUSIVE],
      FEATURE_DISPLAY_NAMES[FEATURES.MASTERMIND_MONTHLY],
    ],
    enterprise: [
      'Everything in Growth Firm',
      FEATURE_DISPLAY_NAMES[FEATURES.WHITE_LABEL_PLATFORM],
      FEATURE_DISPLAY_NAMES[FEATURES.COMMUNITY_EXECUTIVE],
      FEATURE_DISPLAY_NAMES[FEATURES.EVENTS_PRIVATE_HOSTING],
      FEATURE_DISPLAY_NAMES[FEATURES.CUSTOM_BRANDING_API],
      FEATURE_DISPLAY_NAMES[FEATURES.DEAL_SYNDICATION_DIRECT],
      FEATURE_DISPLAY_NAMES[FEATURES.INVESTMENT_COMMITTEE],
      FEATURE_DISPLAY_NAMES[FEATURES.DEDICATED_SUPPORT],
    ],
    community_leader: [
      'Everything in Enterprise',
      FEATURE_DISPLAY_NAMES[FEATURES.REVENUE_SHARE_EVENTS],
      FEATURE_DISPLAY_NAMES[FEATURES.PERSONAL_SHOWCASE],
      FEATURE_DISPLAY_NAMES[FEATURES.MENTOR_LEADERSHIP],
      FEATURE_DISPLAY_NAMES[FEATURES.LP_INTRODUCTIONS],
      FEATURE_DISPLAY_NAMES[FEATURES.COMMUNITY_INFLUENCE],
      FEATURE_DISPLAY_NAMES[FEATURES.STREAMYARD_STUDIO],
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Build Your £200M M&A Empire
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-2">
            The complete integrated ecosystem: SaaS platform + professional community + premium
            events + podcast empire
          </p>
          <p className="text-lg text-blue-600 dark:text-blue-400 font-semibold mb-2">
            Join 156+ M&A professionals • £47.5k MRR platform • Live & operational
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
        <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-6 mb-12">
          {/* Solo Dealmaker */}
          <Card className="relative border-gray-200 dark:border-gray-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-xl font-bold mb-2">Solo Dealmaker 💼</h3>
                <div className="text-center mb-4">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
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
                  Individual professionals and boutique advisors
                </p>
                <ul className="space-y-2 text-left mb-6">
                  {features.solo.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* Clerk Checkout & Details Buttons */}
                <div className="space-y-3">
                  <SignedIn>
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      onClick={() => (window.location.href = '/dashboard?welcome=true')}
                    >
                      Start Free Trial
                    </Button>
                  </SignedIn>

                  <SignedOut>
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      onClick={() => (window.location.href = '/sign-up')}
                    >
                      Start Free Trial
                    </Button>
                  </SignedOut>

                  <Button variant="outline" className="w-full">
                    View All Features
                  </Button>
                </div>
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
                <h3 className="text-xl font-bold mb-2">Growth Firm 📈</h3>
                <div className="text-center mb-4">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
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
                  Mid-market firms and growing practices
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
                <h3 className="text-xl font-bold mb-2">Enterprise 🏢</h3>
                <div className="text-center mb-4">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
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
                  Large PE firms and investment banks
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

          {/* Community Leader - NEW TIER */}
          <Card className="relative border-purple-500 shadow-xl">
            <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-purple-500">
              Premium
            </Badge>
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-xl font-bold mb-2">Community Leader ⭐</h3>
                <div className="text-center mb-4">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
                    {pricingInfo[billingInterval].community_leader.display}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {billingInterval === 'monthly' ? '/month' : '/year'}
                  </span>
                  {billingInterval === 'yearly' && (
                    <div className="text-sm text-green-600 dark:text-green-400 font-semibold mt-1">
                      Save {pricingInfo.yearly.community_leader.savings}
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  Industry leaders and thought leaders
                </p>
                <ul className="space-y-2 text-left">
                  {features.community_leader.map((feature, i) => (
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
        <div className="mt-16 max-w-6xl mx-auto">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border border-blue-200 dark:border-blue-800 rounded-lg p-8">
            <h3 className="text-2xl font-semibold mb-6 text-center">
              Complete M&A Empire - What's Included in Every Plan
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-blue-600 dark:text-blue-400">
                  🏢 SaaS Platform
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Complete M&A workflow</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">AI-powered analysis</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">14-day free trial</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Real-time analytics</span>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-purple-600 dark:text-purple-400">
                  👥 Professional Community
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">156+ M&A professionals</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Monthly networking events</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Deal flow opportunities</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Mastermind sessions</span>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-green-600 dark:text-green-400">
                  🎙️ Content Empire
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">StreamYard-level studio</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">AI content automation</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Multi-platform streaming</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Thought leadership tools</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-8 text-center">
              <div className="inline-flex items-center space-x-6">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-sm font-medium">£47.5k MRR Live Platform</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-sm font-medium">Cancel Anytime</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span className="text-sm font-medium">Secure Stripe Payments</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ or Contact Section */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Ready to build your £200M M&A empire? Questions about our integrated ecosystem?
          </p>
          <div className="space-y-2">
            <a
              href="mailto:dudley@100daysandbeyond.com"
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium block"
            >
              Contact Dudley Peacock - Platform Founder
            </a>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Personal consultation for Enterprise and Community Leader tiers available
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
