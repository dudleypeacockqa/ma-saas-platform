import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUser, UserButton } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Search,
  Bell,
  Plus,
  Menu,
  Command,
  HelpCircle,
  Settings,
  Zap,
  TrendingUp,
  FileText,
  Users,
  BarChart3,
} from 'lucide-react';

const PlatformNavbar = ({ onMenuClick, onQuickAction }) => {
  const { user } = useUser();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');

  // Navigation items based on UX specification
  const navItems = [
    {
      name: 'Deals',
      href: '/deals',
      icon: TrendingUp,
      current: location.pathname.startsWith('/deals'),
    },
    {
      name: 'Documents',
      href: '/documents',
      icon: FileText,
      current: location.pathname.startsWith('/documents'),
    },
    { name: 'Teams', href: '/teams', icon: Users, current: location.pathname.startsWith('/teams') },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      current: location.pathname.startsWith('/analytics'),
    },
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    // Implement global search functionality
    console.log('Search:', searchQuery);
  };

  const handleKeyboardShortcut = (e) => {
    // Cmd/Ctrl + K for quick search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      document.getElementById('global-search').focus();
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-16 flex items-center px-4 lg:px-6">
      <div className="flex items-center flex-1">
        {/* Mobile menu button */}
        <Button variant="ghost" size="sm" className="lg:hidden mr-2" onClick={onMenuClick}>
          <Menu className="h-5 w-5" />
        </Button>

        {/* Logo */}
        <Link to="/" className="flex items-center mr-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-2">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="hidden sm:block text-xl font-bold text-gray-900 dark:text-white">
            M&A Platform
          </span>
        </Link>

        {/* Main Navigation - Desktop */}
        <nav className="hidden lg:flex space-x-8">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                item.current
                  ? 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20'
                  : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <item.icon className="h-4 w-4 mr-2" />
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-4">
        {/* Global Search */}
        <form onSubmit={handleSearch} className="hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="global-search"
              type="search"
              placeholder="Search deals, documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 w-64 lg:w-80"
              onKeyDown={handleKeyboardShortcut}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <kbd className="hidden lg:inline-flex items-center rounded border border-gray-200 px-1 font-mono text-xs text-gray-400">
                ⌘K
              </kbd>
            </div>
          </div>
        </form>

        {/* Quick Actions Button */}
        <Button variant="default" size="sm" onClick={onQuickAction} className="hidden sm:flex">
          <Plus className="h-4 w-4 mr-1" />
          New
        </Button>

        {/* Mobile Quick Action */}
        <Button variant="default" size="sm" onClick={onQuickAction} className="sm:hidden">
          <Plus className="h-4 w-4" />
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="h-5 w-5" />
          <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-red-500">3</Badge>
        </Button>

        {/* Help */}
        <Button variant="ghost" size="sm">
          <HelpCircle className="h-5 w-5" />
        </Button>

        {/* User Menu */}
        <UserButton
          appearance={{
            elements: {
              avatarBox: 'w-8 h-8',
            },
          }}
          afterSignOutUrl="/"
        />
      </div>
    </header>
  );
};

export default PlatformNavbar;
