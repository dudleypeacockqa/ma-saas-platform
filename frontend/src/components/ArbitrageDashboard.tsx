import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  AlertTriangle,
  BarChart3,
  PieChart,
  Activity,
  Calendar,
  Filter,
  Search,
  RefreshCw,
  Plus,
  Eye,
  ShieldCheck,
  Clock,
  ArrowLeft,
  Shield
} from 'lucide-react';

interface Deal {
  id: string;
  target_company: string;
  acquirer_company: string;
  deal_type: string;
  deal_value?: number;
  current_status: string;
  gross_spread_percentage?: number;
  annualized_return?: number;
  completion_probability?: number;
  announcement_date: string;
  expected_close_date?: string;
  overall_risk_score?: number;
}

interface Portfolio {
  id: string;
  portfolio_name: string;
  strategy_type: string;
  current_capital: number;
  total_return?: number;
  sharpe_ratio?: number;
  number_of_positions: number;
  is_active: boolean;
}

interface MarketOverview {
  deals: {
    total: number;
    active: number;
    completion_rate?: number;
  };
  positions: {
    total: number;
    active: number;
  };
  portfolios: {
    total: number;
    active: number;
  };
  market_conditions: {
    volatility_regime: string;
    deal_flow: string;
    risk_environment: string;
  };
}

const ArbitrageDashboard: React.FC = () => {
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const [deals, setDeals] = useState<Deal[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadDashboardData();
  }, [selectedTimeRange, filterStatus]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Load deals
      const dealsResponse = await fetch('/api/arbitrage/deals', { headers });
      if (!dealsResponse.ok) throw new Error(`Failed to load deals: ${dealsResponse.status}`);
      const dealsData = await dealsResponse.json();

      // Load portfolios
      const portfoliosResponse = await fetch('/api/arbitrage/portfolios', { headers });
      if (!portfoliosResponse.ok) throw new Error(`Failed to load portfolios: ${portfoliosResponse.status}`);
      const portfoliosData = await portfoliosResponse.json();

      // Load market overview
      const overviewResponse = await fetch('/api/arbitrage/analytics/market-overview', { headers });
      if (!overviewResponse.ok) throw new Error(`Failed to load market overview: ${overviewResponse.status}`);
      const overviewData = await overviewResponse.json();

      setDeals(dealsData);
      setPortfolios(portfoliosData);
      setMarketOverview(overviewData);

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'announced': 'bg-blue-100 text-blue-700',
      'regulatory_review': 'bg-yellow-100 text-yellow-700',
      'shareholder_approval': 'bg-purple-100 text-purple-700',
      'closing_conditions': 'bg-orange-100 text-orange-700',
      'completed': 'bg-green-100 text-green-700',
      'terminated': 'bg-red-100 text-red-700'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700';
  };

  const getRiskColor = (riskScore?: number) => {
    if (!riskScore) return 'text-gray-500';
    if (riskScore < 30) return 'text-green-600';
    if (riskScore < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getReturnColor = (returnValue?: number) => {
    if (!returnValue) return 'text-gray-500';
    if (returnValue > 0.15) return 'text-green-600';
    if (returnValue > 0.08) return 'text-blue-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 mt-4">Loading arbitrage dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto" />
          <p className="text-red-600 mt-4">Error: {error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-4 mb-2">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span className="text-sm">Back to Dashboard</span>
                </button>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => navigate('/portfolio-manager')}
                    className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors"
                  >
                    <PieChart className="h-4 w-4" />
                    <span>Portfolios</span>
                  </button>
                  <button
                    onClick={() => navigate('/risk-analytics')}
                    className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors"
                  >
                    <Shield className="h-4 w-4" />
                    <span>Risk Analytics</span>
                  </button>
                </div>
              </div>
              <h1 className="text-3xl font-bold text-gray-900">M&A Arbitrage Dashboard</h1>
              <p className="text-gray-600 mt-1">Monitor deals, portfolios, and market opportunities</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button
                onClick={loadDashboardData}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
              >
                <RefreshCw className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Market Overview Cards */}
        {marketOverview && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Target className="h-6 w-6 text-blue-600" />
                </div>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{marketOverview.deals.active}</p>
                <p className="text-sm text-gray-600">Active Deals</p>
                <p className="text-xs text-gray-500 mt-1">
                  {marketOverview.deals.total} total deals
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
                <Activity className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{marketOverview.positions.active}</p>
                <p className="text-sm text-gray-600">Active Positions</p>
                <p className="text-xs text-gray-500 mt-1">
                  {marketOverview.positions.total} total positions
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <PieChart className="h-6 w-6 text-purple-600" />
                </div>
                <BarChart3 className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{marketOverview.portfolios.active}</p>
                <p className="text-sm text-gray-600">Active Portfolios</p>
                <p className="text-xs text-gray-500 mt-1">
                  {marketOverview.portfolios.total} total portfolios
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <ShieldCheck className="h-6 w-6 text-orange-600" />
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  marketOverview.market_conditions.risk_environment === 'STABLE'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {marketOverview.market_conditions.risk_environment}
                </span>
              </div>
              <div>
                <p className="text-lg font-bold text-gray-900">
                  {marketOverview.market_conditions.deal_flow}
                </p>
                <p className="text-sm text-gray-600">Deal Flow</p>
                <p className="text-xs text-gray-500 mt-1">
                  {marketOverview.market_conditions.volatility_regime} volatility
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Portfolios Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Portfolio Performance</h2>
                <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View All
                </button>
              </div>
            </div>
            <div className="p-6">
              {portfolios.length === 0 ? (
                <div className="text-center py-8">
                  <PieChart className="h-12 w-12 text-gray-400 mx-auto" />
                  <p className="text-gray-600 mt-4">No portfolios created</p>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Create Portfolio
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {portfolios.slice(0, 3).map((portfolio) => (
                    <div key={portfolio.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h3 className="font-medium text-gray-900">{portfolio.portfolio_name}</h3>
                        <p className="text-sm text-gray-600">{portfolio.strategy_type}</p>
                        <p className="text-xs text-gray-500">
                          {portfolio.number_of_positions} positions • {formatCurrency(portfolio.current_capital)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm font-medium ${
                          portfolio.total_return && portfolio.total_return > 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}>
                          {portfolio.total_return ? formatPercentage(portfolio.total_return) : 'N/A'}
                        </p>
                        <p className="text-xs text-gray-500">
                          Sharpe: {portfolio.sharpe_ratio?.toFixed(2) || 'N/A'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Deal Activity */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Deal Activity</h2>
                <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View All Deals
                </button>
              </div>
            </div>
            <div className="p-6">
              {deals.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-400 mx-auto" />
                  <p className="text-gray-600 mt-4">No deals tracked</p>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Add Deal
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {deals.slice(0, 3).map((deal) => (
                    <div key={deal.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h3 className="font-medium text-gray-900">{deal.target_company}</h3>
                        <p className="text-sm text-gray-600">← {deal.acquirer_company}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(deal.current_status)}`}>
                            {deal.current_status.replace('_', ' ')}
                          </span>
                          <span className="text-xs text-gray-500">{deal.deal_type}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm font-medium ${getReturnColor(deal.annualized_return)}`}>
                          {deal.annualized_return ? formatPercentage(deal.annualized_return) : 'N/A'}
                        </p>
                        <p className="text-xs text-gray-500">
                          Risk: <span className={getRiskColor(deal.overall_risk_score)}>
                            {deal.overall_risk_score?.toFixed(0) || 'N/A'}
                          </span>
                        </p>
                        <p className="text-xs text-gray-500">
                          {deal.completion_probability ? `${(deal.completion_probability * 100).toFixed(0)}% prob` : ''}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Active Deals Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Active Arbitrage Opportunities</h2>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-gray-500" />
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="text-sm border border-gray-300 rounded-md px-3 py-1"
                  >
                    <option value="all">All Statuses</option>
                    <option value="announced">Announced</option>
                    <option value="regulatory_review">Regulatory Review</option>
                    <option value="shareholder_approval">Shareholder Approval</option>
                  </select>
                </div>
                <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  <Plus className="h-4 w-4" />
                  <span>Add Deal</span>
                </button>
              </div>
            </div>
          </div>

          {deals.length === 0 ? (
            <div className="p-12 text-center">
              <Target className="h-12 w-12 text-gray-400 mx-auto" />
              <p className="text-gray-600 mt-4">No arbitrage opportunities found</p>
              <p className="text-gray-500 text-sm mt-1">Add deals to start tracking arbitrage opportunities</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Deal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Spread
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Annual Return
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timeline
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deals.map((deal) => (
                    <tr key={deal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {deal.target_company}
                          </div>
                          <div className="text-sm text-gray-500">
                            ← {deal.acquirer_company}
                          </div>
                          <div className="text-xs text-gray-400">
                            {deal.deal_type} • {deal.deal_value ? formatCurrency(deal.deal_value) : 'Undisclosed'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(deal.current_status)}`}>
                          {deal.current_status.replace('_', ' ')}
                        </span>
                        {deal.completion_probability && (
                          <div className="text-xs text-gray-500 mt-1">
                            {(deal.completion_probability * 100).toFixed(0)}% prob
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {deal.gross_spread_percentage ? formatPercentage(deal.gross_spread_percentage) : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${getReturnColor(deal.annualized_return)}`}>
                          {deal.annualized_return ? formatPercentage(deal.annualized_return) : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${getRiskColor(deal.overall_risk_score)}`}>
                          {deal.overall_risk_score ? `${deal.overall_risk_score.toFixed(0)}/100` : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {deal.expected_close_date
                            ? new Date(deal.expected_close_date).toLocaleDateString()
                            : 'TBD'
                          }
                        </div>
                        <div className="text-xs text-gray-500">
                          Announced: {new Date(deal.announcement_date).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center space-x-2">
                          <button className="text-blue-600 hover:text-blue-700">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="text-green-600 hover:text-green-700">
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ArbitrageDashboard;