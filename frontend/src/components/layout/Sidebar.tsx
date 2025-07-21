import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
  Collapse,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Storage as StorageIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  Science as ScienceIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  FileUpload as FileUploadIcon,
  TableView as TableViewIcon,
  TrendingUp as TrendingUpIcon,
  ModelTraining as ModelTrainingIcon,
  Assessment as AssessmentIcon,
  Insights as InsightsIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactElement;
  path?: string;
  children?: NavigationItem[];
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
  },
  {
    id: 'datasets',
    label: 'Datasets',
    icon: <StorageIcon />,
    children: [
      {
        id: 'datasets-overview',
        label: 'Overview',
        icon: <TableViewIcon />,
        path: '/datasets',
      },
      {
        id: 'datasets-upload',
        label: 'Upload',
        icon: <FileUploadIcon />,
        path: '/datasets/upload',
      },
    ],
  },
  {
    id: 'models',
    label: 'Models',
    icon: <PsychologyIcon />,
    children: [
      {
        id: 'models-overview',
        label: 'Overview',
        icon: <AssessmentIcon />,
        path: '/models',
      },
      {
        id: 'models-training',
        label: 'Training',
        icon: <ModelTrainingIcon />,
        path: '/models/training',
      },
      {
        id: 'models-evaluation',
        label: 'Evaluation',
        icon: <TrendingUpIcon />,
        path: '/models/evaluation',
      },
    ],
  },
  {
    id: 'analysis',
    label: 'Analysis',
    icon: <AnalyticsIcon />,
    children: [
      {
        id: 'analysis-realtime',
        label: 'Real-time',
        icon: <InsightsIcon />,
        path: '/analysis/realtime',
      },
      {
        id: 'analysis-comparison',
        label: 'Comparison',
        icon: <AssessmentIcon />,
        path: '/analysis/comparison',
      },
    ],
  },
  {
    id: 'experiments',
    label: 'Experiments',
    icon: <ScienceIcon />,
    path: '/experiments',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
  },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedItems, setExpandedItems] = React.useState<string[]>(['datasets', 'models', 'analysis']);

  const handleItemClick = (item: NavigationItem) => {
    if (item.children) {
      // Toggle expansion
      setExpandedItems(prev =>
        prev.includes(item.id)
          ? prev.filter(id => id !== item.id)
          : [...prev, item.id]
      );
    } else if (item.path) {
      // Navigate to path
      navigate(item.path);
    }
  };

  const isItemActive = (path?: string) => {
    return path && location.pathname === path;
  };

  const isParentActive = (item: NavigationItem) => {
    if (item.children) {
      return item.children.some(child => isItemActive(child.path));
    }
    return false;
  };

  const renderNavigationItem = (item: NavigationItem, level = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.includes(item.id);
    const isActive = isItemActive(item.path);
    const isParentOfActive = isParentActive(item);

    return (
      <React.Fragment key={item.id}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={() => handleItemClick(item)}
            sx={{
              pl: 2 + level * 2,
              py: 1,
              backgroundColor: isActive ? 'primary.main' : 'transparent',
              color: isActive ? 'primary.contrastText' : 'text.primary',
              '&:hover': {
                backgroundColor: isActive ? 'primary.dark' : 'action.hover',
              },
              borderRadius: level === 0 ? '0 25px 25px 0' : 1,
              mr: level === 0 ? 1 : 0,
              mb: level === 0 ? 0.5 : 0,
            }}
          >
            <ListItemIcon
              sx={{
                color: isActive || isParentOfActive ? 'primary.main' : 'text.secondary',
                minWidth: 40,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.label}
              sx={{
                '& .MuiListItemText-primary': {
                  fontSize: level === 0 ? '0.9rem' : '0.8rem',
                  fontWeight: isActive || isParentOfActive ? 600 : 400,
                },
              }}
            />
            {hasChildren && (
              isExpanded ? <ExpandLess /> : <ExpandMore />
            )}
          </ListItemButton>
        </ListItem>
        
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderNavigationItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawerContent = (
    <Box sx={{ width: 300, height: '100%', backgroundColor: 'background.paper' }}>
      {/* Header */}
      <Box sx={{ p: 2, pt: 10 }}>
        <Typography variant="overline" color="text.secondary">
          Navigation
        </Typography>
      </Box>
      
      <Divider />
      
      {/* Navigation Items */}
      <List>
        {navigationItems.map(item => renderNavigationItem(item))}
      </List>
      
      <Box sx={{ flexGrow: 1 }} />
      
      {/* Footer */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          IDM Latent Space v1.0.0
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: open ? 300 : 60,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 300 : 60,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid #2A2A2A',
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;