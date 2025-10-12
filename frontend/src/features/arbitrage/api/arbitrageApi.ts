/**
 * RTK Query API slice for Arbitrage Analysis
 * Handles M&A arbitrage opportunity scanning, risk analysis, and position tracking
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type ArbitrageType = 'merger_arbitrage' | 'cash_deal' | 'stock_deal' | 'mixed_deal';
export type DealStatus = 'announced' | 'regulatory_review' | 'shareholder_vote' | 'closing' | 'completed' | 'terminated';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ArbitrageOpportunity {
  id: string;
  organization_id: string;

  // Deal Information
  deal_id?: string;
  acquirer_name: string;
  acquirer_ticker?: string;
  target_name: string;
  target_ticker: string;

  arbitrage_type: ArbitrageType;
  deal_status: DealStatus;
  deal_announcement_date: string;
  expected_close_date?: string;
  actual_close_date?: string;

  // Financial Metrics
  current_price: number;
  offer_price: number;
  spread: number;
  spread_percentage: number;
  annualized_return: number;

  // Deal Terms
  deal_value: number;
  deal_currency: string;
  cash_component?: number;
  stock_component?: number;
  exchange_ratio?: number;

  // Risk Assessment
  risk_level: RiskLevel;
  completion_probability: number;
  regulatory_risk_score: number;
  financing_risk_score: number;
  shareholder_risk_score: number;

  // Market Data
  target_market_cap: number;
  target_volume_30d: number;
  implied_volatility?: number;

  // Position Tracking
  position_size?: number;
  entry_price?: number;
  unrealized_pnl?: number;
  realized_pnl?: number;

  // Alerts
  has_active_alerts: boolean;
  last_alert_date?: string;

  // Metadata
  tags: string[];
  notes?: string;
  is_active: boolean;
  is_monitored: boolean;

  created_at: string;
  updated_at: string;
  last_price_update?: string;
}

export interface ArbitrageOpportunityCreate {
  acquirer_name: string;
  acquirer_ticker?: string;
  target_name: string;
  target_ticker: string;

  arbitrage_type: ArbitrageType;
  deal_status: DealStatus;
  deal_announcement_date: string;
  expected_close_date?: string;

  offer_price: number;
  deal_value: number;
  deal_currency?: string;
  cash_component?: number;
  stock_component?: number;
  exchange_ratio?: number;

  completion_probability?: number;
  tags?: string[];
  notes?: string;
}

export interface ArbitrageOpportunityUpdate extends Partial<ArbitrageOpportunityCreate> {
  current_price?: number;
  deal_status?: DealStatus;
  is_active?: boolean;
  is_monitored?: boolean;
}

export interface ArbitragePosition {
  id: string;
  opportunity_id: string;
  organization_id: string;

  // Position Details
  shares: number;
  entry_price: number;
  entry_date: string;

  exit_price?: number;
  exit_date?: string;

  // P&L
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percentage: number;
  realized_pnl?: number;
  realized_pnl_percentage?: number;

  // Risk Management
  stop_loss?: number;
  take_profit?: number;
  max_loss_allowed: number;

  // Status
  status: 'open' | 'closed' | 'partially_closed';
  is_active: boolean;

  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ArbitragePositionCreate {
  opportunity_id: string;
  shares: number;
  entry_price: number;
  entry_date?: string;
  stop_loss?: number;
  take_profit?: number;
  max_loss_allowed?: number;
  notes?: string;
}

export interface ArbitragePositionUpdate {
  shares?: number;
  stop_loss?: number;
  take_profit?: number;
  notes?: string;
}

export interface ArbitrageAlert {
  id: string;
  opportunity_id: string;
  organization_id: string;

  alert_type: 'spread_change' | 'status_change' | 'risk_change' | 'price_target' | 'news_event';
  severity: 'info' | 'warning' | 'critical';

  message: string;
  details?: Record<string, any>;

  is_read: boolean;
  is_dismissed: boolean;

  triggered_at: string;
  read_at?: string;
  dismissed_at?: string;
}

export interface ArbitrageRiskAnalysis {
  opportunity_id: string;

  // Overall Risk
  overall_risk_score: number;
  overall_risk_level: RiskLevel;
  completion_probability: number;

  // Component Risks
  regulatory_risk: {
    score: number;
    level: RiskLevel;
    factors: string[];
    jurisdictions: string[];
  };

  financing_risk: {
    score: number;
    level: RiskLevel;
    factors: string[];
    acquirer_credit_rating?: string;
  };

  shareholder_risk: {
    score: number;
    level: RiskLevel;
    factors: string[];
    voting_threshold?: number;
  };

  market_risk: {
    score: number;
    level: RiskLevel;
    factors: string[];
    beta?: number;
  };

  // Historical Context
  similar_deals_success_rate?: number;
  industry_average_completion_rate?: number;

  // Recommendations
  recommendations: string[];
  risk_mitigation_strategies: string[];

  calculated_at: string;
}

export interface ArbitrageScanner {
  scan_date: string;
  total_opportunities_found: number;
  opportunities: ArbitrageOpportunity[];

  filters_applied: {
    min_spread?: number;
    max_risk_level?: RiskLevel;
    min_probability?: number;
    arbitrage_types?: ArbitrageType[];
  };

  statistics: {
    average_spread: number;
    median_spread: number;
    average_annualized_return: number;
    total_deal_value: number;
  };
}

export interface ArbitrageScanRequest {
  min_spread?: number;
  max_spread?: number;
  min_annualized_return?: number;
  max_risk_level?: RiskLevel;
  min_completion_probability?: number;
  arbitrage_types?: ArbitrageType[];
  deal_statuses?: DealStatus[];
  include_monitored_only?: boolean;
}

export interface ArbitragePortfolio {
  organization_id: string;

  // Positions Summary
  total_positions: number;
  open_positions: number;
  closed_positions: number;

  // Financial Summary
  total_invested: number;
  current_value: number;
  total_unrealized_pnl: number;
  total_realized_pnl: number;
  total_pnl: number;
  return_percentage: number;

  // Risk Metrics
  portfolio_var_95?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;

  // Position Breakdown
  positions_by_type: Record<ArbitrageType, number>;
  positions_by_risk: Record<RiskLevel, number>;

  // Top Performers
  top_performers: ArbitragePosition[];
  worst_performers: ArbitragePosition[];

  last_updated: string;
}

export interface ArbitrageMarketData {
  ticker: string;
  price: number;
  change: number;
  change_percentage: number;
  volume: number;
  bid: number;
  ask: number;
  high_52w: number;
  low_52w: number;
  market_cap: number;
  updated_at: string;
}

export interface ArbitrageListResponse {
  data: ArbitrageOpportunity[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface ArbitrageFilters {
  arbitrage_type?: ArbitrageType[];
  deal_status?: DealStatus[];
  risk_level?: RiskLevel[];
  min_spread?: number;
  max_spread?: number;
  min_annualized_return?: number;
  min_probability?: number;
  is_monitored?: boolean;
  is_active?: boolean;
  search?: string;
  tags?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

// ============================================================================
// API SLICE
// ============================================================================

export const arbitrageApi = createApi({
  reducerPath: 'arbitrageApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/arbitrage',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Opportunity', 'OpportunityList', 'Position', 'Alert', 'Portfolio', 'RiskAnalysis'],
  endpoints: (builder) => ({
    // ========================================================================
    // OPPORTUNITY MANAGEMENT
    // ========================================================================

    // Create arbitrage opportunity
    createOpportunity: builder.mutation<ArbitrageOpportunity, ArbitrageOpportunityCreate>({
      query: (data) => ({
        url: '/opportunities',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['OpportunityList', 'Portfolio'],
    }),

    // Get opportunities list
    getOpportunities: builder.query<ArbitrageListResponse, ArbitrageFilters | void>({
      query: (filters = {}) => ({
        url: '/opportunities',
        params: filters,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Opportunity' as const, id })),
              { type: 'OpportunityList', id: 'LIST' },
            ]
          : [{ type: 'OpportunityList', id: 'LIST' }],
    }),

    // Get single opportunity
    getOpportunity: builder.query<ArbitrageOpportunity, string>({
      query: (id) => `/opportunities/${id}`,
      providesTags: (result, error, id) => [{ type: 'Opportunity', id }],
    }),

    // Update opportunity
    updateOpportunity: builder.mutation<ArbitrageOpportunity, { id: string; data: ArbitrageOpportunityUpdate }>({
      query: ({ id, data }) => ({
        url: `/opportunities/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id },
        { type: 'OpportunityList', id: 'LIST' },
        'Portfolio',
      ],
    }),

    // Delete opportunity
    deleteOpportunity: builder.mutation<void, string>({
      query: (id) => ({
        url: `/opportunities/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['OpportunityList', 'Portfolio'],
    }),

    // Refresh opportunity prices
    refreshPrices: builder.mutation<ArbitrageOpportunity, string>({
      query: (id) => ({
        url: `/opportunities/${id}/refresh`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Opportunity', id },
        'Portfolio',
      ],
    }),

    // ========================================================================
    // SCANNER
    // ========================================================================

    // Scan for arbitrage opportunities
    scanOpportunities: builder.mutation<ArbitrageScanner, ArbitrageScanRequest>({
      query: (params) => ({
        url: '/scan',
        method: 'POST',
        body: params,
      }),
      invalidatesTags: ['OpportunityList'],
    }),

    // ========================================================================
    // POSITION MANAGEMENT
    // ========================================================================

    // Create position
    createPosition: builder.mutation<ArbitragePosition, ArbitragePositionCreate>({
      query: (data) => ({
        url: '/positions',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Position', 'Portfolio'],
    }),

    // Get all positions
    getPositions: builder.query<ArbitragePosition[], { opportunity_id?: string; status?: string }>({
      query: (params) => ({
        url: '/positions',
        params,
      }),
      providesTags: ['Position'],
    }),

    // Get single position
    getPosition: builder.query<ArbitragePosition, string>({
      query: (id) => `/positions/${id}`,
      providesTags: (result, error, id) => [{ type: 'Position', id }],
    }),

    // Update position
    updatePosition: builder.mutation<ArbitragePosition, { id: string; data: ArbitragePositionUpdate }>({
      query: ({ id, data }) => ({
        url: `/positions/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Position', id },
        'Portfolio',
      ],
    }),

    // Close position
    closePosition: builder.mutation<ArbitragePosition, { id: string; exit_price: number; exit_date?: string }>({
      query: ({ id, exit_price, exit_date }) => ({
        url: `/positions/${id}/close`,
        method: 'POST',
        body: { exit_price, exit_date },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Position', id },
        'Portfolio',
      ],
    }),

    // ========================================================================
    // RISK ANALYSIS
    // ========================================================================

    // Get risk analysis
    getRiskAnalysis: builder.query<ArbitrageRiskAnalysis, string>({
      query: (opportunity_id) => `/risk-analysis/${opportunity_id}`,
      providesTags: (result, error, opportunity_id) => [
        { type: 'RiskAnalysis', id: opportunity_id },
      ],
    }),

    // Recalculate risk
    recalculateRisk: builder.mutation<ArbitrageRiskAnalysis, string>({
      query: (opportunity_id) => ({
        url: `/risk-analysis/${opportunity_id}/recalculate`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, opportunity_id) => [
        { type: 'RiskAnalysis', id: opportunity_id },
        { type: 'Opportunity', id: opportunity_id },
      ],
    }),

    // ========================================================================
    // ALERTS
    // ========================================================================

    // Get alerts
    getAlerts: builder.query<ArbitrageAlert[], { opportunity_id?: string; is_read?: boolean }>({
      query: (params) => ({
        url: '/alerts',
        params,
      }),
      providesTags: ['Alert'],
    }),

    // Mark alert as read
    markAlertRead: builder.mutation<ArbitrageAlert, string>({
      query: (id) => ({
        url: `/alerts/${id}/read`,
        method: 'POST',
      }),
      invalidatesTags: ['Alert'],
    }),

    // Dismiss alert
    dismissAlert: builder.mutation<void, string>({
      query: (id) => ({
        url: `/alerts/${id}/dismiss`,
        method: 'POST',
      }),
      invalidatesTags: ['Alert'],
    }),

    // ========================================================================
    // PORTFOLIO
    // ========================================================================

    // Get portfolio summary
    getPortfolio: builder.query<ArbitragePortfolio, void>({
      query: () => '/portfolio',
      providesTags: ['Portfolio'],
    }),

    // ========================================================================
    // MARKET DATA
    // ========================================================================

    // Get market data for ticker
    getMarketData: builder.query<ArbitrageMarketData, string>({
      query: (ticker) => `/market-data/${ticker}`,
    }),

    // Bulk refresh market data
    bulkRefreshPrices: builder.mutation<{ updated_count: number }, string[]>({
      query: (opportunity_ids) => ({
        url: '/bulk-refresh',
        method: 'POST',
        body: { opportunity_ids },
      }),
      invalidatesTags: ['OpportunityList', 'Portfolio'],
    }),
  }),
});

// ============================================================================
// EXPORT HOOKS
// ============================================================================

export const {
  // Opportunity hooks
  useCreateOpportunityMutation,
  useGetOpportunitiesQuery,
  useGetOpportunityQuery,
  useUpdateOpportunityMutation,
  useDeleteOpportunityMutation,
  useRefreshPricesMutation,

  // Scanner hooks
  useScanOpportunitiesMutation,

  // Position hooks
  useCreatePositionMutation,
  useGetPositionsQuery,
  useGetPositionQuery,
  useUpdatePositionMutation,
  useClosePositionMutation,

  // Risk analysis hooks
  useGetRiskAnalysisQuery,
  useRecalculateRiskMutation,

  // Alert hooks
  useGetAlertsQuery,
  useMarkAlertReadMutation,
  useDismissAlertMutation,

  // Portfolio hooks
  useGetPortfolioQuery,

  // Market data hooks
  useGetMarketDataQuery,
  useBulkRefreshPricesMutation,
} = arbitrageApi;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const formatSpread = (spread: number): string => {
  return `${spread.toFixed(2)}%`;
};

export const formatReturn = (annualizedReturn: number): string => {
  return `${annualizedReturn.toFixed(1)}%`;
};

export const getRiskLevelColor = (level: RiskLevel): string => {
  const colors: Record<RiskLevel, string> = {
    low: '#4caf50',
    medium: '#ff9800',
    high: '#f44336',
    critical: '#9c27b0',
  };
  return colors[level];
};

export const getDealStatusLabel = (status: DealStatus): string => {
  const labels: Record<DealStatus, string> = {
    announced: 'Announced',
    regulatory_review: 'Regulatory Review',
    shareholder_vote: 'Shareholder Vote',
    closing: 'Closing',
    completed: 'Completed',
    terminated: 'Terminated',
  };
  return labels[status];
};

export const getArbitrageTypeLabel = (type: ArbitrageType): string => {
  const labels: Record<ArbitrageType, string> = {
    merger_arbitrage: 'Merger Arbitrage',
    cash_deal: 'Cash Deal',
    stock_deal: 'Stock Deal',
    mixed_deal: 'Mixed Deal',
  };
  return labels[type];
};

export const calculateDaysToClose = (expectedCloseDate: string): number => {
  const now = new Date();
  const closeDate = new Date(expectedCloseDate);
  const diffTime = closeDate.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const calculateImpliedProbability = (currentPrice: number, offerPrice: number, riskFreeRate: number = 0.02): number => {
  const spread = (offerPrice - currentPrice) / currentPrice;
  return 1 - (spread / (1 + riskFreeRate));
};
