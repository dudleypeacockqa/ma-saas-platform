import React from 'react'
import {
  TrendingUp,
  DollarSign,
  CheckCircle,
  Clock,
  BarChart3,
  PieChart,
  Loader2,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useDealAnalytics } from '@/hooks/useDeals'

export const DealAnalytics: React.FC = () => {
  const { analytics, loading, error } = useDealAnalytics()

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
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

  if (error || !analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load analytics</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Deal Analytics</h1>
        <p className="text-muted-foreground mt-1">
          Insights and performance metrics across your deal pipeline
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Deals
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analytics.total_deals}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {analytics.active_deals} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pipeline Value
              </CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {formatCurrency(analytics.total_pipeline_value)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Total deal value</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Win Rate
              </CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analytics.win_rate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">Closed deals won</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg. Days to Close
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analytics.average_days_to_close}</div>
            <p className="text-xs text-muted-foreground mt-1">Average timeline</p>
          </CardContent>
        </Card>
      </div>

      {/* Deals by Stage */}
      <Card>
        <CardHeader>
          <CardTitle>Deals by Stage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(analytics.deals_by_stage).map(([stage, count]) => {
              const percentage = analytics.active_deals > 0
                ? ((count / analytics.active_deals) * 100).toFixed(1)
                : 0

              return (
                <div key={stage} className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-32">
                      <p className="text-sm font-medium capitalize">
                        {stage.replace('_', ' ')}
                      </p>
                    </div>
                    <div className="flex-1 bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <Badge variant="secondary">{count}</Badge>
                    <span className="text-sm text-muted-foreground w-12 text-right">
                      {percentage}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Deals by Priority */}
        <Card>
          <CardHeader>
            <CardTitle>Deals by Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(analytics.deals_by_priority).map(([priority, count]) => (
                <div key={priority} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        priority === 'critical'
                          ? 'bg-red-600'
                          : priority === 'high'
                          ? 'bg-orange-600'
                          : priority === 'medium'
                          ? 'bg-yellow-600'
                          : 'bg-gray-600'
                      }`}
                    />
                    <span className="text-sm font-medium capitalize">{priority}</span>
                  </div>
                  <Badge variant="outline">{count} deals</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Deals by Industry */}
        <Card>
          <CardHeader>
            <CardTitle>Deals by Industry</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(analytics.deals_by_industry)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([industry, count]) => (
                  <div key={industry} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">
                      {industry.replace('_', ' ')}
                    </span>
                    <Badge variant="secondary">{count} deals</Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Deal Leads */}
      <Card>
        <CardHeader>
          <CardTitle>Top Deal Leads</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics.top_deal_leads.map((lead, index) => (
              <div key={lead.user_id} className="flex items-center gap-4">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{lead.user_id}</p>
                  <p className="text-sm text-muted-foreground">
                    {lead.deal_count} deals • {formatCurrency(lead.total_value)} total value
                  </p>
                </div>
                <Badge variant="outline">{lead.deal_count}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Monthly Deal Flow */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Deal Flow</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analytics.monthly_deal_flow.map((month, index) => {
              const prevMonth = analytics.monthly_deal_flow[index - 1]
              const trend = prevMonth
                ? month.count > prevMonth.count
                  ? 'up'
                  : month.count < prevMonth.count
                  ? 'down'
                  : 'stable'
                : 'stable'

              return (
                <div key={month.month} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{month.month}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {month.count} deals
                    </span>
                    {trend === 'up' && (
                      <ArrowUp className="h-4 w-4 text-green-600" />
                    )}
                    {trend === 'down' && (
                      <ArrowDown className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average Deal Size
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(analytics.average_deal_size)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Deal Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.total_deals > 0
                ? ((analytics.active_deals / analytics.total_deals) * 100).toFixed(1)
                : 0}
              %
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Industries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(analytics.deals_by_industry).length}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default DealAnalytics
