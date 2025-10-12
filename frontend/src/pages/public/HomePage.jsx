import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ArrowRight,
  TrendingUp,
  Users,
  FileText,
  BarChart3,
  Shield,
  Zap,
  CheckCircle,
  Star,
  Building2,
  Target,
  PoundSterling,
  ChevronRight,
  PlayCircle,
} from 'lucide-react';

const HomePage = () => {
  const [activeFeature, setActiveFeature] = useState(0);

  // M&A specific features based on UX specification
  const platformFeatures = [
    {
      icon: <TrendingUp className="h-8 w-8 text-blue-600" />,
      title: 'Deal Pipeline Management',
      description:
        'Professional Kanban-style pipeline with deal stages from sourcing to closing. Track millions in deal value.',
      benefits: [
        'Visual pipeline tracking',
        'Stage-based workflows',
        'Deal progress monitoring',
        'Value tracking',
      ],
      screenshot: '/screenshots/pipeline-kanban.png',
    },
    {
      icon: <FileText className="h-8 w-8 text-purple-600" />,
      title: 'Document Collaboration',
      description:
        'Enterprise-grade document management with real-time collaboration, version control, and secure sharing.',
      benefits: [
        'Secure document storage',
        'Real-time collaboration',
        'Version control',
        'Comment threading',
      ],
      screenshot: '/screenshots/document-collaboration.png',
    },
    {
      icon: <Users className="h-8 w-8 text-green-600" />,
      title: 'Team Management',
      description:
        'Coordinate deal teams with role-based permissions, workload management, and activity tracking.',
      benefits: ['Role-based access', 'Team coordination', 'Workload balancing', 'Activity feeds'],
      screenshot: '/screenshots/team-management.png',
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-orange-600" />,
      title: 'Executive Analytics',
      description:
        'Data-driven insights with executive dashboards, pipeline analytics, and performance metrics.',
      benefits: [
        'Executive dashboards',
        'Pipeline insights',
        'Performance tracking',
        'Custom reports',
      ],
      screenshot: '/screenshots/executive-analytics.png',
    },
  ];

  const stats = [
    { value: '£40M+', label: 'Deal Value Managed', description: 'Annual deal volume tracked' },
    { value: '200+', label: 'M&A Professionals', description: 'Active users on platform' },
    { value: '95%', label: 'Deal Success Rate', description: 'Completion rate improvement' },
    { value: '60%', label: 'Time Savings', description: 'Faster deal processing' },
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      title: 'Senior M&A Advisor',
      company: 'Goldman Sachs',
      content:
        'This platform has revolutionized how we manage our deal pipeline. The visual tracking and collaboration tools are game-changing.',
      avatar: '/avatars/sarah-chen.jpg',
      rating: 5,
    },
    {
      name: 'James Mitchell',
      title: 'Managing Director',
      company: 'JP Morgan',
      content:
        'Finally, a platform built specifically for M&A professionals. The analytics give us insights we never had before.',
      avatar: '/avatars/james-mitchell.jpg',
      rating: 5,
    },
    {
      name: 'Victoria Hammond',
      title: 'Partner',
      company: 'Rothschild & Co',
      content:
        'The document collaboration features have streamlined our due diligence process significantly.',
      avatar: '/avatars/victoria-hammond.jpg',
      rating: 5,
    },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Badge variant="outline" className="mb-4 text-blue-600 border-blue-200">
                Professional M&A Platform
              </Badge>
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                Enterprise M&A Deal
                <br />
                <span className="text-blue-600">Management Platform</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                The only platform built specifically for M&A professionals. Manage deals from
                sourcing to closing with enterprise-grade security, collaboration, and analytics.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/sign-up">
                  <Button size="lg" className="text-lg px-8 py-3">
                    Start 14-Day Free Trial
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Button variant="outline" size="lg" className="text-lg px-8 py-3">
                  <PlayCircle className="mr-2 h-5 w-5" />
                  Watch Demo
                </Button>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                Trusted by M&A teams at Goldman Sachs, JP Morgan, and Rothschild & Co
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-lg font-semibold text-gray-900 mb-1">{stat.label}</div>
                <div className="text-sm text-gray-600">{stat.description}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Built for M&A Professionals</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Every feature designed specifically for the complexities of mergers and acquisitions.
              No generic CRM adaptations.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Feature tabs */}
            <div className="space-y-4">
              {platformFeatures.map((feature, index) => (
                <motion.div
                  key={index}
                  className={`p-6 rounded-xl cursor-pointer transition-all duration-300 ${
                    activeFeature === index
                      ? 'bg-blue-50 border-2 border-blue-200'
                      : 'bg-white border-2 border-gray-100 hover:border-gray-200'
                  }`}
                  onClick={() => setActiveFeature(index)}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">{feature.icon}</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-gray-600 mb-3">{feature.description}</p>
                      <ul className="space-y-1">
                        {feature.benefits.map((benefit, idx) => (
                          <li key={idx} className="flex items-center text-sm text-gray-600">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <ChevronRight
                      className={`h-5 w-5 text-gray-400 transition-transform ${
                        activeFeature === index ? 'rotate-90 text-blue-600' : ''
                      }`}
                    />
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Feature screenshot */}
            <div className="lg:pl-8">
              <motion.div
                key={activeFeature}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="bg-gray-100 rounded-xl p-8 aspect-video flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    {platformFeatures[activeFeature].icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {platformFeatures[activeFeature].title}
                  </h3>
                  <p className="text-gray-600">Interactive screenshot placeholder</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Top M&A Professionals
            </h2>
            <p className="text-xl text-gray-600">
              Leading investment banks and advisory firms rely on our platform
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="h-full">
                  <CardContent className="p-6">
                    <div className="flex mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <p className="text-gray-600 mb-6 italic">"{testimonial.content}"</p>
                    <div className="flex items-center">
                      <div className="w-12 h-12 bg-gray-200 rounded-full mr-4" />
                      <div>
                        <div className="font-semibold text-gray-900">{testimonial.name}</div>
                        <div className="text-sm text-gray-600">{testimonial.title}</div>
                        <div className="text-sm text-blue-600">{testimonial.company}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your M&A Process?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of M&A professionals who have streamlined their deal management
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/sign-up">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-3">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/contact">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-3 text-white border-white hover:bg-blue-700"
              >
                Schedule Demo
              </Button>
            </Link>
          </div>
          <p className="text-sm text-blue-100 mt-4">
            14-day free trial • No credit card required • Setup in minutes
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
