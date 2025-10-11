/**
 * Main Application Component
 * Sets up routing, providers, and global configuration
 */

import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ClerkProvider, SignedIn, SignedOut, RedirectToSignIn, useUser, useAuth } from '@clerk/clerk-react';

import { store } from '@/app/store';
import { setUser } from '@/app/slices/authSlice';
import { MainLayout } from '@/components/layout/MainLayout';
import { theme } from '@/styles/theme';

// Lazy load pages for code splitting
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const DealList = lazy(() => import('@/features/deals/components/DealList').then(m => ({ default: m.DealList })));
const DealForm = lazy(() => import('@/features/deals/components/DealForm').then(m => ({ default: m.DealForm })));
const DealDetail = lazy(() => import('@/features/deals/components/DealDetail').then(m => ({ default: m.DealDetail })));
const PipelineView = lazy(() => import('@/pages/deals/PipelineView'));
const Documents = lazy(() => import('@/pages/Documents'));
const Team = lazy(() => import('@/pages/Team'));
const Analytics = lazy(() => import('@/pages/Analytics'));
const Settings = lazy(() => import('@/pages/Settings'));
const Profile = lazy(() => import('@/pages/Profile'));
const NotFound = lazy(() => import('@/pages/NotFound'));

// Get Clerk publishable key from environment
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!clerkPubKey) {
  throw new Error('Missing Clerk Publishable Key');
}

// Loading component
const LoadingFallback = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
    }}
  >
    <CircularProgress />
  </Box>
);

// Auth sync component
const AuthSync: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const clerkUser = useUser();
  const { getToken } = useAuth();

  useEffect(() => {
    const syncAuth = async () => {
      if (clerkUser.isLoaded && clerkUser.user) {
        const token = await getToken();

        const user = {
          id: clerkUser.user.id,
          email: clerkUser.user.primaryEmailAddress?.emailAddress || '',
          firstName: clerkUser.user.firstName || undefined,
          lastName: clerkUser.user.lastName || undefined,
          organizationId: clerkUser.user.publicMetadata.organizationId as string || '',
          organizationName: clerkUser.user.publicMetadata.organizationName as string || undefined,
          role: (clerkUser.user.publicMetadata.role as 'admin' | 'member' | 'viewer') || 'member',
          imageUrl: clerkUser.user.imageUrl || undefined,
        };

        store.dispatch(setUser({ user, token: token || '' }));
      }
    };

    syncAuth();
  }, [clerkUser.isLoaded, clerkUser.user, getToken]);

  return <>{children}</>;
};

// Protected routes wrapper
const ProtectedRoutes = () => (
  <SignedIn>
    <AuthSync>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={
            <Suspense fallback={<LoadingFallback />}>
              <Dashboard />
            </Suspense>
          } />

          {/* Deals routes */}
          <Route path="deals">
            <Route index element={
              <Suspense fallback={<LoadingFallback />}>
                <DealList />
              </Suspense>
            } />
            <Route path="new" element={
              <Suspense fallback={<LoadingFallback />}>
                <DealForm />
              </Suspense>
            } />
            <Route path="pipeline" element={
              <Suspense fallback={<LoadingFallback />}>
                <PipelineView />
              </Suspense>
            } />
            <Route path=":id" element={
              <Suspense fallback={<LoadingFallback />}>
                <DealDetail />
              </Suspense>
            } />
            <Route path=":id/edit" element={
              <Suspense fallback={<LoadingFallback />}>
                <DealForm />
              </Suspense>
            } />
          </Route>

          {/* Other routes */}
          <Route path="documents" element={
            <Suspense fallback={<LoadingFallback />}>
              <Documents />
            </Suspense>
          } />
          <Route path="team" element={
            <Suspense fallback={<LoadingFallback />}>
              <Team />
            </Suspense>
          } />
          <Route path="analytics" element={
            <Suspense fallback={<LoadingFallback />}>
              <Analytics />
            </Suspense>
          } />
          <Route path="settings" element={
            <Suspense fallback={<LoadingFallback />}>
              <Settings />
            </Suspense>
          } />
          <Route path="profile" element={
            <Suspense fallback={<LoadingFallback />}>
              <Profile />
            </Suspense>
          } />
          <Route path="*" element={
            <Suspense fallback={<LoadingFallback />}>
              <NotFound />
            </Suspense>
          } />
        </Route>
      </Routes>
    </AuthSync>
  </SignedIn>
);

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <CssBaseline />
            <BrowserRouter>
              <Routes>
                <Route path="/*" element={<ProtectedRoutes />} />
              </Routes>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </BrowserRouter>
          </LocalizationProvider>
        </ThemeProvider>
      </Provider>
    </ClerkProvider>
  );
}

export default App;