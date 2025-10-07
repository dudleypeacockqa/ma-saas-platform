import React, { useState } from 'react'
import { format } from 'date-fns'
import { Plus, TrendingUp, DollarSign, Calculator, Loader2, Edit } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useDealValuations } from '@/hooks/useDeals'
import type { Deal, DealValuationCreate } from '@/services/dealService'

interface DealFinancialsProps {
  deal: Deal
}

const valuationFormSchema = z.object({
  valuation_date: z.string().min(1, 'Valuation date is required'),
  valuation_method: z.string().min(1, 'Valuation method is required'),
  enterprise_value_low: z.number().optional(),
  enterprise_value_mid: z.number().optional(),
  enterprise_value_high: z.number().optional(),
  notes: z.string().optional(),
})

type ValuationFormData = z.infer<typeof valuationFormSchema>

export const DealFinancials: React.FC<DealFinancialsProps> = ({ deal }) => {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const { valuations, loading, createValuation } = useDealValuations(deal.id)

  const form = useForm<ValuationFormData>({
    resolver: zodResolver(valuationFormSchema),
    defaultValues: {
      valuation_date: new Date().toISOString().split('T')[0],
      valuation_method: 'dcf',
      notes: '',
    },
  })

  const handleSubmit = async (data: ValuationFormData) => {
    try {
      setSubmitting(true)
      await createValuation(data as DealValuationCreate)
      form.reset()
      setIsFormOpen(false)
    } catch (error) {
      console.error('Failed to create valuation:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: deal.deal_currency || 'USD',
      notation: 'compact',
      maximumFractionDigits: 2,
    }).format(amount)
  }

  const formatFullCurrency = (amount?: number) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: deal.deal_currency || 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatMultiple = (multiple?: number) => {
    if (!multiple) return 'N/A'
    return `${multiple.toFixed(2)}x`
  }

  return (
    <div className="space-y-6">
      {/* Key Financial Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Key Financial Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Deal Value</p>
              <p className="text-2xl font-bold">{formatCurrency(deal.deal_value)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Enterprise Value</p>
              <p className="text-2xl font-bold">{formatCurrency(deal.enterprise_value)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Equity Value</p>
              <p className="text-xl font-semibold">{formatCurrency(deal.equity_value)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Debt Assumed</p>
              <p className="text-xl font-semibold">{formatCurrency(deal.debt_assumed)}</p>
            </div>
          </div>

          <Separator className="my-6" />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Revenue Multiple</p>
              <p className="text-xl font-semibold">{formatMultiple(deal.revenue_multiple)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">EBITDA Multiple</p>
              <p className="text-xl font-semibold">{formatMultiple(deal.ebitda_multiple)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Target Revenue</p>
              <p className="text-lg font-medium">{formatCurrency(deal.target_revenue)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Target EBITDA</p>
              <p className="text-lg font-medium">{formatCurrency(deal.target_ebitda)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Deal Structure */}
      <Card>
        <CardHeader>
          <CardTitle>Deal Structure</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <p className="text-sm font-medium text-green-900">Cash</p>
                </div>
                <p className="text-xl font-bold text-green-700">
                  {formatCurrency(deal.cash_consideration)}
                </p>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                  <p className="text-sm font-medium text-blue-900">Stock</p>
                </div>
                <p className="text-xl font-bold text-blue-700">
                  {formatCurrency(deal.stock_consideration)}
                </p>
              </div>

              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <Calculator className="h-4 w-4 text-purple-600" />
                  <p className="text-sm font-medium text-purple-900">Earnout</p>
                </div>
                <p className="text-xl font-bold text-purple-700">
                  {formatCurrency(deal.earnout_consideration)}
                </p>
              </div>
            </div>

            {deal.ownership_percentage && (
              <div className="p-4 bg-gray-50 rounded-lg border">
                <p className="text-sm text-muted-foreground mb-1">Ownership Percentage</p>
                <p className="text-2xl font-bold">{deal.ownership_percentage}%</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Valuation History */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Valuation History</CardTitle>
            <Button onClick={() => setIsFormOpen(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Valuation
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : valuations.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No valuations yet</p>
              <p className="text-sm mt-2">Add valuation analyses to track deal value over time</p>
              <Button onClick={() => setIsFormOpen(true)} variant="outline" className="mt-4">
                Add First Valuation
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {valuations.map((valuation) => (
                <div key={valuation.id} className="p-4 border rounded-lg hover:bg-accent transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">{valuation.valuation_method.toUpperCase()}</h4>
                        <Badge variant="outline">
                          {format(new Date(valuation.valuation_date), 'MMM dd, yyyy')}
                        </Badge>
                      </div>
                      {valuation.prepared_by && (
                        <p className="text-sm text-muted-foreground">
                          Prepared by {valuation.prepared_by}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Low</p>
                      <p className="font-semibold">{formatFullCurrency(valuation.enterprise_value_low)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Mid (Base Case)</p>
                      <p className="font-bold text-lg">{formatFullCurrency(valuation.enterprise_value_mid)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">High</p>
                      <p className="font-semibold">{formatFullCurrency(valuation.enterprise_value_high)}</p>
                    </div>
                  </div>

                  {valuation.notes && (
                    <div className="mt-3 p-2 bg-muted rounded text-sm">
                      {valuation.notes}
                    </div>
                  )}

                  {valuation.assumptions && Object.keys(valuation.assumptions).length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-medium mb-2">Key Assumptions:</p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(valuation.assumptions).map(([key, value]) => (
                          <Badge key={key} variant="secondary" className="text-xs">
                            {key}: {String(value)}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Valuation Dialog */}
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Valuation</DialogTitle>
            <DialogDescription>
              Record a new valuation analysis for this deal
            </DialogDescription>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="valuation_method"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Valuation Method</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select method" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="dcf">DCF (Discounted Cash Flow)</SelectItem>
                          <SelectItem value="comparable_companies">Comparable Companies</SelectItem>
                          <SelectItem value="precedent_transactions">Precedent Transactions</SelectItem>
                          <SelectItem value="asset_based">Asset-Based Valuation</SelectItem>
                          <SelectItem value="lbo">LBO Analysis</SelectItem>
                          <SelectItem value="sum_of_parts">Sum of Parts</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="valuation_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Valuation Date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <Separator />

              <div className="space-y-4">
                <FormLabel>Enterprise Value Range</FormLabel>
                <div className="grid grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="enterprise_value_low"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs">Low Case</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="enterprise_value_mid"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs">Base Case</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="enterprise_value_high"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs">Upside Case</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <FormDescription>
                  Enter enterprise values in {deal.deal_currency || 'USD'}
                </FormDescription>
              </div>

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Key assumptions, methodology notes, or important observations..."
                        className="resize-none h-24"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsFormOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting}>
                  {submitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Add Valuation'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default DealFinancials
