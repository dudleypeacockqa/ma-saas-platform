/**
 * Responsive Layout Component
 * Sprint 25: Intelligent layout that switches between desktop and mobile interfaces
 */

import React, { useState, useEffect } from 'react';
import { useTheme, useMediaQuery, Box } from '@mui/material';
import { useAuth } from '@clerk/clerk-react';

// Import both mobile and desktop layouts
import MobileApp from '../mobile/MobileApp';
import { MainLayout } from './MainLayout';

// Performance monitoring
import PerformanceMonitor from '../utils/PerformanceMonitor';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const { signOut } = useAuth();

  // Responsive breakpoints
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  // Theme management
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('ma-platform-theme');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  // Update theme preference
  useEffect(() => {
    localStorage.setItem('ma-platform-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleThemeToggle = () => {
    setIsDarkMode(prev => !prev);
  };

  const handleLogout = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Mobile-first approach: use mobile layout on mobile and tablet
  if (isMobile || isTablet) {
    return (
      <>
        <MobileApp
          onThemeToggle={handleThemeToggle}
          onLogout={handleLogout}
        />
        <PerformanceMonitor />
      </>
    );
  }

  // Desktop layout for larger screens
  return (
    <>
      <MainLayout>
        {children}
      </MainLayout>
      <PerformanceMonitor />
    </>
  );
};

export default ResponsiveLayout;