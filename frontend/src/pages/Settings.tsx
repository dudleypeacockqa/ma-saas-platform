import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure your account and preferences
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Settings Page
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Organization settings, user preferences, and system configuration will be available here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Settings;