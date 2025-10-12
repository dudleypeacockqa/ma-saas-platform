import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  FunnelChart,
  Funnel,
  LabelList,
} from 'recharts';
import {
  Users,
  UserPlus,
  Target,
  TrendingUp,
  Mail,
  MessageSquare,
  Plus,
  Edit3,
  Settings,
  Share2,
  Download,
  Upload,
  Play,
  Pause,
  Filter,
  Search,
  Calendar,
  Clock,
  DollarSign,
  Award,
  Zap,
  Eye,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Send,
  UserCheck,
  UserX,
  Star,
  AlertCircle,
  CheckCircle,
  XCircle,
  Phone,
  Building,
  MapPin,
  Globe,
  Smartphone,
  Monitor,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  RefreshCw,
  Bot,
  Workflow,
  MousePointer,
  FileText,
  Video,
  Image,
  ShoppingCart,
  Heart,
} from 'lucide-react';

const LeadGenerationHub = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedLead, setSelectedLead] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  const leadMetrics = {
    totalLeads: 4250,
    newLeads: 342,
    qualifiedLeads: 1487,
    convertedLeads: 289,
    conversionRate: 6.8,
    averageLeadScore: 67,
    totalCampaigns: 18,
    activeCampaigns: 7,
    emailsSent: 28450,
    emailOpenRate: 24.5,
    emailClickRate: 3.8,
    costPerLead: 45.5,
    leadValue: 1250,
    roi: 275,
  };

  const leadSources = [
    { name: 'Website', value: 35, count: 1487, color: '#3B82F6' },
    { name: 'Content Download', value: 22, count: 935, color: '#10B981' },
    { name: 'Webinars', value: 18, count: 765, color: '#F59E0B' },
    { name: 'Social Media', value: 12, count: 510, color: '#8B5CF6' },
    { name: 'Paid Ads', value: 8, count: 340, color: '#EF4444' },
    { name: 'Referrals', value: 5, count: 213, color: '#06B6D4' },
  ];

  const leadQuality = [
    { name: 'Hot Leads', value: 15, count: 638, color: '#EF4444' },
    { name: 'Warm Leads', value: 35, count: 1488, color: '#F59E0B' },
    { name: 'Cold Leads', value: 40, count: 1700, color: '#6B7280' },
    { name: 'Qualified', value: 10, count: 424, color: '#10B981' },
  ];

  const campaignPerformance = [
    { month: 'Aug', leads: 285, qualified: 89, converted: 18, cost: 12950, revenue: 22500 },
    { month: 'Sep', leads: 342, qualified: 124, converted: 28, cost: 15580, revenue: 35000 },
    { month: 'Oct', leads: 398, qualified: 156, converted: 34, cost: 18100, revenue: 42500 },
    { month: 'Nov', leads: 367, qualified: 142, converted: 31, cost: 16700, revenue: 38750 },
    { month: 'Dec', leads: 445, qualified: 178, converted: 42, cost: 20250, revenue: 52500 },
    { month: 'Jan', leads: 189, qualified: 67, converted: 15, cost: 8600, revenue: 18750 },
  ];

  const funnelData = [
    { name: 'Visitors', value: 12500, fill: '#3B82F6' },
    { name: 'Leads', value: 4250, fill: '#10B981' },
    { name: 'Qualified', value: 1487, fill: '#F59E0B' },
    { name: 'Opportunities', value: 425, fill: '#8B5CF6' },
    { name: 'Customers', value: 289, fill: '#EF4444' },
  ];

  const recentLeads = [
    {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah.johnson@techcorp.com',
      company: 'TechCorp Ltd',
      title: 'CFO',
      score: 85,
      quality: 'hot',
      source: 'webinar',
      created: '2025-01-12',
      lastActivity: '2025-01-12',
      status: 'new',
    },
    {
      id: 2,
      name: 'Michael Chen',
      email: 'm.chen@growthpartners.co.uk',
      company: 'Growth Partners',
      title: 'Investment Director',
      score: 72,
      quality: 'warm',
      source: 'content_download',
      created: '2025-01-11',
      lastActivity: '2025-01-12',
      status: 'contacted',
    },
    {
      id: 3,
      name: 'Emma Wilson',
      email: 'emma.wilson@strategic.com',
      company: 'Strategic Advisors',
      title: 'Managing Partner',
      score: 91,
      quality: 'hot',
      source: 'referral',
      created: '2025-01-11',
      lastActivity: '2025-01-11',
      status: 'qualified',
    },
    {
      id: 4,
      name: 'David Brown',
      email: 'david@capitalventures.com',
      company: 'Capital Ventures',
      title: 'Principal',
      score: 58,
      quality: 'warm',
      source: 'paid_ads',
      created: '2025-01-10',
      lastActivity: '2025-01-11',
      status: 'nurturing',
    },
  ];

  const activeCampaigns = [
    {
      id: 1,
      name: 'M&A Valuation Guide Campaign',
      type: 'content_marketing',
      status: 'active',
      startDate: '2025-01-08',
      leads: 89,
      qualified: 23,
      budget: 5000,
      spent: 3200,
      cpl: 35.96,
      conversionRate: 25.8,
    },
    {
      id: 2,
      name: 'Private Equity Email Series',
      type: 'email',
      status: 'active',
      startDate: '2025-01-05',
      leads: 156,
      qualified: 42,
      budget: 2500,
      spent: 1800,
      cpl: 11.54,
      conversionRate: 26.9,
    },
    {
      id: 3,
      name: 'LinkedIn Due Diligence Ads',
      type: 'paid_ads',
      status: 'active',
      startDate: '2025-01-10',
      leads: 67,
      qualified: 18,
      budget: 8000,
      spent: 4500,
      cpl: 67.16,
      conversionRate: 26.9,
    },
  ];

  const automationWorkflows = [
    {
      id: 1,
      name: 'Welcome Series - New Subscribers',
      trigger: 'form_submission',
      status: 'active',
      enrolled: 234,
      completed: 89,
      conversionRate: 38.0,
      steps: 5,
    },
    {
      id: 2,
      name: 'Webinar Follow-up Sequence',
      trigger: 'event_registration',
      status: 'active',
      enrolled: 156,
      completed: 67,
      conversionRate: 43.0,
      steps: 4,
    },
    {
      id: 3,
      name: 'High-Score Lead Nurturing',
      trigger: 'scoring_threshold',
      status: 'active',
      enrolled: 89,
      completed: 34,
      conversionRate: 38.2,
      steps: 7,
    },
  ];

  const MetricCard = ({
    title,
    value,
    change,
    icon: Icon,
    color = 'blue',
    format = 'number',
    subtitle,
  }) => {
    const formattedValue =
      format === 'currency'
        ? `£${value.toLocaleString()}`
        : format === 'percentage'
          ? `${value}%`
          : value.toLocaleString();

    return (
      <div
        className="bg-white rounded-lg shadow-lg p-6 border-l-4"
        style={{ borderLeftColor: color }}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{formattedValue}</p>
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
            {change !== undefined && (
              <div
                className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}
              >
                {change >= 0 ? (
                  <ArrowUp className="w-4 h-4 mr-1" />
                ) : (
                  <ArrowDown className="w-4 h-4 mr-1" />
                )}
                <span>{Math.abs(change)}% vs last month</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-full`} style={{ backgroundColor: `${color}20` }}>
            <Icon className="w-6 h-6" style={{ color }} />
          </div>
        </div>
      </div>
    );
  };

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        isActive ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      {label}
    </button>
  );

  const LeadCard = ({ lead }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{lead.name}</h3>
          <p className="text-sm text-gray-600">
            {lead.title} at {lead.company}
          </p>
          <p className="text-sm text-gray-500">{lead.email}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`px-2 py-1 rounded-full text-xs ${
              lead.quality === 'hot'
                ? 'bg-red-100 text-red-800'
                : lead.quality === 'warm'
                  ? 'bg-yellow-100 text-yellow-800'
                  : lead.quality === 'qualified'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
            }`}
          >
            {lead.quality}
          </span>
          <span
            className={`px-2 py-1 rounded-full text-xs ${
              lead.status === 'new'
                ? 'bg-blue-100 text-blue-800'
                : lead.status === 'contacted'
                  ? 'bg-purple-100 text-purple-800'
                  : lead.status === 'qualified'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-orange-100 text-orange-800'
            }`}
          >
            {lead.status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-xl font-bold text-blue-600">{lead.score}</div>
          <div className="text-sm text-blue-700">Score</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-sm font-medium text-green-600 capitalize">
            {lead.source.replace('_', ' ')}
          </div>
          <div className="text-sm text-green-700">Source</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-sm font-medium text-purple-600">{lead.created}</div>
          <div className="text-sm text-purple-700">Created</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">Last activity: {lead.lastActivity}</div>
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-blue-600">
            <Mail className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-green-600">
            <Phone className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-purple-600">
            <Edit3 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const CampaignCard = ({ campaign }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
          <div className="flex items-center text-sm text-gray-600 space-x-4 mt-1">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {campaign.startDate}
            </div>
            <div className="flex items-center capitalize">
              {campaign.type === 'email' && <Mail className="w-4 h-4 mr-1" />}
              {campaign.type === 'content_marketing' && <FileText className="w-4 h-4 mr-1" />}
              {campaign.type === 'paid_ads' && <Target className="w-4 h-4 mr-1" />}
              {campaign.type.replace('_', ' ')}
            </div>
          </div>
        </div>
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            campaign.status === 'active'
              ? 'bg-green-100 text-green-800'
              : campaign.status === 'paused'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
          }`}
        >
          {campaign.status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{campaign.leads}</div>
          <div className="text-sm text-blue-700">Leads Generated</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{campaign.qualified}</div>
          <div className="text-sm text-green-700">Qualified</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4 text-sm">
        <div className="text-center">
          <div className="font-semibold text-gray-900">£{campaign.cpl.toFixed(2)}</div>
          <div className="text-gray-600">Cost/Lead</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-gray-900">{campaign.conversionRate}%</div>
          <div className="text-gray-600">Conversion</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-gray-900">£{campaign.spent}</div>
          <div className="text-gray-600">Spent</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full"
            style={{ width: `${(campaign.spent / campaign.budget) * 100}%` }}
          ></div>
        </div>
        <div className="ml-4 text-sm text-gray-600">
          {Math.round((campaign.spent / campaign.budget) * 100)}%
        </div>
      </div>
    </div>
  );

  const AutomationCard = ({ automation }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{automation.name}</h3>
          <div className="flex items-center text-sm text-gray-600 mt-1">
            <Bot className="w-4 h-4 mr-1" />
            <span className="capitalize">{automation.trigger.replace('_', ' ')}</span>
            <span className="mx-2">•</span>
            <span>{automation.steps} steps</span>
          </div>
        </div>
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            automation.status === 'active'
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {automation.status}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-xl font-bold text-blue-600">{automation.enrolled}</div>
          <div className="text-sm text-blue-700">Enrolled</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-xl font-bold text-green-600">{automation.completed}</div>
          <div className="text-sm text-green-700">Completed</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-xl font-bold text-purple-600">{automation.conversionRate}%</div>
          <div className="text-sm text-purple-700">Conversion</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {automation.enrolled - automation.completed} active enrollments
        </div>
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-blue-600">
            <Eye className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-green-600">
            <Edit3 className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-purple-600">
            <BarChart3 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Lead Generation & Marketing Hub</h1>
              <p className="text-gray-600">
                Advanced lead scoring, multi-channel campaigns, and automated nurture sequences
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                New Campaign
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <UserPlus className="w-4 h-4 mr-2" />
                Add Lead
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-2 mb-8">
          <TabButton
            id="overview"
            label="Overview"
            isActive={activeTab === 'overview'}
            onClick={setActiveTab}
          />
          <TabButton
            id="leads"
            label="Lead Management"
            isActive={activeTab === 'leads'}
            onClick={setActiveTab}
          />
          <TabButton
            id="campaigns"
            label="Campaigns"
            isActive={activeTab === 'campaigns'}
            onClick={setActiveTab}
          />
          <TabButton
            id="automation"
            label="Automation"
            isActive={activeTab === 'automation'}
            onClick={setActiveTab}
          />
          <TabButton
            id="scoring"
            label="Lead Scoring"
            isActive={activeTab === 'scoring'}
            onClick={setActiveTab}
          />
          <TabButton
            id="analytics"
            label="Analytics"
            isActive={activeTab === 'analytics'}
            onClick={setActiveTab}
          />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Total Leads"
                value={leadMetrics.totalLeads}
                change={15.3}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Qualified Leads"
                value={leadMetrics.qualifiedLeads}
                change={22.7}
                icon={UserCheck}
                color="#10B981"
              />
              <MetricCard
                title="Conversion Rate"
                value={leadMetrics.conversionRate}
                change={8.4}
                icon={Target}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Cost Per Lead"
                value={leadMetrics.costPerLead}
                change={-12.1}
                icon={DollarSign}
                color="#8B5CF6"
                format="currency"
              />
            </div>

            {/* Performance Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Generation Funnel</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <FunnelChart>
                    <Tooltip />
                    <Funnel dataKey="value" data={funnelData} isAnimationActive>
                      <LabelList position="center" fill="#fff" stroke="none" />
                    </Funnel>
                  </FunnelChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Campaign Performance</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={campaignPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="leads"
                      stackId="1"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="qualified"
                      stackId="2"
                      stroke="#10B981"
                      fill="#10B981"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Source and Quality Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Lead Sources</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={leadSources}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {leadSources.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Lead Quality Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={leadQuality}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {leadQuality.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 flex flex-col items-center">
                  <UserPlus className="w-8 h-8 mb-2" />
                  <span className="font-medium">Add Lead</span>
                </button>
                <button className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 flex flex-col items-center">
                  <Mail className="w-8 h-8 mb-2" />
                  <span className="font-medium">Email Campaign</span>
                </button>
                <button className="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700 flex flex-col items-center">
                  <Bot className="w-8 h-8 mb-2" />
                  <span className="font-medium">Automation</span>
                </button>
                <button className="bg-orange-600 text-white p-4 rounded-lg hover:bg-orange-700 flex flex-col items-center">
                  <BarChart3 className="w-8 h-8 mb-2" />
                  <span className="font-medium">Analytics</span>
                </button>
              </div>
            </div>
          </>
        )}

        {/* Lead Management Tab */}
        {activeTab === 'leads' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Lead Management</h2>
              <div className="flex space-x-2">
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </button>
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {recentLeads.map((lead) => (
                <LeadCard key={lead.id} lead={lead} />
              ))}
            </div>
          </div>
        )}

        {/* Campaigns Tab */}
        {activeTab === 'campaigns' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Marketing Campaigns</h2>
              <div className="flex space-x-2">
                <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  New Campaign
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {activeCampaigns.map((campaign) => (
                <CampaignCard key={campaign.id} campaign={campaign} />
              ))}
            </div>
          </div>
        )}

        {/* Automation Tab */}
        {activeTab === 'automation' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Marketing Automation</h2>
              <div className="flex space-x-2">
                <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  New Automation
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {automationWorkflows.map((automation) => (
                <AutomationCard key={automation.id} automation={automation} />
              ))}
            </div>
          </div>
        )}

        {/* Lead Scoring Tab */}
        {activeTab === 'scoring' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Scoring Configuration</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <MetricCard
                  title="Average Score"
                  value={leadMetrics.averageLeadScore}
                  change={5.2}
                  icon={Award}
                  color="#3B82F6"
                />
                <MetricCard
                  title="High Score Leads"
                  value={Math.round(leadMetrics.totalLeads * 0.15)}
                  change={18.7}
                  icon={Star}
                  color="#F59E0B"
                  subtitle="Score > 80"
                />
                <MetricCard
                  title="Scoring Rules"
                  value={12}
                  change={0}
                  icon={Settings}
                  color="#8B5CF6"
                  subtitle="Active rules"
                />
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Scoring Rules</h3>

                <div className="space-y-3">
                  {[
                    {
                      category: 'Demographic',
                      rule: 'Company Size: Enterprise',
                      points: 25,
                      active: true,
                    },
                    {
                      category: 'Behavioral',
                      rule: 'Downloaded 3+ Resources',
                      points: 20,
                      active: true,
                    },
                    { category: 'Engagement', rule: 'Attended Webinar', points: 30, active: true },
                    {
                      category: 'Demographic',
                      rule: 'Job Title: C-Level',
                      points: 35,
                      active: true,
                    },
                    {
                      category: 'Behavioral',
                      rule: 'Visited Pricing Page',
                      points: 15,
                      active: false,
                    },
                  ].map((rule, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                    >
                      <div>
                        <div className="font-medium text-gray-900">{rule.rule}</div>
                        <div className="text-sm text-gray-600">{rule.category}</div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="font-semibold text-blue-600">+{rule.points} pts</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            defaultChecked={rule.active}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    </div>
                  ))}
                </div>

                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Scoring Rule
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Generation Analytics</h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Lead Generation Trends</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={campaignPerformance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="leads" stroke="#3B82F6" strokeWidth={3} />
                      <Line type="monotone" dataKey="qualified" stroke="#10B981" strokeWidth={3} />
                      <Line type="monotone" dataKey="converted" stroke="#F59E0B" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">ROI Analysis</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={campaignPerformance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="cost" fill="#EF4444" />
                      <Bar dataKey="revenue" fill="#10B981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeadGenerationHub;
