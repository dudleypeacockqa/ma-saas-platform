/**
 * Mobile Dashboard Component
 * Sprint 24: Mobile-optimized dashboard with widgets and quick actions
 */

import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Grid,
  Avatar,
  Chip,
  LinearProgress,
  Stack,
  Button,
  Paper,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Badge,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  BusinessCenter as DealIcon,
  AttachMoney as MoneyIcon,
  Schedule as TimeIcon,
  Notifications as NotificationIcon,
  Add as AddIcon,
  Call as CallIcon,
  VideoCall as VideoIcon,
  Message as MessageIcon,
  NoteAdd as NoteIcon,
  PhotoCamera as CameraIcon,
  RecordVoiceOver as VoiceIcon,
  MoreVert as MoreIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';
import { useHaptics } from '../../services/haptics';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

interface DashboardProps {
  user?: {
    firstName?: string;
    lastName?: string;
    imageUrl?: string;
  };
  notifications?: number;
  onRefresh?: () => void;
}

interface QuickStat {
  label: string;
  value: string | number;
  change: number;
  icon: React.ReactElement;
  color: string;
}

interface RecentDeal {
  id: string;
  title: string;
  company: string;
  value: number;
  stage: string;
  lastActivity: string;
  assignee: {
    name: string;
    avatar?: string;
  };
}

interface QuickAction {
  label: string;
  icon: React.ReactElement;
  action: () => void;
  color?: string;
}

const MobileDashboard: React.FC<DashboardProps> = ({
  user,
  notifications = 0,
  onRefresh,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const haptics = useHaptics();

  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Mock data - replace with real data from APIs
  const quickStats: QuickStat[] = [
    {
      label: 'Active Deals',
      value: 24,
      change: 12,
      icon: <DealIcon />,
      color: theme.palette.primary.main,
    },
    {
      label: 'Pipeline Value',
      value: '$4.2M',
      change: 8,
      icon: <MoneyIcon />,
      color: theme.palette.success.main,
    },
    {
      label: 'Avg. Close Time',
      value: '45 days',
      change: -5,
      icon: <TimeIcon />,
      color: theme.palette.warning.main,
    },
    {
      label: 'Win Rate',
      value: '68%',
      change: 15,
      icon: <TrendingUpIcon />,
      color: theme.palette.info.main,
    },
  ];

  const recentDeals: RecentDeal[] = [
    {
      id: '1',
      title: 'TechCorp Acquisition',
      company: 'TechCorp Inc.',
      value: 850000,
      stage: 'Due Diligence',
      lastActivity: '2 hours ago',
      assignee: {
        name: 'John Smith',
        avatar: undefined,
      },
    },
    {
      id: '2',
      title: 'StartupX Merger',
      company: 'StartupX Ltd.',
      value: 1200000,
      stage: 'Negotiation',
      lastActivity: '5 hours ago',
      assignee: {
        name: 'Jane Doe',
        avatar: undefined,
      },
    },
    {
      id: '3',
      title: 'GlobalCo Buyout',
      company: 'GlobalCo',
      value: 2500000,
      stage: 'Valuation',
      lastActivity: '1 day ago',
      assignee: {
        name: 'Mike Johnson',
        avatar: undefined,
      },
    },
  ];

  const quickActions: QuickAction[] = [
    {
      label: 'New Deal',
      icon: <DealIcon />,
      action: () => {
        haptics.buttonPress();
        console.log('New Deal');
      },
      color: theme.palette.primary.main,
    },
    {
      label: 'Schedule Call',
      icon: <CallIcon />,
      action: () => {
        haptics.buttonPress();
        console.log('Schedule Call');
      },
      color: theme.palette.success.main,
    },
    {
      label: 'Video Meeting',
      icon: <VideoIcon />,
      action: () => {
        haptics.buttonPress();
        console.log('Video Meeting');
      },
      color: theme.palette.info.main,
    },
    {
      label: 'Send Message',
      icon: <MessageIcon />,
      action: () => {
        haptics.buttonPress();
        console.log('Send Message');
      },
      color: theme.palette.warning.main,
    },
    {
      label: 'Add Note',
      icon: <NoteIcon />,
      action: () => {
        haptics.buttonPress();
        console.log('Add Note');
      },
      color: theme.palette.secondary.main,
    },
    {
      label: 'Take Photo',
      icon: <CameraIcon />,
      action: () => {
        haptics.photoCapture();
        console.log('Take Photo');
      },
      color: theme.palette.error.main,
    },
  ];

  const handleRefresh = async () => {
    setRefreshing(true);
    haptics.pullToRefresh();

    try {
      await onRefresh?.();
    } finally {
      setTimeout(() => setRefreshing(false), 1000);
    }
  };

  const formatCurrency = (amount: number): string => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    }
    return `$${(amount / 1000).toFixed(0)}K`;
  };

  const getStageColor = (stage: string): string => {
    switch (stage.toLowerCase()) {
      case 'sourcing':
        return theme.palette.info.main;
      case 'valuation':
        return theme.palette.warning.main;
      case 'due diligence':
        return theme.palette.error.main;
      case 'negotiation':
        return theme.palette.success.main;
      case 'closing':
        return theme.palette.primary.main;
      default:
        return theme.palette.grey[500];
    }
  };

  return (
    <Box sx={{ pb: 10, pt: 2 }}>
      {/* Header */}
      <Box sx={{ px: 2, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" fontWeight={600}>
              Good morning, {user?.firstName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Here's your deal pipeline overview
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon sx={{
                animation: refreshing ? 'spin 1s linear infinite' : 'none',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }} />
            </IconButton>

            <IconButton>
              <Badge badgeContent={notifications} color="error">
                <NotificationIcon />
              </Badge>
            </IconButton>
          </Stack>
        </Stack>
      </Box>

      {/* Quick Stats Carousel */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ px: 2, mb: 2, fontWeight: 600 }}>
          Key Metrics
        </Typography>

        <Swiper
          modules={[Navigation, Pagination]}
          spaceBetween={16}
          slidesPerView={2.2}
          pagination={{ clickable: true }}
          style={{ paddingLeft: 16, paddingRight: 16 }}
        >
          {quickStats.map((stat, index) => (
            <SwiperSlide key={index}>
              <Card
                sx={{
                  height: 120,
                  background: `linear-gradient(135deg, ${stat.color}15, ${stat.color}25)`,
                  border: `1px solid ${stat.color}30`,
                }}
                onClick={() => haptics.cardTap()}
              >
                <CardContent sx={{ p: 2 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box sx={{ color: stat.color }}>
                      {stat.icon}
                    </Box>
                    <Chip
                      label={`${stat.change > 0 ? '+' : ''}${stat.change}%`}
                      size="small"
                      sx={{
                        bgcolor: stat.change > 0 ? 'success.light' : 'error.light',
                        color: stat.change > 0 ? 'success.dark' : 'error.dark',
                        fontSize: '0.75rem',
                      }}
                    />
                  </Stack>

                  <Typography variant="h5" fontWeight={700} sx={{ mt: 1, mb: 0.5 }}>
                    {stat.value}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </SwiperSlide>
          ))}
        </Swiper>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ px: 2, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Quick Actions
        </Typography>

        <Grid container spacing={2}>
          {quickActions.slice(0, 4).map((action, index) => (
            <Grid item xs={6} key={index}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={action.icon}
                onClick={action.action}
                sx={{
                  py: 1.5,
                  borderColor: action.color,
                  color: action.color,
                  '&:hover': {
                    borderColor: action.color,
                    bgcolor: `${action.color}10`,
                  },
                }}
              >
                {action.label}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Recent Deals */}
      <Box sx={{ px: 2, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            Recent Deals
          </Typography>
          <Button
            size="small"
            endIcon={<AnalyticsIcon />}
            onClick={() => haptics.navigation()}
          >
            View All
          </Button>
        </Stack>

        <Stack spacing={2}>
          {recentDeals.map((deal) => (
            <Card key={deal.id} onClick={() => haptics.cardTap()}>
              <CardContent sx={{ p: 2 }}>
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <Avatar sx={{ bgcolor: theme.palette.primary.main, width: 40, height: 40 }}>
                    <DealIcon />
                  </Avatar>

                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle1" fontWeight={600} noWrap>
                      {deal.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {deal.company}
                    </Typography>

                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                      <Chip
                        label={deal.stage}
                        size="small"
                        sx={{
                          bgcolor: `${getStageColor(deal.stage)}20`,
                          color: getStageColor(deal.stage),
                          fontSize: '0.75rem',
                        }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {deal.lastActivity}
                      </Typography>
                    </Stack>
                  </Box>

                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h6" fontWeight={600} color="primary">
                      {formatCurrency(deal.value)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {deal.assignee.name}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>
      </Box>

      {/* Speed Dial for Quick Actions */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{
          position: 'fixed',
          bottom: 88,
          right: 16,
          '& .MuiSpeedDial-fab': {
            bgcolor: theme.palette.primary.main,
            '&:hover': {
              bgcolor: theme.palette.primary.dark,
            },
          },
        }}
        icon={<SpeedDialIcon />}
        open={speedDialOpen}
        onOpen={() => {
          setSpeedDialOpen(true);
          haptics.buttonPress();
        }}
        onClose={() => setSpeedDialOpen(false)}
      >
        {quickActions.slice(4).map((action) => (
          <SpeedDialAction
            key={action.label}
            icon={action.icon}
            tooltipTitle={action.label}
            onClick={() => {
              action.action();
              setSpeedDialOpen(false);
            }}
            sx={{
              '& .MuiSpeedDialAction-fab': {
                bgcolor: action.color,
                color: 'white',
                '&:hover': {
                  bgcolor: action.color,
                  opacity: 0.8,
                },
              },
            }}
          />
        ))}
      </SpeedDial>
    </Box>
  );
};

export default MobileDashboard;