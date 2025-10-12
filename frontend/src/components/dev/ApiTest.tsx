/**
 * Sprint 21 - API Integration Test Component
 * Simple component to test frontend-backend connectivity
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Chip,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { useGetDealStatisticsQuery, useGetDealsQuery } from '@/features/deals/api/dealsApi';
import { useAppSelector } from '@/app/hooks';

const ApiTest: React.FC = () => {
  const authState = useAppSelector((state) => state.auth);

  // Test API calls
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats
  } = useGetDealStatisticsQuery();

  const {
    data: deals,
    isLoading: dealsLoading,
    error: dealsError,
    refetch: refetchDeals
  } = useGetDealsQuery({ per_page: 3 });

  const handleRefresh = () => {
    refetchStats();
    refetchDeals();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Sprint 21 - API Integration Test
        </Typography>

        {/* Authentication Status */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Authentication Status
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            {authState.isAuthenticated ? (
              <>
                <Chip
                  icon={<CheckIcon />}
                  label="Authenticated"
                  color="success"
                />
                <Typography variant="body2">
                  User: {authState.user?.email} | Org: {authState.user?.organizationId}
                </Typography>
              </>
            ) : (
              <Chip
                icon={<ErrorIcon />}
                label="Not Authenticated"
                color="error"
              />
            )}
          </Stack>
        </Box>

        {/* API Test Results */}
        <Box sx={{ mb: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              API Connection Tests
            </Typography>
            <Button
              onClick={handleRefresh}
              startIcon={<RefreshIcon />}
              size="small"
              variant="outlined"
            >
              Refresh
            </Button>
          </Stack>

          {/* Deal Statistics API Test */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              1. Deal Statistics API (/api/deals/analytics/summary)
            </Typography>

            {statsLoading && (
              <Stack direction="row" spacing={1} alignItems="center">
                <CircularProgress size={20} />
                <Typography>Loading statistics...</Typography>
              </Stack>
            )}

            {statsError && (
              <Alert severity="error" sx={{ mb: 1 }}>
                Error: {JSON.stringify(statsError)}
              </Alert>
            )}

            {stats && (
              <Alert severity="success" sx={{ mb: 1 }}>
                ✅ Success! Retrieved {stats.total_deals} deals,
                Total Value: ${stats.total_value?.toLocaleString() || 0}
              </Alert>
            )}
          </Box>

          {/* Deal List API Test */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              2. Deal List API (/api/deals)
            </Typography>

            {dealsLoading && (
              <Stack direction="row" spacing={1} alignItems="center">
                <CircularProgress size={20} />
                <Typography>Loading deals...</Typography>
              </Stack>
            )}

            {dealsError && (
              <Alert severity="error" sx={{ mb: 1 }}>
                Error: {JSON.stringify(dealsError)}
              </Alert>
            )}

            {deals && (
              <Alert severity="success" sx={{ mb: 1 }}>
                ✅ Success! Retrieved {deals.data?.length || 0} deals
                {deals.data?.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    Sample deal: "{deals.data[0]?.title}"
                    (Stage: {deals.data[0]?.stage})
                  </Box>
                )}
              </Alert>
            )}
          </Box>
        </Box>

        {/* Overall Status */}
        <Box>
          <Typography variant="h6" gutterBottom>
            Overall Status
          </Typography>

          {authState.isAuthenticated && !statsError && !dealsError && (stats || deals) ? (
            <Alert severity="success">
              🎉 Frontend-Backend Integration: WORKING!
              <br />
              All API endpoints are responding correctly.
            </Alert>
          ) : (
            <Alert severity="warning">
              ⚠️ Integration Issues Detected
              <br />
              {!authState.isAuthenticated && "- Authentication required"}
              {statsError && "- Statistics API error"}
              {dealsError && "- Deals API error"}
            </Alert>
          )}
        </Box>

        {/* Debug Info */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Debug Info:
            <br />
            Token Present: {authState.token ? 'Yes' : 'No'}
            <br />
            Base URL: /api/deals
            <br />
            Environment: {import.meta.env.MODE}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default ApiTest;