import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Globe,
  Shield,
  CheckCircle,
  ArrowRight,
  Download,
  Edit3,
  Brain,
} from 'lucide-react';

const TemplateEnginePage = () => {
  const templateCategories = [
    { name: 'Purchase Agreements', count: '45 templates', jurisdictions: '12 countries' },
    { name: 'Due Diligence Checklists', count: '32 templates', jurisdictions: '15 countries' },
    { name: 'Term Sheets', count: '28 templates', jurisdictions: '10 countries' },
    { name: 'Letter of Intent', count: '24 templates', jurisdictions: '14 countries' },
    { name: 'Non-Disclosure Agreements', count: '18 templates', jurisdictions: '20 countries' },
    { name: 'Shareholder Agreements', count: '35 templates', jurisdictions: '8 countries' },
  ];

  const features = [
    {
      icon: <Brain className="h-6 w-6" />,
      title: 'AI-Powered Customization',
      description: 'Intelligent document generation that adapts to your specific deal requirements',
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: 'Multi-Jurisdiction Support',
      description: 'Templates compliant with laws across 20+ countries and jurisdictions',
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Legal Compliance',
      description: 'All templates reviewed and updated by qualified legal professionals',
    },
    {
      icon: <Edit3 className="h-6 w-6" />,
      title: 'Easy Customization',
      description: 'Simple interface to modify templates for your specific needs',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-green-900 via-emerald-900 to-green-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-emerald-500/20 text-emerald-200 border-emerald-400">
              <FileText className="mr-2 h-4 w-4" />
              Professional Template Engine
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              200+ Legal Templates.
              <br />
              <span className="bg-gradient-to-r from-emerald-400 to-green-400 bg-clip-text text-transparent">
                Multi-Jurisdiction Ready.
              </span>
            </h1>
            <p className="text-xl text-green-100 mb-8 max-w-3xl mx-auto">
              Professional-grade legal documents for every M&A scenario. AI-powered customization
              with compliance across 20+ jurisdictions. Never start from scratch again.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700" asChild>
                <Link to="/sign-up">
                  Access Templates
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-emerald-400 text-emerald-100 hover:bg-emerald-800/20"
              >
                Browse Library
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Template Categories Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Complete Template Library</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Every document you need for M&A transactions, professionally drafted and legally
              compliant across multiple jurisdictions.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templateCategories.map((category, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <CardDescription>
                      <div className="flex justify-between items-center mt-2">
                        <span className="text-sm font-medium text-green-600">{category.count}</span>
                        <span className="text-sm text-gray-500">{category.jurisdictions}</span>
                      </div>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="outline" size="sm" className="w-full">
                      <Download className="mr-2 h-4 w-4" />
                      View Templates
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Smart Template Features</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              More than just templates - intelligent document generation with AI-powered
              customization.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-green-600 mx-auto mb-4">
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
      <section className="py-20 bg-gradient-to-br from-green-600 to-emerald-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Access Professional Templates?
            </h2>
            <p className="text-xl text-green-100 mb-8 max-w-2xl mx-auto">
              Get instant access to 200+ professional M&A templates with AI-powered customization.
              Never start from scratch again.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="bg-white text-green-600 hover:bg-gray-100"
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
                View Sample Templates
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default TemplateEnginePage;
