import React from 'react';
import { Card, CardContent, Typography, Button, Stack } from '@mui/material';
import { FileUpload, ModelTraining, Analytics } from '@mui/icons-material';

const QuickActions: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Stack spacing={2}>
          <Button
            variant="outlined"
            startIcon={<FileUpload />}
            fullWidth
            href="/datasets"
          >
            Upload Dataset
          </Button>
          <Button
            variant="outlined"
            startIcon={<ModelTraining />}
            fullWidth
            href="/models"
          >
            Train Model
          </Button>
          <Button
            variant="outlined"
            startIcon={<Analytics />}
            fullWidth
            href="/analysis"
          >
            Analyze Preset
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default QuickActions;