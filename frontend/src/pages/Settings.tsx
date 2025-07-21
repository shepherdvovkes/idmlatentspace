import React from 'react';
import { Box, Typography } from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      
      <Typography variant="body1" color="text.secondary">
        Application settings interface will be implemented here.
      </Typography>
    </Box>
  );
};

export default Settings;