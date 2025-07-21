import React from 'react';
import { Box, Typography } from '@mui/material';

const Experiments: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Experiments
      </Typography>
      
      <Typography variant="body1" color="text.secondary">
        Experiment management interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default Experiments;