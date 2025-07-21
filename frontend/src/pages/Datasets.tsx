import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { FileUpload } from '@mui/icons-material';

const Datasets: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Datasets
        </Typography>
        <Button
          variant="contained"
          startIcon={<FileUpload />}
        >
          Upload Dataset
        </Button>
      </Box>
      
      <Typography variant="body1" color="text.secondary">
        Dataset management interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default Datasets;