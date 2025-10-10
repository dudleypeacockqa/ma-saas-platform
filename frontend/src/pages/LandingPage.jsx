import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  ArrowRight, 
  TrendingUp, 
  Users, 
  FileText, 
  BarChart3, 
  Zap, 
  Shield, 
  Globe,
  CheckCircle,
  Star,
  Play
} from 'lucide-react'
import '../App.css'

const LandingPage = () => {
  const [activeFeature, setActiveFeature] = useState(0)

  const features = [
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Deal Pipeline Management",
      description: "Track and manage your M&A deals from initial contact to closing with our intuitive pipeline system.",
      benefits: ["Visual deal tracking", "Automated workflows", "Progress monitoring"]
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Team Collaboration",
      description: "Collaborate seamlessly with your team, clients, and advisors throughout the deal process.",
      benefits: ["Real-time collaboration", "Role-based permissions", "Communication tools"]
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: "Document Management",
      description: "Securely store, organize, and share deal documents with advanced version control.",
      benefits: ["Secure document storage", "Version control", "Easy sharing"]
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Analytics & Insights",
      description: "Get data-driven insights into your deal performance and market trends.",
      benefits: ["Performance analytics", "Market insights", "Custom reports"]
    }
  ]

  const pricingPlans = [
    {
      name: "Solo Dealmaker",
      price: "$279",
      period: "/month",
      description: "Perfect for individual professionals starting their M&A journey",
      features: [
        "Up to 3 team members",
        "10 active deals",
        "50GB storage",
        "Basic analytics",
        "Email support",
        "Deal pipeline management"
      ],
      popular: false
    },
    {
      name: "Growth Firm",
      price: "$798",
      period: "/month",
      description: "For growing M&A teams and mid-size firms",
      features: [
        "Up to 15 team members",
        "50 active deals",
        "200GB storage",
        "Advanced analytics",
        "Priority support",
        "AI-powered insights",
        "Team collaboration tools",
        "Workflow automation"
      ],
      popular: true
    },
    {
      name: "Enterprise",
      price: "$1,598",
      period: "/month",
      description: "For large firms and investment banks",
      features: [
        "Unlimited team members",
        "Unlimited deals",
        "1TB storage",
        "Custom analytics",
        "Dedicated support",
        "White labeling",
        "SSO integration",
        "Custom integrations",
        "Audit logs"
      ],
      popular: false
    }
  ]

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Managing Director, Apex Capital",
      content: "100 Days and Beyond transformed our deal management process. We've closed 40% more deals since implementing the platform.",
      rating: 5
    },
    {
      name: "Michael Rodriguez",
      role: "Partner, Sterling M&A",
      content: "The analytics and insights have been game-changing for our firm. We can now identify trends and opportunities we never saw before.",
      rating: 5
    },
    {
      name: "Emily Watson",
      role: "VP Corporate Development, TechFlow",
      content: "The collaboration features make it easy to work with our advisors and legal teams. Everything is in one place.",
      rating: 5
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge variant="secondary" className="mb-6">
              🚀 Now in Beta - Join the Future of M&A
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-6">
              Master M&A in
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {" "}100 Days
              </span>
              <br />
              and Beyond
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              The only platform you need to manage, track, and close M&A deals faster. 
              Built by dealmakers, for dealmakers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8 py-4" asChild>
                <Link to="/sign-up">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4">
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
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
              Everything you need to close deals faster
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              From initial contact to deal closing, our platform streamlines every step of the M&A process.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className={`p-6 rounded-lg border cursor-pointer transition-all ${
                    activeFeature === index
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-2 rounded-lg ${
                      activeFeature === index
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                    }`}>
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300 mb-3">
                        {feature.description}
                      </p>
                      <ul className="space-y-1">
                        {feature.benefits.map((benefit, i) => (
                          <li key={i} className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                            {benefit}
                          </li>
                        ))}
                      </ul>
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
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
                <div className="mb-6">
                  {features[activeFeature].icon}
                </div>
                <h3 className="text-2xl font-bold mb-4">
                  {features[activeFeature].title}
                </h3>
                <p className="text-blue-100 mb-6">
                  {features[activeFeature].description}
                </p>
                <div className="space-y-3">
                  {features[activeFeature].benefits.map((benefit, i) => (
                    <div key={i} className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-300 mr-3" />
                      <span className="text-blue-100">{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
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
              Simple, transparent pricing
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Choose the plan that fits your needs. All plans include a 14-day free trial.
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
                <Card className={`relative h-full ${
                  plan.popular 
                    ? 'border-blue-500 shadow-lg scale-105' 
                    : 'border-gray-200 dark:border-gray-700'
                }`}>
                  {plan.popular && (
                    <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
                      Most Popular
                    </Badge>
                  )}
                  <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">{plan.price}</span>
                      <span className="text-gray-500 dark:text-gray-400">{plan.period}</span>
                    </div>
                    <CardDescription className="mt-2">
                      {plan.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-center">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                          <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className="w-full" 
                      variant={plan.popular ? "default" : "outline"}
                      asChild
                    >
                      <Link to="/sign-up">
                        Start Free Trial
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
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
              Trusted by M&A professionals worldwide
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              See what our customers are saying about their experience with 100 Days and Beyond.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full">
                  <CardContent className="p-6">
                    <div className="flex mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      "{testimonial.content}"
                    </p>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {testimonial.name}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {testimonial.role}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-purple-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to transform your M&A process?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join thousands of M&A professionals who are already using 100 Days and Beyond 
              to close deals faster and more efficiently.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-4" asChild>
                <Link to="/sign-up">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-blue-600">
                Schedule Demo
              </Button>
            </div>
            <p className="text-blue-200 mt-4 text-sm">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default LandingPage
