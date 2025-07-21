import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, LinearProgress, Box } from '@mui/material';

const RecentModels: React.FC = () => {
  const models = [
    { id: 1, name: 'Genre Classifier v2', accuracy: 89.2, status: 'training' },
    { id: 2, name: 'Bass Generator', accuracy: 91.5, status: 'completed' },
    { id: 3, name: 'Lead Synthesizer', accuracy: 87.8, status: 'completed' },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Models
        </Typography>
        <List dense>
          {models.map((model) => (
            <ListItem key={model.id}>
              <ListItemText
                primary={model.name}
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Accuracy: {model.accuracy}% • {model.status}
                    </Typography>
                    {model.status === 'training' && (
                      <LinearProgress sx={{ mt: 1 }} />
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default RecentModels;