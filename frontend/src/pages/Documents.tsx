import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Documents: React.FC = () => {
  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom>
          Document Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Secure document storage and organization
        </Typography>
      </Paper>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Coming in Sprint 3
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Document upload, organization, and management features will be implemented in Sprint 3.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Documents;