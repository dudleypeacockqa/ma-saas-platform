import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  TrendingUp,
  TrendingDown,
  PoundSterling,
  Calendar,
  Users,
  AlertCircle,
  BarChart3,
  PieChart,
  Target,
  Clock,
  ChevronUp,
  ChevronDown,
  MoreHorizontal,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const ExecutiveDashboard = () => {
  const [timeFrame, setTimeFrame] = useState('q4-2025');

  // Executive dashboard data based on UX specification
  const pipelineOverview = {
    activeDeals: 23,
    activeDealsChange: 15,
    totalValue: '£347.5M',
    totalValueChange: 23,
    closingQ4: 8,
    closingQ4Value: '£124.3M',
    winRate: 67,
    winRateChange: 5,
  };

  const dealStages = [
    { name: 'Sourcing', count: 8, value: 45.2, color: '#94A3B8' },
    { name: 'Qualifying', count: 5, value: 82.5, color: '#3B82F6' },
    { name: 'Due Diligence', count: 3, value: 124.3, color: '#8B5CF6' },
    { name: 'Negotiation', count: 4, value: 95.7, color: '#F59E0B' },
    { name: 'Closing', count: 3, value: 67.1, color: '#10B981' },
  ];

  const valueDistribution = [
    { name: 'Technology', value: 45, color: '#3B82F6' },
    { name: 'Retail', value: 25, color: '#10B981' },
    { name: 'Finance', value: 20, color: '#F59E0B' },
    { name: 'Other', value: 10, color: '#8B5CF6' },
  ];

  const highPriorityDeals = [
    {
      name: 'TechCo Acquisition',
      value: '£45.2M',
      status: 'Due in 15 days',
      priority: 'critical',
      progress: 85,
    },
    {
      name: 'RetailX Merger',
      value: '£23.8M',
      status: 'Action required',
      priority: 'high',
      progress: 65,
    },
    {
      name: 'FinServ Partnership',
      value: '£67.1M',
      status: 'Under review',
      priority: 'medium',
      progress: 78,
    },
  ];

  const teamPerformance = [
    { name: 'S. Chen', deals: 8, value: '£89.2M', performance: 'excellent' },
    { name: 'J. Mitchell', deals: 6, value: '£67.8M', performance: 'good' },
    { name: 'T. Brown', deals: 5, value: '£45.3M', performance: 'good' },
    { name: 'K. Davis', deals: 4, value: '£34.7M', performance: 'fair' },
  ];

  const monthlyData = [
    { month: 'Jul', deals: 18, value: 245 },
    { month: 'Aug', deals: 22, value: 289 },
    { month: 'Sep', deals: 20, value: 312 },
    { month: 'Oct', deals: 23, value: 348 },
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getPerformanceColor = (performance) => {
    switch (performance) {
      case 'excellent':
        return 'text-green-600';
      case 'good':
        return 'text-blue-600';
      case 'fair':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatCurrency = (value) => {
    if (value >= 1000) {
      return `£${(value / 1000).toFixed(1)}B`;
    }
    return `£${value}M`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard</h1>
          <p className="text-gray-600">October 2025 • Pipeline Overview & Performance</p>
        </div>

        <div className="flex items-center space-x-3">
          <Select value={timeFrame} onValueChange={setTimeFrame}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="q4-2025">Q4 2025</SelectItem>
              <SelectItem value="q3-2025">Q3 2025</SelectItem>
              <SelectItem value="q2-2025">Q2 2025</SelectItem>
              <SelectItem value="ytd">Year to Date</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Pipeline Overview KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Deals</p>
                <p className="text-3xl font-bold text-gray-900">{pipelineOverview.activeDeals}</p>
                <div className="flex items-center mt-1">
                  <ChevronUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">
                    +{pipelineOverview.activeDealsChange}%
                  </span>
                </div>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Value</p>
                <p className="text-3xl font-bold text-gray-900">{pipelineOverview.totalValue}</p>
                <div className="flex items-center mt-1">
                  <ChevronUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">
                    +{pipelineOverview.totalValueChange}%
                  </span>
                </div>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <PoundSterling className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Closing Q4</p>
                <p className="text-3xl font-bold text-gray-900">{pipelineOverview.closingQ4}</p>
                <p className="text-sm text-gray-600 mt-1">{pipelineOverview.closingQ4Value}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <Calendar className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className="text-3xl font-bold text-gray-900">{pipelineOverview.winRate}%</p>
                <div className="flex items-center mt-1">
                  <ChevronUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">+{pipelineOverview.winRateChange}%</span>
                </div>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline by Stage */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Pipeline by Stage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dealStages.map((stage, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: stage.color }} />
                    <span className="text-sm font-medium">{stage.name}</span>
                    <Badge variant="secondary" className="text-xs">
                      {stage.count}
                    </Badge>
                  </div>
                  <span className="text-sm font-semibold">£{stage.value}M</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Value Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Value Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={valueDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {valueDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}%`} />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {valueDistribution.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: item.color }} />
                  <span className="text-sm">
                    {item.name}: {item.value}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* High Priority Deals */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              High Priority Deals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {highPriorityDeals.map((deal, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${getPriorityColor(deal.priority)}`} />
                    <div>
                      <p className="font-medium text-gray-900">{deal.name}</p>
                      <p className="text-sm text-gray-600">{deal.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{deal.value}</p>
                    <p className="text-sm text-gray-600">{deal.progress}% complete</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Team Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Team Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {teamPerformance.map((member, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">
                        {member.name
                          .split(' ')
                          .map((n) => n[0])
                          .join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{member.name}</p>
                      <p
                        className={`text-sm capitalize ${getPerformanceColor(member.performance)}`}
                      >
                        {member.performance}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{member.deals} deals</p>
                    <p className="text-sm text-gray-600">{member.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Performance Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="deals" fill="#3B82F6" name="Active Deals" />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="value"
                  stroke="#10B981"
                  strokeWidth={3}
                  name="Pipeline Value (£M)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExecutiveDashboard;
