/**
 * Task Management Component for Due Diligence
 * Kanban-style task board for DD workflow management
 * Features: task assignment, status tracking, dependencies, time tracking
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Tooltip,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  AvatarGroup,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Flag as FlagIcon,
  AccessTime as TimeIcon,
  Assignment as AssignmentIcon,
  Comment as CommentIcon,
  AttachFile as AttachIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';

interface TaskManagementProps {
  processId: string;
  readOnly?: boolean;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_to: string[];
  assigned_to_names: string[];
  created_by: string;
  created_by_name: string;
  due_date: string;
  created_at: string;
  updated_at: string;
  checklist_item_id: string | null;
  comments_count: number;
  attachments_count: number;
  time_estimate: number | null;
  time_spent: number | null;
  tags: string[];
}

interface Column {
  id: 'todo' | 'in_progress' | 'review' | 'done';
  title: string;
  color: string;
  tasks: Task[];
}

const TaskManagement: React.FC<TaskManagementProps> = ({ processId, readOnly = false }) => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [columns, setColumns] = useState<Column[]>([
    { id: 'todo', title: 'To Do', color: '#757575', tasks: [] },
    { id: 'in_progress', title: 'In Progress', color: '#1976d2', tasks: [] },
    { id: 'review', title: 'Review', color: '#f57c00', tasks: [] },
    { id: 'done', title: 'Done', color: '#388e3c', tasks: [] },
  ]);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Form states
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'critical',
    due_date: '',
    assigned_to: [] as string[],
    time_estimate: '',
  });

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/tasks`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch tasks');

      const data = await response.json();
      setTasks(data);

      // Organize tasks into columns
      organizeTasksIntoColumns(data);

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  // Organize tasks into columns
  const organizeTasksIntoColumns = (tasksList: Task[]) => {
    const newColumns = columns.map(column => ({
      ...column,
      tasks: tasksList.filter(task => task.status === column.id),
    }));
    setColumns(newColumns);
  };

  useEffect(() => {
    fetchTasks();
  }, [processId]);

  // Create task
  const handleCreateTask = async () => {
    try {
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/tasks`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...newTask,
            time_estimate: newTask.time_estimate ? parseFloat(newTask.time_estimate) : null,
          }),
        }
      );

      if (!response.ok) throw new Error('Failed to create task');

      setCreateDialogOpen(false);
      setNewTask({
        title: '',
        description: '',
        priority: 'medium',
        due_date: '',
        assigned_to: [],
        time_estimate: '',
      });
      await fetchTasks();
    } catch (err) {
      console.error('Error creating task:', err);
    }
  };

  // Update task status
  const handleUpdateTaskStatus = async (taskId: string, newStatus: 'todo' | 'in_progress' | 'review' | 'done') => {
    if (readOnly) return;

    try {
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/tasks/${taskId}/status`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) throw new Error('Failed to update task status');

      await fetchTasks();
    } catch (err) {
      console.error('Error updating task status:', err);
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    const colors = {
      low: '#757575',
      medium: '#1976d2',
      high: '#f57c00',
      critical: '#d32f2f',
    };
    return colors[priority as keyof typeof colors] || '#757575';
  };

  // Render task card
  const renderTaskCard = (task: Task) => {
    const isOverdue = new Date(task.due_date) < new Date() && task.status !== 'done';

    return (
      <Card
        key={task.id}
        sx={{
          mb: 2,
          cursor: readOnly ? 'default' : 'move',
          borderLeft: `4px solid ${getPriorityColor(task.priority)}`,
          '&:hover': {
            boxShadow: 3,
          },
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                {task.title}
              </Typography>
              {task.description && (
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                  {task.description}
                </Typography>
              )}
            </Box>
            <IconButton size="small">
              <MoreIcon fontSize="small" />
            </IconButton>
          </Box>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5, mb: 1, flexWrap: 'wrap' }}>
              {task.tags.map((tag, index) => (
                <Chip key={index} label={tag} size="small" />
              ))}
            </Box>
          )}

          {/* Due date and priority */}
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Chip
              label={task.priority.toUpperCase()}
              size="small"
              sx={{
                bgcolor: getPriorityColor(task.priority),
                color: 'white',
              }}
            />
            {task.due_date && (
              <Chip
                icon={<TimeIcon />}
                label={new Date(task.due_date).toLocaleDateString()}
                size="small"
                color={isOverdue ? 'error' : 'default'}
              />
            )}
          </Box>

          {/* Time tracking */}
          {(task.time_estimate || task.time_spent) && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Time: {task.time_spent || 0}h / {task.time_estimate}h
              </Typography>
              <LinearProgress
                variant="determinate"
                value={task.time_estimate ? ((task.time_spent || 0) / task.time_estimate) * 100 : 0}
                sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
              />
            </Box>
          )}

          {/* Footer */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
            {/* Assigned users */}
            <AvatarGroup max={3} sx={{ justifyContent: 'flex-start' }}>
              {task.assigned_to_names.map((name, index) => (
                <Tooltip key={index} title={name}>
                  <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                    {name.charAt(0).toUpperCase()}
                  </Avatar>
                </Tooltip>
              ))}
            </AvatarGroup>

            {/* Activity indicators */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              {task.comments_count > 0 && (
                <Tooltip title={`${task.comments_count} comments`}>
                  <Chip
                    icon={<CommentIcon />}
                    label={task.comments_count}
                    size="small"
                    variant="outlined"
                  />
                </Tooltip>
              )}
              {task.attachments_count > 0 && (
                <Tooltip title={`${task.attachments_count} attachments`}>
                  <Chip
                    icon={<AttachIcon />}
                    label={task.attachments_count}
                    size="small"
                    variant="outlined"
                  />
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Status movement buttons */}
          {!readOnly && (
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              {task.status !== 'todo' && (
                <Button
                  size="small"
                  onClick={() => {
                    const statusOrder: ('todo' | 'in_progress' | 'review' | 'done')[] = ['todo', 'in_progress', 'review', 'done'];
                    const currentIndex = statusOrder.indexOf(task.status);
                    if (currentIndex > 0) {
                      handleUpdateTaskStatus(task.id, statusOrder[currentIndex - 1]);
                    }
                  }}
                >
                  ← Move Back
                </Button>
              )}
              {task.status !== 'done' && (
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => {
                    const statusOrder: ('todo' | 'in_progress' | 'review' | 'done')[] = ['todo', 'in_progress', 'review', 'done'];
                    const currentIndex = statusOrder.indexOf(task.status);
                    if (currentIndex < statusOrder.length - 1) {
                      handleUpdateTaskStatus(task.id, statusOrder[currentIndex + 1]);
                    }
                  }}
                >
                  Move Forward →
                </Button>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  // Render column
  const renderColumn = (column: Column) => (
    <Box
      key={column.id}
      sx={{
        flex: 1,
        minWidth: 300,
        bgcolor: '#f5f5f5',
        borderRadius: 1,
        p: 2,
      }}
    >
      {/* Column Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: column.color,
            }}
          />
          <Typography variant="h6">{column.title}</Typography>
          <Chip label={column.tasks.length} size="small" />
        </Box>
      </Box>

      {/* Tasks */}
      <Box sx={{ minHeight: 200 }}>
        {column.tasks.map(renderTaskCard)}
      </Box>
    </Box>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Task Management</Typography>
        {!readOnly && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            New Task
          </Button>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Kanban Board */}
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2 }}>
        {columns.map(renderColumn)}
      </Box>

      {/* Create Task Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Title"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as any })}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Due Date"
                value={newTask.due_date}
                onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Time Estimate (hours)"
                value={newTask.time_estimate}
                onChange={(e) => setNewTask({ ...newTask, time_estimate: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateTask}
            disabled={!newTask.title.trim()}
          >
            Create Task
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskManagement;
