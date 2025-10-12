import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Target,
  Brain,
  TrendingUp,
  Users,
  CheckCircle,
  ArrowRight,
  Search,
  BarChart3,
} from 'lucide-react';

const DealMatchingPage = () => {
  const matchingCriteria = [
    {
      name: 'Industry Sector',
      weight: '25%',
      description: 'SIC codes, sub-sectors, and market focus',
    },
    {
      name: 'Company Size',
      weight: '20%',
      description: 'Revenue, EBITDA, and employee count ranges',
    },
    {
      name: 'Geographic Location',
      weight: '15%',
      description: 'Regional preferences and market presence',
    },
    { name: 'Deal Type', weight: '15%', description: 'Strategic vs. financial buyer preferences' },
    {
      name: 'Financial Profile',
      weight: '15%',
      description: 'Profitability, growth rates, and margins',
    },
    { name: 'Strategic Fit', weight: '10%', description: 'Synergies and strategic objectives' },
  ];

  const aiFeatures = [
    {
      icon: <Brain className="h-6 w-6" />,
      title: 'Machine Learning Algorithms',
      description: 'Advanced ML models trained on thousands of successful M&A transactions',
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: 'Compatibility Scoring',
      description: 'Numerical compatibility scores based on 50+ deal factors',
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: 'Market Intelligence',
      description: 'Real-time market data and trend analysis for better matching',
    },
    {
      icon: <Search className="h-6 w-6" />,
      title: 'Intelligent Search',
      description: 'Natural language search with semantic understanding',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-orange-900 via-red-900 to-orange-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-red-500/20 text-red-200 border-red-400">
              <Target className="mr-2 h-4 w-4" />
              Intelligent Deal Matching
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              AI-Powered Matching.
              <br />
              <span className="bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                Perfect Connections.
              </span>
            </h1>
            <p className="text-xl text-orange-100 mb-8 max-w-3xl mx-auto">
              Find the perfect buyers and sellers with AI-powered compatibility scoring. Advanced
              algorithms analyze 50+ factors to identify ideal M&A matches.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-red-600 hover:bg-red-700" asChild>
                <Link to="/sign-up">
                  Find Matches
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-red-400 text-red-100 hover:bg-red-800/20"
              >
                See Demo
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Matching Criteria Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">50+ Matching Criteria</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI analyzes multiple dimensions to find the most compatible buyers and sellers.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {matchingCriteria.map((criteria, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-center mb-2">
                      <CardTitle className="text-lg">{criteria.name}</CardTitle>
                      <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                        {criteria.weight}
                      </Badge>
                    </div>
                    <CardDescription>{criteria.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Advanced AI Technology</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Powered by machine learning algorithms trained on thousands of successful M&A
              transactions.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {aiFeatures.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 mx-auto mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-orange-600 to-red-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">Ready to Find Perfect Matches?</h2>
            <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
              Let AI find the most compatible buyers and sellers for your deals with advanced
              matching algorithms.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="bg-white text-orange-600 hover:bg-gray-100"
                asChild
              >
                <Link to="/sign-up">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default DealMatchingPage;
