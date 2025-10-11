import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Profile: React.FC = () => {
  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom>
          Profile
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your personal information
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          User Profile
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Profile management features will be available here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Profile;