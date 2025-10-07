import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import {
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Building2,
  MapPin,
  Star,
  Eye,
  Phone,
  MessageSquare,
  CheckCircle,
  X,
  RefreshCw,
  Download
} from 'lucide-react';

interface Opportunity {
  id: string;
  organization_id: string;
  company_name: string;
  region: 'UK' | 'US' | 'EU' | 'APAC';
  industry_vertical: string;
  status: 'new' | 'screening' | 'qualified' | 'contacted' | 'in_discussion' | 'rejected' | 'converted_to_deal';
  overall_score?: number;
  financial_health_score?: number;
  strategic_fit_score?: number;
  annual_revenue?: number;
  ebitda?: number;
  employee_count?: number;
  source_url?: string;
  created_at: string;
  updated_at?: string;
}

interface PipelineMetrics {
  total_opportunities: number;
  status_breakdown: Record<string, number>;
  average_score: number;
  qualified_count: number;
  conversion_rate: number;
  new_this_week: number;
}

const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800',
  screening: 'bg-yellow-100 text-yellow-800',
  qualified: 'bg-green-100 text-green-800',
  contacted: 'bg-purple-100 text-purple-800',
  in_discussion: 'bg-indigo-100 text-indigo-800',
  rejected: 'bg-red-100 text-red-800',
  converted_to_deal: 'bg-emerald-100 text-emerald-800'
};

const statusIcons: Record<string, React.ReactNode> = {
  new: <Star className="w-4 h-4" />,
  screening: <Eye className="w-4 h-4" />,
  qualified: <CheckCircle className="w-4 h-4" />,
  contacted: <Phone className="w-4 h-4" />,
  in_discussion: <MessageSquare className="w-4 h-4" />,
  rejected: <X className="w-4 h-4" />,
  converted_to_deal: <TrendingUp className="w-4 h-4" />
};

export const OpportunityDashboard: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [metrics, setMetrics] = useState<PipelineMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [regionFilter, setRegionFilter] = useState<string>('all');
  const [industryFilter, setIndustryFilter] = useState<string>('all');
  const [minScore, setMinScore] = useState<number>(0);

  useEffect(() => {
    fetchOpportunities();
    fetchMetrics();
  }, [statusFilter, regionFilter, industryFilter, minScore, searchQuery]);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();

      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (regionFilter !== 'all') params.append('region', regionFilter);
      if (industryFilter !== 'all') params.append('industry_vertical', industryFilter);
      if (minScore > 0) params.append('min_score', minScore.toString());
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(`/api/opportunities?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setOpportunities(data);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/opportunities/metrics/pipeline', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const scanCompaniesHouse = async () => {
    try {
      const response = await fetch('/api/opportunities/scan/companies-house', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          region: 'UK',
          industry_sic: '62',
          min_age_years: 3
        })
      });

      if (response.ok) {
        const newOpportunities = await response.json();
        alert(`Discovered ${newOpportunities.length} new UK opportunities!`);
        fetchOpportunities();
        fetchMetrics();
      }
    } catch (error) {
      console.error('Error scanning Companies House:', error);
      alert('Error scanning Companies House');
    }
  };

  const scoreOpportunity = async (opportunityId: string) => {
    try {
      const opportunity = opportunities.find(o => o.id === opportunityId);
      if (!opportunity) return;

      const response = await fetch(`/api/opportunities/${opportunityId}/score`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          company_data: {
            revenue: opportunity.annual_revenue || 0,
            ebitda: opportunity.ebitda || 0,
            industry: opportunity.industry_vertical,
            region: opportunity.region,
            employee_count: opportunity.employee_count
          }
        })
      });

      if (response.ok) {
        alert('Opportunity scored successfully!');
        fetchOpportunities();
      }
    } catch (error) {
      console.error('Error scoring opportunity:', error);
      alert('Error scoring opportunity');
    }
  };

  const updateStatus = async (opportunityId: string, newStatus: string) => {
    try {
      const response = await fetch(`/api/opportunities/${opportunityId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        fetchOpportunities();
        fetchMetrics();
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount);
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">M&A Opportunities</h1>
          <p className="text-gray-500">Discover and qualify acquisition targets</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={scanCompaniesHouse} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Scan Companies House
          </Button>
          <Button onClick={fetchOpportunities}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Opportunities</CardTitle>
              <Building2 className="w-4 h-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_opportunities}</div>
              <p className="text-xs text-green-600 flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                {metrics.new_this_week} new this week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Qualified</CardTitle>
              <CheckCircle className="w-4 h-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.qualified_count}</div>
              <p className="text-xs text-gray-500 mt-1">
                {metrics.conversion_rate.toFixed(1)}% conversion rate
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <Star className="w-4 h-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.average_score.toFixed(1)}/100</div>
              <p className="text-xs text-gray-500 mt-1">Opportunity quality</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Status Breakdown</CardTitle>
              <Eye className="w-4 h-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {Object.entries(metrics.status_breakdown).slice(0, 3).map(([status, count]) => (
                  <div key={status} className="flex justify-between text-xs">
                    <span className="capitalize">{status.replace('_', ' ')}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="screening">Screening</SelectItem>
                <SelectItem value="qualified">Qualified</SelectItem>
                <SelectItem value="contacted">Contacted</SelectItem>
                <SelectItem value="in_discussion">In Discussion</SelectItem>
              </SelectContent>
            </Select>

            <Select value={regionFilter} onValueChange={setRegionFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Regions</SelectItem>
                <SelectItem value="UK">UK</SelectItem>
                <SelectItem value="US">US</SelectItem>
                <SelectItem value="EU">EU</SelectItem>
                <SelectItem value="APAC">APAC</SelectItem>
              </SelectContent>
            </Select>

            <Select value={industryFilter} onValueChange={setIndustryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                <SelectItem value="technology">Technology</SelectItem>
                <SelectItem value="healthcare">Healthcare</SelectItem>
                <SelectItem value="manufacturing">Manufacturing</SelectItem>
                <SelectItem value="retail">Retail</SelectItem>
                <SelectItem value="professional_services">Professional Services</SelectItem>
              </SelectContent>
            </Select>

            <div>
              <Input
                type="number"
                placeholder="Min Score"
                value={minScore || ''}
                onChange={(e) => setMinScore(parseInt(e.target.value) || 0)}
                min="0"
                max="100"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Opportunities Grid */}
      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-500">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="w-12 h-12 mx-auto text-gray-300" />
            <h3 className="mt-4 text-lg font-medium">No opportunities found</h3>
            <p className="mt-2 text-gray-500">Try scanning for new opportunities or adjusting your filters</p>
            <Button onClick={scanCompaniesHouse} className="mt-4">
              <RefreshCw className="w-4 h-4 mr-2" />
              Scan Now
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {opportunities.map((opp) => (
            <Card
              key={opp.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedOpportunity(opp)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{opp.company_name}</CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <MapPin className="w-3 h-3" />
                      {opp.region}
                      <span className="mx-1">•</span>
                      {opp.industry_vertical}
                    </CardDescription>
                  </div>
                  <Badge className={statusColors[opp.status]}>
                    <span className="flex items-center gap-1">
                      {statusIcons[opp.status]}
                      {opp.status.replace('_', ' ')}
                    </span>
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Score */}
                  {opp.overall_score !== undefined && (
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-500">Overall Score</span>
                        <span className={`text-lg font-bold ${getScoreColor(opp.overall_score)}`}>
                          {opp.overall_score.toFixed(0)}/100
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            opp.overall_score >= 75 ? 'bg-green-500' :
                            opp.overall_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${opp.overall_score}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Financials */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-gray-500">Revenue</p>
                      <p className="font-semibold flex items-center">
                        <DollarSign className="w-3 h-3 mr-1" />
                        {formatCurrency(opp.annual_revenue)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">EBITDA</p>
                      <p className="font-semibold flex items-center">
                        <DollarSign className="w-3 h-3 mr-1" />
                        {formatCurrency(opp.ebitda)}
                      </p>
                    </div>
                  </div>

                  {/* Employees */}
                  {opp.employee_count && (
                    <div className="text-sm">
                      <p className="text-gray-500">Employees</p>
                      <p className="font-semibold">{opp.employee_count.toLocaleString()}</p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    {!opp.overall_score && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          scoreOpportunity(opp.id);
                        }}
                      >
                        <Star className="w-3 h-3 mr-1" />
                        Score
                      </Button>
                    )}
                    <Select
                      value={opp.status}
                      onValueChange={(value) => {
                        updateStatus(opp.id, value);
                      }}
                    >
                      <SelectTrigger className="h-8" onClick={(e) => e.stopPropagation()}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="new">New</SelectItem>
                        <SelectItem value="screening">Screening</SelectItem>
                        <SelectItem value="qualified">Qualified</SelectItem>
                        <SelectItem value="contacted">Contacted</SelectItem>
                        <SelectItem value="in_discussion">In Discussion</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default OpportunityDashboard;
