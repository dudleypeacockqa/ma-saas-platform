/**
 * Deal AI Insights Component
 * Sprint 23: AI-powered deal analysis and recommendations
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Button,
  Stack,
  Alert,
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Psychology as AIIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Lightbulb as RecommendationIcon,
  Assessment as ScoreIcon,
  Security as RiskIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import {
  useGetDealScoreQuery,
  useAnalyzeDealMutation,
  useGetDealRecommendationsQuery,
  type DealAnalysisResponse,
} from '../api/aiApi';

interface DealAIInsightsProps {
  dealId: string;
  dealData?: Record<string, any>;
  compact?: boolean;
}

const DealAIInsights: React.FC<DealAIInsightsProps> = ({
  dealId,
  dealData,
  compact = false
}) => {
  const theme = useTheme();
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [fullAnalysis, setFullAnalysis] = useState<DealAnalysisResponse | null>(null);

  // API hooks
  const {
    data: quickScore,
    isLoading: isLoadingScore,
    error: scoreError,
    refetch: refetchScore
  } = useGetDealScoreQuery(dealId);

  const {
    data: recommendations,
    isLoading: isLoadingRecommendations
  } = useGetDealRecommendationsQuery(dealId);

  const [
    analyzeDeal,
    { isLoading: isAnalyzing }
  ] = useAnalyzeDealMutation();

  const handleFullAnalysis = async () => {
    if (!dealData) {
      console.error('Deal data required for full analysis');
      return;
    }

    try {
      const result = await analyzeDeal({
        deal_id: dealId,
        deal_data: dealData,
        include_market_analysis: true,
        include_competitive_analysis: true,
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

  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'low': return theme.palette.success.main;
      case 'medium': return theme.palette.warning.main;
      case 'high': return theme.palette.error.main;
      case 'critical': return theme.palette.error.dark;
      default: return theme.palette.text.secondary;
    }
  };

  const formatScore = (score: number): string => {
    return Math.round(score).toString();
  };

  if (isLoadingScore) {
    return (
      <Card elevation={1}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <CircularProgress size={24} />
            <Typography variant="body2">Loading AI insights...</Typography>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  if (scoreError) {
    return (
      <Card elevation={1}>
        <CardContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            AI insights temporarily unavailable
          </Alert>
          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={() => refetchScore()}
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <Card elevation={1}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={2} alignItems="center">
              <AIIcon color="primary" />
              <Box>
                <Typography variant="subtitle2" fontWeight="600">
                  AI Score
                </Typography>
                {quickScore && (
                  <Typography variant="h6" color={getScoreColor(quickScore.score)}>
                    {formatScore(quickScore.score)}/100
                  </Typography>
                )}
              </Box>
            </Stack>
            <Button
              size="small"
              variant="outlined"
              onClick={handleFullAnalysis}
              disabled={!dealData || isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Card elevation={2}>
        <CardContent>
          {/* Header */}
          <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <AIIcon color="primary" sx={{ fontSize: 28 }} />
              <Typography variant="h6" fontWeight="600">
                AI Insights
              </Typography>
            </Stack>
            <Stack direction="row" spacing={1}>
              <Button
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => refetchScore()}
                disabled={isLoadingScore}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                size="small"
                startIcon={<ScoreIcon />}
                onClick={handleFullAnalysis}
                disabled={!dealData || isAnalyzing}
              >
                {isAnalyzing ? 'Analyzing...' : 'Full Analysis'}
              </Button>
            </Stack>
          </Stack>

          <Grid container spacing={3}>
            {/* Quick Score */}
            <Grid item xs={12} sm={6}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: alpha(theme.palette.primary.main, 0.05), borderRadius: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Overall AI Score
                </Typography>
                {quickScore && (
                  <>
                    <Typography variant="h3" color={getScoreColor(quickScore.score)} fontWeight="700">
                      {formatScore(quickScore.score)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      out of 100
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={quickScore.score}
                      sx={{ mt: 1, height: 8, borderRadius: 4 }}
                      color={quickScore.score >= 80 ? 'success' : quickScore.score >= 60 ? 'warning' : 'error'}
                    />
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      Confidence: {Math.round(quickScore.confidence * 100)}%
                    </Typography>
                  </>
                )}
              </Box>
            </Grid>

            {/* Quick Recommendations */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" gutterBottom>
                AI Recommendations
              </Typography>
              {isLoadingRecommendations ? (
                <CircularProgress size={24} />
              ) : recommendations ? (
                <List dense>
                  {recommendations.priority_actions.slice(0, 3).map((action, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemIcon>
                        <RecommendationIcon color="primary" sx={{ fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={action}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                  {recommendations.priority_actions.length > 3 && (
                    <ListItem sx={{ pl: 0 }}>
                      <ListItemText
                        primary={`+${recommendations.priority_actions.length - 3} more recommendations`}
                        primaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                      />
                    </ListItem>
                  )}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recommendations available
                </Typography>
              )}
            </Grid>
          </Grid>

          {/* Status */}
          {quickScore && (
            <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Typography variant="caption" color="text.secondary">
                  Last updated: {new Date(quickScore.last_updated).toLocaleDateString()}
                </Typography>
                <Chip
                  icon={<SuccessIcon />}
                  label="AI Analysis Ready"
                  color="success"
                  size="small"
                />
              </Stack>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Full Analysis Dialog */}
      <Dialog
        open={analysisDialogOpen}
        onClose={() => setAnalysisDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" spacing={2} alignItems="center">
            <AIIcon color="primary" />
            <Typography variant="h6">Comprehensive AI Analysis</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          {fullAnalysis && (
            <Grid container spacing={3}>
              {/* Scores Breakdown */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Score Breakdown
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h4" color={getScoreColor(fullAnalysis.financial_score)}>
                        {formatScore(fullAnalysis.financial_score)}
                      </Typography>
                      <Typography variant="caption">Financial</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h4" color={getScoreColor(fullAnalysis.strategic_score)}>
                        {formatScore(fullAnalysis.strategic_score)}
                      </Typography>
                      <Typography variant="caption">Strategic</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h4" color={getScoreColor(fullAnalysis.risk_score)}>
                        {formatScore(fullAnalysis.risk_score)}
                      </Typography>
                      <Typography variant="caption">Risk</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h4" color={getScoreColor(fullAnalysis.market_score)}>
                        {formatScore(fullAnalysis.market_score)}
                      </Typography>
                      <Typography variant="caption">Market</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h4" color={getScoreColor(fullAnalysis.team_score)}>
                        {formatScore(fullAnalysis.team_score)}
                      </Typography>
                      <Typography variant="caption">Team</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Grid>

              {/* Recommendation and Risk */}
              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>
                  AI Recommendation
                </Typography>
                <Alert
                  severity={
                    fullAnalysis.recommendation === 'proceed' ? 'success' :
                    fullAnalysis.recommendation === 'proceed_with_caution' ? 'warning' :
                    fullAnalysis.recommendation === 'investigate_further' ? 'info' : 'error'
                  }
                  sx={{ textTransform: 'capitalize' }}
                >
                  {fullAnalysis.recommendation.replace('_', ' ')}
                </Alert>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>
                  Risk Assessment
                </Typography>
                <Chip
                  icon={<RiskIcon />}
                  label={`${fullAnalysis.risk_level} Risk`}
                  color={
                    fullAnalysis.risk_level === 'low' ? 'success' :
                    fullAnalysis.risk_level === 'medium' ? 'warning' : 'error'
                  }
                  sx={{ textTransform: 'capitalize' }}
                />
              </Grid>

              {/* Next Actions */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Recommended Next Actions
                </Typography>
                <List>
                  {fullAnalysis.next_actions.map((action, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <RecommendationIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={action} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalysisDialogOpen(false)}>
            Close
          </Button>
          <Button variant="contained" onClick={() => window.print()}>
            Export Analysis
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DealAIInsights;