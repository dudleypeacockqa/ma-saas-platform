import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Brain,
  FileText,
  Calculator,
  Target,
  BarChart3,
  ArrowRight,
  CheckCircle,
  Users,
  Globe,
  Shield,
  Zap,
  TrendingUp,
} from 'lucide-react';

const PlatformOverviewPage = () => {
  const coreServices = [
    {
      icon: <Brain className="h-8 w-8" />,
      title: 'AI-Powered Financial Intelligence',
      description: '47+ key metrics with real-time accounting integration',
      features: [
        'Xero, QuickBooks, Sage & NetSuite integration',
        'Real-time financial health monitoring',
        'AI-powered insights & recommendations',
      ],
      link: '/services/financial-intelligence',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: 'Professional Template Engine',
      description: '200+ jurisdiction-specific legal documents',
      features: [
        'Multi-jurisdiction compliance',
        'AI-powered customization',
        'Professional document generation',
      ],
      link: '/services/template-engine',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: <Calculator className="h-8 w-8" />,
      title: 'Interactive Offer Stack Generator',
      description: 'Professional presentations with multiple funding scenarios',
      features: [
        'Multiple funding scenarios',
        'Excel & PowerPoint export',
        'What-if analysis capabilities',
      ],
      link: '/services/offer-generator',
      color: 'from-purple-500 to-violet-500',
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: 'Intelligent Deal Matching',
      description: 'AI-powered buyer/seller matching with compatibility scoring',
      features: [
        'AI-powered matching algorithms',
        'Compatibility scoring',
        'Market intelligence insights',
      ],
      link: '/services/deal-matching',
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: 'Automated Valuation Engine',
      description: 'Multi-methodology valuation with advanced analytics',
      features: [
        'DCF & comparable analysis',
        'Monte Carlo simulation',
        'Precedent transaction data',
      ],
      link: '/services/valuation-engine',
      color: 'from-indigo-500 to-purple-500',
    },
  ];

  const platformBenefits = [
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Lightning Fast',
      description: 'Process deals 10x faster with AI automation',
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Enterprise Security',
      description: 'Bank-grade security with SOC 2 compliance',
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: 'Global Reach',
      description: 'Multi-jurisdiction support for international deals',
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: 'Team Collaboration',
      description: 'Real-time collaboration tools for deal teams',
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: 'Revenue Growth',
      description: '90%+ trial-to-paid conversion guarantee',
    },
    {
      icon: <Brain className="h-6 w-6" />,
      title: 'AI-Powered',
      description: 'Advanced AI for insights and automation',
    },
  ];

  const stats = [
    { number: '£200M', label: 'Target Platform Valuation' },
    { number: '90%+', label: 'Trial-to-Paid Conversion' },
    { number: '5', label: 'Core M&A Services' },
    { number: '200+', label: 'Legal Templates' },
    { number: '47+', label: 'Financial Metrics' },
    { number: '10x', label: 'Faster Deal Processing' },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-blue-500/20 text-blue-200 border-blue-400">
              🚀 The World's Most Amazing M&A Ecosystem Platform
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Complete M&A Platform
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Built for Excellence
              </span>
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-4xl mx-auto">
              Everything you need to execute M&A deals with precision and speed. 5 core AI-powered
              services, enterprise security, and the tools that drive 90%+ trial-to-paid conversion.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700" asChild>
                <Link to="/sign-up">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-blue-400 text-blue-100 hover:bg-blue-800/20"
              >
                Schedule Demo
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 text-sm">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Services Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              5 Core M&A Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Each service is designed to give you an unfair advantage in M&A, backed by AI and
              built for professionals who demand excellence.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-8">
            {coreServices.map((service, index) => (
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
                      className={`w-16 h-16 rounded-xl bg-gradient-to-r ${service.color} flex items-center justify-center text-white mb-4`}
                    >
                      {service.icon}
                    </div>
                    <CardTitle className="text-xl mb-2">{service.title}</CardTitle>
                    <CardDescription className="text-base">{service.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 mb-6">
                      {service.features.map((feature, i) => (
                        <li key={i} className="flex items-center text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button variant="outline" className="w-full" asChild>
                      <Link to={service.link}>Learn More</Link>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Benefits Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Why Choose Our Platform?</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built from the ground up for M&A professionals who demand the best tools, fastest
              performance, and highest security standards.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {platformBenefits.map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="text-center h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mx-auto mb-4">
                      {benefit.icon}
                    </div>
                    <CardTitle className="text-lg">{benefit.title}</CardTitle>
                    <CardDescription>{benefit.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Overview */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Enterprise-Grade Architecture</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built with modern technologies and best practices to ensure scalability, security, and
              performance at enterprise level.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-lg">Frontend</CardTitle>
                <CardDescription>
                  React, TypeScript, Vite, Tailwind CSS, Framer Motion
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-lg">Backend</CardTitle>
                <CardDescription>Python, FastAPI, SQLAlchemy, PostgreSQL, Redis</CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-lg">AI & Integrations</CardTitle>
                <CardDescription>
                  Claude AI, OpenAI, Clerk Auth, Stripe, Cloudflare R2
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Professional M&A Platform Pricing
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Three tiers designed for different stages of your M&A practice growth.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="text-center border-gray-200">
              <CardHeader>
                <CardTitle className="text-xl">Professional</CardTitle>
                <div className="text-3xl font-bold text-blue-600 mt-4">
                  £99<span className="text-lg text-gray-500">/month</span>
                </div>
                <CardDescription>Perfect for solo M&A professionals</CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center border-blue-500 shadow-lg scale-105">
              <CardHeader>
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
                  Most Popular
                </Badge>
                <CardTitle className="text-xl">Enterprise</CardTitle>
                <div className="text-3xl font-bold text-blue-600 mt-4">
                  £299<span className="text-lg text-gray-500">/month</span>
                </div>
                <CardDescription>For growing M&A teams and firms</CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center border-gray-200">
              <CardHeader>
                <CardTitle className="text-xl">Investment Bank</CardTitle>
                <div className="text-3xl font-bold text-blue-600 mt-4">
                  £999<span className="text-lg text-gray-500">/month</span>
                </div>
                <CardDescription>For large firms and investment banks</CardDescription>
              </CardHeader>
            </Card>
          </div>

          <div className="text-center mt-8">
            <Button size="lg" asChild>
              <Link to="/pricing">View Full Pricing Details</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Transform Your M&A Practice?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join the M&A professionals building their £200M wealth objective with the world's most
              amazing M&A ecosystem platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="bg-white text-blue-600 hover:bg-gray-100"
                asChild
              >
                <Link to="/sign-up">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-white text-white hover:bg-white/10"
              >
                Schedule Demo
              </Button>
            </div>
            <p className="text-blue-200 mt-6 text-sm">
              No credit card required • 14-day free trial • 90%+ conversion guarantee
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default PlatformOverviewPage;
