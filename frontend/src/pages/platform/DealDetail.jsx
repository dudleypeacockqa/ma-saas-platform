import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { trackEvent } from '@/lib/analytics';
import {
  ArrowLeft,
  Edit,
  Share2,
  MoreHorizontal,
  Calendar,
  DollarSign,
  Users,
  FileText,
  Activity,
} from 'lucide-react';

const DealDetail = () => {
  const { dealId } = useParams();
  const { getToken } = useAuth();
  const { user } = useUser();
  const [insights, setInsights] = useState(null);
  const [insightsError, setInsightsError] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  // TODO: Replace mock with API data
  const deal = {
    id: dealId,
    name: 'TechCo Acquisition',
    targetCompany: 'TechCo Ltd',
    value: '£45.2M',
    stage: 'Due Diligence',
    priority: 'critical',
    progress: 75,
    lead: 'Sarah Chen',
    team: ['John Smith', 'Michael Brown', 'Lisa Johnson'],
    created: '2025-09-15',
    expectedClose: '2025-12-30',
    description:
      'Strategic acquisition of leading technology company to expand our digital capabilities in the financial services sector.',
  };

  useEffect(() => {
    const fetchInsights = async () => {
      if (!dealId) return;
      setLoadingInsights(true);
      setInsightsError(null);

      try {
        const token = await getToken();
        const response = await fetch(`/api/deals/${dealId}/insights`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        if (!response.ok) {
          if (response.status !== 404) {
            throw new Error(`Failed to load insights (${response.status})`);
          }
          setInsights(null);
          return;
        }

        const data = await response.json();
        setInsights(data);
        trackEvent('deal_insight_viewed', {
          deal_id: dealId,
          win_probability: data.win_probability,
          confidence: data.confidence,
        });
      } catch (error) {
        console.error('Unable to load deal insights', error);
        setInsightsError(error instanceof Error ? error.message : 'Unknown error');
      } finally {
        setLoadingInsights(false);
      }
    };

    fetchInsights();
  }, [dealId, getToken]);

  const probabilityLabel = useMemo(() => {
    if (!insights) return 'Pending';
    if (insights.win_probability >= 70) return 'Strong outlook';
    if (insights.win_probability >= 40) return 'Moderate outlook';
    return 'At risk';
  }, [insights]);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Pipeline
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{deal.name}</h1>
            <p className="text-gray-600">{deal.targetCompany}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Badge variant="outline" className="text-red-600 border-red-200">
            {deal.priority}
          </Badge>
          <Badge variant="secondary">{deal.stage}</Badge>
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Deal Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium">Deal Value</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.value}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium">Expected Close</span>
            </div>
            <div className="text-lg font-semibold mt-1">{deal.expectedClose}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-600" />
              <span className="text-sm font-medium">Team Size</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.team.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-orange-600" />
              <span className="text-sm font-medium">Progress</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.progress}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Deal Information */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Deal Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">{deal.description}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">Activity timeline coming soon</div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>AI Deal Insights</span>
                {insights?.confidence && (
                  <Badge variant="outline">Confidence: {insights.confidence}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingInsights && <p className="text-sm text-muted-foreground">Analyzing latest data...</p>}
              {insightsError && (
                <p className="text-sm text-destructive">{insightsError}</p>
              )}
              {!loadingInsights && !insights && !insightsError && (
                <p className="text-sm text-muted-foreground">Insights will appear once deal data is synced.</p>
              )}
              {insights && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                      <Activity className="h-4 w-4" />
                      {probabilityLabel}
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-2xl font-semibold">{insights.win_probability}%</span>
                      <Badge variant="secondary">Win probability</Badge>
                    </div>
                    <Progress value={insights.win_probability} className="mt-2" />
                  </div>

                  {insights.risk_factors?.length ? (
                    <div>
                      <p className="text-sm font-semibold mb-1">Key Risks</p>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        {insights.risk_factors.map((risk, index) => (
                          <li key={index}>• {risk}</li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No major risks flagged.</p>
                  )}

                  {insights.recommended_actions?.length && (
                    <div>
                      <p className="text-sm font-semibold mb-1">Recommended Actions</p>
                      <ul className="space-y-1 text-sm">
                        {insights.recommended_actions.map((action, index) => (
                          <li key={index}>• {action}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {insights.next_milestone && (
                    <div className="rounded-lg border p-3 text-sm">
                      <p className="font-semibold">Next Milestone</p>
                      <p className="text-muted-foreground">
                        {insights.next_milestone.date ? new Date(insights.next_milestone.date).toLocaleDateString() : 'Date TBD'}
                      </p>
                      {insights.next_milestone.description && (
                        <p className="mt-1 text-muted-foreground">{insights.next_milestone.description}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Deal Team</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600">SC</span>
                  </div>
                  <div>
                    <p className="font-medium">{deal.lead}</p>
                    <p className="text-sm text-gray-600">Deal Lead</p>
                  </div>
                </div>
                {deal.team.map((member, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {member
                          .split(' ')
                          .map((n) => n[0])
                          .join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{member}</p>
                      <p className="text-sm text-gray-600">Team Member</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">No documents uploaded yet</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DealDetail;
