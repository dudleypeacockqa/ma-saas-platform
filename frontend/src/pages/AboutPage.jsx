import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Target,
  Users,
  Lightbulb,
  TrendingUp,
  Shield,
  Globe,
  ArrowRight,
  CheckCircle,
  Award,
  Briefcase,
} from 'lucide-react';

const AboutPage = () => {
  const milestones = [
    {
      year: '2024',
      title: 'Platform Launch',
      description: "Launched the world's most amazing M&A ecosystem platform with 5 core services",
    },
    {
      year: '2024',
      title: 'AI Integration',
      description:
        'Integrated advanced AI capabilities with Claude and OpenAI for intelligent automation',
    },
    {
      year: '2024',
      title: 'Market Validation',
      description:
        'Achieved 90%+ trial-to-paid conversion rate, validating our unique value proposition',
    },
    {
      year: '2025',
      title: 'Global Expansion',
      description: 'Expanding to serve M&A professionals across multiple jurisdictions worldwide',
    },
  ];

  const values = [
    {
      icon: <Target className="h-8 w-8" />,
      title: 'Excellence First',
      description:
        'We build tools that M&A professionals love to use because they deliver exceptional results',
    },
    {
      icon: <Lightbulb className="h-8 w-8" />,
      title: 'Innovation Driven',
      description: 'Leveraging cutting-edge AI and technology to solve real M&A challenges',
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: 'Client Success',
      description:
        "Your success is our success. We're committed to helping you achieve your wealth objectives",
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: 'Trust & Security',
      description:
        'Enterprise-grade security and compliance you can trust with your most sensitive deals',
    },
  ];

  const teamStats = [
    { number: '15+', label: 'Years Combined M&A Experience' },
    { number: '50+', label: 'Deals Closed Using Our Platform' },
    { number: '£2B+', label: 'Total Deal Value Processed' },
    { number: '90%+', label: 'Client Success Rate' },
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
              About 100 Days and Beyond
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Building the Future of
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                M&A Excellence
              </span>
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-4xl mx-auto">
              We're on a mission to revolutionize how M&A professionals work, combining advanced AI,
              professional-grade tools, and enterprise security to create the world's most amazing
              M&A ecosystem platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700" asChild>
                <Link to="/platform">
                  Explore Platform
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-blue-400 text-blue-100 hover:bg-blue-800/20"
                asChild
              >
                <Link to="/sign-up">Start Free Trial</Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Our Mission: Democratizing M&A Excellence
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                M&A shouldn't be limited to the largest investment banks with infinite resources.
                Every professional deserves access to world-class tools, AI-powered insights, and
                the ability to execute deals with precision and speed.
              </p>
              <p className="text-lg text-gray-600 mb-6">
                That's why we built the world's most amazing M&A ecosystem platform - to level the
                playing field and give every M&A professional the tools they need to achieve their
                £200M wealth objective.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-gray-700">5 AI-powered core services in one platform</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-gray-700">90%+ trial-to-paid conversion guarantee</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-gray-700">Enterprise-grade security and compliance</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-gray-700">Global multi-jurisdiction support</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8"
            >
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Platform Vision</h3>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center text-white">
                    <Target className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">£200M Valuation Target</h4>
                    <p className="text-gray-600 text-sm">
                      Building a platform valued at £200M by delivering exceptional value to M&A
                      professionals worldwide.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center text-white">
                    <TrendingUp className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">90%+ Conversion Rate</h4>
                    <p className="text-gray-600 text-sm">
                      Creating such compelling value that 9 out of 10 trial users become paying
                      customers.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center text-white">
                    <Globe className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Global M&A Platform</h4>
                    <p className="text-gray-600 text-sm">
                      The go-to platform for M&A professionals across all markets and jurisdictions.
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Core Values</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The principles that guide everything we do as we build the world's most amazing M&A
              ecosystem platform.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="text-center h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mx-auto mb-4">
                      {value.icon}
                    </div>
                    <CardTitle className="text-lg">{value.title}</CardTitle>
                    <CardDescription>{value.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Journey</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From concept to the world's most amazing M&A ecosystem platform.
            </p>
          </motion.div>

          <div className="relative">
            <div className="absolute left-1/2 transform -translate-x-1/2 w-0.5 h-full bg-blue-200"></div>
            <div className="space-y-12">
              {milestones.map((milestone, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className={`relative flex items-center ${index % 2 === 0 ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`w-5/12 ${index % 2 === 0 ? 'pr-8 text-right' : 'pl-8 text-left'}`}
                  >
                    <Card>
                      <CardHeader>
                        <div
                          className={`flex items-center ${index % 2 === 0 ? 'justify-end' : 'justify-start'} mb-2`}
                        >
                          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                            {milestone.year}
                          </Badge>
                        </div>
                        <CardTitle className="text-lg">{milestone.title}</CardTitle>
                        <CardDescription>{milestone.description}</CardDescription>
                      </CardHeader>
                    </Card>
                  </div>
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full border-4 border-white"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team Stats */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Proven Track Record</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our team's experience and the platform's performance speak for themselves.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamStats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
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
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Join Our Mission</h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Be part of the revolution in M&A. Join thousands of professionals who are already
              building their wealth with the world's most amazing M&A ecosystem platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="bg-white text-blue-600 hover:bg-gray-100"
                asChild
              >
                <Link to="/sign-up">
                  Start Your Journey
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-white text-white hover:bg-white/10"
                asChild
              >
                <Link to="/platform">Explore Platform</Link>
              </Button>
            </div>
            <p className="text-blue-200 mt-6 text-sm">
              No credit card required • 14-day free trial • Join the £200M journey
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
