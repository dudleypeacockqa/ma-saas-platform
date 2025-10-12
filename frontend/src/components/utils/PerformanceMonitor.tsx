/**
 * Performance Monitor Component
 * Sprint 25: Real-time performance monitoring and optimization
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Card, CardContent, Chip, Stack } from '@mui/material';
import { useMobile } from '../../hooks/useMobile';

interface PerformanceMetrics {
  fps: number;
  memoryUsage: number;
  navigationTiming: {
    loadTime: number;
    domContentLoaded: number;
    firstPaint: number;
    firstContentfulPaint: number;
  };
  vitals: {
    cls: number;
    fid: number;
    lcp: number;
  };
  bundleSize: number;
  resourceCount: number;
}

const PerformanceMonitor: React.FC = () => {
  const mobile = useMobile();
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  // Only show in development mode
  const isDevelopment = process.env.NODE_ENV === 'development';

  useEffect(() => {
    if (!isDevelopment) return;

    // Show on mobile devices or when specifically enabled
    if (mobile.deviceInfo.isMobile || localStorage.getItem('show-perf-monitor') === 'true') {
      setIsVisible(true);
      startMonitoring();
    }

    // Toggle visibility with keyboard shortcut
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        setIsVisible(prev => !prev);
        if (!isVisible) {
          startMonitoring();
        }
      }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, [isDevelopment, mobile.deviceInfo.isMobile, isVisible]);

  const startMonitoring = useCallback(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let fpsValue = 0;

    // FPS monitoring
    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();

      if (currentTime >= lastTime + 1000) {
        fpsValue = Math.round((frameCount * 1000) / (currentTime - lastTime));
        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(measureFPS);
    };

    measureFPS();

    // Collect metrics every 2 seconds
    const metricsInterval = setInterval(() => {
      const performanceEntries = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');
      const resourceEntries = performance.getEntriesByType('resource');

      // Memory usage (Chrome only)
      const memoryInfo = (performance as any).memory;
      const memoryUsage = memoryInfo ?
        Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024) : 0;

      // Navigation timing
      const navigationTiming = {
        loadTime: Math.round(performanceEntries.loadEventEnd - performanceEntries.navigationStart),
        domContentLoaded: Math.round(performanceEntries.domContentLoadedEventEnd - performanceEntries.navigationStart),
        firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
      };

      // Web Vitals (simplified)
      const vitals = {
        cls: 0, // Would need to implement layout shift observer
        fid: 0, // Would need to implement first input delay observer
        lcp: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
      };

      // Bundle size estimation
      const bundleSize = resourceEntries
        .filter(entry => entry.name.includes('.js') || entry.name.includes('.css'))
        .reduce((total, entry) => total + (entry.transferSize || 0), 0);

      setMetrics({
        fps: fpsValue,
        memoryUsage,
        navigationTiming,
        vitals,
        bundleSize: Math.round(bundleSize / 1024), // KB
        resourceCount: resourceEntries.length,
      });
    }, 2000);

    return () => clearInterval(metricsInterval);
  }, []);

  if (!isDevelopment || !isVisible || !metrics) {
    return null;
  }

  const getPerformanceColor = (value: number, thresholds: { good: number; poor: number }) => {
    if (value <= thresholds.good) return 'success';
    if (value <= thresholds.poor) return 'warning';
    return 'error';
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 10,
        right: 10,
        zIndex: 9999,
        maxWidth: 300,
        opacity: 0.9,
      }}
    >
      <Card sx={{ bgcolor: 'rgba(0,0,0,0.8)', color: 'white' }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Typography variant="h6" sx={{ mb: 1, fontSize: '0.875rem' }}>
            Performance Monitor
          </Typography>

          <Stack spacing={1}>
            {/* FPS */}
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">FPS:</Typography>
              <Chip
                label={metrics.fps}
                size="small"
                color={getPerformanceColor(60 - metrics.fps, { good: 15, poor: 30 })}
                sx={{ minWidth: 50 }}
              />
            </Stack>

            {/* Memory Usage */}
            {metrics.memoryUsage > 0 && (
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">Memory:</Typography>
                <Chip
                  label={`${metrics.memoryUsage}MB`}
                  size="small"
                  color={getPerformanceColor(metrics.memoryUsage, { good: 50, poor: 100 })}
                  sx={{ minWidth: 50 }}
                />
              </Stack>
            )}

            {/* Load Time */}
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Load:</Typography>
              <Chip
                label={`${Math.round(metrics.navigationTiming.loadTime)}ms`}
                size="small"
                color={getPerformanceColor(metrics.navigationTiming.loadTime, { good: 1000, poor: 3000 })}
                sx={{ minWidth: 50 }}
              />
            </Stack>

            {/* Bundle Size */}
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Bundle:</Typography>
              <Chip
                label={`${metrics.bundleSize}KB`}
                size="small"
                color={getPerformanceColor(metrics.bundleSize, { good: 500, poor: 1000 })}
                sx={{ minWidth: 50 }}
              />
            </Stack>

            {/* Network Status */}
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Network:</Typography>
              <Chip
                label={mobile.isOnline ? 'Online' : 'Offline'}
                size="small"
                color={mobile.isOnline ? 'success' : 'error'}
                sx={{ minWidth: 50 }}
              />
            </Stack>

            {/* Battery (if available) */}
            {mobile.battery && (
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">Battery:</Typography>
                <Chip
                  label={`${mobile.battery.level}%`}
                  size="small"
                  color={getPerformanceColor(100 - mobile.battery.level, { good: 50, poor: 80 })}
                  sx={{ minWidth: 50 }}
                />
              </Stack>
            )}

            {/* Connection Type */}
            {mobile.network && (
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">Connection:</Typography>
                <Chip
                  label={mobile.network.effectiveType}
                  size="small"
                  color={
                    ['4g', '5g'].includes(mobile.network.effectiveType) ? 'success' :
                    mobile.network.effectiveType === '3g' ? 'warning' : 'error'
                  }
                  sx={{ minWidth: 50 }}
                />
              </Stack>
            )}
          </Stack>

          <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.7 }}>
            Ctrl+Shift+P to toggle
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PerformanceMonitor;