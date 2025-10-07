/**
 * React hooks for deal management
 * Provides easy-to-use hooks for all deal-related operations
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@clerk/clerk-react'
import * as dealService from '../services/dealService'
import type {
  Deal,
  DealCreate,
  DealUpdate,
  DealActivity,
  DealActivityCreate,
  DealValuation,
  DealValuationCreate,
  DealMilestone,
  DealMilestoneCreate,
  DealDocument,
  DealDocumentCreate,
  DealTeamMember,
  DealAnalytics,
} from '../services/dealService'

// Hook for listing deals with filters
export function useDeals(params?: Parameters<typeof dealService.listDeals>[1]) {
  const { getToken } = useAuth()
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchDeals = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listDeals(getToken, params)
      setDeals(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, JSON.stringify(params)])

  useEffect(() => {
    fetchDeals()
  }, [fetchDeals])

  return { deals, loading, error, refetch: fetchDeals }
}

// Hook for a single deal
export function useDeal(dealId: string | null) {
  const { getToken } = useAuth()
  const [deal, setDeal] = useState<Deal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchDeal = useCallback(async () => {
    if (!dealId) {
      setDeal(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.getDeal(getToken, dealId)
      setDeal(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId])

  useEffect(() => {
    fetchDeal()
  }, [fetchDeal])

  return { deal, loading, error, refetch: fetchDeal }
}

// Hook for deal CRUD operations
export function useDealMutations() {
  const { getToken } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const createDeal = async (data: DealCreate): Promise<Deal> => {
    try {
      setLoading(true)
      setError(null)
      const result = await dealService.createDeal(getToken, data)
      return result
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateDeal = async (dealId: string, data: DealUpdate): Promise<Deal> => {
    try {
      setLoading(true)
      setError(null)
      const result = await dealService.updateDeal(getToken, dealId, data)
      return result
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteDeal = async (dealId: string): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      await dealService.deleteDeal(getToken, dealId)
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateStage = async (dealId: string, stage: string, notes?: string): Promise<Deal> => {
    try {
      setLoading(true)
      setError(null)
      const result = await dealService.updateDealStage(getToken, dealId, stage, notes)
      return result
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { createDeal, updateDeal, deleteDeal, updateStage, loading, error }
}

// Hook for deal activities
export function useDealActivities(dealId: string | null, params?: { skip?: number; limit?: number }) {
  const { getToken } = useAuth()
  const [activities, setActivities] = useState<DealActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchActivities = useCallback(async () => {
    if (!dealId) {
      setActivities([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listActivities(getToken, dealId, params)
      setActivities(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId, JSON.stringify(params)])

  const createActivity = async (data: DealActivityCreate) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.createActivity(getToken, dealId, data)
      await fetchActivities()
    } catch (err) {
      throw err
    }
  }

  useEffect(() => {
    fetchActivities()
  }, [fetchActivities])

  return { activities, loading, error, refetch: fetchActivities, createActivity }
}

// Hook for deal valuations
export function useDealValuations(dealId: string | null) {
  const { getToken } = useAuth()
  const [valuations, setValuations] = useState<DealValuation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchValuations = useCallback(async () => {
    if (!dealId) {
      setValuations([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listValuations(getToken, dealId)
      setValuations(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId])

  const createValuation = async (data: DealValuationCreate) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.createValuation(getToken, dealId, data)
      await fetchValuations()
    } catch (err) {
      throw err
    }
  }

  useEffect(() => {
    fetchValuations()
  }, [fetchValuations])

  return { valuations, loading, error, refetch: fetchValuations, createValuation }
}

// Hook for deal milestones
export function useDealMilestones(dealId: string | null, status?: string) {
  const { getToken } = useAuth()
  const [milestones, setMilestones] = useState<DealMilestone[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchMilestones = useCallback(async () => {
    if (!dealId) {
      setMilestones([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listMilestones(getToken, dealId, status)
      setMilestones(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId, status])

  const createMilestone = async (data: DealMilestoneCreate) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.createMilestone(getToken, dealId, data)
      await fetchMilestones()
    } catch (err) {
      throw err
    }
  }

  const updateMilestone = async (milestoneId: string, data: Partial<DealMilestone>) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.updateMilestone(getToken, dealId, milestoneId, data)
      await fetchMilestones()
    } catch (err) {
      throw err
    }
  }

  const deleteMilestone = async (milestoneId: string) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.deleteMilestone(getToken, dealId, milestoneId)
      await fetchMilestones()
    } catch (err) {
      throw err
    }
  }

  useEffect(() => {
    fetchMilestones()
  }, [fetchMilestones])

  return {
    milestones,
    loading,
    error,
    refetch: fetchMilestones,
    createMilestone,
    updateMilestone,
    deleteMilestone,
  }
}

// Hook for deal documents
export function useDealDocuments(dealId: string | null, category?: string) {
  const { getToken } = useAuth()
  const [documents, setDocuments] = useState<DealDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchDocuments = useCallback(async () => {
    if (!dealId) {
      setDocuments([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listDocuments(getToken, dealId, { category })
      setDocuments(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId, category])

  const createDocument = async (data: DealDocumentCreate) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.createDocument(getToken, dealId, data)
      await fetchDocuments()
    } catch (err) {
      throw err
    }
  }

  const deleteDocument = async (documentId: string) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.deleteDocument(getToken, dealId, documentId)
      await fetchDocuments()
    } catch (err) {
      throw err
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  return {
    documents,
    loading,
    error,
    refetch: fetchDocuments,
    createDocument,
    deleteDocument,
  }
}

// Hook for deal team members
export function useDealTeam(dealId: string | null) {
  const { getToken } = useAuth()
  const [teamMembers, setTeamMembers] = useState<DealTeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchTeamMembers = useCallback(async () => {
    if (!dealId) {
      setTeamMembers([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await dealService.listTeamMembers(getToken, dealId)
      setTeamMembers(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, dealId])

  const addTeamMember = async (data: {
    user_id: string
    role: string
    responsibilities?: string
    time_allocation_percentage?: number
  }) => {
    if (!dealId) throw new Error('No deal ID provided')

    try {
      await dealService.addTeamMember(getToken, dealId, data)
      await fetchTeamMembers()
    } catch (err) {
      throw err
    }
  }

  useEffect(() => {
    fetchTeamMembers()
  }, [fetchTeamMembers])

  return { teamMembers, loading, error, refetch: fetchTeamMembers, addTeamMember }
}

// Hook for deal analytics
export function useDealAnalytics() {
  const { getToken } = useAuth()
  const [analytics, setAnalytics] = useState<DealAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await dealService.getAnalytics(getToken)
      setAnalytics(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  return { analytics, loading, error, refetch: fetchAnalytics }
}

// Hook for deal comparison
export function useDealComparison() {
  const { getToken } = useAuth()
  const [comparison, setComparison] = useState<{
    deals: Deal[]
    comparison_date: string
    compared_by: string
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const compareDeals = async (dealIds: string[]) => {
    try {
      setLoading(true)
      setError(null)
      const data = await dealService.compareDeals(getToken, dealIds)
      setComparison(data)
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { comparison, loading, error, compareDeals }
}
