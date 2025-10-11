import { Link } from 'react-router-dom'
import { Briefcase, Twitter, Linkedin, Youtube } from 'lucide-react'

const Footer = () => {
  const footerLinks = {
    'Platform': [
      { href: '/deals', label: 'Deals' },
      { href: '/podcast', label: 'Podcast' },
      { href: '/analytics', label: 'Analytics' },
      { href: '/documents', label: 'Documents' },
    ],
    'Company': [
      { href: '/about', label: 'About Us' },
      { href: '/blog', label: 'Blog' },
      { href: '/careers', label: 'Careers' },
      { href: '/contact', label: 'Contact' },
    ],
    'Resources': [
      { href: '/help', label: 'Help Center' },
      { href: '/api-docs', label: 'API' },
      { href: '/terms', label: 'Terms of Service' },
      { href: '/privacy', label: 'Privacy Policy' },
    ],
  }

  const socialLinks = [
    { href: '#', icon: <Twitter className="h-6 w-6" /> },
    { href: '#', icon: <Linkedin className="h-6 w-6" /> },
    { href: '#', icon: <Youtube className="h-6 w-6" /> },
  ]

  return (
    <footer className="bg-background border-t">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl">
              <Briefcase className="h-7 w-7 text-blue-600" />
              <span>100 Days & Beyond</span>
            </Link>
            <p className="mt-4 text-muted-foreground text-sm">
              The ultimate M&A platform for dealmakers.
            </p>
          </div>
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase">{title}</h3>
              <ul className="mt-4 space-y-2">
                {links.map(link => (
                  <li key={link.href}>
                    <Link to={link.href} className="text-base text-muted-foreground hover:text-foreground">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 border-t pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-base text-muted-foreground md:order-1">
            &copy; {new Date().getFullYear()} 100 Days & Beyond. All rights reserved.
          </p>
          <div className="flex space-x-6 md:order-2 mt-4 md:mt-0">
            {socialLinks.map((link, index) => (
              <a key={index} href={link.href} className="text-muted-foreground hover:text-foreground">
                {link.icon}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
