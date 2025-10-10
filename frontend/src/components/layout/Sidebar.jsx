import { Link, useLocation } from 'react-router-dom'
import { Briefcase, Mic, Settings, Newspaper, DollarSign, Home, BarChart3, Users, FileText } from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard', icon: <Home className="h-5 w-5" /> },
    { href: '/deals', label: 'Deals', icon: <Briefcase className="h-5 w-5" /> },
    { href: '/podcast', label: 'Podcast', icon: <Mic className="h-5 w-5" /> },
    { href: '/analytics', label: 'Analytics', icon: <BarChart3 className="h-5 w-5" /> },
    { href: '/documents', label: 'Documents', icon: <FileText className="h-5 w-5" /> },
    { href: '/team', label: 'Team', icon: <Users className="h-5 w-5" /> },
  ]

  const bottomLinks = [
    { href: '/settings', label: 'Settings', icon: <Settings className="h-5 w-5" /> },
    { href: '/pricing', label: 'Billing', icon: <DollarSign className="h-5 w-5" /> },
    { href: '/blog', label: 'Blog', icon: <Newspaper className="h-5 w-5" /> },
  ]

  const isActive = (href) => location.pathname === href

  return (
    <aside className="hidden md:flex flex-col w-64 border-r bg-background">
      <div className="flex-1 overflow-y-auto">
        <nav className="p-4 space-y-2">
          {navLinks.map(link => (
            <Link
              key={link.href}
              to={link.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${isActive(link.href) ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}>
              {link.icon}
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="p-4 border-t">
        <nav className="space-y-2">
          {bottomLinks.map(link => (
            <Link
              key={link.href}
              to={link.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${isActive(link.href) ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}>
              {link.icon}
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar
