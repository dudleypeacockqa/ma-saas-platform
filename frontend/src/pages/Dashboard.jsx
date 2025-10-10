import { useUser } from "@clerk/clerk-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, Briefcase, DollarSign, Users, FileText } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

const Dashboard = () => {
  const { user } = useUser()

  const data = [
    { name: "Jan", deals: 4, value: 2400 },
    { name: "Feb", deals: 3, value: 1398 },
    { name: "Mar", deals: 2, value: 9800 },
    { name: "Apr", deals: 2.7, value: 3908 },
    { name: "May", deals: 1.8, value: 4800 },
    { name: "Jun", deals: 2.3, value: 3800 },
    { name: "Jul", deals: 3.4, value: 4300 },
  ]

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.firstName}!</h1>
      <p className="text-muted-foreground mb-8">Here is a snapshot of your M&A activities.</p>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Deals</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">+2 from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pipeline Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$250.6M</div>
            <p className="text-xs text-muted-foreground">+15.2% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">+1 new member this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">342</div>
            <p className="text-xs text-muted-foreground">+25 uploaded this month</p>
          </CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Deal Activity</CardTitle>
          <CardDescription>A summary of your deal pipeline over the last 6 months.</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="deals" stroke="#8884d8" activeDot={{ r: 8 }} />
              <Line type="monotone" dataKey="value" stroke="#82ca9d" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              <li className="flex items-center gap-4">
                <div className="bg-blue-100 dark:bg-blue-900 p-2 rounded-full">
                  <Briefcase className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium">New deal "Project Phoenix" added</p>
                  <p className="text-sm text-muted-foreground">2 hours ago</p>
                </div>
              </li>
              <li className="flex items-center gap-4">
                <div className="bg-green-100 dark:bg-green-900 p-2 rounded-full">
                  <FileText className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium">NDA signed for "Project Titan"</p>
                  <p className="text-sm text-muted-foreground">1 day ago</p>
                </div>
              </li>
              <li className="flex items-center gap-4">
                <div className="bg-purple-100 dark:bg-purple-900 p-2 rounded-full">
                  <Users className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium">Jane Doe invited to "Project Phoenix"</p>
                  <p className="text-sm text-muted-foreground">3 days ago</p>
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Button>Create New Deal</Button>
            <Button variant="outline">Upload Document</Button>
            <Button variant="outline">Invite Team Member</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
