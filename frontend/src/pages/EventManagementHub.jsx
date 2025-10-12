import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { 
  Calendar, Users, MapPin, Clock, DollarSign, TrendingUp, 
  Plus, Edit3, Settings, Share2, Download, Upload,
  Video, Mic, Globe, CheckCircle, XCircle, AlertCircle,
  UserPlus, Mail, Phone, Building, Award, Target,
  BarChart3, PieChart as PieChartIcon, Activity, Zap,
  ExternalLink, Sync, PlayCircle, StopCircle, Eye,
  Filter, Search, Calendar as CalendarIcon, Clock3
} from 'lucide-react';

const EventManagementHub = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  const eventMetrics = {
    totalEvents: 24,
    upcomingEvents: 8,
    totalRegistrations: 3420,
    totalAttendees: 2890,
    averageAttendance: 84.5,
    totalRevenue: 125750,
    leadsGenerated: 1250,
    conversionRate: 12.8
  };

  const upcomingEvents = [
    {
      id: 1,
      title: "M&A Valuation Masterclass",
      type: "masterclass",
      format: "virtual",
      date: "2025-01-15",
      time: "14:00",
      duration: 120,
      registrations: 145,
      capacity: 200,
      price: 299,
      status: "scheduled",
      platform: "Zoom",
      eventbriteSync: true
    },
    {
      id: 2,
      title: "Private Equity Networking Summit",
      type: "networking",
      format: "hybrid",
      date: "2025-01-22",
      time: "18:00",
      duration: 180,
      registrations: 89,
      capacity: 150,
      price: 0,
      status: "scheduled",
      venue: "London Business Centre",
      eventbriteSync: true
    },
    {
      id: 3,
      title: "Due Diligence Workshop",
      type: "workshop",
      format: "virtual",
      date: "2025-01-28",
      time: "10:00",
      duration: 240,
      registrations: 67,
      capacity: 100,
      price: 199,
      status: "scheduled",
      platform: "Teams",
      eventbriteSync: false
    }
  ];

  const recentEvents = [
    {
      id: 4,
      title: "Deal Structuring Webinar",
      type: "webinar",
      date: "2025-01-08",
      registrations: 234,
      attendees: 198,
      attendanceRate: 84.6,
      revenue: 0,
      leads: 45,
      rating: 4.7,
      status: "completed"
    },
    {
      id: 5,
      title: "Investment Banking Panel",
      type: "panel_discussion",
      date: "2025-01-05",
      registrations: 156,
      attendees: 142,
      attendanceRate: 91.0,
      revenue: 4680,
      leads: 38,
      rating: 4.9,
      status: "completed"
    },
    {
      id: 6,
      title: "M&A Market Outlook 2025",
      type: "conference",
      date: "2024-12-20",
      registrations: 342,
      attendees: 289,
      attendanceRate: 84.5,
      revenue: 17100,
      leads: 89,
      rating: 4.5,
      status: "completed"
    }
  ];

  const analyticsData = [
    { month: 'Aug', events: 3, registrations: 420, attendees: 356, revenue: 12500 },
    { month: 'Sep', events: 4, registrations: 580, attendees: 492, revenue: 18200 },
    { month: 'Oct', events: 5, registrations: 720, attendees: 612, revenue: 24600 },
    { month: 'Nov', events: 4, registrations: 650, attendees: 553, revenue: 21800 },
    { month: 'Dec', events: 6, registrations: 890, attendees: 756, revenue: 32400 },
    { month: 'Jan', events: 2, registrations: 160, attendees: 121, revenue: 6250 }
  ];

  const eventTypeDistribution = [
    { name: 'Webinars', value: 35, color: '#3B82F6' },
    { name: 'Workshops', value: 25, color: '#10B981' },
    { name: 'Masterclasses', value: 20, color: '#F59E0B' },
    { name: 'Networking', value: 12, color: '#8B5CF6' },
    { name: 'Conferences', value: 8, color: '#EF4444' }
  ];

  const leadQualityData = [
    { name: 'Hot Leads', value: 28, color: '#EF4444' },
    { name: 'Warm Leads', value: 42, color: '#F59E0B' },
    { name: 'Cold Leads', value: 30, color: '#6B7280' }
  ];

  const MetricCard = ({ title, value, change, icon: Icon, color = "blue", format = "number" }) => {
    const formattedValue = format === "currency" ? `£${value.toLocaleString()}` : 
                          format === "percentage" ? `${value}%` : 
                          value.toLocaleString();

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 border-l-4" style={{ borderLeftColor: color }}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{formattedValue}</p>
            {change !== undefined && (
              <div className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingUp className="w-4 h-4 mr-1 rotate-180" />}
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
        isActive 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      {label}
    </button>
  );

  const EventCard = ({ event, isUpcoming = true }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{event.title}</h3>
          <div className="flex items-center text-sm text-gray-600 space-x-4">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {event.date}
            </div>
            {event.time && (
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {event.time}
              </div>
            )}
            <div className="flex items-center">
              <Clock3 className="w-4 h-4 mr-1" />
              {event.duration || 120} min
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {event.eventbriteSync && (
            <div className="flex items-center text-green-600 text-xs">
              <Sync className="w-3 h-3 mr-1" />
              EventBrite
            </div>
          )}
          <span className={`px-2 py-1 rounded-full text-xs ${
            event.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
            event.status === 'live' ? 'bg-green-100 text-green-800' :
            event.status === 'completed' ? 'bg-gray-100 text-gray-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {event.status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{event.registrations}</div>
          <div className="text-sm text-blue-700">Registrations</div>
        </div>
        {isUpcoming ? (
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{event.capacity}</div>
            <div className="text-sm text-green-700">Capacity</div>
          </div>
        ) : (
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{event.attendees}</div>
            <div className="text-sm text-green-700">Attended</div>
          </div>
        )}
      </div>

      {!isUpcoming && (
        <div className="grid grid-cols-3 gap-2 mb-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-gray-900">{event.attendanceRate}%</div>
            <div className="text-gray-600">Attendance</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-900">{event.leads}</div>
            <div className="text-gray-600">Leads</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-900 flex items-center justify-center">
              <Award className="w-4 h-4 mr-1 text-yellow-500" />
              {event.rating}
            </div>
            <div className="text-gray-600">Rating</div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center text-sm text-gray-600">
          {event.format === 'virtual' ? (
            <Video className="w-4 h-4 mr-1" />
          ) : event.format === 'hybrid' ? (
            <Globe className="w-4 h-4 mr-1" />
          ) : (
            <MapPin className="w-4 h-4 mr-1" />
          )}
          <span className="capitalize">{event.format}</span>
          {event.price > 0 && (
            <>
              <span className="mx-2">•</span>
              <DollarSign className="w-4 h-4 mr-1" />
              £{event.price}
            </>
          )}
        </div>
        
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-blue-600">
            <Edit3 className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-green-600">
            <Share2 className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-purple-600">
            <BarChart3 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const EventbriteIntegration = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">EventBrite Integration</h2>
        <div className="flex items-center space-x-2">
          <div className="flex items-center text-green-600">
            <CheckCircle className="w-5 h-5 mr-2" />
            Connected
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Settings className="w-4 h-4 mr-2 inline" />
            Settings
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <Sync className="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-blue-600">18</div>
          <div className="text-sm text-blue-700">Events Synced</div>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-green-600">2,847</div>
          <div className="text-sm text-green-700">Total Registrations</div>
        </div>
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <DollarSign className="w-8 h-8 text-purple-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-purple-600">£89,450</div>
          <div className="text-sm text-purple-700">Revenue Generated</div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Sync Settings</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Auto-sync new events</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Sync registrations</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Auto-create tickets</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="font-medium">Sync frequency</span>
            <select className="border border-gray-300 rounded px-3 py-1">
              <option>Every hour</option>
              <option>Every 6 hours</option>
              <option>Daily</option>
              <option>Manual only</option>
            </select>
          </div>
        </div>

        <div className="flex space-x-4 pt-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
            <Sync className="w-4 h-4 mr-2" />
            Sync Now
          </button>
          <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center">
            <ExternalLink className="w-4 h-4 mr-2" />
            Open EventBrite
          </button>
        </div>
      </div>
    </div>
  );

  const LeadManagement = () => (
    <div className="space-y-6">
      {/* Lead Generation Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Generation Performance</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <MetricCard 
            title="Total Leads" 
            value={eventMetrics.leadsGenerated} 
            change={18.5}
            icon={UserPlus} 
            color="#3B82F6"
          />
          <MetricCard 
            title="Qualified Leads" 
            value={Math.round(eventMetrics.leadsGenerated * 0.35)} 
            change={22.3}
            icon={Target} 
            color="#10B981"
          />
          <MetricCard 
            title="Conversion Rate" 
            value={eventMetrics.conversionRate} 
            change={5.7}
            icon={TrendingUp} 
            color="#F59E0B" 
            format="percentage"
          />
          <MetricCard 
            title="Lead Value" 
            value={Math.round(eventMetrics.totalRevenue / eventMetrics.leadsGenerated)} 
            change={12.1}
            icon={DollarSign} 
            color="#8B5CF6" 
            format="currency"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Lead Quality Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={leadQualityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {leadQualityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Recent High-Quality Leads</h3>
            <div className="space-y-3">
              {[
                { name: "Sarah Johnson", company: "TechCorp Ltd", event: "M&A Valuation Masterclass", quality: "hot" },
                { name: "Michael Chen", company: "Growth Partners", event: "PE Networking Summit", quality: "warm" },
                { name: "Emma Wilson", company: "Strategic Advisors", event: "Due Diligence Workshop", quality: "hot" },
                { name: "David Brown", company: "Capital Ventures", event: "Deal Structuring Webinar", quality: "warm" }
              ].map((lead, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{lead.name}</div>
                    <div className="text-sm text-gray-600">{lead.company}</div>
                    <div className="text-xs text-gray-500">{lead.event}</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      lead.quality === 'hot' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {lead.quality}
                    </span>
                    <button className="p-1 text-gray-400 hover:text-blue-600">
                      <Mail className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
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
              <h1 className="text-3xl font-bold text-gray-900">Event Management Hub</h1>
              <p className="text-gray-600">Professional event management with EventBrite integration</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Create Event
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Sync className="w-4 h-4 mr-2" />
                Sync EventBrite
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-2 mb-8">
          <TabButton id="overview" label="Overview" isActive={activeTab === 'overview'} onClick={setActiveTab} />
          <TabButton id="upcoming" label="Upcoming Events" isActive={activeTab === 'upcoming'} onClick={setActiveTab} />
          <TabButton id="completed" label="Completed Events" isActive={activeTab === 'completed'} onClick={setActiveTab} />
          <TabButton id="leads" label="Lead Management" isActive={activeTab === 'leads'} onClick={setActiveTab} />
          <TabButton id="eventbrite" label="EventBrite" isActive={activeTab === 'eventbrite'} onClick={setActiveTab} />
          <TabButton id="analytics" label="Analytics" isActive={activeTab === 'analytics'} onClick={setActiveTab} />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Event Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard 
                title="Total Events" 
                value={eventMetrics.totalEvents} 
                change={12.5}
                icon={Calendar} 
                color="#3B82F6"
              />
              <MetricCard 
                title="Total Registrations" 
                value={eventMetrics.totalRegistrations} 
                change={18.7}
                icon={Users} 
                color="#10B981"
              />
              <MetricCard 
                title="Average Attendance" 
                value={eventMetrics.averageAttendance} 
                change={5.2}
                icon={CheckCircle} 
                color="#F59E0B" 
                format="percentage"
              />
              <MetricCard 
                title="Total Revenue" 
                value={eventMetrics.totalRevenue} 
                change={23.8}
                icon={DollarSign} 
                color="#8B5CF6" 
                format="currency"
              />
            </div>

            {/* Performance Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Event Performance Trends</h2>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analyticsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="registrations" stackId="1" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="attendees" stackId="2" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Event Type Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={eventTypeDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {eventTypeDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-4">
                  <button className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 flex flex-col items-center">
                    <Plus className="w-8 h-8 mb-2" />
                    <span className="font-medium">New Event</span>
                  </button>
                  <button className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 flex flex-col items-center">
                    <Users className="w-8 h-8 mb-2" />
                    <span className="font-medium">View Registrations</span>
                  </button>
                  <button className="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700 flex flex-col items-center">
                    <BarChart3 className="w-8 h-8 mb-2" />
                    <span className="font-medium">Analytics</span>
                  </button>
                  <button className="bg-orange-600 text-white p-4 rounded-lg hover:bg-orange-700 flex flex-col items-center">
                    <Target className="w-8 h-8 mb-2" />
                    <span className="font-medium">Manage Leads</span>
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Upcoming Events Tab */}
        {activeTab === 'upcoming' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Upcoming Events</h2>
              <div className="flex space-x-2">
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </button>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <CalendarIcon className="w-4 h-4 mr-2" />
                  Calendar View
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {upcomingEvents.map(event => (
                <EventCard key={event.id} event={event} isUpcoming={true} />
              ))}
            </div>
          </div>
        )}

        {/* Completed Events Tab */}
        {activeTab === 'completed' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Completed Events</h2>
              <div className="flex space-x-2">
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center">
                  <Download className="w-4 h-4 mr-2" />
                  Export Report
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {recentEvents.map(event => (
                <EventCard key={event.id} event={event} isUpcoming={false} />
              ))}
            </div>
          </div>
        )}

        {/* Lead Management Tab */}
        {activeTab === 'leads' && <LeadManagement />}

        {/* EventBrite Integration Tab */}
        {activeTab === 'eventbrite' && <EventbriteIntegration />}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Detailed Event Analytics</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Registration vs Attendance</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analyticsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="registrations" fill="#3B82F6" />
                      <Bar dataKey="attendees" fill="#10B981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Revenue Trends</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analyticsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="revenue" stroke="#8B5CF6" strokeWidth={3} />
                    </LineChart>
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

export default EventManagementHub;
