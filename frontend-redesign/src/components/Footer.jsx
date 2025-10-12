import { Link } from 'react-router-dom'
import { BarChart3, Mail, Phone, MapPin, Twitter, Linkedin, Github } from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerSections = [
    {
      title: 'Platform',
      links: [
        { name: 'Deal Pipeline', href: '/platform/pipeline' },
        { name: 'Team Collaboration', href: '/platform/collaboration' },
        { name: 'Document Management', href: '/platform/documents' },
        { name: 'Analytics & Insights', href: '/platform/analytics' }
      ]
    },
    {
      title: 'Solutions',
      links: [
        { name: 'M&A Advisors', href: '/solutions/advisors' },
        { name: 'Deal Teams', href: '/solutions/teams' },
        { name: 'Investment Banks', href: '/solutions/banks' },
        { name: 'Private Equity', href: '/solutions/pe' }
      ]
    },
    {
      title: 'Resources',
      links: [
        { name: 'Case Studies', href: '/resources/case-studies' },
        { name: 'Best Practices', href: '/resources/best-practices' },
        { name: 'API Documentation', href: '/resources/api' },
        { name: 'Help Center', href: '/resources/help' }
      ]
    },
    {
      title: 'Company',
      links: [
        { name: 'About Us', href: '/company/about' },
        { name: 'Careers', href: '/company/careers' },
        { name: 'Press', href: '/company/press' },
        { name: 'Contact', href: '/contact' }
      ]
    }
  ]

  return (
    <footer className="bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center space-x-2 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold">100 Days</span>
                <span className="text-xl font-light text-blue-400 ml-1">& Beyond</span>
              </div>
            </Link>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              The only platform you need to manage, track, and close M&A deals faster. 
              Built by dealmakers, for dealmakers.
            </p>

            <div className="space-y-3">
              <div className="flex items-center text-slate-300">
                <Mail className="w-5 h-5 mr-3 text-blue-400" />
                <a href="mailto:hello@100daysandbeyond.com" className="hover:text-white transition-colors">
                  hello@100daysandbeyond.com
                </a>
              </div>
              <div className="flex items-center text-slate-300">
                <Phone className="w-5 h-5 mr-3 text-blue-400" />
                <a href="tel:+442071234567" className="hover:text-white transition-colors">
                  +44 (0) 207 123 4567
                </a>
              </div>
              <div className="flex items-center text-slate-300">
                <MapPin className="w-5 h-5 mr-3 text-blue-400" />
                <span>London, United Kingdom</span>
              </div>
            </div>
          </div>

          {/* Navigation Sections */}
          {footerSections.map((section) => (
            <div key={section.title} className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-4">{section.title}</h3>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.href}
                      className="text-slate-300 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="border-t border-slate-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-8">
              <p className="text-slate-400 text-sm">
                © {currentYear} 100 Days & Beyond. All rights reserved.
              </p>
              <div className="flex space-x-6 text-sm">
                <Link to="/legal/privacy" className="text-slate-400 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
                <Link to="/legal/terms" className="text-slate-400 hover:text-white transition-colors">
                  Terms of Service
                </Link>
                <Link to="/legal/cookies" className="text-slate-400 hover:text-white transition-colors">
                  Cookie Policy
                </Link>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex space-x-4 mt-4 md:mt-0">
              <a
                href="https://twitter.com/100daysandbeyond"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors duration-200"
              >
                <Twitter className="w-5 h-5 text-slate-400 hover:text-white" />
              </a>
              <a
                href="https://linkedin.com/company/100daysandbeyond"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors duration-200"
              >
                <Linkedin className="w-5 h-5 text-slate-400 hover:text-white" />
              </a>
              <a
                href="https://github.com/100daysandbeyond"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors duration-200"
              >
                <Github className="w-5 h-5 text-slate-400 hover:text-white" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="border-t border-slate-800 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center text-slate-400 text-sm">
            <div className="flex items-center space-x-6 mb-4 md:mb-0">
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                SOC 2 Compliant
              </span>
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                GDPR Ready
              </span>
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                99.9% Uptime
              </span>
            </div>
            <div className="text-xs">
              Trusted by 500+ M&A professionals managing £50B+ in transactions
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
