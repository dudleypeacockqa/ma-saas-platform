/**
 * Due Diligence Dashboard
 * Main orchestration UI for managing due diligence processes
 * Supports checklist management, document tracking, risk assessment, and team collaboration
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Tooltip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Assignment as AssignmentIcon,
  Folder as FolderIcon,
  People as PeopleIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

interface Deal {
  id: string;
  name: string;
  status: string;
}

interface DueDiligenceProcess {
  id: string;
  deal_id: string;
  name: string;
  checklist_id: string;
  checklist_name: string;
  status: string;
  progress_percentage: number;
  items_total: number;
  items_completed: number;
  documents_requested: number;
  documents_received: number;
  risk_level: string;
  target_completion_date: string;
  lead_reviewer_id: string;
  lead_reviewer_name: string;
  created_at: string;
  updated_at: string;
}

interface ProcessStats {
  total_processes: number;
  in_progress: number;
  completed: number;
  overdue: number;
  avg_completion: number;
  high_risk_count: number;
  documents_pending: number;
}

interface RiskSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

const DueDiligenceDashboard: React.FC = () => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Data states
  const [processes, setProcesses] = useState<DueDiligenceProcess[]>([]);
  const [stats, setStats] = useState<ProcessStats | null>(null);
  const [riskSummary, setRiskSummary] = useState<RiskSummary | null>(null);
  const [deals, setDeals] = useState<Deal[]>([]);

  // UI states
  const [selectedProcess, setSelectedProcess] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuProcessId, setMenuProcessId] = useState<string | null>(null);

  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');

  // Fetch processes
  const fetchProcesses = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const queryParams = new URLSearchParams();
      if (statusFilter !== 'all') queryParams.append('status', statusFilter);
      if (riskFilter !== 'all') queryParams.append('risk_level', riskFilter);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes?${queryParams}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch DD processes');

      const data = await response.json();
      setProcesses(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching processes:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/stats`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
        setRiskSummary(data.risk_summary);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Fetch deals for process creation
  const fetchDeals = async () => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/deals?status=active`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      }
    } catch (err) {
      console.error('Error fetching deals:', err);
    }
  };

  useEffect(() => {
    fetchProcesses();
    fetchStats();
    fetchDeals();
  }, [statusFilter, riskFilter]);

  // Handlers
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, processId: string) => {
    setAnchorEl(event.currentTarget);
    setMenuProcessId(processId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuProcessId(null);
  };

  const handleCreateProcess = () => {
    setCreateDialogOpen(true);
  };

  const handleViewProcess = (processId: string) => {
    setSelectedProcess(processId);
    // Navigate to detailed process view
    window.location.href = `/due-diligence/${processId}`;
  };

  const handleExportReport = async (processId: string) => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/export`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dd-report-${processId}.pdf`;
        a.click();
      }
    } catch (err) {
      console.error('Error exporting report:', err);
    }
    handleMenuClose();
  };

  // Get status color
  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
      'not_started': 'default',
      'in_progress': 'primary',
      'under_review': 'warning',
      'completed': 'success',
      'on_hold': 'error',
    };
    return colors[status] || 'default';
  };

  // Get risk color
  const getRiskColor = (risk: string) => {
    const colors: Record<string, string> = {
      'critical': '#d32f2f',
      'high': '#f57c00',
      'medium': '#fbc02d',
      'low': '#388e3c',
      'none': '#757575',
    };
    return colors[risk] || '#757575';
  };

  // Render statistics cards
  const renderStatsCards = () => {
    if (!stats) return null;

    const cards = [
      { label: 'Total Processes', value: stats.total_processes, icon: <AssignmentIcon />, color: '#1976d2' },
      { label: 'In Progress', value: stats.in_progress, icon: <TimelineIcon />, color: '#0288d1' },
      { label: 'Completed', value: stats.completed, icon: <CheckIcon />, color: '#388e3c' },
      { label: 'High Risk', value: stats.high_risk_count, icon: <WarningIcon />, color: '#f57c00' },
    ];

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ color: card.color, mr: 1 }}>{card.icon}</Box>
                  <Typography variant="h4" component="div">
                    {card.value}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {card.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  // Render process list
  const renderProcessList = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      );
    }

    if (processes.length === 0) {
      return (
        <Alert severity="info">
          No due diligence processes found. Create one to get started.
        </Alert>
      );
    }

    return (
      <List>
        {processes.map((process) => (
          <React.Fragment key={process.id}>
            <ListItem
              sx={{
                border: '1px solid #e0e0e0',
                borderRadius: 1,
                mb: 2,
                cursor: 'pointer',
                '&:hover': { bgcolor: '#f5f5f5' },
              }}
            >
              <ListItemIcon>
                <FolderIcon sx={{ color: getRiskColor(process.risk_level) }} />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6">{process.name}</Typography>
                    <Chip
                      label={process.status.replace('_', ' ').toUpperCase()}
                      color={getStatusColor(process.status)}
                      size="small"
                    />
                    <Chip
                      label={`Risk: ${process.risk_level.toUpperCase()}`}
                      size="small"
                      sx={{ bgcolor: getRiskColor(process.risk_level), color: 'white' }}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Checklist: {process.checklist_name} | Lead: {process.lead_reviewer_name}
                    </Typography>
                    <Box sx={{ mt: 1, mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption">
                          Progress: {process.items_completed}/{process.items_total} items
                        </Typography>
                        <Typography variant="caption">
                          {process.progress_percentage.toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={process.progress_percentage}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Documents: {process.documents_received}/{process.documents_requested} |
                      Target: {new Date(process.target_completion_date).toLocaleDateString()}
                    </Typography>
                  </Box>
                }
              />
              <IconButton onClick={(e) => handleMenuOpen(e, process.id)}>
                <MoreIcon />
              </IconButton>
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Due Diligence Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchProcesses}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateProcess}
          >
            New DD Process
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {renderStatsCards()}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FilterIcon />
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              label="Status"
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="not_started">Not Started</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="under_review">Under Review</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="on_hold">On Hold</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Risk Level</InputLabel>
            <Select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              label="Risk Level"
            >
              <MenuItem value="all">All Risk Levels</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="All Processes" />
        <Tab label="In Progress" />
        <Tab label="Completed" />
        <Tab label="High Priority" />
      </Tabs>

      {/* Process List */}
      <Card>
        <CardContent>
          {renderProcessList()}
        </CardContent>
      </Card>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => menuProcessId && handleViewProcess(menuProcessId)}>
          View Details
        </MenuItem>
        <MenuItem onClick={() => menuProcessId && handleExportReport(menuProcessId)}>
          <DownloadIcon sx={{ mr: 1 }} fontSize="small" />
          Export Report
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>Archive</MenuItem>
      </Menu>

      {/* Create Process Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New DD Process</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Initialize a new due diligence process for a deal
          </Typography>
          {/* Form fields would go here */}
          <Alert severity="info">
            Form implementation coming soon. Will include deal selection, checklist template, and team assignment.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled>Create Process</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DueDiligenceDashboard;
