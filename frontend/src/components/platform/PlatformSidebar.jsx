import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  TrendingUp,
  FileText,
  Users,
  BarChart3,
  Calendar,
  Archive,
  Trash2,
  Settings,
  X,
  ChevronDown,
  ChevronRight,
  Home,
  PlusCircle,
  Clock,
  Star,
  Filter,
} from 'lucide-react';
import { useState } from 'react';

const PlatformSidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState({
    deals: true,
    documents: false,
    teams: false,
    analytics: false,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Navigation structure based on UX specification
  const navigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: Home,
      current: location.pathname === '/',
    },
    {
      name: 'Deals',
      icon: TrendingUp,
      current: location.pathname.startsWith('/deals'),
      expandable: true,
      section: 'deals',
      children: [
        { name: 'Pipeline View', href: '/deals/pipeline', badge: '23' },
        { name: 'List View', href: '/deals/list' },
        { name: 'Calendar View', href: '/deals/calendar' },
        { name: 'My Deals', href: '/deals/my', badge: '8' },
        { name: 'Archived Deals', href: '/deals/archived' },
      ],
    },
    {
      name: 'Documents',
      icon: FileText,
      current: location.pathname.startsWith('/documents'),
      expandable: true,
      section: 'documents',
      children: [
        { name: 'Document Library', href: '/documents' },
        { name: 'Templates', href: '/documents/templates' },
        { name: 'Recent Documents', href: '/documents/recent' },
        { name: 'Shared with Me', href: '/documents/shared' },
        { name: 'Trash', href: '/documents/trash', icon: Trash2 },
      ],
    },
    {
      name: 'Teams',
      icon: Users,
      current: location.pathname.startsWith('/teams'),
      expandable: true,
      section: 'teams',
      children: [
        { name: 'Team Overview', href: '/teams' },
        { name: 'Members', href: '/teams/members' },
        { name: 'Workload', href: '/teams/workload' },
        { name: 'Activity Feed', href: '/teams/activity' },
        { name: 'Settings', href: '/teams/settings', icon: Settings },
      ],
    },
    {
      name: 'Analytics',
      icon: BarChart3,
      current: location.pathname.startsWith('/analytics'),
      expandable: true,
      section: 'analytics',
      children: [
        { name: 'Executive Dashboard', href: '/analytics/executive' },
        { name: 'Pipeline Analytics', href: '/analytics/pipeline' },
        { name: 'Performance Metrics', href: '/analytics/performance' },
        { name: 'Financial Analysis', href: '/analytics/financial' },
        { name: 'Custom Reports', href: '/analytics/reports' },
      ],
    },
  ];

  const quickActions = [
    { name: 'New Deal', icon: PlusCircle, action: 'new-deal' },
    { name: 'Upload Document', icon: FileText, action: 'upload-doc' },
    { name: 'Create Task', icon: Clock, action: 'create-task' },
    { name: 'Schedule Meeting', icon: Calendar, action: 'schedule-meeting' },
  ];

  const NavItem = ({ item, depth = 0 }) => {
    const isExpanded = item.expandable && expandedSections[item.section];

    return (
      <div>
        <Link
          to={item.href || '#'}
          onClick={
            item.expandable
              ? (e) => {
                  e.preventDefault();
                  toggleSection(item.section);
                }
              : undefined
          }
          className={cn(
            'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
            depth > 0 && 'ml-6',
            item.current
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700',
          )}
        >
          <item.icon className={cn('flex-shrink-0 h-5 w-5 mr-3')} />
          <span className="flex-1">{item.name}</span>

          {item.badge && (
            <Badge variant="secondary" className="ml-2 h-5 text-xs">
              {item.badge}
            </Badge>
          )}

          {item.expandable && (
            <div className="ml-2">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </div>
          )}
        </Link>

        {/* Submenu */}
        {item.expandable && isExpanded && item.children && (
          <div className="mt-1 space-y-1">
            {item.children.map((child) => (
              <Link
                key={child.name}
                to={child.href}
                className={cn(
                  'group flex items-center pl-11 pr-3 py-2 text-sm font-medium rounded-md transition-colors',
                  location.pathname === child.href
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700',
                )}
              >
                {child.icon && <child.icon className="flex-shrink-0 h-4 w-4 mr-3" />}
                <span className="flex-1">{child.name}</span>
                {child.badge && (
                  <Badge variant="secondary" className="ml-2 h-5 text-xs">
                    {child.badge}
                  </Badge>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden bg-gray-600 bg-opacity-75" onClick={onClose} />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 lg:hidden">
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              M&A Platform
            </span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <NavItem key={item.name} item={item} />
            ))}
          </nav>

          {/* Quick Actions */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              Quick Actions
            </h3>
            <div className="space-y-1">
              {quickActions.map((action) => (
                <Button
                  key={action.name}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => console.log(action.action)}
                >
                  <action.icon className="h-4 w-4 mr-3" />
                  {action.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Settings */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <Link
              to="/settings"
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700"
            >
              <Settings className="h-5 w-5 mr-3" />
              Settings
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default PlatformSidebar;
