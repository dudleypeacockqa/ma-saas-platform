import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { ClerkProvider, SignIn, SignUp, useAuth, useUser, useOrganization, RedirectToSignIn } from '@clerk/clerk-react'
import Dashboard from './components/Dashboard'
import UserProfile from './components/UserProfile'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

function ConfigError() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mb-4 mx-auto">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">Configuration Required</h2>
        <p className="text-gray-600 mb-4 text-center">
          The Clerk authentication key is not configured. Please add your Clerk publishable key to continue.
        </p>
        <div className="bg-gray-50 rounded p-3 mb-4">
          <p className="text-sm font-mono text-gray-700">
            VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
          </p>
        </div>
        <ol className="text-sm text-gray-600 space-y-2">
          <li>1. Get your key from <a href="https://dashboard.clerk.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Clerk Dashboard</a></li>
          <li>2. Add it to <code className="bg-gray-100 px-1 rounded">frontend/.env.local</code></li>
          <li>3. Restart the development server</li>
        </ol>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading authentication...</p>
        </div>
      </div>
    )
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />
  }

  return children
}

function PublicRoute({ children }) {
  const { isLoaded, isSignedIn } = useAuth()
  const navigate = useNavigate()

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading...</p>
        </div>
      </div>
    )
  }

  if (isSignedIn) {
    navigate('/dashboard')
    return null
  }

  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/sign-in/*"
        element={
          <PublicRoute>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
              <SignIn
                routing="path"
                path="/sign-in"
                signUpUrl="/sign-up"
                appearance={{
                  elements: {
                    rootBox: "mx-auto",
                    card: "shadow-2xl",
                    headerTitle: "text-2xl font-bold",
                    headerSubtitle: "text-gray-600",
                    formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
                    footerActionLink: "text-blue-600 hover:text-blue-700",
                    identityPreviewEditButton: "text-blue-600 hover:text-blue-700",
                    formFieldInput: "border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    formFieldLabel: "text-gray-700",
                    dividerLine: "bg-gray-200",
                    dividerText: "text-gray-500",
                    socialButtonsBlockButton: "border-gray-300 hover:bg-gray-50",
                    socialButtonsBlockButtonText: "text-gray-700",
                    formHeaderTitle: "text-xl font-semibold",
                    formHeaderSubtitle: "text-gray-600",
                    otpCodeFieldInput: "border-gray-300 focus:border-blue-500",
                  },
                  layout: {
                    socialButtonsPlacement: "bottom",
                    socialButtonsVariant: "blockButton",
                  },
                  variables: {
                    colorPrimary: "#2563eb",
                    colorText: "#111827",
                    colorTextSecondary: "#6b7280",
                    colorInputText: "#111827",
                    colorBackground: "#ffffff",
                    colorInputBackground: "#ffffff",
                    colorDanger: "#ef4444",
                    colorSuccess: "#10b981",
                    colorWarning: "#f59e0b",
                    colorNeutral: "#6b7280",
                    fontFamily: "Inter, system-ui, sans-serif",
                    borderRadius: "0.5rem",
                    spacingUnit: "1rem",
                  }
                }}
              />
            </div>
          </PublicRoute>
        }
      />
      <Route
        path="/sign-up/*"
        element={
          <PublicRoute>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
              <SignUp
                routing="path"
                path="/sign-up"
                signInUrl="/sign-in"
                appearance={{
                  elements: {
                    rootBox: "mx-auto",
                    card: "shadow-2xl",
                    headerTitle: "text-2xl font-bold",
                    headerSubtitle: "text-gray-600",
                    formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
                    footerActionLink: "text-blue-600 hover:text-blue-700",
                    identityPreviewEditButton: "text-blue-600 hover:text-blue-700",
                    formFieldInput: "border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    formFieldLabel: "text-gray-700",
                    dividerLine: "bg-gray-200",
                    dividerText: "text-gray-500",
                    socialButtonsBlockButton: "border-gray-300 hover:bg-gray-50",
                    socialButtonsBlockButtonText: "text-gray-700",
                    formHeaderTitle: "text-xl font-semibold",
                    formHeaderSubtitle: "text-gray-600",
                    otpCodeFieldInput: "border-gray-300 focus:border-blue-500",
                  },
                  layout: {
                    socialButtonsPlacement: "bottom",
                    socialButtonsVariant: "blockButton",
                  },
                  variables: {
                    colorPrimary: "#2563eb",
                    colorText: "#111827",
                    colorTextSecondary: "#6b7280",
                    colorInputText: "#111827",
                    colorBackground: "#ffffff",
                    colorInputBackground: "#ffffff",
                    colorDanger: "#ef4444",
                    colorSuccess: "#10b981",
                    colorWarning: "#f59e0b",
                    colorNeutral: "#6b7280",
                    fontFamily: "Inter, system-ui, sans-serif",
                    borderRadius: "0.5rem",
                    spacingUnit: "1rem",
                  }
                }}
              />
            </div>
          </PublicRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <UserProfile />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

function App() {
  // Show configuration error if no valid key
  if (!publishableKey || publishableKey === 'pk_test_YOUR_CLERK_PUBLISHABLE_KEY_HERE') {
    return (
      <Router>
        <ConfigError />
      </Router>
    )
  }

  return (
    <Router>
      <ClerkProvider
        publishableKey={publishableKey}
        appearance={{
          baseTheme: undefined,
          variables: {
            colorPrimary: "#2563eb",
            colorText: "#111827",
            colorTextSecondary: "#6b7280",
            colorBackground: "#ffffff",
            fontFamily: "Inter, system-ui, sans-serif",
            borderRadius: "0.5rem",
          }
        }}
      >
        <AppRoutes />
      </ClerkProvider>
    </Router>
  )
}

export default App