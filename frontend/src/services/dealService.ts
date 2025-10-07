/**
 * Deal Service - API client for deal management
 * Handles all API calls related to deals, valuations, activities, milestones, and documents
 */

import { useAuth } from '@clerk/clerk-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Types
export interface Deal {
  id: string
  deal_number: string
  title: string
  code_name?: string
  deal_type: string
  stage: string
  priority: string

  target_company_name: string
  target_company_website?: string
  target_industry?: string

  deal_value?: number
  deal_currency: string
  enterprise_value?: number

  probability_of_close: number
  risk_level?: string

  deal_lead_id?: string
  deal_lead_name?: string

  days_in_pipeline: number
  is_active: boolean

  created_at: string
  updated_at: string

  team_member_count?: number
  document_count?: number
  activity_count?: number
}

export interface DealCreate {
  title: string
  code_name?: string
  deal_type: string
  stage: string
  priority: string

  target_company_name: string
  target_company_website?: string
  target_company_description?: string
  target_industry?: string
  target_country?: string
  target_employees?: number

  deal_value?: number
  deal_currency: string
  enterprise_value?: number
  equity_value?: number
  debt_assumed?: number
  revenue_multiple?: number
  ebitda_multiple?: number
  target_revenue?: number
  target_ebitda?: number

  cash_consideration?: number
  stock_consideration?: number
  earnout_consideration?: number
  ownership_percentage?: number

  initial_contact_date?: string
  expected_close_date?: string

  deal_lead_id?: string

  probability_of_close: number
  risk_level?: string

  executive_summary?: string
  investment_thesis?: string
  key_risks?: string[]
  key_opportunities?: string[]
  next_steps?: string

  tags?: string[]
}

export interface DealUpdate extends Partial<DealCreate> {}

export interface DealActivity {
  id: string
  activity_type: string
  activity_date: string
  subject: string
  description?: string
  participants?: string[]
  outcome?: string
  follow_up_required: boolean
  follow_up_date?: string
  created_by: string
}

export interface DealActivityCreate {
  activity_type: string
  subject: string
  description?: string
  participants?: string[]
  outcome?: string
  follow_up_required?: boolean
  follow_up_date?: string
}

export interface DealValuation {
  id: string
  valuation_date: string
  valuation_method: string
  enterprise_value_low?: number
  enterprise_value_mid?: number
  enterprise_value_high?: number
  assumptions?: Record<string, any>
  notes?: string
  prepared_by?: string
}

export interface DealValuationCreate {
  valuation_date: string
  valuation_method: string
  enterprise_value_low?: number
  enterprise_value_mid?: number
  enterprise_value_high?: number
  assumptions?: Record<string, any>
  notes?: string
}

export interface DealMilestone {
  id: string
  title: string
  description?: string
  milestone_type?: string
  target_date: string
  actual_completion_date?: string
  status: string
  owner_id?: string
  owner_name?: string
  completion_notes?: string
  is_critical: boolean
  is_overdue: boolean
  dependencies?: string[]
  created_at: string
}

export interface DealMilestoneCreate {
  title: string
  description?: string
  milestone_type?: string
  target_date: string
  owner_id?: string
  is_critical?: boolean
  dependencies?: string[]
}

export interface DealDocument {
  id: string
  title: string
  description?: string
  category: string
  file_name: string
  file_path?: string
  file_url?: string
  file_size?: number
  file_type?: string
  version: string
  is_confidential: boolean
  access_level: string
  tags?: string[]
  uploaded_by?: string
  upload_date: string
  reviewed_by?: string
  review_date?: string
  created_at: string
}

export interface DealDocumentCreate {
  title: string
  description?: string
  category: string
  file_name: string
  file_path?: string
  file_url?: string
  file_size?: number
  file_type?: string
  version?: string
  is_confidential?: boolean
  access_level?: string
  tags?: string[]
}

export interface DealTeamMember {
  id: string
  user_id: string
  user_name?: string
  user_email?: string
  role: string
  responsibilities?: string
  time_allocation_percentage?: number
  added_date: string
}

export interface DealAnalytics {
  total_deals: number
  active_deals: number
  total_pipeline_value: number
  average_deal_size: number
  average_days_to_close: number
  win_rate: number
  deals_by_stage: Record<string, number>
  deals_by_priority: Record<string, number>
  deals_by_industry: Record<string, number>
  monthly_deal_flow: Array<{ month: string; count: number }>
  top_deal_leads: Array<{ user_id: string; deal_count: number; total_value: number }>
}

// Helper function to get auth headers
async function getAuthHeaders(getToken: any): Promise<HeadersInit> {
  const token = await getToken()
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }
}

// Deal CRUD Operations

export async function listDeals(
  getToken: any,
  params: {
    stage?: string
    priority?: string
    is_active?: boolean
    search?: string
    skip?: number
    limit?: number
    sort_by?: string
    sort_order?: string
  } = {}
): Promise<Deal[]> {
  const headers = await getAuthHeaders(getToken)
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, String(value))
    }
  })

  const response = await fetch(
    `${API_BASE_URL}/api/deals?${queryParams.toString()}`,
    { headers }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch deals: ${response.statusText}`)
  }

  return response.json()
}

export async function getDeal(getToken: any, dealId: string): Promise<Deal> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}`, { headers })

  if (!response.ok) {
    throw new Error(`Failed to fetch deal: ${response.statusText}`)
  }

  return response.json()
}

export async function createDeal(getToken: any, data: DealCreate): Promise<Deal> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to create deal: ${response.statusText}`)
  }

  return response.json()
}

export async function updateDeal(
  getToken: any,
  dealId: string,
  data: DealUpdate
): Promise<Deal> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to update deal: ${response.statusText}`)
  }

  return response.json()
}

export async function deleteDeal(getToken: any, dealId: string): Promise<void> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    throw new Error(`Failed to delete deal: ${response.statusText}`)
  }
}

export async function updateDealStage(
  getToken: any,
  dealId: string,
  stage: string,
  notes?: string
): Promise<Deal> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/stage`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ stage, notes }),
  })

  if (!response.ok) {
    throw new Error(`Failed to update deal stage: ${response.statusText}`)
  }

  return response.json()
}

// Activities

export async function listActivities(
  getToken: any,
  dealId: string,
  params: { skip?: number; limit?: number } = {}
): Promise<DealActivity[]> {
  const headers = await getAuthHeaders(getToken)
  const queryParams = new URLSearchParams()

  if (params.skip) queryParams.append('skip', String(params.skip))
  if (params.limit) queryParams.append('limit', String(params.limit))

  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/activities?${queryParams.toString()}`,
    { headers }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch activities: ${response.statusText}`)
  }

  return response.json()
}

export async function createActivity(
  getToken: any,
  dealId: string,
  data: DealActivityCreate
): Promise<{ message: string; id: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/activities`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to create activity: ${response.statusText}`)
  }

  return response.json()
}

// Valuations

export async function listValuations(
  getToken: any,
  dealId: string
): Promise<DealValuation[]> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/valuations`,
    { headers }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch valuations: ${response.statusText}`)
  }

  return response.json()
}

export async function createValuation(
  getToken: any,
  dealId: string,
  data: DealValuationCreate
): Promise<{ message: string; id: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/valuations`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to create valuation: ${response.statusText}`)
  }

  return response.json()
}

// Milestones

export async function listMilestones(
  getToken: any,
  dealId: string,
  status?: string
): Promise<DealMilestone[]> {
  const headers = await getAuthHeaders(getToken)
  const queryParams = status ? `?status=${status}` : ''

  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/milestones${queryParams}`,
    { headers }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch milestones: ${response.statusText}`)
  }

  return response.json()
}

export async function createMilestone(
  getToken: any,
  dealId: string,
  data: DealMilestoneCreate
): Promise<{ message: string; id: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/milestones`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to create milestone: ${response.statusText}`)
  }

  return response.json()
}

export async function updateMilestone(
  getToken: any,
  dealId: string,
  milestoneId: string,
  data: Partial<DealMilestone>
): Promise<{ message: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/milestones/${milestoneId}`,
    {
      method: 'PATCH',
      headers,
      body: JSON.stringify(data),
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to update milestone: ${response.statusText}`)
  }

  return response.json()
}

export async function deleteMilestone(
  getToken: any,
  dealId: string,
  milestoneId: string
): Promise<void> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/milestones/${milestoneId}`,
    {
      method: 'DELETE',
      headers,
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to delete milestone: ${response.statusText}`)
  }
}

// Documents

export async function listDocuments(
  getToken: any,
  dealId: string,
  params: { category?: string; skip?: number; limit?: number } = {}
): Promise<DealDocument[]> {
  const headers = await getAuthHeaders(getToken)
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) queryParams.append(key, String(value))
  })

  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/documents?${queryParams.toString()}`,
    { headers }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.statusText}`)
  }

  return response.json()
}

export async function createDocument(
  getToken: any,
  dealId: string,
  data: DealDocumentCreate
): Promise<{ message: string; id: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/documents`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to create document: ${response.statusText}`)
  }

  return response.json()
}

export async function deleteDocument(
  getToken: any,
  dealId: string,
  documentId: string
): Promise<void> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(
    `${API_BASE_URL}/api/deals/${dealId}/documents/${documentId}`,
    {
      method: 'DELETE',
      headers,
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to delete document: ${response.statusText}`)
  }
}

// Team Members

export async function listTeamMembers(
  getToken: any,
  dealId: string
): Promise<DealTeamMember[]> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/team`, { headers })

  if (!response.ok) {
    throw new Error(`Failed to fetch team members: ${response.statusText}`)
  }

  return response.json()
}

export async function addTeamMember(
  getToken: any,
  dealId: string,
  data: {
    user_id: string
    role: string
    responsibilities?: string
    time_allocation_percentage?: number
  }
): Promise<{ message: string }> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/${dealId}/team`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`Failed to add team member: ${response.statusText}`)
  }

  return response.json()
}

// Analytics

export async function getAnalytics(getToken: any): Promise<DealAnalytics> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/analytics/summary`, { headers })

  if (!response.ok) {
    throw new Error(`Failed to fetch analytics: ${response.statusText}`)
  }

  return response.json()
}

// Comparison

export async function compareDeals(
  getToken: any,
  dealIds: string[]
): Promise<{
  deals: Deal[]
  comparison_date: string
  compared_by: string
}> {
  const headers = await getAuthHeaders(getToken)
  const response = await fetch(`${API_BASE_URL}/api/deals/compare`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ deal_ids: dealIds }),
  })

  if (!response.ok) {
    throw new Error(`Failed to compare deals: ${response.statusText}`)
  }

  return response.json()
}

export default {
  listDeals,
  getDeal,
  createDeal,
  updateDeal,
  deleteDeal,
  updateDealStage,
  listActivities,
  createActivity,
  listValuations,
  createValuation,
  listMilestones,
  createMilestone,
  updateMilestone,
  deleteMilestone,
  listDocuments,
  createDocument,
  deleteDocument,
  listTeamMembers,
  addTeamMember,
  getAnalytics,
  compareDeals,
}
