import React from 'react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import {
  Building2,
  DollarSign,
  Calendar,
  Users,
  FileText,
  Activity,
  AlertTriangle,
  TrendingUp,
  Clock,
  ChevronRight
} from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import type { Deal } from '@/services/dealService'

interface DealCardProps {
  deal: Deal
  onDragStart?: (e: React.DragEvent, deal: Deal) => void
  onDragEnd?: (e: React.DragEvent) => void
  draggable?: boolean
  onClick?: () => void
}

const priorityColors = {
  critical: 'bg-red-600 text-white',
  high: 'bg-orange-600 text-white',
  medium: 'bg-yellow-600 text-white',
  low: 'bg-gray-600 text-white',
}

const stageLabels: Record<string, string> = {
  sourcing: 'Sourcing',
  initial_review: 'Initial Review',
  nda_execution: 'NDA Execution',
  preliminary_analysis: 'Preliminary Analysis',
  valuation: 'Valuation',
  due_diligence: 'Due Diligence',
  negotiation: 'Negotiation',
  loi_drafting: 'LOI Drafting',
  documentation: 'Documentation',
  closing: 'Closing',
  closed_won: 'Closed Won',
  closed_lost: 'Closed Lost',
  on_hold: 'On Hold',
}

export const DealCard: React.FC<DealCardProps> = ({
  deal,
  onDragStart,
  onDragEnd,
  draggable = false,
  onClick,
}) => {
  const formatCurrency = (amount?: number, currency: string = 'USD') => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set'
    return format(new Date(dateString), 'MMM dd, yyyy')
  }

  const getProbabilityColor = (probability: number) => {
    if (probability >= 75) return 'text-green-600'
    if (probability >= 50) return 'text-yellow-600'
    if (probability >= 25) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <Card
      className={cn(
        'group hover:shadow-lg transition-all duration-200 cursor-pointer',
        draggable && 'cursor-move hover:scale-[1.02]'
      )}
      draggable={draggable}
      onDragStart={(e) => onDragStart?.(e, deal)}
      onDragEnd={onDragEnd}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-base truncate group-hover:text-primary transition-colors">
              {deal.title}
            </h3>
            {deal.code_name && (
              <p className="text-xs text-muted-foreground mt-1">
                Code: {deal.code_name}
              </p>
            )}
          </div>
          <Badge className={priorityColors[deal.priority as keyof typeof priorityColors]}>
            {deal.priority}
          </Badge>
        </div>

        <div className="flex items-center gap-1 text-sm text-muted-foreground mt-2">
          <Building2 className="h-4 w-4" />
          <span className="truncate">{deal.target_company_name}</span>
        </div>

        {deal.target_industry && (
          <Badge variant="outline" className="mt-2 w-fit">
            {deal.target_industry}
          </Badge>
        )}
      </CardHeader>

      <CardContent className="pb-3 space-y-3">
        {/* Deal Value */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">
              {formatCurrency(deal.deal_value, deal.deal_currency)}
            </span>
          </div>
          {deal.enterprise_value && (
            <span className="text-xs text-muted-foreground">
              EV: {formatCurrency(deal.enterprise_value, deal.deal_currency)}
            </span>
          )}
        </div>

        {/* Probability of Close */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Probability</span>
            <span className={cn('font-medium', getProbabilityColor(deal.probability_of_close))}>
              {deal.probability_of_close}%
            </span>
          </div>
          <Progress value={deal.probability_of_close} className="h-1.5" />
        </div>

        {/* Days in Pipeline */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>{deal.days_in_pipeline} days in pipeline</span>
        </div>

        {/* Deal Lead */}
        {deal.deal_lead_name && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            <span className="truncate">{deal.deal_lead_name}</span>
          </div>
        )}

        {/* Risk Level */}
        {deal.risk_level && (
          <div className="flex items-center gap-2">
            <AlertTriangle className={cn(
              'h-4 w-4',
              deal.risk_level === 'critical' && 'text-red-600',
              deal.risk_level === 'high' && 'text-orange-600',
              deal.risk_level === 'medium' && 'text-yellow-600',
              deal.risk_level === 'low' && 'text-green-600'
            )} />
            <span className="text-sm capitalize">{deal.risk_level} Risk</span>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between pt-3 border-t">
        {/* Stats */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {deal.team_member_count !== undefined && (
            <div className="flex items-center gap-1" title="Team members">
              <Users className="h-3.5 w-3.5" />
              <span>{deal.team_member_count}</span>
            </div>
          )}
          {deal.document_count !== undefined && (
            <div className="flex items-center gap-1" title="Documents">
              <FileText className="h-3.5 w-3.5" />
              <span>{deal.document_count}</span>
            </div>
          )}
          {deal.activity_count !== undefined && (
            <div className="flex items-center gap-1" title="Activities">
              <Activity className="h-3.5 w-3.5" />
              <span>{deal.activity_count}</span>
            </div>
          )}
        </div>

        {/* View Button */}
        <Button
          variant="ghost"
          size="sm"
          className="h-8 px-2"
          onClick={(e) => {
            e.stopPropagation()
          }}
          asChild
        >
          <Link to={`/deals/${deal.id}`} className="flex items-center gap-1">
            View
            <ChevronRight className="h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>

      {/* Updated Date */}
      <div className="px-6 pb-3 text-xs text-muted-foreground">
        Updated {format(new Date(deal.updated_at), 'MMM dd, yyyy')}
      </div>
    </Card>
  )
}

export default DealCard
