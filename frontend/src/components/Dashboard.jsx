import { useState, useEffect } from 'react'
import { useUser, useOrganization, useOrganizationList, UserButton } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
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
  DollarSign
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu.jsx'
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'

function OrganizationSwitcher() {
  const { organization, isLoaded: orgLoaded } = useOrganization()
  const { isLoaded: listLoaded, organizationList, setActive } = useOrganizationList()
  const [isCreating, setIsCreating] = useState(false)
  const [isSwitching, setIsSwitching] = useState(false)

  if (!orgLoaded || !listLoaded) {
    return (
      <div className="flex items-center space-x-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-gray-500">Loading organizations...</span>
      </div>
    )
  }

  const handleSwitchOrganization = async (org) => {
    setIsSwitching(true)
    try {
      await setActive({ organization: org.id })
    } catch (error) {
      console.error('Error switching organization:', error)
    } finally {
      setIsSwitching(false)
    }
  }

  const handleCreateOrganization = async () => {
    setIsCreating(true)
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
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center space-x-2">
          <Building2 className="h-4 w-4" />
          <span className="max-w-[200px] truncate">
            {organization ? organization.name : 'Personal Account'}
          </span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Switch Organization</DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => handleSwitchOrganization(null)}
          disabled={!organization || isSwitching}
        >
          <Users className="mr-2 h-4 w-4" />
          Personal Account
          {!organization && <CheckCircle className="ml-auto h-4 w-4 text-green-500" />}
        </DropdownMenuItem>

        {organizationList?.map((org) => (
          <DropdownMenuItem
            key={org.organization.id}
            onClick={() => handleSwitchOrganization(org.organization)}
            disabled={organization?.id === org.organization.id || isSwitching}
          >
            <Building2 className="mr-2 h-4 w-4" />
            <span className="truncate">{org.organization.name}</span>
            {organization?.id === org.organization.id && (
              <CheckCircle className="ml-auto h-4 w-4 text-green-500" />
            )}
          </DropdownMenuItem>
        ))}

        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleCreateOrganization} disabled={isCreating}>
          <Plus className="mr-2 h-4 w-4" />
          {isCreating ? 'Creating...' : 'Create Organization'}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

function Dashboard() {
  const navigate = useNavigate()
  const { user, isLoaded: userLoaded } = useUser()
  const { organization, isLoaded: orgLoaded } = useOrganization()
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (userLoaded && orgLoaded) {
      loadDealData()
    }
  }, [userLoaded, orgLoaded, organization])

  const loadDealData = async () => {
    setLoading(true)
    setError(null)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))

      const mockDeals = organization ? [
        {
          id: 1,
          name: "TechCorp Acquisition",
          stage: "Due Diligence",
          value: "$2.5M",
          target: "TechCorp Ltd",
          progress: 65,
          status: "active",
          daysInStage: 12,
          nextAction: "Review financial statements",
          assignedTo: user?.fullName || "You"
        },
        {
          id: 2,
          name: "Manufacturing Buyout",
          stage: "Negotiation",
          value: "$8.2M",
          target: "Industrial Solutions",
          progress: 40,
          status: "active",
          daysInStage: 5,
          nextAction: "Schedule meeting with stakeholders",
          assignedTo: "Team Lead"
        },
        {
          id: 3,
          name: "SaaS Platform Purchase",
          stage: "Initial Review",
          value: "$1.8M",
          target: "CloudTech Inc",
          progress: 25,
          status: "pending",
          daysInStage: 3,
          nextAction: "Complete initial assessment",
          assignedTo: user?.fullName || "You"
        },
        {
          id: 4,
          name: "Retail Chain Merger",
          stage: "Closed",
          value: "$5.5M",
          target: "RetailPro Stores",
          progress: 100,
          status: "completed",
          daysInStage: 0,
          nextAction: "None - Deal completed",
          assignedTo: "Previous Team"
        }
      ] : [
        {
          id: 1,
          name: "Personal Investment",
          stage: "Research",
          value: "$500K",
          target: "StartupXYZ",
          progress: 15,
          status: "active",
          daysInStage: 2,
          nextAction: "Complete market analysis",
          assignedTo: user?.fullName || "You"
        }
      ]

      setDeals(mockDeals)
    } catch (err) {
      setError('Failed to load deal data. Please try again.')
      console.error('Error loading deals:', err)
    } finally {
      setLoading(false)
    }
  }

  const stats = organization ? [
    { label: "Active Deals", value: deals.filter(d => d.status === 'active').length.toString(), icon: Building2, color: "text-blue-600" },
    { label: "Total Value", value: "$17.5M", icon: DollarSign, color: "text-green-600" },
    { label: "Team Members", value: organization.membersCount?.toString() || "1", icon: Users, color: "text-purple-600" },
    { label: "Documents", value: "156", icon: FileText, color: "text-orange-600" }
  ] : [
    { label: "Active Investments", value: "1", icon: Building2, color: "text-blue-600" },
    { label: "Portfolio Value", value: "$500K", icon: DollarSign, color: "text-green-600" },
    { label: "Watchlist", value: "3", icon: Clock, color: "text-purple-600" },
    { label: "Reports", value: "8", icon: FileText, color: "text-orange-600" }
  ]

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'active': return 'default'
      case 'pending': return 'secondary'
      case 'completed': return 'outline'
      default: return 'default'
    }
  }

  const getStageColor = (stage) => {
    const stageColors = {
      'Initial Review': 'border-yellow-500',
      'Due Diligence': 'border-blue-500',
      'Negotiation': 'border-purple-500',
      'Closing': 'border-green-500',
      'Closed': 'border-gray-500',
      'Research': 'border-orange-500'
    }
    return stageColors[stage] || 'border-gray-400'
  }

  if (!userLoaded || !orgLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 mx-auto animate-spin" />
          <p className="text-gray-600 mt-4">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Building2 className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-900">M&A Platform</h1>
              <OrganizationSwitcher />
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="hidden sm:flex">
                {organization ? 'Organization' : 'Personal'}
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/profile')}
                className="hidden sm:flex"
              >
                <Settings className="h-4 w-4" />
              </Button>
              <UserButton
                afterSignOutUrl="/sign-in"
                appearance={{
                  elements: {
                    avatarBox: "h-9 w-9",
                    userButtonTrigger: "focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
                  }
                }}
              />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.firstName || 'User'}
          </h2>
          <p className="text-gray-600">
            {organization
              ? `Managing deals for ${organization.name}`
              : 'Managing your personal investment portfolio'
            }
          </p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Deal Pipeline</CardTitle>
                  <CardDescription>
                    {organization ? 'Active M&A transactions' : 'Your investment opportunities'}
                  </CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Deal
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  {deals.map((deal) => (
                    <div key={deal.id} className={`border-l-4 ${getStageColor(deal.stage)} pl-4 py-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow`}>
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 text-lg">{deal.name}</h4>
                          <p className="text-sm text-gray-600 mb-1">{deal.target}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={getStatusBadgeVariant(deal.status)}>
                            {deal.status}
                          </Badge>
                          <Badge variant="secondary">{deal.stage}</Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wider">Deal Value</p>
                          <p className="text-sm font-semibold text-green-600">{deal.value}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wider">Days in Stage</p>
                          <p className="text-sm font-medium text-gray-900">{deal.daysInStage} days</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wider">Assigned To</p>
                          <p className="text-sm font-medium text-gray-900">{deal.assignedTo}</p>
                        </div>
                      </div>

                      <div className="mb-3">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Next Action</p>
                        <p className="text-sm text-gray-700">{deal.nextAction}</p>
                      </div>

                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2 flex-1">
                          <Progress value={deal.progress} className="h-2 flex-1" />
                          <span className="text-xs text-gray-500 font-medium">{deal.progress}%</span>
                        </div>
                        <Button variant="ghost" size="sm" className="ml-4">
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!loading && deals.length === 0 && (
                <div className="text-center py-8">
                  <Building2 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No deals found</p>
                  <Button className="mt-4" variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Deal
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Button className="h-20 flex flex-col items-center justify-center">
                  <Building2 className="h-6 w-6 mb-2" />
                  New Deal
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                  <FileText className="h-6 w-6 mb-2" />
                  Upload Doc
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                  <BarChart3 className="h-6 w-6 mb-2" />
                  Analytics
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                  <Users className="h-6 w-6 mb-2" />
                  Team
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest updates across your deals</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Due diligence completed</p>
                    <p className="text-xs text-gray-500">TechCorp Acquisition • 2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FileText className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">New documents uploaded</p>
                    <p className="text-xs text-gray-500">Manufacturing Buyout • 5 hours ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Users className="h-5 w-5 text-purple-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Team member added</p>
                    <p className="text-xs text-gray-500">John Smith joined • Yesterday</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Action required</p>
                    <p className="text-xs text-gray-500">SaaS Platform Purchase • 2 days ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

export default Dashboard