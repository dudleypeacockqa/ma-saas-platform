import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  ArrowRight, 
  BarChart3, 
  Users, 
  FileText, 
  TrendingUp,
  CheckCircle,
  Star,
  Play,
  Shield,
  Zap,
  Globe,
  Award,
  ChevronRight,
  Building2,
  Target,
  Clock
} from 'lucide-react'

const HomePage = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)
  const [isVisible, setIsVisible] = useState({})

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Managing Director, Goldman Sachs",
      company: "Goldman Sachs",
      content: "100 Days and Beyond transformed how we manage our M&A pipeline. We've reduced deal cycle time by 40% and increased our success rate significantly.",
      rating: 5,
      dealValue: "£2.3B in deals closed"
    },
    {
      name: "James Mitchell",
      role: "Partner, KKR",
      company: "KKR",
      content: "The platform's analytics capabilities give us unprecedented visibility into our deal performance. It's become indispensable for our investment committee.",
      rating: 5,
      dealValue: "£1.8B portfolio value"
    },
    {
      name: "Victoria Hammond",
      role: "Head of M&A, Barclays",
      company: "Barclays",
      content: "Finally, a platform built by dealmakers for dealmakers. The collaboration features have revolutionized how our teams work together on complex transactions.",
      rating: 5,
      dealValue: "£3.1B in transactions"
    }
  ]

  const features = [
    {
      icon: BarChart3,
      title: "Deal Pipeline Management",
      description: "Track and manage your M&A deals from initial contact to closing with our intuitive pipeline system.",
      benefits: ["Visual deal tracking", "Automated workflows", "Progress monitoring"],
      color: "blue"
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Collaborate seamlessly with your team, clients, and advisors throughout the deal process.",
      benefits: ["Real-time collaboration", "Role-based permissions", "Communication tools"],
      color: "green"
    },
    {
      icon: FileText,
      title: "Document Management",
      description: "Securely store, organize, and share deal documents with advanced version control.",
      benefits: ["Secure document storage", "Version control", "Easy sharing"],
      color: "purple"
    },
    {
      icon: TrendingUp,
      title: "Analytics & Insights",
      description: "Get data-driven insights into your deal performance and market trends.",
      benefits: ["Performance analytics", "Market insights", "Custom reports"],
      color: "orange"
    }
  ]

  const stats = [
    { value: "£50B+", label: "Deals Managed", icon: Target },
    { value: "500+", label: "Active Users", icon: Users },
    { value: "40%", label: "Faster Closings", icon: Clock },
    { value: "99.9%", label: "Uptime", icon: Shield }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }))
          }
        })
      },
      { threshold: 0.1 }
    )

    document.querySelectorAll('[id]').forEach((el) => {
      observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Hero Content */}
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center px-4 py-2 bg-blue-500/20 rounded-full text-blue-200 text-sm font-medium mb-6 backdrop-blur-sm">
                <Award className="w-4 h-4 mr-2" />
                Trusted by Top Investment Banks
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
                Master M&A in
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                  100 Days & Beyond
                </span>
              </h1>
              
              <p className="text-xl text-blue-100 mb-8 leading-relaxed">
                The only platform you need to manage, track, and close M&A deals faster. 
                Built by dealmakers, for dealmakers. Join 500+ professionals managing £50B+ in transactions.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Link to="/dashboard">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-200 hover:scale-105 shadow-xl">
                    Start Free Trial
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-200 backdrop-blur-sm"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Watch Demo
                </Button>
              </div>

              <div className="flex items-center justify-center lg:justify-start space-x-6 text-blue-200">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                  <span>14-day free trial</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                  <span>No credit card required</span>
                </div>
              </div>
            </div>

            {/* Hero Visual */}
            <div className="relative">
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
                <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between text-white mb-4">
                    <h3 className="font-semibold">Deal Pipeline</h3>
                    <BarChart3 className="w-5 h-5" />
                  </div>
                  <div className="grid grid-cols-4 gap-2">
                    {['Sourcing', 'Qualifying', 'Due Diligence', 'Closing'].map((stage, index) => (
                      <div key={stage} className="bg-white/20 rounded p-2 text-center">
                        <div className="text-xs text-blue-100">{stage}</div>
                        <div className="text-lg font-bold">{[8, 5, 3, 2][index]}</div>
                        <div className="text-xs text-blue-200">£{[45.2, 82.5, 124.3, 95.7][index]}M</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  {['TechCo Acquisition - £45.2M', 'RetailX Merger - £23.8M', 'FinServ Deal - £67.1M'].map((deal, index) => (
                    <div key={deal} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium text-sm">{deal.split(' - ')[0]}</div>
                        <div className="text-blue-200 text-xs">{deal.split(' - ')[1]}</div>
                      </div>
                      <div className="flex space-x-1">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <div 
                            key={i} 
                            className={`w-2 h-2 rounded-full ${
                              i < [4, 3, 5][index] ? 'bg-green-400' : 'bg-white/20'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-blue-500/20 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-cyan-500/20 rounded-full blur-xl animate-pulse delay-1000"></div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={stat.label} className="text-center group">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-xl mb-4 group-hover:bg-blue-200 transition-colors duration-200">
                  <stat.icon className="w-8 h-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-2">{stat.value}</div>
                <div className="text-slate-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className={`py-20 bg-slate-50 transition-all duration-1000 ${
        isVisible.features ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Everything you need to close deals faster
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our comprehensive platform provides all the tools and insights you need to manage 
              complex M&A transactions from start to finish.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {features.map((feature, index) => (
              <div 
                key={feature.title}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 group border border-slate-200"
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-${feature.color}-100 rounded-xl mb-6 group-hover:scale-110 transition-transform duration-200`}>
                  <feature.icon className={`w-8 h-8 text-${feature.color}-600`} />
                </div>
                
                <h3 className="text-2xl font-bold text-slate-900 mb-4">{feature.title}</h3>
                <p className="text-slate-600 mb-6 leading-relaxed">{feature.description}</p>
                
                <ul className="space-y-3 mb-6">
                  {feature.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-center text-slate-700">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                      {benefit}
                    </li>
                  ))}
                </ul>

                <Link to="/platform" className="inline-flex items-center text-blue-600 font-semibold hover:text-blue-700 transition-colors duration-200">
                  Learn more
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className={`py-20 bg-white transition-all duration-1000 ${
        isVisible.testimonials ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Trusted by industry leaders
            </h2>
            <p className="text-xl text-slate-600">
              See what top M&A professionals are saying about our platform
            </p>
          </div>

          <div className="relative max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 lg:p-12 border border-blue-100">
              <div className="flex items-center mb-6">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                ))}
              </div>
              
              <blockquote className="text-xl lg:text-2xl text-slate-700 mb-8 leading-relaxed">
                "{testimonials[currentTestimonial].content}"
              </blockquote>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center text-white font-bold text-xl mr-4">
                    {testimonials[currentTestimonial].name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-bold text-slate-900">{testimonials[currentTestimonial].name}</div>
                    <div className="text-slate-600">{testimonials[currentTestimonial].role}</div>
                    <div className="text-sm text-blue-600 font-semibold">{testimonials[currentTestimonial].company}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">{testimonials[currentTestimonial].dealValue}</div>
                  <div className="text-sm text-slate-600">Managed on platform</div>
                </div>
              </div>
            </div>

            {/* Testimonial Navigation */}
            <div className="flex justify-center mt-8 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-200 ${
                    index === currentTestimonial ? 'bg-blue-600' : 'bg-slate-300 hover:bg-slate-400'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to transform your M&A process?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join hundreds of M&A professionals who are already closing deals faster with our platform.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/dashboard">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-200 hover:scale-105">
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link to="/contact">
              <Button 
                size="lg" 
                variant="outline" 
                className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-200"
              >
                Contact Sales
              </Button>
            </Link>
          </div>

          <div className="mt-8 text-blue-200">
            <p>14-day free trial • No credit card required • Cancel anytime</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
