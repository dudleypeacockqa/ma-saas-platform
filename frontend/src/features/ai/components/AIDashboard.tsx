/**
 * AI Insights Dashboard
 * Sprint 23: AI-powered deal intelligence and recommendations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Stack,
  CircularProgress,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Lightbulb as LightbulbIcon,
  Analytics as AnalyticsIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

import {
  useGetPipelineVelocityQuery,
  useAnalyzePipelineMutation,
  useGetAIModelsStatusQuery,
  type PipelineVelocity,
  type PipelineAnalysisResponse,
  type AIModelStatus,
} from '../api/aiApi';

interface AIDashboardProps {
  dealId?: string;
  showFullAnalysis?: boolean;
}

const AIDashboard: React.FC<AIDashboardProps> = ({
  dealId,
  showFullAnalysis = true
}) => {
  const theme = useTheme();
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [fullAnalysis, setFullAnalysis] = useState<PipelineAnalysisResponse | null>(null);

  // API hooks
  const {
    data: velocityData,
    isLoading: isLoadingVelocity,
    error: velocityError,
    refetch: refetchVelocity
  } = useGetPipelineVelocityQuery({ daysBack: 30 });

  const {
    data: aiStatus,
    isLoading: isLoadingStatus
  } = useGetAIModelsStatusQuery();

  const [
    analyzePipeline,
    { isLoading: isAnalyzing }
  ] = useAnalyzePipelineMutation();

  const handleFullAnalysis = async () => {
    try {
      const result = await analyzePipeline({
        include_historical_data: true,
        date_range_days: 90,
        include_forecasting: true,
      }).unwrap();

      setFullAnalysis(result);
      setAnalysisDialogOpen(true);
    } catch (error) {
      console.error('Full analysis failed:', error);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return theme.palette.success.main;
    if (score >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUpIcon color="success" />;
      case 'decreasing':
        return <TrendingDownIcon color="error" />;
      default:
        return <TimelineIcon color="info" />;
    }
  };

  const formatDuration = (days: number): string => {
    if (days < 7) return `${Math.round(days)} days`;
    const weeks = Math.round(days / 7);
    return `${weeks} week${weeks !== 1 ? 's' : ''}`;
  };

  if (isLoadingVelocity || isLoadingStatus) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (velocityError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load AI insights. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <PsychologyIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h5" fontWeight="600">
            AI Intelligence Dashboard
          </Typography>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => refetchVelocity()} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          {showFullAnalysis && (
            <Button
              variant="contained"
              startIcon={<AnalyticsIcon />}
              onClick={handleFullAnalysis}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing...' : 'Full Analysis'}
            </Button>
          )}
        </Stack>
      </Stack>

      <Grid container spacing={3}>
        {/* Pipeline Velocity Overview */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                <SpeedIcon color="primary" />
                <Typography variant="h6" fontWeight="600">
                  Pipeline Velocity
                </Typography>
                {velocityData && (
                  <Chip
                    icon={getTrendIcon(velocityData.velocity_trend)}
                    label={velocityData.velocity_trend}
                    color={
                      velocityData.velocity_trend === 'increasing' ? 'success' :
                      velocityData.velocity_trend === 'decreasing' ? 'error' : 'default'
                    }
                    size="small"
                  />
                )}
              </Stack>

              {velocityData && (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.primary.main, 0.1) }}>
                      <Typography variant="h4" color="primary" fontWeight="700">
                        {formatDuration(velocityData.average_cycle_time)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Average Cycle Time
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.success.main, 0.1) }}>
                      <Typography variant="h4" color="success.main" fontWeight="700">
                        {velocityData.efficiency_score}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Efficiency Score
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.warning.main, 0.1) }}>
                      <Typography variant="h4" color="warning.main" fontWeight="700">
                        {velocityData.bottleneck_count}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Active Bottlenecks
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.info.main, 0.1) }}>
                      <Typography variant="h4" color="info.main" fontWeight="700">
                        {Object.keys(velocityData.stage_performance).length}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Active Stages
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              )}

              {velocityData && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Stage Performance
                  </Typography>
                  {Object.entries(velocityData.stage_performance).map(([stage, days]) => (
                    <Box key={stage} sx={{ mb: 1 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {stage.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2" fontWeight="600">
                          {formatDuration(days)}
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(100, (days / 60) * 100)} // Normalize to 60 days max
                        sx={{ height: 6, borderRadius: 3 }}
                        color={days > 30 ? 'warning' : days > 45 ? 'error' : 'success'}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* AI System Status */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                <AssessmentIcon color="primary" />
                <Typography variant="h6" fontWeight="600">
                  AI System Status
                </Typography>
              </Stack>

              {aiStatus && (
                <Stack spacing={2}>
                  {/* Health Status */}
                  <Box>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">System Health</Typography>
                      <Chip
                        icon={<CheckCircleIcon />}
                        label={aiStatus.health_check.status}
                        color="success"
                        size="small"
                      />
                    </Stack>
                  </Box>

                  {/* Processing Stats */}
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Processing Statistics
                    </Typography>
                    <Stack spacing={1}>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="caption">Success Rate</Typography>
                        <Typography variant="caption" fontWeight="600">
                          {aiStatus.processing_stats.success_rate.toFixed(1)}%
                        </Typography>
                      </Stack>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="caption">Avg Processing Time</Typography>
                        <Typography variant="caption" fontWeight="600">
                          {aiStatus.processing_stats.average_processing_time_ms}ms
                        </Typography>
                      </Stack>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="caption">Total Requests</Typography>
                        <Typography variant="caption" fontWeight="600">
                          {aiStatus.processing_stats.total_requests.toLocaleString()}
                        </Typography>
                      </Stack>
                    </Stack>
                  </Box>

                  {/* Active Models */}
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Active AI Models
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {aiStatus.processing_stats.active_models} models operational
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={100}
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      color="success"
                    />
                  </Box>
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* AI Insights and Recommendations */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                <LightbulbIcon color="primary" />
                <Typography variant="h6" fontWeight="600">
                  AI Insights & Recommendations
                </Typography>
              </Stack>

              <Grid container spacing={3}>
                {/* Quick Insights */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Pipeline Insights
                  </Typography>
                  <List dense>
                    {velocityData && velocityData.efficiency_score < 70 && (
                      <ListItem>
                        <ListItemIcon>
                          <WarningIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Pipeline Efficiency Below Target"
                          secondary="Consider process optimization to improve deal flow"
                        />
                      </ListItem>
                    )}
                    {velocityData && velocityData.bottleneck_count > 0 && (
                      <ListItem>
                        <ListItemIcon>
                          <WarningIcon color="error" />
                        </ListItemIcon>
                        <ListItemText
                          primary={`${velocityData.bottleneck_count} Bottleneck${velocityData.bottleneck_count > 1 ? 's' : ''} Detected`}
                          secondary="Review stage processes and resource allocation"
                        />
                      </ListItem>
                    )}
                    {velocityData && velocityData.velocity_trend === 'increasing' && (
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Positive Velocity Trend"
                          secondary="Pipeline efficiency is improving over time"
                        />
                      </ListItem>
                    )}
                    <ListItem>
                      <ListItemIcon>
                        <InfoIcon color="info" />
                      </ListItemIcon>
                      <ListItemText
                        primary="AI Analysis Available"
                        secondary="Run full analysis for detailed insights and forecasting"
                      />
                    </ListItem>
                  </List>
                </Grid>

                {/* AI Recommendations */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    AI Recommendations
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <LightbulbIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Implement Parallel Processing"
                        secondary="Run due diligence and valuation concurrently for 20% faster cycles"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LightbulbIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Automate Initial Screening"
                        secondary="Use AI-powered screening to reduce manual review time"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LightbulbIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Early Stakeholder Engagement"
                        secondary="Involve key stakeholders from the valuation stage onwards"
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Full Analysis Dialog */}
      <Dialog
        open={analysisDialogOpen}
        onClose={() => setAnalysisDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" spacing={2} alignItems="center">
            <AnalyticsIcon color="primary" />
            <Typography variant="h6">Comprehensive Pipeline Analysis</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          {fullAnalysis && (
            <Grid container spacing={3}>
              {/* Bottlenecks */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Identified Bottlenecks
                </Typography>
                {fullAnalysis.bottlenecks.length === 0 ? (
                  <Alert severity="success">
                    No major bottlenecks detected in your pipeline!
                  </Alert>
                ) : (
                  <Stack spacing={2}>
                    {fullAnalysis.bottlenecks.map((bottleneck, index) => (
                      <Card key={index} variant="outlined">
                        <CardContent>
                          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                            <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                              {bottleneck.stage.replace('_', ' ')}
                            </Typography>
                            <Chip
                              label={bottleneck.urgency_level}
                              color={
                                bottleneck.urgency_level === 'high' ? 'error' :
                                bottleneck.urgency_level === 'medium' ? 'warning' : 'default'
                              }
                              size="small"
                            />
                          </Stack>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {bottleneck.deals_affected} deals affected • {bottleneck.average_delay_days} day average delay
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            Revenue Impact: ${(bottleneck.impact_on_revenue / 1000000).toFixed(1)}M
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Suggested Actions:
                          </Typography>
                          <List dense>
                            {bottleneck.suggested_actions.slice(0, 2).map((action, actionIndex) => (
                              <ListItem key={actionIndex} sx={{ pl: 0 }}>
                                <ListItemText primary={action} />
                              </ListItem>
                            ))}
                          </List>
                        </CardContent>
                      </Card>
                    ))}
                  </Stack>
                )}
              </Grid>

              {/* Revenue Forecast */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Revenue Forecast
                </Typography>
                {fullAnalysis.revenue_forecast && (
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <Box>
                          <Typography variant="subtitle2">Annual Forecast</Typography>
                          <Typography variant="h4" color="primary">
                            ${(fullAnalysis.revenue_forecast.annual_forecast.expected_revenue / 1000000).toFixed(1)}M
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Expected Annual Revenue
                          </Typography>
                        </Box>
                        <Divider />
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Key Assumptions
                          </Typography>
                          {fullAnalysis.revenue_forecast.key_assumptions.map((assumption, index) => (
                            <Typography key={index} variant="body2" color="text.secondary">
                              • {assumption}
                            </Typography>
                          ))}
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                )}
              </Grid>

              {/* Optimization Opportunities */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Optimization Opportunities
                </Typography>
                <Grid container spacing={2}>
                  {fullAnalysis.optimization_opportunities.map((opportunity, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Stack direction="row" spacing={1} alignItems="flex-start">
                            <LightbulbIcon color="primary" sx={{ mt: 0.5 }} />
                            <Typography variant="body2">
                              {opportunity}
                            </Typography>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalysisDialogOpen(false)}>
            Close
          </Button>
          <Button variant="contained" onClick={() => window.print()}>
            Export Report
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIDashboard;