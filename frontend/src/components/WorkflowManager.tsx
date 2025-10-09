import React, { useState, useEffect } from 'react'
import { useUser, useOrganization } from '@clerk/clerk-react'
import {
  Workflow,
  Play,
  Pause,
  Stop,
  Settings,
  Plus,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  ArrowRight,
  Copy,
  Edit,
  Trash2,
  Filter,
  Search,
  MoreHorizontal,
  Zap,
  GitBranch,
  Target,
  BarChart3,
  RefreshCw,
  Layers,
  Timer,
  Flag,
  Activity,
  Brain,
  ChevronDown,
  ChevronRight,
  Eye,
  Download,
  Upload
} from 'lucide-react'

import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Input } from './ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Progress } from './ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { Separator } from './ui/separator'
import { Textarea } from './ui/textarea'
import { Switch } from './ui/switch'
import { Label } from './ui/label'

// Types
interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: 'due_diligence' | 'negotiation' | 'integration' | 'compliance' | 'analysis'
  estimated_duration_days: number
  task_count: number
  complexity: 'simple' | 'moderate' | 'complex'
  is_public: boolean
  created_by: string
  created_at: string
  usage_count: number
}

interface WorkflowInstance {
  id: string
  template_id: string
  name: string
  description?: string
  team_id: string
  deal_id?: string
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'
  progress_percentage: number
  start_date?: string
  target_end_date?: string
  actual_end_date?: string
  created_by: string
  created_at: string
  updated_at?: string
}

interface WorkflowTask {
  id: string
  workflow_id: string
  name: string
  description?: string
  status: 'pending' | 'ready' | 'in_progress' | 'completed' | 'skipped' | 'failed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  estimated_hours: number
  actual_hours?: number
  assigned_to?: string
  depends_on: string[]
  start_date?: string
  due_date?: string
  completion_date?: string
  automation_rules?: string[]
}

interface AutomationRule {
  id: string
  name: string
  description: string
  trigger_type: 'task_completed' | 'task_overdue' | 'milestone_reached' | 'team_member_added'
  trigger_conditions: Record<string, any>
  actions: Array<{
    type: 'send_notification' | 'create_task' | 'assign_task' | 'update_status' | 'schedule_meeting'
    parameters: Record<string, any>
  }>
  is_active: boolean
  created_at: string
  execution_count: number
}

interface WorkflowMetrics {
  total_workflows: number
  active_workflows: number
  completed_workflows: number
  average_completion_time: number
  efficiency_score: number
  automation_usage: number
  bottleneck_tasks: string[]
  top_performing_templates: string[]
}

const WorkflowManager: React.FC = () => {
  const { user, isLoaded: userLoaded } = useUser()
  const { organization, isLoaded: orgLoaded } = useOrganization()

  // State
  const [workflows, setWorkflows] = useState<WorkflowInstance[]>([])
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([])
  const [automationRules, setAutomationRules] = useState<AutomationRule[]>([])
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowInstance | null>(null)
  const [workflowTasks, setWorkflowTasks] = useState<WorkflowTask[]>([])
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [activeTab, setActiveTab] = useState('workflows')

  // Mock data for development
  useEffect(() => {
    if (userLoaded && orgLoaded) {
      // Mock workflow templates
      const mockTemplates: WorkflowTemplate[] = [
        {
          id: '1',
          name: 'Financial Due Diligence',
          description: 'Comprehensive financial analysis and review process',
          category: 'due_diligence',
          estimated_duration_days: 21,
          task_count: 15,
          complexity: 'complex',
          is_public: true,
          created_by: 'system',
          created_at: '2024-01-01T00:00:00Z',
          usage_count: 45
        },
        {
          id: '2',
          name: 'Legal Due Diligence',
          description: 'Legal document review and compliance check',
          category: 'due_diligence',
          estimated_duration_days: 14,
          task_count: 12,
          complexity: 'moderate',
          is_public: true,
          created_by: 'system',
          created_at: '2024-01-01T00:00:00Z',
          usage_count: 38
        },
        {
          id: '3',
          name: 'Deal Negotiation Process',
          description: 'Structured approach to deal negotiations',
          category: 'negotiation',
          estimated_duration_days: 30,
          task_count: 20,
          complexity: 'complex',
          is_public: true,
          created_by: 'system',
          created_at: '2024-01-01T00:00:00Z',
          usage_count: 22
        }
      ]

      // Mock workflow instances
      const mockWorkflows: WorkflowInstance[] = [
        {
          id: '1',
          template_id: '1',
          name: 'TechCorp Financial DD',
          description: 'Financial due diligence for TechCorp acquisition',
          team_id: 'team-1',
          deal_id: 'deal-1',
          status: 'active',
          progress_percentage: 65,
          start_date: '2024-07-01T00:00:00Z',
          target_end_date: '2024-07-22T00:00:00Z',
          created_by: 'user-1',
          created_at: '2024-07-01T00:00:00Z'
        },
        {
          id: '2',
          template_id: '2',
          name: 'TechCorp Legal Review',
          description: 'Legal due diligence and contract review',
          team_id: 'team-1',
          deal_id: 'deal-1',
          status: 'completed',
          progress_percentage: 100,
          start_date: '2024-06-15T00:00:00Z',
          target_end_date: '2024-06-29T00:00:00Z',
          actual_end_date: '2024-06-28T00:00:00Z',
          created_by: 'user-2',
          created_at: '2024-06-15T00:00:00Z'
        },
        {
          id: '3',
          template_id: '3',
          name: 'StartupXYZ Negotiation',
          description: 'Deal negotiation workflow for StartupXYZ',
          team_id: 'team-2',
          deal_id: 'deal-2',
          status: 'draft',
          progress_percentage: 0,
          created_by: 'user-3',
          created_at: '2024-07-10T00:00:00Z'
        }
      ]

      // Mock workflow tasks
      const mockTasks: WorkflowTask[] = [
        {
          id: '1',
          workflow_id: '1',
          name: 'Review Financial Statements',
          description: 'Analyze last 3 years of financial statements',
          status: 'completed',
          priority: 'high',
          estimated_hours: 16,
          actual_hours: 14,
          assigned_to: 'user-1',
          depends_on: [],
          start_date: '2024-07-01T00:00:00Z',
          due_date: '2024-07-03T00:00:00Z',
          completion_date: '2024-07-02T00:00:00Z'
        },
        {
          id: '2',
          workflow_id: '1',
          name: 'Cash Flow Analysis',
          description: 'Detailed cash flow projection and analysis',
          status: 'in_progress',
          priority: 'high',
          estimated_hours: 12,
          actual_hours: 8,
          assigned_to: 'user-2',
          depends_on: ['1'],
          start_date: '2024-07-03T00:00:00Z',
          due_date: '2024-07-05T00:00:00Z'
        },
        {
          id: '3',
          workflow_id: '1',
          name: 'Risk Assessment',
          description: 'Identify and assess financial risks',
          status: 'ready',
          priority: 'medium',
          estimated_hours: 8,
          assigned_to: 'user-3',
          depends_on: ['1', '2'],
          due_date: '2024-07-08T00:00:00Z'
        }
      ]

      // Mock automation rules
      const mockRules: AutomationRule[] = [
        {
          id: '1',
          name: 'Task Completion Notification',
          description: 'Send notification when critical tasks are completed',
          trigger_type: 'task_completed',
          trigger_conditions: { priority: 'critical' },
          actions: [
            {
              type: 'send_notification',
              parameters: { recipients: ['team_lead'], message: 'Critical task completed' }
            }
          ],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          execution_count: 15
        },
        {
          id: '2',
          name: 'Overdue Task Alert',
          description: 'Alert team when tasks become overdue',
          trigger_type: 'task_overdue',
          trigger_conditions: { days_overdue: 1 },
          actions: [
            {
              type: 'send_notification',
              parameters: { recipients: ['assignee', 'team_lead'], urgency: 'high' }
            }
          ],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          execution_count: 8
        }
      ]

      // Mock metrics
      const mockMetrics: WorkflowMetrics = {
        total_workflows: 25,
        active_workflows: 8,
        completed_workflows: 15,
        average_completion_time: 18.5,
        efficiency_score: 87,
        automation_usage: 65,
        bottleneck_tasks: ['Legal Review', 'Financial Analysis', 'Risk Assessment'],
        top_performing_templates: ['Financial Due Diligence', 'Legal Due Diligence']
      }

      setTemplates(mockTemplates)
      setWorkflows(mockWorkflows)
      setAutomationRules(mockRules)
      setSelectedWorkflow(mockWorkflows[0])
      setWorkflowTasks(mockTasks)
      setMetrics(mockMetrics)
      setLoading(false)
    }
  }, [userLoaded, orgLoaded])

  // Filtered workflows
  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || workflow.status === statusFilter

    return matchesSearch && matchesStatus
  })

  // Status colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'paused': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Task status colors
  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'ready': return 'bg-purple-100 text-purple-800'
      case 'pending': return 'bg-gray-100 text-gray-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'skipped': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Priority colors
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Complexity colors
  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-green-100 text-green-800'
      case 'moderate': return 'bg-yellow-100 text-yellow-800'
      case 'complex': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!userLoaded || !orgLoaded) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading workflows...</div>
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <p className="text-lg font-medium text-gray-900">Error loading workflows</p>
          <p className="text-gray-500">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflow Manager</h1>
          <p className="text-gray-600">Orchestrate workflows, automate processes, and track progress</p>
        </div>
        <div className="flex items-center space-x-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Import Template
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Import Workflow Template</DialogTitle>
                <DialogDescription>
                  Upload a workflow template from file or select from library.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Input type="file" accept=".json,.yaml,.yml" />
                <p className="text-sm text-gray-500">Or select from template library:</p>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose template" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="due_diligence">Due Diligence Standard</SelectItem>
                    <SelectItem value="integration">Post-Merger Integration</SelectItem>
                    <SelectItem value="compliance">Compliance Review</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Workflow</DialogTitle>
                <DialogDescription>
                  Start a new workflow from a template or create a custom workflow.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Workflow Name</Label>
                    <Input placeholder="Enter workflow name" />
                  </div>
                  <div>
                    <Label>Template</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select template" />
                      </SelectTrigger>
                      <SelectContent>
                        {templates.map((template) => (
                          <SelectItem key={template.id} value={template.id}>
                            {template.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea placeholder="Enter workflow description" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Team</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select team" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="team-1">TechCorp Acquisition Team</SelectItem>
                        <SelectItem value="team-2">Legal Operations</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Target End Date</Label>
                    <Input type="date" />
                  </div>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="workflows">Active Workflows</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Active Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search workflows..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Workflows List */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Workflow className="h-5 w-5 mr-2" />
                    Workflows ({filteredWorkflows.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-2 p-4">
                    {filteredWorkflows.map((workflow) => (
                      <div
                        key={workflow.id}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedWorkflow?.id === workflow.id
                            ? 'bg-blue-50 border-blue-200'
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => setSelectedWorkflow(workflow)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{workflow.name}</h3>
                            <p className="text-sm text-gray-500 mt-1">{workflow.description}</p>
                            <div className="flex items-center space-x-4 mt-3">
                              <Badge className={getStatusColor(workflow.status)}>
                                {workflow.status}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                {workflow.progress_percentage}% complete
                              </span>
                            </div>
                            <Progress value={workflow.progress_percentage} className="h-1 mt-2" />
                          </div>
                          <ChevronRight className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Workflow Details */}
            <div className="lg:col-span-2">
              {selectedWorkflow ? (
                <div className="space-y-6">
                  {/* Workflow Header */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="flex items-center">
                            <Workflow className="h-5 w-5 mr-2" />
                            {selectedWorkflow.name}
                          </CardTitle>
                          <CardDescription>{selectedWorkflow.description}</CardDescription>
                        </div>
                        <div className="flex items-center space-x-2">
                          {selectedWorkflow.status === 'active' && (
                            <Button variant="outline" size="sm">
                              <Pause className="h-4 w-4 mr-2" />
                              Pause
                            </Button>
                          )}
                          {selectedWorkflow.status === 'paused' && (
                            <Button variant="outline" size="sm">
                              <Play className="h-4 w-4 mr-2" />
                              Resume
                            </Button>
                          )}
                          {selectedWorkflow.status === 'draft' && (
                            <Button size="sm">
                              <Play className="h-4 w-4 mr-2" />
                              Start
                            </Button>
                          )}
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="outline" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                              <DropdownMenuItem>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit Workflow
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Copy className="h-4 w-4 mr-2" />
                                Duplicate
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Download className="h-4 w-4 mr-2" />
                                Export
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-600">
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm font-medium text-gray-500">Status</p>
                          <Badge className={getStatusColor(selectedWorkflow.status)}>
                            {selectedWorkflow.status}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-500">Progress</p>
                          <p className="text-sm text-gray-900">{selectedWorkflow.progress_percentage}%</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-500">Target End Date</p>
                          <p className="text-sm text-gray-900">
                            {selectedWorkflow.target_end_date
                              ? new Date(selectedWorkflow.target_end_date).toLocaleDateString()
                              : 'Not set'
                            }
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-500">Created</p>
                          <p className="text-sm text-gray-900">
                            {new Date(selectedWorkflow.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <Progress value={selectedWorkflow.progress_percentage} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>

                  {/* Workflow Tasks */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle>Workflow Tasks</CardTitle>
                        <Button size="sm">
                          <Plus className="h-4 w-4 mr-2" />
                          Add Task
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {workflowTasks.map((task, index) => (
                          <div key={task.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-sm font-medium text-gray-600">
                              {index + 1}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <h4 className="font-medium text-gray-900">{task.name}</h4>
                                <Badge className={getTaskStatusColor(task.status)}>
                                  {task.status.replace('_', ' ')}
                                </Badge>
                                <Badge className={getPriorityColor(task.priority)}>
                                  {task.priority}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-500 mt-1">{task.description}</p>
                              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                                <span>{task.estimated_hours}h estimated</span>
                                {task.actual_hours && <span>{task.actual_hours}h actual</span>}
                                {task.due_date && (
                                  <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                                )}
                                {task.assigned_to && (
                                  <span>Assigned to: User {task.assigned_to}</span>
                                )}
                              </div>
                              {task.depends_on.length > 0 && (
                                <div className="flex items-center space-x-2 mt-2">
                                  <GitBranch className="h-4 w-4 text-gray-400" />
                                  <span className="text-sm text-gray-500">
                                    Depends on: {task.depends_on.join(', ')}
                                  </span>
                                </div>
                              )}
                            </div>
                            <div className="flex items-center space-x-2">
                              {task.status === 'completed' && (
                                <CheckCircle className="h-5 w-5 text-green-500" />
                              )}
                              {task.status === 'in_progress' && (
                                <Clock className="h-5 w-5 text-blue-500" />
                              )}
                              {task.status === 'failed' && (
                                <AlertCircle className="h-5 w-5 text-red-500" />
                              )}
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                  <DropdownMenuItem>Edit Task</DropdownMenuItem>
                                  <DropdownMenuItem>Assign to...</DropdownMenuItem>
                                  <DropdownMenuItem>Change Status</DropdownMenuItem>
                                  <DropdownMenuItem>Set Priority</DropdownMenuItem>
                                  <DropdownMenuItem className="text-red-600">
                                    Delete Task
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card>
                  <CardContent className="flex items-center justify-center h-64">
                    <div className="text-center">
                      <Workflow className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <p className="text-lg font-medium text-gray-900">Select a Workflow</p>
                      <p className="text-gray-500">Choose a workflow from the list to view details</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem>
                          <Play className="h-4 w-4 mr-2" />
                          Use Template
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Eye className="h-4 w-4 mr-2" />
                          Preview
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Copy className="h-4 w-4 mr-2" />
                          Duplicate
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Category</span>
                      <Badge className="capitalize">{template.category.replace('_', ' ')}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Complexity</span>
                      <Badge className={getComplexityColor(template.complexity)}>
                        {template.complexity}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Duration</span>
                      <span className="text-sm text-gray-900">{template.estimated_duration_days} days</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Tasks</span>
                      <span className="text-sm text-gray-900">{template.task_count}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Usage</span>
                      <span className="text-sm text-gray-900">{template.usage_count} times</span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <Button className="w-full" size="sm">
                      <Play className="h-4 w-4 mr-2" />
                      Create Workflow
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Automation Tab */}
        <TabsContent value="automation" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Automation Rules</h3>
              <p className="text-gray-500">Automate workflow actions and notifications</p>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Rule
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {automationRules.map((rule) => (
              <Card key={rule.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center">
                        <Zap className="h-5 w-5 mr-2" />
                        {rule.name}
                      </CardTitle>
                      <CardDescription>{rule.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch checked={rule.is_active} />
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit Rule
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Activity className="h-4 w-4 mr-2" />
                            View Executions
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Trigger</p>
                      <p className="text-sm text-gray-900 capitalize">
                        {rule.trigger_type.replace('_', ' ')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Actions</p>
                      <p className="text-sm text-gray-900">{rule.actions.length}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Executions</p>
                      <p className="text-sm text-gray-900">{rule.execution_count}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Status</p>
                      <Badge className={rule.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Workflow className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Workflows</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics?.total_workflows}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Activity className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Active</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics?.active_workflows}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Completed</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics?.completed_workflows}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Timer className="h-8 w-8 text-orange-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Avg. Time</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics?.average_completion_time}d</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Efficiency Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Efficiency Score</span>
                      <span className="text-sm text-gray-900">{metrics?.efficiency_score}%</span>
                    </div>
                    <Progress value={metrics?.efficiency_score} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Automation Usage</span>
                      <span className="text-sm text-gray-900">{metrics?.automation_usage}%</span>
                    </div>
                    <Progress value={metrics?.automation_usage} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Performing Templates</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {metrics?.top_performing_templates.map((template, index) => (
                    <div key={template} className="flex items-center justify-between">
                      <span className="text-sm text-gray-900">{template}</span>
                      <Badge>{index + 1}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Workflow Bottlenecks</CardTitle>
                <CardDescription>Tasks that commonly cause delays</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {metrics?.bottleneck_tasks.map((task, index) => (
                    <div key={task} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <AlertCircle className="h-5 w-5 text-red-500" />
                        <span className="text-sm font-medium text-gray-900">{task}</span>
                      </div>
                      <Button variant="outline" size="sm">
                        Analyze
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default WorkflowManager