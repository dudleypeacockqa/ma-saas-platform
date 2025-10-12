import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  Menu, 
  X, 
  ChevronDown, 
  BarChart3, 
  Users, 
  FileText, 
  TrendingUp,
  Building2,
  Briefcase,
  Target,
  Shield
} from 'lucide-react'

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState(null)
  const location = useLocation()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navigationItems = [
    {
      name: 'Platform',
      href: '/platform',
      dropdown: [
        { name: 'Deal Pipeline', href: '/platform/pipeline', icon: BarChart3, description: 'Manage your M&A deals from start to finish' },
        { name: 'Team Collaboration', href: '/platform/collaboration', icon: Users, description: 'Work seamlessly with your team and advisors' },
        { name: 'Document Management', href: '/platform/documents', icon: FileText, description: 'Secure document storage and version control' },
        { name: 'Analytics & Insights', href: '/platform/analytics', icon: TrendingUp, description: 'Data-driven insights for better decisions' }
      ]
    },
    {
      name: 'Solutions',
      href: '/solutions',
      dropdown: [
        { name: 'M&A Advisors', href: '/solutions/advisors', icon: Briefcase, description: 'For senior M&A professionals managing multiple deals' },
        { name: 'Deal Teams', href: '/solutions/teams', icon: Users, description: 'For associates and analysts executing transactions' },
        { name: 'Investment Banks', href: '/solutions/banks', icon: Building2, description: 'For large financial institutions' },
        { name: 'Private Equity', href: '/solutions/pe', icon: Target, description: 'For PE firms and portfolio management' }
      ]
    },
    { name: 'Pricing', href: '/pricing' },
    {
      name: 'Resources',
      href: '/resources',
      dropdown: [
        { name: 'Case Studies', href: '/resources/case-studies', icon: FileText, description: 'Success stories from our clients' },
        { name: 'Best Practices', href: '/resources/best-practices', icon: Shield, description: 'M&A industry insights and guides' },
        { name: 'API Documentation', href: '/resources/api', icon: FileText, description: 'Technical documentation for developers' }
      ]
    },
    { name: 'Company', href: '/company' }
  ]

  const isActivePage = (href) => {
    return location.pathname === href || location.pathname.startsWith(href + '/')
  }

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled 
        ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-slate-200' 
        : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform duration-200">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-xl font-bold text-slate-900">100 Days</span>
              <span className="text-xl font-light text-blue-600 ml-1">& Beyond</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            {navigationItems.map((item) => (
              <div
                key={item.name}
                className="relative"
                onMouseEnter={() => item.dropdown && setActiveDropdown(item.name)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  to={item.href}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActivePage(item.href)
                      ? 'text-blue-600 bg-blue-50'
                      : isScrolled
                      ? 'text-slate-700 hover:text-blue-600 hover:bg-slate-50'
                      : 'text-white hover:text-blue-200'
                  }`}
                >
                  <span>{item.name}</span>
                  {item.dropdown && (
                    <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${
                      activeDropdown === item.name ? 'rotate-180' : ''
                    }`} />
                  )}
                </Link>

                {/* Dropdown Menu */}
                {item.dropdown && activeDropdown === item.name && (
                  <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50">
                    {item.dropdown.map((dropdownItem) => (
                      <Link
                        key={dropdownItem.name}
                        to={dropdownItem.href}
                        className="flex items-start space-x-3 px-4 py-3 hover:bg-slate-50 transition-colors duration-200"
                      >
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                          <dropdownItem.icon className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium text-slate-900">{dropdownItem.name}</div>
                          <div className="text-sm text-slate-600 mt-1">{dropdownItem.description}</div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex items-center space-x-4">
            <Link to="/contact">
              <Button variant="ghost" className={`${
                isScrolled ? 'text-slate-700 hover:text-blue-600' : 'text-white hover:text-blue-200'
              }`}>
                Contact Sales
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105">
                Start Free Trial
              </Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              className={`${isScrolled ? 'text-slate-700' : 'text-white'}`}
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="lg:hidden absolute top-full left-0 right-0 bg-white border-b border-slate-200 shadow-lg">
            <div className="px-4 py-6 space-y-4">
              {navigationItems.map((item) => (
                <div key={item.name}>
                  <Link
                    to={item.href}
                    className={`block px-3 py-2 rounded-lg text-base font-medium transition-colors duration-200 ${
                      isActivePage(item.href)
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-slate-700 hover:text-blue-600 hover:bg-slate-50'
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    {item.name}
                  </Link>
                  {item.dropdown && (
                    <div className="ml-4 mt-2 space-y-2">
                      {item.dropdown.map((dropdownItem) => (
                        <Link
                          key={dropdownItem.name}
                          to={dropdownItem.href}
                          className="block px-3 py-2 text-sm text-slate-600 hover:text-blue-600 hover:bg-slate-50 rounded-lg transition-colors duration-200"
                          onClick={() => setIsOpen(false)}
                        >
                          {dropdownItem.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-4 border-t border-slate-200 space-y-3">
                <Link to="/contact" onClick={() => setIsOpen(false)}>
                  <Button variant="outline" className="w-full">
                    Contact Sales
                  </Button>
                </Link>
                <Link to="/dashboard" onClick={() => setIsOpen(false)}>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    Start Free Trial
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navigation
