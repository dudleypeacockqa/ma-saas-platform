import React, { useState, useMemo } from 'react'
import { Plus, Filter, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { DealCard } from './DealCard'
import { DealForm } from './DealForm'
import { useDeals, useDealMutations } from '@/hooks/useDeals'
import type { Deal } from '@/services/dealService'
import { cn } from '@/lib/utils'

const DEAL_STAGES = [
  { value: 'sourcing', label: 'Sourcing', color: 'bg-gray-100' },
  { value: 'initial_review', label: 'Initial Review', color: 'bg-blue-100' },
  { value: 'nda_execution', label: 'NDA Execution', color: 'bg-indigo-100' },
  { value: 'preliminary_analysis', label: 'Preliminary Analysis', color: 'bg-purple-100' },
  { value: 'valuation', label: 'Valuation', color: 'bg-pink-100' },
  { value: 'due_diligence', label: 'Due Diligence', color: 'bg-orange-100' },
  { value: 'negotiation', label: 'Negotiation', color: 'bg-yellow-100' },
  { value: 'loi_drafting', label: 'LOI Drafting', color: 'bg-lime-100' },
  { value: 'documentation', label: 'Documentation', color: 'bg-green-100' },
  { value: 'closing', label: 'Closing', color: 'bg-emerald-100' },
]

const CLOSED_STAGES = [
  { value: 'closed_won', label: 'Closed Won', color: 'bg-green-200' },
  { value: 'closed_lost', label: 'Closed Lost', color: 'bg-red-200' },
  { value: 'on_hold', label: 'On Hold', color: 'bg-gray-200' },
]

export const DealPipeline: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [showClosed, setShowClosed] = useState(false)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [draggedDeal, setDraggedDeal] = useState<Deal | null>(null)

  const { deals, loading, error, refetch } = useDeals({ is_active: true })
  const { updateStage } = useDealMutations()

  // Filter deals
  const filteredDeals = useMemo(() => {
    return deals.filter((deal) => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesSearch =
          deal.title.toLowerCase().includes(query) ||
          deal.target_company_name.toLowerCase().includes(query) ||
          deal.code_name?.toLowerCase().includes(query) ||
          deal.deal_number.toLowerCase().includes(query)

        if (!matchesSearch) return false
      }

      // Priority filter
      if (priorityFilter !== 'all' && deal.priority !== priorityFilter) {
        return false
      }

      // Show/hide closed deals
      const isClosedDeal = ['closed_won', 'closed_lost', 'on_hold'].includes(deal.stage)
      if (!showClosed && isClosedDeal) {
        return false
      }

      return true
    })
  }, [deals, searchQuery, priorityFilter, showClosed])

  // Group deals by stage
  const dealsByStage = useMemo(() => {
    const stages = showClosed ? [...DEAL_STAGES, ...CLOSED_STAGES] : DEAL_STAGES
    const grouped: Record<string, Deal[]> = {}

    stages.forEach((stage) => {
      grouped[stage.value] = filteredDeals.filter((deal) => deal.stage === stage.value)
    })

    return grouped
  }, [filteredDeals, showClosed])

  // Calculate total value by stage
  const totalValueByStage = useMemo(() => {
    const totals: Record<string, number> = {}
    Object.entries(dealsByStage).forEach(([stage, deals]) => {
      totals[stage] = deals.reduce((sum, deal) => sum + (deal.deal_value || 0), 0)
    })
    return totals
  }, [dealsByStage])

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, deal: Deal) => {
    setDraggedDeal(deal)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragEnd = (e: React.DragEvent) => {
    setDraggedDeal(null)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = async (e: React.DragEvent, targetStage: string) => {
    e.preventDefault()

    if (!draggedDeal || draggedDeal.stage === targetStage) {
      setDraggedDeal(null)
      return
    }

    try {
      await updateStage(draggedDeal.id, targetStage)
      await refetch()
    } catch (error) {
      console.error('Failed to update deal stage:', error)
    } finally {
      setDraggedDeal(null)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount)
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-lg font-medium text-destructive">Error loading deals</p>
          <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
          <Button onClick={() => refetch()} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header and Filters */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Deal Pipeline</h1>
          <p className="text-muted-foreground mt-1">
            Manage your M&A deals through the pipeline
          </p>
        </div>
        <Button onClick={() => setIsFormOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Deal
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search deals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-40">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant={showClosed ? 'default' : 'outline'}
          onClick={() => setShowClosed(!showClosed)}
        >
          {showClosed ? 'Hide' : 'Show'} Closed
        </Button>
      </div>

      {/* Pipeline Columns */}
      <div className="overflow-x-auto pb-4">
        <div className="inline-flex gap-4 min-w-full">
          {(showClosed ? [...DEAL_STAGES, ...CLOSED_STAGES] : DEAL_STAGES).map((stage) => (
            <div
              key={stage.value}
              className="flex-shrink-0 w-80"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, stage.value)}
            >
              <Card className={cn('h-full', stage.color)}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-sm">{stage.label}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs">
                          {dealsByStage[stage.value]?.length || 0}
                        </Badge>
                        {totalValueByStage[stage.value] > 0 && (
                          <span className="text-xs text-muted-foreground">
                            {formatCurrency(totalValueByStage[stage.value])}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <ScrollArea className="h-[calc(100vh-320px)]">
                    <div className="space-y-3 pr-4">
                      {loading ? (
                        // Loading skeletons
                        <>
                          {[1, 2, 3].map((i) => (
                            <Skeleton key={i} className="h-48 w-full" />
                          ))}
                        </>
                      ) : (
                        <>
                          {dealsByStage[stage.value]?.map((deal) => (
                            <DealCard
                              key={deal.id}
                              deal={deal}
                              onDragStart={handleDragStart}
                              onDragEnd={handleDragEnd}
                              draggable
                            />
                          ))}

                          {(!dealsByStage[stage.value] ||
                            dealsByStage[stage.value].length === 0) && (
                            <div className="text-center py-8 text-muted-foreground text-sm">
                              No deals in this stage
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>

      {/* Create Deal Form */}
      <DealForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={async (data) => {
          // Handle in the form component
          await refetch()
        }}
        mode="create"
      />
    </div>
  )
}

export default DealPipeline
