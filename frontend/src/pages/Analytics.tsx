import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Analytics: React.FC = () => {
  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom>
          Analytics & Insights
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Advanced analytics and reporting
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Coming Soon
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Advanced analytics and reporting features will be available in a future release.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Analytics;