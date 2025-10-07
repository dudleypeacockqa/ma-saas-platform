import React, { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { format } from 'date-fns'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Building2,
  DollarSign,
  Calendar,
  TrendingUp,
  Users,
  FileText,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock,
  Loader2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { DealForm } from './DealForm'
import { DealTimeline } from './DealTimeline'
import { DealFinancials } from './DealFinancials'
import { DealDocuments } from './DealDocuments'
import { useDeal, useDealMutations, useDealTeam, useDealMilestones } from '@/hooks/useDeals'
import { cn } from '@/lib/utils'

const priorityColors = {
  critical: 'bg-red-600 text-white',
  high: 'bg-orange-600 text-white',
  medium: 'bg-yellow-600 text-white',
  low: 'bg-gray-600 text-white',
}

const stageColors: Record<string, string> = {
  sourcing: 'bg-gray-500',
  initial_review: 'bg-blue-500',
  nda_execution: 'bg-indigo-500',
  preliminary_analysis: 'bg-purple-500',
  valuation: 'bg-pink-500',
  due_diligence: 'bg-orange-500',
  negotiation: 'bg-yellow-500',
  loi_drafting: 'bg-lime-500',
  documentation: 'bg-green-500',
  closing: 'bg-emerald-500',
  closed_won: 'bg-green-600',
  closed_lost: 'bg-red-600',
  on_hold: 'bg-gray-600',
}

export const DealDetail: React.FC = () => {
  const { dealId } = useParams<{ dealId: string }>()
  const navigate = useNavigate()
  const [isEditFormOpen, setIsEditFormOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  const { deal, loading, error, refetch } = useDeal(dealId || null)
  const { deleteDeal } = useDealMutations()
  const { teamMembers, loading: teamLoading } = useDealTeam(dealId || null)
  const { milestones, loading: milestonesLoading } = useDealMilestones(dealId || null)

  const handleDelete = async () => {
    if (!dealId || !deal) return

    if (
      confirm(
        `Are you sure you want to delete "${deal.title}"? This action cannot be undone.`
      )
    ) {
      try {
        await deleteDeal(dealId)
        navigate('/deals')
      } catch (error) {
        console.error('Failed to delete deal:', error)
      }
    }
  }

  const formatCurrency = (amount?: number, currency: string = 'USD') => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-12 w-12 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !deal) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-destructive" />
          <p className="text-lg font-medium">Deal not found</p>
          <p className="text-sm text-muted-foreground mt-2">
            {error?.message || 'The deal you are looking for does not exist.'}
          </p>
          <Button onClick={() => navigate('/deals')} className="mt-4">
            Back to Deals
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/deals">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Pipeline
              </Link>
            </Button>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <h1 className="text-3xl font-bold">{deal.title}</h1>
            <Badge className={priorityColors[deal.priority as keyof typeof priorityColors]}>
              {deal.priority}
            </Badge>
            <Badge className={cn('text-white', stageColors[deal.stage])}>
              {deal.stage.replace('_', ' ')}
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-sm">{deal.deal_number}</span>
            {deal.code_name && (
              <>
                <span>•</span>
                <span className="text-sm">Code: {deal.code_name}</span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setIsEditFormOpen(true)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" onClick={handleDelete} className="text-destructive">
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Deal Value
              </CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(deal.deal_value, deal.deal_currency)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {deal.deal_currency} currency
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Probability
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deal.probability_of_close}%</div>
            <Progress value={deal.probability_of_close} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Days in Pipeline
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deal.days_in_pipeline}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Since {format(new Date(deal.created_at), 'MMM dd, yyyy')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Team Size
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deal.team_member_count || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Team members</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Target Company Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Target Company
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Company Name</p>
                  <p className="font-semibold">{deal.target_company_name}</p>
                </div>

                {deal.target_company_website && (
                  <div>
                    <p className="text-sm text-muted-foreground">Website</p>
                    <a
                      href={deal.target_company_website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      {deal.target_company_website}
                    </a>
                  </div>
                )}

                {deal.target_industry && (
                  <div>
                    <p className="text-sm text-muted-foreground">Industry</p>
                    <Badge variant="outline" className="mt-1">
                      {deal.target_industry}
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Key Information */}
            <Card>
              <CardHeader>
                <CardTitle>Key Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Deal Type</p>
                  <p className="font-semibold capitalize">{deal.deal_type.replace('_', ' ')}</p>
                </div>

                {deal.risk_level && (
                  <div>
                    <p className="text-sm text-muted-foreground">Risk Level</p>
                    <Badge
                      variant="outline"
                      className={cn(
                        deal.risk_level === 'critical' && 'border-red-600 text-red-600',
                        deal.risk_level === 'high' && 'border-orange-600 text-orange-600',
                        deal.risk_level === 'medium' && 'border-yellow-600 text-yellow-600',
                        deal.risk_level === 'low' && 'border-green-600 text-green-600'
                      )}
                    >
                      {deal.risk_level}
                    </Badge>
                  </div>
                )}

                {deal.deal_lead_name && (
                  <div>
                    <p className="text-sm text-muted-foreground">Deal Lead</p>
                    <p className="font-semibold">{deal.deal_lead_name}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Milestones */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Upcoming Milestones
              </CardTitle>
            </CardHeader>
            <CardContent>
              {milestonesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : milestones.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No milestones yet</p>
              ) : (
                <div className="space-y-3">
                  {milestones.slice(0, 5).map((milestone) => (
                    <div
                      key={milestone.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            'w-2 h-2 rounded-full',
                            milestone.status === 'completed'
                              ? 'bg-green-500'
                              : milestone.is_overdue
                              ? 'bg-red-500'
                              : 'bg-yellow-500'
                          )}
                        />
                        <div>
                          <p className="font-medium">{milestone.title}</p>
                          {milestone.owner_name && (
                            <p className="text-sm text-muted-foreground">
                              Owner: {milestone.owner_name}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge
                          variant={milestone.is_critical ? 'destructive' : 'outline'}
                          className="mb-1"
                        >
                          {milestone.is_critical ? 'Critical' : milestone.status}
                        </Badge>
                        <p className="text-xs text-muted-foreground">
                          {format(new Date(milestone.target_date), 'MMM dd, yyyy')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Financials Tab */}
        <TabsContent value="financials" className="mt-6">
          <DealFinancials deal={deal} />
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline" className="mt-6">
          <DealTimeline dealId={deal.id} />
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="mt-6">
          <DealDocuments dealId={deal.id} />
        </TabsContent>

        {/* Team Tab */}
        <TabsContent value="team" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
            </CardHeader>
            <CardContent>
              {teamLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : teamMembers.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No team members yet</p>
              ) : (
                <div className="space-y-3">
                  {teamMembers.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <p className="font-semibold">{member.user_name || 'Unknown'}</p>
                        <p className="text-sm text-muted-foreground">{member.role}</p>
                        {member.responsibilities && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {member.responsibilities}
                          </p>
                        )}
                      </div>
                      {member.time_allocation_percentage && (
                        <Badge variant="outline">
                          {member.time_allocation_percentage}% allocated
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Form Dialog */}
      <DealForm
        isOpen={isEditFormOpen}
        onClose={() => setIsEditFormOpen(false)}
        onSubmit={async () => {
          await refetch()
        }}
        initialData={deal as any}
        mode="edit"
      />
    </div>
  )
}

export default DealDetail
