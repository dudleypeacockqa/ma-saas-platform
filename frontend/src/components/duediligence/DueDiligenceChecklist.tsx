import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useOrganization } from '@clerk/clerk-react'
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  Clock,
  FileText,
  Upload,
  Download,
  Search,
  Filter,
  Plus,
  ChevronDown,
  ChevronRight,
  Flag,
  Users,
  Calendar,
  BarChart3,
  Shield,
  AlertTriangle,
  XCircle
} from 'lucide-react'

interface ChecklistTemplate {
  id: string
  name: string
  description: string
  type: string
  industry: string
  categories: string[]
  itemCount: number
  usageCount: number
}

interface ChecklistItem {
  id: string
  category: string
  title: string
  description: string
  isRequired: boolean
  documentTypes: string[]
  status: 'not_started' | 'requested' | 'uploaded' | 'under_review' | 'approved' | 'rejected'
  riskWeight: number
  criticalItem: boolean
  documents: Document[]
  reviews: Review[]
}

interface Document {
  id: string
  name: string
  uploadedBy: string
  uploadedAt: string
  status: string
  riskScore: number
}

interface Review {
  id: string
  reviewerId: string
  reviewerName: string
  status: string
  riskLevel: string
  findings: string
}

const categoryColors: Record<string, string> = {
  financial: 'bg-blue-100 text-blue-800 border-blue-300',
  legal: 'bg-purple-100 text-purple-800 border-purple-300',
  operational: 'bg-green-100 text-green-800 border-green-300',
  commercial: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  hr: 'bg-pink-100 text-pink-800 border-pink-300',
  it: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  regulatory: 'bg-red-100 text-red-800 border-red-300',
  tax: 'bg-orange-100 text-orange-800 border-orange-300'
}

const statusIcons: Record<string, React.ReactNode> = {
  not_started: <Circle className="w-5 h-5 text-gray-400" />,
  requested: <Clock className="w-5 h-5 text-yellow-500" />,
  uploaded: <FileText className="w-5 h-5 text-blue-500" />,
  under_review: <AlertCircle className="w-5 h-5 text-orange-500" />,
  approved: <CheckCircle2 className="w-5 h-5 text-green-500" />,
  rejected: <XCircle className="w-5 h-5 text-red-500" />
}

const templates: ChecklistTemplate[] = [
  {
    id: '1',
    name: 'Technology Company DD',
    description: 'Comprehensive checklist for technology and SaaS companies',
    type: 'technology',
    industry: 'Technology',
    categories: ['financial', 'legal', 'it', 'operational', 'commercial'],
    itemCount: 156,
    usageCount: 342
  },
  {
    id: '2',
    name: 'Healthcare DD',
    description: 'Due diligence for healthcare and medical companies',
    type: 'healthcare',
    industry: 'Healthcare',
    categories: ['financial', 'legal', 'regulatory', 'operational', 'commercial'],
    itemCount: 189,
    usageCount: 128
  },
  {
    id: '3',
    name: 'Manufacturing DD',
    description: 'Industrial and manufacturing company due diligence',
    type: 'manufacturing',
    industry: 'Manufacturing',
    categories: ['financial', 'legal', 'operational', 'environmental', 'hr'],
    itemCount: 167,
    usageCount: 95
  }
]

export default function DueDiligenceChecklist() {
  const { dealId } = useParams<{ dealId: string }>()
  const { organization } = useOrganization()
  const [selectedTemplate, setSelectedTemplate] = useState<ChecklistTemplate | null>(null)
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([])
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showTemplateModal, setShowTemplateModal] = useState(true)
  const [activeTab, setActiveTab] = useState<'checklist' | 'documents' | 'reviews' | 'risks'>('checklist')

  useEffect(() => {
    // Load checklist items based on template
    if (selectedTemplate) {
      loadChecklistItems()
    }
  }, [selectedTemplate])

  const loadChecklistItems = () => {
    // Mock data - replace with API call
    const items: ChecklistItem[] = [
      {
        id: '1',
        category: 'financial',
        title: 'Audited Financial Statements (3 years)',
        description: 'Complete audited financial statements for the last 3 fiscal years',
        isRequired: true,
        documentTypes: ['PDF', 'Excel'],
        status: 'approved',
        riskWeight: 2.0,
        criticalItem: true,
        documents: [],
        reviews: []
      },
      {
        id: '2',
        category: 'financial',
        title: 'Management Accounts (Current Year)',
        description: 'Unaudited management accounts for the current fiscal year',
        isRequired: true,
        documentTypes: ['PDF', 'Excel'],
        status: 'under_review',
        riskWeight: 1.5,
        criticalItem: false,
        documents: [],
        reviews: []
      },
      {
        id: '3',
        category: 'legal',
        title: 'Corporate Structure & Ownership',
        description: 'Complete corporate structure diagram and cap table',
        isRequired: true,
        documentTypes: ['PDF'],
        status: 'uploaded',
        riskWeight: 1.8,
        criticalItem: true,
        documents: [],
        reviews: []
      },
      {
        id: '4',
        category: 'legal',
        title: 'Material Contracts',
        description: 'All material customer and supplier contracts',
        isRequired: true,
        documentTypes: ['PDF'],
        status: 'requested',
        riskWeight: 1.6,
        criticalItem: false,
        documents: [],
        reviews: []
      },
      {
        id: '5',
        category: 'operational',
        title: 'Employee Handbook & Policies',
        description: 'Current employee handbook and HR policies',
        isRequired: false,
        documentTypes: ['PDF', 'Word'],
        status: 'not_started',
        riskWeight: 1.0,
        criticalItem: false,
        documents: [],
        reviews: []
      }
    ]
    setChecklistItems(items)
  }

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const getCompletionStats = () => {
    const total = checklistItems.length
    const completed = checklistItems.filter(item =>
      item.status === 'approved'
    ).length
    const inProgress = checklistItems.filter(item =>
      ['requested', 'uploaded', 'under_review'].includes(item.status)
    ).length
    const notStarted = checklistItems.filter(item =>
      item.status === 'not_started'
    ).length
    const rejected = checklistItems.filter(item =>
      item.status === 'rejected'
    ).length

    return {
      total,
      completed,
      inProgress,
      notStarted,
      rejected,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0
    }
  }

  const getRiskScore = () => {
    const criticalItems = checklistItems.filter(item => item.criticalItem)
    const criticalComplete = criticalItems.filter(item => item.status === 'approved').length
    const criticalRejected = criticalItems.filter(item => item.status === 'rejected').length

    let riskScore = 50 // Base score
    riskScore -= (criticalComplete * 10)
    riskScore += (criticalRejected * 15)

    return Math.max(0, Math.min(100, riskScore))
  }

  const getRiskLevel = (score: number) => {
    if (score >= 75) return { level: 'Critical', color: 'text-red-600', bg: 'bg-red-100' }
    if (score >= 50) return { level: 'High', color: 'text-orange-600', bg: 'bg-orange-100' }
    if (score >= 25) return { level: 'Medium', color: 'text-yellow-600', bg: 'bg-yellow-100' }
    return { level: 'Low', color: 'text-green-600', bg: 'bg-green-100' }
  }

  const stats = getCompletionStats()
  const riskScore = getRiskScore()
  const riskLevel = getRiskLevel(riskScore)

  const groupedItems = checklistItems.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = []
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, ChecklistItem[]>)

  const filteredItems = Object.entries(groupedItems).reduce((acc, [category, items]) => {
    if (filterCategory !== 'all' && category !== filterCategory) return acc

    const filtered = items.filter(item => {
      if (filterStatus !== 'all' && item.status !== filterStatus) return false
      if (searchTerm && !item.title.toLowerCase().includes(searchTerm.toLowerCase())) return false
      return true
    })

    if (filtered.length > 0) acc[category] = filtered
    return acc
  }, {} as Record<string, ChecklistItem[]>)

  if (showTemplateModal && !selectedTemplate) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">Select Due Diligence Template</h2>
            <p className="text-gray-600 mt-1">Choose a template to start your due diligence process</p>
          </div>

          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map(template => (
              <div
                key={template.id}
                onClick={() => {
                  setSelectedTemplate(template)
                  setShowTemplateModal(false)
                }}
                className="border rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-lg">{template.name}</h3>
                  <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    {template.itemCount} items
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-3">{template.description}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {template.categories.slice(0, 3).map(cat => (
                    <span
                      key={cat}
                      className={`text-xs px-2 py-1 rounded-full border ${categoryColors[cat] || 'bg-gray-100'}`}
                    >
                      {cat}
                    </span>
                  ))}
                  {template.categories.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{template.categories.length - 3} more
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  Used {template.usageCount} times
                </div>
              </div>
            ))}
          </div>

          <div className="p-6 border-t bg-gray-50 flex justify-between">
            <button className="px-4 py-2 text-gray-700 hover:text-gray-900">
              Create Custom Template
            </button>
            <button
              onClick={() => setShowTemplateModal(false)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Due Diligence Management</h1>
              <p className="text-gray-600 mt-1">
                {selectedTemplate?.name} - Deal #{dealId}
              </p>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export Report
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Bulk Upload
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Completion</span>
              <BarChart3 className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.percentage}%</div>
            <div className="text-xs text-gray-500 mt-1">
              {stats.completed} of {stats.total} items
            </div>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.percentage}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Risk Score</span>
              <Shield className="w-4 h-4 text-gray-400" />
            </div>
            <div className={`text-2xl font-bold ${riskLevel.color}`}>
              {riskScore}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs px-2 py-1 rounded-full ${riskLevel.bg} ${riskLevel.color}`}>
                {riskLevel.level} Risk
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">In Progress</span>
              <Clock className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-yellow-600">{stats.inProgress}</div>
            <div className="text-xs text-gray-500 mt-1">Items being reviewed</div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Issues</span>
              <AlertTriangle className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
            <div className="text-xs text-gray-500 mt-1">Items rejected</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg border">
          <div className="border-b">
            <div className="flex">
              {[
                { id: 'checklist', label: 'Checklist', icon: CheckCircle2 },
                { id: 'documents', label: 'Documents', icon: FileText },
                { id: 'reviews', label: 'Reviews', icon: Users },
                { id: 'risks', label: 'Risk Assessment', icon: Shield }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-6 py-3 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {activeTab === 'checklist' && (
            <div>
              {/* Filters */}
              <div className="p-4 border-b bg-gray-50">
                <div className="flex flex-wrap gap-3">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search items..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  <select
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All Categories</option>
                    <option value="financial">Financial</option>
                    <option value="legal">Legal</option>
                    <option value="operational">Operational</option>
                    <option value="commercial">Commercial</option>
                  </select>

                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All Status</option>
                    <option value="not_started">Not Started</option>
                    <option value="requested">Requested</option>
                    <option value="uploaded">Uploaded</option>
                    <option value="under_review">Under Review</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
              </div>

              {/* Checklist Items */}
              <div className="p-4">
                {Object.entries(filteredItems).map(([category, items]) => (
                  <div key={category} className="mb-6">
                    <button
                      onClick={() => toggleCategory(category)}
                      className="flex items-center gap-2 mb-3 text-gray-700 hover:text-gray-900"
                    >
                      {expandedCategories.has(category) ?
                        <ChevronDown className="w-4 h-4" /> :
                        <ChevronRight className="w-4 h-4" />
                      }
                      <span className="font-semibold capitalize">{category}</span>
                      <span className={`text-xs px-2 py-1 rounded-full border ${categoryColors[category]}`}>
                        {items.length} items
                      </span>
                    </button>

                    {expandedCategories.has(category) && (
                      <div className="space-y-2 ml-6">
                        {items.map(item => (
                          <div
                            key={item.id}
                            className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex items-start gap-3 flex-1">
                                {statusIcons[item.status]}
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <h4 className="font-medium text-gray-900">{item.title}</h4>
                                    {item.isRequired && (
                                      <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">
                                        Required
                                      </span>
                                    )}
                                    {item.criticalItem && (
                                      <Flag className="w-4 h-4 text-red-500" />
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                    <span>Accepts: {item.documentTypes.join(', ')}</span>
                                    <span>Risk Weight: {item.riskWeight}x</span>
                                  </div>
                                </div>
                              </div>

                              <div className="flex items-center gap-2">
                                <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded">
                                  <Upload className="w-4 h-4" />
                                </button>
                                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                                  <ChevronRight className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="p-6">
              <p className="text-gray-600">Document management interface coming soon...</p>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div className="p-6">
              <p className="text-gray-600">Review workflow interface coming soon...</p>
            </div>
          )}

          {activeTab === 'risks' && (
            <div className="p-6">
              <p className="text-gray-600">Risk assessment dashboard coming soon...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}