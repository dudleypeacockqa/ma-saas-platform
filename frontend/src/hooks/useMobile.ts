/**
 * Mobile Detection and Utilities Hook
 * Sprint 24: Provides mobile-specific functionality and detection
 */

import { useState, useEffect } from 'react';
import { useTheme, useMediaQuery } from '@mui/material';

export interface MobileCapabilities {
  isTouch: boolean;
  hasCamera: boolean;
  hasGeolocation: boolean;
  hasVibration: boolean;
  hasDeviceMotion: boolean;
  hasNotifications: boolean;
  hasServiceWorker: boolean;
  isStandalone: boolean;
  isInstallable: boolean;
}

export interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isIOS: boolean;
  isAndroid: boolean;
  screenWidth: number;
  screenHeight: number;
  pixelRatio: number;
  orientation: 'portrait' | 'landscape';
}

export interface MobileState {
  deviceInfo: DeviceInfo;
  capabilities: MobileCapabilities;
  isOnline: boolean;
  battery?: {
    level: number;
    charging: boolean;
  };
  network?: {
    effectiveType: string;
    downlink: number;
  };
}

export function useMobile() {
  const theme = useTheme();
  const isMobileQuery = useMediaQuery(theme.breakpoints.down('md'));
  const isTabletQuery = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  const [mobileState, setMobileState] = useState<MobileState>(() => {
    const userAgent = navigator.userAgent.toLowerCase();
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isAndroid = /android/.test(userAgent);

    return {
      deviceInfo: {
        isMobile: isMobileQuery,
        isTablet: isTabletQuery,
        isDesktop: !isMobileQuery && !isTabletQuery,
        isIOS,
        isAndroid,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        pixelRatio: window.devicePixelRatio || 1,
        orientation: window.screen.width > window.screen.height ? 'landscape' : 'portrait',
      },
      capabilities: {
        isTouch: 'ontouchstart' in window,
        hasCamera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
        hasGeolocation: 'geolocation' in navigator,
        hasVibration: 'vibrate' in navigator,
        hasDeviceMotion: 'DeviceMotionEvent' in window,
        hasNotifications: 'Notification' in window,
        hasServiceWorker: 'serviceWorker' in navigator,
        isStandalone: window.matchMedia('(display-mode: standalone)').matches,
        isInstallable: false, // Will be updated by beforeinstallprompt event
      },
      isOnline: navigator.onLine,
    };
  });

  // Update device info on resize and orientation change
  useEffect(() => {
    const updateDeviceInfo = () => {
      setMobileState(prev => ({
        ...prev,
        deviceInfo: {
          ...prev.deviceInfo,
          isMobile: isMobileQuery,
          isTablet: isTabletQuery,
          isDesktop: !isMobileQuery && !isTabletQuery,
          screenWidth: window.screen.width,
          screenHeight: window.screen.height,
          orientation: window.screen.width > window.screen.height ? 'landscape' : 'portrait',
        },
      }));
    };

    const mediaQueryList = window.matchMedia('(orientation: portrait)');
    mediaQueryList.addEventListener('change', updateDeviceInfo);
    window.addEventListener('resize', updateDeviceInfo);

    return () => {
      mediaQueryList.removeEventListener('change', updateDeviceInfo);
      window.removeEventListener('resize', updateDeviceInfo);
    };
  }, [isMobileQuery, isTabletQuery]);

  // Monitor online/offline status
  useEffect(() => {
    const updateOnlineStatus = () => {
      setMobileState(prev => ({
        ...prev,
        isOnline: navigator.onLine,
      }));
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, []);

  // Monitor battery status
  useEffect(() => {
    const updateBatteryInfo = async () => {
      if ('getBattery' in navigator) {
        try {
          const battery = await (navigator as any).getBattery();

          const updateBattery = () => {
            setMobileState(prev => ({
              ...prev,
              battery: {
                level: Math.round(battery.level * 100),
                charging: battery.charging,
              },
            }));
          };

          updateBattery();
          battery.addEventListener('levelchange', updateBattery);
          battery.addEventListener('chargingchange', updateBattery);

          return () => {
            battery.removeEventListener('levelchange', updateBattery);
            battery.removeEventListener('chargingchange', updateBattery);
          };
        } catch (error) {
          console.log('Battery API not available:', error);
        }
      }
    };

    updateBatteryInfo();
  }, []);

  // Monitor network information
  useEffect(() => {
    const updateNetworkInfo = () => {
      const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;

      if (connection) {
        setMobileState(prev => ({
          ...prev,
          network: {
            effectiveType: connection.effectiveType || 'unknown',
            downlink: connection.downlink || 0,
          },
        }));
      }
    };

    updateNetworkInfo();

    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
    if (connection) {
      connection.addEventListener('change', updateNetworkInfo);
      return () => connection.removeEventListener('change', updateNetworkInfo);
    }
  }, []);

  // Monitor PWA installability
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setMobileState(prev => ({
        ...prev,
        capabilities: {
          ...prev.capabilities,
          isInstallable: true,
        },
      }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Utility functions
  const requestFullscreen = async (): Promise<boolean> => {
    try {
      if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Fullscreen request failed:', error);
      return false;
    }
  };

  const exitFullscreen = async (): Promise<boolean> => {
    try {
      if (document.exitFullscreen) {
        await document.exitFullscreen();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Exit fullscreen failed:', error);
      return false;
    }
  };

  const lockOrientation = async (orientation: OrientationLockType): Promise<boolean> => {
    try {
      if ('orientation' in screen && 'lock' in screen.orientation) {
        await screen.orientation.lock(orientation);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Orientation lock failed:', error);
      return false;
    }
  };

  const unlockOrientation = (): boolean => {
    try {
      if ('orientation' in screen && 'unlock' in screen.orientation) {
        screen.orientation.unlock();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Orientation unlock failed:', error);
      return false;
    }
  };

  const shareContent = async (data: ShareData): Promise<boolean> => {
    try {
      if ('share' in navigator) {
        await navigator.share(data);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Share failed:', error);
      return false;
    }
  };

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      if ('clipboard' in navigator) {
        await navigator.clipboard.writeText(text);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Copy to clipboard failed:', error);
      return false;
    }
  };

  const requestWakeLock = async (): Promise<WakeLockSentinel | null> => {
    try {
      if ('wakeLock' in navigator) {
        return await navigator.wakeLock.request('screen');
      }
      return null;
    } catch (error) {
      console.error('Wake lock request failed:', error);
      return null;
    }
  };

  const getCurrentPosition = (options?: PositionOptions): Promise<GeolocationPosition> => {
    return new Promise((resolve, reject) => {
      if (!mobileState.capabilities.hasGeolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });
  };

  const watchPosition = (
    callback: PositionCallback,
    errorCallback?: PositionErrorCallback,
    options?: PositionOptions
  ): number | null => {
    if (!mobileState.capabilities.hasGeolocation) {
      return null;
    }

    return navigator.geolocation.watchPosition(callback, errorCallback, options);
  };

  const clearWatch = (watchId: number): void => {
    if (mobileState.capabilities.hasGeolocation) {
      navigator.geolocation.clearWatch(watchId);
    }
  };

  return {
    // State
    ...mobileState,

    // Utility functions
    requestFullscreen,
    exitFullscreen,
    lockOrientation,
    unlockOrientation,
    shareContent,
    copyToClipboard,
    requestWakeLock,

    // Geolocation
    getCurrentPosition,
    watchPosition,
    clearWatch,

    // Helpers
    isLowPowerMode: mobileState.battery ? mobileState.battery.level < 20 && !mobileState.battery.charging : false,
    isSlowNetwork: mobileState.network ? ['slow-2g', '2g'].includes(mobileState.network.effectiveType) : false,
    shouldReduceMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    prefersDarkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
  };
}

export default useMobile;