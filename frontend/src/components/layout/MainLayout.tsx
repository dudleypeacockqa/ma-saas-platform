/**
 * Main Application Layout
 * Provides the shell with sidebar navigation and header
 */

import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Breadcrumbs,
  Link,
  Chip,
  useTheme,
  useMediaQuery,
  Collapse,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  BusinessCenter as DealsIcon,
  Description as DocumentsIcon,
  People as TeamIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  ExpandLess,
  ExpandMore,
  Logout as LogoutIcon,
  Help as HelpIcon,
  KeyboardArrowDown,
} from '@mui/icons-material';

import { RootState } from '@/app/store';
import { toggleSidebar, setSidebarOpen } from '@/app/slices/uiSlice';
import { clearAuth } from '@/app/slices/authSlice';

const drawerWidth = 280;

interface NavItem {
  title: string;
  path?: string;
  icon: React.ReactElement;
  children?: NavItem[];
  badge?: number;
}

const navigationItems: NavItem[] = [
  {
    title: 'Dashboard',
    path: '/',
    icon: <DashboardIcon />,
  },
  {
    title: 'Deals',
    icon: <DealsIcon />,
    children: [
      { title: 'All Deals', path: '/deals', icon: <DealsIcon /> },
      { title: 'Pipeline View', path: '/deals/pipeline', icon: <DealsIcon /> },
      { title: 'Create Deal', path: '/deals/new', icon: <DealsIcon /> },
    ],
  },
  {
    title: 'Documents',
    path: '/documents',
    icon: <DocumentsIcon />,
    badge: 3,
  },
  {
    title: 'Team',
    path: '/team',
    icon: <TeamIcon />,
  },
  {
    title: 'Analytics',
    path: '/analytics',
    icon: <AnalyticsIcon />,
  },
  {
    title: 'Settings',
    path: '/settings',
    icon: <SettingsIcon />,
  },
];

export const MainLayout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const { sidebarOpen } = useSelector((state: RootState) => state.ui);
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const handleDrawerToggle = () => {
    dispatch(toggleSidebar());
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(clearAuth());
    navigate('/login');
    handleProfileMenuClose();
  };

  const handleNavItemClick = (item: NavItem) => {
    if (item.children) {
      const isExpanded = expandedItems.includes(item.title);
      setExpandedItems(
        isExpanded
          ? expandedItems.filter(i => i !== item.title)
          : [...expandedItems, item.title]
      );
    } else if (item.path) {
      navigate(item.path);
      if (isMobile) {
        dispatch(setSidebarOpen(false));
      }
    }
  };

  const isNavItemActive = (item: NavItem): boolean => {
    if (item.path) {
      return location.pathname === item.path;
    }
    if (item.children) {
      return item.children.some(child => child.path === location.pathname);
    }
    return false;
  };

  const renderNavItem = (item: NavItem, depth = 0) => {
    const hasChildren = Boolean(item.children);
    const isExpanded = expandedItems.includes(item.title);
    const isActive = isNavItemActive(item);

    return (
      <React.Fragment key={item.title}>
        <ListItem disablePadding sx={{ display: 'block' }}>
          <ListItemButton
            onClick={() => handleNavItemClick(item)}
            selected={isActive}
            sx={{
              minHeight: 48,
              justifyContent: sidebarOpen ? 'initial' : 'center',
              px: 2.5,
              pl: depth > 0 ? 4 : 2.5,
              borderRadius: 1,
              mx: 1,
              my: 0.5,
              backgroundColor: isActive ? 'action.selected' : 'transparent',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: sidebarOpen ? 3 : 'auto',
                justifyContent: 'center',
                color: isActive ? 'primary.main' : 'inherit',
              }}
            >
              {item.badge ? (
                <Badge badgeContent={item.badge} color="error">
                  {item.icon}
                </Badge>
              ) : (
                item.icon
              )}
            </ListItemIcon>
            <ListItemText
              primary={item.title}
              sx={{
                opacity: sidebarOpen ? 1 : 0,
                color: isActive ? 'primary.main' : 'inherit',
              }}
            />
            {hasChildren && sidebarOpen && (
              <>{isExpanded ? <ExpandLess /> : <ExpandMore />}</>
            )}
          </ListItemButton>
        </ListItem>
        {hasChildren && sidebarOpen && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderNavItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ px: 2, py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          <BusinessCenter sx={{ mr: 2, color: 'primary.main' }} />
          {sidebarOpen && (
            <Box>
              <Typography variant="h6" noWrap component="div" fontWeight="bold">
                M&A Platform
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.organizationName || 'Loading...'}
              </Typography>
            </Box>
          )}
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ flexGrow: 1, py: 1 }}>
        {navigationItems.map(item => renderNavItem(item))}
      </List>
      <Divider />
      {sidebarOpen && user && (
        <Box sx={{ p: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 2,
              borderRadius: 2,
              bgcolor: 'action.hover',
              cursor: 'pointer',
            }}
            onClick={handleProfileMenuOpen}
          >
            <Avatar
              src={user.imageUrl}
              alt={user.firstName}
              sx={{ width: 32, height: 32, mr: 2 }}
            >
              {user.firstName?.[0]}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle2" noWrap>
                {user.firstName} {user.lastName}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {user.email}
              </Typography>
            </Box>
            <KeyboardArrowDown />
          </Box>
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${sidebarOpen ? drawerWidth : 64}px)` },
          ml: { md: `${sidebarOpen ? drawerWidth : 64}px` },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          backgroundColor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }}>
            <Breadcrumbs aria-label="breadcrumb">
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/')}
                underline="hover"
                color="inherit"
              >
                Home
              </Link>
              {location.pathname.split('/').filter(Boolean).map((segment, index, array) => {
                const path = `/${array.slice(0, index + 1).join('/')}`;
                const isLast = index === array.length - 1;
                const label = segment.charAt(0).toUpperCase() + segment.slice(1);

                return isLast ? (
                  <Typography key={path} color="text.primary" variant="body2">
                    {label}
                  </Typography>
                ) : (
                  <Link
                    key={path}
                    component="button"
                    variant="body2"
                    onClick={() => navigate(path)}
                    underline="hover"
                    color="inherit"
                  >
                    {label}
                  </Link>
                );
              })}
            </Breadcrumbs>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <HelpIcon />
            </IconButton>
            {!isMobile && (
              <IconButton
                color="inherit"
                onClick={handleProfileMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar
                  src={user?.imageUrl}
                  alt={user?.firstName}
                  sx={{ width: 32, height: 32 }}
                >
                  {user?.firstName?.[0]}
                </Avatar>
              </IconButton>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { md: sidebarOpen ? drawerWidth : 64 },
          flexShrink: { md: 0 },
        }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={isMobile ? sidebarOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: sidebarOpen ? drawerWidth : 64,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${sidebarOpen ? drawerWidth : 64}px)` },
          mt: 8,
          backgroundColor: 'background.default',
          minHeight: '100vh',
        }}
      >
        <Outlet />
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => { navigate('/profile'); handleProfileMenuClose(); }}>
          <ListItemIcon>
            <AccountIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => { navigate('/settings'); handleProfileMenuClose(); }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
};