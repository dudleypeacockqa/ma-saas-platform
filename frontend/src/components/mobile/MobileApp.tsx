/**
 * Mobile App Wrapper Component
 * Sprint 25: Main mobile application container with responsive layout switching
 */

import React, { useState, useEffect } from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import { Routes, Route, useLocation } from 'react-router-dom';

// Mobile components
import MobileNavigation from './MobileNavigation';
import MobileDashboard from './MobileDashboard';
import MobilePipeline from '../deals/components/MobilePipeline';
import MobileActivity from '../deals/components/MobileActivity';
import PhotoCapture from './PhotoCapture';

// Services
import { useHaptics } from '../../services/haptics';
import { useMobile } from '../../hooks/useMobile';
import { useWebSocket } from '../../services/websocket';
import { usePushNotifications } from '../../services/pushNotifications';
import { useOfflineSync } from '../../services/offlineSync';

// Context and state management
import { useAuth } from '@clerk/clerk-react';

interface MobileAppProps {
  onThemeToggle?: () => void;
  onLogout?: () => void;
}

const MobileApp: React.FC<MobileAppProps> = ({
  onThemeToggle,
  onLogout,
}) => {
  const theme = useTheme();
  const location = useLocation();
  const { getToken, user } = useAuth();

  // Mobile hooks
  const mobile = useMobile();
  const haptics = useHaptics();
  const webSocket = useWebSocket();
  const pushNotifications = usePushNotifications();
  const offlineSync = useOfflineSync();

  // State
  const [notifications, setNotifications] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Initialize mobile features on mount
  useEffect(() => {
    initializeMobileFeatures();
  }, [user]);

  const initializeMobileFeatures = async () => {
    if (!user) return;

    try {
      // Initialize WebSocket connection
      const token = await getToken();
      if (token && user.publicMetadata?.organizationId) {
        webSocket.connect(token, user.publicMetadata.organizationId as string);
      }

      // Setup push notifications if supported
      if (pushNotifications.isSupported()) {
        const permission = await pushNotifications.requestPermission();
        if (permission === 'granted') {
          await pushNotifications.subscribe(
            user.id,
            user.publicMetadata?.organizationId as string || ''
          );
        }
      }

      // Setup WebSocket event listeners
      webSocket.on('notification', (data) => {
        setNotifications(prev => prev + 1);
        haptics.notification();

        // Show local notification if page is not visible
        if (document.hidden) {
          pushNotifications.showLocalNotification({
            title: data.title,
            body: data.message,
            data: data.data,
          });
        }
      });

      webSocket.on('connection_status', (status) => {
        if (status === 'connected') {
          haptics.connectionRestored();
        } else if (status === 'disconnected') {
          haptics.connectionLost();
        }
      });

    } catch (error) {
      console.error('Failed to initialize mobile features:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    haptics.pullToRefresh();

    try {
      // Sync offline data
      await offlineSync.syncPendingRequests();

      // Refresh current page data
      // This would trigger data refetches based on current route

    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setTimeout(() => setIsRefreshing(false), 1000);
    }
  };

  const handlePhotoCapture = async (photo: any) => {
    haptics.success();

    // Handle photo upload or storage
    try {
      // This would integrate with your document/media API
      console.log('Photo captured:', photo);
    } catch (error) {
      console.error('Photo upload failed:', error);
      haptics.error();
    }
  };

  // Don't render on desktop
  if (!mobile.deviceInfo.isMobile && !mobile.deviceInfo.isTablet) {
    return null;
  }

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        overflow: 'hidden',
      }}
    >
      {/* Mobile Navigation */}
      <MobileNavigation
        user={{
          firstName: user?.firstName || '',
          lastName: user?.lastName || '',
          email: user?.emailAddresses[0]?.emailAddress || '',
          imageUrl: user?.imageUrl,
        }}
        notificationCount={notifications}
        onLogout={onLogout}
        onThemeToggle={onThemeToggle}
      />

      {/* Main Content Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          WebkitOverflowScrolling: 'touch', // Smooth scrolling on iOS
        }}
      >
        <Routes>
          {/* Mobile Dashboard */}
          <Route
            index
            element={
              <MobileDashboard
                user={{
                  firstName: user?.firstName || '',
                  lastName: user?.lastName || '',
                  imageUrl: user?.imageUrl,
                }}
                notifications={notifications}
                onRefresh={handleRefresh}
              />
            }
          />

          {/* Mobile Deals */}
          <Route path="deals" element={<MobilePipeline />} />
          <Route path="deals/mobile-pipeline" element={<MobilePipeline />} />
          <Route path="deals/:id/activity" element={<MobileActivity />} />

          {/* Other mobile routes would go here */}
          <Route path="documents" element={<div>Mobile Documents</div>} />
          <Route path="teams" element={<div>Mobile Teams</div>} />
          <Route path="analytics" element={<div>Mobile Analytics</div>} />
        </Routes>
      </Box>

      {/* Photo Capture Component */}
      <PhotoCapture
        onPhotoCapture={handlePhotoCapture}
        documentMode={location.pathname.includes('documents')}
        allowMultiple={false}
        autoEnhance={true}
      />

      {/* Connection Status Indicator */}
      {!mobile.isOnline && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bgcolor: 'error.main',
            color: 'error.contrastText',
            textAlign: 'center',
            py: 0.5,
            fontSize: '0.875rem',
            zIndex: theme.zIndex.snackbar,
          }}
        >
          No internet connection - Working offline
        </Box>
      )}

      {/* Performance Monitor (Development only) */}
      {process.env.NODE_ENV === 'development' && (
        <Box
          sx={{
            position: 'fixed',
            top: 10,
            left: 10,
            bgcolor: 'rgba(0,0,0,0.8)',
            color: 'white',
            p: 1,
            borderRadius: 1,
            fontSize: '0.75rem',
            zIndex: 9999,
          }}
        >
          <div>Battery: {mobile.battery?.level || 'N/A'}%</div>
          <div>Network: {mobile.network?.effectiveType || 'N/A'}</div>
          <div>Online: {mobile.isOnline ? 'Yes' : 'No'}</div>
          <div>WebSocket: {webSocket.isConnected() ? 'Connected' : 'Disconnected'}</div>
        </Box>
      )}
    </Box>
  );
};

export default MobileApp;