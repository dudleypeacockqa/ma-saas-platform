import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useUser, SignInButton } from '@clerk/clerk-react'
import { Button } from '@/components/ui/button'
import { 
  Check, 
  X, 
  Star, 
  ArrowRight, 
  Users, 
  Database, 
  Shield, 
  Zap,
  Building2,
  Crown,
  Calculator,
  Phone
} from 'lucide-react'

const PricingPage = () => {
  const [billingCycle, setBillingCycle] = useState('monthly')
  const [selectedPlan, setSelectedPlan] = useState('growth')
  const { isSignedIn, user } = useUser()

  const plans = [
    {
      id: 'solo',
      name: 'Solo Dealmaker',
      description: 'Perfect for individual professionals starting their M&A journey',
      monthlyPrice: 279,
      yearlyPrice: 2790,
      yearlyDiscount: 17,
      popular: false,
      icon: Users,
      color: 'slate',
      clerkPlanId: 'plan_solo_dealmaker', // Clerk subscription plan ID
      stripePriceId: billingCycle === 'monthly' ? 'price_solo_monthly' : 'price_solo_yearly',
      features: {
        core: [
          'Up to 3 team members',
          '10 active deals',
          '50GB storage',
          'Basic analytics',
          'Email support'
        ],
        advanced: [
          'Deal pipeline management',
          'Document storage',
          'Basic reporting',
          'Mobile app access'
        ],
        integrations: [
          'Email integration',
          'Calendar sync',
          'Basic API access'
        ],
        support: [
          'Email support',
          'Knowledge base',
          'Community forum'
        ]
      },
      limitations: [
        'Limited integrations',
        'Basic analytics only',
        'No custom branding'
      ]
    },
    {
      id: 'growth',
      name: 'Growth Firm',
      description: 'For growing M&A teams and mid-size firms',
      monthlyPrice: 798,
      yearlyPrice: 7980,
      yearlyDiscount: 17,
      popular: true,
      icon: Building2,
      color: 'blue',
      clerkPlanId: 'plan_growth_firm',
      stripePriceId: billingCycle === 'monthly' ? 'price_growth_monthly' : 'price_growth_yearly',
      features: {
        core: [
          'Up to 15 team members',
          '50 active deals',
          '200GB storage',
          'Advanced analytics',
          'Priority support'
        ],
        advanced: [
          'Advanced pipeline management',
          'Document collaboration',
          'Custom workflows',
          'Advanced reporting',
          'API access',
          'Mobile app'
        ],
        integrations: [
          'CRM integration',
          'Email & calendar sync',
          'Third-party apps',
          'Webhook support'
        ],
        support: [
          'Priority email support',
          'Phone support',
          'Onboarding assistance',
          'Training sessions'
        ]
      },
      limitations: []
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large firms and investment banks',
      monthlyPrice: 1598,
      yearlyPrice: 15980,
      yearlyDiscount: 17,
      popular: false,
      icon: Crown,
      color: 'purple',
      clerkPlanId: 'plan_enterprise',
      stripePriceId: billingCycle === 'monthly' ? 'price_enterprise_monthly' : 'price_enterprise_yearly',
      features: {
        core: [
          'Unlimited team members',
          'Unlimited deals',
          '1TB storage',
          'Custom analytics',
          'Dedicated support'
        ],
        advanced: [
          'Enterprise pipeline management',
          'Advanced document management',
          'Custom integrations',
          'White-label options',
          'Advanced security',
          'Custom workflows',
          'API & webhooks'
        ],
        integrations: [
          'Custom integrations',
          'Enterprise SSO',
          'Advanced API',
          'Data export tools'
        ],
        support: [
          'Dedicated account manager',
          '24/7 phone support',
          'Custom onboarding',
          'Training & consulting',
          'SLA guarantee'
        ]
      },
      limitations: []
    }
  ]

  const getPrice = (plan) => {
    const price = billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice / 12
    return Math.round(price)
  }

  const getSavings = (plan) => {
    if (billingCycle === 'monthly') return 0
    const monthlyTotal = plan.monthlyPrice * 12
    const yearlyTotal = plan.yearlyPrice
    return monthlyTotal - yearlyTotal
  }

  const handleSubscribe = async (plan) => {
    if (!isSignedIn) {
      // Redirect to sign in if not authenticated
      return
    }

    try {
      // Call your backend API to create Clerk subscription
      const response = await fetch('/api/create-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          planId: plan.clerkPlanId,
          priceId: plan.stripePriceId,
          billingCycle: billingCycle
        }),
      })

      const { checkoutUrl } = await response.json()
      
      // Redirect to Stripe Checkout
      window.location.href = checkoutUrl
    } catch (error) {
      console.error('Subscription error:', error)
      // Handle error (show toast, etc.)
    }
  }

  const featureCategories = [
    { key: 'core', name: 'Core Features', icon: Zap },
    { key: 'advanced', name: 'Advanced Features', icon: Star },
    { key: 'integrations', name: 'Integrations', icon: Database },
    { key: 'support', name: 'Support & Training', icon: Shield }
  ]

  return (
    <div className="min-h-screen bg-white pt-16">
      {/* Header */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Simple, transparent pricing
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-white rounded-xl p-1 shadow-lg border border-slate-200">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                billingCycle === 'monthly'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 relative ${
                billingCycle === 'yearly'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Yearly
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`relative bg-white rounded-2xl border-2 transition-all duration-300 hover:shadow-xl ${
                  plan.popular
                    ? 'border-blue-500 shadow-lg scale-105'
                    : 'border-slate-200 hover:border-slate-300'
                } ${selectedPlan === plan.id ? 'ring-4 ring-blue-200' : ''}`}
                onClick={() => setSelectedPlan(plan.id)}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Header */}
                  <div className="text-center mb-8">
                    <div className={`inline-flex items-center justify-center w-16 h-16 bg-${plan.color}-100 rounded-xl mb-4`}>
                      <plan.icon className={`w-8 h-8 text-${plan.color}-600`} />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                    <p className="text-slate-600">{plan.description}</p>
                  </div>

                  {/* Pricing */}
                  <div className="text-center mb-8">
                    <div className="flex items-baseline justify-center">
                      <span className="text-4xl font-bold text-slate-900">£{getPrice(plan)}</span>
                      <span className="text-slate-600 ml-2">/month</span>
                    </div>
                    {billingCycle === 'yearly' && getSavings(plan) > 0 && (
                      <div className="text-green-600 text-sm font-medium mt-2">
                        Save £{getSavings(plan)} per year
                      </div>
                    )}
                    {billingCycle === 'yearly' && (
                      <div className="text-slate-500 text-sm mt-1">
                        Billed annually (£{plan.yearlyPrice})
                      </div>
                    )}
                  </div>

                  {/* Core Features */}
                  <div className="mb-8">
                    <ul className="space-y-3">
                      {plan.features.core.map((feature) => (
                        <li key={feature} className="flex items-center">
                          <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                          <span className="text-slate-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* CTA Button */}
                  {isSignedIn ? (
                    <Button
                      onClick={() => handleSubscribe(plan)}
                      className={`w-full py-3 text-lg font-semibold rounded-xl transition-all duration-200 ${
                        plan.popular
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-900'
                      }`}
                    >
                      Subscribe Now
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  ) : (
                    <SignInButton mode="modal">
                      <Button
                        className={`w-full py-3 text-lg font-semibold rounded-xl transition-all duration-200 ${
                          plan.popular
                            ? 'bg-blue-600 hover:bg-blue-700 text-white'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-900'
                        }`}
                      >
                        Start Free Trial
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </Button>
                    </SignInButton>
                  )}

                  <div className="text-center mt-4 text-sm text-slate-500">
                    14-day free trial • No credit card required
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Compare all features
            </h2>
            <p className="text-xl text-slate-600">
              See exactly what's included in each plan
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Features</th>
                    {plans.map((plan) => (
                      <th key={plan.id} className="text-center py-4 px-6">
                        <div className="font-semibold text-slate-900">{plan.name}</div>
                        <div className="text-sm text-slate-600 mt-1">
                          £{getPrice(plan)}/month
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {featureCategories.map((category) => (
                    <React.Fragment key={category.key}>
                      <tr className="bg-slate-25">
                        <td colSpan={4} className="py-4 px-6">
                          <div className="flex items-center font-semibold text-slate-900">
                            <category.icon className="w-5 h-5 mr-2 text-blue-600" />
                            {category.name}
                          </div>
                        </td>
                      </tr>
                      {plans[0].features[category.key].map((feature, index) => (
                        <tr key={feature} className="border-b border-slate-100">
                          <td className="py-3 px-6 text-slate-700">{feature}</td>
                          {plans.map((plan) => (
                            <td key={plan.id} className="py-3 px-6 text-center">
                              {plan.features[category.key][index] ? (
                                <Check className="w-5 h-5 text-green-500 mx-auto" />
                              ) : (
                                <X className="w-5 h-5 text-slate-300 mx-auto" />
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Calculator */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Calculate your ROI
            </h2>
            <p className="text-xl text-slate-600">
              See how much time and money you can save with our platform
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 border border-blue-100">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-4">
                  <Calculator className="w-6 h-6 inline mr-2 text-blue-600" />
                  Your Current Process
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Average deal cycle:</span>
                    <span className="font-semibold">180 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Time spent on admin:</span>
                    <span className="font-semibold">40%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Document search time:</span>
                    <span className="font-semibold">2 hours/day</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-4">
                  <Zap className="w-6 h-6 inline mr-2 text-green-600" />
                  With Our Platform
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Average deal cycle:</span>
                    <span className="font-semibold text-green-600">108 days (-40%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Time spent on admin:</span>
                    <span className="font-semibold text-green-600">15% (-62%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Document search time:</span>
                    <span className="font-semibold text-green-600">15 min/day (-87%)</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 p-6 bg-white rounded-xl border border-blue-200">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">£2.4M+</div>
                <div className="text-slate-600">Estimated annual savings for a 10-person team</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to get started?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of M&A professionals who trust our platform
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isSignedIn ? (
              <Link to="/dashboard">
                <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-xl">
                  Go to Dashboard
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            ) : (
              <SignInButton mode="modal">
                <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-xl">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </SignInButton>
            )}
            <Link to="/contact">
              <Button 
                size="lg" 
                variant="outline" 
                className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg font-semibold rounded-xl"
              >
                <Phone className="w-5 h-5 mr-2" />
                Contact Sales
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default PricingPage
