/**
 * RTK Query API slice for Platform Integrations
 * Handles multi-platform integrations (Shopify, Salesforce, HubSpot, QuickBooks, etc.)
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type IntegrationPlatform =
  | 'shopify'
  | 'salesforce'
  | 'hubspot'
  | 'quickbooks'
  | 'xero'
  | 'stripe'
  | 'mailchimp'
  | 'slack'
  | 'zapier'
  | 'google_drive'
  | 'dropbox'
  | 'microsoft_dynamics'
  | 'sap'
  | 'netsuite';

export type IntegrationStatus = 'active' | 'inactive' | 'error' | 'pending_auth' | 'expired';
export type SyncStatus = 'idle' | 'syncing' | 'completed' | 'failed';
export type DataEntity = 'customers' | 'products' | 'orders' | 'invoices' | 'contacts' | 'deals' | 'companies' | 'documents';

export interface Integration {
  id: string;
  organization_id: string;

  // Platform Details
  platform: IntegrationPlatform;
  platform_instance_name?: string;
  platform_account_id?: string;

  // Status
  status: IntegrationStatus;
  is_enabled: boolean;

  // Authentication
  auth_type: 'oauth2' | 'api_key' | 'basic_auth';
  auth_expires_at?: string;
  last_auth_refresh?: string;

  // Sync Configuration
  sync_enabled: boolean;
  sync_frequency: 'realtime' | 'hourly' | 'daily' | 'weekly' | 'manual';
  sync_entities: DataEntity[];
  last_sync_at?: string;
  next_sync_at?: string;

  // Sync Statistics
  total_syncs: number;
  successful_syncs: number;
  failed_syncs: number;
  last_sync_status?: SyncStatus;
  last_sync_error?: string;
  records_synced_count: number;

  // Mapping Configuration
  field_mappings: FieldMapping[];
  custom_settings: Record<string, any>;

  // Webhooks
  webhook_enabled: boolean;
  webhook_url?: string;
  webhook_events: string[];

  // Metadata
  tags: string[];
  notes?: string;

  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface IntegrationCreate {
  platform: IntegrationPlatform;
  platform_instance_name?: string;
  auth_type: 'oauth2' | 'api_key' | 'basic_auth';
  credentials?: Record<string, any>;
  sync_enabled?: boolean;
  sync_frequency?: 'realtime' | 'hourly' | 'daily' | 'weekly' | 'manual';
  sync_entities?: DataEntity[];
  field_mappings?: FieldMapping[];
  custom_settings?: Record<string, any>;
  webhook_enabled?: boolean;
  webhook_events?: string[];
  tags?: string[];
  notes?: string;
}

export interface IntegrationUpdate extends Partial<IntegrationCreate> {
  is_enabled?: boolean;
}

export interface FieldMapping {
  source_field: string;
  target_field: string;
  transform?: 'uppercase' | 'lowercase' | 'trim' | 'date_format' | 'currency_format' | 'custom';
  transform_function?: string;
  is_required: boolean;
  default_value?: any;
}

export interface OAuth2Config {
  authorization_url: string;
  client_id: string;
  redirect_uri: string;
  scope: string[];
  state: string;
}

export interface OAuth2Callback {
  code: string;
  state: string;
  integration_id: string;
}

export interface IntegrationSync {
  id: string;
  integration_id: string;
  organization_id: string;

  // Sync Details
  sync_type: 'full' | 'incremental' | 'manual';
  entities_synced: DataEntity[];
  status: SyncStatus;

  // Timing
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;

  // Results
  records_processed: number;
  records_created: number;
  records_updated: number;
  records_failed: number;
  records_skipped: number;

  // Error Details
  error_message?: string;
  error_details?: Record<string, any>;
  failed_records?: Array<{
    record_id: string;
    error: string;
  }>;

  // Metadata
  triggered_by: 'schedule' | 'webhook' | 'manual' | 'api';
  triggered_by_user?: string;
}

export interface SyncTriggerRequest {
  integration_id: string;
  sync_type?: 'full' | 'incremental';
  entities?: DataEntity[];
  force?: boolean;
}

export interface IntegrationWebhook {
  id: string;
  integration_id: string;
  organization_id: string;

  // Webhook Details
  event_type: string;
  payload: Record<string, any>;
  headers: Record<string, string>;

  // Processing
  status: 'pending' | 'processed' | 'failed';
  processed_at?: string;
  retry_count: number;
  error_message?: string;

  received_at: string;
}

export interface DataMapping {
  id: string;
  integration_id: string;
  organization_id: string;

  // Mapping Details
  entity_type: DataEntity;
  external_id: string;
  internal_id: string;
  external_data: Record<string, any>;

  // Sync Status
  last_synced_at: string;
  sync_status: 'synced' | 'pending' | 'conflict' | 'error';
  conflict_reason?: string;

  created_at: string;
  updated_at: string;
}

export interface IntegrationPlatformInfo {
  platform: IntegrationPlatform;
  name: string;
  description: string;
  logo_url: string;
  category: 'crm' | 'ecommerce' | 'accounting' | 'communication' | 'storage' | 'automation' | 'erp';

  auth_type: 'oauth2' | 'api_key' | 'basic_auth';
  supported_entities: DataEntity[];
  supported_sync_frequencies: string[];

  features: {
    realtime_sync: boolean;
    webhooks: boolean;
    bulk_operations: boolean;
    custom_fields: boolean;
  };

  pricing_tier: 'free' | 'standard' | 'premium' | 'enterprise';
  documentation_url: string;
  setup_guide_url: string;
}

export interface IntegrationStatistics {
  organization_id: string;

  // Counts
  total_integrations: number;
  active_integrations: number;
  inactive_integrations: number;
  integrations_with_errors: number;

  // By Platform
  by_platform: Record<IntegrationPlatform, number>;

  // Sync Stats
  total_syncs_24h: number;
  successful_syncs_24h: number;
  failed_syncs_24h: number;
  total_records_synced_24h: number;

  // Performance
  average_sync_duration_seconds: number;
  sync_success_rate: number;

  // Recent Activity
  recent_syncs: IntegrationSync[];
  recent_errors: Array<{
    integration_id: string;
    platform: IntegrationPlatform;
    error: string;
    timestamp: string;
  }>;

  last_updated: string;
}

export interface IntegrationListResponse {
  data: Integration[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface IntegrationFilters {
  platform?: IntegrationPlatform[];
  status?: IntegrationStatus[];
  is_enabled?: boolean;
  sync_enabled?: boolean;
  search?: string;
  tags?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

export interface IntegrationTestResult {
  success: boolean;
  connection_status: 'connected' | 'failed';
  latency_ms: number;
  api_version?: string;
  available_entities?: DataEntity[];
  error_message?: string;
  tested_at: string;
}

export interface BulkSyncRequest {
  integration_ids: string[];
  sync_type?: 'full' | 'incremental';
  entities?: DataEntity[];
}

// ============================================================================
// API SLICE
// ============================================================================

export const integrationsApi = createApi({
  reducerPath: 'integrationsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/integrations',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Integration', 'IntegrationList', 'Sync', 'Webhook', 'Mapping', 'Statistics'],
  endpoints: (builder) => ({
    // ========================================================================
    // INTEGRATION MANAGEMENT
    // ========================================================================

    // Get available platforms
    getAvailablePlatforms: builder.query<IntegrationPlatformInfo[], void>({
      query: () => '/platforms',
    }),

    // Get platform details
    getPlatformInfo: builder.query<IntegrationPlatformInfo, IntegrationPlatform>({
      query: (platform) => `/platforms/${platform}`,
    }),

    // Create integration
    createIntegration: builder.mutation<Integration, IntegrationCreate>({
      query: (data) => ({
        url: '/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['IntegrationList', 'Statistics'],
    }),

    // Get integrations list
    getIntegrations: builder.query<IntegrationListResponse, IntegrationFilters | void>({
      query: (filters = {}) => ({
        url: '/',
        params: filters,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Integration' as const, id })),
              { type: 'IntegrationList', id: 'LIST' },
            ]
          : [{ type: 'IntegrationList', id: 'LIST' }],
    }),

    // Get single integration
    getIntegration: builder.query<Integration, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Integration', id }],
    }),

    // Update integration
    updateIntegration: builder.mutation<Integration, { id: string; data: IntegrationUpdate }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Integration', id },
        { type: 'IntegrationList', id: 'LIST' },
        'Statistics',
      ],
    }),

    // Delete integration
    deleteIntegration: builder.mutation<void, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['IntegrationList', 'Statistics'],
    }),

    // Test integration connection
    testIntegration: builder.mutation<IntegrationTestResult, string>({
      query: (id) => ({
        url: `/${id}/test`,
        method: 'POST',
      }),
    }),

    // ========================================================================
    // OAUTH2 AUTHENTICATION
    // ========================================================================

    // Get OAuth2 authorization URL
    getOAuth2Config: builder.mutation<OAuth2Config, { platform: IntegrationPlatform; integration_id?: string }>({
      query: (data) => ({
        url: '/oauth2/authorize',
        method: 'POST',
        body: data,
      }),
    }),

    // Handle OAuth2 callback
    handleOAuth2Callback: builder.mutation<Integration, OAuth2Callback>({
      query: (data) => ({
        url: '/oauth2/callback',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { integration_id }) => [
        { type: 'Integration', id: integration_id },
      ],
    }),

    // Refresh OAuth2 token
    refreshOAuth2Token: builder.mutation<Integration, string>({
      query: (id) => ({
        url: `/${id}/oauth2/refresh`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Integration', id },
      ],
    }),

    // ========================================================================
    // SYNC OPERATIONS
    // ========================================================================

    // Trigger sync
    triggerSync: builder.mutation<IntegrationSync, SyncTriggerRequest>({
      query: (data) => ({
        url: '/sync/trigger',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { integration_id }) => [
        { type: 'Integration', id: integration_id },
        'Sync',
        'Statistics',
      ],
    }),

    // Get sync history
    getSyncHistory: builder.query<IntegrationSync[], { integration_id?: string; limit?: number }>({
      query: (params) => ({
        url: '/sync/history',
        params,
      }),
      providesTags: ['Sync'],
    }),

    // Get sync details
    getSyncDetails: builder.query<IntegrationSync, string>({
      query: (sync_id) => `/sync/${sync_id}`,
      providesTags: (result, error, sync_id) => [{ type: 'Sync', id: sync_id }],
    }),

    // Cancel sync
    cancelSync: builder.mutation<void, string>({
      query: (sync_id) => ({
        url: `/sync/${sync_id}/cancel`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, sync_id) => [
        { type: 'Sync', id: sync_id },
      ],
    }),

    // Retry failed sync
    retrySync: builder.mutation<IntegrationSync, string>({
      query: (sync_id) => ({
        url: `/sync/${sync_id}/retry`,
        method: 'POST',
      }),
      invalidatesTags: ['Sync', 'Statistics'],
    }),

    // Bulk sync trigger
    bulkTriggerSync: builder.mutation<{ triggered_count: number; sync_ids: string[] }, BulkSyncRequest>({
      query: (data) => ({
        url: '/sync/bulk-trigger',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['IntegrationList', 'Sync', 'Statistics'],
    }),

    // ========================================================================
    // WEBHOOKS
    // ========================================================================

    // Get webhooks
    getWebhooks: builder.query<IntegrationWebhook[], { integration_id?: string; status?: string; limit?: number }>({
      query: (params) => ({
        url: '/webhooks',
        params,
      }),
      providesTags: ['Webhook'],
    }),

    // Retry webhook processing
    retryWebhook: builder.mutation<IntegrationWebhook, string>({
      query: (webhook_id) => ({
        url: `/webhooks/${webhook_id}/retry`,
        method: 'POST',
      }),
      invalidatesTags: ['Webhook'],
    }),

    // ========================================================================
    // DATA MAPPINGS
    // ========================================================================

    // Get data mappings
    getMappings: builder.query<DataMapping[], { integration_id?: string; entity_type?: DataEntity }>({
      query: (params) => ({
        url: '/mappings',
        params,
      }),
      providesTags: ['Mapping'],
    }),

    // Resolve mapping conflict
    resolveMappingConflict: builder.mutation<DataMapping, { mapping_id: string; resolution: 'use_external' | 'use_internal' | 'merge' }>({
      query: ({ mapping_id, resolution }) => ({
        url: `/mappings/${mapping_id}/resolve`,
        method: 'POST',
        body: { resolution },
      }),
      invalidatesTags: ['Mapping'],
    }),

    // ========================================================================
    // STATISTICS
    // ========================================================================

    // Get integration statistics
    getStatistics: builder.query<IntegrationStatistics, void>({
      query: () => '/statistics',
      providesTags: ['Statistics'],
    }),

    // ========================================================================
    // FIELD MAPPINGS
    // ========================================================================

    // Get available fields for platform
    getAvailableFields: builder.query<{ entity: DataEntity; fields: string[] }[], { platform: IntegrationPlatform; entity?: DataEntity }>({
      query: ({ platform, entity }) => ({
        url: `/platforms/${platform}/fields`,
        params: { entity },
      }),
    }),

    // Update field mappings
    updateFieldMappings: builder.mutation<Integration, { integration_id: string; mappings: FieldMapping[] }>({
      query: ({ integration_id, mappings }) => ({
        url: `/${integration_id}/mappings`,
        method: 'PUT',
        body: { mappings },
      }),
      invalidatesTags: (result, error, { integration_id }) => [
        { type: 'Integration', id: integration_id },
      ],
    }),
  }),
});

// ============================================================================
// EXPORT HOOKS
// ============================================================================

export const {
  // Platform hooks
  useGetAvailablePlatformsQuery,
  useGetPlatformInfoQuery,

  // Integration management hooks
  useCreateIntegrationMutation,
  useGetIntegrationsQuery,
  useGetIntegrationQuery,
  useUpdateIntegrationMutation,
  useDeleteIntegrationMutation,
  useTestIntegrationMutation,

  // OAuth2 hooks
  useGetOAuth2ConfigMutation,
  useHandleOAuth2CallbackMutation,
  useRefreshOAuth2TokenMutation,

  // Sync hooks
  useTriggerSyncMutation,
  useGetSyncHistoryQuery,
  useGetSyncDetailsQuery,
  useCancelSyncMutation,
  useRetrySyncMutation,
  useBulkTriggerSyncMutation,

  // Webhook hooks
  useGetWebhooksQuery,
  useRetryWebhookMutation,

  // Mapping hooks
  useGetMappingsQuery,
  useResolveMappingConflictMutation,

  // Statistics hooks
  useGetStatisticsQuery,

  // Field mapping hooks
  useGetAvailableFieldsQuery,
  useUpdateFieldMappingsMutation,
} = integrationsApi;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const getPlatformLabel = (platform: IntegrationPlatform): string => {
  const labels: Record<IntegrationPlatform, string> = {
    shopify: 'Shopify',
    salesforce: 'Salesforce',
    hubspot: 'HubSpot',
    quickbooks: 'QuickBooks',
    xero: 'Xero',
    stripe: 'Stripe',
    mailchimp: 'Mailchimp',
    slack: 'Slack',
    zapier: 'Zapier',
    google_drive: 'Google Drive',
    dropbox: 'Dropbox',
    microsoft_dynamics: 'Microsoft Dynamics',
    sap: 'SAP',
    netsuite: 'NetSuite',
  };
  return labels[platform];
};

export const getStatusColor = (status: IntegrationStatus): string => {
  const colors: Record<IntegrationStatus, string> = {
    active: '#4caf50',
    inactive: '#9e9e9e',
    error: '#f44336',
    pending_auth: '#ff9800',
    expired: '#795548',
  };
  return colors[status];
};

export const getSyncStatusColor = (status: SyncStatus): string => {
  const colors: Record<SyncStatus, string> = {
    idle: '#9e9e9e',
    syncing: '#2196f3',
    completed: '#4caf50',
    failed: '#f44336',
  };
  return colors[status];
};

export const formatSyncDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
};

export const getSyncFrequencyLabel = (frequency: string): string => {
  const labels: Record<string, string> = {
    realtime: 'Real-time',
    hourly: 'Every Hour',
    daily: 'Daily',
    weekly: 'Weekly',
    manual: 'Manual Only',
  };
  return labels[frequency] || frequency;
};

export const getEntityLabel = (entity: DataEntity): string => {
  const labels: Record<DataEntity, string> = {
    customers: 'Customers',
    products: 'Products',
    orders: 'Orders',
    invoices: 'Invoices',
    contacts: 'Contacts',
    deals: 'Deals',
    companies: 'Companies',
    documents: 'Documents',
  };
  return labels[entity];
};
