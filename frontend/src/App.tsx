import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Toaster } from '@/components/ui/sonner';
import { ThemeProvider } from '@/components/theme-provider';
import ErrorBoundary from '@/components/ErrorBoundary';
import './App.css';

// Public pages (Marketing website)
import HomePage from '@/pages/public/HomePage';
import CommunityPage from '@/pages/public/CommunityPage';
import AboutPage from '@/pages/AboutPage';
import PricingPage from '@/pages/PricingPage';
import BlogPage from '@/pages/BlogPage';
import SignInPage from '@/pages/auth/SignInPage';
import SignUpPage from '@/pages/auth/SignUpPage';

// M&A Service Pages (Public)
import FinancialIntelligencePage from '@/pages/services/FinancialIntelligencePage';
import TemplateEnginePage from '@/pages/services/TemplateEnginePage';
import OfferStackGeneratorPage from '@/pages/services/OfferStackGeneratorPage';
import DealMatchingPage from '@/pages/services/DealMatchingPage';
import ValuationEnginePage from '@/pages/services/ValuationEnginePage';
import PlatformOverviewPage from '@/pages/PlatformOverviewPage';

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
import UserSettings from '@/pages/SettingsPage';

// Layout components
import PublicLayout from '@/components/layouts/PublicLayout';
import PlatformLayout from '@/components/layouts/PlatformLayout';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import AnalyticsListener from '@/components/analytics/AnalyticsListener';

// Clerk configuration
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_live_Y2xlcmsuMTAwZGF5c2FuZGJleW9uZC5jb20k';

function App() {
  return (
    <ErrorBoundary>
      <ClerkProvider publishableKey={clerkPubKey}>
        <ThemeProvider defaultTheme="light" storageKey="ma-platform-theme">
          <Router>
            <AnalyticsListener />
            <div className="min-h-screen bg-background">

            {/* Public Routes - Professional M&A Marketing Website */}
            <SignedOut>
              <Routes>
                {/* Homepage - Professional M&A Platform */}
                <Route
                  path="/"
                  element={
                    <>
                      <Navbar />
                      <HomePage />
                      <Footer />
                    </>
                  }
                />

                {/* Core Marketing Pages */}
                <Route
                  path="/about"
                  element={
                    <>
                      <Navbar />
                      <AboutPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/community"
                  element={
                    <>
                      <Navbar />
                      <CommunityPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/platform"
                  element={
                    <>
                      <Navbar />
                      <PlatformOverviewPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/pricing"
                  element={
                    <>
                      <Navbar />
                      <PricingPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/blog"
                  element={
                    <>
                      <Navbar />
                      <BlogPage />
                      <Footer />
                    </>
                  }
                />

                {/* M&A Service Detail Pages */}
                <Route
                  path="/services/financial-intelligence"
                  element={
                    <>
                      <Navbar />
                      <FinancialIntelligencePage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/services/template-engine"
                  element={
                    <>
                      <Navbar />
                      <TemplateEnginePage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/services/offer-generator"
                  element={
                    <>
                      <Navbar />
                      <OfferStackGeneratorPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/services/deal-matching"
                  element={
                    <>
                      <Navbar />
                      <DealMatchingPage />
                      <Footer />
                    </>
                  }
                />
                <Route
                  path="/services/valuation-engine"
                  element={
                    <>
                      <Navbar />
                      <ValuationEnginePage />
                      <Footer />
                    </>
                  }
                />

                {/* Authentication pages */}
                <Route path="/sign-in" element={<SignInPage />} />
                <Route path="/sign-up" element={<SignUpPage />} />
              </Routes>
            </SignedOut>

            {/* Authenticated Platform Routes - M&A Professional Application */}
            <SignedIn>
              <Routes>
                <Route path="/" element={<PlatformLayout />}>
                  {/* Default route - Deal Pipeline (Primary landing) */}
                  <Route index element={<DealsPipeline />} />

                  {/* DEALS MANAGEMENT - Based on UX Spec Navigation */}
                  <Route path="deals" element={<DealsPipeline />} />
                  <Route path="deals/pipeline" element={<DealsPipeline />} />
                  <Route path="deals/list" element={<DealsPipeline />} />
                  <Route path="deals/calendar" element={<DealsPipeline />} />
                  <Route path="deals/my" element={<DealsPipeline />} />
                  <Route path="deals/archived" element={<DealsPipeline />} />
                  <Route path="deals/:dealId" element={<DealDetail />} />

                  {/* DOCUMENTS MANAGEMENT - Based on UX Spec Navigation */}
                  <Route path="documents" element={<DocumentLibrary />} />
                  <Route path="documents/templates" element={<DocumentLibrary />} />
                  <Route path="documents/recent" element={<DocumentLibrary />} />
                  <Route path="documents/shared" element={<DocumentLibrary />} />
                  <Route path="documents/trash" element={<DocumentLibrary />} />
                  <Route path="documents/:docId" element={<DocumentReview />} />

                  {/* TEAMS MANAGEMENT - Based on UX Spec Navigation */}
                  <Route path="teams" element={<TeamOverview />} />
                  <Route path="teams/members" element={<TeamMembers />} />
                  <Route path="teams/workload" element={<TeamOverview />} />
                  <Route path="teams/activity" element={<TeamOverview />} />
                  <Route path="teams/settings" element={<TeamOverview />} />

                  {/* ANALYTICS & INSIGHTS - Based on UX Spec Navigation */}
                  <Route path="analytics" element={<ExecutiveDashboard />} />
                  <Route path="analytics/executive" element={<ExecutiveDashboard />} />
                  <Route path="analytics/pipeline" element={<PipelineAnalytics />} />
                  <Route path="analytics/performance" element={<PerformanceMetrics />} />
                  <Route path="analytics/financial" element={<FinancialAnalysis />} />
                  <Route path="analytics/reports" element={<ExecutiveDashboard />} />

                  {/* USER SETTINGS */}
                  <Route path="settings" element={<UserSettings />} />

                  {/* Legacy routes for existing service pages (authenticated access) */}
                  <Route path="services/financial-intelligence" element={<FinancialIntelligencePage />} />
                  <Route path="services/template-engine" element={<TemplateEnginePage />} />
                  <Route path="services/offer-generator" element={<OfferStackGeneratorPage />} />
                  <Route path="services/deal-matching" element={<DealMatchingPage />} />
                  <Route path="services/valuation-engine" element={<ValuationEnginePage />} />
                </Route>
              </Routes>
            </SignedIn>

            <Toaster />
          </div>
        </Router>
      </ThemeProvider>
    </ClerkProvider>
    </ErrorBoundary>
  );
}

export default App;
