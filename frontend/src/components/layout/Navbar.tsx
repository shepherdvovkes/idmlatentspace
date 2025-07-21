import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';

interface NavbarProps {
  onToggleSidebar: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [notificationCount] = React.useState(3);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // Implement logout logic
    handleMenuClose();
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
        borderBottom: '1px solid #2A2A2A',
        boxShadow: 'none',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left Section */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="toggle sidebar"
            onClick={onToggleSidebar}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Logo/Icon */}
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: 1,
                background: 'linear-gradient(45deg, #00D4FF 30%, #FF6B00 90%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              IDM
            </Box>
            
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(45deg, #00D4FF 30%, #FF6B00 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Latent Space
            </Typography>
          </Box>
        </Box>

        {/* Center Section - Search could go here */}
        <Box sx={{ flexGrow: 1 }} />

        {/* Right Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={notificationCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Settings">
            <IconButton color="inherit" href="/settings">
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <IconButton
            edge="end"
            aria-label="account of current user"
            aria-controls="user-menu"
            aria-haspopup="true"
            onClick={handleMenuOpen}
            color="inherit"
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: 'primary.main',
                fontSize: '14px',
              }}
            >
              SV
            </Avatar>
          </IconButton>
        </Box>

        {/* User Menu */}
        <Menu
          id="user-menu"
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          sx={{
            '& .MuiPaper-root': {
              backgroundColor: 'background.paper',
              border: '1px solid #2A2A2A',
              mt: 1.5,
              minWidth: 200,
            },
          }}
        >
          <MenuItem onClick={handleMenuClose}>
            <AccountCircleIcon sx={{ mr: 1 }} />
            Profile
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <SettingsIcon sx={{ mr: 1 }} />
            Settings
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <LogoutIcon sx={{ mr: 1 }} />
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;