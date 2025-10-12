/**
 * Mobile Navigation Component
 * Sprint 24: Optimized mobile navigation with bottom tab bar and gesture support
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  BottomNavigation,
  BottomNavigationAction,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  useTheme,
  useMediaQuery,
  Slide,
  Paper,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  BusinessCenter as DealsIcon,
  Description as DocumentsIcon,
  People as TeamIcon,
  Analytics as AnalyticsIcon,
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
  Person as ProfileIcon,
  ExitToApp as LogoutIcon,
  Brightness4 as ThemeIcon,
  Chat as ChatIcon,
  Phone as CallIcon,
  VideoCall as VideoIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useHaptics } from '../../services/haptics';

interface NavigationItem {
  label: string;
  value: string;
  icon: React.ReactElement;
  path: string;
  badge?: number;
}

interface MobileNavigationProps {
  user?: {
    firstName?: string;
    lastName?: string;
    email?: string;
    imageUrl?: string;
  };
  notificationCount?: number;
  onLogout?: () => void;
  onThemeToggle?: () => void;
}

const MobileNavigation: React.FC<MobileNavigationProps> = ({
  user,
  notificationCount = 0,
  onLogout,
  onThemeToggle,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const navigate = useNavigate();
  const haptics = useHaptics();

  const [currentTab, setCurrentTab] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  // Main navigation tabs
  const navigationTabs: NavigationItem[] = [
    {
      label: 'Deals',
      value: 'deals',
      icon: <DealsIcon />,
      path: '/deals',
    },
    {
      label: 'Documents',
      value: 'documents',
      icon: <DocumentsIcon />,
      path: '/documents',
    },
    {
      label: 'Team',
      value: 'team',
      icon: <TeamIcon />,
      path: '/teams',
    },
    {
      label: 'Analytics',
      value: 'analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
    },
  ];

  // Drawer menu items
  const drawerItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { label: 'Profile', icon: <ProfileIcon />, path: '/profile' },
    { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    { label: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { label: 'Call', icon: <CallIcon />, path: '/call' },
    { label: 'Video', icon: <VideoIcon />, path: '/video' },
  ];

  // Update current tab based on location
  useEffect(() => {
    const currentPath = location.pathname;
    const tabIndex = navigationTabs.findIndex(tab =>
      currentPath.startsWith(tab.path)
    );
    if (tabIndex >= 0) {
      setCurrentTab(tabIndex);
    }
  }, [location.pathname]);

  // Hide/show navigation on scroll
  useEffect(() => {
    if (!isMobile) return;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const isScrollingDown = currentScrollY > lastScrollY;

      // Hide when scrolling down, show when scrolling up
      if (isScrollingDown && currentScrollY > 50) {
        setIsVisible(false);
      } else if (!isScrollingDown || currentScrollY < 50) {
        setIsVisible(true);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY, isMobile]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    const tab = navigationTabs[newValue];
    if (tab) {
      setCurrentTab(newValue);
      navigate(tab.path);
      haptics.navigation();
    }
  };

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
    haptics.buttonPress();
  };

  const handleDrawerItemClick = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
    haptics.navigation();
  };

  const handleLogout = () => {
    onLogout?.();
    setDrawerOpen(false);
    haptics.buttonPress();
  };

  if (!isMobile) {
    return null; // Only show on mobile
  }

  return (
    <>
      {/* Top App Bar */}
      <Slide direction="down" in={isVisible} mountOnEnter unmountOnExit>
        <AppBar
          position="fixed"
          sx={{
            zIndex: theme.zIndex.appBar,
            bgcolor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>

            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              M&A Platform
            </Typography>

            <IconButton>
              <SearchIcon />
            </IconButton>

            <IconButton>
              <Badge badgeContent={notificationCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>

            <IconButton onClick={() => navigate('/profile')}>
              <Avatar
                src={user?.imageUrl}
                sx={{ width: 32, height: 32 }}
              >
                {user?.firstName?.[0]}{user?.lastName?.[0]}
              </Avatar>
            </IconButton>
          </Toolbar>
        </AppBar>
      </Slide>

      {/* Bottom Navigation */}
      <Slide direction="up" in={isVisible} mountOnEnter unmountOnExit>
        <Paper
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: theme.zIndex.appBar,
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
          elevation={8}
        >
          <BottomNavigation
            value={currentTab}
            onChange={handleTabChange}
            showLabels
            sx={{
              '& .MuiBottomNavigationAction-root': {
                minWidth: 'auto',
                px: 1,
              },
            }}
          >
            {navigationTabs.map((tab, index) => (
              <BottomNavigationAction
                key={tab.value}
                label={tab.label}
                icon={
                  tab.badge ? (
                    <Badge badgeContent={tab.badge} color="error">
                      {tab.icon}
                    </Badge>
                  ) : (
                    tab.icon
                  )
                }
                sx={{
                  '&.Mui-selected': {
                    color: theme.palette.primary.main,
                  },
                }}
              />
            ))}
          </BottomNavigation>
        </Paper>
      </Slide>

      {/* Navigation Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        PaperProps={{
          sx: {
            width: 280,
            maxWidth: '80vw',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          {/* User Info */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar
              src={user?.imageUrl}
              sx={{ width: 48, height: 48, mr: 2 }}
            >
              {user?.firstName?.[0]}{user?.lastName?.[0]}
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={600}>
                {user?.firstName} {user?.lastName}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Navigation Items */}
          <List>
            {drawerItems.map((item) => (
              <ListItemButton
                key={item.label}
                onClick={() => handleDrawerItemClick(item.path)}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  '&:hover': {
                    bgcolor: theme.palette.action.hover,
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}

            <Divider sx={{ my: 2 }} />

            {/* Theme Toggle */}
            <ListItemButton
              onClick={() => {
                onThemeToggle?.();
                haptics.toggleSwitch();
              }}
              sx={{ borderRadius: 1, mb: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <ThemeIcon />
              </ListItemIcon>
              <ListItemText primary="Dark Mode" />
            </ListItemButton>

            {/* Logout */}
            <ListItemButton
              onClick={handleLogout}
              sx={{
                borderRadius: 1,
                color: theme.palette.error.main,
                '&:hover': {
                  bgcolor: theme.palette.error.light + '20',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40, color: 'inherit' }}>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItemButton>
          </List>
        </Box>
      </Drawer>

      {/* Spacer for fixed navigation */}
      <Box sx={{ pb: 7 }} /> {/* Bottom navigation height */}
      <Box sx={{ pt: 8 }} /> {/* Top app bar height */}
    </>
  );
};

export default MobileNavigation;