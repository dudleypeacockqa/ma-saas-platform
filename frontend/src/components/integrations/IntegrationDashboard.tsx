import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Link as LinkIcon,
  Loader2,
  RefreshCw,
  Settings,
  TrendingUp,
  XCircle,
  Zap,
  Globe,
  MessageSquare,
  Video,
  Users,
  DollarSign
} from 'lucide-react';

interface Platform {
  name: string;
  type: string;
  status: string;
  health: string;
  last_sync: string | null;
  connection_status: string;
}

interface HealthSummary {
  overall_status: string;
  healthy: number;
  degraded: number;
  down: number;
}

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  platform_name: string;
  message: string;
  created_at: string;
}

interface IntegrationsOverview {
  connected_platforms_count: number;
  connected_platforms: string[];
  health_summary: HealthSummary;
  alerts_summary: {
    active_alerts: number;
  };
}

const PLATFORM_ICONS: Record<string, React.ReactNode> = {
  linkedin: <Users className="h-5 w-5" />,
  twitter: <MessageSquare className="h-5 w-5" />,
  youtube: <Video className="h-5 w-5" />,
  stripe: <DollarSign className="h-5 w-5" />,
  buzzsprout: <Activity className="h-5 w-5" />,
  hubspot: <Users className="h-5 w-5" />,
  default: <Globe className="h-5 w-5" />
};

const STATUS_COLORS: Record<string, string> = {
  healthy: 'text-green-600 bg-green-50',
  degraded: 'text-yellow-600 bg-yellow-50',
  down: 'text-red-600 bg-red-50',
  unknown: 'text-gray-600 bg-gray-50'
};

export const IntegrationDashboard: React.FC = () => {
  const [overview, setOverview] = useState<IntegrationsOverview | null>(null);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const headers = {
        'Authorization': `Bearer ${localStorage.getItem('clerk_token')}`,
        'Content-Type': 'application/json'
      };

      // Fetch overview
      const overviewRes = await fetch(`${API_BASE_URL}/api/integrations/overview`, { headers });
      if (overviewRes.ok) {
        const data = await overviewRes.json();
        setOverview(data);
      }

      // Fetch detailed health status
      const healthRes = await fetch(`${API_BASE_URL}/api/integrations/health`, { headers });
      if (healthRes.ok) {
        const healthData = await healthRes.json();

        // Combine healthy, degraded, and down platforms
        const allPlatforms = [
          ...(healthData.healthy || []),
          ...(healthData.degraded || []),
          ...(healthData.down || [])
        ];

        setPlatforms(allPlatforms);
      }

      // Fetch active alerts
      const alertsRes = await fetch(`${API_BASE_URL}/api/integrations/alerts`, { headers });
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load integration data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'down':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
          <p className="text-muted-foreground">
            Manage your platform connections and workflows
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
          <Button size="sm">
            <LinkIcon className="h-4 w-4 mr-2" />
            Connect Platform
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Integrations</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview.connected_platforms_count}</div>
              <p className="text-xs text-muted-foreground">Connected platforms</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {overview.health_summary.healthy}
              </div>
              <p className="text-xs text-muted-foreground">Operating normally</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Issues</CardTitle>
              <AlertCircle className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {overview.health_summary.degraded + overview.health_summary.down}
              </div>
              <p className="text-xs text-muted-foreground">Require attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview.alerts_summary.active_alerts}</div>
              <p className="text-xs text-muted-foreground">Unresolved issues</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="platforms" className="space-y-4">
        <TabsList>
          <TabsTrigger value="platforms">Connected Platforms</TabsTrigger>
          <TabsTrigger value="alerts">
            Alerts
            {alerts.length > 0 && (
              <Badge className="ml-2" variant="destructive">{alerts.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
        </TabsList>

        {/* Platforms Tab */}
        <TabsContent value="platforms" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((platform) => (
              <Card key={platform.name}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-primary/10">
                        {PLATFORM_ICONS[platform.name] || PLATFORM_ICONS.default}
                      </div>
                      <div>
                        <CardTitle className="text-base capitalize">{platform.name}</CardTitle>
                        <CardDescription className="text-xs capitalize">
                          {platform.type}
                        </CardDescription>
                      </div>
                    </div>
                    {getStatusIcon(platform.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge className={STATUS_COLORS[platform.status] || STATUS_COLORS.unknown}>
                      {platform.status}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Connection:</span>
                    <span className="capitalize">{platform.connection_status}</span>
                  </div>

                  {platform.last_sync && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Last Sync:</span>
                      <span className="text-xs">
                        {new Date(platform.last_sync).toLocaleDateString()}
                      </span>
                    </div>
                  )}

                  <div className="flex gap-2 pt-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Settings className="h-4 w-4 mr-1" />
                      Configure
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Sync
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {platforms.length === 0 && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Globe className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium mb-2">No platforms connected</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Connect your first platform to get started
                </p>
                <Button>
                  <LinkIcon className="h-4 w-4 mr-2" />
                  Connect Platform
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          {alerts.length > 0 ? (
            <div className="space-y-2">
              {alerts.map((alert) => (
                <Card key={alert.id}>
                  <CardContent className="flex items-start justify-between p-4">
                    <div className="flex items-start gap-3 flex-1">
                      <AlertCircle className={`h-5 w-5 mt-0.5 ${
                        alert.severity === 'critical' ? 'text-red-600' :
                        alert.severity === 'error' ? 'text-orange-600' :
                        alert.severity === 'warning' ? 'text-yellow-600' :
                        'text-blue-600'
                      }`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="capitalize">
                            {alert.severity}
                          </Badge>
                          <Badge variant="secondary" className="capitalize">
                            {alert.platform_name}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(alert.created_at).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm">{alert.message}</p>
                      </div>
                    </div>
                    <Button size="sm" variant="ghost">
                      Resolve
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <CheckCircle2 className="h-12 w-12 text-green-600 mb-4" />
                <p className="text-lg font-medium mb-2">All clear!</p>
                <p className="text-sm text-muted-foreground">
                  No active alerts at this time
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows">
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Zap className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">Workflows</p>
              <p className="text-sm text-muted-foreground mb-4">
                Automate cross-platform actions
              </p>
              <Button>Create Workflow</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics">
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <TrendingUp className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">Performance Metrics</p>
              <p className="text-sm text-muted-foreground">
                View integration performance and uptime
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
