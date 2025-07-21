import React from 'react';
import { Card, CardContent, Typography, Grid, Chip, Box } from '@mui/material';

const DatasetOverview: React.FC = () => {
  const datasets = [
    { name: 'Bass Presets Collection', presets: 2847, status: 'ready', quality: 94 },
    { name: 'Lead Synthesizer Pack', presets: 1523, status: 'processing', quality: 87 },
    { name: 'Dubstep Arsenal', presets: 3192, status: 'ready', quality: 91 },
    { name: 'IDM Experimental', presets: 1876, status: 'ready', quality: 89 },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Dataset Overview
        </Typography>
        <Grid container spacing={2}>
          {datasets.map((dataset, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Box 
                sx={{ 
                  p: 2, 
                  border: '1px solid', 
                  borderColor: 'divider', 
                  borderRadius: 2,
                  backgroundColor: 'background.paper'
                }}
              >
                <Typography variant="subtitle2" gutterBottom>
                  {dataset.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dataset.presets.toLocaleString()} presets
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Chip 
                    label={dataset.status} 
                    size="small" 
                    color={dataset.status === 'ready' ? 'success' : 'warning'}
                  />
                  <Typography variant="caption">
                    Q: {dataset.quality}%
                  </Typography>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default DatasetOverview;