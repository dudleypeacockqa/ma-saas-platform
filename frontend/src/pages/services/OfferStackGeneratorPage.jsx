import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Calculator,
  FileSpreadsheet,
  Presentation,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  DollarSign,
  PieChart,
} from 'lucide-react';

const OfferStackGeneratorPage = () => {
  const scenarios = [
    {
      name: 'Cash Offer',
      description: 'Full cash acquisition with immediate liquidity',
      popularity: '35%',
    },
    {
      name: 'Stock + Cash',
      description: 'Mixed consideration for balanced risk/reward',
      popularity: '28%',
    },
    {
      name: 'Earnout Structure',
      description: 'Performance-based payments over time',
      popularity: '22%',
    },
    {
      name: 'Debt Financing',
      description: 'Leveraged buyout with debt component',
      popularity: '15%',
    },
  ];

  const exportFormats = [
    {
      icon: <FileSpreadsheet className="h-8 w-8" />,
      title: 'Excel Workbooks',
      description: 'Detailed financial models with formulas and assumptions',
    },
    {
      icon: <Presentation className="h-8 w-8" />,
      title: 'PowerPoint Presentations',
      description: 'Professional pitch decks ready for stakeholder meetings',
    },
    {
      icon: <PieChart className="h-8 w-8" />,
      title: 'Interactive Dashboards',
      description: 'Real-time scenarios with drag-and-drop parameters',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-900 via-violet-900 to-purple-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-violet-500/20 text-violet-200 border-violet-400">
              <Calculator className="mr-2 h-4 w-4" />
              Interactive Offer Stack Generator
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Professional Offers.
              <br />
              <span className="bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
                Multiple Scenarios.
              </span>
            </h1>
            <p className="text-xl text-purple-100 mb-8 max-w-3xl mx-auto">
              Create compelling offer presentations with multiple funding scenarios. Export to Excel
              and PowerPoint for professional stakeholder presentations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-violet-600 hover:bg-violet-700" asChild>
                <Link to="/sign-up">
                  Generate Offers
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-violet-400 text-violet-100 hover:bg-violet-800/20"
              >
                View Examples
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Scenarios Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Multiple Funding Scenarios</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Present various deal structures to maximize acceptance rates and optimize terms.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {scenarios.map((scenario, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{scenario.name}</CardTitle>
                    <Badge variant="secondary" className="w-fit">
                      {scenario.popularity} popular
                    </Badge>
                    <CardDescription>{scenario.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Export Formats Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Professional Export Options</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Share your offer stacks in the formats your stakeholders expect.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {exportFormats.map((format, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mx-auto mb-4">
                      {format.icon}
                    </div>
                    <CardTitle className="text-xl">{format.title}</CardTitle>
                    <CardDescription>{format.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-purple-600 to-violet-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">Ready to Create Winning Offers?</h2>
            <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
              Generate professional offer stacks with multiple scenarios and export to
              Excel/PowerPoint.
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

export default OfferStackGeneratorPage;
