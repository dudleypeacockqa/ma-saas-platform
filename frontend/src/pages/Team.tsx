import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Team: React.FC = () => {
  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom>
          Team Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage team members and collaboration
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Coming in Sprint 4
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Team collaboration and management features will be implemented in Sprint 4.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Team;