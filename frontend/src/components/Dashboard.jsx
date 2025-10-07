import { useState, useEffect } from 'react'
import { useUser, useOrganization, useOrganizationList, UserButton } from '@clerk/clerk-react'
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
  const navigate = useNavigate()
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalDeals: 0,
    activeDeals: 0,
    portfolioValue: 0,
    avgDealSize: 0,
    closedThisMonth: 0,
    pipeline: 0,
    winRate: 0,
    avgTimeToClose: 0
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
      // Mock data for now
      await new Promise(resolve => setTimeout(resolve, 500))

      const mockDeals = [
        {
          id: 1,
          name: 'TechCorp Acquisition',
          stage: 'Due Diligence',
          value: 5000000,
          probability: 75,
          expectedClose: '2024-03-15',
          priority: 'high'
        },
        {
          id: 2,
          name: 'DataFlow Merger',
          stage: 'Negotiation',
          value: 12000000,
          probability: 60,
          expectedClose: '2024-04-01',
          priority: 'medium'
        },
        {
          id: 3,
          name: 'CloudBase Investment',
          stage: 'Initial Review',
          value: 3500000,
          probability: 30,
          expectedClose: '2024-05-20',
          priority: 'low'
        },
        {
          id: 4,
          name: 'RetailPro Buyout',
          stage: 'LOI Drafting',
          value: 8000000,
          probability: 85,
          expectedClose: '2024-02-28',
          priority: 'high'
        }
      ]

      setDeals(mockDeals)
      setStats({
        totalDeals: mockDeals.length,
        activeDeals: mockDeals.filter(d => d.stage !== 'Closed').length,
        portfolioValue: mockDeals.reduce((sum, d) => sum + d.value, 0),
        avgDealSize: mockDeals.reduce((sum, d) => sum + d.value, 0) / mockDeals.length,
        closedThisMonth: 2,
        pipeline: mockDeals.reduce((sum, d) => sum + (d.value * d.probability / 100), 0),
        winRate: 67,
        avgTimeToClose: 45
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
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

  const getStageColor = (stage) => {
    const colors = {
      'Initial Review': 'bg-gray-100 text-gray-700',
      'Due Diligence': 'bg-blue-100 text-blue-700',
      'Negotiation': 'bg-yellow-100 text-yellow-700',
      'LOI Drafting': 'bg-purple-100 text-purple-700',
      'Documentation': 'bg-orange-100 text-orange-700',
      'Closing': 'bg-green-100 text-green-700',
      'Closed': 'bg-gray-500 text-white'
    }
    return colors[stage] || 'bg-gray-100 text-gray-700'
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'high': 'text-red-600',
      'medium': 'text-yellow-600',
      'low': 'text-gray-600'
    }
    return colors[priority] || 'text-gray-600'
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
              <p className="text-2xl font-bold text-gray-900">{stats.totalDeals}</p>
              <p className="text-sm text-gray-600">Active Investments</p>
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
              <span className="text-sm font-medium text-purple-600">{stats.winRate}%</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.pipeline)}</p>
              <p className="text-sm text-gray-600">Pipeline Value</p>
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
              <p className="text-2xl font-bold text-gray-900">{stats.avgTimeToClose}</p>
              <p className="text-sm text-gray-600">Avg. Days to Close</p>
            </div>
          </div>
        </div>

        {/* Recent Activity Alert */}
        <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-blue-600 mr-2" />
            <p className="text-sm text-blue-900">
              <span className="font-medium">3 deals</span> require your attention today
            </p>
          </div>
        </div>

        {/* Deal Pipeline */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Deal Pipeline</h3>
                <p className="text-sm text-gray-600 mt-1">Your investment opportunities</p>
              </div>
              <button
                onClick={() => navigate('/deals')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                <span>New Deal</span>
              </button>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
              <p className="text-gray-600 mt-4">Loading deals...</p>
            </div>
          ) : deals.length === 0 ? (
            <div className="p-12 text-center">
              <Briefcase className="h-12 w-12 text-gray-400 mx-auto" />
              <p className="text-gray-600 mt-4">No active deals</p>
              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium">
                Create your first deal →
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Deal Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stage
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Probability
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Expected Close
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deals.map((deal) => (
                    <tr key={deal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className={`h-2 w-2 rounded-full mr-2 ${getPriorityColor(deal.priority)} bg-current`} />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{deal.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(deal.stage)}`}>
                          {deal.stage}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(deal.value)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm text-gray-900">{deal.probability}%</div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${deal.probability}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(deal.expectedClose).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button className="text-blue-600 hover:text-blue-700 flex items-center space-x-1">
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