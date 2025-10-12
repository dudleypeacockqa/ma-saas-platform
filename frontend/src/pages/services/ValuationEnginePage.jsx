import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  TrendingUp,
  Calculator,
  PieChart,
  CheckCircle,
  ArrowRight,
  Target,
  DollarSign,
} from 'lucide-react';

const ValuationEnginePage = () => {
  const valuationMethods = [
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: 'DCF Analysis',
      description: 'Discounted Cash Flow models with terminal value calculations',
      accuracy: '95%',
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: 'Comparable Companies',
      description: 'Trading multiples analysis from 10,000+ public companies',
      accuracy: '92%',
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: 'Precedent Transactions',
      description: 'Recent M&A transaction data and premium analysis',
      accuracy: '89%',
    },
    {
      icon: <PieChart className="h-8 w-8" />,
      title: 'Monte Carlo Simulation',
      description: 'Risk-adjusted valuations with probability distributions',
      accuracy: '96%',
    },
  ];

  const features = [
    'Real-time market data integration',
    'Industry-specific multiples',
    'Risk-adjusted discount rates',
    'Sensitivity analysis tools',
    'Professional valuation reports',
    'Multiple scenario modeling',
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-purple-500/20 text-purple-200 border-purple-400">
              <BarChart3 className="mr-2 h-4 w-4" />
              Automated Valuation Engine
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Multi-Method Valuation.
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                Precise Results.
              </span>
            </h1>
            <p className="text-xl text-purple-100 mb-8 max-w-3xl mx-auto">
              Professional-grade valuation using DCF, comparable companies, and precedent
              transactions. Monte Carlo simulation for risk-adjusted scenarios.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700" asChild>
                <Link to="/sign-up">
                  Value Companies
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-purple-400 text-purple-100 hover:bg-purple-800/20"
              >
                View Sample Report
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Valuation Methods Section */}
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
              Multiple Valuation Methodologies
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive valuation analysis using industry-standard methodologies for maximum
              accuracy.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {valuationMethods.map((method, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full text-center hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mx-auto mb-4">
                      {method.icon}
                    </div>
                    <CardTitle className="text-lg">{method.title}</CardTitle>
                    <Badge variant="secondary" className="bg-green-100 text-green-800 mb-2">
                      {method.accuracy} accurate
                    </Badge>
                    <CardDescription>{method.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Advanced Valuation Features</h2>
              <p className="text-lg text-gray-600 mb-6">
                Go beyond basic calculations with sophisticated financial modeling and risk analysis
                tools used by investment banks.
              </p>
              <div className="space-y-4">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8"
            >
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Valuation Report Preview</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-white rounded-lg shadow-sm">
                  <span className="font-medium">DCF Valuation</span>
                  <span className="text-purple-600 font-bold">£12.5M</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-white rounded-lg shadow-sm">
                  <span className="font-medium">Comparable Analysis</span>
                  <span className="text-purple-600 font-bold">£11.8M</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-white rounded-lg shadow-sm">
                  <span className="font-medium">Precedent Transactions</span>
                  <span className="text-purple-600 font-bold">£13.2M</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-purple-100 rounded-lg border-2 border-purple-200">
                  <span className="font-bold text-purple-900">Weighted Average</span>
                  <span className="text-purple-900 font-bold text-lg">£12.4M</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready for Professional Valuations?
            </h2>
            <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
              Get investment-grade valuations using multiple methodologies and advanced financial
              modeling.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="bg-white text-purple-600 hover:bg-gray-100"
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

export default ValuationEnginePage;
