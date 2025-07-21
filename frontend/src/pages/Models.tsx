import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { ModelTraining } from '@mui/icons-material';

const Models: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Models
        </Typography>
        <Button
          variant="contained"
          startIcon={<ModelTraining />}
        >
          Train New Model
        </Button>
      </Box>
      
      <Typography variant="body1" color="text.secondary">
        Model training and evaluation interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default Models;