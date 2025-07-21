import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Button,
  Stack,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  FileUpload as FileUploadIcon,
  ModelTraining as ModelTrainingIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import MetricCard from '../components/dashboard/MetricCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import QuickActions from '../components/dashboard/QuickActions';
import SystemStatus from '../components/dashboard/SystemStatus';
import LatentSpaceVisualization from '../components/visualizations/LatentSpaceVisualization';
import RecentModels from '../components/dashboard/RecentModels';
import DatasetOverview from '../components/dashboard/DatasetOverview';

interface DashboardMetrics {
  totalDatasets: number;
  totalPresets: number;
  activeModels: number;
  processingJobs: number;
  systemLoad: number;
  memoryUsage: number;
  apiRequests: number;
  accuracyAverage: number;
}

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalDatasets: 0,
    totalPresets: 0,
    activeModels: 0,
    processingJobs: 0,
    systemLoad: 0,
    memoryUsage: 0,
    apiRequests: 0,
    accuracyAverage: 0,
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Mock data - replace with real API calls
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMetrics({
        totalDatasets: 24,
        totalPresets: 15847,
        activeModels: 12,
        processingJobs: 3,
        systemLoad: 68.5,
        memoryUsage: 72.3,
        apiRequests: 1247,
        accuracyAverage: 89.2,
      });
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    fetchDashboardData();
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            IDM Latent Space Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<FileUploadIcon />}
            href="/datasets"
          >
            Upload Dataset
          </Button>
          <Button
            variant="contained"
            startIcon={<ModelTrainingIcon />}
            href="/models"
          >
            Train Model
          </Button>
          <IconButton onClick={refreshData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Stack>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics Row */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Datasets"
            value={metrics.totalDatasets}
            icon={<StorageIcon />}
            color="primary"
            loading={loading}
            trend={{ value: 12, isPositive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Presets"
            value={metrics.totalPresets.toLocaleString()}
            icon={<AnalyticsIcon />}
            color="secondary"
            loading={loading}
            trend={{ value: 8.5, isPositive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Models"
            value={metrics.activeModels}
            icon={<PsychologyIcon />}
            color="success"
            loading={loading}
            trend={{ value: 2, isPositive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Accuracy"
            value={`${metrics.accuracyAverage}%`}
            icon={<TrendingUpIcon />}
            color="info"
            loading={loading}
            trend={{ value: 3.2, isPositive: true }}
          />
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={4}>
          <SystemStatus
            systemLoad={metrics.systemLoad}
            memoryUsage={metrics.memoryUsage}
            processingJobs={metrics.processingJobs}
            apiRequests={metrics.apiRequests}
            loading={loading}
          />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <QuickActions />
        </Grid>

        {/* Activity Feed */}
        <Grid item xs={12} md={4}>
          <ActivityFeed />
        </Grid>

        {/* Latent Space Visualization */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Latent Space Explorer
              </Typography>
              <Box sx={{ height: 400, position: 'relative' }}>
                <LatentSpaceVisualization />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Models */}
        <Grid item xs={12} md={4}>
          <RecentModels />
        </Grid>

        {/* Dataset Overview */}
        <Grid item xs={12}>
          <DatasetOverview />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;