import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import './App.css'

// Import pages
import LandingPage from '@/pages/LandingPage'
import Dashboard from '@/pages/Dashboard'
import DealsPage from '@/pages/DealsPage'
import PodcastPage from '@/pages/PodcastPage'
import SettingsPage from '@/pages/SettingsPage'
import PricingPage from '@/pages/PricingPage'
import BlogPage from '@/pages/BlogPage'
import SignInPage from '@/pages/SignInPage'
import SignUpPage from '@/pages/SignUpPage'

// Import layout components
import Navbar from '@/components/layout/Navbar'
import Sidebar from '@/components/layout/Sidebar'
import Footer from '@/components/layout/Footer'

// Clerk configuration
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPubKey) {
  throw new Error("Missing Publishable Key")
}

function App() {
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
  )
}

export default App
