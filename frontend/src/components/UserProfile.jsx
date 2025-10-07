import { useState } from 'react'
import { useUser, useOrganization, useClerk } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert.jsx'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog.jsx'
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Building2,
  Globe,
  MapPin,
  Calendar,
  Shield,
  Settings,
  LogOut,
  Save,
  Camera,
  Loader2,
  CheckCircle,
  AlertCircle,
  Key,
  Bell,
  Lock,
  Smartphone,
  CreditCard,
  Plus
} from 'lucide-react'
import { Switch } from '@/components/ui/switch.jsx'

function UserProfile() {
  const navigate = useNavigate()
  const { user, isLoaded } = useUser()
  const { organization } = useOrganization()
  const { signOut } = useClerk()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [profileData, setProfileData] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    bio: '',
    phone: '',
    location: '',
    website: '',
    jobTitle: '',
    department: ''
  })
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    smsAlerts: false,
    dealUpdates: true,
    teamUpdates: true,
    weeklyReports: true,
    monthlyReports: false
  })

  const handleProfileUpdate = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await user.update({
        firstName: profileData.firstName,
        lastName: profileData.lastName,
      })
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to update profile. Please try again.')
      console.error('Profile update error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    await signOut()
    navigate('/sign-in')
  }

  const handleImageUpload = () => {
    alert('Image upload would be handled here with Clerk\'s user.setProfileImage() method')
  }

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 mx-auto animate-spin" />
          <p className="text-gray-600 mt-4">Loading profile...</p>
        </div>
      </div>
    )
  }

  const initials = `${user?.firstName?.charAt(0) || ''}${user?.lastName?.charAt(0) || ''}`
  const memberSince = user?.createdAt ? new Date(user.createdAt).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric'
  }) : 'Unknown'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
            <div className="flex items-center space-x-4">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Sign Out</DialogTitle>
                    <DialogDescription>
                      Are you sure you want to sign out? You'll need to sign in again to access your account.
                    </DialogDescription>
                  </DialogHeader>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => {}}>Cancel</Button>
                    <Button onClick={handleSignOut}>Sign Out</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Account Settings</h1>
          <p className="text-gray-600 mt-2">Manage your profile and preferences</p>
        </div>

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertTitle className="text-green-800">Success</AlertTitle>
            <AlertDescription className="text-green-700">{success}</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center">
                  <div className="relative">
                    <Avatar className="h-24 w-24">
                      <AvatarImage src={user?.imageUrl} alt={user?.fullName} />
                      <AvatarFallback className="text-xl">{initials}</AvatarFallback>
                    </Avatar>
                    <Button
                      size="sm"
                      className="absolute bottom-0 right-0 rounded-full h-8 w-8 p-0"
                      onClick={handleImageUpload}
                    >
                      <Camera className="h-4 w-4" />
                    </Button>
                  </div>
                  <h2 className="text-xl font-semibold mt-4">{user?.fullName}</h2>
                  <p className="text-gray-600">{user?.primaryEmailAddress?.emailAddress}</p>
                  {organization && (
                    <Badge variant="secondary" className="mt-2">
                      <Building2 className="h-3 w-3 mr-1" />
                      {organization.name}
                    </Badge>
                  )}
                </div>

                <Separator className="my-6" />

                <div className="space-y-4">
                  <div className="flex items-center text-sm">
                    <Mail className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-gray-600">{user?.primaryEmailAddress?.emailAddress}</span>
                  </div>
                  {profileData.phone && (
                    <div className="flex items-center text-sm">
                      <Phone className="h-4 w-4 text-gray-400 mr-3" />
                      <span className="text-gray-600">{profileData.phone}</span>
                    </div>
                  )}
                  {profileData.location && (
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 text-gray-400 mr-3" />
                      <span className="text-gray-600">{profileData.location}</span>
                    </div>
                  )}
                  {profileData.website && (
                    <div className="flex items-center text-sm">
                      <Globe className="h-4 w-4 text-gray-400 mr-3" />
                      <span className="text-gray-600">{profileData.website}</span>
                    </div>
                  )}
                  <div className="flex items-center text-sm">
                    <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-gray-600">Member since {memberSince}</span>
                  </div>
                </div>

                <Separator className="my-6" />

                <div className="space-y-3">
                  <h3 className="font-medium text-gray-900">Account Status</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Email Verified</span>
                      {user?.primaryEmailAddress?.verification?.status === 'verified' ? (
                        <Badge variant="outline" className="text-green-600">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Verified
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-yellow-600">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Unverified
                        </Badge>
                      )}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Two-Factor Auth</span>
                      <Badge variant="outline" className="text-gray-600">
                        <Lock className="h-3 w-3 mr-1" />
                        Disabled
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <Tabs defaultValue="profile" className="space-y-4">
              <TabsList>
                <TabsTrigger value="profile">Profile</TabsTrigger>
                <TabsTrigger value="security">Security</TabsTrigger>
                <TabsTrigger value="notifications">Notifications</TabsTrigger>
                <TabsTrigger value="billing">Billing</TabsTrigger>
              </TabsList>

              <TabsContent value="profile">
                <Card>
                  <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                      Update your personal information and contact details
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="firstName">First Name</Label>
                        <Input
                          id="firstName"
                          value={profileData.firstName}
                          onChange={(e) => setProfileData({ ...profileData, firstName: e.target.value })}
                          placeholder="Enter first name"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="lastName">Last Name</Label>
                        <Input
                          id="lastName"
                          value={profileData.lastName}
                          onChange={(e) => setProfileData({ ...profileData, lastName: e.target.value })}
                          placeholder="Enter last name"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={user?.primaryEmailAddress?.emailAddress}
                        disabled
                        className="bg-gray-50"
                      />
                      <p className="text-xs text-gray-500">Contact support to change your email address</p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="bio">Bio</Label>
                      <Textarea
                        id="bio"
                        value={profileData.bio}
                        onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                        placeholder="Tell us about yourself"
                        rows={4}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="jobTitle">Job Title</Label>
                        <Input
                          id="jobTitle"
                          value={profileData.jobTitle}
                          onChange={(e) => setProfileData({ ...profileData, jobTitle: e.target.value })}
                          placeholder="e.g. Managing Director"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="department">Department</Label>
                        <Input
                          id="department"
                          value={profileData.department}
                          onChange={(e) => setProfileData({ ...profileData, department: e.target.value })}
                          placeholder="e.g. M&A Advisory"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone Number</Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={profileData.phone}
                          onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                          placeholder="+1 (555) 123-4567"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="location">Location</Label>
                        <Input
                          id="location"
                          value={profileData.location}
                          onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                          placeholder="City, Country"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        type="url"
                        value={profileData.website}
                        onChange={(e) => setProfileData({ ...profileData, website: e.target.value })}
                        placeholder="https://example.com"
                      />
                    </div>

                    <div className="flex justify-end">
                      <Button onClick={handleProfileUpdate} disabled={loading}>
                        {loading ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="h-4 w-4 mr-2" />
                            Save Changes
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="security">
                <Card>
                  <CardHeader>
                    <CardTitle>Security Settings</CardTitle>
                    <CardDescription>
                      Manage your password and security preferences
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Key className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="font-medium">Password</p>
                            <p className="text-sm text-gray-600">Last changed 30 days ago</p>
                          </div>
                        </div>
                        <Button variant="outline">Change Password</Button>
                      </div>

                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Shield className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="font-medium">Two-Factor Authentication</p>
                            <p className="text-sm text-gray-600">Add an extra layer of security</p>
                          </div>
                        </div>
                        <Button variant="outline">Enable 2FA</Button>
                      </div>

                      <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Smartphone className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="font-medium">Trusted Devices</p>
                            <p className="text-sm text-gray-600">Manage your trusted devices</p>
                          </div>
                        </div>
                        <Button variant="outline">Manage</Button>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="font-medium mb-4">Active Sessions</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium text-sm">Current Session</p>
                            <p className="text-xs text-gray-600">Chrome on Windows • Your location</p>
                          </div>
                          <Badge variant="outline" className="text-green-600">Active</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="notifications">
                <Card>
                  <CardHeader>
                    <CardTitle>Notification Preferences</CardTitle>
                    <CardDescription>
                      Choose how you want to be notified about updates
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="email-alerts" className="font-normal">
                            Email Notifications
                          </Label>
                          <p className="text-sm text-gray-600">Receive notifications via email</p>
                        </div>
                        <Switch
                          id="email-alerts"
                          checked={notifications.emailAlerts}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, emailAlerts: checked })
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="sms-alerts" className="font-normal">
                            SMS Notifications
                          </Label>
                          <p className="text-sm text-gray-600">Receive notifications via SMS</p>
                        </div>
                        <Switch
                          id="sms-alerts"
                          checked={notifications.smsAlerts}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, smsAlerts: checked })
                          }
                        />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="deal-updates" className="font-normal">
                            Deal Updates
                          </Label>
                          <p className="text-sm text-gray-600">Get notified about deal progress</p>
                        </div>
                        <Switch
                          id="deal-updates"
                          checked={notifications.dealUpdates}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, dealUpdates: checked })
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="team-updates" className="font-normal">
                            Team Updates
                          </Label>
                          <p className="text-sm text-gray-600">Stay informed about team activities</p>
                        </div>
                        <Switch
                          id="team-updates"
                          checked={notifications.teamUpdates}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, teamUpdates: checked })
                          }
                        />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="weekly-reports" className="font-normal">
                            Weekly Reports
                          </Label>
                          <p className="text-sm text-gray-600">Receive weekly summary reports</p>
                        </div>
                        <Switch
                          id="weekly-reports"
                          checked={notifications.weeklyReports}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, weeklyReports: checked })
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label htmlFor="monthly-reports" className="font-normal">
                            Monthly Reports
                          </Label>
                          <p className="text-sm text-gray-600">Receive monthly summary reports</p>
                        </div>
                        <Switch
                          id="monthly-reports"
                          checked={notifications.monthlyReports}
                          onCheckedChange={(checked) =>
                            setNotifications({ ...notifications, monthlyReports: checked })
                          }
                        />
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <Button>
                        <Save className="h-4 w-4 mr-2" />
                        Save Preferences
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="billing">
                <Card>
                  <CardHeader>
                    <CardTitle>Billing & Subscription</CardTitle>
                    <CardDescription>
                      Manage your subscription and payment methods
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">Current Plan</h3>
                        <Badge>Professional</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        $99/month • Billed monthly • Renews on January 1, 2025
                      </p>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">Change Plan</Button>
                        <Button size="sm" variant="outline">Cancel Subscription</Button>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium mb-4">Payment Methods</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <CreditCard className="h-5 w-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-sm">•••• •••• •••• 4242</p>
                              <p className="text-xs text-gray-600">Expires 12/25</p>
                            </div>
                          </div>
                          <Badge variant="outline">Default</Badge>
                        </div>
                      </div>
                      <Button className="mt-3" variant="outline">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Payment Method
                      </Button>
                    </div>

                    <div>
                      <h3 className="font-medium mb-4">Billing History</h3>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium text-sm">December 2024</p>
                            <p className="text-xs text-gray-600">Professional Plan</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-sm">$99.00</p>
                            <Button variant="link" className="h-auto p-0 text-xs">
                              Download
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium text-sm">November 2024</p>
                            <p className="text-xs text-gray-600">Professional Plan</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-sm">$99.00</p>
                            <Button variant="link" className="h-auto p-0 text-xs">
                              Download
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  )
}

export default UserProfile