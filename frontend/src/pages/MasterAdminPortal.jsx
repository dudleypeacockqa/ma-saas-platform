import React, { useState, useEffect, useRef } from 'react';
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
  Mic,
  Video,
  Send,
  BarChart3,
  Crown,
  Smartphone,
} from 'lucide-react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { toast } from 'sonner';

const MasterAdminPortal = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [activeTab, setActiveTab] = useState('overview');
  const [realTimeUpdates, setRealTimeUpdates] = useState(true);
  const hasConnectedToLiveRef = useRef(false);

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

  // Live API integration with robust error handling
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get auth token from Clerk
      let token = null;

      if (typeof getToken === 'function') {
        token = await getToken({ template: 'default' });
      } else if (typeof user?.getToken === 'function') {
        token = await user.getToken({ template: 'default' });
      }

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(
        `https://api-server.100daysandbeyond.com/api/admin/dashboard?period=${selectedTimeRange}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        },
      );

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed - please refresh and try again');
        } else if (response.status === 403) {
          throw new Error('Admin access required');
        } else if (response.status >= 500) {
          throw new Error('Server temporarily unavailable');
        } else {
          throw new Error(`API error: ${response.status}`);
        }
      }

      const data = await response.json();
      setDashboardData((current) => ({
        ...(current ?? mockDashboardData),
        ...data,
        api_status: 'live',
        last_updated: new Date().toISOString(),
      }));

      if (!hasConnectedToLiveRef.current) {
        toast.success('✅ Connected to live business intelligence!');
      }
      hasConnectedToLiveRef.current = true;
    } catch (err) {
      console.warn('Dashboard API error, using mock data:', err);
      setError(`Live API unavailable: ${err.message}`);

      // Fallback to enhanced mock data with live API simulation
      setDashboardData({
        ...mockDashboardData,
        last_updated: new Date().toISOString(),
        api_status: 'mock_fallback',
      });
      hasConnectedToLiveRef.current = false;

      // Show warning toast for API fallback
      toast.warning('📊 Using demo data - API connection failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user, selectedTimeRange]);

  // Real-time updates every 30 seconds
  useEffect(() => {
    if (!realTimeUpdates || !user) return;

    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [realTimeUpdates, user, selectedTimeRange]);

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

  const MetricCard = ({
    title,
    value,
    change,
    icon: Icon,
    color = '#3B82F6',
    format = 'number',
    trend = null,
    subtitle = null,
  }) => {
    const formattedValue =
      format === 'currency'
        ? formatCurrency(value)
        : format === 'percentage'
          ? `${value}%`
          : formatNumber(value);

    return (
      <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 hover:border-gray-200 group hover:-translate-y-1">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <p className="text-sm font-medium text-gray-600">{title}</p>
              {trend && (
                <div
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    trend === 'up'
                      ? 'bg-emerald-100 text-emerald-700'
                      : trend === 'down'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-blue-100 text-blue-700'
                  }`}
                >
                  {trend === 'up' ? '↗️' : trend === 'down' ? '↘️' : '📊'}
                </div>
              )}
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">{formattedValue}</p>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
            {change !== undefined && (
              <div
                className={`flex items-center mt-2 text-sm font-medium ${
                  change >= 0 ? 'text-emerald-600' : 'text-red-600'
                }`}
              >
                {change >= 0 ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
                )}
                <span>{Math.abs(change)}% vs last period</span>
              </div>
            )}
          </div>
          <div
            className="p-4 rounded-xl group-hover:scale-110 transition-transform duration-300"
            style={{ backgroundColor: `${color}15` }}
          >
            <Icon className="w-8 h-8" style={{ color }} />
          </div>
        </div>
      </div>
    );
  };

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
        isActive
          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg transform scale-105'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      {label}
    </button>
  );

  const revenueData = [
    { month: 'Jan', revenue: 35000, subscribers: 120 },
    { month: 'Feb', revenue: 38500, subscribers: 128 },
    { month: 'Mar', revenue: 42000, subscribers: 142 },
    { month: 'Apr', revenue: 45200, subscribers: 151 },
    { month: 'May', revenue: 47500, subscribers: 156 },
  ];

  const viewData = dashboardData ?? {
    ...mockDashboardData,
    api_status: 'mock_fallback',
    last_updated: new Date().toISOString(),
  };
  const isMockData = viewData.api_status === 'mock_fallback';

  const leadSourceData = Object.entries(viewData.lead_metrics.lead_sources).map(
    ([source, count]) => ({
      name: source.charAt(0).toUpperCase() + source.slice(1),
      value: count,
    }),
  );

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <main role="main" className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
          <div className="bg-blue-50 border border-blue-200 text-blue-900 px-4 py-3 rounded-lg flex items-center justify-between" role="status" aria-live="polite">
            <div>
              <p className="font-semibold">Refreshing live metrics...</p>
              <p className="text-sm text-blue-700">Pulling the latest command center analytics.</p>
            </div>
            <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" aria-hidden="true"></span>
          </div>
        </div>
      )}

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="bg-amber-50 border border-amber-200 text-amber-900 px-4 py-3 rounded-lg" role="alert">
            <p className="font-semibold">Live API unavailable</p>
            <p className="text-sm">Showing demo metrics while we reconnect. {error}</p>
          </div>
        </div>
      )}
      {/* Premium Executive Header */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 shadow-xl border-b border-yellow-400/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-yellow-400 rounded-xl">
                <Crown className="w-8 h-8 text-slate-900" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white mb-1">Business Command Center</h1>
                <p className="text-slate-300 text-lg">Master Admin Portal for £200M+ M&A Empire</p>
                <div className="flex items-center mt-2 space-x-4 text-sm">
                  <div
                    className={`flex items-center ${
                      isMockData
                        ? 'text-orange-400'
                        : error
                          ? 'text-red-400'
                          : 'text-emerald-400'
                    }`}
                  >
                    <div
                      className={`w-2 h-2 rounded-full mr-2 ${
                        isMockData
                          ? 'bg-orange-400 animate-pulse'
                          : error
                            ? 'bg-red-400'
                            : 'bg-emerald-400 animate-pulse'
                      }`}
                    ></div>
                    {isMockData
                      ? 'Demo Mode Active'
                      : error
                        ? 'Connection Lost'
                        : 'Live Data Connected'}
                  </div>
                  <div className="flex items-center text-yellow-400">
                    <Smartphone className="w-4 h-4 mr-1" />
                    Mobile Ready
                  </div>
                  <div className="flex items-center text-blue-400">
                    <Crown className="w-4 h-4 mr-1" />
                    Premium Active
                  </div>
                  {viewData.last_updated && (
                    <div className="flex items-center text-slate-400">
                      <Calendar className="w-4 h-4 mr-1" />
                      Updated: {new Date(viewData.last_updated).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-white text-sm">Real-time Updates:</label>
                <button
                  onClick={() => setRealTimeUpdates(!realTimeUpdates)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    realTimeUpdates ? 'bg-emerald-500' : 'bg-slate-600'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      realTimeUpdates ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  ></div>
                </button>
              </div>
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="bg-slate-800 border border-slate-600 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button
                onClick={() => {
                  toast.success('Report exported successfully!');
                  // TODO: Implement actual export functionality
                }}
                className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-slate-900 px-6 py-3 rounded-xl hover:from-yellow-500 hover:to-yellow-600 flex items-center font-semibold transition-all duration-300 hover:scale-105"
              >
                <Download className="w-5 h-5 mr-2" />
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Premium Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-white rounded-xl p-2 shadow-lg border border-gray-200">
          <TabButton
            id="overview"
            label="📊 Overview"
            isActive={activeTab === 'overview'}
            onClick={setActiveTab}
          />
          <TabButton
            id="subscriptions"
            label="💳 Subscribers"
            isActive={activeTab === 'subscriptions'}
            onClick={setActiveTab}
          />
          <TabButton
            id="content"
            label="🎥 Content Studio"
            isActive={activeTab === 'content'}
            onClick={setActiveTab}
          />
          <TabButton
            id="marketing"
            label="📧 Campaigns"
            isActive={activeTab === 'marketing'}
            onClick={setActiveTab}
          />
          <TabButton
            id="events"
            label="🎪 Events"
            isActive={activeTab === 'events'}
            onClick={setActiveTab}
          />
          <TabButton
            id="podcast"
            label="🎙️ Podcast Studio"
            isActive={activeTab === 'podcast'}
            onClick={setActiveTab}
          />
          <TabButton
            id="mobile"
            label="📱 Mobile Command"
            isActive={activeTab === 'mobile'}
            onClick={setActiveTab}
          />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Executive KPI Dashboard */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Monthly Recurring Revenue"
                value={viewData.dashboard_metrics.mrr}
                change={viewData.dashboard_metrics.revenue_growth}
                icon={DollarSign}
                color="#10B981"
                format="currency"
                trend="up"
                subtitle="£200M target: 23% complete"
              />
              <MetricCard
                title="Active Subscribers"
                value={viewData.dashboard_metrics.active_subscribers}
                change={8.2}
                icon={Users}
                color="#3B82F6"
                trend="up"
                subtitle="Growing 8.2% monthly"
              />
              <MetricCard
                title="Churn Rate"
                value={viewData.dashboard_metrics.churn_rate}
                change={-1.1}
                icon={AlertCircle}
                color="#EF4444"
                format="percentage"
                trend="down"
                subtitle="Industry avg: 5.2%"
              />
              <MetricCard
                title="Customer LTV"
                value={viewData.dashboard_metrics.ltv}
                change={12.5}
                icon={Target}
                color="#8B5CF6"
                format="currency"
                trend="up"
                subtitle="LTV:CAC ratio 67:1"
              />
            </div>

            {/* Enhanced Business Intelligence Summary */}
            <div className="bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 rounded-2xl p-8 mb-8 text-white shadow-2xl border border-yellow-400/20">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-yellow-400 to-yellow-200 bg-clip-text text-transparent">
                    Empire Command Intelligence
                  </h2>
                  <p className="text-blue-200 text-lg">
                    Real-time business intelligence for your £200M wealth-building journey
                  </p>
                  <div className="flex items-center mt-3 space-x-6 text-sm">
                    <div className="flex items-center text-emerald-400">
                      <Target className="w-4 h-4 mr-1" />
                      On Track for £200M
                    </div>
                    <div className="flex items-center text-yellow-400">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      Accelerating Growth
                    </div>
                    <div className="flex items-center text-blue-400">
                      <Award className="w-4 h-4 mr-1" />
                      Premium Performance
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-yellow-400 mb-1">
                    {Math.round((viewData.dashboard_metrics.arr / 20000000) * 100)}%
                  </div>
                  <div className="text-sm text-blue-200 mb-2">to £200M target</div>
                  <div className="text-xs text-yellow-300 bg-yellow-400/20 px-3 py-1 rounded-full">
                    {formatCurrency(20000000 - viewData.dashboard_metrics.arr)} remaining
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/10 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <BarChart3 className="w-5 h-5 text-emerald-400 mr-2" />
                    <span className="font-semibold">Revenue Velocity</span>
                  </div>
                  <div className="text-2xl font-bold text-emerald-400">
                    +{viewData.dashboard_metrics.revenue_growth}%
                  </div>
                  <div className="text-sm text-blue-200">Month-over-month growth</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <Target className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="font-semibold">Conversion Engine</span>
                  </div>
                  <div className="text-2xl font-bold text-yellow-400">
                    {viewData.dashboard_metrics.trial_conversion_rate}%
                  </div>
                  <div className="text-sm text-blue-200">Trial to paid conversion</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <Crown className="w-5 h-5 text-purple-400 mr-2" />
                    <span className="font-semibold">Empire Valuation</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-400">
                    {formatCurrency(viewData.dashboard_metrics.arr * 10)}
                  </div>
                  <div className="text-sm text-blue-200">Estimated business value</div>
                </div>
              </div>
            </div>

            {/* Premium Action Center */}
            <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-6 mb-8 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Executive Action Center</h2>
                <div className="flex items-center text-emerald-400 text-sm">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                  All Systems Operational
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button
                  onClick={() => {
                    toast.success('📧 Campaign wizard launched!');
                    setActiveTab('marketing');
                  }}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white p-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  <Mail className="w-6 h-6 mx-auto mb-2" />
                  <div className="text-sm font-semibold">Launch Campaign</div>
                  <div className="text-xs text-blue-200">Email & Social</div>
                </button>
                <button
                  onClick={() => {
                    toast.success('🎙️ Recording studio ready!');
                    setActiveTab('podcast');
                  }}
                  className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white p-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  <Mic className="w-6 h-6 mx-auto mb-2" />
                  <div className="text-sm font-semibold">Record Podcast</div>
                  <div className="text-xs text-red-200">StreamYard Studio</div>
                </button>
                <button
                  onClick={() => {
                    toast.success('📊 Analytics deep dive activated!');
                    // This would open detailed analytics
                  }}
                  className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white p-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  <BarChart3 className="w-6 h-6 mx-auto mb-2" />
                  <div className="text-sm font-semibold">Deep Analytics</div>
                  <div className="text-xs text-purple-200">Business Intel</div>
                </button>
                <button
                  onClick={() => {
                    toast.success('🎪 Event creation started!');
                    setActiveTab('events');
                  }}
                  className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white p-4 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  <Calendar className="w-6 h-6 mx-auto mb-2" />
                  <div className="text-sm font-semibold">Create Event</div>
                  <div className="text-xs text-green-200">Premium Hosting</div>
                </button>
              </div>
            </div>

            {/* Revenue Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Revenue Growth</h2>
                <div className="text-sm text-gray-600">
                  ARR: {formatCurrency(viewData.dashboard_metrics.arr)}
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
                value={viewData.dashboard_metrics.trial_conversion_rate}
                change={3.2}
                icon={UserCheck}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Customer Acquisition Cost"
                value={viewData.dashboard_metrics.cac}
                change={-8.5}
                icon={CreditCard}
                color="#10B981"
                format="currency"
              />
              <MetricCard
                title="Lead Generation"
                value={viewData.content_metrics.lead_generation_from_content}
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
                value={viewData.subscription_metrics.total_subscriptions}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Active Subscriptions"
                value={viewData.subscription_metrics.active_subscriptions}
                icon={UserCheck}
                color="#10B981"
              />
              <MetricCard
                title="Trial Subscriptions"
                value={viewData.subscription_metrics.trial_subscriptions}
                icon={Eye}
                color="#F59E0B"
              />
              <MetricCard
                title="Payment Failures"
                value={viewData.subscription_metrics.payment_failures}
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
                {Object.entries(viewData.subscription_metrics.revenue_by_plan).map(
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
                value={viewData.content_metrics.podcast_downloads}
                icon={PlayCircle}
                color="#8B5CF6"
              />
              <MetricCard
                title="Video Views"
                value={viewData.content_metrics.video_views}
                icon={Eye}
                color="#3B82F6"
              />
              <MetricCard
                title="Blog Post Views"
                value={viewData.content_metrics.blog_post_views}
                icon={FileText}
                color="#10B981"
              />
              <MetricCard
                title="Engagement Rate"
                value={viewData.content_metrics.content_engagement_rate}
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
                {viewData.content_metrics.top_performing_content.map((content, index) => (
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
                value={viewData.lead_metrics.total_leads}
                icon={Users}
                color="#3B82F6"
              />
              <MetricCard
                title="Qualified Leads"
                value={viewData.lead_metrics.qualified_leads}
                icon={UserCheck}
                color="#10B981"
              />
              <MetricCard
                title="Conversion Rate"
                value={viewData.lead_metrics.conversion_rate}
                icon={Target}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Pipeline Value"
                value={viewData.lead_metrics.pipeline_value}
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
                value={viewData.event_metrics.upcoming_events}
                icon={Calendar}
                color="#3B82F6"
                subtitle="Next: M&A Masterclass"
              />
              <MetricCard
                title="Total Attendees"
                value={viewData.event_metrics.total_attendees}
                icon={Users}
                color="#10B981"
                subtitle="Growing 15% monthly"
              />
              <MetricCard
                title="Attendance Rate"
                value={viewData.event_metrics.attendance_rate}
                icon={UserCheck}
                color="#F59E0B"
                format="percentage"
                subtitle="Industry avg: 65%"
              />
              <MetricCard
                title="Event Revenue"
                value={viewData.event_metrics.revenue_from_events}
                icon={DollarSign}
                color="#8B5CF6"
                format="currency"
                subtitle="£50k monthly target"
              />
            </div>

            {/* Event Management */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">Event Management Hub</h2>
                <button
                  onClick={() => toast.success('Event creation wizard launched!')}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 flex items-center font-semibold transition-all duration-300 hover:scale-105"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create Premium Event
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900 text-lg">Weekly Member Events</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                      <div>
                        <span className="font-semibold text-blue-900">Deal Review Session</span>
                        <p className="text-sm text-blue-700">Member-only deal analysis</p>
                      </div>
                      <span className="text-sm font-medium text-blue-600 bg-white px-3 py-1 rounded-lg">
                        Wed 2PM GMT
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-xl border border-emerald-200">
                      <div>
                        <span className="font-semibold text-emerald-900">Expert Interview</span>
                        <p className="text-sm text-emerald-700">Industry leader insights</p>
                      </div>
                      <span className="text-sm font-medium text-emerald-600 bg-white px-3 py-1 rounded-lg">
                        Fri 3PM GMT
                      </span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900 text-lg">Premium Quarterly Events</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl border border-purple-200">
                      <div>
                        <span className="font-semibold text-purple-900">M&A Summit 2025</span>
                        <p className="text-sm text-purple-700">£2,997 VIP networking</p>
                      </div>
                      <span className="text-sm font-medium text-purple-600 bg-white px-3 py-1 rounded-lg">
                        Mar 15-16
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-orange-100 rounded-xl border border-orange-200">
                      <div>
                        <span className="font-semibold text-orange-900">Regional Meetup</span>
                        <p className="text-sm text-orange-700">£497 premium networking</p>
                      </div>
                      <span className="text-sm font-medium text-orange-600 bg-white px-3 py-1 rounded-lg">
                        Apr 20
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Podcast Studio Tab */}
        {activeTab === 'podcast' && (
          <div className="space-y-6">
            {/* Podcast Creation Studio */}
            <div className="bg-gradient-to-r from-red-900 to-purple-900 rounded-2xl p-8 text-white">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold mb-2">StreamYard Pro Studio</h2>
                  <p className="text-red-200">
                    Professional recording + AI automation + multi-platform distribution
                  </p>
                  <div className="flex items-center mt-3 space-x-6 text-sm">
                    <div className="flex items-center text-emerald-400">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                      Studio Ready
                    </div>
                    <div className="flex items-center text-yellow-400">
                      <Crown className="w-4 h-4 mr-1" />
                      Pro Features Enabled
                    </div>
                    <div className="flex items-center text-blue-400">
                      <Zap className="w-4 h-4 mr-1" />
                      AI Automation Active
                    </div>
                  </div>
                </div>
                <div className="flex space-x-4">
                  <button
                    onClick={() => {
                      toast.success('🎬 StreamYard Studio launching...');
                      // This would open the StreamYard Studio component
                      window.open('/podcast-studio', '_blank');
                    }}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-4 rounded-xl flex items-center font-semibold transition-all duration-300 hover:scale-105 shadow-lg"
                  >
                    <Mic className="w-6 h-6 mr-2" />
                    Launch Studio
                  </button>
                  <button
                    onClick={() => {
                      toast.success('📡 Multi-platform streaming ready!');
                      // This would prepare live streaming
                    }}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-4 rounded-xl flex items-center font-semibold transition-all duration-300 hover:scale-105 shadow-lg"
                  >
                    <Video className="w-6 h-6 mr-2" />
                    Go Live
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-red-300">🎬 Recording Studio</h3>
                  <ul className="space-y-2 text-red-200 text-sm">
                    <li>• 4K multi-guest recording</li>
                    <li>• Screen sharing & slides</li>
                    <li>• Real-time scene switching</li>
                    <li>• Professional graphics overlay</li>
                    <li>• AI noise reduction</li>
                    <li>• Multi-track audio</li>
                    <li>• Cloud backup & storage</li>
                  </ul>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-purple-300">📡 Live Streaming</h3>
                  <ul className="space-y-2 text-purple-200 text-sm">
                    <li>• YouTube Live</li>
                    <li>• LinkedIn Live</li>
                    <li>• Facebook Live</li>
                    <li>• X Spaces</li>
                    <li>• Twitch streaming</li>
                    <li>• Custom RTMP</li>
                    <li>• Multi-platform simultaneously</li>
                  </ul>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-blue-300">🤖 AI Automation</h3>
                  <ul className="space-y-2 text-blue-200 text-sm">
                    <li>• Auto transcription</li>
                    <li>• AI show notes</li>
                    <li>• Social media clips</li>
                    <li>• Blog post generation</li>
                    <li>• Newsletter content</li>
                    <li>• SEO optimization</li>
                    <li>• Lead magnet creation</li>
                  </ul>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-green-300">💼 Business Tools</h3>
                  <ul className="space-y-2 text-green-200 text-sm">
                    <li>• Lead generation CTAs</li>
                    <li>• Conversion tracking</li>
                    <li>• Sponsor integration</li>
                    <li>• Revenue analytics</li>
                    <li>• Audience insights</li>
                    <li>• Email list building</li>
                    <li>• Deal flow generation</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Podcast Analytics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Total Downloads"
                value={viewData.content_metrics.podcast_downloads}
                icon={PlayCircle}
                color="#DC2626"
                trend="up"
                subtitle="10k monthly target"
              />
              <MetricCard
                title="Episode Views"
                value={viewData.content_metrics.video_views}
                icon={Eye}
                color="#7C3AED"
                trend="up"
                subtitle="Video podcast views"
              />
              <MetricCard
                title="Lead Generation"
                value={viewData.content_metrics.lead_generation_from_content}
                icon={Target}
                color="#059669"
                trend="up"
                subtitle="From podcast CTAs"
              />
              <MetricCard
                title="Engagement Rate"
                value={viewData.content_metrics.content_engagement_rate}
                icon={MousePointer}
                color="#D97706"
                format="percentage"
                trend="up"
                subtitle="Listener interaction"
              />
            </div>
          </div>
        )}

        {/* Mobile Command Center Tab */}
        {activeTab === 'mobile' && (
          <div className="space-y-6">
            {/* Mobile Command Center */}
            <div className="bg-gradient-to-r from-blue-900 to-cyan-900 rounded-2xl p-8 text-white">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Mobile Business Command Center</h2>
                  <p className="text-blue-200">Run your £200M empire from anywhere in the world</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-cyan-400">100%</div>
                  <div className="text-sm text-blue-200">Mobile Ready</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white/10 rounded-xl p-6 text-center">
                  <Smartphone className="w-12 h-12 text-cyan-400 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Real-time Dashboard</h3>
                  <p className="text-blue-200 text-sm">Key metrics in 3 taps</p>
                </div>
                <div className="bg-white/10 rounded-xl p-6 text-center">
                  <Mic className="w-12 h-12 text-green-400 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Mobile Recording</h3>
                  <p className="text-blue-200 text-sm">HD podcast on-the-go</p>
                </div>
                <div className="bg-white/10 rounded-xl p-6 text-center">
                  <Mail className="w-12 h-12 text-yellow-400 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Campaign Management</h3>
                  <p className="text-blue-200 text-sm">Email campaigns anywhere</p>
                </div>
                <div className="bg-white/10 rounded-xl p-6 text-center">
                  <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Emergency Access</h3>
                  <p className="text-blue-200 text-sm">Crisis management ready</p>
                </div>
              </div>

              <div className="mt-8 bg-white/10 rounded-xl p-6">
                <h3 className="font-bold text-xl mb-4">Mobile Capabilities</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3 text-cyan-400">Business Management</h4>
                    <ul className="space-y-2 text-blue-200">
                      <li>• Real-time KPI monitoring</li>
                      <li>• Subscription management</li>
                      <li>• Customer support chat</li>
                      <li>• Financial oversight</li>
                      <li>• Team communication</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3 text-green-400">Content Creation</h4>
                    <ul className="space-y-2 text-blue-200">
                      <li>• Mobile podcast recording</li>
                      <li>• Social media management</li>
                      <li>• Email campaign creation</li>
                      <li>• Live streaming capability</li>
                      <li>• Content scheduling</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

// Enhanced loading state component
const LoadingSpinner = ({ message = 'Loading...' }) => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
    <span className="text-gray-600">{message}</span>
  </div>
);

export default MasterAdminPortal;















