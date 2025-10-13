import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ArrowRight,
  Users,
  Calendar,
  TrendingUp,
  Star,
  Building2,
  Target,
  PoundSterling,
  Network,
  Crown,
  Gift,
  Handshake,
  Award,
  MessageCircle,
  UserPlus,
  BarChart3,
} from 'lucide-react';

const CommunityPage = () => {
  const [activeTab, setActiveTab] = useState('networking');

  const communityStats = [
    { value: '156+', label: 'Active Members', description: 'M&A professionals worldwide' },
    { value: '£47.5k', label: 'Monthly Revenue', description: 'Live platform generating income' },
    { value: '12+', label: 'Monthly Events', description: 'Networking and masterclasses' },
    { value: '20%', label: 'Revenue Share', description: 'For Community Leaders' },
  ];

  const membershipTiers = [
    {
      tier: 'Solo Dealmaker',
      price: '£279/month',
      color: 'blue',
      features: [
        'Community access and networking',
        'Monthly networking events',
        'Deal flow opportunities',
        'Mastermind session access',
        'Professional directory listing',
        'M&A resource library',
      ],
    },
    {
      tier: 'Growth Firm',
      price: '£798/month',
      color: 'purple',
      popular: true,
      features: [
        'Everything in Solo Dealmaker',
        'VIP community events',
        'Advanced networking features',
        'Priority deal matching',
        'Team collaboration tools',
        'Enhanced community profile',
      ],
    },
    {
      tier: 'Enterprise',
      price: '£1,598/month',
      color: 'green',
      features: [
        'Everything in Growth Firm',
        'Event hosting rights',
        'Premium community features',
        'Custom networking events',
        'White-label community access',
        'Dedicated community manager',
      ],
    },
    {
      tier: 'Community Leader',
      price: '£2,997/month',
      color: 'gold',
      premium: true,
      features: [
        'Everything in Enterprise',
        '20% revenue share on events',
        'Personal thought leader showcase',
        'LP introduction services',
        'Program leadership opportunities',
        'Industry influence platform',
      ],
    },
  ];

  const communityFeatures = {
    networking: {
      title: 'Professional Networking',
      description: 'Connect with 156+ M&A professionals worldwide',
      features: [
        {
          icon: <Users className="h-6 w-6 text-blue-600" />,
          title: 'Member Directory',
          description: 'Searchable directory of M&A professionals with expertise matching',
        },
        {
          icon: <MessageCircle className="h-6 w-6 text-blue-600" />,
          title: 'Direct Messaging',
          description: 'Private messaging system for deal discussions and partnerships',
        },
        {
          icon: <Network className="h-6 w-6 text-blue-600" />,
          title: 'Industry Groups',
          description: 'Sector-specific groups for focused networking and knowledge sharing',
        },
        {
          icon: <Handshake className="h-6 w-6 text-blue-600" />,
          title: 'Deal Matching',
          description: 'AI-powered matching system for complementary deal opportunities',
        },
      ],
    },
    events: {
      title: 'Premium Events',
      description: 'Exclusive masterclasses and networking events',
      features: [
        {
          icon: <Calendar className="h-6 w-6 text-purple-600" />,
          title: 'Monthly Masterclasses',
          description: '£497-£2,997 premium events with industry thought leaders',
        },
        {
          icon: <Crown className="h-6 w-6 text-purple-600" />,
          title: 'VIP Networking',
          description: 'Exclusive networking events for higher-tier members',
        },
        {
          icon: <Award className="h-6 w-6 text-purple-600" />,
          title: 'Industry Summits',
          description: 'Annual conferences featuring top M&A professionals',
        },
        {
          icon: <Gift className="h-6 w-6 text-purple-600" />,
          title: 'Revenue Sharing',
          description: 'Community leaders earn 20% of revenue from hosted events',
        },
      ],
    },
    leadership: {
      title: 'Community Leadership',
      description: 'Become an industry thought leader',
      features: [
        {
          icon: <Star className="h-6 w-6 text-gold-600" />,
          title: 'Thought Leadership',
          description: 'Personal showcase and industry influence platform',
        },
        {
          icon: <TrendingUp className="h-6 w-6 text-gold-600" />,
          title: 'Revenue Generation',
          description: 'Multiple income streams through community leadership',
        },
        {
          icon: <Building2 className="h-6 w-6 text-gold-600" />,
          title: 'LP Introductions',
          description: 'Direct access to limited partners and institutional investors',
        },
        {
          icon: <Target className="h-6 w-6 text-gold-600" />,
          title: 'Program Leadership',
          description: 'Lead specialized programs and build your personal brand',
        },
      ],
    },
  };

  const successStories = [
    {
      name: 'Michael Chen',
      title: 'Independent M&A Advisor',
      story:
        'Through the community, I connected with 3 strategic partners and closed 2 major deals worth £15M total.',
      result: '£15M in deals closed',
      tier: 'Growth Firm',
    },
    {
      name: 'Sarah Williams',
      title: 'Managing Director, Williams Capital',
      story:
        'The networking events introduced me to key LPs. I raised £50M for my new fund within 6 months.',
      result: '£50M fund raised',
      tier: 'Enterprise',
    },
    {
      name: 'David Thompson',
      title: 'Community Leader',
      story:
        'As a Community Leader, I earn £8k+ monthly from event revenue sharing while building my thought leadership.',
      result: '£8k+ monthly passive income',
      tier: 'Community Leader',
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
                Professional M&A Community • 156+ Members
              </Badge>
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                The Premier
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  M&A Community
                </span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto">
                Connect with 156+ M&A professionals, access exclusive events, and build your empire
                through strategic networking.
                <strong className="text-blue-600">
                  {' '}
                  Revenue sharing opportunities for leaders.
                </strong>
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/sign-up">
                  <Button
                    size="lg"
                    className="text-lg px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    Join The Community
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button
                    variant="outline"
                    size="lg"
                    className="text-lg px-8 py-3 border-purple-200 text-purple-600"
                  >
                    View Membership Tiers
                  </Button>
                </Link>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                4-tier membership from £279-£2,997/month • Revenue sharing for Community Leaders
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {communityStats.map((stat, index) => (
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

      {/* Community Features Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Community Features</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Professional networking, exclusive events, and leadership opportunities for M&A
              professionals
            </p>
          </div>

          {/* Feature Tabs */}
          <div className="flex justify-center mb-12">
            <div className="bg-gray-100 rounded-lg p-1 inline-flex">
              {Object.keys(communityFeatures).map((key) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`px-6 py-3 rounded-md font-medium transition-all ${
                    activeTab === key
                      ? 'bg-white shadow-md text-gray-900'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {communityFeatures[key].title}
                </button>
              ))}
            </div>
          </div>

          {/* Active Feature Content */}
          <div className="max-w-4xl mx-auto">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {communityFeatures[activeTab].title}
                </h3>
                <p className="text-gray-600">{communityFeatures[activeTab].description}</p>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {communityFeatures[activeTab].features.map((feature, index) => (
                  <Card key={index}>
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0 mt-1">{feature.icon}</div>
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900 mb-2">
                            {feature.title}
                          </h4>
                          <p className="text-gray-600">{feature.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Membership Tiers */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Community Membership Tiers</h2>
            <p className="text-xl text-gray-600">
              Choose your level of community engagement and revenue opportunity
            </p>
          </div>

          <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-6">
            {membershipTiers.map((tier, index) => (
              <Card
                key={index}
                className={`relative ${
                  tier.popular
                    ? 'border-purple-500 shadow-xl scale-105 z-10'
                    : tier.premium
                      ? 'border-yellow-500 shadow-xl'
                      : 'border-gray-200'
                }`}
              >
                {tier.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-purple-500">
                    Most Popular
                  </Badge>
                )}
                {tier.premium && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-500">
                    Premium
                  </Badge>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-xl font-bold">{tier.tier}</CardTitle>
                  <div className="text-2xl font-bold text-blue-600 mt-2">{tier.price}</div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-start">
                        <Users className="h-4 w-4 text-green-500 mr-2 flex-shrink-0 mt-1" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Success Stories */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Community Success Stories</h2>
            <p className="text-xl text-gray-600">Real results from our community members</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {successStories.map((story, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="h-full">
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      <Badge variant="outline" className="mr-2">
                        {story.tier}
                      </Badge>
                      <div className="text-lg font-bold text-green-600">{story.result}</div>
                    </div>
                    <p className="text-gray-600 mb-4 italic">"{story.story}"</p>
                    <div className="border-t pt-4">
                      <div className="font-semibold text-gray-900">{story.name}</div>
                      <div className="text-sm text-blue-600">{story.title}</div>
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
            Ready to Join the Premier M&A Community?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Connect with 156+ professionals, access exclusive events, and build revenue-generating
            partnerships
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/sign-up">
              <Button
                size="lg"
                variant="secondary"
                className="text-lg px-8 py-3 bg-white text-blue-600 hover:bg-gray-100"
              >
                Join Community
                <UserPlus className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/pricing">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-3 text-white border-white hover:bg-blue-700"
              >
                View All Tiers
              </Button>
            </Link>
          </div>
          <p className="text-sm text-blue-100 mt-4">
            Start with £279/month • Revenue sharing available • Community Leader tier: £2,997/month
          </p>
        </div>
      </section>
    </div>
  );
};

export default CommunityPage;
