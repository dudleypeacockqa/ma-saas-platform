# 🌟 BMAD v6 World-Class Website Development Prompts

**Date:** 2025-10-14  
**Objective:** Create enterprise-level, irresistible, high-converting website using BMAD methodology  
**Target:** Professional multi-page website that converts visitors to paying customers  
**Documentation:** Integrated with `C:\Projects\ma-saas-platform\docs\stories`  

---

## 🎯 **PROMPT 1: Complete E1.P0.003 - Subscription Selection Enhancement**

```bash
# BMAD v6 Sprint 1 Completion - E1.P0.003 Subscription Selection
# Objective: Complete subscription selection with world-class UI/UX
# Expected Output: Production-ready subscription interface with enterprise-level design

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
import os
from pathlib import Path
from datetime import datetime

print("🎯 BMAD v6 E1.P0.003 - World-Class Subscription Selection")
print("=" * 70)

# Create story documentation
docs_dir = Path("docs/stories")
docs_dir.mkdir(parents=True, exist_ok=True)

story_doc = f"""# E1.P0.003 - Subscription Selection Interface

## 🎯 Story Context
**Epic:** Revenue Generation  
**Priority:** P0 - CRITICAL  
**Size:** L (3-4 days)  
**Status:** 80% Complete → 100% Complete  
**Sprint:** 1 (Week 1)  

## 👤 User Story
**As a** registered user ready to subscribe  
**I want** to select and purchase a subscription plan with enterprise-level experience  
**So that** I can access premium features and the company generates revenue  

## ✅ Acceptance Criteria
**Given** I am logged in and want to upgrade my account  
**When** I select a subscription plan and complete payment  
**Then** My account is upgraded with world-class user experience  

**And:**
- Pricing plans displayed with enterprise-level design
- Payment processing is secure, fast, and intuitive
- Subscription status updated immediately with confirmation
- User receives professional confirmation email
- Mobile-responsive design with premium feel
- Trust signals and security badges prominently displayed

## 🎨 World-Class Design Requirements

### **Enterprise-Level Visual Standards:**
- Premium color gradients signaling high-value tech platform
- Elegant typography pairing (primary + accent fonts)
- Data-driven iconography with subtle motion effects
- Professional spacing and visual hierarchy
- Trust badges and security certifications
- Social proof integration (testimonials, user counts)

### **Conversion Optimization:**
- Clear value proposition for each tier
- Feature comparison matrix with visual emphasis
- Urgency elements (limited-time offers, popular badges)
- Risk reversal (money-back guarantee, free trial)
- Multiple payment options (annual discount emphasis)
- Exit-intent capture with special offers

### **Technical Excellence:**
- Sub-3 second page load time
- Smooth animations and micro-interactions
- Accessibility compliance (WCAG AA)
- Cross-browser compatibility
- Mobile-first responsive design
- Analytics tracking for conversion optimization

## 🔧 Implementation Steps

### Step 1: Enhanced Pricing Page Design
```bash
# Create world-class pricing components
cd frontend/src/components/pricing

# Create PricingHero component
cat > PricingHero.jsx << 'COMPONENT'
import React from 'react';
import { motion } from 'framer-motion';

const PricingHero = () => {
  return (
    <motion.section 
      className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.h1 
          className="text-5xl md:text-6xl font-bold text-white mb-6"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
        >
          Choose Your <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Success Plan</span>
        </motion.h1>
        <motion.p 
          className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          Join 10,000+ M&A professionals who trust our platform for deal intelligence, 
          network access, and revenue acceleration
        </motion.p>
        <motion.div 
          className="flex justify-center items-center space-x-8 text-gray-400"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
        >
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            30-Day Money Back Guarantee
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Enterprise Security
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            24/7 Expert Support
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
};

export default PricingHero;
COMPONENT

# Create PricingCards component with enterprise design
cat > PricingCards.jsx << 'COMPONENT'
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useUser } from '@clerk/clerk-react';

const PricingCards = () => {
  const { user } = useUser();
  const [billingCycle, setBillingCycle] = useState('annual');
  
  const plans = [
    {
      name: "Professional",
      price: { monthly: 279, annual: 2790 },
      description: "Perfect for solo M&A professionals and boutique firms",
      features: [
        "AI-Powered Deal Analysis",
        "Market Intelligence Dashboard", 
        "Document Management Suite",
        "Basic Network Access",
        "Email Support",
        "Mobile App Access"
      ],
      cta: "Start Free Trial",
      popular: false,
      color: "from-blue-500 to-blue-600"
    },
    {
      name: "Enterprise",
      price: { monthly: 799, annual: 7990 },
      description: "Advanced features for growing M&A teams",
      features: [
        "Everything in Professional",
        "Advanced AI Valuation Models",
        "Team Collaboration Tools",
        "Priority Network Access",
        "Custom Integrations",
        "Dedicated Account Manager",
        "Advanced Analytics",
        "White-label Options"
      ],
      cta: "Start Free Trial",
      popular: true,
      color: "from-purple-500 to-purple-600"
    },
    {
      name: "Elite",
      price: { monthly: 1598, annual: 15980 },
      description: "Premium solution for enterprise M&A operations",
      features: [
        "Everything in Enterprise",
        "Concierge Deal Services",
        "Exclusive Event Access",
        "Custom AI Model Training",
        "24/7 Priority Support",
        "On-site Training",
        "Custom Development",
        "Strategic Advisory Access"
      ],
      cta: "Contact Sales",
      popular: false,
      color: "from-gold-500 to-gold-600"
    }
  ];

  const handleSubscribe = async (plan) => {
    // Integration with Clerk checkout
    try {
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planName: plan.name,
          billingCycle,
          userId: user?.id
        })
      });
      
      const { url } = await response.json();
      window.location.href = url;
    } catch (error) {
      console.error('Checkout error:', error);
    }
  };

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Billing Toggle */}
        <div className="flex justify-center mb-12">
          <div className="bg-white p-1 rounded-lg shadow-lg">
            <button
              className={`px-6 py-2 rounded-md transition-all duration-200 $${
                billingCycle === 'monthly' 
                  ? 'bg-blue-500 text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              onClick={() => setBillingCycle('monthly')}
            >
              Monthly
            </button>
            <button
              className={`px-6 py-2 rounded-md transition-all duration-200 relative $${
                billingCycle === 'annual' 
                  ? 'bg-blue-500 text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              onClick={() => setBillingCycle('annual')}
            >
              Annual
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              className={`relative bg-white rounded-2xl shadow-xl overflow-hidden $${
                plan.popular ? 'ring-2 ring-purple-500 scale-105' : ''
              }`}
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
              whileHover={{ y: -5, transition: { duration: 0.2 } }}
            >
              {plan.popular && (
                <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-purple-500 to-purple-600 text-white text-center py-2 text-sm font-semibold">
                  Most Popular
                </div>
              )}
              
              <div className={`p-8 $${plan.popular ? 'pt-12' : ''}`}>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-6">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900">
                    £{billingCycle === 'annual' ? plan.price.annual : plan.price.monthly}
                  </span>
                  <span className="text-gray-600">
                    /{billingCycle === 'annual' ? 'year' : 'month'}
                  </span>
                  {billingCycle === 'annual' && (
                    <div className="text-sm text-green-600 font-semibold">
                      Save £{(plan.price.monthly * 12) - plan.price.annual} annually
                    </div>
                  )}
                </div>

                <motion.button
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 mb-6 bg-gradient-to-r $${plan.color} text-white hover:shadow-lg`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleSubscribe(plan)}
                >
                  {plan.cta}
                </motion.button>

                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Trust Signals */}
        <motion.div 
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
        >
          <p className="text-gray-600 mb-8">Trusted by leading M&A professionals worldwide</p>
          <div className="flex justify-center items-center space-x-12 opacity-60">
            {/* Add client logos here */}
            <div className="text-2xl font-bold text-gray-400">Goldman Sachs</div>
            <div className="text-2xl font-bold text-gray-400">Morgan Stanley</div>
            <div className="text-2xl font-bold text-gray-400">JP Morgan</div>
            <div className="text-2xl font-bold text-gray-400">Blackstone</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default PricingCards;
COMPONENT
```

### Step 2: Enhanced Backend Integration
```bash
# Update Stripe service for enterprise-level features
cd backend/app/services

# Enhance stripe_service.py
cat >> stripe_service.py << 'ENHANCEMENT'

class EnterpriseStripeService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
    
    async def create_enterprise_checkout_session(
        self, 
        plan_name: str, 
        billing_cycle: str, 
        user_id: str,
        success_url: str,
        cancel_url: str
    ):
        """Create enterprise-level checkout session with enhanced features"""
        
        # Plan configuration
        plan_configs = {
            "Professional": {
                "monthly": {"price_id": "price_professional_monthly", "amount": 27900},
                "annual": {"price_id": "price_professional_annual", "amount": 279000}
            },
            "Enterprise": {
                "monthly": {"price_id": "price_enterprise_monthly", "amount": 79900},
                "annual": {"price_id": "price_enterprise_annual", "amount": 799000}
            },
            "Elite": {
                "monthly": {"price_id": "price_elite_monthly", "amount": 159800},
                "annual": {"price_id": "price_elite_annual", "amount": 1598000}
            }
        }
        
        config = plan_configs[plan_name][billing_cycle]
        
        session = self.stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': config["price_id"],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=user_id,
            customer_email=None,  # Will be filled by Clerk
            metadata={
                'plan_name': plan_name,
                'billing_cycle': billing_cycle,
                'user_id': user_id
            },
            subscription_data={
                'metadata': {
                    'plan_name': plan_name,
                    'billing_cycle': billing_cycle,
                    'user_id': user_id
                }
            },
            # Enterprise features
            allow_promotion_codes=True,
            billing_address_collection='required',
            tax_id_collection={'enabled': True},
            custom_fields=[
                {
                    'key': 'company_name',
                    'label': {'type': 'custom', 'custom': 'Company Name'},
                    'type': 'text',
                    'optional': False
                },
                {
                    'key': 'company_size',
                    'label': {'type': 'custom', 'custom': 'Company Size'},
                    'type': 'dropdown',
                    'dropdown': {
                        'options': [
                            {'label': '1-10 employees', 'value': '1-10'},
                            {'label': '11-50 employees', 'value': '11-50'},
                            {'label': '51-200 employees', 'value': '51-200'},
                            {'label': '200+ employees', 'value': '200+'}
                        ]
                    },
                    'optional': False
                }
            ]
        )
        
        return session
ENHANCEMENT
```

### Step 3: Analytics and Conversion Tracking
```bash
# Add conversion tracking
cd frontend/src/utils

cat > analytics.js << 'ANALYTICS'
// Enterprise-level analytics tracking
import { gtag } from 'ga-gtag';

export class ConversionTracker {
  constructor() {
    this.events = [];
  }

  // Track pricing page events
  trackPricingView(planName) {
    gtag('event', 'view_pricing', {
      'event_category': 'engagement',
      'event_label': planName,
      'value': 1
    });
    
    // Mixpanel tracking
    if (window.mixpanel) {
      window.mixpanel.track('Pricing Page View', {
        'Plan': planName,
        'Page': 'Pricing',
        'Timestamp': new Date().toISOString()
      });
    }
  }

  trackPlanSelection(planName, billingCycle, price) {
    gtag('event', 'select_plan', {
      'event_category': 'conversion',
      'event_label': `$${planName}_$${billingCycle}`,
      'value': price
    });
    
    if (window.mixpanel) {
      window.mixpanel.track('Plan Selected', {
        'Plan Name': planName,
        'Billing Cycle': billingCycle,
        'Price': price,
        'Currency': 'GBP'
      });
    }
  }

  trackCheckoutStart(planName, billingCycle, price) {
    gtag('event', 'begin_checkout', {
      'event_category': 'ecommerce',
      'event_label': planName,
      'value': price,
      'currency': 'GBP'
    });
    
    if (window.mixpanel) {
      window.mixpanel.track('Checkout Started', {
        'Plan Name': planName,
        'Billing Cycle': billingCycle,
        'Price': price
      });
    }
  }

  trackSubscriptionSuccess(planName, billingCycle, price, subscriptionId) {
    gtag('event', 'purchase', {
      'transaction_id': subscriptionId,
      'value': price,
      'currency': 'GBP',
      'items': [{
        'item_id': planName.toLowerCase(),
        'item_name': `$${planName} - $${billingCycle}`,
        'category': 'subscription',
        'quantity': 1,
        'price': price
      }]
    });
    
    if (window.mixpanel) {
      window.mixpanel.track('Subscription Created', {
        'Plan Name': planName,
        'Billing Cycle': billingCycle,
        'Price': price,
        'Subscription ID': subscriptionId,
        'Revenue': price
      });
    }
  }
}

export const tracker = new ConversionTracker();
ANALYTICS
```

## 📊 Testing & Validation
```bash
# Run comprehensive tests
pytest backend/tests/test_api/test_stripe_event_pricing.py -v
pytest backend/tests/test_api/test_user_registration_sync.py -v

# Frontend testing
cd frontend
npm run test:pricing
npm run test:e2e:subscription

# Performance testing
npm run lighthouse:pricing
npm run test:accessibility
```

## ✅ Definition of Done
- [ ] Enterprise-level pricing page design implemented
- [ ] Smooth animations and micro-interactions
- [ ] Mobile-responsive design tested
- [ ] Stripe checkout integration working
- [ ] Analytics tracking implemented
- [ ] Accessibility compliance verified
- [ ] Performance metrics >90 Lighthouse score
- [ ] Cross-browser compatibility tested
- [ ] User acceptance testing completed
- [ ] Documentation updated in docs/stories/

## 📝 Story Documentation
Save this documentation to: `docs/stories/E1-P0-003-subscription-selection.md`
EOF

# Save story documentation
with open('docs/stories/E1-P0-003-subscription-selection.md', 'w') as f:
    f.write(story_doc)

print(f"\n✅ Story E1.P0.003 documentation created")
print(f"📁 Saved to: docs/stories/E1-P0-003-subscription-selection.md")
print(f"\n🚀 Next: Execute implementation steps to complete world-class subscription interface")
EOF
```

---

## 🎯 **PROMPT 2: E1.P0.004 - World-Class Welcome Dashboard**

```bash
# BMAD v6 Sprint 1 Completion - E1.P0.004 Welcome Dashboard
# Objective: Create enterprise-level welcome dashboard with irresistible onboarding
# Expected Output: World-class dashboard that converts trial users to paying customers

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime

print("🎯 BMAD v6 E1.P0.004 - World-Class Welcome Dashboard")
print("=" * 70)

story_doc = f"""# E1.P0.004 - World-Class Welcome Dashboard

## 🎯 Story Context
**Epic:** Customer Onboarding  
**Priority:** P0 - CRITICAL  
**Size:** L (3-4 days)  
**Status:** Ready for Implementation  
**Sprint:** 1 (Week 1)  

## 👤 User Story
**As a** newly registered user accessing the platform  
**I want** to see an irresistible welcome dashboard that guides me through key features  
**So that** I can quickly understand value and convert to a paying customer  

## ✅ Acceptance Criteria
**Given** I have completed registration and logged in for the first time  
**When** I access my dashboard  
**Then** I see a world-class welcome interface with guided experience  

**And:**
- Dashboard shows personalized welcome with enterprise-level design
- Interactive guided tour highlighting key value propositions
- Progress indicators creating psychological momentum
- Quick action buttons for high-value features
- Social proof and success metrics prominently displayed
- Conversion-optimized CTAs for subscription upgrade
- Mobile-responsive with premium feel

## 🎨 World-Class Design Requirements

### **Enterprise-Level Welcome Experience:**
- Personalized greeting with user's name and company
- Interactive product tour with value-focused messaging
- Progress gamification (completion badges, milestones)
- Feature discovery with benefit-focused explanations
- Success metrics and social proof integration
- Conversion-optimized upgrade prompts

### **Psychological Conversion Triggers:**
- Scarcity elements (limited-time trial features)
- Social proof (user testimonials, success stories)
- Authority signals (industry certifications, partnerships)
- Reciprocity (free valuable resources, tools)
- Commitment (goal setting, progress tracking)
- Urgency (trial countdown, special offers)

## 🔧 Implementation Components

### **1. Welcome Hero Section**
```jsx
const WelcomeHero = ({ user }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  
  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <motion.div 
      className="bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 rounded-2xl p-8 text-white mb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            {getGreeting()}, {user.firstName}! 👋
          </h1>
          <p className="text-blue-200 text-lg">
            Welcome to the future of M&A intelligence. Let's get you started.
          </p>
        </div>
        <div className="text-right">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div className="text-2xl font-bold">14</div>
            <div className="text-sm text-blue-200">Days left in trial</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
```

### **2. Interactive Progress Tracker**
```jsx
const OnboardingProgress = ({ completedSteps, totalSteps }) => {
  const progress = (completedSteps / totalSteps) * 100;
  
  const steps = [
    { id: 1, title: "Account Setup", completed: true, icon: "✓" },
    { id: 2, title: "Profile Complete", completed: true, icon: "✓" },
    { id: 3, title: "First Deal Added", completed: false, icon: "3" },
    { id: 4, title: "AI Analysis Run", completed: false, icon: "4" },
    { id: 5, title: "Network Connected", completed: false, icon: "5" }
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Your Success Journey</h2>
        <span className="text-sm text-gray-500">{completedSteps}/{totalSteps} Complete</span>
      </div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          {steps.map((step, index) => (
            <div key={step.id} className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold $${
                step.completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {step.icon}
              </div>
              <span className="text-xs mt-2 text-center max-w-20">{step.title}</span>
            </div>
          ))}
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div 
            className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `$${progress}%` }}
            transition={{ duration: 1, delay: 0.5 }}
          />
        </div>
      </div>
    </div>
  );
};
```

### **3. Quick Action Cards**
```jsx
const QuickActions = () => {
  const actions = [
    {
      title: "Add Your First Deal",
      description: "Start tracking your M&A opportunities",
      icon: "💼",
      cta: "Add Deal",
      value: "Track $10M+ in deal flow",
      color: "from-blue-500 to-blue-600"
    },
    {
      title: "Run AI Analysis", 
      description: "Get instant valuation insights",
      icon: "🤖",
      cta: "Analyze Deal",
      value: "Save 40+ hours of analysis",
      color: "from-purple-500 to-purple-600"
    },
    {
      title: "Connect Your Network",
      description: "Access exclusive deal opportunities", 
      icon: "🌐",
      cta: "Join Network",
      value: "Connect with 10,000+ professionals",
      color: "from-green-500 to-green-600"
    },
    {
      title: "Upgrade to Pro",
      description: "Unlock advanced features",
      icon: "⭐",
      cta: "Upgrade Now",
      value: "Save 17% with annual billing",
      color: "from-gold-500 to-gold-600"
    }
  ];

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {actions.map((action, index) => (
        <motion.div
          key={action.title}
          className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.6 }}
          whileHover={{ y: -5 }}
        >
          <div className="text-3xl mb-3">{action.icon}</div>
          <h3 className="font-semibold text-lg mb-2">{action.title}</h3>
          <p className="text-gray-600 text-sm mb-3">{action.description}</p>
          <div className="text-xs text-green-600 font-semibold mb-4">{action.value}</div>
          <motion.button
            className={`w-full py-2 px-4 rounded-lg text-white font-semibold bg-gradient-to-r $${action.color}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {action.cta}
          </motion.button>
        </motion.div>
      ))}
    </div>
  );
};
```

### **4. Social Proof & Success Metrics**
```jsx
const SocialProof = () => {
  const metrics = [
    { value: "$2.4B", label: "Deals Tracked", icon: "💰" },
    { value: "10,000+", label: "Active Users", icon: "👥" },
    { value: "95%", label: "Success Rate", icon: "📈" },
    { value: "24/7", label: "Expert Support", icon: "🎯" }
  ];

  const testimonials = [
    {
      quote: "This platform helped us close 3 deals worth $50M in our first quarter.",
      author: "Sarah Chen",
      title: "VP M&A, TechCorp",
      avatar: "/avatars/sarah.jpg"
    },
    {
      quote: "The AI analysis saved us weeks of due diligence work.",
      author: "Michael Rodriguez", 
      title: "Partner, Growth Capital",
      avatar: "/avatars/michael.jpg"
    }
  ];

  return (
    <div className="bg-gray-50 rounded-xl p-6 mb-8">
      <h2 className="text-xl font-semibold mb-6 text-center">
        Join Thousands of Successful M&A Professionals
      </h2>
      
      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            className="text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1, duration: 0.6 }}
          >
            <div className="text-2xl mb-1">{metric.icon}</div>
            <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
            <div className="text-sm text-gray-600">{metric.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Testimonials */}
      <div className="grid md:grid-cols-2 gap-6">
        {testimonials.map((testimonial, index) => (
          <motion.div
            key={index}
            className="bg-white rounded-lg p-4 shadow-sm"
            initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 + index * 0.2, duration: 0.6 }}
          >
            <p className="text-gray-700 mb-3 italic">"{testimonial.quote}"</p>
            <div className="flex items-center">
              <img 
                src={testimonial.avatar} 
                alt={testimonial.author}
                className="w-10 h-10 rounded-full mr-3"
              />
              <div>
                <div className="font-semibold text-sm">{testimonial.author}</div>
                <div className="text-xs text-gray-600">{testimonial.title}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
```

## 📊 Conversion Optimization Features

### **Trial Countdown Timer**
```jsx
const TrialCountdown = ({ trialEndDate }) => {
  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());
  
  function calculateTimeLeft() {
    const difference = +new Date(trialEndDate) - +new Date();
    let timeLeft = {};
    
    if (difference > 0) {
      timeLeft = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60)
      };
    }
    
    return timeLeft;
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeLeft(calculateTimeLeft());
    }, 60000);
    
    return () => clearTimeout(timer);
  });

  return (
    <motion.div 
      className="bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg p-4 mb-6"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Your Trial Expires Soon!</h3>
          <p className="text-sm opacity-90">Upgrade now to keep your data and features</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">
            {timeLeft.days}d {timeLeft.hours}h {timeLeft.minutes}m
          </div>
          <motion.button
            className="bg-white text-orange-500 px-4 py-2 rounded-lg font-semibold mt-2"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Upgrade Now - Save 17%
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
```

## ✅ Definition of Done
- [ ] World-class welcome dashboard implemented
- [ ] Interactive onboarding flow created
- [ ] Progress tracking with gamification
- [ ] Social proof and testimonials integrated
- [ ] Conversion-optimized CTAs implemented
- [ ] Trial countdown and urgency elements
- [ ] Mobile-responsive design verified
- [ ] Analytics tracking implemented
- [ ] A/B testing framework ready
- [ ] User acceptance testing completed

## 📝 Story Documentation
Save this documentation to: `docs/stories/E1-P0-004-welcome-dashboard.md`
"""

# Save story documentation
docs_dir = Path("docs/stories")
docs_dir.mkdir(parents=True, exist_ok=True)

with open('docs/stories/E1-P0-004-welcome-dashboard.md', 'w') as f:
    f.write(story_doc)

print(f"\n✅ Story E1.P0.004 documentation created")
print(f"📁 Saved to: docs/stories/E1-P0-004-welcome-dashboard.md")
print(f"\n🚀 Ready to implement world-class welcome dashboard")
EOF
```

---

## 🎯 **PROMPT 3: Sprint 2 Planning - Deal Management Excellence**

```bash
# BMAD v6 Sprint 2 Planning - Deal Management System
# Objective: Plan world-class deal management interface for Sprint 2
# Expected Output: Comprehensive Sprint 2 stories with enterprise-level requirements

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime, timedelta

print("🎯 BMAD v6 Sprint 2 Planning - Deal Management Excellence")
print("=" * 70)

# Sprint 2 stories with world-class requirements
sprint2_stories = [
    {
        "story_id": "E2.P1.001",
        "title": "World-Class Deal Creation Interface",
        "epic": "Deal Management",
        "priority": "P1 - HIGH",
        "size": "XL (4-5 days)",
        "description": "Enterprise-level deal creation with intelligent form design and AI assistance",
        "world_class_features": [
            "Smart form with progressive disclosure",
            "AI-powered deal categorization and valuation estimates",
            "Drag-and-drop document upload with OCR",
            "Real-time collaboration features",
            "Template library for common deal types",
            "Integration with external data sources",
            "Mobile-optimized interface",
            "Advanced validation and error handling"
        ]
    },
    {
        "story_id": "E2.P1.002", 
        "title": "Interactive Deal Pipeline with Advanced Analytics",
        "epic": "Deal Management",
        "priority": "P1 - HIGH",
        "size": "XL (4-5 days)",
        "description": "Kanban-style pipeline with real-time updates and business intelligence",
        "world_class_features": [
            "Customizable pipeline stages with automation",
            "Real-time collaboration and notifications",
            "Advanced filtering and search capabilities",
            "Bulk operations and batch processing",
            "Pipeline analytics and forecasting",
            "Integration with calendar and email",
            "Mobile-responsive drag-and-drop",
            "Export capabilities (PDF, Excel, PowerBI)"
        ]
    },
    {
        "story_id": "E2.P1.003",
        "title": "AI-Powered Deal Intelligence Dashboard", 
        "epic": "AI Intelligence",
        "priority": "P1 - HIGH",
        "size": "XL (4-5 days)",
        "description": "Comprehensive AI analysis with predictive insights and recommendations",
        "world_class_features": [
            "Real-time valuation modeling with multiple methodologies",
            "Risk assessment with probability scoring",
            "Market comparables with dynamic updates",
            "Predictive deal outcome modeling",
            "Automated due diligence checklists",
            "Integration with financial data providers",
            "Custom report generation",
            "Interactive data visualizations"
        ]
    }
]

# Create comprehensive Sprint 2 documentation
sprint2_doc = f"""# Sprint 2: Deal Management Excellence

## 🎯 Sprint Overview
**Timeline:** Week 2-3 (Oct 21 - Nov 3, 2025)  
**Objective:** Create world-class deal management system that converts users to paying customers  
**Theme:** Enterprise-level functionality with irresistible user experience  

## 📊 Sprint Goals
- Complete deal creation and pipeline management
- Implement AI-powered deal intelligence
- Achieve 90%+ user engagement with deal features
- Drive subscription conversions through value demonstration
- Establish foundation for enterprise sales

## 🌟 World-Class Standards

### **Design Excellence:**
- Enterprise-level visual design with premium feel
- Intuitive user experience with minimal learning curve
- Mobile-first responsive design
- Accessibility compliance (WCAG AA)
- Performance optimization (sub-2 second load times)

### **Functionality Excellence:**
- AI-powered intelligent features
- Real-time collaboration capabilities
- Advanced analytics and reporting
- Seamless integrations with external tools
- Robust error handling and data validation

### **Business Excellence:**
- Clear value proposition demonstration
- Conversion-optimized user flows
- Upgrade prompts at strategic moments
- Success metrics tracking
- Customer success enablement

## 📋 Sprint 2 Stories

"""

for story in sprint2_stories:
    sprint2_doc += f"""
### **{story['story_id']} - {story['title']}**

**Epic:** {story['epic']}  
**Priority:** {story['priority']}  
**Size:** {story['size']}  

**Description:** {story['description']}

**World-Class Features:**
"""
    for feature in story['world_class_features']:
        sprint2_doc += f"- {feature}\n"
    
    sprint2_doc += f"""
**Acceptance Criteria:**
- [ ] Enterprise-level design implementation
- [ ] Mobile-responsive interface
- [ ] Real-time functionality working
- [ ] Analytics tracking implemented
- [ ] Performance metrics >90 Lighthouse score
- [ ] User acceptance testing completed
- [ ] Documentation updated

**Definition of Done:**
- [ ] Code implemented and tested
- [ ] UI/UX matches world-class standards
- [ ] API endpoints functional and documented
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Accessibility compliance verified
- [ ] Mobile testing completed
- [ ] Stakeholder approval received

---
"""

sprint2_doc += f"""
## 🚀 Implementation Strategy

### **Week 2 (Oct 21-27):**
- E2.P1.001: World-Class Deal Creation Interface
- Focus: Core functionality with enterprise design
- Milestone: Deal creation fully functional

### **Week 3 (Oct 28 - Nov 3):**
- E2.P1.002: Interactive Deal Pipeline
- E2.P1.003: AI-Powered Deal Intelligence
- Focus: Advanced features and AI integration
- Milestone: Complete deal management system

## 📊 Success Metrics

### **User Engagement:**
- Deal creation completion rate >85%
- Pipeline interaction time >5 minutes per session
- Feature adoption rate >70% within first week

### **Business Metrics:**
- Trial-to-paid conversion rate >15%
- User retention rate >80% after deal creation
- Customer satisfaction score >4.5/5

### **Technical Metrics:**
- Page load time <2 seconds
- API response time <500ms
- Uptime >99.9%
- Mobile performance score >90

## 🎯 Conversion Optimization

### **Strategic Upgrade Prompts:**
- After first deal creation: "Unlock unlimited deals"
- After pipeline view: "Get advanced analytics"
- After AI analysis: "Access premium AI features"

### **Value Demonstration:**
- Show time saved with AI analysis
- Display deal value tracked
- Highlight network connections made
- Demonstrate ROI calculations

## 📝 Documentation Requirements

Each story must include:
- Detailed technical specifications
- UI/UX design mockups
- API documentation
- Testing procedures
- Performance benchmarks
- User acceptance criteria

## 🔄 Sprint Ceremonies

### **Sprint Planning (Oct 21):**
- Review and refine story requirements
- Estimate effort and assign tasks
- Set up development environment
- Align on world-class standards

### **Daily Standups:**
- Progress against world-class criteria
- Blockers and dependencies
- Quality assurance checkpoints
- User feedback integration

### **Sprint Review (Nov 3):**
- Demo world-class features
- Validate against acceptance criteria
- Gather stakeholder feedback
- Plan Sprint 3 priorities

### **Sprint Retrospective:**
- Assess world-class delivery
- Identify improvement opportunities
- Refine development processes
- Update quality standards

---

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Methodology:** BMAD v6 Level 4 Sprint Planning  
**Next Sprint:** Sprint 3 - AI Intelligence & Community Platform  
"""

# Save Sprint 2 documentation
with open('docs/stories/Sprint-2-Deal-Management-Excellence.md', 'w') as f:
    f.write(sprint2_doc)

# Create individual story files
for story in sprint2_stories:
    story_detail = f"""# {story['story_id']} - {story['title']}

## 🎯 Story Context
**Epic:** {story['epic']}  
**Priority:** {story['priority']}  
**Size:** {story['size']}  
**Sprint:** 2 (Week 2-3)  
**Status:** Ready for Implementation  

## 📝 Description
{story['description']}

## 🌟 World-Class Features
"""
    for feature in story['world_class_features']:
        story_detail += f"- {feature}\n"
    
    story_detail += f"""
## 👤 User Story
**As a** M&A professional managing deals  
**I want** {story['title'].lower()}  
**So that** I can efficiently manage my deal flow and demonstrate platform value  

## ✅ Acceptance Criteria
**Given** I am a logged-in user with deal management needs  
**When** I use the {story['title'].lower()}  
**Then** I experience world-class functionality that exceeds expectations  

**And:**
- Interface meets enterprise-level design standards
- Performance is optimized for speed and responsiveness
- Mobile experience is seamless and intuitive
- Analytics tracking captures all user interactions
- Conversion opportunities are strategically placed
- Help and guidance are contextually available

## 🔧 Technical Requirements

### **Frontend:**
- React components with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Hook Form for form handling
- RTK Query for data management
- Mobile-responsive design

### **Backend:**
- FastAPI endpoints with validation
- SQLAlchemy models and relationships
- Celery for background processing
- Redis for caching and real-time features
- Comprehensive error handling
- API documentation with OpenAPI

### **Integration:**
- Real-time updates via WebSocket
- External data source integration
- Analytics tracking (GA4, Mixpanel)
- Email notifications
- File storage and processing
- AI service integration

## 📊 Performance Requirements
- Page load time: <2 seconds
- API response time: <500ms
- Mobile performance score: >90
- Accessibility score: >95
- SEO score: >90

## 🧪 Testing Strategy
- Unit tests for all components
- Integration tests for API endpoints
- E2E tests for user workflows
- Performance testing with Lighthouse
- Accessibility testing with axe
- Cross-browser compatibility testing
- Mobile device testing

## ✅ Definition of Done
- [ ] Code implemented and tested
- [ ] UI/UX matches world-class standards
- [ ] API endpoints functional and documented
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Accessibility compliance verified
- [ ] Mobile testing completed
- [ ] Analytics tracking implemented
- [ ] User acceptance testing completed
- [ ] Stakeholder approval received
- [ ] Documentation updated
- [ ] Deployed to staging environment

## 📝 Notes
- Follow BMAD v6 methodology for systematic implementation
- Ensure all acceptance criteria are met before marking complete
- Test thoroughly on multiple devices and browsers
- Document any deviations or additional requirements discovered
- Update team on progress and any blockers encountered

---
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Methodology:** BMAD v6 Level 4 Story Planning  
**Dependencies:** Sprint 1 completion  
"""
    
    filename = f"docs/stories/{story['story_id'].replace('.', '-')}-{story['title'].lower().replace(' ', '-').replace(':', '')}.md"
    with open(filename, 'w') as f:
        f.write(story_detail)

print(f"\n✅ Sprint 2 planning documentation created")
print(f"📁 Sprint overview: docs/stories/Sprint-2-Deal-Management-Excellence.md")
print(f"📁 Individual stories: docs/stories/E2-P1-*.md")
print(f"\n🚀 Ready to execute world-class Sprint 2 development")
print(f"\n📋 Next Actions:")
print(f"   1. Complete Sprint 1 stories (E1.P0.003, E1.P0.004)")
print(f"   2. Review Sprint 2 requirements with stakeholders")
print(f"   3. Begin Sprint 2 implementation with E2.P1.001")
print(f"   4. Maintain world-class standards throughout development")
EOF
```

These prompts will drive your website development to the world-class, enterprise-level standards you expect. Each prompt includes:

- **Comprehensive story documentation** in your `docs/stories` structure
- **World-class design requirements** with enterprise-level standards
- **Conversion optimization** features and psychological triggers
- **Technical excellence** with performance and accessibility requirements
- **Systematic implementation** following BMAD v6 methodology

Execute these prompts in sequence to complete Sprint 1 and plan Sprint 2 with the irresistible, high-converting website you envision!
