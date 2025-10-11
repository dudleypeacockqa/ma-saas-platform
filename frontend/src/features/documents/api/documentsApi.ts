/**
 * RTK Query API slice for document management
 * Story 3.2: Document List UI - API integration
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../../../app/store';

// Types
export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_extension: string;
  mime_type: string;
  file_size: number;
  document_type: string;
  status: string;
  folder_path: string;
  deal_id?: string;
  version: number;
  is_latest_version: boolean;
  is_confidential: boolean;
  title?: string;
  description?: string;
  tags: string[];
  uploaded_at: string;
  modified_at: string;
  download_count: number;
  view_count: number;
  presigned_url?: string;
}

export interface DocumentListResponse {
  data: Document[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface DocumentUploadRequest {
  file: File;
  title?: string;
  description?: string;
  document_type?: string;
  folder_path?: string;
  deal_id?: string;
  tags?: string[];
  is_confidential?: boolean;
}

export interface DocumentSearchParams {
  search?: string;
  deal_id?: string;
  folder_path?: string;
  document_type?: string;
  tags?: string[];
  is_confidential?: boolean;
  page?: number;
  per_page?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface Folder {
  id: string;
  name: string;
  path: string;
  parent_id?: string;
  deal_id?: string;
  description?: string;
  color?: string;
  icon?: string;
  is_system_folder: boolean;
  is_readonly: boolean;
  created_at: string;
  modified_at: string;
  document_count: number;
  total_size: number;
}

export interface PresignedUploadUrl {
  upload_url: string;
  fields: Record<string, string>;
  s3_key: string;
}

export interface BulkOperation {
  operation: 'move' | 'delete' | 'archive' | 'update_tags';
  document_ids: string[];
  data?: Record<string, any>;
}

// API Slice
export const documentsApi = createApi({
  reducerPath: 'documentsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1/documents',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth?.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      const tenantId = (getState() as RootState).auth?.currentTenant;
      if (tenantId) {
        headers.set('X-Tenant-ID', tenantId);
      }
      return headers;
    },
  }),
  tagTypes: ['Document', 'Folder'],
  endpoints: (builder) => ({
    // Get documents list
    getDocuments: builder.query<DocumentListResponse, DocumentSearchParams>({
      query: (params) => ({
        url: '/',
        params,
      }),
      providesTags: ['Document'],
    }),

    // Get single document
    getDocument: builder.query<Document, string>({
      query: (id) => `/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'Document', id }],
    }),

    // Upload document
    uploadDocument: builder.mutation<Document, FormData>({
      query: (formData) => ({
        url: '/upload',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Document', 'Folder'],
    }),

    // Get presigned upload URL
    getPresignedUploadUrl: builder.mutation<PresignedUploadUrl, {
      filename: string;
      content_type: string;
      deal_id?: string;
    }>({
      query: (data) => ({
        url: '/upload/presigned',
        method: 'POST',
        body: data,
      }),
    }),

    // Update document metadata
    updateDocument: builder.mutation<Document, { id: string; data: Partial<Document> }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'Document', id }],
    }),

    // Delete document
    deleteDocument: builder.mutation<void, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Document', 'Folder'],
    }),

    // Get download URL
    getDownloadUrl: builder.query<{ url: string }, string>({
      query: (id) => `/download/${id}`,
    }),

    // Bulk operations
    bulkOperation: builder.mutation<{ success: boolean; affected_count: number }, BulkOperation>({
      query: (operation) => ({
        url: '/bulk',
        method: 'POST',
        body: operation,
      }),
      invalidatesTags: ['Document', 'Folder'],
    }),

    // Folder operations
    getFolders: builder.query<Folder[], { path?: string; deal_id?: string }>({
      query: (params) => ({
        url: '/folders',
        params,
      }),
      providesTags: ['Folder'],
    }),

    createFolder: builder.mutation<Folder, {
      name: string;
      parent_path?: string;
      deal_id?: string;
      description?: string;
      color?: string;
      icon?: string;
    }>({
      query: (data) => ({
        url: '/folders',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Folder'],
    }),

    updateFolder: builder.mutation<Folder, { id: string; data: Partial<Folder> }>({
      query: ({ id, data }) => ({
        url: `/folders/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['Folder'],
    }),

    deleteFolder: builder.mutation<void, string>({
      query: (id) => ({
        url: `/folders/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Folder', 'Document'],
    }),

    // Document versions
    getDocumentVersions: builder.query<Document[], string>({
      query: (id) => `/${id}/versions`,
      providesTags: (_result, _error, id) => [{ type: 'Document', id }],
    }),

    // Search documents
    searchDocuments: builder.query<DocumentListResponse, { query: string; filters?: DocumentSearchParams }>({
      query: ({ query, filters }) => ({
        url: '/search',
        params: {
          q: query,
          ...filters,
        },
      }),
      providesTags: ['Document'],
    }),

    // Get document statistics
    getDocumentStats: builder.query<{
      total_documents: number;
      total_size: number;
      by_type: Record<string, number>;
      by_deal: Record<string, number>;
      recent_uploads: Document[];
      most_accessed: Document[];
    }, void>({
      query: () => '/stats',
    }),
  }),
});

// Export hooks
export const {
  useGetDocumentsQuery,
  useGetDocumentQuery,
  useUploadDocumentMutation,
  useGetPresignedUploadUrlMutation,
  useUpdateDocumentMutation,
  useDeleteDocumentMutation,
  useGetDownloadUrlQuery,
  useBulkOperationMutation,
  useGetFoldersQuery,
  useCreateFolderMutation,
  useUpdateFolderMutation,
  useDeleteFolderMutation,
  useGetDocumentVersionsQuery,
  useSearchDocumentsQuery,
  useGetDocumentStatsQuery,
} = documentsApi;

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getFileIcon = (mimeType: string, extension: string): string => {
  if (mimeType.startsWith('image/')) return 'image';
  if (mimeType.startsWith('video/')) return 'movie';
  if (mimeType.includes('pdf')) return 'picture_as_pdf';
  if (mimeType.includes('word') || extension === '.doc' || extension === '.docx') return 'description';
  if (mimeType.includes('excel') || extension === '.xls' || extension === '.xlsx') return 'table_chart';
  if (mimeType.includes('powerpoint') || extension === '.ppt' || extension === '.pptx') return 'slideshow';
  if (mimeType.includes('zip') || mimeType.includes('rar')) return 'folder_zip';
  return 'insert_drive_file';
};

export const getDocumentTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    nda: '#9c27b0',
    loi: '#2196f3',
    term_sheet: '#00bcd4',
    due_diligence: '#ff9800',
    financial_statement: '#4caf50',
    legal_document: '#f44336',
    presentation: '#3f51b5',
    report: '#009688',
    contract: '#795548',
    other: '#607d8b',
  };
  return colors[type] || colors.other;
};