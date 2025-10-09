import React, { useState, useEffect } from 'react'
import { useUser, useOrganization } from '@clerk/clerk-react'
import {
  Users,
  Plus,
  Settings,
  Calendar,
  MessageSquare,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  BarChart3,
  Filter,
  Search,
  MoreHorizontal,
  ChevronRight,
  Edit,
  Trash2,
  UserPlus,
  FileText,
  Video,
  Bell,
  Star,
  ArrowUp,
  ArrowDown
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

// Types
interface Team {
  id: string
  name: string
  description?: string
  team_type: 'deal_team' | 'functional' | 'project' | 'temporary'
  status: 'forming' | 'active' | 'on_hold' | 'completed' | 'disbanded'
  team_lead_id: string
  deal_id?: string
  member_count: number
  budget_allocated?: number
  budget_used?: number
  budget_limit?: number
  target_completion_date?: string
  created_at: string
  updated_at?: string
}

interface TeamMember {
  id: string
  team_id: string
  user_id: string
  role: 'lead' | 'admin' | 'member' | 'consultant' | 'observer'
  hourly_rate?: number
  expected_hours_per_week?: number
  actual_hours_logged?: number
  start_date?: string
  end_date?: string
  status: string
  joined_at: string
}

interface Task {
  id: string
  team_id: string
  title: string
  description?: string
  assigned_to_id?: string
  status: 'todo' | 'in_progress' | 'review' | 'completed' | 'blocked'
  due_date?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  estimated_hours?: number
  actual_hours?: number
  progress_percentage: number
  created_at: string
  updated_at?: string
}

interface TeamMetrics {
  team_productivity_score: number
  task_completion_rate: number
  budget_utilization: number
  average_task_completion_time: number
  member_performance_scores: Record<string, number>
  period_start: string
  period_end: string
}

const TeamDashboard: React.FC = () => {
  const { user, isLoaded: userLoaded } = useUser()
  const { organization, isLoaded: orgLoaded } = useOrganization()

  // State
  const [teams, setTeams] = useState<Team[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [teamTasks, setTeamTasks] = useState<Task[]>([])
  const [teamMetrics, setTeamMetrics] = useState<TeamMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [activeTab, setActiveTab] = useState('overview')

  // Mock data for development
  useEffect(() => {
    if (userLoaded && orgLoaded) {
      // Mock teams data
      const mockTeams: Team[] = [
        {
          id: '1',
          name: 'TechCorp Acquisition',
          description: 'Due diligence and negotiation for TechCorp acquisition',
          team_type: 'deal_team',
          status: 'active',
          team_lead_id: '1',
          deal_id: 'deal-1',
          member_count: 8,
          budget_allocated: 250000,
          budget_used: 175000,
          budget_limit: 300000,
          target_completion_date: '2024-12-31',
          created_at: '2024-01-15T00:00:00Z'
        },
        {
          id: '2',
          name: 'Legal Operations',
          description: 'Ongoing legal support and compliance',
          team_type: 'functional',
          status: 'active',
          team_lead_id: '2',
          member_count: 5,
          budget_allocated: 120000,
          budget_used: 45000,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '3',
          name: 'Market Research Initiative',
          description: 'Q3 market research and analysis project',
          team_type: 'project',
          status: 'forming',
          team_lead_id: '3',
          member_count: 3,
          target_completion_date: '2024-09-30',
          created_at: '2024-07-01T00:00:00Z'
        }
      ]

      // Mock team members
      const mockMembers: TeamMember[] = [
        {
          id: '1',
          team_id: '1',
          user_id: '1',
          role: 'lead',
          hourly_rate: 250,
          expected_hours_per_week: 40,
          actual_hours_logged: 145,
          status: 'active',
          joined_at: '2024-01-15T00:00:00Z'
        },
        {
          id: '2',
          team_id: '1',
          user_id: '2',
          role: 'member',
          hourly_rate: 180,
          expected_hours_per_week: 35,
          actual_hours_logged: 120,
          status: 'active',
          joined_at: '2024-01-20T00:00:00Z'
        }
      ]

      // Mock tasks
      const mockTasks: Task[] = [
        {
          id: '1',
          team_id: '1',
          title: 'Financial Due Diligence Review',
          description: 'Complete financial analysis of target company',
          assigned_to_id: '1',
          status: 'in_progress',
          due_date: '2024-08-15T00:00:00Z',
          priority: 'high',
          estimated_hours: 40,
          actual_hours: 25,
          progress_percentage: 60,
          created_at: '2024-07-01T00:00:00Z'
        },
        {
          id: '2',
          team_id: '1',
          title: 'Legal Document Review',
          description: 'Review all legal documents and contracts',
          assigned_to_id: '2',
          status: 'completed',
          due_date: '2024-07-30T00:00:00Z',
          priority: 'medium',
          estimated_hours: 20,
          actual_hours: 18,
          progress_percentage: 100,
          created_at: '2024-07-01T00:00:00Z'
        }
      ]

      // Mock metrics
      const mockMetrics: TeamMetrics = {
        team_productivity_score: 87.5,
        task_completion_rate: 0.75,
        budget_utilization: 0.70,
        average_task_completion_time: 4.2,
        member_performance_scores: {
          '1': 92,
          '2': 88,
          '3': 85
        },
        period_start: '2024-07-01',
        period_end: '2024-07-31'
      }

      setTeams(mockTeams)
      setSelectedTeam(mockTeams[0])
      setTeamMembers(mockMembers)
      setTeamTasks(mockTasks)
      setTeamMetrics(mockMetrics)
      setLoading(false)
    }
  }, [userLoaded, orgLoaded])

  // Filtered teams
  const filteredTeams = teams.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || team.status === statusFilter
    const matchesType = typeFilter === 'all' || team.team_type === typeFilter

    return matchesSearch && matchesStatus && matchesType
  })

  // Team status colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'forming': return 'bg-blue-100 text-blue-800'
      case 'on_hold': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-gray-100 text-gray-800'
      case 'disbanded': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Task status colors
  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'review': return 'bg-purple-100 text-purple-800'
      case 'blocked': return 'bg-red-100 text-red-800'
      case 'todo': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Priority colors
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!userLoaded || !orgLoaded) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading teams...</div>
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <p className="text-lg font-medium text-gray-900">Error loading teams</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Team Management</h1>
          <p className="text-gray-600">Manage teams, track progress, and coordinate collaboration</p>
        </div>
        <div className="flex items-center space-x-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Team
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Team</DialogTitle>
                <DialogDescription>
                  Set up a new team for deal management, projects, or functional work.
                </DialogDescription>
              </DialogHeader>
              {/* Team creation form would go here */}
              <div className="grid gap-4 py-4">
                <Input placeholder="Team name" />
                <Input placeholder="Description" />
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Team type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="deal_team">Deal Team</SelectItem>
                    <SelectItem value="functional">Functional Team</SelectItem>
                    <SelectItem value="project">Project Team</SelectItem>
                    <SelectItem value="temporary">Temporary Team</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search teams..."
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
            <SelectItem value="forming">Forming</SelectItem>
            <SelectItem value="on_hold">On Hold</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="disbanded">Disbanded</SelectItem>
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="deal_team">Deal Team</SelectItem>
            <SelectItem value="functional">Functional</SelectItem>
            <SelectItem value="project">Project</SelectItem>
            <SelectItem value="temporary">Temporary</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Teams List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Teams ({filteredTeams.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-2 p-4">
                {filteredTeams.map((team) => (
                  <div
                    key={team.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedTeam?.id === team.id
                        ? 'bg-blue-50 border-blue-200'
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedTeam(team)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{team.name}</h3>
                        <p className="text-sm text-gray-500 mt-1">{team.description}</p>
                        <div className="flex items-center space-x-4 mt-3">
                          <Badge className={getStatusColor(team.status)}>
                            {team.status.replace('_', ' ')}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            {team.member_count} members
                          </span>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Team Details */}
        <div className="lg:col-span-2">
          {selectedTeam ? (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="members">Members</TabsTrigger>
                <TabsTrigger value="tasks">Tasks</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{selectedTeam.name}</CardTitle>
                        <CardDescription>{selectedTeam.description}</CardDescription>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit Team
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <UserPlus className="h-4 w-4 mr-2" />
                            Add Member
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Calendar className="h-4 w-4 mr-2" />
                            Schedule Meeting
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete Team
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm font-medium text-gray-500">Status</p>
                        <Badge className={getStatusColor(selectedTeam.status)}>
                          {selectedTeam.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Type</p>
                        <p className="text-sm text-gray-900 capitalize">
                          {selectedTeam.team_type.replace('_', ' ')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Members</p>
                        <p className="text-sm text-gray-900">{selectedTeam.member_count}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Created</p>
                        <p className="text-sm text-gray-900">
                          {new Date(selectedTeam.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    {selectedTeam.budget_allocated && (
                      <div className="mt-6">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm font-medium text-gray-500">Budget Utilization</p>
                          <p className="text-sm text-gray-900">
                            ${selectedTeam.budget_used?.toLocaleString()} / ${selectedTeam.budget_allocated.toLocaleString()}
                          </p>
                        </div>
                        <Progress
                          value={(selectedTeam.budget_used || 0) / selectedTeam.budget_allocated * 100}
                          className="h-2"
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center">
                        <CheckCircle className="h-8 w-8 text-green-500" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Completed Tasks</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {teamTasks.filter(t => t.status === 'completed').length}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center">
                        <Clock className="h-8 w-8 text-blue-500" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Active Tasks</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {teamTasks.filter(t => t.status === 'in_progress').length}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center">
                        <TrendingUp className="h-8 w-8 text-purple-500" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Team Score</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {teamMetrics?.team_productivity_score}%
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Members Tab */}
              <TabsContent value="members">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Team Members ({teamMembers.length})</CardTitle>
                      <Button size="sm">
                        <UserPlus className="h-4 w-4 mr-2" />
                        Add Member
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {teamMembers.map((member) => (
                        <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div className="flex items-center space-x-4">
                            <Avatar>
                              <AvatarImage src="" />
                              <AvatarFallback>
                                {member.user_id.slice(0, 2).toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium text-gray-900">User {member.user_id}</p>
                              <p className="text-sm text-gray-500 capitalize">{member.role}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">
                                {member.actual_hours_logged}h logged
                              </p>
                              <p className="text-sm text-gray-500">
                                ${member.hourly_rate}/hr
                              </p>
                            </div>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="outline" size="sm">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent>
                                <DropdownMenuItem>Edit Role</DropdownMenuItem>
                                <DropdownMenuItem>View Profile</DropdownMenuItem>
                                <DropdownMenuItem className="text-red-600">
                                  Remove from Team
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Tasks Tab */}
              <TabsContent value="tasks">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Team Tasks ({teamTasks.length})</CardTitle>
                      <Button size="sm">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Task
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Task</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Progress</TableHead>
                          <TableHead>Due Date</TableHead>
                          <TableHead>Assigned To</TableHead>
                          <TableHead></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {teamTasks.map((task) => (
                          <TableRow key={task.id}>
                            <TableCell>
                              <div>
                                <p className="font-medium text-gray-900">{task.title}</p>
                                <p className="text-sm text-gray-500">{task.description}</p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge className={getTaskStatusColor(task.status)}>
                                {task.status.replace('_', ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge className={getPriorityColor(task.priority)}>
                                {task.priority}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <Progress value={task.progress_percentage} className="h-2 w-16" />
                                <span className="text-sm text-gray-500">{task.progress_percentage}%</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
                            </TableCell>
                            <TableCell>
                              <Avatar className="h-6 w-6">
                                <AvatarFallback className="text-xs">
                                  {task.assigned_to_id?.slice(0, 2).toUpperCase()}
                                </AvatarFallback>
                              </Avatar>
                            </TableCell>
                            <TableCell>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                  <DropdownMenuItem>Edit Task</DropdownMenuItem>
                                  <DropdownMenuItem>Assign to...</DropdownMenuItem>
                                  <DropdownMenuItem>Change Priority</DropdownMenuItem>
                                  <DropdownMenuItem className="text-red-600">
                                    Delete Task
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Metrics Tab */}
              <TabsContent value="metrics">
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Team Performance Metrics</CardTitle>
                      <CardDescription>
                        Performance analysis for {teamMetrics?.period_start} to {teamMetrics?.period_end}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-500">Productivity Score</p>
                              <p className="text-2xl font-bold text-gray-900">
                                {teamMetrics?.team_productivity_score}%
                              </p>
                            </div>
                            <TrendingUp className="h-8 w-8 text-green-500" />
                          </div>
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-500">Task Completion</p>
                              <p className="text-2xl font-bold text-gray-900">
                                {Math.round((teamMetrics?.task_completion_rate || 0) * 100)}%
                              </p>
                            </div>
                            <CheckCircle className="h-8 w-8 text-blue-500" />
                          </div>
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-500">Budget Utilization</p>
                              <p className="text-2xl font-bold text-gray-900">
                                {Math.round((teamMetrics?.budget_utilization || 0) * 100)}%
                              </p>
                            </div>
                            <BarChart3 className="h-8 w-8 text-purple-500" />
                          </div>
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-500">Avg. Completion Time</p>
                              <p className="text-2xl font-bold text-gray-900">
                                {teamMetrics?.average_task_completion_time}d
                              </p>
                            </div>
                            <Clock className="h-8 w-8 text-orange-500" />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Member Performance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(teamMetrics?.member_performance_scores || {}).map(([userId, score]) => (
                          <div key={userId} className="flex items-center justify-between p-4 border rounded-lg">
                            <div className="flex items-center space-x-4">
                              <Avatar>
                                <AvatarFallback>{userId.slice(0, 2).toUpperCase()}</AvatarFallback>
                              </Avatar>
                              <div>
                                <p className="font-medium text-gray-900">User {userId}</p>
                                <p className="text-sm text-gray-500">Team Member</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-4">
                              <Progress value={score} className="h-2 w-24" />
                              <span className="text-lg font-bold text-gray-900">{score}%</span>
                              {score >= 90 ? (
                                <Star className="h-5 w-5 text-yellow-500" />
                              ) : score >= 85 ? (
                                <ArrowUp className="h-5 w-5 text-green-500" />
                              ) : (
                                <ArrowDown className="h-5 w-5 text-red-500" />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Settings Tab */}
              <TabsContent value="settings">
                <Card>
                  <CardHeader>
                    <CardTitle>Team Settings</CardTitle>
                    <CardDescription>Manage team configuration and preferences</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Team Information</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-gray-700">Team Name</label>
                          <Input value={selectedTeam.name} className="mt-1" />
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-700">Description</label>
                          <Input value={selectedTeam.description || ''} className="mt-1" />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Notifications</h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Task assignments</span>
                          <Button variant="outline" size="sm">Configure</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Meeting reminders</span>
                          <Button variant="outline" size="sm">Configure</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Status updates</span>
                          <Button variant="outline" size="sm">Configure</Button>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Integrations</h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Slack notifications</span>
                          <Button variant="outline" size="sm">Connect</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Microsoft Teams</span>
                          <Button variant="outline" size="sm">Connect</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">Google Calendar</span>
                          <Button variant="outline" size="sm">Connect</Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64">
                <div className="text-center">
                  <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-900">Select a Team</p>
                  <p className="text-gray-500">Choose a team from the list to view details</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default TeamDashboard