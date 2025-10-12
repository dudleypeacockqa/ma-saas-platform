import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Toaster } from '@/components/ui/sonner';
import { ThemeProvider } from '@/components/theme-provider';
import './App.css';

// Public pages (Marketing website)
import HomePage from '@/pages/public/HomePage';
import AboutPage from '@/pages/public/AboutPage';
import SolutionsPage from '@/pages/public/SolutionsPage';
import PricingPage from '@/pages/public/PricingPage';
import ContactPage from '@/pages/public/ContactPage';
import BlogPage from '@/pages/public/BlogPage';
import SignInPage from '@/pages/auth/SignInPage';
import SignUpPage from '@/pages/auth/SignUpPage';

// Platform pages (Authenticated M&A application)
import DealsPipeline from '@/pages/platform/DealsPipeline';
import DealDetail from '@/pages/platform/DealDetail';
import DocumentLibrary from '@/pages/platform/DocumentLibrary';
import DocumentReview from '@/pages/platform/DocumentReview';
import TeamOverview from '@/pages/platform/TeamOverview';
import TeamMembers from '@/pages/platform/TeamMembers';
import ExecutiveDashboard from '@/pages/platform/ExecutiveDashboard';
import PipelineAnalytics from '@/pages/platform/PipelineAnalytics';
import PerformanceMetrics from '@/pages/platform/PerformanceMetrics';
import FinancialAnalysis from '@/pages/platform/FinancialAnalysis';
import UserSettings from '@/pages/platform/UserSettings';

// Layout components
import PublicLayout from '@/components/layouts/PublicLayout';
import PlatformLayout from '@/components/layouts/PlatformLayout';

// Clerk configuration
const clerkPubKey =
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_live_Y2xlcmsuMTAwZGF5c2FuZGJleW9uZC5jb20k';

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <ThemeProvider defaultTheme="light" storageKey="ma-platform-theme">
        <Router>
          <div className="min-h-screen bg-background">
            {/* Public Routes - Marketing Website */}
            <SignedOut>
              <Routes>
                {/* Marketing website with proper M&A focus */}
                <Route path="/" element={<PublicLayout />}>
                  <Route index element={<HomePage />} />
                  <Route path="about" element={<AboutPage />} />
                  <Route path="solutions" element={<SolutionsPage />} />
                  <Route path="pricing" element={<PricingPage />} />
                  <Route path="contact" element={<ContactPage />} />
                  <Route path="blog" element={<BlogPage />} />
                  <Route path="blog/:slug" element={<BlogPage />} />
                </Route>

                {/* Authentication pages */}
                <Route path="/sign-in" element={<SignInPage />} />
                <Route path="/sign-up" element={<SignUpPage />} />
              </Routes>
            </SignedOut>

            {/* Platform Routes - M&A Application */}
            <SignedIn>
              <Routes>
                <Route path="/" element={<PlatformLayout />}>
                  {/* Default route redirects to deals pipeline */}
                  <Route index element={<DealsPipeline />} />

                  {/* Deals Management */}
                  <Route path="deals" element={<DealsPipeline />} />
                  <Route path="deals/pipeline" element={<DealsPipeline />} />
                  <Route path="deals/:dealId" element={<DealDetail />} />

                  {/* Document Management */}
                  <Route path="documents" element={<DocumentLibrary />} />
                  <Route path="documents/:docId" element={<DocumentReview />} />

                  {/* Team Management */}
                  <Route path="teams" element={<TeamOverview />} />
                  <Route path="teams/members" element={<TeamMembers />} />

                  {/* Analytics & Insights */}
                  <Route path="analytics" element={<ExecutiveDashboard />} />
                  <Route path="analytics/executive" element={<ExecutiveDashboard />} />
                  <Route path="analytics/pipeline" element={<PipelineAnalytics />} />
                  <Route path="analytics/performance" element={<PerformanceMetrics />} />
                  <Route path="analytics/financial" element={<FinancialAnalysis />} />

                  {/* User Settings */}
                  <Route path="settings" element={<UserSettings />} />
                </Route>
              </Routes>
            </SignedIn>

            <Toaster />
          </div>
        </Router>
      </ThemeProvider>
    </ClerkProvider>
  );
}

export default App;
