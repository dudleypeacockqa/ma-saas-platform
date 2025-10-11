import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Activity, TrendingUp, Clock, AlertCircle, Users, Zap } from 'lucide-react';

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/metrics');
        if (!response.ok) throw new Error('Failed to fetch metrics');
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const getStatusColor = (code) => {
    if (code.startsWith('2')) return 'bg-green-500';
    if (code.startsWith('3')) return 'bg-yellow-500';
    if (code.startsWith('4')) return 'bg-orange-500';
    if (code.startsWith('5')) return 'bg-red-500';
    return 'bg-gray-500';
  };

  const formatMemory = (bytes) => {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  const getHealthStatus = () => {
    const errorRate = (metrics.errors.count / metrics.requests.total) * 100;
    if (errorRate === 0) return { status: 'Excellent', color: 'text-green-600', badge: 'default' };
    if (errorRate < 1) return { status: 'Good', color: 'text-blue-600', badge: 'secondary' };
    if (errorRate < 5) return { status: 'Warning', color: 'text-yellow-600', badge: 'outline' };
    return { status: 'Critical', color: 'text-red-600', badge: 'destructive' };
  };

  const health = getHealthStatus();

  return (
    <div className="p-8 space-y-8 bg-background min-h-screen">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Metrics Dashboard</h1>
          <p className="text-muted-foreground">Real-time application performance monitoring</p>
        </div>
        <Badge variant={health.badge} className="text-sm px-3 py-1">
          <Activity className="h-3 w-3 mr-1 inline" />
          {health.status}
        </Badge>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.requests.total.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Since {metrics.uptime.human} ago</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.performance.avgResponseTime}ms</div>
            <p className="text-xs text-muted-foreground">
              Min: {metrics.performance.minResponseTime}ms, Max:{' '}
              {metrics.performance.maxResponseTime}ms
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((metrics.errors.count / metrics.requests.total) * 100).toFixed(2)}%
            </div>
            <p className="text-xs text-muted-foreground">{metrics.errors.count} errors total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uptime</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.uptime.human}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.uptime.seconds.toLocaleString()} seconds
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Status Codes */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Response Status Codes</CardTitle>
            <CardDescription>Distribution of HTTP status codes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(metrics.requests.byStatus).map(([code, count]) => (
                <div key={code} className="flex items-center">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">{code}</span>
                      <span className="text-sm text-muted-foreground">
                        {count} ({((count / metrics.requests.total) * 100).toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getStatusColor(code)}`}
                        style={{ width: `${(count / metrics.requests.total) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Paths</CardTitle>
            <CardDescription>Most accessed endpoints</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(metrics.requests.topPaths)
                .slice(0, 5)
                .map(([path, count]) => (
                  <div key={path} className="flex items-center">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium font-mono">{path}</span>
                        <span className="text-sm text-muted-foreground">{count}</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-primary"
                          style={{
                            width: `${(count / metrics.requests.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Resources */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Memory Usage</CardTitle>
            <CardDescription>Node.js process memory</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Heap Used</span>
                <span className="text-sm font-medium">{formatMemory(metrics.memory.heapUsed)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Heap Total</span>
                <span className="text-sm font-medium">
                  {formatMemory(metrics.memory.heapTotal)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">RSS</span>
                <span className="text-sm font-medium">{formatMemory(metrics.memory.rss)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">External</span>
                <span className="text-sm font-medium">{formatMemory(metrics.memory.external)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>CPU Usage</CardTitle>
            <CardDescription>Process CPU time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">User CPU</span>
                <span className="text-sm font-medium">
                  {(metrics.cpu.user / 1000000).toFixed(2)}s
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">System CPU</span>
                <span className="text-sm font-medium">
                  {(metrics.cpu.system / 1000000).toFixed(2)}s
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Total CPU</span>
                <span className="text-sm font-medium">
                  {((metrics.cpu.user + metrics.cpu.system) / 1000000).toFixed(2)}s
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Errors */}
      {metrics.errors.recent.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Errors</CardTitle>
            <CardDescription>Last {metrics.errors.recent.length} errors</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {metrics.errors.recent.map((error, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 rounded-lg bg-destructive/10 border border-destructive/20"
                >
                  <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">
                        {error.method} {error.path}
                      </span>
                      <Badge variant="destructive">{error.status}</Badge>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      <span>{new Date(error.timestamp).toLocaleString()}</span>
                      <span>•</span>
                      <span className="font-mono">{error.ip}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="text-center text-sm text-muted-foreground">
        Auto-refreshing every 5 seconds • Last updated:{' '}
        {new Date(metrics.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}
