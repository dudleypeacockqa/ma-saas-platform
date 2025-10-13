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

  // Integrated M&A Ecosystem Features
  const platformFeatures = [
    {
      icon: <TrendingUp className="h-8 w-8 text-blue-600" />,
      title: 'Complete M&A Platform',
      description:
        'AI-powered deal management with real-time analytics, document collaboration, and advanced workflow automation.',
      benefits: [
        'AI deal analysis & matching',
        'Visual pipeline tracking',
        'Document management',
        'Master admin portal',
      ],
      screenshot: '/screenshots/pipeline-kanban.png',
    },
    {
      icon: <Users className="h-8 w-8 text-purple-600" />,
      title: 'Professional Community',
      description:
        '156+ M&A professionals with monthly networking, deal flow opportunities, and mastermind sessions.',
      benefits: [
        '156+ active professionals',
        'Monthly networking events',
        'Deal flow access',
        'Mastermind sessions',
      ],
      screenshot: '/screenshots/community-networking.png',
    },
    {
      icon: <Target className="h-8 w-8 text-green-600" />,
      title: 'Premium Events',
      description:
        '£497-£2,997 masterclasses with industry leaders. Community leaders earn 20% revenue share on hosted events.',
      benefits: [
        'Premium masterclasses',
        'Industry leader access',
        'Revenue sharing',
        'Event hosting rights',
      ],
      screenshot: '/screenshots/premium-events.png',
    },
    {
      icon: <PlayCircle className="h-8 w-8 text-orange-600" />,
      title: 'StreamYard Studio & Content',
      description:
        'Professional podcast studio with 4K recording, live streaming, AI automation, and multi-platform distribution.',
      benefits: [
        'StreamYard-level recording',
        'AI content automation',
        'Multi-platform streaming',
        'Thought leadership tools',
      ],
      screenshot: '/screenshots/podcast-studio.png',
    },
  ];

  const stats = [
    { value: '£47.5k', label: 'MRR Live Platform', description: '156+ active subscribers' },
    { value: '£200M', label: 'Wealth Target', description: 'Building M&A empire systematically' },
    { value: '4-Tier', label: 'Pricing Structure', description: '£279-£2,997/month premium' },
    { value: '15,420', label: 'Podcast Downloads', description: 'StreamYard-level content' },
  ];

  const testimonials = [
    {
      name: 'Michael Roberts',
      title: 'Principal',
      company: 'Independent M&A Advisor',
      content:
        'The integrated ecosystem approach is brilliant. Platform + community + events + content creation - everything I need to build my practice systematically.',
      avatar: '/avatars/michael-roberts.jpg',
      rating: 5,
    },
    {
      name: 'Emma Thompson',
      title: 'Managing Director',
      company: 'Thompson Capital Partners',
      content:
        'The StreamYard-level podcast studio has transformed my thought leadership. AI automation generates content automatically from each recording.',
      avatar: '/avatars/emma-thompson.jpg',
      rating: 5,
    },
    {
      name: 'David Wilson',
      title: 'Partner',
      company: 'Wilson Advisory Group',
      content:
        'The premium community events provide incredible networking value. As a Community Leader, the revenue sharing model creates additional income streams.',
      avatar: '/avatars/david-wilson.jpg',
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
              <Badge variant="outline" className="mb-4 text-purple-600 border-purple-200">
                Complete M&A Empire • Live & Operational
              </Badge>
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                Build Your £200M
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  M&A Empire
                </span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto">
                The complete integrated ecosystem: SaaS platform + professional community + premium
                events + StreamYard-level podcast studio.
                <strong className="text-blue-600">
                  Join 156+ M&A professionals • £47.5k MRR platform
                </strong>
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/sign-up">
                  <Button
                    size="lg"
                    className="text-lg px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    Join 156+ Professionals
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="lg"
                  className="text-lg px-8 py-3 border-purple-200 text-purple-600"
                >
                  <PlayCircle className="mr-2 h-5 w-5" />
                  StreamYard Demo
                </Button>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                4-tier pricing from £279-£2,997/month • Community + Events + Content Empire included
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
            <h2 className="text-4xl font-bold text-gray-900 mb-4">The Complete M&A Empire</h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto">
              Beyond software - an integrated ecosystem combining platform, community, events, and
              content creation. Everything you need to build your £200M wealth systematically.
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
              Building Wealth Through Community
            </h2>
            <p className="text-xl text-gray-600">
              156+ M&A professionals using our integrated ecosystem to build their empires
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
      <section className="py-24 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Build Your £200M M&A Empire?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join 156+ professionals using our integrated ecosystem. Platform + community + events +
            content creation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/sign-up">
              <Button
                size="lg"
                variant="secondary"
                className="text-lg px-8 py-3 bg-white text-blue-600 hover:bg-gray-100"
              >
                Join The Empire
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/pricing">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-3 text-white border-white hover:bg-blue-700"
              >
                View 4-Tier Pricing
              </Button>
            </Link>
          </div>
          <p className="text-sm text-blue-100 mt-4">
            £47.5k MRR live platform • StreamYard studio included • Community + events access
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
