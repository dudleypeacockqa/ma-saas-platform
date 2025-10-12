/**
 * RTK Query API slice for Content Creation and Marketing
 * Handles blog posts, newsletters, podcasts, social media, and content campaigns
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/app/store';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type ContentType = 'blog_post' | 'newsletter' | 'podcast' | 'social_post' | 'video' | 'whitepaper' | 'case_study' | 'ebook';
export type ContentStatus = 'draft' | 'review' | 'scheduled' | 'published' | 'archived';
export type PublishingPlatform = 'website' | 'linkedin' | 'twitter' | 'facebook' | 'instagram' | 'youtube' | 'medium' | 'substack';

export interface ContentItem {
  id: string;
  organization_id: string;

  // Basic Information
  title: string;
  slug?: string;
  content_type: ContentType;
  status: ContentStatus;

  // Content
  content: string;
  excerpt?: string;
  seo_title?: string;
  seo_description?: string;
  seo_keywords: string[];

  // Media
  featured_image_url?: string;
  thumbnail_url?: string;
  media_urls: string[];

  // Authoring
  author_id: string;
  author_name?: string;
  co_authors: string[];

  // Categories and Tags
  category?: string;
  tags: string[];
  topics: string[];

  // Publishing
  published_at?: string;
  scheduled_for?: string;
  publishing_platforms: PublishingPlatform[];

  // Engagement Metrics
  views_count: number;
  likes_count: number;
  shares_count: number;
  comments_count: number;
  engagement_rate?: number;

  // SEO Metrics
  seo_score?: number;
  readability_score?: number;
  word_count: number;
  reading_time_minutes: number;

  // AI Features
  ai_generated: boolean;
  ai_assisted: boolean;
  ai_suggestions?: string[];

  // Versioning
  version: number;
  is_latest_version: boolean;

  // Metadata
  custom_fields: Record<string, any>;
  notes?: string;

  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface ContentCreate {
  title: string;
  content_type: ContentType;
  content: string;
  excerpt?: string;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string[];
  featured_image_url?: string;
  thumbnail_url?: string;
  category?: string;
  tags?: string[];
  topics?: string[];
  status?: ContentStatus;
  scheduled_for?: string;
  publishing_platforms?: PublishingPlatform[];
  custom_fields?: Record<string, any>;
  notes?: string;
}

export interface ContentUpdate extends Partial<ContentCreate> {
  co_authors?: string[];
}

export interface Newsletter {
  id: string;
  organization_id: string;

  // Basic Information
  subject: string;
  preview_text?: string;
  content: string;

  // Design
  template_id?: string;
  template_name?: string;

  // Audience
  subscriber_list_ids: string[];
  total_recipients: number;
  segment_filters?: Record<string, any>;

  // Scheduling
  status: 'draft' | 'scheduled' | 'sending' | 'sent' | 'paused' | 'cancelled';
  scheduled_for?: string;
  sent_at?: string;

  // Email Metrics
  emails_sent: number;
  emails_delivered: number;
  emails_bounced: number;
  opens_count: number;
  open_rate: number;
  clicks_count: number;
  click_rate: number;
  unsubscribes_count: number;
  spam_reports_count: number;

  // A/B Testing
  ab_test_enabled: boolean;
  ab_test_variants?: Array<{
    subject: string;
    percentage: number;
    opens: number;
    clicks: number;
  }>;

  // Personalization
  personalization_enabled: boolean;
  personalization_fields: string[];

  // Metadata
  tags: string[];
  campaign_id?: string;

  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface NewsletterCreate {
  subject: string;
  preview_text?: string;
  content: string;
  template_id?: string;
  subscriber_list_ids: string[];
  segment_filters?: Record<string, any>;
  scheduled_for?: string;
  ab_test_enabled?: boolean;
  ab_test_variants?: Array<{ subject: string; percentage: number }>;
  personalization_enabled?: boolean;
  tags?: string[];
  campaign_id?: string;
}

export interface PodcastEpisode {
  id: string;
  organization_id: string;

  // Episode Details
  title: string;
  episode_number?: number;
  season_number?: number;
  description: string;
  show_notes?: string;

  // Audio
  audio_url: string;
  audio_duration_seconds: number;
  audio_file_size_bytes: number;

  // Publishing
  status: ContentStatus;
  published_at?: string;
  scheduled_for?: string;

  // Metadata
  hosts: string[];
  guests: string[];
  topics: string[];
  tags: string[];

  // Distribution
  rss_published: boolean;
  platforms: Array<{
    platform: 'spotify' | 'apple_podcasts' | 'google_podcasts' | 'youtube';
    url?: string;
    published: boolean;
  }>;

  // Engagement
  downloads_count: number;
  listens_count: number;
  average_listen_percentage: number;
  ratings_count: number;
  average_rating: number;

  // SEO
  seo_title?: string;
  seo_description?: string;
  transcript?: string;
  transcript_url?: string;

  // Artwork
  cover_image_url?: string;
  thumbnail_url?: string;

  created_at: string;
  updated_at: string;
}

export interface PodcastEpisodeCreate {
  title: string;
  episode_number?: number;
  season_number?: number;
  description: string;
  show_notes?: string;
  audio_url: string;
  audio_duration_seconds: number;
  hosts?: string[];
  guests?: string[];
  topics?: string[];
  tags?: string[];
  status?: ContentStatus;
  scheduled_for?: string;
  cover_image_url?: string;
  transcript?: string;
}

export interface ContentCampaign {
  id: string;
  organization_id: string;

  // Campaign Details
  name: string;
  description?: string;
  objective: 'brand_awareness' | 'lead_generation' | 'engagement' | 'sales' | 'education';

  // Timeline
  status: 'planning' | 'active' | 'paused' | 'completed' | 'cancelled';
  start_date: string;
  end_date?: string;

  // Content
  content_items_ids: string[];
  content_items_count: number;

  // Targeting
  target_audience?: string;
  target_personas?: string[];

  // Budget
  budget_amount?: number;
  budget_currency: string;
  actual_spend?: number;

  // Performance Goals
  goal_impressions?: number;
  goal_clicks?: number;
  goal_conversions?: number;
  goal_revenue?: number;

  // Actual Performance
  total_impressions: number;
  total_clicks: number;
  total_conversions: number;
  total_revenue: number;
  roi: number;

  // Team
  owner_id: string;
  team_members: string[];

  // Metadata
  tags: string[];
  notes?: string;

  created_at: string;
  updated_at: string;
}

export interface ContentCampaignCreate {
  name: string;
  description?: string;
  objective: 'brand_awareness' | 'lead_generation' | 'engagement' | 'sales' | 'education';
  start_date: string;
  end_date?: string;
  target_audience?: string;
  target_personas?: string[];
  budget_amount?: number;
  budget_currency?: string;
  goal_impressions?: number;
  goal_clicks?: number;
  goal_conversions?: number;
  goal_revenue?: number;
  tags?: string[];
  notes?: string;
}

export interface AIContentGeneration {
  prompt: string;
  content_type: ContentType;
  tone?: 'professional' | 'casual' | 'friendly' | 'authoritative' | 'conversational';
  length?: 'short' | 'medium' | 'long';
  keywords?: string[];
  target_audience?: string;
  include_seo?: boolean;
}

export interface AIContentResult {
  content: string;
  title?: string;
  excerpt?: string;
  seo_title?: string;
  seo_description?: string;
  suggested_keywords: string[];
  seo_score: number;
  readability_score: number;
  word_count: number;
  suggestions: string[];
  generated_at: string;
}

export interface ContentAnalytics {
  content_id: string;
  period: 'day' | 'week' | 'month' | 'year' | 'all_time';

  // Traffic
  pageviews: number;
  unique_visitors: number;
  returning_visitors: number;

  // Engagement
  avg_time_on_page_seconds: number;
  bounce_rate: number;
  scroll_depth_percentage: number;
  social_shares: number;
  comments: number;

  // SEO
  organic_traffic: number;
  search_rankings: Array<{
    keyword: string;
    position: number;
    change: number;
  }>;

  // Conversions
  conversions: number;
  conversion_rate: number;
  revenue_attributed: number;

  // Traffic Sources
  traffic_sources: Record<string, number>;
  top_referrers: Array<{ domain: string; visits: number }>;

  // Geographic
  top_countries: Array<{ country: string; visits: number }>;
  top_cities: Array<{ city: string; visits: number }>;

  calculated_at: string;
}

export interface ContentListResponse {
  data: ContentItem[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface ContentFilters {
  content_type?: ContentType[];
  status?: ContentStatus[];
  author_id?: string;
  category?: string;
  tags?: string[];
  topics?: string[];
  search?: string;
  published_from?: string;
  published_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

// ============================================================================
// API SLICE
// ============================================================================

export const contentApi = createApi({
  reducerPath: 'contentApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/content',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Content', 'ContentList', 'Newsletter', 'Podcast', 'Campaign', 'Analytics'],
  endpoints: (builder) => ({
    // ========================================================================
    // CONTENT MANAGEMENT
    // ========================================================================

    // Create content
    createContent: builder.mutation<ContentItem, ContentCreate>({
      query: (data) => ({
        url: '/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['ContentList'],
    }),

    // Get content list
    getContent: builder.query<ContentListResponse, ContentFilters | void>({
      query: (filters = {}) => ({
        url: '/',
        params: filters,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Content' as const, id })),
              { type: 'ContentList', id: 'LIST' },
            ]
          : [{ type: 'ContentList', id: 'LIST' }],
    }),

    // Get single content item
    getContentItem: builder.query<ContentItem, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Content', id }],
    }),

    // Update content
    updateContent: builder.mutation<ContentItem, { id: string; data: ContentUpdate }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Content', id },
        { type: 'ContentList', id: 'LIST' },
      ],
    }),

    // Delete content
    deleteContent: builder.mutation<void, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['ContentList'],
    }),

    // Publish content
    publishContent: builder.mutation<ContentItem, { id: string; platforms?: PublishingPlatform[] }>({
      query: ({ id, platforms }) => ({
        url: `/${id}/publish`,
        method: 'POST',
        body: { platforms },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Content', id },
        { type: 'ContentList', id: 'LIST' },
      ],
    }),

    // Schedule content
    scheduleContent: builder.mutation<ContentItem, { id: string; scheduled_for: string; platforms?: PublishingPlatform[] }>({
      query: ({ id, scheduled_for, platforms }) => ({
        url: `/${id}/schedule`,
        method: 'POST',
        body: { scheduled_for, platforms },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Content', id },
        { type: 'ContentList', id: 'LIST' },
      ],
    }),

    // ========================================================================
    // AI CONTENT GENERATION
    // ========================================================================

    // Generate content with AI
    generateContent: builder.mutation<AIContentResult, AIContentGeneration>({
      query: (data) => ({
        url: '/ai/generate',
        method: 'POST',
        body: data,
      }),
    }),

    // Get AI suggestions for content
    getAISuggestions: builder.mutation<{ suggestions: string[]; improvements: string[] }, { content_id: string }>({
      query: ({ content_id }) => ({
        url: `/ai/suggestions/${content_id}`,
        method: 'POST',
      }),
    }),

    // Optimize SEO with AI
    optimizeSEO: builder.mutation<{ seo_title: string; seo_description: string; keywords: string[] }, { content_id: string }>({
      query: ({ content_id }) => ({
        url: `/ai/seo-optimize/${content_id}`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, { content_id }) => [
        { type: 'Content', id: content_id },
      ],
    }),

    // ========================================================================
    // NEWSLETTERS
    // ========================================================================

    // Create newsletter
    createNewsletter: builder.mutation<Newsletter, NewsletterCreate>({
      query: (data) => ({
        url: '/newsletters',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Newsletter'],
    }),

    // Get newsletters
    getNewsletters: builder.query<Newsletter[], { status?: string; campaign_id?: string }>({
      query: (params) => ({
        url: '/newsletters',
        params,
      }),
      providesTags: ['Newsletter'],
    }),

    // Get single newsletter
    getNewsletter: builder.query<Newsletter, string>({
      query: (id) => `/newsletters/${id}`,
      providesTags: (result, error, id) => [{ type: 'Newsletter', id }],
    }),

    // Send newsletter
    sendNewsletter: builder.mutation<Newsletter, { id: string; send_test?: boolean; test_email?: string }>({
      query: ({ id, send_test, test_email }) => ({
        url: `/newsletters/${id}/send`,
        method: 'POST',
        body: { send_test, test_email },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Newsletter', id },
      ],
    }),

    // ========================================================================
    // PODCASTS
    // ========================================================================

    // Create podcast episode
    createPodcast: builder.mutation<PodcastEpisode, PodcastEpisodeCreate>({
      query: (data) => ({
        url: '/podcasts',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Podcast'],
    }),

    // Get podcast episodes
    getPodcasts: builder.query<PodcastEpisode[], { status?: ContentStatus; season?: number }>({
      query: (params) => ({
        url: '/podcasts',
        params,
      }),
      providesTags: ['Podcast'],
    }),

    // Get single podcast episode
    getPodcast: builder.query<PodcastEpisode, string>({
      query: (id) => `/podcasts/${id}`,
      providesTags: (result, error, id) => [{ type: 'Podcast', id }],
    }),

    // Generate transcript
    generateTranscript: builder.mutation<{ transcript: string; transcript_url: string }, string>({
      query: (id) => ({
        url: `/podcasts/${id}/transcript`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Podcast', id },
      ],
    }),

    // ========================================================================
    // CAMPAIGNS
    // ========================================================================

    // Create campaign
    createCampaign: builder.mutation<ContentCampaign, ContentCampaignCreate>({
      query: (data) => ({
        url: '/campaigns',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Campaign'],
    }),

    // Get campaigns
    getCampaigns: builder.query<ContentCampaign[], { status?: string }>({
      query: (params) => ({
        url: '/campaigns',
        params,
      }),
      providesTags: ['Campaign'],
    }),

    // Get single campaign
    getCampaign: builder.query<ContentCampaign, string>({
      query: (id) => `/campaigns/${id}`,
      providesTags: (result, error, id) => [{ type: 'Campaign', id }],
    }),

    // Add content to campaign
    addContentToCampaign: builder.mutation<ContentCampaign, { campaign_id: string; content_ids: string[] }>({
      query: ({ campaign_id, content_ids }) => ({
        url: `/campaigns/${campaign_id}/content`,
        method: 'POST',
        body: { content_ids },
      }),
      invalidatesTags: (result, error, { campaign_id }) => [
        { type: 'Campaign', id: campaign_id },
      ],
    }),

    // ========================================================================
    // ANALYTICS
    // ========================================================================

    // Get content analytics
    getContentAnalytics: builder.query<ContentAnalytics, { content_id: string; period?: string }>({
      query: ({ content_id, period }) => ({
        url: `/analytics/${content_id}`,
        params: { period },
      }),
      providesTags: (result, error, { content_id }) => [
        { type: 'Analytics', id: content_id },
      ],
    }),

    // Get campaign analytics
    getCampaignAnalytics: builder.query<ContentAnalytics, { campaign_id: string; period?: string }>({
      query: ({ campaign_id, period }) => ({
        url: `/analytics/campaigns/${campaign_id}`,
        params: { period },
      }),
      providesTags: (result, error, { campaign_id }) => [
        { type: 'Analytics', id: `campaign-${campaign_id}` },
      ],
    }),
  }),
});

// ============================================================================
// EXPORT HOOKS
// ============================================================================

export const {
  // Content management hooks
  useCreateContentMutation,
  useGetContentQuery,
  useGetContentItemQuery,
  useUpdateContentMutation,
  useDeleteContentMutation,
  usePublishContentMutation,
  useScheduleContentMutation,

  // AI hooks
  useGenerateContentMutation,
  useGetAISuggestionsMutation,
  useOptimizeSEOMutation,

  // Newsletter hooks
  useCreateNewsletterMutation,
  useGetNewslettersQuery,
  useGetNewsletterQuery,
  useSendNewsletterMutation,

  // Podcast hooks
  useCreatePodcastMutation,
  useGetPodcastsQuery,
  useGetPodcastQuery,
  useGenerateTranscriptMutation,

  // Campaign hooks
  useCreateCampaignMutation,
  useGetCampaignsQuery,
  useGetCampaignQuery,
  useAddContentToCampaignMutation,

  // Analytics hooks
  useGetContentAnalyticsQuery,
  useGetCampaignAnalyticsQuery,
} = contentApi;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const getContentTypeLabel = (type: ContentType): string => {
  const labels: Record<ContentType, string> = {
    blog_post: 'Blog Post',
    newsletter: 'Newsletter',
    podcast: 'Podcast',
    social_post: 'Social Post',
    video: 'Video',
    whitepaper: 'Whitepaper',
    case_study: 'Case Study',
    ebook: 'eBook',
  };
  return labels[type];
};

export const getStatusColor = (status: ContentStatus): string => {
  const colors: Record<ContentStatus, string> = {
    draft: '#9e9e9e',
    review: '#ff9800',
    scheduled: '#2196f3',
    published: '#4caf50',
    archived: '#795548',
  };
  return colors[status];
};

export const formatReadingTime = (minutes: number): string => {
  if (minutes < 1) return 'Less than 1 min';
  if (minutes === 1) return '1 min read';
  return `${Math.round(minutes)} min read`;
};

export const calculateEngagementRate = (views: number, likes: number, shares: number, comments: number): number => {
  if (views === 0) return 0;
  return ((likes + shares + comments) / views) * 100;
};

export const getSEOScoreColor = (score: number): string => {
  if (score >= 80) return '#4caf50';
  if (score >= 60) return '#ff9800';
  return '#f44336';
};

export const getPlatformLabel = (platform: PublishingPlatform): string => {
  const labels: Record<PublishingPlatform, string> = {
    website: 'Website',
    linkedin: 'LinkedIn',
    twitter: 'Twitter',
    facebook: 'Facebook',
    instagram: 'Instagram',
    youtube: 'YouTube',
    medium: 'Medium',
    substack: 'Substack',
  };
  return labels[platform];
};
