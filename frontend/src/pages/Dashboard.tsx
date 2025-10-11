/**
 * Dashboard Page
 * Main overview page with key metrics and recent activity
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  AttachMoney as MoneyIcon,
  BusinessCenter as DealsIcon,
  Schedule as PendingIcon,
  CheckCircle as SuccessIcon,
  Warning as WarningIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';

import { useGetDealStatisticsQuery, useGetDealsQuery } from '@/features/deals/api/dealsApi';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  // Fetch statistics
  const { data: stats } = useGetDealStatisticsQuery();
  const { data: recentDeals } = useGetDealsQuery({
    per_page: 5,
    sort_by: 'updated_at',
    sort_order: 'desc',
  });

  const metrics = [
    {
      title: 'Total Pipeline Value',
      value: stats ? `$${(stats.total_value / 1000000).toFixed(1)}M` : '-',
      change: '+12.5%',
      icon: <MoneyIcon />,
      color: theme.palette.success.main,
    },
    {
      title: 'Active Deals',
      value: stats?.active_deals || 0,
      change: '+5',
      icon: <DealsIcon />,
      color: theme.palette.primary.main,
    },
    {
      title: 'Average Probability',
      value: stats ? `${Math.round(stats.average_probability)}%` : '-',
      change: '+3%',
      icon: <TrendingUpIcon />,
      color: theme.palette.warning.main,
    },
    {
      title: 'Closing This Month',
      value: stats?.closing_this_month || 0,
      change: '2 overdue',
      icon: <PendingIcon />,
      color: theme.palette.info.main,
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Welcome back! Here's your M&A pipeline overview.
      </Typography>

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="caption" gutterBottom>
                      {metric.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {metric.value}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: metric.change.startsWith('+') ? 'success.main' : 'error.main',
                        mt: 1,
                      }}
                    >
                      {metric.change}
                    </Typography>
                  </Box>
                  <Avatar
                    sx={{
                      bgcolor: `${metric.color}20`,
                      color: metric.color,
                    }}
                  >
                    {metric.icon}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Pipeline Progress */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Pipeline Progress
            </Typography>

            {stats && Object.entries(stats.by_stage).map(([stage, count]) => (
              <Box key={stage} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">
                    {stage.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {count} deals
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(count / stats.total_deals) * 100}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            ))}

            <Button
              fullWidth
              variant="outlined"
              endIcon={<ArrowIcon />}
              sx={{ mt: 3 }}
              onClick={() => navigate('/deals/pipeline')}
            >
              View Full Pipeline
            </Button>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Deals
            </Typography>

            <List>
              {recentDeals?.data.slice(0, 5).map((deal) => (
                <ListItem
                  key={deal.id}
                  button
                  onClick={() => navigate(`/deals/${deal.id}`)}
                  sx={{ px: 0 }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      {deal.target_company_name[0]}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={deal.title}
                    secondary={
                      <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                        <Chip
                          label={deal.stage.replace(/_/g, ' ')}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={`${deal.probability_of_close}%`}
                          size="small"
                          color={deal.probability_of_close >= 70 ? 'success' : 'default'}
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Button
              fullWidth
              variant="outlined"
              endIcon={<ArrowIcon />}
              onClick={() => navigate('/deals')}
            >
              View All Deals
            </Button>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<DealsIcon />}
                  onClick={() => navigate('/deals/new')}
                >
                  Create New Deal
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/documents')}
                >
                  Upload Documents
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/team')}
                >
                  Invite Team Member
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/analytics')}
                >
                  View Analytics
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;