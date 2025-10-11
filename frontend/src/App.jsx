import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Toaster } from '@/components/ui/toaster';
import { ThemeProvider } from '@/components/theme-provider';
import './App.css';

// Import pages
import LandingPage from '@/pages/LandingPage';
import Dashboard from '@/pages/Dashboard';
import DealsPage from '@/pages/DealsPage';
import PodcastPage from '@/pages/PodcastPage';
import SettingsPage from '@/pages/SettingsPage';
import PricingPage from '@/pages/PricingPage';
import BlogPage from '@/pages/BlogPage';
import SignInPage from '@/pages/SignInPage';
import SignUpPage from '@/pages/SignUpPage';
import MetricsDashboard from '@/pages/MetricsDashboard';

// Import layout components
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import Footer from '@/components/layout/Footer';

function ConfigError() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mb-4 mx-auto">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">
          Configuration Required
        </h2>
        <p className="text-gray-600 mb-4 text-center">
          The Clerk authentication key is not configured. Please add your Clerk publishable key to
          continue.
        </p>
        <div className="bg-gray-50 rounded p-3 mb-4">
          <p className="text-sm font-mono text-gray-700">VITE_CLERK_PUBLISHABLE_KEY=pk_test_...</p>
        </div>
        <ol className="text-sm text-gray-600 space-y-2">
          <li>
            1. Get your key from{' '}
            <a
              href="https://dashboard.clerk.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Clerk Dashboard
            </a>
          </li>
          <li>
            2. Add it to <code className="bg-gray-100 px-1 rounded">frontend/.env.local</code>
          </li>
          <li>3. Restart the development server</li>
        </ol>
      </div>
    </div>
  );
}

// Clerk configuration
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!clerkPubKey) {
  throw new Error('Missing Publishable Key');
}

function App() {
  // Show configuration error if no valid key
  if (!clerkPubKey || clerkPubKey === 'pk_test_YOUR_CLERK_PUBLISHABLE_KEY_HERE') {
    return (
      <Router>
        <ConfigError />
      </Router>
    );
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <ThemeProvider defaultTheme="light" storageKey="ma-saas-theme">
        <Router>
          <div className="min-h-screen bg-background">
            <SignedOut>
              {/* Public routes */}
              <Navbar />
              <main>
                <Routes>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/pricing" element={<PricingPage />} />
                  <Route path="/blog" element={<BlogPage />} />
                  <Route path="/podcast" element={<PodcastPage />} />
                  <Route path="/sign-in" element={<SignInPage />} />
                  <Route path="/sign-up" element={<SignUpPage />} />
                  <Route path="/metrics" element={<MetricsDashboard />} />
                </Routes>
              </main>
              <Footer />
            </SignedOut>

            <SignedIn>
              {/* Authenticated routes */}
              <div className="flex h-screen">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Navbar />
                  <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/deals" element={<DealsPage />} />
                      <Route path="/podcast" element={<PodcastPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                      <Route path="/pricing" element={<PricingPage />} />
                      <Route path="/blog" element={<BlogPage />} />
                      <Route path="/metrics" element={<MetricsDashboard />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </SignedIn>

            <Toaster />
          </div>
        </Router>
      </ThemeProvider>
    </ClerkProvider>
  );
}

export default App;
