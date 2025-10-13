/**
 * Quick Actions Menu Component
 * Provides quick access to common platform actions
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Plus,
  FileText,
  Users,
  Calendar,
  MessageSquare,
  FolderPlus,
  UserPlus,
  BarChart3,
} from 'lucide-react';

interface QuickActionsMenuProps {
  isOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

const QuickActionsMenu: React.FC<QuickActionsMenuProps> = ({
  isOpen,
  onClose,
  className = '',
}) => {
  const quickActions = [
    {
      group: 'Deals',
      actions: [
        { icon: Plus, label: 'New Deal', shortcut: 'Ctrl+N' },
        { icon: FileText, label: 'Import Deal', shortcut: 'Ctrl+I' },
        { icon: Calendar, label: 'Schedule Meeting', shortcut: 'Ctrl+M' },
      ],
    },
    {
      group: 'Documents',
      actions: [
        { icon: FileText, label: 'Upload Document', shortcut: 'Ctrl+U' },
        { icon: FolderPlus, label: 'Create Folder', shortcut: 'Ctrl+F' },
        { icon: MessageSquare, label: 'Add Comment', shortcut: 'Ctrl+/' },
      ],
    },
    {
      group: 'Team',
      actions: [
        { icon: UserPlus, label: 'Invite Member', shortcut: 'Ctrl+Shift+I' },
        { icon: Users, label: 'Create Team', shortcut: 'Ctrl+T' },
        { icon: BarChart3, label: 'Generate Report', shortcut: 'Ctrl+R' },
      ],
    },
  ];

  return (
    <DropdownMenu open={isOpen} onOpenChange={(open) => !open && onClose?.()}>
      <DropdownMenuTrigger asChild>
        <Button size="sm" className={`bg-blue-600 hover:bg-blue-700 ${className}`}>
          <Plus className="h-4 w-4 mr-2" />
          Quick Actions
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel>Quick Actions</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {quickActions.map((group, groupIndex) => (
          <div key={group.group}>
            <DropdownMenuLabel className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              {group.group}
            </DropdownMenuLabel>
            {group.actions.map((action, actionIndex) => (
              <DropdownMenuItem key={actionIndex} className="flex items-center justify-between">
                <div className="flex items-center">
                  <action.icon className="h-4 w-4 mr-3" />
                  <span>{action.label}</span>
                </div>
                <kbd className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                  {action.shortcut}
                </kbd>
              </DropdownMenuItem>
            ))}
            {groupIndex < quickActions.length - 1 && <DropdownMenuSeparator />}
          </div>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default QuickActionsMenu;
