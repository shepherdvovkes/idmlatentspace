import React from 'react';
import { Box, Typography } from '@mui/material';

const Analysis: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Real-time Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary">
        Real-time preset analysis interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default Analysis;