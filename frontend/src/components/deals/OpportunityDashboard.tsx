/**
 * Opportunity Dashboard Component
 * Main dashboard for M&A opportunity discovery and management
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  TrendingUp,
  Target,
  Filter,
  Search,
  RefreshCw,
  BarChart3,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface Opportunity {
  id: string;
  company_name: string;
  opportunity_name: string;
  opportunity_score: number;
  stage: string;
  source: string;
  financial_health: string;
  estimated_valuation: number | null;
  discovered_at: string;
  company_location: string;
  industry: string;
}

interface PipelineAnalytics {
  total_opportunities: number;
  average_score: number;
  stage_breakdown: Record<string, number>;
  source_breakdown: Record<string, number>;
  financial_health_breakdown: Record<string, number>;
  high_score_count: number;
  qualified_count: number;
}

const OpportunityDashboard: React.FC = () => {
  const { getToken } = useAuth();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [analytics, setAnalytics] = useState<PipelineAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStage, setFilterStage] = useState<string>('all');
  const [minScore, setMinScore] = useState<number>(0);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      // Load opportunities
      const oppsResponse = await fetch(
        `${API_URL}/api/deal-discovery/opportunities?limit=100`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!oppsResponse.ok) throw new Error('Failed to load opportunities');

      const oppsData = await oppsResponse.json();
      setOpportunities(oppsData);

      // Load analytics
      const analyticsResponse = await fetch(
        `${API_URL}/api/deal-discovery/analytics/pipeline`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!analyticsResponse.ok) throw new Error('Failed to load analytics');

      const analyticsData = await analyticsResponse.json();
      setAnalytics(analyticsData);

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const refreshScores = async () => {
    try {
      const token = await getToken();

      await fetch(
        `${API_URL}/api/deal-discovery/refresh-scores`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      alert('Score refresh started. This may take a few minutes.');
    } catch (err) {
      alert('Failed to start score refresh');
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 65) return 'text-blue-600 bg-blue-100';
    if (score >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getHealthBadgeColor = (health: string): string => {
    const colors: Record<string, string> = {
      'excellent': 'bg-green-100 text-green-800',
      'good': 'bg-blue-100 text-blue-800',
      'fair': 'bg-yellow-100 text-yellow-800',
      'poor': 'bg-orange-100 text-orange-800',
      'distressed': 'bg-red-100 text-red-800',
      'unknown': 'bg-gray-100 text-gray-800'
    };
    return colors[health] || colors.unknown;
  };

  const filteredOpportunities = opportunities.filter(opp => {
    if (filterStage !== 'all' && opp.stage !== filterStage) return false;
    if (opp.opportunity_score < minScore) return false;
    if (searchQuery && !opp.company_name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-red-800">{error}</p>
        </div>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Deal Discovery</h1>
          <p className="text-gray-600 mt-1">Discover and track M&A opportunities</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={refreshScores}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh Scores
          </button>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Opportunities</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics.total_opportunities}
                </p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics.average_score.toFixed(1)}
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Score (75+)</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics.high_score_count}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Qualified</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics.qualified_count}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="w-full md:w-48">
            <select
              value={filterStage}
              onChange={(e) => setFilterStage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Stages</option>
              <option value="discovery">Discovery</option>
              <option value="initial_review">Initial Review</option>
              <option value="due_diligence">Due Diligence</option>
              <option value="negotiation">Negotiation</option>
            </select>
          </div>

          <div className="w-full md:w-48">
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="0">Min Score: Any</option>
              <option value="50">Min Score: 50</option>
              <option value="65">Min Score: 65</option>
              <option value="75">Min Score: 75</option>
              <option value="85">Min Score: 85</option>
            </select>
          </div>
        </div>
      </div>

      {/* Opportunities List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Financial Health
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valuation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredOpportunities.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    No opportunities found. Try adjusting your filters.
                  </td>
                </tr>
              ) : (
                filteredOpportunities.map((opp) => (
                  <tr key={opp.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {opp.company_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {opp.company_location} • {opp.industry}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(opp.opportunity_score)}`}>
                        {opp.opportunity_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getHealthBadgeColor(opp.financial_health)}`}>
                        {opp.financial_health}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {opp.stage.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {opp.estimated_valuation
                        ? `$${(opp.estimated_valuation / 1_000_000).toFixed(1)}M`
                        : 'N/A'
                      }
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {opp.source.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <a
                        href={`/deals/opportunities/${opp.id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600 text-center">
        Showing {filteredOpportunities.length} of {opportunities.length} opportunities
      </div>
    </div>
  );
};

export default OpportunityDashboard;
