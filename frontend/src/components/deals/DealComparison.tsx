import React, { useState } from 'react'
import { format } from 'date-fns'
import { X, Plus, ArrowRight, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useDeals, useDealComparison } from '@/hooks/useDeals'
import type { Deal } from '@/services/dealService'
import { cn } from '@/lib/utils'

export const DealComparison: React.FC = () => {
  const [selectedDealIds, setSelectedDealIds] = useState<string[]>([])
  const { deals, loading: dealsLoading } = useDeals({ is_active: true })
  const { comparison, loading: comparing, compareDeals } = useDealComparison()

  const handleAddDeal = (dealId: string) => {
    if (selectedDealIds.length < 5 && !selectedDealIds.includes(dealId)) {
      setSelectedDealIds([...selectedDealIds, dealId])
    }
  }

  const handleRemoveDeal = (dealId: string) => {
    setSelectedDealIds(selectedDealIds.filter((id) => id !== dealId))
  }

  const handleCompare = async () => {
    if (selectedDealIds.length >= 2) {
      await compareDeals(selectedDealIds)
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

  const formatMultiple = (multiple?: number) => {
    if (!multiple) return 'N/A'
    return `${multiple.toFixed(2)}x`
  }

  const availableDeals = deals.filter((d) => !selectedDealIds.includes(d.id))

  const comparisonRows = [
    { label: 'Deal Number', key: 'deal_number' },
    { label: 'Target Company', key: 'target_company_name' },
    { label: 'Industry', key: 'target_industry' },
    { label: 'Stage', key: 'stage', badge: true },
    { label: 'Priority', key: 'priority', badge: true },
    { label: 'Deal Type', key: 'deal_type' },
    { label: 'Deal Value', key: 'deal_value', format: 'currency' },
    { label: 'Enterprise Value', key: 'enterprise_value', format: 'currency' },
    { label: 'Equity Value', key: 'equity_value', format: 'currency' },
    { label: 'Revenue Multiple', key: 'revenue_multiple', format: 'multiple' },
    { label: 'EBITDA Multiple', key: 'ebitda_multiple', format: 'multiple' },
    { label: 'Probability of Close', key: 'probability_of_close', format: 'percentage' },
    { label: 'Risk Level', key: 'risk_level', badge: true },
    { label: 'Days in Pipeline', key: 'days_in_pipeline' },
    { label: 'Team Members', key: 'team_member_count' },
    { label: 'Documents', key: 'document_count' },
    { label: 'Activities', key: 'activity_count' },
    { label: 'Milestones', key: 'milestone_count' },
    { label: 'Deal Lead', key: 'deal_lead_name' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Compare Deals</h1>
        <p className="text-muted-foreground mt-1">
          Compare up to 5 deals side by side to evaluate opportunities
        </p>
      </div>

      {/* Deal Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Deals to Compare</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Selected Deals */}
            <div className="flex items-center gap-2 flex-wrap">
              {selectedDealIds.map((dealId) => {
                const deal = deals.find((d) => d.id === dealId)
                if (!deal) return null

                return (
                  <Badge key={dealId} variant="secondary" className="pl-3 pr-2 py-1.5">
                    <span className="mr-2">{deal.title}</span>
                    <button
                      onClick={() => handleRemoveDeal(dealId)}
                      className="hover:bg-destructive/20 rounded-sm"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )
              })}

              {selectedDealIds.length < 5 && (
                <Select onValueChange={handleAddDeal}>
                  <SelectTrigger className="w-64">
                    <Plus className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Add deal..." />
                  </SelectTrigger>
                  <SelectContent>
                    {availableDeals.map((deal) => (
                      <SelectItem key={deal.id} value={deal.id}>
                        {deal.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* Compare Button */}
            <div className="flex items-center gap-4">
              <Button
                onClick={handleCompare}
                disabled={selectedDealIds.length < 2 || comparing}
              >
                {comparing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Comparing...
                  </>
                ) : (
                  <>
                    Compare {selectedDealIds.length} Deals
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>

              {selectedDealIds.length < 2 && (
                <p className="text-sm text-muted-foreground">
                  Select at least 2 deals to compare
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comparison Table */}
      {comparison && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Comparison Results</CardTitle>
              <p className="text-sm text-muted-foreground">
                Compared on {format(new Date(comparison.comparison_date), 'MMM dd, yyyy HH:mm')}
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 bg-muted font-semibold sticky left-0 z-10">
                      Metric
                    </th>
                    {comparison.deals.map((deal) => (
                      <th key={deal.id} className="text-left p-3 bg-muted font-semibold min-w-48">
                        <div>
                          <p className="font-bold">{deal.title}</p>
                          <p className="text-xs font-normal text-muted-foreground mt-1">
                            {deal.deal_number}
                          </p>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparisonRows.map((row, index) => (
                    <tr key={row.key} className={cn('border-b', index % 2 === 0 && 'bg-muted/20')}>
                      <td className="p-3 font-medium sticky left-0 z-10 bg-background">
                        {row.label}
                      </td>
                      {comparison.deals.map((deal) => {
                        let value = deal[row.key as keyof Deal]

                        // Format value
                        if (row.format === 'currency') {
                          value = formatCurrency(value as number, deal.deal_currency)
                        } else if (row.format === 'multiple') {
                          value = formatMultiple(value as number)
                        } else if (row.format === 'percentage') {
                          value = value ? `${value}%` : 'N/A'
                        }

                        // Display as badge
                        if (row.badge && value) {
                          return (
                            <td key={deal.id} className="p-3">
                              <Badge variant="outline" className="capitalize">
                                {String(value).replace('_', ' ')}
                              </Badge>
                            </td>
                          )
                        }

                        return (
                          <td key={deal.id} className="p-3">
                            {value !== undefined && value !== null ? String(value) : 'N/A'}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Separator className="my-6" />

            {/* Summary Insights */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Key Insights</h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Highest Value
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const highest = comparison.deals.reduce((prev, current) =>
                        (current.deal_value || 0) > (prev.deal_value || 0) ? current : prev
                      )
                      return (
                        <>
                          <p className="font-bold truncate">{highest.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatCurrency(highest.deal_value, highest.deal_currency)}
                          </p>
                        </>
                      )
                    })()}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Highest Probability
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const highest = comparison.deals.reduce((prev, current) =>
                        current.probability_of_close > prev.probability_of_close ? current : prev
                      )
                      return (
                        <>
                          <p className="font-bold truncate">{highest.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {highest.probability_of_close}% probability
                          </p>
                        </>
                      )
                    })()}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Fastest Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const fastest = comparison.deals.reduce((prev, current) =>
                        current.days_in_pipeline < prev.days_in_pipeline ? current : prev
                      )
                      return (
                        <>
                          <p className="font-bold truncate">{fastest.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {fastest.days_in_pipeline} days
                          </p>
                        </>
                      )
                    })()}
                  </CardContent>
                </Card>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DealComparison
