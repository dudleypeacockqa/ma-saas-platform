import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ArrowRight,
  TrendingUp,
  Brain,
  FileText,
  Calculator,
  Target,
  Zap,
  Shield,
  Globe,
  CheckCircle,
  Star,
  Play,
  DollarSign,
  BarChart3,
  Users,
  Lightbulb,
} from 'lucide-react';

const LandingPage = () => {
  const [activeService, setActiveService] = useState(0);

  const coreServices = [
    {
      icon: <Brain className="h-12 w-12" />,
      title: 'AI-Powered Financial Intelligence',
      description:
        'Advanced financial analysis with 47+ key metrics, real-time accounting integration, and AI insights',
      benefits: [
        'Xero, QuickBooks, Sage & NetSuite integration',
        'Real-time financial health monitoring',
        'AI-powered insights & recommendations',
      ],
      link: '/services/financial-intelligence',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: <FileText className="h-12 w-12" />,
      title: 'Professional Template Engine',
      description: '200+ jurisdiction-specific legal documents with AI-powered customization',
      benefits: [
        '200+ professional templates',
        'Multi-jurisdiction compliance',
        'AI-powered document generation',
      ],
      link: '/services/template-engine',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: <Calculator className="h-12 w-12" />,
      title: 'Interactive Offer Stack Generator',
      description:
        'Professional offer presentations with multiple funding scenarios and Excel/PowerPoint export',
      benefits: [
        'Multiple funding scenarios',
        'Professional presentations',
        'Excel & PowerPoint export',
      ],
      link: '/services/offer-generator',
      color: 'from-purple-500 to-violet-500',
    },
    {
      icon: <Target className="h-12 w-12" />,
      title: 'Intelligent Deal Matching',
      description:
        'AI-powered buyer/seller matching with compatibility scoring and market intelligence',
      benefits: [
        'AI-powered matching algorithms',
        'Compatibility scoring',
        'Market intelligence insights',
      ],
      link: '/services/deal-matching',
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: <BarChart3 className="h-12 w-12" />,
      title: 'Automated Valuation Engine',
      description:
        'Multi-methodology valuation with DCF, comparable companies, and precedent transaction analysis',
      benefits: [
        'DCF & comparable analysis',
        'Monte Carlo simulation',
        'Precedent transaction data',
      ],
      link: '/services/valuation-engine',
      color: 'from-indigo-500 to-purple-500',
    },
  ];

  const platformStats = [
    { number: '£200M', label: 'Target Platform Valuation' },
    { number: '90%+', label: 'Trial-to-Paid Conversion' },
    { number: '5', label: 'Core M&A Services' },
    { number: '200+', label: 'Legal Templates' },
  ];

  const pricingPlans = [
    {
      name: 'Professional',
      price: '£99',
      period: '/month',
      description: 'Perfect for solo M&A professionals',
      features: [
        'AI Financial Intelligence',
        'Template Engine (50 templates)',
        'Basic Offer Generator',
        'Deal Matching (10 matches/month)',
        'Basic Valuation Tools',
        'Email Support',
      ],
      popular: false,
    },
    {
      name: 'Enterprise',
      price: '£299',
      period: '/month',
      description: 'For growing M&A teams and firms',
      features: [
        'All Professional features',
        'Full Template Library (200+)',
        'Advanced Offer Generator',
        'Unlimited Deal Matching',
        'Complete Valuation Engine',
        'Team Collaboration',
        'Priority Support',
        'Custom Integrations',
      ],
      popular: true,
    },
    {
      name: 'Investment Bank',
      price: '£999',
      period: '/month',
      description: 'For large firms and investment banks',
      features: [
        'All Enterprise features',
        'White-label Platform',
        'Advanced Analytics',
        'Custom Workflows',
        'API Access',
        'Dedicated Success Manager',
        'SLA Guarantee',
        'Custom Development',
      ],
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge
              variant="secondary"
              className="mb-6 bg-blue-500/20 text-blue-200 border-blue-400"
            >
              🚀 The World's Most Amazing M&A Ecosystem Platform
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Master M&A in
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                {' '}
                100 Days
              </span>
              <br />
              and Beyond
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-4xl mx-auto">
              The only platform you need with 5 AI-powered core services: Financial Intelligence,
              Template Engine, Offer Generator, Deal Matching, and Valuation Engine.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button size="lg" className="text-lg px-8 py-4 bg-blue-600 hover:bg-blue-700" asChild>
                <Link to="/sign-up">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="text-lg px-8 py-4 border-blue-400 text-blue-100 hover:bg-blue-800/20"
              >
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
              </Button>
            </div>

            {/* Platform Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
              {platformStats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-3xl md:text-4xl font-bold text-blue-400 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-blue-200 text-sm md:text-base">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Core Services Section */}
      <section className="py-24 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              5 Core M&A Services That Drive Results
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Each service is designed to give you an unfair advantage in M&A, backed by AI and
              built for professionals who demand excellence.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
            <div className="space-y-4">
              {coreServices.map((service, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className={`p-6 rounded-xl border cursor-pointer transition-all ${
                    activeService === index
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-md'
                  }`}
                  onClick={() => setActiveService(index)}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${service.color} text-white`}>
                      {service.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        {service.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300 mb-3">{service.description}</p>
                      <ul className="space-y-1 mb-4">
                        {service.benefits.map((benefit, i) => (
                          <li
                            key={i}
                            className="flex items-center text-sm text-gray-500 dark:text-gray-400"
                          >
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                            {benefit}
                          </li>
                        ))}
                      </ul>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={service.link}>Learn More</Link>
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div
                className={`bg-gradient-to-br ${coreServices[activeService].color} rounded-2xl p-8 text-white shadow-2xl`}
              >
                <div className="mb-6">{coreServices[activeService].icon}</div>
                <h3 className="text-2xl font-bold mb-4">{coreServices[activeService].title}</h3>
                <p className="text-white/90 mb-6">{coreServices[activeService].description}</p>
                <div className="space-y-3 mb-8">
                  {coreServices[activeService].benefits.map((benefit, i) => (
                    <div key={i} className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-white/80 mr-3 flex-shrink-0" />
                      <span className="text-white/90">{benefit}</span>
                    </div>
                  ))}
                </div>
                <Button variant="secondary" size="lg" className="w-full" asChild>
                  <Link to={coreServices[activeService].link}>
                    Explore This Service
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </div>
            </motion.div>
          </div>

          {/* Service Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {coreServices.slice(0, 6).map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow border-l-4 border-l-blue-500">
                  <CardHeader className="pb-4">
                    <div
                      className={`w-12 h-12 rounded-lg bg-gradient-to-r ${service.color} flex items-center justify-center text-white mb-4`}
                    >
                      {service.icon}
                    </div>
                    <CardTitle className="text-lg">{service.title}</CardTitle>
                    <CardDescription className="text-sm">{service.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="outline" size="sm" className="w-full" asChild>
                      <Link to={service.link}>Learn More</Link>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              Professional M&A Platform Pricing
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Choose the plan that fits your M&A practice. All plans include 90%+ trial-to-paid
              conversion guarantee.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card
                  className={`relative h-full ${
                    plan.popular
                      ? 'border-blue-500 shadow-xl scale-105 bg-gradient-to-b from-blue-50 to-white dark:from-blue-900/20 dark:to-gray-800'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                >
                  {plan.popular && (
                    <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white">
                      Most Popular
                    </Badge>
                  )}
                  <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                    <div className="mt-4">
                      <span className="text-4xl font-bold text-blue-600">{plan.price}</span>
                      <span className="text-gray-500 dark:text-gray-400">{plan.period}</span>
                    </div>
                    <CardDescription className="mt-2">{plan.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-center">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                          <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button
                      className="w-full"
                      variant={plan.popular ? 'default' : 'outline'}
                      size="lg"
                      asChild
                    >
                      <Link to="/sign-up">Start Free Trial</Link>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Build Your £200M M&A Empire?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join the M&A professionals who are already using our 5 core services to achieve 90%+
              trial-to-paid conversion and build wealth through superior deal execution.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="text-lg px-8 py-4 bg-white text-blue-600 hover:bg-gray-100"
                asChild
              >
                <Link to="/sign-up">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-4 border-white text-white hover:bg-white/10"
                asChild
              >
                <Link to="/platform">View Platform Overview</Link>
              </Button>
            </div>
            <p className="text-blue-200 mt-6 text-sm">
              No credit card required • 14-day free trial • 90%+ conversion guarantee • £200M wealth
              building path
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
