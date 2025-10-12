/**
 * RTK Query API slice for Valuation and Financial Modeling operations
 * Handles DCF analysis, multiples valuation, scenario modeling, and sensitivity analysis
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type ValuationMethod =
  | 'dcf'
  | 'multiples'
  | 'precedent_transactions'
  | 'asset_based'
  | 'liquidation_value';

export type ScenarioType = 'base_case' | 'best_case' | 'worst_case' | 'custom';

export interface DCFAssumptions {
  projection_years: number;
  terminal_growth_rate: number;
  wacc: number;
  tax_rate: number;
  revenue_growth_rates: number[];
  ebitda_margins: number[];
  capex_percent: number;
  nwc_percent: number;
  depreciation_percent: number;
}

export interface DCFProjection {
  year: number;
  revenue: number;
  ebitda: number;
  ebit: number;
  tax: number;
  nopat: number;
  depreciation: number;
  capex: number;
  change_in_nwc: number;
  free_cash_flow: number;
  discount_factor: number;
  present_value: number;
}

export interface DCFValuation {
  id: string;
  deal_id?: string;
  opportunity_id?: string;
  target_company_name: string;

  // Assumptions
  assumptions: DCFAssumptions;

  // Results
  projections: DCFProjection[];
  terminal_value: number;
  terminal_value_pv: number;
  enterprise_value: number;
  net_debt: number;
  equity_value: number;
  shares_outstanding: number;
  value_per_share: number;

  // Sensitivity analysis results
  sensitivity_results?: Record<string, any>;

  // Metadata
  scenario_type: ScenarioType;
  version: number;
  is_latest: boolean;
  notes?: string;

  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface DCFValuationCreate {
  deal_id?: string;
  opportunity_id?: string;
  target_company_name: string;
  assumptions: DCFAssumptions;
  scenario_type?: ScenarioType;
  notes?: string;
}

export interface MultiplesComparable {
  company_name: string;
  revenue: number;
  ebitda: number;
  ev: number;
  ev_revenue_multiple: number;
  ev_ebitda_multiple: number;
  pe_ratio?: number;
  market_cap?: number;
  is_manual: boolean;
}

export interface MultiplesValuation {
  id: string;
  deal_id?: string;
  opportunity_id?: string;
  target_company_name: string;

  // Target metrics
  target_revenue: number;
  target_ebitda: number;
  target_net_income?: number;

  // Comparable companies
  comparables: MultiplesComparable[];

  // Results
  median_ev_revenue: number;
  median_ev_ebitda: number;
  median_pe?: number;

  implied_ev_from_revenue: number;
  implied_ev_from_ebitda: number;
  implied_ev_from_pe?: number;

  blended_enterprise_value: number;
  equity_value: number;

  // Adjustments
  liquidity_discount: number;
  control_premium: number;

  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface MultiplesValuationCreate {
  deal_id?: string;
  opportunity_id?: string;
  target_company_name: string;
  target_revenue: number;
  target_ebitda: number;
  target_net_income?: number;
  comparables: Omit<MultiplesComparable, 'ev_revenue_multiple' | 'ev_ebitda_multiple'>[];
  liquidity_discount?: number;
  control_premium?: number;
  notes?: string;
}

export interface SensitivityAnalysis {
  id: string;
  valuation_id: string;
  valuation_type: 'dcf' | 'multiples';

  variable_1: string;
  variable_1_range: number[];
  variable_2?: string;
  variable_2_range?: number[];

  results: {
    values: number[][];
    min_value: number;
    max_value: number;
    base_case_value: number;
  };

  created_at: string;
}

export interface SensitivityAnalysisRequest {
  valuation_id: string;
  valuation_type: 'dcf' | 'multiples';
  variable_1: string;
  variable_1_min: number;
  variable_1_max: number;
  variable_1_steps: number;
  variable_2?: string;
  variable_2_min?: number;
  variable_2_max?: number;
  variable_2_steps?: number;
}

export interface ScenarioComparison {
  deal_id: string;
  scenarios: {
    base_case: DCFValuation;
    best_case: DCFValuation;
    worst_case: DCFValuation;
  };
  probability_weighted_value: number;
  expected_value: number;
}

export interface ValuationSummary {
  deal_id?: string;
  opportunity_id?: string;
  target_company_name: string;

  dcf_valuations: DCFValuation[];
  multiples_valuations: MultiplesValuation[];

  recommended_valuation: {
    method: ValuationMethod;
    enterprise_value: number;
    equity_value: number;
    value_range_low: number;
    value_range_high: number;
  };

  last_updated: string;
}

export interface ComparableCompanySearchParams {
  industry?: string;
  revenue_min?: number;
  revenue_max?: number;
  country?: string;
  limit?: number;
}

export interface ComparableCompany {
  ticker: string;
  company_name: string;
  industry: string;
  country: string;
  revenue: number;
  ebitda: number;
  market_cap: number;
  enterprise_value: number;
  ev_revenue: number;
  ev_ebitda: number;
  pe_ratio: number;
  data_source: string;
}

export interface ValuationListResponse {
  data: (DCFValuation | MultiplesValuation)[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// ============================================================================
// API SLICE
// ============================================================================

export const valuationsApi = createApi({
  reducerPath: 'valuationsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/valuations',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['DCFValuation', 'MultiplesValuation', 'SensitivityAnalysis', 'ValuationList', 'Comparables'],
  endpoints: (builder) => ({
    // ========================================================================
    // DCF VALUATION ENDPOINTS
    // ========================================================================

    // Create DCF valuation
    createDCFValuation: builder.mutation<DCFValuation, DCFValuationCreate>({
      query: (data) => ({
        url: '/dcf',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['ValuationList'],
    }),

    // Get DCF valuation by ID
    getDCFValuation: builder.query<DCFValuation, string>({
      query: (id) => `/dcf/${id}`,
      providesTags: (result, error, id) => [{ type: 'DCFValuation', id }],
    }),

    // Update DCF valuation
    updateDCFValuation: builder.mutation<DCFValuation, { id: string; data: Partial<DCFValuationCreate> }>({
      query: ({ id, data }) => ({
        url: `/dcf/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'DCFValuation', id },
        'ValuationList',
      ],
    }),

    // Get all DCF valuations for a deal or opportunity
    getDCFValuations: builder.query<ValuationListResponse, { deal_id?: string; opportunity_id?: string }>({
      query: (params) => ({
        url: '/dcf',
        params,
      }),
      providesTags: ['ValuationList'],
    }),

    // Recalculate DCF valuation with new assumptions
    recalculateDCF: builder.mutation<DCFValuation, { id: string; assumptions: Partial<DCFAssumptions> }>({
      query: ({ id, assumptions }) => ({
        url: `/dcf/${id}/recalculate`,
        method: 'POST',
        body: { assumptions },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'DCFValuation', id },
        'ValuationList',
      ],
    }),

    // ========================================================================
    // MULTIPLES VALUATION ENDPOINTS
    // ========================================================================

    // Create multiples valuation
    createMultiplesValuation: builder.mutation<MultiplesValuation, MultiplesValuationCreate>({
      query: (data) => ({
        url: '/multiples',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['ValuationList'],
    }),

    // Get multiples valuation by ID
    getMultiplesValuation: builder.query<MultiplesValuation, string>({
      query: (id) => `/multiples/${id}`,
      providesTags: (result, error, id) => [{ type: 'MultiplesValuation', id }],
    }),

    // Update multiples valuation
    updateMultiplesValuation: builder.mutation<MultiplesValuation, { id: string; data: Partial<MultiplesValuationCreate> }>({
      query: ({ id, data }) => ({
        url: `/multiples/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'MultiplesValuation', id },
        'ValuationList',
      ],
    }),

    // Get all multiples valuations for a deal or opportunity
    getMultiplesValuations: builder.query<ValuationListResponse, { deal_id?: string; opportunity_id?: string }>({
      query: (params) => ({
        url: '/multiples',
        params,
      }),
      providesTags: ['ValuationList'],
    }),

    // ========================================================================
    // SENSITIVITY ANALYSIS ENDPOINTS
    // ========================================================================

    // Run sensitivity analysis
    runSensitivityAnalysis: builder.mutation<SensitivityAnalysis, SensitivityAnalysisRequest>({
      query: (data) => ({
        url: '/sensitivity',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { valuation_id }) => [
        { type: 'SensitivityAnalysis', id: valuation_id },
      ],
    }),

    // Get sensitivity analysis results
    getSensitivityAnalysis: builder.query<SensitivityAnalysis[], string>({
      query: (valuation_id) => `/sensitivity/${valuation_id}`,
      providesTags: (result, error, valuation_id) => [
        { type: 'SensitivityAnalysis', id: valuation_id },
      ],
    }),

    // ========================================================================
    // SCENARIO ANALYSIS ENDPOINTS
    // ========================================================================

    // Create scenario comparison
    createScenarioComparison: builder.mutation<ScenarioComparison, { deal_id: string }>({
      query: ({ deal_id }) => ({
        url: `/scenarios/${deal_id}`,
        method: 'POST',
      }),
      invalidatesTags: ['ValuationList'],
    }),

    // Get scenario comparison
    getScenarioComparison: builder.query<ScenarioComparison, string>({
      query: (deal_id) => `/scenarios/${deal_id}`,
      providesTags: (result, error, deal_id) => [{ type: 'DCFValuation', id: `scenario-${deal_id}` }],
    }),

    // ========================================================================
    // COMPARABLE COMPANIES ENDPOINTS
    // ========================================================================

    // Search comparable companies
    searchComparables: builder.query<ComparableCompany[], ComparableCompanySearchParams>({
      query: (params) => ({
        url: '/comparables/search',
        params,
      }),
      providesTags: ['Comparables'],
    }),

    // Get comparable company details
    getComparableDetails: builder.query<ComparableCompany, string>({
      query: (ticker) => `/comparables/${ticker}`,
      providesTags: (result, error, ticker) => [{ type: 'Comparables', id: ticker }],
    }),

    // ========================================================================
    // SUMMARY AND REPORTING ENDPOINTS
    // ========================================================================

    // Get valuation summary for deal/opportunity
    getValuationSummary: builder.query<ValuationSummary, { deal_id?: string; opportunity_id?: string }>({
      query: (params) => ({
        url: '/summary',
        params,
      }),
      providesTags: ['ValuationList'],
    }),

    // Export valuation to Excel
    exportValuation: builder.mutation<{ download_url: string }, { id: string; type: 'dcf' | 'multiples' }>({
      query: ({ id, type }) => ({
        url: `/export/${type}/${id}`,
        method: 'POST',
      }),
    }),

    // Delete valuation
    deleteValuation: builder.mutation<void, { id: string; type: 'dcf' | 'multiples' }>({
      query: ({ id, type }) => ({
        url: `/${type}/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['ValuationList'],
    }),
  }),
});

// ============================================================================
// EXPORT HOOKS
// ============================================================================

export const {
  // DCF hooks
  useCreateDCFValuationMutation,
  useGetDCFValuationQuery,
  useUpdateDCFValuationMutation,
  useGetDCFValuationsQuery,
  useRecalculateDCFMutation,

  // Multiples hooks
  useCreateMultiplesValuationMutation,
  useGetMultiplesValuationQuery,
  useUpdateMultiplesValuationMutation,
  useGetMultiplesValuationsQuery,

  // Sensitivity analysis hooks
  useRunSensitivityAnalysisMutation,
  useGetSensitivityAnalysisQuery,

  // Scenario analysis hooks
  useCreateScenarioComparisonMutation,
  useGetScenarioComparisonQuery,

  // Comparables hooks
  useSearchComparablesQuery,
  useGetComparableDetailsQuery,

  // Summary hooks
  useGetValuationSummaryQuery,
  useExportValuationMutation,
  useDeleteValuationMutation,
} = valuationsApi;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const formatCurrency = (value: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatMultiple = (value: number): string => {
  return `${value.toFixed(1)}x`;
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const calculateCAGR = (beginValue: number, endValue: number, years: number): number => {
  return Math.pow(endValue / beginValue, 1 / years) - 1;
};

export const calculateWACC = (
  costOfEquity: number,
  costOfDebt: number,
  equityWeight: number,
  debtWeight: number,
  taxRate: number
): number => {
  return (equityWeight * costOfEquity) + (debtWeight * costOfDebt * (1 - taxRate));
};

export const getValuationMethodLabel = (method: ValuationMethod): string => {
  const labels: Record<ValuationMethod, string> = {
    dcf: 'Discounted Cash Flow',
    multiples: 'Comparable Companies',
    precedent_transactions: 'Precedent Transactions',
    asset_based: 'Asset-Based Valuation',
    liquidation_value: 'Liquidation Value',
  };
  return labels[method];
};

export const getScenarioTypeLabel = (scenario: ScenarioType): string => {
  const labels: Record<ScenarioType, string> = {
    base_case: 'Base Case',
    best_case: 'Best Case',
    worst_case: 'Worst Case',
    custom: 'Custom Scenario',
  };
  return labels[scenario];
};

export const getScenarioColor = (scenario: ScenarioType): string => {
  const colors: Record<ScenarioType, string> = {
    base_case: '#2196f3',
    best_case: '#4caf50',
    worst_case: '#f44336',
    custom: '#ff9800',
  };
  return colors[scenario];
};
