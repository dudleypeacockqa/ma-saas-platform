import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import {
  Columns,
  Plus,
  MoreVertical,
  Clock,
  CheckCircle,
  AlertTriangle,
  Circle
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
  assigned_to_id: string | null;
  due_date: string | null;
  completion_percentage: number;
  is_critical_path: boolean;
}

interface Workstream {
  id: string;
  workstream_name: string;
  workstream_type: string;
  status: string;
  progress_percentage: number;
  health_status: string;
  tasks_total: number;
  tasks_completed: number;
}

const TASK_STATUSES = [
  { value: 'not_started', label: 'Not Started', color: 'bg-gray-200 text-gray-800' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-blue-200 text-blue-800' },
  { value: 'at_risk', label: 'At Risk', color: 'bg-yellow-200 text-yellow-800' },
  { value: 'blocked', label: 'Blocked', color: 'bg-red-200 text-red-800' },
  { value: 'completed', label: 'Completed', color: 'bg-green-200 text-green-800' }
];

export default function WorkstreamBoard({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [workstreams, setWorkstreams] = useState<Workstream[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedWorkstream, setSelectedWorkstream] = useState<string | null>(null);
  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchWorkstreams();
    }
  }, [organization?.id, projectId]);

  useEffect(() => {
    if (selectedWorkstream && organization?.id) {
      fetchTasks(selectedWorkstream);
    }
  }, [selectedWorkstream, organization?.id]);

  const fetchWorkstreams = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/workstreams`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setWorkstreams(data);
        if (data.length > 0 && !selectedWorkstream) {
          setSelectedWorkstream(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching workstreams:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTasks = async (workstreamId: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/tasks?workstream_id=${workstreamId}`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const updateTaskStatus = async (taskId: string, newStatus: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/tasks/${taskId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          },
          body: JSON.stringify({ status: newStatus })
        }
      );

      if (response.ok) {
        if (selectedWorkstream) {
          fetchTasks(selectedWorkstream);
        }
        fetchWorkstreams(); // Refresh workstream stats
      }
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const handleDragStart = (task: Task) => {
    setDraggedTask(task);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (status: string) => {
    if (draggedTask && draggedTask.status !== status) {
      updateTaskStatus(draggedTask.id, status);
    }
    setDraggedTask(null);
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case 'medium':
        return <Circle className="h-4 w-4 text-yellow-600" />;
      case 'low':
        return <Circle className="h-4 w-4 text-green-600" />;
      default:
        return <Circle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'green':
        return 'bg-green-100 text-green-800';
      case 'yellow':
        return 'bg-yellow-100 text-yellow-800';
      case 'red':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTasksByStatus = (status: string) => {
    return tasks.filter(task => task.status === status);
  };

  const selectedWorkstreamData = workstreams.find(w => w.id === selectedWorkstream);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Workstream Selector */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Columns className="h-6 w-6 mr-2 text-indigo-600" />
            Workstream Board
          </h2>
          <button
            onClick={() => setShowCreateTaskModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Task
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {workstreams.map((workstream) => (
            <button
              key={workstream.id}
              onClick={() => setSelectedWorkstream(workstream.id)}
              className={`
                p-4 rounded-lg border-2 transition-all text-left
                ${selectedWorkstream === workstream.id
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 text-sm">{workstream.workstream_name}</h3>
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getHealthColor(workstream.health_status)}`}>
                  {workstream.health_status}
                </span>
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-indigo-600 h-1.5 rounded-full transition-all"
                    style={{ width: `${workstream.progress_percentage}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {workstream.tasks_completed}/{workstream.tasks_total} tasks
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Kanban Board */}
      {selectedWorkstreamData && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {selectedWorkstreamData.workstream_name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {selectedWorkstreamData.progress_percentage}% complete • {tasks.length} total tasks
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {TASK_STATUSES.map((status) => {
              const statusTasks = getTasksByStatus(status.value);

              return (
                <div
                  key={status.value}
                  className="flex flex-col bg-gray-50 rounded-lg p-4"
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(status.value)}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900 text-sm">{status.label}</h4>
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-xs font-medium text-gray-600">
                      {statusTasks.length}
                    </span>
                  </div>

                  <div className="space-y-3 flex-1">
                    {statusTasks.length === 0 ? (
                      <p className="text-xs text-gray-400 text-center py-4">No tasks</p>
                    ) : (
                      statusTasks.map((task) => (
                        <div
                          key={task.id}
                          draggable
                          onDragStart={() => handleDragStart(task)}
                          className={`
                            bg-white p-3 rounded-lg border border-gray-200 shadow-sm
                            cursor-move hover:shadow-md transition-shadow
                            ${task.is_critical_path ? 'border-l-4 border-l-red-500' : ''}
                          `}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <p className="text-sm font-medium text-gray-900 flex-1 pr-2">
                              {task.title}
                            </p>
                            {getPriorityIcon(task.priority)}
                          </div>

                          {task.completion_percentage > 0 && (
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-1">
                                <div
                                  className="bg-indigo-600 h-1 rounded-full"
                                  style={{ width: `${task.completion_percentage}%` }}
                                />
                              </div>
                            </div>
                          )}

                          {task.due_date && (
                            <div className="flex items-center mt-2 text-xs text-gray-500">
                              <Clock className="h-3 w-3 mr-1" />
                              {new Date(task.due_date).toLocaleDateString()}
                            </div>
                          )}

                          {task.is_critical_path && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mt-2">
                              Critical Path
                            </span>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Create Task Modal - Placeholder */}
      {showCreateTaskModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <h3 className="text-lg font-semibold mb-4">Create New Task</h3>
            <p className="text-gray-600 mb-4">Task creation form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateTaskModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowCreateTaskModal(false);
                  if (selectedWorkstream) {
                    fetchTasks(selectedWorkstream);
                  }
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
