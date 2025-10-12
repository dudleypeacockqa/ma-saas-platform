import { SignIn, SignUp, useUser, UserButton } from '@clerk/clerk-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { BarChart3, Users, FileText, TrendingUp, Plus } from 'lucide-react'

const DashboardPage = () => {
  const { isSignedIn, user } = useUser()
  const [authMode, setAuthMode] = useState('signin')

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center pt-16">
        <div className="max-w-md w-full mx-auto px-4">
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-slate-900 mb-2">
                {authMode === 'signin' ? 'Welcome Back' : 'Get Started'}
              </h1>
              <p className="text-slate-600">
                {authMode === 'signin' 
                  ? 'Sign in to your M&A platform' 
                  : 'Create your account and start your free trial'
                }
              </p>
            </div>

            {authMode === 'signin' ? (
              <SignIn 
                appearance={{
                  elements: {
                    formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
                    card: 'shadow-none',
                  }
                }}
              />
            ) : (
              <SignUp 
                appearance={{
                  elements: {
                    formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
                    card: 'shadow-none',
                  }
                }}
              />
            )}

            <div className="mt-6 text-center">
              <button
                onClick={() => setAuthMode(authMode === 'signin' ? 'signup' : 'signin')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                {authMode === 'signin' 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Sign in"
                }
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 pt-16">
      {/* Dashboard Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Welcome back, {user?.firstName || 'User'}!
              </h1>
              <p className="text-slate-600 mt-1">
                Here's what's happening with your M&A deals today.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                New Deal
              </Button>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: 'w-10 h-10'
                  }
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { title: 'Active Deals', value: '23', change: '+15%', icon: BarChart3, color: 'blue' },
            { title: 'Total Value', value: '£347.5M', change: '+23%', icon: TrendingUp, color: 'green' },
            { title: 'Team Members', value: '12', change: '+2', icon: Users, color: 'purple' },
            { title: 'Documents', value: '1,247', change: '+89', icon: FileText, color: 'orange' }
          ].map((stat) => (
            <div key={stat.title} className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm font-medium">{stat.title}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
                  <p className={`text-sm font-medium mt-1 text-${stat.color}-600`}>
                    {stat.change} from last month
                  </p>
                </div>
                <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                  <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Pipeline Overview */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Deal Pipeline</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { stage: 'Sourcing', count: 8, value: '£45.2M', color: 'slate' },
              { stage: 'Qualifying', count: 5, value: '£82.5M', color: 'blue' },
              { stage: 'Due Diligence', count: 3, value: '£124.3M', color: 'purple' },
              { stage: 'Closing', count: 2, value: '£95.7M', color: 'green' }
            ].map((stage) => (
              <div key={stage.stage} className={`bg-${stage.color}-50 rounded-lg p-4 border border-${stage.color}-200`}>
                <h3 className={`font-semibold text-${stage.color}-900 mb-2`}>{stage.stage}</h3>
                <p className={`text-2xl font-bold text-${stage.color}-700`}>{stage.count}</p>
                <p className={`text-sm text-${stage.color}-600`}>{stage.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { action: 'New deal created', deal: 'TechCo Acquisition', time: '2 hours ago', user: 'Sarah Chen' },
              { action: 'Document uploaded', deal: 'RetailX Merger', time: '4 hours ago', user: 'James Mitchell' },
              { action: 'Stage updated', deal: 'FinServ Deal', time: '6 hours ago', user: 'Victoria Hammond' },
              { action: 'Meeting scheduled', deal: 'ManuCo Acquisition', time: '1 day ago', user: 'Tom Brown' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-slate-100 last:border-b-0">
                <div>
                  <p className="font-medium text-slate-900">{activity.action}</p>
                  <p className="text-sm text-slate-600">{activity.deal} • {activity.user}</p>
                </div>
                <p className="text-sm text-slate-500">{activity.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
