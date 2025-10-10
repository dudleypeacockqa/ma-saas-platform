/**
 * Opportunity Detail Component
 * Detailed view of a single M&A opportunity with financial analysis
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  TrendingUp,
  DollarSign,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  ExternalLink,
  Building2,
  MapPin,
  Globe
} from 'lucide-react';

interface OpportunityData {
  opportunity: {
    id: string;
    opportunity_name: string;
    opportunity_score: number;
    stage: string;
    source: string;
    financial_health: string;
    estimated_valuation: number | null;
    notes: string | null;
    discovered_at: string;
  };
  company: {
    id: string;
    name: string;
    legal_name: string | null;
    description: string | null;
    website: string | null;
    industry: string;
    location: {
      city: string | null;
      region: string | null;
      country: string | null;
    };
    data_source: string;
    external_id: string;
  };
  financials: Array<{
    year: number;
    revenue: number | null;
    ebitda: number | null;
    net_income: number | null;
    total_assets: number | null;
    profit_margin: number | null;
  }>;
  market_intelligence: Array<{
    id: string;
    type: string;
    source: string;
    relevance_score: number | null;
    content_summary: string;
    created_at: string;
  }>;
}

interface ScoringData {
  opportunity_id: string;
  total_score: number;
  recommendation: string;
  component_scores: {
    [key: string]: {
      score: number;
      weight: number;
      weighted_contribution: number;
    };
  };
  scored_at: string;
}

const OpportunityDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const [opportunity, setOpportunity] = useState<OpportunityData | null>(null);
  const [scoring, setScoring] = useState<ScoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'intelligence' | 'scoring'>('overview');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadOpportunity();
    loadScoring();
  }, [id]);

  const loadOpportunity = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const response = await fetch(
        `${API_URL}/api/deal-discovery/opportunities/${id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) throw new Error('Failed to load opportunity');

      const data = await response.json();
      setOpportunity(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load opportunity');
    } finally {
      setLoading(false);
    }
  };

  const loadScoring = async () => {
    try {
      const token = await getToken();

      const response = await fetch(
        `${API_URL}/api/deal-discovery/opportunities/${id}/score`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        console.warn('Failed to load scoring');
        return;
      }

      const data = await response.json();
      setScoring(data);
    } catch (err) {
      console.error('Error loading scoring:', err);
    }
  };

  const recalculateScore = async () => {
    await loadScoring();
    alert('Score recalculated successfully');
  };

  const formatCurrency = (value: number | null): string => {
    if (!value) return 'N/A';
    return `$${(value / 1_000_000).toFixed(2)}M`;
  };

  const formatPercentage = (value: number | null): string => {
    if (!value) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const getRecommendationBadge = (recommendation: string) => {
    const badges = {
      'strong_buy': { color: 'bg-green-100 text-green-800', text: 'Strong Buy' },
      'buy': { color: 'bg-blue-100 text-blue-800', text: 'Buy' },
      'consider': { color: 'bg-yellow-100 text-yellow-800', text: 'Consider' },
      'pass': { color: 'bg-orange-100 text-orange-800', text: 'Pass' },
      'avoid': { color: 'bg-red-100 text-red-800', text: 'Avoid' }
    };
    return badges[recommendation as keyof typeof badges] || badges.consider;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !opportunity) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-red-800">{error || 'Opportunity not found'}</p>
        </div>
        <button
          onClick={() => navigate('/deals/opportunities')}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Back to Opportunities
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/deals/opportunities')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{opportunity.company.name}</h1>
            <p className="text-gray-600 mt-1">{opportunity.opportunity.opportunity_name}</p>
          </div>
        </div>
        <button
          onClick={recalculateScore}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Recalculate Score
        </button>
      </div>

      {/* Score Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Opportunity Score</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {opportunity.opportunity.opportunity_score.toFixed(1)}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Est. Valuation</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(opportunity.opportunity.estimated_valuation)}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm text-gray-600">Financial Health</p>
            <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium ${
              opportunity.opportunity.financial_health === 'excellent' ? 'bg-green-100 text-green-800' :
              opportunity.opportunity.financial_health === 'good' ? 'bg-blue-100 text-blue-800' :
              opportunity.opportunity.financial_health === 'fair' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {opportunity.opportunity.financial_health}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm text-gray-600">Stage</p>
            <p className="text-lg font-semibold text-gray-900 mt-2">
              {opportunity.opportunity.stage.replace('_', ' ').toUpperCase()}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'financials', label: 'Financials' },
              { id: 'intelligence', label: 'Market Intelligence' },
              { id: 'scoring', label: 'Scoring Analysis' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Company Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Information</h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm text-gray-500">Legal Name</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {opportunity.company.legal_name || 'N/A'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500">Industry</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {opportunity.company.industry}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500">Location</dt>
                      <dd className="text-sm font-medium text-gray-900 flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {[
                          opportunity.company.location.city,
                          opportunity.company.location.region,
                          opportunity.company.location.country
                        ].filter(Boolean).join(', ')}
                      </dd>
                    </div>
                    {opportunity.company.website && (
                      <div>
                        <dt className="text-sm text-gray-500">Website</dt>
                        <dd className="text-sm font-medium text-blue-600">
                          <a
                            href={opportunity.company.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 hover:underline"
                          >
                            <Globe className="h-4 w-4" />
                            {opportunity.company.website}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </dd>
                      </div>
                    )}
                    <div>
                      <dt className="text-sm text-gray-500">Data Source</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {opportunity.company.data_source.replace('_', ' ').toUpperCase()}
                      </dd>
                    </div>
                  </dl>
                </div>

                {/* Description */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
                  <p className="text-sm text-gray-700">
                    {opportunity.company.description || 'No description available.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Financials Tab */}
          {activeTab === 'financials' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial History</h3>
              {opportunity.financials.length === 0 ? (
                <p className="text-gray-500">No financial data available.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Year
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Revenue
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          EBITDA
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Net Income
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Total Assets
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Profit Margin
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {opportunity.financials.map((fin) => (
                        <tr key={fin.year}>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {fin.year}
                          </td>
                          <td className="px-6 py-4 text-sm text-right text-gray-900">
                            {formatCurrency(fin.revenue)}
                          </td>
                          <td className="px-6 py-4 text-sm text-right text-gray-900">
                            {formatCurrency(fin.ebitda)}
                          </td>
                          <td className="px-6 py-4 text-sm text-right text-gray-900">
                            {formatCurrency(fin.net_income)}
                          </td>
                          <td className="px-6 py-4 text-sm text-right text-gray-900">
                            {formatCurrency(fin.total_assets)}
                          </td>
                          <td className="px-6 py-4 text-sm text-right text-gray-900">
                            {formatPercentage(fin.profit_margin)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Market Intelligence Tab */}
          {activeTab === 'intelligence' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Intelligence</h3>
              {opportunity.market_intelligence.length === 0 ? (
                <p className="text-gray-500">No market intelligence available.</p>
              ) : (
                <div className="space-y-4">
                  {opportunity.market_intelligence.map((intel) => (
                    <div key={intel.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                            {intel.type.replace('_', ' ')}
                          </span>
                          <span className="text-xs text-gray-500">
                            {intel.source}
                          </span>
                        </div>
                        {intel.relevance_score && (
                          <span className="text-xs text-gray-500">
                            Relevance: {(intel.relevance_score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-700">{intel.content_summary}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(intel.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Scoring Analysis Tab */}
          {activeTab === 'scoring' && scoring && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Scoring Analysis</h3>
                <span className={`px-4 py-2 rounded-full text-sm font-medium ${getRecommendationBadge(scoring.recommendation).color}`}>
                  {getRecommendationBadge(scoring.recommendation).text}
                </span>
              </div>

              <div className="space-y-4">
                {Object.entries(scoring.component_scores).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {key.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-900 font-semibold">
                        {value.score.toFixed(1)} / 100
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${value.score}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        Weight: {value.weight}%
                      </span>
                      <span className="text-xs text-gray-500">
                        Contribution: {value.weighted_contribution.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-xs text-gray-500 mt-4">
                Last scored: {new Date(scoring.scored_at).toLocaleString()}
              </p>
            </div>
          )}

          {activeTab === 'scoring' && !scoring && (
            <p className="text-gray-500">No scoring data available. Click "Recalculate Score" to generate.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpportunityDetail;
