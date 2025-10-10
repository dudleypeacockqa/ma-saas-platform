import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import {
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  Activity,
  ArrowUp,
  ArrowDown,
  Minus,
  ChevronRight
} from 'lucide-react';

interface IntegrationProject {
  id: string;
  project_name: string;
  integration_approach: string;
  status: string;
  overall_progress_percent?: number;
  overall_health_score?: number;
  target_synergies?: number;
  realized_synergies?: number;
  start_date: string;
  target_completion_date: string;
}

interface DashboardMetrics {
  project: IntegrationProject;
  milestones: {
    total: number;
    completed: number;
    completion_rate: number;
  };
  tasks: {
    total: number;
    completed: number;
    in_progress: number;
    at_risk: number;
  };
  synergies: {
    total_target: number;
    total_realized: number;
    capture_rate: number;
    count: number;
  };
  budget: {
    total: number;
    spent: number;
    remaining: number;
    utilization_rate: number;
  };
  risks: {
    critical: number;
    high: number;
    total_open: number;
  };
  issues: {
    urgent: number;
    total_open: number;
  };
  health: {
    status: string;
    is_on_track: boolean;
    overall_progress: number;
    current_phase: string;
  };
}

export default function IntegrationDashboard() {
  const { organization } = useOrganization();
  const [projects, setProjects] = useState<IntegrationProject[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id) {
      fetchProjects();
    }
  }, [organization?.id]);

  useEffect(() => {
    if (selectedProjectId) {
      fetchDashboard(selectedProjectId);
    }
  }, [selectedProjectId]);

  const fetchProjects = async () => {
    try:
      const response = await fetch(`${import.meta.env.VITE_API_URL}/integration/projects`, {
        headers: {
          'Authorization': `Bearer ${await organization?.getToken()}`,
          'X-Organization-ID': organization?.id || ''
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data);
        if (data.length > 0 && !selectedProjectId) {
          setSelectedProjectId(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboard = async (projectId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/dashboard`, {
        headers: {
          'Authorization': `Bearer ${await organization?.getToken()}`,
          'X-Organization-ID': organization?.id || ''
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'green': return 'bg-green-100 text-green-800';
      case 'yellow': return 'bg-yellow-100 text-yellow-800';
      case 'red': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, string> = {
      'pre_closing': 'Pre-Closing',
      'day_1': 'Day 1',
      'day_30': 'Day 30',
      'day_100': 'Day 100',
      'month_6': '6 Months',
      'month_12': '12 Months',
      'month_24': '24 Months'
    };
    return labels[phase] || phase;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Integration Projects</h3>
          <p className="mt-1 text-sm text-gray-500">
            Create an integration project for a closed deal to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Project Selector */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <label htmlFor="project-select" className="block text-sm font-medium text-gray-700 mb-2">
              Integration Project
            </label>
            <select
              id="project-select"
              value={selectedProjectId || ''}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="block w-full max-w-md rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.project_name} - {project.status}
                </option>
              ))}
            </select>
          </div>

          {dashboardData && (
            <div className="flex items-center space-x-3">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(dashboardData.health.status)}`}>
                {dashboardData.health.is_on_track ? (
                  <CheckCircle className="w-4 h-4 mr-1" />
                ) : (
                  <AlertTriangle className="w-4 h-4 mr-1" />
                )}
                {dashboardData.health.is_on_track ? 'On Track' : 'At Risk'}
              </span>
            </div>
          )}
        </div>
      </div>

      {dashboardData && (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Overall Progress */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Activity className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Overall Progress
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {dashboardData.health.overall_progress}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${dashboardData.health.overall_progress}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Synergy Capture */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Synergy Capture
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {dashboardData.synergies.capture_rate?.toFixed(1) || 0}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    {formatCurrency(dashboardData.synergies.total_realized)} of {formatCurrency(dashboardData.synergies.total_target)}
                  </p>
                </div>
              </div>
            </div>

            {/* Budget Utilization */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Budget Utilization
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {dashboardData.budget.utilization_rate?.toFixed(0) || 0}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    {formatCurrency(dashboardData.budget.remaining)} remaining
                  </p>
                </div>
              </div>
            </div>

            {/* Open Issues */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className={`h-6 w-6 ${dashboardData.issues.urgent > 0 ? 'text-red-600' : 'text-gray-400'}`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Open Issues
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {dashboardData.issues.total_open}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-2">
                  <p className="text-sm text-red-600">
                    {dashboardData.issues.urgent} urgent
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {/* Milestones & Tasks */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Execution Status</h3>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Milestones</span>
                    <span className="text-sm text-gray-500">
                      {dashboardData.milestones.completed} of {dashboardData.milestones.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${dashboardData.milestones.completion_rate}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Tasks</span>
                    <span className="text-sm text-gray-500">
                      {dashboardData.tasks.completed} of {dashboardData.tasks.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(dashboardData.tasks.completed / dashboardData.tasks.total) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-gray-500">In Progress</dt>
                      <dd className="text-lg font-semibold text-blue-600">{dashboardData.tasks.in_progress}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500">At Risk</dt>
                      <dd className="text-lg font-semibold text-yellow-600">{dashboardData.tasks.at_risk}</dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>

            {/* Risks */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Profile</h3>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
                    <span className="text-sm font-medium text-red-900">Critical Risks</span>
                  </div>
                  <span className="text-lg font-bold text-red-600">{dashboardData.risks.critical}</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2" />
                    <span className="text-sm font-medium text-yellow-900">High Risks</span>
                  </div>
                  <span className="text-lg font-bold text-yellow-600">{dashboardData.risks.high}</span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <Activity className="h-5 w-5 text-gray-600 mr-2" />
                    <span className="text-sm font-medium text-gray-900">Total Open Risks</span>
                  </div>
                  <span className="text-lg font-bold text-gray-600">{dashboardData.risks.total_open}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Synergy Details */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Synergy Realization</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-500 mb-1">Target Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(dashboardData.synergies.total_target)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-1">Realized Value</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(dashboardData.synergies.total_realized)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-1">Opportunities Identified</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {dashboardData.synergies.count}
                </p>
              </div>
            </div>

            <div className="mt-6">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(dashboardData.synergies.capture_rate || 0, 100)}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {dashboardData.synergies.capture_rate?.toFixed(1)}% capture rate
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button className="flex items-center justify-between p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm font-medium text-gray-700">View Tasks</span>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </button>

              <button className="flex items-center justify-between p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm font-medium text-gray-700">Synergy Tracker</span>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </button>

              <button className="flex items-center justify-between p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm font-medium text-gray-700">Risk Register</span>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </button>

              <button className="flex items-center justify-between p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <span className="text-sm font-medium text-gray-700">Timeline</span>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
