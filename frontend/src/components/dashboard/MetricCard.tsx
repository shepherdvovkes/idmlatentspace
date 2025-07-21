import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';

interface Trend {
  value: number;
  isPositive: boolean;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  loading?: boolean;
  trend?: Trend;
  subtitle?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color,
  loading = false,
  trend,
  subtitle,
}) => {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 48,
              height: 48,
              borderRadius: 2,
              backgroundColor: `${color}.main`,
              color: `${color}.contrastText`,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Typography variant="h4" component="div" fontWeight="bold">
                {value}
              </Typography>
            )}
          </Box>
        </Box>

        {/* Trend Indicator */}
        {trend && !loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Chip
              icon={
                trend.isPositive ? (
                  <TrendingUpIcon sx={{ fontSize: 16 }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 16 }} />
                )
              }
              label={`${trend.isPositive ? '+' : ''}${trend.value}%`}
              size="small"
              color={trend.isPositive ? 'success' : 'error'}
              variant="outlined"
              sx={{ fontSize: '0.75rem' }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ ml: 1 }}
            >
              vs last period
            </Typography>
          </Box>
        )}

        {/* Subtitle */}
        {subtitle && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 1, display: 'block' }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;