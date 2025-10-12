/**
 * AI Intelligence API Client
 * Sprint 23: AI-powered deal intelligence and pipeline predictions
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// Types for AI Intelligence
export interface DealAnalysisRequest {
  deal_id: string;
  deal_data: Record<string, any>;
  include_market_analysis?: boolean;
  include_competitive_analysis?: boolean;
}

export interface DealAnalysisResponse {
  deal_id: string;
  overall_score: number;
  financial_score: number;
  strategic_score: number;
  risk_score: number;
  market_score: number;
  team_score: number;
  recommendation: string;
  risk_level: string;
  market_insights: Record<string, any>;
  next_actions: string[];
  confidence: number;
  analysis_timestamp: string;
}

export interface DealScore {
  deal_id: string;
  score: number;
  confidence: number;
  last_updated: string;
}

export interface PipelineAnalysisRequest {
  include_historical_data?: boolean;
  date_range_days?: number;
  include_forecasting?: boolean;
}

export interface PipelineAnalysisResponse {
  velocity_metrics: {
    average_days_per_stage: Record<string, number>;
    total_pipeline_duration: number;
    velocity_trend: string;
    efficiency_score: number;
    bottleneck_stages: string[];
  };
  bottlenecks: Array<{
    stage: string;
    deals_affected: number;
    average_delay_days: number;
    impact_on_revenue: number;
    suggested_actions: string[];
    urgency_level: string;
  }>;
  revenue_forecast: {
    monthly_forecast: Array<{
      month: number;
      expected_revenue: number;
      best_case: number;
      worst_case: number;
    }>;
    quarterly_forecast: Array<{
      quarter: number;
      expected_revenue: number;
      deals_expected: number;
    }>;
    annual_forecast: {
      expected_revenue: number;
      pipeline_value: number;
      conversion_rate: number;
    };
    confidence_intervals: Record<string, [number, number]>;
    key_assumptions: string[];
  };
  optimization_opportunities: string[];
  prediction_timestamp: string;
}

export interface PipelineVelocity {
  average_cycle_time: number;
  velocity_trend: string;
  efficiency_score: number;
  bottleneck_count: number;
  stage_performance: Record<string, number>;
}

export interface AIInsightRequest {
  context: string;
  data: Record<string, any>;
  insight_type?: string;
}

export interface AIInsightResponse {
  insights: Array<{
    type: string;
    description: string;
    impact: string;
  }>;
  recommendations: string[];
  confidence: number;
  processing_time_ms: number;
}

export interface AIModelStatus {
  available_models: Array<{
    model_id: string;
    name: string;
    version: string;
    type: string;
    capabilities: string[];
  }>;
  processing_stats: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_processing_time_ms: number;
    success_rate: number;
    active_models: number;
  };
  health_check: {
    status: string;
    active_processors: number;
    timestamp: string;
  };
  capabilities: Record<string, string[]>;
}

export interface DocumentAnalysisResponse {
  analysis: Record<string, any>;
  confidence: number;
  processing_time_ms: number;
  extracted_data: Record<string, any>;
  summary: string;
  key_metrics: Record<string, any>;
  risk_factors: string[];
}

export interface DealRecommendations {
  deal_id: string;
  recommendations: string[];
  priority_actions: string[];
  risk_mitigations: string[];
  optimization_suggestions: string[];
  confidence: number;
  last_updated: string;
}

// Create the AI API slice
export const aiApi = createApi({
  reducerPath: 'aiApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/ai',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['DealAnalysis', 'PipelineAnalysis', 'AIInsights', 'AIModels', 'DealRecommendations'],
  endpoints: (builder) => ({
    // Deal Intelligence Endpoints
    analyzeDeal: builder.mutation<DealAnalysisResponse, DealAnalysisRequest>({
      query: ({ deal_id, ...body }) => ({
        url: `/deals/${deal_id}/analyze`,
        method: 'POST',
        body,
      }),
      invalidatesTags: ['DealAnalysis'],
    }),

    getDealScore: builder.query<DealScore, string>({
      query: (dealId) => `/deals/${dealId}/score`,
      providesTags: ['DealAnalysis'],
    }),

    // Pipeline Intelligence Endpoints
    analyzePipeline: builder.mutation<PipelineAnalysisResponse, PipelineAnalysisRequest>({
      query: (body) => ({
        url: '/pipeline/analyze',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['PipelineAnalysis'],
    }),

    getPipelineVelocity: builder.query<PipelineVelocity, { daysBack?: number }>({
      query: ({ daysBack = 30 } = {}) => ({
        url: '/pipeline/velocity',
        params: { days_back: daysBack },
      }),
      providesTags: ['PipelineAnalysis'],
    }),

    // AI Insights Endpoints
    generateInsights: builder.mutation<AIInsightResponse, AIInsightRequest>({
      query: (body) => ({
        url: '/insights/generate',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['AIInsights'],
    }),

    // AI Models and Status
    getAIModelsStatus: builder.query<AIModelStatus, void>({
      query: () => '/models/status',
      providesTags: ['AIModels'],
    }),

    // Document Analysis
    analyzeDocument: builder.mutation<DocumentAnalysisResponse, {
      document_content: string;
      document_type?: string;
    }>({
      query: (body) => ({
        url: '/documents/analyze',
        method: 'POST',
        body,
      }),
    }),

    // Deal Recommendations
    getDealRecommendations: builder.query<DealRecommendations, string>({
      query: (dealId) => `/recommendations/${dealId}`,
      providesTags: ['DealRecommendations'],
    }),
  }),
});

// Export hooks for use in components
export const {
  useAnalyzeDealMutation,
  useGetDealScoreQuery,
  useAnalyzePipelineMutation,
  useGetPipelineVelocityQuery,
  useGenerateInsightsMutation,
  useGetAIModelsStatusQuery,
  useAnalyzeDocumentMutation,
  useGetDealRecommendationsQuery,
} = aiApi;

// Utility functions for AI operations
export const aiOperations = {
  /**
   * Quick deal scoring for dashboard display
   */
  async quickDealScore(dealId: string, dispatch: any): Promise<DealScore | null> {
    try {
      const result = await dispatch(aiApi.endpoints.getDealScore.initiate(dealId));
      return result.data || null;
    } catch (error) {
      console.error('Quick deal score failed:', error);
      return null;
    }
  },

  /**
   * Comprehensive deal analysis
   */
  async comprehensiveDealAnalysis(
    dealId: string,
    dealData: Record<string, any>,
    dispatch: any,
    options: {
      includeMarketAnalysis?: boolean;
      includeCompetitiveAnalysis?: boolean;
    } = {}
  ): Promise<DealAnalysisResponse | null> {
    try {
      const result = await dispatch(
        aiApi.endpoints.analyzeDeal.initiate({
          deal_id: dealId,
          deal_data: dealData,
          include_market_analysis: options.includeMarketAnalysis ?? true,
          include_competitive_analysis: options.includeCompetitiveAnalysis ?? true,
        })
      );
      return result.data || null;
    } catch (error) {
      console.error('Comprehensive deal analysis failed:', error);
      return null;
    }
  },

  /**
   * Pipeline velocity analysis for dashboard
   */
  async pipelineVelocityAnalysis(
    dispatch: any,
    daysBack: number = 30
  ): Promise<PipelineVelocity | null> {
    try {
      const result = await dispatch(
        aiApi.endpoints.getPipelineVelocity.initiate({ daysBack })
      );
      return result.data || null;
    } catch (error) {
      console.error('Pipeline velocity analysis failed:', error);
      return null;
    }
  },

  /**
   * Full pipeline intelligence analysis
   */
  async fullPipelineAnalysis(
    dispatch: any,
    options: {
      includeHistoricalData?: boolean;
      dateRangeDays?: number;
      includeForecasting?: boolean;
    } = {}
  ): Promise<PipelineAnalysisResponse | null> {
    try {
      const result = await dispatch(
        aiApi.endpoints.analyzePipeline.initiate({
          include_historical_data: options.includeHistoricalData ?? true,
          date_range_days: options.dateRangeDays ?? 90,
          include_forecasting: options.includeForecasting ?? true,
        })
      );
      return result.data || null;
    } catch (error) {
      console.error('Full pipeline analysis failed:', error);
      return null;
    }
  },

  /**
   * Generate custom insights from data
   */
  async generateCustomInsights(
    data: Record<string, any>,
    context: string,
    dispatch: any,
    insightType: string = 'general'
  ): Promise<AIInsightResponse | null> {
    try {
      const result = await dispatch(
        aiApi.endpoints.generateInsights.initiate({
          context,
          data,
          insight_type: insightType,
        })
      );
      return result.data || null;
    } catch (error) {
      console.error('Generate insights failed:', error);
      return null;
    }
  },

  /**
   * Analyze document with AI
   */
  async analyzeDocument(
    documentContent: string,
    dispatch: any,
    documentType: string = 'unknown'
  ): Promise<DocumentAnalysisResponse | null> {
    try {
      const result = await dispatch(
        aiApi.endpoints.analyzeDocument.initiate({
          document_content: documentContent,
          document_type: documentType,
        })
      );
      return result.data || null;
    } catch (error) {
      console.error('Document analysis failed:', error);
      return null;
    }
  },
};

// Selectors for AI data
export const selectDealScore = (dealId: string) => (state: RootState) => {
  return aiApi.endpoints.getDealScore.select(dealId)(state)?.data;
};

export const selectPipelineVelocity = (daysBack: number = 30) => (state: RootState) => {
  return aiApi.endpoints.getPipelineVelocity.select({ daysBack })(state)?.data;
};

export const selectAIModelsStatus = (state: RootState) => {
  return aiApi.endpoints.getAIModelsStatus.select()(state)?.data;
};

export const selectDealRecommendations = (dealId: string) => (state: RootState) => {
  return aiApi.endpoints.getDealRecommendations.select(dealId)(state)?.data;
};

export default aiApi;