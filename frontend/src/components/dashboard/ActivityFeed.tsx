import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Chip } from '@mui/material';

const ActivityFeed: React.FC = () => {
  const activities = [
    { id: 1, action: 'Dataset uploaded', item: 'Bass Presets v2', time: '2 minutes ago', status: 'success' },
    { id: 2, action: 'Model training', item: 'Genre Classifier', time: '5 minutes ago', status: 'running' },
    { id: 3, action: 'Analysis completed', item: 'Dubstep Lead', time: '10 minutes ago', status: 'success' },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <List dense>
          {activities.map((activity) => (
            <ListItem key={activity.id}>
              <ListItemText
                primary={`${activity.action}: ${activity.item}`}
                secondary={activity.time}
              />
              <Chip 
                label={activity.status} 
                size="small" 
                color={activity.status === 'success' ? 'success' : 'primary'}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default ActivityFeed;