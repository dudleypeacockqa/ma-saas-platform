import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useUser } from '@clerk/clerk-react';
import {
  TrendingUp,
  FileText,
  Users,
  BarChart3,
  Plus,
  Search,
  Bell,
  Settings,
  HelpCircle,
  Menu,
  X,
} from 'lucide-react';
import PlatformNavbar from '@/components/platform/PlatformNavbar';
import PlatformSidebar from '@/components/platform/PlatformSidebar';
import QuickActionsMenu from '@/components/platform/QuickActionsMenu';

const PlatformLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  const { user } = useUser();

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <PlatformSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <PlatformNavbar
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onQuickAction={() => setQuickActionsOpen(true)}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>

      {/* Quick Actions Menu */}
      <QuickActionsMenu isOpen={quickActionsOpen} onClose={() => setQuickActionsOpen(false)} />
    </div>
  );
};

export default PlatformLayout;
