# 🎯 BMAD v6 Bootstrapped Revenue Generation Prompts

**Date:** 2025-10-16  
**Objective:** Focus messaging on immediate SaaS revenue to fund personal PE development  
**Strategy:** Bootstrap through subscriptions and events to generate investment capital  

---

## 🎯 **PROMPT 1: Revenue-Focused Homepage Messaging**

```bash
# BMAD v6 Bootstrap Revenue Focus - Homepage Conversion Optimization
# Objective: Maximize subscription conversions and event revenue
# Expected Output: High-converting homepage focused on immediate revenue

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime

print("🎯 BMAD v6 Bootstrap Revenue Homepage")
print("=" * 70)

homepage_content = """
# Bootstrap Revenue-Focused Homepage

## Hero Section - Subscription Conversion Focus
```jsx
const BootstrapHero = () => {
  return (
    <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="bg-green-500 text-white px-4 py-2 rounded-full inline-block mb-4 text-sm font-semibold">
              Join 1,000+ M&A Professionals
            </div>
            
            <h1 className="text-5xl lg:text-6xl font-bold text-white mb-6">
              Close More Deals with 
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                AI-Powered Intelligence
              </span>
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              The M&A Intelligence Platform used by leading professionals to source deals, 
              analyze opportunities, and accelerate success. Join the exclusive community 
              driving £2.4B+ in deal flow annually.
            </p>

            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-8">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-400">3x</div>
                  <div className="text-sm text-gray-300">More Deals Closed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-400">£2.4B</div>
                  <div className="text-sm text-gray-300">Annual Deal Flow</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-400">94%</div>
                  <div className="text-sm text-gray-300">Analysis Accuracy</div>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <motion.button
                className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:shadow-xl transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Start Free 30-Day Trial
              </motion.button>
              <motion.button
                className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-gray-900 transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Watch Live Demo
              </motion.button>
            </div>

            <div className="flex items-center text-gray-300 text-sm">
              <svg className="w-4 h-4 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              No credit card required • Cancel anytime • 30-day money-back guarantee
            </div>
          </motion.div>

          <motion.div
            className="relative"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="bg-white rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Live Deal Intelligence</h3>
                <div className="flex items-center text-green-500">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  LIVE DATA
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-700 font-medium">Active Deal Pipeline</span>
                    <span className="text-blue-600 font-bold">£47.2M</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-blue-400 to-purple-500 h-2 rounded-full w-3/4"></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">23 opportunities tracked</div>
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-lg font-bold text-gray-900">847</div>
                    <div className="text-sm text-gray-600">Deals Sourced</div>
                    <div className="text-xs text-green-600">+156% this quarter</div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-lg font-bold text-gray-900">94%</div>
                    <div className="text-sm text-gray-600">AI Accuracy</div>
                    <div className="text-xs text-green-600">Industry leading</div>
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                  <div className="flex items-center text-green-700 text-sm font-medium mb-1">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    New Opportunity Alert
                  </div>
                  <div className="text-xs text-green-600">£15M SaaS company - 85% match score</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
```

## Value Proposition Section - Revenue Focus
```jsx
const ValueProposition = () => {
  const benefits = [
    {
      icon: "🎯",
      title: "AI-Powered Deal Sourcing",
      description: "Find off-market opportunities before your competition with intelligent market scanning and predictive analytics.",
      metric: "3x more deals",
      proof: "vs manual sourcing"
    },
    {
      icon: "📊",
      title: "Advanced Valuation Models", 
      description: "Make confident investment decisions with comprehensive DCF modeling, comparable analysis, and risk assessment.",
      metric: "94% accuracy",
      proof: "in deal predictions"
    },
    {
      icon: "🤝",
      title: "Exclusive Deal Network",
      description: "Access our private community of 1,000+ M&A professionals sharing off-market opportunities and insights.",
      metric: "£2.4B+ deal flow",
      proof: "shared annually"
    },
    {
      icon: "⚡",
      title: "Streamlined Execution",
      description: "Close deals faster with integrated workflows, due diligence templates, and collaboration tools.",
      metric: "50% faster",
      proof: "deal completion"
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Why Leading M&A Professionals Choose Our Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto">
            Join the exclusive community of successful deal makers who rely on our 
            AI-powered intelligence to source, analyze, and execute more profitable transactions.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100 hover:shadow-lg transition-all duration-300"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
              whileHover={{ y: -5 }}
            >
              <div className="flex items-start">
                <div className="text-4xl mr-4">{benefit.icon}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{benefit.title}</h3>
                  <p className="text-gray-600 mb-4">{benefit.description}</p>
                  
                  <div className="bg-white rounded-lg p-3 border border-gray-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-lg font-bold text-blue-600">{benefit.metric}</div>
                        <div className="text-sm text-gray-500">{benefit.proof}</div>
                      </div>
                      <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="text-center mt-12">
          <motion.button
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-12 py-4 rounded-lg font-semibold text-xl hover:shadow-xl transition-all duration-300"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Start Your Free Trial Today
          </motion.button>
          <p className="text-gray-500 text-sm mt-2">Join 1,000+ professionals already using our platform</p>
        </div>
      </div>
    </section>
  );
};
```

## Social Proof Section - Revenue Credibility
```jsx
const SocialProof = () => {
  const testimonials = [
    {
      quote: "The AI analysis helped me identify a £25M acquisition opportunity that I would have missed. The platform paid for itself 100x over with just one deal.",
      author: "Sarah Chen",
      title: "VP M&A, TechCorp",
      deal: "£25M SaaS Acquisition",
      result: "300% ROI in 18 months"
    },
    {
      quote: "The exclusive network gave me access to off-market deals worth £50M+. The quarterly events alone are worth the subscription price.",
      author: "Michael Rodriguez", 
      title: "Partner, Growth Capital",
      deal: "£50M+ Deal Flow",
      result: "3 successful exits"
    },
    {
      quote: "Our deal completion time dropped by 50% using the platform's workflow tools. The due diligence templates are incredibly comprehensive.",
      author: "Emma Thompson",
      title: "Director, Corporate Development",
      deal: "£15M Manufacturing Buy",
      result: "50% faster execution"
    }
  ];

  const logos = [
    "TechCorp", "Growth Capital", "Meridian Partners", "Apex Ventures", 
    "Summit Capital", "Pinnacle Investments", "Catalyst Partners", "Nexus Capital"
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Trusted by Leading M&A Professionals
          </h2>
          <p className="text-xl text-gray-600">
            See how our platform has helped professionals close £2.4B+ in deals
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.author}
              className="bg-white rounded-xl p-6 shadow-lg border border-gray-200"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
            >
              <div className="mb-4">
                <svg className="w-8 h-8 text-blue-500 mb-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
                <blockquote className="text-gray-700 italic">
                  "{testimonial.quote}"
                </blockquote>
              </div>
              
              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                    <div className="text-sm text-gray-600">{testimonial.title}</div>
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-3 mt-3">
                  <div className="text-sm font-medium text-green-800">{testimonial.deal}</div>
                  <div className="text-sm text-green-600">{testimonial.result}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Trusted by professionals at leading firms
          </h3>
          <div className="grid grid-cols-4 md:grid-cols-8 gap-6 items-center opacity-60">
            {logos.map((logo, index) => (
              <div key={logo} className="text-gray-500 font-semibold text-sm">
                {logo}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
```

## Pricing Section - Conversion Optimized
```jsx
const PricingSection = () => {
  const plans = [
    {
      name: "Professional",
      price: "£279",
      period: "/month",
      description: "Perfect for solo M&A professionals and independent advisors",
      features: [
        "AI-powered deal sourcing and analysis",
        "Advanced valuation models (DCF, Comps)",
        "Due diligence templates and checklists", 
        "Basic community access and networking",
        "Email support and knowledge base",
        "Mobile app access",
        "Track up to 5 active deals"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Enterprise", 
      price: "£799",
      period: "/month",
      description: "Advanced features for growing M&A teams and boutique firms",
      features: [
        "Everything in Professional",
        "Priority community access and VIP networking",
        "Advanced analytics and custom reporting",
        "Team collaboration tools (up to 10 users)",
        "API access and third-party integrations",
        "Dedicated account manager",
        "Priority support with SLA",
        "Unlimited deal tracking"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Elite",
      price: "£1,598", 
      period: "/month",
      description: "Premium solution for enterprise M&A operations",
      features: [
        "Everything in Enterprise",
        "VIP event access and private masterminds",
        "Custom integrations and white-label options",
        "24/7 priority support with dedicated team",
        "Strategic advisory access",
        "Custom AI model training",
        "Concierge deal services",
        "Advanced security and compliance"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Success Plan
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Start with a 30-day free trial. No credit card required. Cancel anytime.
          </p>
          
          <div className="flex items-center justify-center space-x-8 text-gray-600">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              30-Day Free Trial
            </div>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Money-Back Guarantee
            </div>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Cancel Anytime
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              className={`bg-white rounded-2xl shadow-lg overflow-hidden border-2 $${
                plan.popular ? 'border-purple-500 scale-105' : 'border-gray-200'
              }`}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
              whileHover={{ y: -5 }}
            >
              {plan.popular && (
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-center py-2 text-sm font-semibold">
                  Most Popular - Save 20%
                </div>
              )}
              
              <div className={`p-8 $${plan.popular ? 'pt-6' : ''}`}>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-6">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                  <div className="text-sm text-gray-500">per user, billed monthly</div>
                </div>

                <motion.button
                  className={`w-full py-3 px-6 rounded-lg font-semibold mb-6 transition-all duration-200 $${
                    plan.popular 
                      ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:shadow-lg' 
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {plan.cta}
                </motion.button>

                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <svg className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            Need a custom solution for your organization?
          </p>
          <motion.button
            className="bg-gray-100 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Contact Sales Team
          </motion.button>
        </div>
      </div>
    </section>
  );
};
```

## Event Revenue Section - Premium Community
```jsx
const EventRevenue = () => {
  const events = [
    {
      title: "Quarterly Deal Forums",
      subtitle: "Exclusive networking with 50-100 M&A professionals",
      price: "£1,000",
      frequency: "per ticket",
      description: "Intimate quarterly gatherings for serious deal makers to share opportunities, insights, and build lasting relationships.",
      features: [
        "Off-market deal sharing sessions",
        "Expert panels and case studies", 
        "1-on-1 networking opportunities",
        "Deal collaboration workshops",
        "Premium venue and catering",
        "Digital deal room access"
      ],
      nextEvent: "January 25, 2025 - London",
      earlyBird: "£750 Early Bird (Limited Time)"
    },
    {
      title: "Annual M&A Summit",
      subtitle: "Premier UK M&A conference with 500+ attendees", 
      price: "£3,500",
      frequency: "per ticket",
      description: "The UK's most influential M&A event bringing together industry leaders, investors, and deal makers for two days of intensive learning and networking.",
      features: [
        "20+ expert speakers and panels",
        "Masterclass sessions with industry legends",
        "Exhibition hall with 50+ vendors",
        "VIP networking receptions",
        "Awards ceremony and gala dinner",
        "12 months of digital content access"
      ],
      nextEvent: "June 15-16, 2025 - London",
      earlyBird: "£2,500 Early Bird (Save £1,000)"
    },
    {
      title: "Private Masterminds",
      subtitle: "Exclusive 10-person groups with industry leaders",
      price: "£10,000",
      frequency: "per year",
      description: "Join an exclusive mastermind group of 10 successful M&A professionals for quarterly strategic sessions, deal reviews, and peer advisory.",
      features: [
        "Quarterly in-person meetings",
        "Monthly virtual check-ins",
        "Confidential deal reviews and feedback",
        "Strategic planning sessions",
        "Peer advisory and mentorship",
        "Exclusive deal sharing network"
      ],
      nextEvent: "Rolling Admission - Apply Now",
      earlyBird: "Founding Member: £8,500 (Save £1,500)"
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-900 to-blue-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Exclusive M&A Events & Community
          </h2>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto">
            Join the UK's most influential M&A community. Access invite-only events, 
            off-market deals, and industry insights that accelerate your success.
          </p>
        </div>

        <div className="space-y-8">
          {events.map((event, index) => (
            <motion.div
              key={event.title}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2, duration: 0.6 }}
            >
              <div className="grid lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <div className="flex items-center mb-4">
                    <h3 className="text-2xl font-bold text-white mr-4">{event.title}</h3>
                    <div className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      Limited Seats
                    </div>
                  </div>
                  <p className="text-gray-300 mb-4">{event.subtitle}</p>
                  <p className="text-gray-400 mb-6">{event.description}</p>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    {event.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center text-gray-300">
                        <svg className="w-4 h-4 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="lg:col-span-1">
                  <div className="bg-white rounded-xl p-6">
                    <div className="text-center mb-4">
                      <div className="text-3xl font-bold text-gray-900">{event.price}</div>
                      <div className="text-gray-600">{event.frequency}</div>
                    </div>
                    
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                      <div className="text-green-800 font-semibold text-sm">Early Bird Special</div>
                      <div className="text-green-600 text-sm">{event.earlyBird}</div>
                    </div>
                    
                    <div className="mb-4">
                      <div className="text-gray-700 font-semibold text-sm">Next Event:</div>
                      <div className="text-gray-600 text-sm">{event.nextEvent}</div>
                    </div>
                    
                    <motion.button
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Register Now
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-gray-300 mb-4">
            Platform subscribers get exclusive access and member pricing
          </p>
          <motion.button
            className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:shadow-xl transition-all duration-300"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Join Platform & Save on Events
          </motion.button>
        </div>
      </div>
    </section>
  );
};
```
"""

# Save bootstrap homepage content
docs_dir = Path("docs/stories")
docs_dir.mkdir(parents=True, exist_ok=True)

with open('docs/stories/bootstrap-revenue-homepage.md', 'w') as f:
    f.write(homepage_content)

print(f"\n✅ Bootstrap revenue homepage created")
print(f"📁 Saved to: docs/stories/bootstrap-revenue-homepage.md")
print(f"\n🚀 Ready to implement revenue-focused homepage for subscription growth")
EOF
```

This prompt creates a homepage specifically designed to maximize subscription conversions and event revenue, supporting your bootstrapped approach to building investment capital for your PE firm development.
