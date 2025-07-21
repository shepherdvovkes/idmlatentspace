import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material';

interface SystemStatusProps {
  systemLoad: number;
  memoryUsage: number;
  processingJobs: number;
  apiRequests: number;
  loading?: boolean;
}

const SystemStatus: React.FC<SystemStatusProps> = ({
  systemLoad,
  memoryUsage,
  processingJobs,
  apiRequests,
  loading = false,
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            CPU Load: {systemLoad}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={systemLoad} 
            color={systemLoad > 80 ? 'error' : 'primary'}
            sx={{ mt: 1 }}
          />
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Memory Usage: {memoryUsage}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={memoryUsage} 
            color={memoryUsage > 80 ? 'warning' : 'primary'}
            sx={{ mt: 1 }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Typography variant="body2">
            Active Jobs: {processingJobs}
          </Typography>
          <Typography variant="body2">
            API Requests: {apiRequests}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SystemStatus;