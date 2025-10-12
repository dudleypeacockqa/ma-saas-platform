/**
 * RTK Query API slice for Opportunity Management
 * M&A opportunity discovery, scoring, and pipeline management
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// Types matching backend schemas
export type OpportunityStatus =
  | 'NEW'
  | 'REVIEWING'
  | 'QUALIFIED'
  | 'IN_DISCUSSION'
  | 'DISQUALIFIED'
  | 'CONVERTED_TO_DEAL'
  | 'ON_HOLD';

export type CompanyRegion = 'UK' | 'US' | 'EU' | 'ASIA' | 'OTHER';

export type IndustryVertical =
  | 'TECHNOLOGY'
  | 'HEALTHCARE'
  | 'FINANCE'
  | 'RETAIL'
  | 'MANUFACTURING'
  | 'SERVICES'
  | 'REAL_ESTATE'
  | 'ENERGY'
  | 'TELECOM'
  | 'OTHER';

export type ActivityType =
  | 'CREATED'
  | 'STATUS_CHANGED'
  | 'SCORED'
  | 'NOTE_ADDED'
  | 'CONTACT_MADE'
  | 'MEETING_SCHEDULED'
  | 'DOCUMENT_UPLOADED'
  | 'CONVERTED_TO_DEAL';

export type FinancialHealth = 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'CRITICAL';

export interface Opportunity {
  id: string;
  organization_id: string;
  company_name: string;
  region: CompanyRegion;
  industry_vertical: IndustryVertical;
  status: OpportunityStatus;
  overall_score?: number;
  financial_health_score?: number;
  strategic_fit_score?: number;
  annual_revenue?: number;
  ebitda?: number;
  employee_count?: number;
  source_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface OpportunityCreate {
  company_name: string;
  region: CompanyRegion;
  industry_vertical: IndustryVertical;
  company_registration_number?: string;
  website?: string;
  annual_revenue?: number;
  ebitda?: number;
  employee_count?: number;
  source_url?: string;
  metadata?: Record<string, any>;
}

export interface OpportunityUpdate {
  status?: OpportunityStatus;
  notes?: string;
  annual_revenue?: number;
  ebitda?: number;
  employee_count?: number;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface OpportunityFilters {
  status?: OpportunityStatus[];
  region?: CompanyRegion;
  industry_vertical?: IndustryVertical[];
  min_score?: number;
  max_score?: number;
  min_revenue?: number;
  max_revenue?: number;
  search?: string;
  sort_by?: 'created_at' | 'overall_score' | 'annual_revenue' | 'company_name';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface OpportunityScore {
  id: string;
  opportunity_id: string;
  overall_score: number;
  financial_health_score: number;
  growth_trajectory_score: number;
  strategic_fit_score: number;
  market_position_score: number;
  risk_assessment_score: number;
  ai_insights: Record<string, any>;
  confidence_level: number;
  scored_at: string;
}

export interface OpportunityActivity {
  id: string;
  opportunity_id: string;
  user_id: string;
  activity_type: ActivityType;
  description: string;
  metadata?: Record<string, any>;
  occurred_at: string;
}

export interface ScanRequest {
  region: CompanyRegion;
  industry_sic?: string;
  industry_vertical?: IndustryVertical;
  min_age_years?: number;
  cik_list?: string[];
}

export interface ScoreRequest {
  company_data: Record<string, any>;
}

export interface ConvertToDealRequest {
  deal_data?: Record<string, any>;
}

export interface ROIProjectionRequest {
  purchase_price: number;
  annual_revenue: number;
  ebitda: number;
  growth_rate?: number;
  exit_multiple?: number;
  hold_period_years?: number;
}

export interface ROIProjection {
  roi_percentage: number;
  irr: number;
  payback_period_years: number;
  total_return: number;
  exit_value: number;
}

export interface PipelineMetrics {
  total_opportunities: number;
  status_breakdown: Record<string, number>;
  average_score: number;
  qualified_count: number;
  conversion_rate: number;
  new_this_week: number;
}

export interface EnhancedScreeningRequest {
  revenue_min?: number;
  revenue_max?: number;
  industries?: IndustryVertical[];
  countries?: string[];
  employee_min?: number;
  employee_max?: number;
  growth_rate_min?: number;
  ebitda_margin_min?: number;
  financial_health?: FinancialHealth[];
}

// Create the API slice
export const opportunitiesApi = createApi({
  reducerPath: 'opportunitiesApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/opportunities',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Opportunity', 'OpportunityList', 'OpportunityScore', 'PipelineMetrics'],
  endpoints: (builder) => ({
    // CRUD Operations
    createOpportunity: builder.mutation<Opportunity, OpportunityCreate>({
      query: (opportunity) => ({
        url: '/',
        method: 'POST',
        body: opportunity,
      }),
      invalidatesTags: ['OpportunityList', 'PipelineMetrics'],
    }),

    getOpportunities: builder.query<Opportunity[], OpportunityFilters | void>({
      query: (filters = {}) => ({
        url: '/',
        params: filters,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Opportunity' as const, id })),
              { type: 'OpportunityList', id: 'LIST' },
            ]
          : [{ type: 'OpportunityList', id: 'LIST' }],
    }),

    getOpportunity: builder.query<Opportunity, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Opportunity', id }],
    }),

    updateOpportunity: builder.mutation<Opportunity, { id: string; data: OpportunityUpdate }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id },
        { type: 'OpportunityList', id: 'LIST' },
        'PipelineMetrics',
      ],
    }),

    deleteOpportunity: builder.mutation<void, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['OpportunityList', 'PipelineMetrics'],
    }),

    // Discovery & Scanning
    scanCompaniesHouse: builder.mutation<Opportunity[], ScanRequest>({
      query: (scanRequest) => ({
        url: '/scan/companies-house',
        method: 'POST',
        body: scanRequest,
      }),
      invalidatesTags: ['OpportunityList', 'PipelineMetrics'],
    }),

    scanSecEdgar: builder.mutation<Opportunity[], ScanRequest>({
      query: (scanRequest) => ({
        url: '/scan/sec-edgar',
        method: 'POST',
        body: scanRequest,
      }),
      invalidatesTags: ['OpportunityList', 'PipelineMetrics'],
    }),

    scanDistressed: builder.mutation<Opportunity[], { region: CompanyRegion; industry: IndustryVertical }>({
      query: ({ region, industry }) => ({
        url: '/scan/distressed',
        method: 'POST',
        params: { region, industry },
      }),
      invalidatesTags: ['OpportunityList', 'PipelineMetrics'],
    }),

    // Scoring & Analysis
    scoreOpportunity: builder.mutation<OpportunityScore, { id: string; data: ScoreRequest }>({
      query: ({ id, data }) => ({
        url: `/${id}/score`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id },
        { type: 'OpportunityScore', id },
      ],
    }),

    getOpportunityScore: builder.query<OpportunityScore, string>({
      query: (id) => `/${id}/score`,
      providesTags: (result, error, id) => [{ type: 'OpportunityScore', id }],
    }),

    calculateROI: builder.mutation<ROIProjection, ROIProjectionRequest>({
      query: (request) => ({
        url: '/roi-projection',
        method: 'POST',
        body: request,
      }),
    }),

    // Pipeline Management
    convertToDeal: builder.mutation<{ opportunity_id: string; deal_id: string; message: string }, { id: string; data?: ConvertToDealRequest }>({
      query: ({ id, data }) => ({
        url: `/${id}/convert-to-deal`,
        method: 'POST',
        body: data || {},
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id },
        { type: 'OpportunityList', id: 'LIST' },
        'PipelineMetrics',
      ],
    }),

    getOpportunityTimeline: builder.query<OpportunityActivity[], string>({
      query: (id) => `/${id}/timeline`,
      providesTags: (result, error, id) => [{ type: 'Opportunity', id }],
    }),

    // Enhanced Screening
    enhancedScreening: builder.mutation<Opportunity[], EnhancedScreeningRequest>({
      query: (filters) => ({
        url: '/screen/enhanced',
        method: 'POST',
        body: filters,
      }),
    }),

    identifyDistressed: builder.mutation<Opportunity[], { min_current_ratio?: number; max_debt_to_equity?: number; min_ebitda_margin?: number; negative_growth?: boolean }>({
      query: (filters) => ({
        url: '/screen/distressed',
        method: 'POST',
        body: filters,
      }),
    }),

    findSuccessionOpportunities: builder.query<Opportunity[], { min_years_in_business?: number; owner_age_threshold?: number }>({
      query: (params) => ({
        url: '/screen/succession',
        params,
      }),
    }),

    rankOpportunities: builder.query<Array<{ opportunity: Opportunity; scores: Record<string, any>; overall_score: number }>, { filters?: Record<string, any>; limit?: number }>({
      query: (params) => ({
        url: '/rank',
        params,
      }),
    }),

    // Pipeline Metrics
    getPipelineMetrics: builder.query<PipelineMetrics, void>({
      query: () => '/metrics/pipeline',
      providesTags: ['PipelineMetrics'],
    }),
  }),
});

// Export hooks
export const {
  useCreateOpportunityMutation,
  useGetOpportunitiesQuery,
  useGetOpportunityQuery,
  useUpdateOpportunityMutation,
  useDeleteOpportunityMutation,
  useScanCompaniesHouseMutation,
  useScanSecEdgarMutation,
  useScanDistressedMutation,
  useScoreOpportunityMutation,
  useGetOpportunityScoreQuery,
  useCalculateROIMutation,
  useConvertToDealMutation,
  useGetOpportunityTimelineQuery,
  useEnhancedScreeningMutation,
  useIdentifyDistressedMutation,
  useFindSuccessionOpportunitiesQuery,
  useRankOpportunitiesQuery,
  useGetPipelineMetricsQuery,
} = opportunitiesApi;

// Utility functions
export const getOpportunityStatusColor = (status: OpportunityStatus): string => {
  const colors: Record<OpportunityStatus, string> = {
    NEW: '#2196f3',
    REVIEWING: '#ff9800',
    QUALIFIED: '#4caf50',
    IN_DISCUSSION: '#9c27b0',
    DISQUALIFIED: '#f44336',
    CONVERTED_TO_DEAL: '#00bcd4',
    ON_HOLD: '#607d8b',
  };
  return colors[status];
};

export const getOpportunityStatusLabel = (status: OpportunityStatus): string => {
  const labels: Record<OpportunityStatus, string> = {
    NEW: 'New',
    REVIEWING: 'Under Review',
    QUALIFIED: 'Qualified',
    IN_DISCUSSION: 'In Discussion',
    DISQUALIFIED: 'Disqualified',
    CONVERTED_TO_DEAL: 'Converted to Deal',
    ON_HOLD: 'On Hold',
  };
  return labels[status];
};

export const formatScore = (score?: number): string => {
  if (score === undefined || score === null) return 'N/A';
  return `${score.toFixed(1)}/100`;
};

export const formatRevenue = (revenue?: number): string => {
  if (!revenue) return 'N/A';
  if (revenue >= 1000000) {
    return `$${(revenue / 1000000).toFixed(1)}M`;
  }
  if (revenue >= 1000) {
    return `$${(revenue / 1000).toFixed(1)}K`;
  }
  return `$${revenue.toFixed(0)}`;
};
