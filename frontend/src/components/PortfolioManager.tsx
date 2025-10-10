import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  TrendingUp, TrendingDown, DollarSign, Target, BarChart3, PieChart,
  Shuffle, AlertTriangle, Settings, Plus, Trash2, Edit, Save, X,
  RefreshCw, Download, Upload, Calendar, Filter
} from 'lucide-react';

interface Portfolio {
  id: string;
  name: string;
  description?: string;
  total_capital: number;
  available_capital: number;
  invested_capital: number;
  target_return: number;
  max_position_size: number;
  max_single_deal_exposure: number;
  risk_tolerance: string;
  created_at: string;
  updated_at: string;
  performance_summary?: {
    total_return: number;
    annualized_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
  };
}

interface Position {
  id: string;
  portfolio_id: string;
  deal_id: string;
  target_company: string;
  acquirer_company: string;
  shares: number;
  entry_price: number;
  current_price?: number;
  position_value: number;
  unrealized_pnl?: number;
  unrealized_pnl_percentage?: number;
  position_size_percentage: number;
  entry_date: string;
  status: string;
  risk_score?: number;
}

interface OptimizationRequest {
  portfolio_id: string;
  objective: string;
  max_positions: number;
  risk_tolerance: number;
  sector_limits?: Record<string, number>;
}

interface OptimizationResult {
  recommended_positions: Array<{
    deal_id: string;
    target_company: string;
    recommended_allocation: number;
    expected_return: number;
    risk_score: number;
    rationale: string;
  }>;
  portfolio_metrics: {
    expected_return: number;
    expected_risk: number;
    sharpe_ratio: number;
  };
  rebalancing_trades: Array<{
    action: string;
    deal_id: string;
    target_company: string;
    shares: number;
    estimated_cost: number;
  }>;
}

const PortfolioManager: React.FC = () => {
  const { getToken } = useAuth();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'positions' | 'optimization' | 'analytics'>('overview');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPortfolio, setEditingPortfolio] = useState<Portfolio | null>(null);
  const [newPortfolio, setNewPortfolio] = useState({
    name: '',
    description: '',
    total_capital: 1000000,
    target_return: 0.15,
    max_position_size: 0.10,
    max_single_deal_exposure: 0.05,
    risk_tolerance: 'moderate'
  });

  useEffect(() => {
    loadPortfolios();
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      loadPositions(selectedPortfolio.id);
    }
  }, [selectedPortfolio]);

  const loadPortfolios = async () => {
    try {
      const token = await getToken();
      const response = await fetch('/api/arbitrage/portfolios', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPortfolios(data);
        if (data.length > 0 && !selectedPortfolio) {
          setSelectedPortfolio(data[0]);
        }
      } else {
        setError('Failed to load portfolios');
      }
    } catch (err) {
      setError('Error loading portfolios');
      console.error('Error loading portfolios:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPositions = async (portfolioId: string) => {
    try {
      const token = await getToken();
      const response = await fetch(`/api/arbitrage/portfolios/${portfolioId}/positions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPositions(data);
      } else {
        setError('Failed to load positions');
      }
    } catch (err) {
      setError('Error loading positions');
      console.error('Error loading positions:', err);
    }
  };

  const createPortfolio = async () => {
    try {
      const token = await getToken();
      const response = await fetch('/api/arbitrage/portfolios', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPortfolio),
      });

      if (response.ok) {
        const portfolio = await response.json();
        setPortfolios([...portfolios, portfolio]);
        setSelectedPortfolio(portfolio);
        setShowCreateForm(false);
        setNewPortfolio({
          name: '',
          description: '',
          total_capital: 1000000,
          target_return: 0.15,
          max_position_size: 0.10,
          max_single_deal_exposure: 0.05,
          risk_tolerance: 'moderate'
        });
      } else {
        setError('Failed to create portfolio');
      }
    } catch (err) {
      setError('Error creating portfolio');
      console.error('Error creating portfolio:', err);
    }
  };

  const updatePortfolio = async (portfolio: Portfolio) => {
    try {
      const token = await getToken();
      const response = await fetch(`/api/arbitrage/portfolios/${portfolio.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(portfolio),
      });

      if (response.ok) {
        const updated = await response.json();
        setPortfolios(portfolios.map(p => p.id === updated.id ? updated : p));
        setSelectedPortfolio(updated);
        setEditingPortfolio(null);
      } else {
        setError('Failed to update portfolio');
      }
    } catch (err) {
      setError('Error updating portfolio');
      console.error('Error updating portfolio:', err);
    }
  };

  const optimizePortfolio = async () => {
    if (!selectedPortfolio) return;

    try {
      const token = await getToken();
      const optimizationRequest: OptimizationRequest = {
        portfolio_id: selectedPortfolio.id,
        objective: 'sharpe_ratio',
        max_positions: 20,
        risk_tolerance: selectedPortfolio.max_position_size
      };

      const response = await fetch('/api/arbitrage/optimize', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(optimizationRequest),
      });

      if (response.ok) {
        const result = await response.json();
        setOptimizationResult(result);
        setActiveTab('optimization');
      } else {
        setError('Failed to optimize portfolio');
      }
    } catch (err) {
      setError('Error optimizing portfolio');
      console.error('Error optimizing portfolio:', err);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Manager</h1>
          <p className="text-gray-600">Manage and optimize your arbitrage portfolios</p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            <span>Create Portfolio</span>
          </button>
          <button
            onClick={optimizePortfolio}
            disabled={!selectedPortfolio}
            className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <BarChart3 className="h-4 w-4" />
            <span>Optimize</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Portfolio Selection */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Portfolios</h2>
          <div className="text-sm text-gray-500">{portfolios.length} portfolio(s)</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {portfolios.map((portfolio) => (
            <div
              key={portfolio.id}
              onClick={() => setSelectedPortfolio(portfolio)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedPortfolio?.id === portfolio.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">{portfolio.name}</h3>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingPortfolio(portfolio);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Edit className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Capital:</span>
                  <span className="font-medium">{formatCurrency(portfolio.total_capital)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Invested:</span>
                  <span className="font-medium">{formatCurrency(portfolio.invested_capital)}</span>
                </div>
                {portfolio.performance_summary && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Return:</span>
                    <span className={`font-medium ${
                      portfolio.performance_summary.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(portfolio.performance_summary.total_return)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Portfolio Details */}
      {selectedPortfolio && (
        <div className="space-y-6">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', name: 'Overview', icon: PieChart },
                { id: 'positions', name: 'Positions', icon: Target },
                { id: 'optimization', name: 'Optimization', icon: BarChart3 },
                { id: 'analytics', name: 'Analytics', icon: TrendingUp },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold mb-4">Portfolio Summary</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Capital:</span>
                    <span className="font-medium">{formatCurrency(selectedPortfolio.total_capital)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Invested Capital:</span>
                    <span className="font-medium">{formatCurrency(selectedPortfolio.invested_capital)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Available Capital:</span>
                    <span className="font-medium">{formatCurrency(selectedPortfolio.available_capital)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Target Return:</span>
                    <span className="font-medium">{formatPercentage(selectedPortfolio.target_return)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Max Position Size:</span>
                    <span className="font-medium">{formatPercentage(selectedPortfolio.max_position_size)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Tolerance:</span>
                    <span className="font-medium capitalize">{selectedPortfolio.risk_tolerance}</span>
                  </div>
                </div>
              </div>

              {selectedPortfolio.performance_summary && (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Return:</span>
                      <span className={`font-medium ${
                        selectedPortfolio.performance_summary.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercentage(selectedPortfolio.performance_summary.total_return)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Annualized Return:</span>
                      <span className="font-medium">
                        {formatPercentage(selectedPortfolio.performance_summary.annualized_return)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sharpe Ratio:</span>
                      <span className="font-medium">
                        {selectedPortfolio.performance_summary.sharpe_ratio.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Drawdown:</span>
                      <span className="font-medium text-red-600">
                        {formatPercentage(selectedPortfolio.performance_summary.max_drawdown)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Win Rate:</span>
                      <span className="font-medium">
                        {formatPercentage(selectedPortfolio.performance_summary.win_rate)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Positions Tab */}
          {activeTab === 'positions' && (
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Active Positions</h3>
                  <div className="text-sm text-gray-500">{positions.length} position(s)</div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Deal
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Position
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        P&L
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Risk Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {positions.map((position) => (
                      <tr key={position.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium text-gray-900">{position.target_company}</div>
                            <div className="text-sm text-gray-500">← {position.acquirer_company}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium">{position.shares.toLocaleString()} shares</div>
                            <div className="text-sm text-gray-500">
                              {formatPercentage(position.position_size_percentage)} of portfolio
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium">{formatCurrency(position.position_value)}</div>
                            <div className="text-sm text-gray-500">
                              Entry: {formatCurrency(position.entry_price)}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {position.unrealized_pnl !== undefined && (
                            <div className={`font-medium ${
                              position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatCurrency(position.unrealized_pnl)}
                              <div className="text-sm">
                                ({formatPercentage(position.unrealized_pnl_percentage || 0)})
                              </div>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {position.risk_score !== undefined && (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              position.risk_score <= 3 ? 'bg-green-100 text-green-800' :
                              position.risk_score <= 6 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {position.risk_score}/10
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            position.status === 'active' ? 'bg-blue-100 text-blue-800' :
                            position.status === 'closed' ? 'bg-gray-100 text-gray-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {position.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Optimization Tab */}
          {activeTab === 'optimization' && (
            <div className="space-y-6">
              {optimizationResult ? (
                <>
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold mb-4">Optimization Results</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatPercentage(optimizationResult.portfolio_metrics.expected_return)}
                        </div>
                        <div className="text-sm text-gray-600">Expected Return</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {formatPercentage(optimizationResult.portfolio_metrics.expected_risk)}
                        </div>
                        <div className="text-sm text-gray-600">Expected Risk</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {optimizationResult.portfolio_metrics.sharpe_ratio.toFixed(2)}
                        </div>
                        <div className="text-sm text-gray-600">Sharpe Ratio</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow-sm border">
                    <div className="p-6 border-b border-gray-200">
                      <h3 className="text-lg font-semibold">Recommended Positions</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Deal
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Allocation
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Expected Return
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Risk Score
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Rationale
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {optimizationResult.recommended_positions.map((position, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="font-medium text-gray-900">{position.target_company}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="font-medium">{formatPercentage(position.recommended_allocation)}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="font-medium text-green-600">
                                  {formatPercentage(position.expected_return)}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  position.risk_score <= 3 ? 'bg-green-100 text-green-800' :
                                  position.risk_score <= 6 ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {position.risk_score}/10
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <div className="text-sm text-gray-900">{position.rationale}</div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {optimizationResult.rebalancing_trades.length > 0 && (
                    <div className="bg-white rounded-lg shadow-sm border">
                      <div className="p-6 border-b border-gray-200">
                        <h3 className="text-lg font-semibold">Rebalancing Trades</h3>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Action
                              </th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Deal
                              </th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Shares
                              </th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Estimated Cost
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {optimizationResult.rebalancing_trades.map((trade, index) => (
                              <tr key={index} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    trade.action === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                  }`}>
                                    {trade.action.toUpperCase()}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="font-medium text-gray-900">{trade.target_company}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="font-medium">{trade.shares.toLocaleString()}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="font-medium">{formatCurrency(trade.estimated_cost)}</div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
                  <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Optimization</h3>
                  <p className="text-gray-600 mb-4">
                    Run optimization to get recommendations for improving your portfolio allocation
                  </p>
                  <button
                    onClick={optimizePortfolio}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Run Optimization
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Advanced Analytics</h3>
              <p className="text-gray-600">
                Detailed performance analytics and risk metrics coming soon
              </p>
            </div>
          )}
        </div>
      )}

      {/* Create Portfolio Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-90vh overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Create New Portfolio</h3>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Portfolio Name
                </label>
                <input
                  type="text"
                  value={newPortfolio.name}
                  onChange={(e) => setNewPortfolio({ ...newPortfolio, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter portfolio name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={newPortfolio.description}
                  onChange={(e) => setNewPortfolio({ ...newPortfolio, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="Portfolio description"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Total Capital
                  </label>
                  <input
                    type="number"
                    value={newPortfolio.total_capital}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, total_capital: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Return (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newPortfolio.target_return * 100}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, target_return: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Position Size (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newPortfolio.max_position_size * 100}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, max_position_size: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Single Deal Exposure (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newPortfolio.max_single_deal_exposure * 100}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, max_single_deal_exposure: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risk Tolerance
                </label>
                <select
                  value={newPortfolio.risk_tolerance}
                  onChange={(e) => setNewPortfolio({ ...newPortfolio, risk_tolerance: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="conservative">Conservative</option>
                  <option value="moderate">Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end space-x-4">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={createPortfolio}
                disabled={!newPortfolio.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Portfolio
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Portfolio Modal */}
      {editingPortfolio && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-90vh overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Edit Portfolio</h3>
                <button
                  onClick={() => setEditingPortfolio(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Portfolio Name
                </label>
                <input
                  type="text"
                  value={editingPortfolio.name}
                  onChange={(e) => setEditingPortfolio({ ...editingPortfolio, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={editingPortfolio.description || ''}
                  onChange={(e) => setEditingPortfolio({ ...editingPortfolio, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Total Capital
                  </label>
                  <input
                    type="number"
                    value={editingPortfolio.total_capital}
                    onChange={(e) => setEditingPortfolio({ ...editingPortfolio, total_capital: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Return (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingPortfolio.target_return * 100}
                    onChange={(e) => setEditingPortfolio({ ...editingPortfolio, target_return: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Position Size (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingPortfolio.max_position_size * 100}
                    onChange={(e) => setEditingPortfolio({ ...editingPortfolio, max_position_size: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Single Deal Exposure (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingPortfolio.max_single_deal_exposure * 100}
                    onChange={(e) => setEditingPortfolio({ ...editingPortfolio, max_single_deal_exposure: Number(e.target.value) / 100 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risk Tolerance
                </label>
                <select
                  value={editingPortfolio.risk_tolerance}
                  onChange={(e) => setEditingPortfolio({ ...editingPortfolio, risk_tolerance: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="conservative">Conservative</option>
                  <option value="moderate">Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end space-x-4">
              <button
                onClick={() => setEditingPortfolio(null)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => updatePortfolio(editingPortfolio)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioManager;