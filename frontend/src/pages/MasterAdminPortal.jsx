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
} from 'recharts';
import {
  DollarSign,
  Users,
  TrendingUp,
  TrendingDown,
  Calendar,
  PlayCircle,
  FileText,
  Mail,
  Settings,
  Plus,
  Download,
  Eye,
  MousePointer,
  UserCheck,
  CreditCard,
  AlertCircle,
  Target,
  Zap,
  Award,
  Globe,
} from 'lucide-react';

const MasterAdminPortal = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for demonstration
  const mockDashboardData = {
    dashboard_metrics: {
      mrr: 47500,
      arr: 570000,
      active_subscribers: 156,
      churn_rate: 3.2,
      ltv: 12500,
      cac: 185,
      trial_conversion_rate: 28.5,
      revenue_growth: 15.7,
    },
    subscription_metrics: {
      total_subscriptions: 189,
      active_subscriptions: 156,
      trial_subscriptions: 23,
      cancelled_subscriptions: 10,
      upgrade_rate: 8.3,
      downgrade_rate: 2.1,
      payment_failures: 3,
      revenue_by_plan: {
        Starter: 14850,
        Professional: 23700,
        Enterprise: 8950,
      },
    },
    content_metrics: {
      podcast_downloads: 15420,
      video_views: 8750,
      blog_post_views: 12300,
      content_engagement_rate: 7.8,
      lead_generation_from_content: 245,
      top_performing_content: [
        { title: 'M&A Valuation Masterclass', type: 'video', views: 2100 },
        { title: 'Due Diligence Checklist', type: 'blog', views: 1850 },
        { title: 'Private Equity Trends 2025', type: 'podcast', downloads: 3200 },
      ],
    },
    lead_metrics: {
      total_leads: 1247,
      qualified_leads: 312,
      conversion_rate: 25.0,
      lead_sources: { website: 45, podcast: 23, linkedin: 18, referral: 14 },
      pipeline_value: 125000,
      average_deal_size: 2500,
    },
    event_metrics: {
      upcoming_events: 4,
      total_attendees: 156,
      attendance_rate: 78.5,
      revenue_from_events: 12500,
      member_engagement_score: 8.2,
    },
  };

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDashboardData(mockDashboardData);
      setLoading(false);
    }, 1000);
  }, [selectedTimeRange]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-GB').format(num);
  };

  const MetricCard = ({ title, value, change, icon: Icon, color = 'blue', format = 'number' }) => {
    const formattedValue =
      format === 'currency'
        ? formatCurrency(value)
        : format === 'percentage'
          ? `${value}%`
          : formatNumber(value);

    return (
      <div
        className="bg-white rounded-lg shadow-lg p-6 border-l-4"
        style={{ borderLeftColor: color }}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{formattedValue}</p>
            {change !== undefined && (
              <div
                className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}
              >
                {change >= 0 ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Master Admin Portal...</p>
        </div>
      </div>
    );
  }

  const revenueData = [
    { month: 'Jan', revenue: 35000, subscribers: 120 },
    { month: 'Feb', revenue: 38500, subscribers: 128 },
    { month: 'Mar', revenue: 42000, subscribers: 142 },
    { month: 'Apr', revenue: 45200, subscribers: 151 },
    { month: 'May', revenue: 47500, subscribers: 156 },
  ];

  const leadSourceData = Object.entries(dashboardData.lead_metrics.lead_sources).map(
    ([source, count]) => ({
      name: source.charAt(0).toUpperCase() + source.slice(1),
      value: count,
    }),
  );

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Master Admin Portal</h1>
              <p className="text-gray-600">Complete business management for your M&A SaaS empire</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Download className="w-4 h-4 mr-2" />
                Export Report
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
            id="subscriptions"
            label="Subscriptions"
            isActive={activeTab === 'subscriptions'}
            onClick={setActiveTab}
          />
          <TabButton
            id="content"
            label="Content"
            isActive={activeTab === 'content'}
            onClick={setActiveTab}
          />
          <TabButton
            id="marketing"
            label="Marketing"
            isActive={activeTab === 'marketing'}
            onClick={setActiveTab}
          />
          <TabButton
            id="events"
            label="Events"
            isActive={activeTab === 'events'}
            onClick={setActiveTab}
          />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Monthly Recurring Revenue"
                value={dashboardData.dashboard_metrics.mrr}
                change={dashboardData.dashboard_metrics.revenue_growth}
                icon={DollarSign}
                color="#10B981"
                format="currency"
              />
              <MetricCard
                title="Active Subscribers"
                value={dashboardData.dashboard_metrics.active_subscribers}
                change={8.2}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Churn Rate"
                value={dashboardData.dashboard_metrics.churn_rate}
                change={-1.1}
                icon={TrendingDown}
                color="#EF4444"
                format="percentage"
              />
              <MetricCard
                title="Customer LTV"
                value={dashboardData.dashboard_metrics.ltv}
                change={12.5}
                icon={Target}
                color="#8B5CF6"
                format="currency"
              />
            </div>

            {/* Revenue Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Revenue Growth</h2>
                <div className="text-sm text-gray-600">
                  ARR: {formatCurrency(dashboardData.dashboard_metrics.arr)}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => formatCurrency(value)} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Area type="monotone" dataKey="revenue" stroke="#3B82F6" fill="#3B82F620" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Secondary Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <MetricCard
                title="Trial Conversion Rate"
                value={dashboardData.dashboard_metrics.trial_conversion_rate}
                change={3.2}
                icon={UserCheck}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Customer Acquisition Cost"
                value={dashboardData.dashboard_metrics.cac}
                change={-8.5}
                icon={CreditCard}
                color="#10B981"
                format="currency"
              />
              <MetricCard
                title="Lead Generation"
                value={dashboardData.content_metrics.lead_generation_from_content}
                change={18.7}
                icon={Zap}
                color="#8B5CF6"
              />
            </div>

            {/* Lead Sources Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Sources</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={leadSourceData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {leadSourceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-4">
                  {leadSourceData.map((source, index) => (
                    <div key={source.name} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div
                          className="w-4 h-4 rounded-full mr-3"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <span className="font-medium">{source.name}</span>
                      </div>
                      <span className="text-gray-600">{source.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {/* Subscriptions Tab */}
        {activeTab === 'subscriptions' && (
          <div className="space-y-6">
            {/* Subscription Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Total Subscriptions"
                value={dashboardData.subscription_metrics.total_subscriptions}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Active Subscriptions"
                value={dashboardData.subscription_metrics.active_subscriptions}
                icon={UserCheck}
                color="#10B981"
              />
              <MetricCard
                title="Trial Subscriptions"
                value={dashboardData.subscription_metrics.trial_subscriptions}
                icon={Eye}
                color="#F59E0B"
              />
              <MetricCard
                title="Payment Failures"
                value={dashboardData.subscription_metrics.payment_failures}
                icon={AlertCircle}
                color="#EF4444"
              />
            </div>

            {/* Revenue by Plan */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Revenue by Plan</h2>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Promo Code
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(dashboardData.subscription_metrics.revenue_by_plan).map(
                  ([plan, revenue]) => (
                    <div key={plan} className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-semibold text-gray-900">{plan}</h3>
                      <p className="text-2xl font-bold text-blue-600">{formatCurrency(revenue)}</p>
                      <p className="text-sm text-gray-600">Monthly revenue</p>
                    </div>
                  ),
                )}
              </div>
            </div>

            {/* Subscription Management Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Subscription Management</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 flex items-center justify-center">
                  <Plus className="w-5 h-5 mr-2" />
                  New Subscription
                </button>
                <button className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 flex items-center justify-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  Billing Issues
                </button>
                <button className="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 flex items-center justify-center">
                  <Award className="w-5 h-5 mr-2" />
                  Loyalty Program
                </button>
                <button className="bg-orange-600 text-white px-4 py-3 rounded-lg hover:bg-orange-700 flex items-center justify-center">
                  <Target className="w-5 h-5 mr-2" />
                  Win-Back Campaign
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div className="space-y-6">
            {/* Content Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Podcast Downloads"
                value={dashboardData.content_metrics.podcast_downloads}
                icon={PlayCircle}
                color="#8B5CF6"
              />
              <MetricCard
                title="Video Views"
                value={dashboardData.content_metrics.video_views}
                icon={Eye}
                color="#3B82F6"
              />
              <MetricCard
                title="Blog Post Views"
                value={dashboardData.content_metrics.blog_post_views}
                icon={FileText}
                color="#10B981"
              />
              <MetricCard
                title="Engagement Rate"
                value={dashboardData.content_metrics.content_engagement_rate}
                icon={MousePointer}
                color="#F59E0B"
                format="percentage"
              />
            </div>

            {/* Content Creation Studio */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Content Creation Studio</h2>
                <div className="flex space-x-2">
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center">
                    <PlayCircle className="w-4 h-4 mr-2" />
                    Record Podcast
                  </button>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                    <Eye className="w-4 h-4 mr-2" />
                    Create Video
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Write Blog Post
                  </button>
                </div>
              </div>

              {/* Top Performing Content */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Top Performing Content</h3>
                {dashboardData.content_metrics.top_performing_content.map((content, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <div
                        className={`p-2 rounded-full mr-4 ${
                          content.type === 'video'
                            ? 'bg-blue-100'
                            : content.type === 'blog'
                              ? 'bg-green-100'
                              : 'bg-purple-100'
                        }`}
                      >
                        {content.type === 'video' ? (
                          <Eye className="w-5 h-5 text-blue-600" />
                        ) : content.type === 'blog' ? (
                          <FileText className="w-5 h-5 text-green-600" />
                        ) : (
                          <PlayCircle className="w-5 h-5 text-purple-600" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{content.title}</h4>
                        <p className="text-sm text-gray-600 capitalize">{content.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        {formatNumber(content.views || content.downloads)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {content.views ? 'views' : 'downloads'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Marketing Tab */}
        {activeTab === 'marketing' && (
          <div className="space-y-6">
            {/* Marketing Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Total Leads"
                value={dashboardData.lead_metrics.total_leads}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Qualified Leads"
                value={dashboardData.lead_metrics.qualified_leads}
                icon={UserCheck}
                color="#10B981"
              />
              <MetricCard
                title="Conversion Rate"
                value={dashboardData.lead_metrics.conversion_rate}
                icon={Target}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Pipeline Value"
                value={dashboardData.lead_metrics.pipeline_value}
                icon={DollarSign}
                color="#8B5CF6"
                format="currency"
              />
            </div>

            {/* Marketing Campaign Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Marketing Campaigns</h2>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <Mail className="w-4 h-4 mr-2" />
                  Create Campaign
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900">Email Marketing</h3>
                  <p className="text-sm text-blue-700 mt-1">Automated nurture sequences</p>
                  <button className="mt-3 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                    Manage
                  </button>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900">Social Media</h3>
                  <p className="text-sm text-green-700 mt-1">LinkedIn & Twitter campaigns</p>
                  <button className="mt-3 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                    Schedule
                  </button>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900">SEO Content</h3>
                  <p className="text-sm text-purple-700 mt-1">Blog posts & landing pages</p>
                  <button className="mt-3 bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                    Optimize
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="space-y-6">
            {/* Event Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Upcoming Events"
                value={dashboardData.event_metrics.upcoming_events}
                icon={Calendar}
                color="#3B82F6"
              />
              <MetricCard
                title="Total Attendees"
                value={dashboardData.event_metrics.total_attendees}
                icon={Users}
                color="#10B981"
              />
              <MetricCard
                title="Attendance Rate"
                value={dashboardData.event_metrics.attendance_rate}
                icon={UserCheck}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Event Revenue"
                value={dashboardData.event_metrics.revenue_from_events}
                icon={DollarSign}
                color="#8B5CF6"
                format="currency"
              />
            </div>

            {/* Event Management */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Event Management</h2>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Event
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Weekly Online Meetings</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="font-medium">Deal Review Session</span>
                      <span className="text-sm text-gray-600">Wed 2PM GMT</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="font-medium">Expert Interview</span>
                      <span className="text-sm text-gray-600">Fri 3PM GMT</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">Quarterly Events</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="font-medium">M&A Summit 2025</span>
                      <span className="text-sm text-gray-600">Mar 15-16</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <span className="font-medium">Regional Meetup</span>
                      <span className="text-sm text-gray-600">Apr 20</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MasterAdminPortal;
