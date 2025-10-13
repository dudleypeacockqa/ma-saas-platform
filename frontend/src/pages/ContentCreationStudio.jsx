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
} from 'recharts';
import {
  PlayCircle,
  Video,
  Mic,
  Settings,
  Calendar,
  Users,
  Upload,
  Download,
  Share2,
  Eye,
  ThumbsUp,
  MessageCircle,
  Clock,
  TrendingUp,
  Award,
  Zap,
  Plus,
  Edit3,
  Camera,
  Headphones,
  Monitor,
  Smartphone,
  Globe,
  FileText,
  Image,
  Film,
  Radio,
  Tv,
  Youtube,
  Linkedin,
  Twitter,
  Facebook,
  Instagram,
} from 'lucide-react';

const ContentCreationStudio = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSeries, setSelectedSeries] = useState(null);
  const [recordingSession, setRecordingSession] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  const contentMetrics = {
    totalViews: 125420,
    totalDownloads: 89750,
    totalEpisodes: 47,
    averageEngagement: 8.2,
    monthlyGrowth: 23.5,
    revenueGenerated: 15750,
  };

  const contentSeries = [
    {
      id: 1,
      name: 'M&A Masterclass',
      type: 'podcast',
      episodes: 12,
      totalViews: 45200,
      avgRating: 4.8,
      status: 'active',
      nextEpisode: '2025-01-15',
    },
    {
      id: 2,
      name: 'Deal Breakdown Weekly',
      type: 'video',
      episodes: 8,
      totalViews: 32100,
      avgRating: 4.6,
      status: 'active',
      nextEpisode: '2025-01-12',
    },
    {
      id: 3,
      name: 'Private Equity Insights',
      type: 'podcast',
      episodes: 15,
      totalViews: 28900,
      avgRating: 4.7,
      status: 'active',
      nextEpisode: '2025-01-18',
    },
  ];

  const recentEpisodes = [
    {
      id: 1,
      title: 'Valuation Methods in Tech M&A',
      series: 'M&A Masterclass',
      type: 'podcast',
      duration: '42:15',
      views: 2850,
      status: 'published',
      publishDate: '2025-01-08',
    },
    {
      id: 2,
      title: 'Due Diligence Red Flags',
      series: 'Deal Breakdown Weekly',
      type: 'video',
      duration: '28:30',
      views: 1920,
      status: 'published',
      publishDate: '2025-01-05',
    },
    {
      id: 3,
      title: 'PE Fund Structures Explained',
      series: 'Private Equity Insights',
      type: 'podcast',
      duration: '35:45',
      views: 1650,
      status: 'in_production',
      publishDate: null,
    },
  ];

  const analyticsData = [
    { month: 'Aug', views: 8500, downloads: 6200, engagement: 7.2 },
    { month: 'Sep', views: 9200, downloads: 6800, engagement: 7.5 },
    { month: 'Oct', views: 10800, downloads: 7900, engagement: 7.8 },
    { month: 'Nov', views: 12400, downloads: 9100, engagement: 8.0 },
    { month: 'Dec', views: 14200, downloads: 10300, engagement: 8.2 },
    { month: 'Jan', views: 15900, downloads: 11500, engagement: 8.4 },
  ];

  const platformDistribution = [
    { name: 'Apple Podcasts', value: 35, color: '#000000' },
    { name: 'Spotify', value: 28, color: '#1DB954' },
    { name: 'YouTube', value: 20, color: '#FF0000' },
    { name: 'LinkedIn', value: 12, color: '#0077B5' },
    { name: 'Website', value: 5, color: '#3B82F6' },
  ];

  const MetricCard = ({ title, value, change, icon: Icon, color = 'blue', format = 'number' }) => {
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
            {change !== undefined && (
              <div
                className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}
              >
                {change >= 0 ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingUp className="w-4 h-4 mr-1 rotate-180" />
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

  const RecordingStudio = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">Professional Recording Studio</h2>
        <div className="flex space-x-2">
          <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center">
            <PlayCircle className="w-4 h-4 mr-2" />
            Start Recording
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
            <Calendar className="w-4 h-4 mr-2" />
            Schedule Session
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recording Controls */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Recording Settings</h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Video className="w-5 h-5 text-blue-600 mr-3" />
                <span className="font-medium">Video Quality</span>
              </div>
              <select className="border border-gray-300 rounded px-3 py-1">
                <option>4K Ultra HD</option>
                <option>1080p Full HD</option>
                <option>720p HD</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Mic className="w-5 h-5 text-green-600 mr-3" />
                <span className="font-medium">Audio Quality</span>
              </div>
              <select className="border border-gray-300 rounded px-3 py-1">
                <option>48kHz/24-bit</option>
                <option>44.1kHz/16-bit</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Users className="w-5 h-5 text-purple-600 mr-3" />
                <span className="font-medium">Max Participants</span>
              </div>
              <select className="border border-gray-300 rounded px-3 py-1">
                <option>10 participants</option>
                <option>5 participants</option>
                <option>2 participants</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Globe className="w-5 h-5 text-orange-600 mr-3" />
                <span className="font-medium">Live Streaming</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Live Preview */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Live Preview</h3>
          <div className="bg-black rounded-lg aspect-video flex items-center justify-center">
            <div className="text-center text-white">
              <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm opacity-75">Camera preview will appear here</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <button className="bg-gray-100 p-2 rounded text-center hover:bg-gray-200">
              <Monitor className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs">Screen</span>
            </button>
            <button className="bg-gray-100 p-2 rounded text-center hover:bg-gray-200">
              <Camera className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs">Camera</span>
            </button>
            <button className="bg-gray-100 p-2 rounded text-center hover:bg-gray-200">
              <Headphones className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs">Audio</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const ContentLibrary = () => (
    <div className="space-y-6">
      {/* Content Series */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Content Series</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            New Series
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {contentSeries.map((series) => (
            <div
              key={series.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  {series.type === 'podcast' ? (
                    <Radio className="w-5 h-5 text-purple-600 mr-2" />
                  ) : (
                    <Video className="w-5 h-5 text-red-600 mr-2" />
                  )}
                  <h3 className="font-semibold text-gray-900">{series.name}</h3>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs ${
                    series.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {series.status}
                </span>
              </div>

              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Episodes:</span>
                  <span className="font-medium">{series.episodes}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Views:</span>
                  <span className="font-medium">{series.totalViews.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Rating:</span>
                  <div className="flex items-center">
                    <Award className="w-4 h-4 text-yellow-500 mr-1" />
                    <span className="font-medium">{series.avgRating}</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span>Next Episode:</span>
                  <span className="font-medium">{series.nextEpisode}</span>
                </div>
              </div>

              <div className="mt-4 flex space-x-2">
                <button className="flex-1 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                  Manage
                </button>
                <button className="flex-1 bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200">
                  Analytics
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Episodes */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Recent Episodes</h2>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            New Episode
          </button>
        </div>

        <div className="space-y-4">
          {recentEpisodes.map((episode) => (
            <div
              key={episode.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`p-2 rounded-full ${
                    episode.type === 'podcast' ? 'bg-purple-100' : 'bg-red-100'
                  }`}
                >
                  {episode.type === 'podcast' ? (
                    <Radio
                      className={`w-5 h-5 ${episode.type === 'podcast' ? 'text-purple-600' : 'text-red-600'}`}
                    />
                  ) : (
                    <Video
                      className={`w-5 h-5 ${episode.type === 'podcast' ? 'text-purple-600' : 'text-red-600'}`}
                    />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{episode.title}</h3>
                  <p className="text-sm text-gray-600">
                    {episode.series} • {episode.duration}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="flex items-center text-sm text-gray-600">
                    <Eye className="w-4 h-4 mr-1" />
                    {episode.views.toLocaleString()}
                  </div>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-xs ${
                    episode.status === 'published'
                      ? 'bg-green-100 text-green-800'
                      : episode.status === 'in_production'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {episode.status.replace('_', ' ')}
                </span>

                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-blue-600">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-green-600">
                    <Share2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const DistributionHub = () => (
    <div className="space-y-6">
      {/* Platform Distribution */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Multi-Platform Distribution</h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Distribution Channels</h3>
            <div className="space-y-3">
              {[
                { name: 'Apple Podcasts', icon: Radio, connected: true, color: 'text-gray-800' },
                { name: 'Spotify', icon: Radio, connected: true, color: 'text-green-600' },
                { name: 'YouTube', icon: Youtube, connected: true, color: 'text-red-600' },
                { name: 'LinkedIn', icon: Linkedin, connected: true, color: 'text-blue-600' },
                { name: 'Twitter', icon: Twitter, connected: false, color: 'text-blue-400' },
                { name: 'Facebook', icon: Facebook, connected: false, color: 'text-blue-800' },
              ].map((platform, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center">
                    <platform.icon className={`w-5 h-5 ${platform.color} mr-3`} />
                    <span className="font-medium">{platform.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        platform.connected
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {platform.connected ? 'Connected' : 'Not Connected'}
                    </span>
                    <button
                      className={`px-3 py-1 rounded text-sm ${
                        platform.connected
                          ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {platform.connected ? 'Manage' : 'Connect'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Platform Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={platformDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {platformDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Auto-Publishing Settings */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Auto-Publishing Settings</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Publishing Schedule</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Auto-publish to all platforms</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Generate social media posts</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Create short-form clips</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Content Optimization</h3>
            <div className="space-y-3">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <Zap className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="font-medium text-blue-900">AI Enhancement</span>
                </div>
                <p className="text-sm text-blue-700">
                  Automatically generate thumbnails, show notes, and SEO-optimized descriptions
                </p>
              </div>

              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <FileText className="w-5 h-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-900">Transcription</span>
                </div>
                <p className="text-sm text-green-700">
                  99%+ accurate transcription with speaker identification and timestamps
                </p>
              </div>

              <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-5 h-5 text-purple-600 mr-2" />
                  <span className="font-medium text-purple-900">Analytics</span>
                </div>
                <p className="text-sm text-purple-700">
                  Track performance across all platforms with unified analytics
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <main role="main" className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Content Creation Studio</h1>
              <p className="text-gray-600">Professional podcast and video production suite</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center">
                <PlayCircle className="w-4 h-4 mr-2" />
                Go Live
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                New Content
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
            id="studio"
            label="Recording Studio"
            isActive={activeTab === 'studio'}
            onClick={setActiveTab}
          />
          <TabButton
            id="library"
            label="Content Library"
            isActive={activeTab === 'library'}
            onClick={setActiveTab}
          />
          <TabButton
            id="distribution"
            label="Distribution"
            isActive={activeTab === 'distribution'}
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
            {/* Content Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <MetricCard
                title="Total Views"
                value={contentMetrics.totalViews}
                change={15.2}
                icon={Eye}
                color="#3B82F6"
              />
              <MetricCard
                title="Total Downloads"
                value={contentMetrics.totalDownloads}
                change={12.8}
                icon={Download}
                color="#10B981"
              />
              <MetricCard
                title="Total Episodes"
                value={contentMetrics.totalEpisodes}
                change={8.5}
                icon={PlayCircle}
                color="#8B5CF6"
              />
              <MetricCard
                title="Avg Engagement"
                value={contentMetrics.averageEngagement}
                change={5.3}
                icon={ThumbsUp}
                color="#F59E0B"
                format="percentage"
              />
              <MetricCard
                title="Monthly Growth"
                value={contentMetrics.monthlyGrowth}
                change={18.7}
                icon={TrendingUp}
                color="#EF4444"
                format="percentage"
              />
              <MetricCard
                title="Revenue Generated"
                value={contentMetrics.revenueGenerated}
                change={25.4}
                icon={Award}
                color="#06B6D4"
                format="currency"
              />
            </div>

            {/* Performance Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Content Performance Trends</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analyticsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="views" stroke="#3B82F6" strokeWidth={2} />
                  <Line type="monotone" dataKey="downloads" stroke="#10B981" strokeWidth={2} />
                  <Line type="monotone" dataKey="engagement" stroke="#F59E0B" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button className="bg-red-600 text-white p-4 rounded-lg hover:bg-red-700 flex flex-col items-center">
                  <PlayCircle className="w-8 h-8 mb-2" />
                  <span className="font-medium">Start Recording</span>
                </button>
                <button className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 flex flex-col items-center">
                  <Calendar className="w-8 h-8 mb-2" />
                  <span className="font-medium">Schedule Session</span>
                </button>
                <button className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 flex flex-col items-center">
                  <Upload className="w-8 h-8 mb-2" />
                  <span className="font-medium">Upload Content</span>
                </button>
                <button className="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700 flex flex-col items-center">
                  <Share2 className="w-8 h-8 mb-2" />
                  <span className="font-medium">Distribute</span>
                </button>
              </div>
            </div>
          </>
        )}

        {/* Recording Studio Tab */}
        {activeTab === 'studio' && <RecordingStudio />}

        {/* Content Library Tab */}
        {activeTab === 'library' && <ContentLibrary />}

        {/* Distribution Tab */}
        {activeTab === 'distribution' && <DistributionHub />}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Detailed Analytics</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Platform Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={platformDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {platformDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Growth Metrics</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={analyticsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="views" fill="#3B82F6" />
                    <Bar dataKey="downloads" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default ContentCreationStudio;
