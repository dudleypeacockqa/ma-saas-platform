/**
 * Risk Assessment Dashboard
 * Comprehensive risk analysis and visualization for due diligence
 * Features: risk scoring, heat maps, mitigation tracking, executive summary
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

interface RiskAssessmentProps {
  processId: string;
  readOnly?: boolean;
}

interface RiskCategory {
  category: string;
  score: number;
  level: 'critical' | 'high' | 'medium' | 'low' | 'none';
  issues_count: number;
  mitigations_count: number;
  trend: 'up' | 'down' | 'stable';
}

interface RiskIssue {
  id: string;
  category: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  probability: number;
  impact: number;
  risk_score: number;
  status: string;
  identified_date: string;
  identified_by: string;
  mitigation_strategy: string | null;
  residual_risk: number | null;
  owner: string | null;
  target_resolution_date: string | null;
}

interface RiskSummary {
  overall_risk_score: number;
  overall_risk_level: 'critical' | 'high' | 'medium' | 'low';
  deal_recommendation: string;
  confidence_level: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  mitigated_issues: number;
  categories: RiskCategory[];
}

const RiskAssessment: React.FC<RiskAssessmentProps> = ({ processId, readOnly = false }) => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [riskSummary, setRiskSummary] = useState<RiskSummary | null>(null);
  const [riskIssues, setRiskIssues] = useState<RiskIssue[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Dialog states
  const [addIssueDialogOpen, setAddIssueDialogOpen] = useState(false);
  const [newIssue, setNewIssue] = useState({
    category: 'financial',
    title: '',
    description: '',
    severity: 'medium' as 'critical' | 'high' | 'medium' | 'low',
    probability: 50,
    impact: 50,
  });

  // Fetch risk summary
  const fetchRiskSummary = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/risk-summary`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch risk summary');

      const data = await response.json();
      setRiskSummary(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching risk summary:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch risk issues
  const fetchRiskIssues = async () => {
    try {
      const token = await getToken();

      const queryParams = new URLSearchParams();
      if (selectedCategory !== 'all') {
        queryParams.append('category', selectedCategory);
      }

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/risk-issues?${queryParams}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRiskIssues(data);
      }
    } catch (err) {
      console.error('Error fetching risk issues:', err);
    }
  };

  useEffect(() => {
    fetchRiskSummary();
    fetchRiskIssues();
  }, [processId, selectedCategory]);

  // Get risk level color
  const getRiskColor = (level: string): string => {
    const colors: Record<string, string> = {
      'critical': '#d32f2f',
      'high': '#f57c00',
      'medium': '#fbc02d',
      'low': '#388e3c',
      'none': '#757575',
    };
    return colors[level] || '#757575';
  };

  // Get risk level icon
  const getRiskIcon = (level: string) => {
    if (level === 'critical' || level === 'high') return <ErrorIcon />;
    if (level === 'medium') return <WarningIcon />;
    return <CheckCircleIcon />;
  };

  // Render risk gauge
  const renderRiskGauge = () => {
    if (!riskSummary) return null;

    const score = riskSummary.overall_risk_score;
    const level = riskSummary.overall_risk_level;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Overall Risk Score
                </Typography>
                <Box
                  sx={{
                    position: 'relative',
                    display: 'inline-flex',
                    width: 200,
                    height: 200,
                    borderRadius: '50%',
                    bgcolor: `${getRiskColor(level)}20`,
                    justifyContent: 'center',
                    alignItems: 'center',
                    border: `8px solid ${getRiskColor(level)}`,
                  }}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h2" fontWeight="bold" color={getRiskColor(level)}>
                      {score.toFixed(0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      / 100
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Chip
                    icon={getRiskIcon(level)}
                    label={`${level.toUpperCase()} RISK`}
                    sx={{
                      bgcolor: getRiskColor(level),
                      color: 'white',
                      fontSize: '1rem',
                      fontWeight: 'bold',
                      py: 2,
                      px: 1,
                    }}
                  />
                </Box>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Risk Summary
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Deal Recommendation"
                    secondary={riskSummary.deal_recommendation}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Confidence Level"
                    secondary={
                      <LinearProgress
                        variant="determinate"
                        value={riskSummary.confidence_level}
                        sx={{ height: 8, borderRadius: 4, mt: 1 }}
                      />
                    }
                  />
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    {riskSummary.confidence_level.toFixed(0)}%
                  </Typography>
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Total Issues"
                    secondary={
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        <Chip
                          label={`${riskSummary.critical_issues} Critical`}
                          size="small"
                          sx={{ bgcolor: getRiskColor('critical'), color: 'white' }}
                        />
                        <Chip
                          label={`${riskSummary.high_issues} High`}
                          size="small"
                          sx={{ bgcolor: getRiskColor('high'), color: 'white' }}
                        />
                        <Chip
                          label={`${riskSummary.mitigated_issues} Mitigated`}
                          size="small"
                          color="success"
                        />
                      </Box>
                    }
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // Render category breakdown
  const renderCategoryBreakdown = () => {
    if (!riskSummary) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Risk by Category</Typography>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Filter Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Filter Category"
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value="financial">Financial</MenuItem>
                <MenuItem value="legal">Legal</MenuItem>
                <MenuItem value="operational">Operational</MenuItem>
                <MenuItem value="market">Market</MenuItem>
                <MenuItem value="regulatory">Regulatory</MenuItem>
                <MenuItem value="reputation">Reputation</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Grid container spacing={2}>
            {riskSummary.categories.map((category) => (
              <Grid item xs={12} sm={6} md={4} key={category.category}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ textTransform: 'capitalize', fontWeight: 'bold' }}>
                        {category.category}
                      </Typography>
                      <Tooltip title={`${category.trend === 'up' ? 'Increasing' : category.trend === 'down' ? 'Decreasing' : 'Stable'}`}>
                        {category.trend === 'up' ? (
                          <TrendingUpIcon color="error" />
                        ) : category.trend === 'down' ? (
                          <TrendingDownIcon color="success" />
                        ) : (
                          <Box sx={{ width: 24, height: 24 }} />
                        )}
                      </Tooltip>
                    </Box>

                    <Box sx={{ textAlign: 'center', my: 2 }}>
                      <Typography
                        variant="h3"
                        fontWeight="bold"
                        sx={{ color: getRiskColor(category.level) }}
                      >
                        {category.score.toFixed(0)}
                      </Typography>
                      <Chip
                        label={category.level.toUpperCase()}
                        size="small"
                        sx={{
                          bgcolor: getRiskColor(category.level),
                          color: 'white',
                          mt: 1,
                        }}
                      />
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {category.issues_count} issues
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {category.mitigations_count} mitigations
                      </Typography>
                    </Box>

                    <LinearProgress
                      variant="determinate"
                      value={category.score}
                      sx={{
                        mt: 1,
                        height: 6,
                        borderRadius: 3,
                        bgcolor: `${getRiskColor(category.level)}20`,
                        '& .MuiLinearProgress-bar': {
                          bgcolor: getRiskColor(category.level),
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // Render risk issues table
  const renderRiskIssues = () => {
    if (riskIssues.length === 0) {
      return (
        <Alert severity="info">
          No risk issues identified yet. Add issues as they are discovered during due diligence.
        </Alert>
      );
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Issue</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {riskIssues.map((issue) => (
              <TableRow key={issue.id}>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {issue.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {issue.description}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip label={issue.category} size="small" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={issue.severity}
                    size="small"
                    sx={{
                      bgcolor: getRiskColor(issue.severity),
                      color: 'white',
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" fontWeight="bold">
                      {issue.risk_score.toFixed(0)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      P:{issue.probability}% I:{issue.impact}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip label={issue.status} size="small" />
                </TableCell>
                <TableCell>{issue.owner || 'Unassigned'}</TableCell>
                <TableCell>
                  <IconButton size="small">
                    <EditIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Risk Assessment</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Export Report
          </Button>
          {!readOnly && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setAddIssueDialogOpen(true)}
            >
              Add Risk Issue
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Risk Gauge */}
      {renderRiskGauge()}

      {/* Category Breakdown */}
      {renderCategoryBreakdown()}

      {/* Risk Issues */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Identified Risk Issues
          </Typography>
          {renderRiskIssues()}
        </CardContent>
      </Card>

      {/* Add Issue Dialog */}
      <Dialog open={addIssueDialogOpen} onClose={() => setAddIssueDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Risk Issue</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Issue Title"
                value={newIssue.title}
                onChange={(e) => setNewIssue({ ...newIssue, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={newIssue.description}
                onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={newIssue.category}
                  onChange={(e) => setNewIssue({ ...newIssue, category: e.target.value })}
                  label="Category"
                >
                  <MenuItem value="financial">Financial</MenuItem>
                  <MenuItem value="legal">Legal</MenuItem>
                  <MenuItem value="operational">Operational</MenuItem>
                  <MenuItem value="market">Market</MenuItem>
                  <MenuItem value="regulatory">Regulatory</MenuItem>
                  <MenuItem value="reputation">Reputation</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={newIssue.severity}
                  onChange={(e) => setNewIssue({ ...newIssue, severity: e.target.value as any })}
                  label="Severity"
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
                type="number"
                label="Probability (%)"
                value={newIssue.probability}
                onChange={(e) => setNewIssue({ ...newIssue, probability: parseInt(e.target.value) })}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Impact (%)"
                value={newIssue.impact}
                onChange={(e) => setNewIssue({ ...newIssue, impact: parseInt(e.target.value) })}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                Risk Score = (Probability × Impact) / 100 = {((newIssue.probability * newIssue.impact) / 100).toFixed(0)}
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddIssueDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!newIssue.title.trim()}>
            Add Issue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RiskAssessment;
