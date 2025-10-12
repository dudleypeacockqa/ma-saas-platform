import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Filter,
  Plus,
  Search,
  MoreHorizontal,
  TrendingUp,
  Calendar,
  Users,
  PoundSterling,
  Clock,
  ChevronRight,
  List,
  LayoutGrid,
  CalendarDays,
} from 'lucide-react';

const DealsPipeline = () => {
  const [view, setView] = useState('kanban'); // kanban, list, calendar
  const [filteredDeals, setFilteredDeals] = useState([]);

  // Mock deal data based on UX specification
  const dealStages = [
    { id: 'sourcing', name: 'SOURCING', count: 8, value: '£45.2M', color: 'bg-gray-400' },
    { id: 'qualifying', name: 'QUALIFYING', count: 5, value: '£82.5M', color: 'bg-blue-500' },
    {
      id: 'due-diligence',
      name: 'DUE DILIGENCE',
      count: 3,
      value: '£124.3M',
      color: 'bg-purple-500',
    },
    { id: 'negotiation', name: 'NEGOTIATION', count: 4, value: '£95.7M', color: 'bg-orange-500' },
    { id: 'closing', name: 'CLOSING', count: 2, value: '£67.1M', color: 'bg-emerald-500' },
  ];

  const mockDeals = [
    {
      id: 'DEAL-001',
      name: 'TechCo Acquisition',
      targetCompany: 'TechCo Ltd',
      value: '£5.2M',
      stage: 'sourcing',
      priority: 'medium',
      lead: { name: 'J. Smith', avatar: '/avatars/jsmith.jpg', initials: 'JS' },
      tasks: 3,
      progress: 60,
      daysInStage: 12,
      probability: 45,
    },
    {
      id: 'DEAL-005',
      name: 'RetailX Merger',
      targetCompany: 'RetailX Corp',
      value: '£12.8M',
      stage: 'qualifying',
      priority: 'high',
      lead: { name: 'S. Chen', avatar: '/avatars/schen.jpg', initials: 'SC' },
      tasks: 5,
      progress: 80,
      daysInStage: 8,
      probability: 72,
    },
    {
      id: 'DEAL-009',
      name: 'FinServ Integration',
      targetCompany: 'FinServ Inc',
      value: '£45.0M',
      stage: 'due-diligence',
      priority: 'critical',
      lead: { name: 'T. Brown', avatar: '/avatars/tbrown.jpg', initials: 'TB' },
      tasks: 8,
      progress: 100,
      daysInStage: 23,
      probability: 85,
    },
    {
      id: 'DEAL-013',
      name: 'ManuCo Partnership',
      targetCompany: 'ManuCo Ltd',
      value: '£23.5M',
      stage: 'negotiation',
      priority: 'high',
      lead: { name: 'K. Davis', avatar: '/avatars/kdavis.jpg', initials: 'KD' },
      tasks: 2,
      progress: 80,
      daysInStage: 15,
      probability: 78,
    },
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-blue-500';
      case 'low':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getProgressDots = (progress) => {
    const dots = [];
    for (let i = 0; i < 5; i++) {
      dots.push(
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i < Math.floor(progress / 20) ? 'bg-blue-500' : 'bg-gray-300'
          }`}
        />,
      );
    }
    return dots;
  };

  const DealCard = ({ deal }) => (
    <Card className="mb-3 hover:shadow-md transition-shadow cursor-pointer group">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-semibold text-gray-600">{deal.id}</span>
            {deal.priority === 'critical' && (
              <div className={`w-2 h-2 rounded-full ${getPriorityColor(deal.priority)}`} />
            )}
          </div>
          <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>

        <h3 className="font-semibold text-gray-900 mb-1">{deal.name}</h3>
        <p className="text-sm text-gray-600 mb-2">{deal.targetCompany}</p>

        <div className="text-lg font-bold text-gray-900 mb-3">{deal.value}</div>

        <div className="flex items-center space-x-1 mb-3">{getProgressDots(deal.progress)}</div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6">
              <AvatarImage src={deal.lead.avatar} />
              <AvatarFallback className="text-xs">{deal.lead.initials}</AvatarFallback>
            </Avatar>
            <span className="text-sm text-gray-600">{deal.lead.name}</span>
          </div>
          <div className="text-sm text-gray-500">{deal.tasks} tasks</div>
        </div>

        <div className="mt-2 text-xs text-gray-500">
          {deal.daysInStage} days in stage • {deal.probability}% probability
        </div>
      </CardContent>
    </Card>
  );

  const KanbanView = () => (
    <div className="flex space-x-6 overflow-x-auto pb-4">
      {dealStages.map((stage) => (
        <div key={stage.id} className="flex-shrink-0 w-80">
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                <Button variant="ghost" size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>{stage.count} deals</span>
                <span className="font-semibold">{stage.value}</span>
              </div>
            </div>

            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {mockDeals
                .filter((deal) => deal.stage === stage.id)
                .map((deal) => (
                  <Link key={deal.id} to={`/deals/${deal.id}`}>
                    <DealCard deal={deal} />
                  </Link>
                ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Deal Pipeline</h1>
          <p className="text-gray-600">Manage your M&A deals from sourcing to closing</p>
        </div>

        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>

          <Select value={view} onValueChange={setView}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="kanban">
                <div className="flex items-center">
                  <LayoutGrid className="h-4 w-4 mr-2" />
                  Kanban
                </div>
              </SelectItem>
              <SelectItem value="list">
                <div className="flex items-center">
                  <List className="h-4 w-4 mr-2" />
                  List
                </div>
              </SelectItem>
              <SelectItem value="calendar">
                <div className="flex items-center">
                  <CalendarDays className="h-4 w-4 mr-2" />
                  Calendar
                </div>
              </SelectItem>
            </SelectContent>
          </Select>

          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Deal
          </Button>
        </div>
      </div>

      {/* Pipeline Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-blue-500" />
              <span className="text-sm font-medium">Active Deals</span>
            </div>
            <div className="text-2xl font-bold mt-1">22</div>
            <div className="text-sm text-green-600">+15% from last month</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <PoundSterling className="h-5 w-5 text-green-500" />
              <span className="text-sm font-medium">Total Value</span>
            </div>
            <div className="text-2xl font-bold mt-1">£414.8M</div>
            <div className="text-sm text-green-600">+23% from last month</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-500" />
              <span className="text-sm font-medium">Avg. Cycle Time</span>
            </div>
            <div className="text-2xl font-bold mt-1">47 days</div>
            <div className="text-sm text-red-600">+3 days from target</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-500" />
              <span className="text-sm font-medium">Win Rate</span>
            </div>
            <div className="text-2xl font-bold mt-1">72%</div>
            <div className="text-sm text-green-600">+5% from last quarter</div>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Content */}
      {view === 'kanban' && <KanbanView />}

      {view === 'list' && (
        <Card>
          <CardContent className="p-0">
            <div className="text-center py-12">
              <List className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">List View</h3>
              <p className="text-gray-600">List view implementation coming soon</p>
            </div>
          </CardContent>
        </Card>
      )}

      {view === 'calendar' && (
        <Card>
          <CardContent className="p-0">
            <div className="text-center py-12">
              <CalendarDays className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Calendar View</h3>
              <p className="text-gray-600">Calendar view implementation coming soon</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DealsPipeline;
