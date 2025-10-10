import { useState, useEffect } from 'react'
import { useUser, useOrganization } from '@clerk/clerk-react'
import {
  ChartBarIcon,
  UserGroupIcon,
  EnvelopeIcon,
  CursorArrowRaysIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
  TagIcon,
  FunnelIcon,
  PlayIcon,
  PauseIcon,
  PlusIcon
} from '@heroicons/react/24/outline'

function MarketingDashboard() {
  const { user } = useUser()
  const { organization } = useOrganization()

  const [activeTab, setActiveTab] = useState('overview')
  const [analytics, setAnalytics] = useState(null)
  const [prospects, setProspects] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [funnel, setFunnel] = useState({})
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState(30)
  const [showCreateCampaign, setShowCreateCampaign] = useState(false)

  // Fetch analytics data
  useEffect(() => {
    fetchAnalytics()
    fetchProspects()
    fetchCampaigns()
    fetchFunnel()
  }, [selectedPeriod])

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`/api/marketing/analytics/overview?days=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  const fetchProspects = async () => {
    try {
      const response = await fetch('/api/marketing/prospects?limit=10', {
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      const data = await response.json()
      setProspects(data.prospects)
    } catch (error) {
      console.error('Error fetching prospects:', error)
    }
  }

  const fetchCampaigns = async () => {
    try {
      const response = await fetch('/api/marketing/campaigns', {
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      const data = await response.json()
      setCampaigns(data)
    } catch (error) {
      console.error('Error fetching campaigns:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchFunnel = async () => {
    try {
      const response = await fetch('/api/marketing/analytics/funnel', {
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      const data = await response.json()
      setFunnel(data)
    } catch (error) {
      console.error('Error fetching funnel:', error)
    }
  }

  const handleLaunchCampaign = async (campaignId) => {
    try {
      const response = await fetch(`/api/marketing/campaigns/${campaignId}/launch`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      if (response.ok) {
        fetchCampaigns()
      }
    } catch (error) {
      console.error('Error launching campaign:', error)
    }
  }

  const handlePauseCampaign = async (campaignId) => {
    try {
      const response = await fetch(`/api/marketing/campaigns/${campaignId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await user.getToken()}`
        }
      })
      if (response.ok) {
        fetchCampaigns()
      }
    } catch (error) {
      console.error('Error pausing campaign:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading marketing dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Marketing Dashboard</h1>
          <p className="text-gray-600 mt-2">Subscriber acquisition and campaign management</p>
        </div>

        {/* Period Selector */}
        <div className="mb-6 flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Period:</label>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>

        {/* Metrics Overview */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <UserGroupIcon className="h-10 w-10 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Prospects</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.prospects.total}</p>
                    <p className="text-sm text-green-600">+{analytics.prospects.new} new</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <EnvelopeIcon className="h-10 w-10 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Email Performance</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.campaigns.open_rate.toFixed(1)}%</p>
                    <p className="text-sm text-gray-600">Open rate</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <CursorArrowRaysIcon className="h-10 w-10 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Click Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.campaigns.click_rate.toFixed(1)}%</p>
                    <p className="text-sm text-gray-600">{analytics.campaigns.clicks} clicks</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <ArrowTrendingUpIcon className="h-10 w-10 text-orange-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Conversions</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.prospects.converted}</p>
                    <p className="text-sm text-gray-600">{analytics.conversion.conversion_rate.toFixed(1)}% rate</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('prospects')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'prospects'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Prospects
            </button>
            <button
              onClick={() => setActiveTab('campaigns')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'campaigns'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Campaigns
            </button>
            <button
              onClick={() => setActiveTab('funnel')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'funnel'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Funnel
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              </div>
              <div className="px-6 py-4">
                <div className="space-y-4">
                  {prospects.slice(0, 5).map(prospect => (
                    <div key={prospect.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {prospect.first_name} {prospect.last_name}
                        </p>
                        <p className="text-sm text-gray-600">{prospect.company_name}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        prospect.status === 'converted' ? 'bg-green-100 text-green-800' :
                        prospect.status === 'qualified' ? 'bg-blue-100 text-blue-800' :
                        prospect.status === 'engaged' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {prospect.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Campaign Performance */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Active Campaigns</h3>
              </div>
              <div className="px-6 py-4">
                <div className="space-y-4">
                  {campaigns.filter(c => c.status === 'active').slice(0, 3).map(campaign => (
                    <div key={campaign.id} className="border-l-4 border-blue-500 pl-4">
                      <p className="font-medium text-gray-900">{campaign.name}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span>Sent: {campaign.metrics?.total_sent || 0}</span>
                        <span>Opens: {campaign.metrics?.open_rate?.toFixed(1) || 0}%</span>
                        <span>Clicks: {campaign.metrics?.click_rate?.toFixed(1) || 0}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'prospects' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Prospects</h3>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
                <PlusIcon className="h-4 w-4" />
                Add Prospect
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lead Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {prospects.map(prospect => (
                    <tr key={prospect.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {prospect.first_name} {prospect.last_name}
                          </p>
                          <p className="text-sm text-gray-500">{prospect.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {prospect.company_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-900">{prospect.lead_score}</span>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${Math.min(prospect.lead_score, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          prospect.status === 'converted' ? 'bg-green-100 text-green-800' :
                          prospect.status === 'qualified' ? 'bg-blue-100 text-blue-800' :
                          prospect.status === 'engaged' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {prospect.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {prospect.source}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                        <button className="text-gray-600 hover:text-gray-900">Email</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Campaigns</h3>
              <button
                onClick={() => setShowCreateCampaign(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <PlusIcon className="h-4 w-4" />
                Create Campaign
              </button>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {campaigns.map(campaign => (
                <div key={campaign.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">{campaign.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">Type: {campaign.type}</p>
                      <div className="flex items-center gap-4 mt-3">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                          campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                          campaign.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {campaign.status}
                        </span>
                        {campaign.started_at && (
                          <span className="text-sm text-gray-600">
                            Started: {new Date(campaign.started_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => handleLaunchCampaign(campaign.id)}
                          className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-1 text-sm"
                        >
                          <PlayIcon className="h-4 w-4" />
                          Launch
                        </button>
                      )}
                      {campaign.status === 'active' && (
                        <button
                          onClick={() => handlePauseCampaign(campaign.id)}
                          className="px-3 py-1 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center gap-1 text-sm"
                        >
                          <PauseIcon className="h-4 w-4" />
                          Pause
                        </button>
                      )}
                    </div>
                  </div>

                  {campaign.metrics && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
                      <div>
                        <p className="text-sm text-gray-600">Sent</p>
                        <p className="text-xl font-semibold text-gray-900">{campaign.metrics.total_sent}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Opens</p>
                        <p className="text-xl font-semibold text-gray-900">
                          {campaign.metrics.opened} ({campaign.metrics.open_rate?.toFixed(1)}%)
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Clicks</p>
                        <p className="text-xl font-semibold text-gray-900">
                          {campaign.metrics.clicked} ({campaign.metrics.click_rate?.toFixed(1)}%)
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Replies</p>
                        <p className="text-xl font-semibold text-gray-900">{campaign.metrics.replied}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'funnel' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Conversion Funnel</h3>
            <div className="space-y-4">
              {Object.entries(funnel).map(([stage, count], index) => {
                const maxCount = Math.max(...Object.values(funnel))
                const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0

                return (
                  <div key={stage}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700 capitalize">{stage}</span>
                      <span className="text-sm font-semibold text-gray-900">{count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-8">
                      <div
                        className={`h-8 rounded-full flex items-center justify-end pr-3 text-white text-xs font-medium ${
                          index === 0 ? 'bg-blue-600' :
                          index === Object.keys(funnel).length - 1 ? 'bg-green-600' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${percentage}%`, minWidth: '80px' }}
                      >
                        {percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Conversion Insights</h4>
              <div className="space-y-2 text-sm text-gray-600">
                {analytics && (
                  <>
                    <p>• Lead qualification rate: {analytics.conversion.lead_rate.toFixed(1)}%</p>
                    <p>• Overall conversion rate: {analytics.conversion.conversion_rate.toFixed(1)}%</p>
                    <p>• Average time to conversion: ~14 days</p>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Create Campaign Modal */}
        {showCreateCampaign && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Campaign</h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Q1 Acquisition Campaign"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="email">Email</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="multi_channel">Multi-channel</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., finance, private-equity"
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateCampaign(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create Campaign
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MarketingDashboard