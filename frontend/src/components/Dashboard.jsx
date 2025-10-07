import { useState, useEffect } from 'react'
import { useUser, useOrganization, useOrganizationList, UserButton, useAuth } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import {
  Building2,
  TrendingUp,
  Users,
  FileText,
  BarChart3,
  Settings,
  ChevronDown,
  Plus,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Activity,
  Target,
  Briefcase,
  Calendar,
  ChevronRight,
  Eye
} from 'lucide-react'

function OrganizationSwitcher() {
  const { organization, isLoaded: orgLoaded } = useOrganization()
  const { isLoaded: listLoaded, organizationList, setActive } = useOrganizationList()
  const [isCreating, setIsCreating] = useState(false)
  const [isSwitching, setIsSwitching] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  if (!orgLoaded || !listLoaded) {
    return (
      <div className="flex items-center space-x-2">
        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
        <span className="text-sm text-gray-500">Loading organizations...</span>
      </div>
    )
  }

  const handleSwitchOrganization = async (org) => {
    setIsSwitching(true)
    setIsOpen(false)
    try {
      await setActive({ organization: org?.id || null })
    } catch (error) {
      console.error('Error switching organization:', error)
    } finally {
      setIsSwitching(false)
    }
  }

  const handleCreateOrganization = async () => {
    setIsCreating(true)
    setIsOpen(false)
    try {
      const orgName = prompt('Enter organization name:')
      if (orgName) {
        const newOrg = await organizationList.createOrganization({ name: orgName })
        await setActive({ organization: newOrg.id })
      }
    } catch (error) {
      console.error('Error creating organization:', error)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <Building2 className="h-4 w-4 text-gray-600" />
        <span className="max-w-[200px] truncate text-gray-900 font-medium">
          {organization ? organization.name : 'Personal Account'}
        </span>
        <ChevronDown className={`h-4 w-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <div className="px-4 py-2 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-700">Switch Organization</p>
          </div>

          <div className="py-2">
            <button
              onClick={() => handleSwitchOrganization(null)}
              disabled={!organization || isSwitching}
              className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 disabled:opacity-50"
            >
              <Users className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-900">Personal Account</span>
              {!organization && <CheckCircle className="ml-auto h-4 w-4 text-green-500" />}
            </button>

            {organizationList?.map(({ organization: org }) => (
              <button
                key={org.id}
                onClick={() => handleSwitchOrganization(org)}
                disabled={organization?.id === org.id || isSwitching}
                className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 disabled:opacity-50"
              >
                <Building2 className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-900">{org.name}</span>
                {organization?.id === org.id && <CheckCircle className="ml-auto h-4 w-4 text-green-500" />}
              </button>
            ))}
          </div>

          <div className="px-4 py-2 border-t border-gray-200">
            <button
              onClick={handleCreateOrganization}
              disabled={isCreating}
              className="w-full flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <Plus className="h-4 w-4" />
              <span className="text-sm">Create Organization</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { organization } = useOrganization()
  const { getToken } = useAuth()
  const navigate = useNavigate()
  const [opportunities, setOpportunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalOpportunities: 0,
    activeOpportunities: 0,
    portfolioValue: 0,
    avgOpportunitySize: 0,
    newThisMonth: 0,
    pipeline: 0,
    conversionRate: 0,
    avgScore: 0
  })

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      navigate('/sign-in')
    }
  }, [isLoaded, isSignedIn, navigate])

  useEffect(() => {
    loadDashboardData()
  }, [organization])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const token = await getToken()
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }

      // Fetch opportunities from API
      const response = await fetch('/api/opportunities/', {
        headers
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const opportunitiesData = await response.json()

      // Fetch pipeline metrics
      const metricsResponse = await fetch('/api/opportunities/metrics/pipeline', {
        headers
      })

      let metrics = null
      if (metricsResponse.ok) {
        metrics = await metricsResponse.json()
      }

      setOpportunities(opportunitiesData)

      // Calculate stats from opportunities data
      const totalValue = opportunitiesData.reduce((sum, opp) => sum + (opp.annual_revenue || 0), 0)
      const avgScore = opportunitiesData.length > 0
        ? opportunitiesData.reduce((sum, opp) => sum + (opp.overall_score || 0), 0) / opportunitiesData.length
        : 0

      setStats({
        totalOpportunities: opportunitiesData.length,
        activeOpportunities: opportunitiesData.filter(o => o.status !== 'REJECTED' && o.status !== 'COMPLETED').length,
        portfolioValue: totalValue,
        avgOpportunitySize: opportunitiesData.length > 0 ? totalValue / opportunitiesData.length : 0,
        newThisMonth: metrics?.new_this_week || 0,
        pipeline: totalValue,
        conversionRate: metrics?.conversion_rate || 0,
        avgScore: avgScore
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      // Keep empty state on error
      setOpportunities([])
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const getStatusColor = (status) => {
    const colors = {
      'NEW': 'bg-blue-100 text-blue-700',
      'RESEARCHING': 'bg-yellow-100 text-yellow-700',
      'CONTACTED': 'bg-purple-100 text-purple-700',
      'QUALIFIED': 'bg-green-100 text-green-700',
      'IN_DISCUSSION': 'bg-orange-100 text-orange-700',
      'REJECTED': 'bg-red-100 text-red-700',
      'COMPLETED': 'bg-gray-500 text-white'
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    if (score >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  const formatStatus = (status) => {
    const statusLabels = {
      'NEW': 'New',
      'RESEARCHING': 'Researching',
      'CONTACTED': 'Contacted',
      'QUALIFIED': 'Qualified',
      'IN_DISCUSSION': 'In Discussion',
      'REJECTED': 'Rejected',
      'COMPLETED': 'Completed'
    }
    return statusLabels[status] || status
  }

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 mt-4">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">M&A Platform</h1>
              <OrganizationSwitcher />
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/profile')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="h-5 w-5" />
              </button>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.firstName || 'there'}!
          </h2>
          <p className="text-gray-600 mt-1">
            {organization ? `Managing ${organization.name}'s investment portfolio` : 'Managing your personal investment portfolio'}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Briefcase className="h-6 w-6 text-blue-600" />
              </div>
              <span className="text-sm text-gray-500">This month</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalOpportunities}</p>
              <p className="text-sm text-gray-600">Total Opportunities</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.portfolioValue)}</p>
              <p className="text-sm text-gray-600">Portfolio Value</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
              <span className="text-sm font-medium text-purple-600">{Math.round(stats.conversionRate)}%</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.pipeline)}</p>
              <p className="text-sm text-gray-600">Portfolio Value</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="h-6 w-6 text-orange-600" />
              </div>
              <Activity className="h-4 w-4 text-gray-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{Math.round(stats.avgScore)}</p>
              <p className="text-sm text-gray-600">Avg. Opportunity Score</p>
            </div>
          </div>
        </div>

        {/* Recent Activity Alert */}
        <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-blue-600 mr-2" />
            <p className="text-sm text-blue-900">
              <span className="font-medium">{stats.activeOpportunities} opportunities</span> are actively being tracked
            </p>
          </div>
        </div>

        {/* Opportunity Pipeline */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Opportunity Pipeline</h3>
                <p className="text-sm text-gray-600 mt-1">Your M&A opportunities</p>
              </div>
              <button
                onClick={() => navigate('/opportunities')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                <span>New Opportunity</span>
              </button>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
              <p className="text-gray-600 mt-4">Loading opportunities...</p>
            </div>
          ) : opportunities.length === 0 ? (
            <div className="p-12 text-center">
              <Briefcase className="h-12 w-12 text-gray-400 mx-auto" />
              <p className="text-gray-600 mt-4">No opportunities found</p>
              <button
                onClick={() => navigate('/opportunities')}
                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
              >
                Discover your first opportunity →
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Industry
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {opportunities.map((opportunity) => (
                    <tr key={opportunity.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className={`h-2 w-2 rounded-full mr-2 ${getScoreColor(opportunity.overall_score || 0)} bg-current`} />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{opportunity.company_name}</div>
                            <div className="text-xs text-gray-500">{opportunity.region}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(opportunity.status)}`}>
                          {formatStatus(opportunity.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {opportunity.annual_revenue ? formatCurrency(opportunity.annual_revenue) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className={`text-sm ${getScoreColor(opportunity.overall_score || 0)}`}>
                            {opportunity.overall_score ? Math.round(opportunity.overall_score) : 'N/A'}
                          </div>
                          {opportunity.overall_score && (
                            <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${opportunity.overall_score >= 70 ? 'bg-green-600' : opportunity.overall_score >= 50 ? 'bg-yellow-600' : 'bg-red-600'}`}
                                style={{ width: `${opportunity.overall_score}%` }}
                              />
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {opportunity.industry_vertical?.replace('_', ' ') || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => navigate(`/opportunities/${opportunity.id}`)}
                          className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                        >
                          <Eye className="h-4 w-4" />
                          <span>View</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Personal Investment Section */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Investment</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">StartupXYZ</span>
                <span className="text-sm font-medium text-gray-900">$150,000</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">activeResearch</span>
                <span className="text-sm font-medium text-gray-900">$75,000</span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-900">Total Personal Portfolio</span>
                  <span className="text-base font-bold text-gray-900">$225,000</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-900">LOI signed for TechCorp</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Clock className="h-5 w-5 text-yellow-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-900">Due diligence started for DataFlow</p>
                  <p className="text-xs text-gray-500">Yesterday</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <FileText className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-900">New documents received for CloudBase</p>
                  <p className="text-xs text-gray-500">3 days ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}