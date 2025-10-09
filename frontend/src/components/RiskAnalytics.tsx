import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  AlertTriangle, TrendingDown, Shield, BarChart3, Activity, Target,
  Thermometer, Zap, Clock, DollarSign, RefreshCw, Download, Filter,
  Eye, Settings, AlertCircle, CheckCircle, XCircle, ArrowUp, ArrowDown
} from 'lucide-react';

interface RiskMetrics {
  portfolio_id: string;
  value_at_risk_1d: number;
  value_at_risk_5d: number;
  expected_shortfall_1d: number;
  expected_shortfall_5d: number;
  portfolio_volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  concentration_risk: number;
  correlation_risk: number;
  sector_concentration: Record<string, number>;
  largest_position_weight: number;
  total_exposure: number;
  cash_position: number;
  last_updated: string;
}

interface StressTestResult {
  scenario_name: string;
  scenario_description: string;
  portfolio_impact: number;
  portfolio_impact_percentage: number;
  position_impacts: Array<{
    deal_id: string;
    target_company: string;
    impact: number;
    impact_percentage: number;
  }>;
  probability: number;
  stress_test_date: string;
}

interface RiskAlert {
  id: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  portfolio_id?: string;
  position_id?: string;
  threshold_value: number;
  current_value: number;
  created_at: string;
  status: 'active' | 'acknowledged' | 'resolved';
}

interface PositionRisk {
  deal_id: string;
  target_company: string;
  acquirer_company: string;
  position_value: number;
  var_contribution: number;
  beta: number;
  individual_var: number;
  correlation_with_portfolio: number;
  sector: string;
  risk_score: number;
  concentration_risk: number;
  liquidity_risk: number;
}

interface CorrelationMatrix {
  positions: string[];
  correlations: number[][];
  last_updated: string;
}

const RiskAnalytics: React.FC = () => {
  const { getToken } = useAuth();
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>('');
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [stressTestResults, setStressTestResults] = useState<StressTestResult[]>([]);
  const [riskAlerts, setRiskAlerts] = useState<RiskAlert[]>([]);
  const [positionRisks, setPositionRisks] = useState<PositionRisk[]>([]);
  const [correlationMatrix, setCorrelationMatrix] = useState<CorrelationMatrix | null>(null);
  const [portfolios, setPortfolios] = useState<Array<{id: string, name: string}>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'stress' | 'alerts' | 'positions' | 'correlation'>('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1d' | '5d' | '1m'>('1d');

  useEffect(() => {
    loadPortfolios();
  }, []);

  useEffect(() => {
    if (selectedPortfolioId) {
      loadRiskData();
    }
  }, [selectedPortfolioId]);

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
        setPortfolios(data.map((p: any) => ({ id: p.id, name: p.name })));
        if (data.length > 0 && !selectedPortfolioId) {
          setSelectedPortfolioId(data[0].id);
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

  const loadRiskData = async () => {
    if (!selectedPortfolioId) return;

    setRefreshing(true);
    try {
      const token = await getToken();

      // Load all risk data in parallel
      const [metricsRes, stressRes, alertsRes, positionsRes, correlationRes] = await Promise.all([
        fetch(`/api/arbitrage/portfolios/${selectedPortfolioId}/risk-metrics`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`/api/arbitrage/portfolios/${selectedPortfolioId}/stress-tests`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`/api/arbitrage/risk-alerts?portfolio_id=${selectedPortfolioId}`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`/api/arbitrage/portfolios/${selectedPortfolioId}/position-risks`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`/api/arbitrage/portfolios/${selectedPortfolioId}/correlation-matrix`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        })
      ]);

      if (metricsRes.ok) {
        setRiskMetrics(await metricsRes.json());
      }
      if (stressRes.ok) {
        setStressTestResults(await stressRes.json());
      }
      if (alertsRes.ok) {
        setRiskAlerts(await alertsRes.json());
      }
      if (positionsRes.ok) {
        setPositionRisks(await positionsRes.json());
      }
      if (correlationRes.ok) {
        setCorrelationMatrix(await correlationRes.json());
      }

    } catch (err) {
      setError('Error loading risk data');
      console.error('Error loading risk data:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const runStressTest = async (scenarioType: string) => {
    if (!selectedPortfolioId) return;

    try {
      const token = await getToken();
      const response = await fetch('/api/arbitrage/stress-test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          portfolio_id: selectedPortfolioId,
          scenario_type: scenarioType
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setStressTestResults([result, ...stressTestResults]);
        setActiveTab('stress');
      } else {
        setError('Failed to run stress test');
      }
    } catch (err) {
      setError('Error running stress test');
      console.error('Error running stress test:', err);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const token = await getToken();
      const response = await fetch(`/api/arbitrage/risk-alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setRiskAlerts(riskAlerts.map(alert =>
          alert.id === alertId ? { ...alert, status: 'acknowledged' } : alert
        ));
      }
    } catch (err) {
      console.error('Error acknowledging alert:', err);
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

  const getRiskColor = (riskScore: number) => {
    if (riskScore <= 3) return 'text-green-600 bg-green-100';
    if (riskScore <= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-blue-600 bg-blue-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Risk Analytics</h1>
          <p className="text-gray-600">Monitor and analyze portfolio risk metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedPortfolioId}
            onChange={(e) => setSelectedPortfolioId(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {portfolios.map((portfolio) => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
          <button
            onClick={loadRiskData}
            disabled={refreshing}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Active Alerts Summary */}
      {riskAlerts.filter(alert => alert.status === 'active').length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <span className="text-yellow-800 font-medium">
                {riskAlerts.filter(alert => alert.status === 'active').length} Active Risk Alert(s)
              </span>
            </div>
            <button
              onClick={() => setActiveTab('alerts')}
              className="text-yellow-600 hover:text-yellow-800 text-sm font-medium"
            >
              View All →
            </button>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Risk Overview', icon: Shield },
            { id: 'stress', name: 'Stress Testing', icon: Zap },
            { id: 'alerts', name: 'Risk Alerts', icon: AlertTriangle },
            { id: 'positions', name: 'Position Risk', icon: Target },
            { id: 'correlation', name: 'Correlations', icon: Activity },
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

      {/* Risk Overview Tab */}
      {activeTab === 'overview' && riskMetrics && (
        <div className="space-y-6">
          {/* Key Risk Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Value at Risk (1D)</p>
                  <p className="text-2xl font-bold text-red-600">
                    {formatCurrency(riskMetrics.value_at_risk_1d)}
                  </p>
                  <p className="text-sm text-gray-500">95% confidence</p>
                </div>
                <div className="p-3 bg-red-100 rounded-full">
                  <TrendingDown className="h-6 w-6 text-red-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Expected Shortfall (1D)</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {formatCurrency(riskMetrics.expected_shortfall_1d)}
                  </p>
                  <p className="text-sm text-gray-500">Conditional VaR</p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <AlertTriangle className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Portfolio Volatility</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatPercentage(riskMetrics.portfolio_volatility)}
                  </p>
                  <p className="text-sm text-gray-500">Annualized</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                  <p className="text-2xl font-bold text-green-600">
                    {riskMetrics.sharpe_ratio.toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-500">Risk-adjusted</p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <BarChart3 className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Risk Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Composition</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Concentration Risk:</span>
                  <span className={`font-medium px-2 py-1 rounded text-sm ${getRiskColor(riskMetrics.concentration_risk * 10)}`}>
                    {formatPercentage(riskMetrics.concentration_risk)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Correlation Risk:</span>
                  <span className={`font-medium px-2 py-1 rounded text-sm ${getRiskColor(riskMetrics.correlation_risk * 10)}`}>
                    {formatPercentage(riskMetrics.correlation_risk)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Max Drawdown:</span>
                  <span className="font-medium text-red-600">
                    {formatPercentage(riskMetrics.max_drawdown)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Largest Position:</span>
                  <span className="font-medium">
                    {formatPercentage(riskMetrics.largest_position_weight)}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4">Sector Concentration</h3>
              <div className="space-y-3">
                {Object.entries(riskMetrics.sector_concentration).map(([sector, weight]) => (
                  <div key={sector} className="flex items-center justify-between">
                    <span className="text-gray-600 capitalize">{sector}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${Math.min(weight * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-12 text-right">
                        {formatPercentage(weight)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Portfolio Exposure */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Portfolio Exposure</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(riskMetrics.total_exposure)}
                </div>
                <div className="text-sm text-gray-600">Total Exposure</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(riskMetrics.cash_position)}
                </div>
                <div className="text-sm text-gray-600">Cash Position</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {formatPercentage(riskMetrics.total_exposure / (riskMetrics.total_exposure + riskMetrics.cash_position))}
                </div>
                <div className="text-sm text-gray-600">Invested Ratio</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stress Testing Tab */}
      {activeTab === 'stress' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Stress Testing</h3>
              <div className="flex space-x-2">
                {['market_crash', 'deal_break_spike', 'sector_rotation', 'interest_rate_shock'].map((scenario) => (
                  <button
                    key={scenario}
                    onClick={() => runStressTest(scenario)}
                    className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {scenario.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {stressTestResults.length > 0 ? (
              <div className="space-y-4">
                {stressTestResults.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium text-gray-900">{result.scenario_name}</h4>
                        <p className="text-sm text-gray-600">{result.scenario_description}</p>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          result.portfolio_impact < 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {formatCurrency(result.portfolio_impact)}
                        </div>
                        <div className="text-sm text-gray-600">
                          ({formatPercentage(result.portfolio_impact_percentage)})
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-gray-500 mb-3">
                      Probability: {formatPercentage(result.probability)} |
                      Run: {new Date(result.stress_test_date).toLocaleString()}
                    </div>

                    {result.position_impacts.length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Top Position Impacts:</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {result.position_impacts.slice(0, 4).map((impact, idx) => (
                            <div key={idx} className="flex justify-between text-sm">
                              <span className="text-gray-600">{impact.target_company}</span>
                              <span className={`font-medium ${
                                impact.impact < 0 ? 'text-red-600' : 'text-green-600'
                              }`}>
                                {formatCurrency(impact.impact)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No stress test results available. Run a stress test to see potential portfolio impacts.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Risk Alerts Tab */}
      {activeTab === 'alerts' && (
        <div className="space-y-4">
          {riskAlerts.length > 0 ? (
            riskAlerts.map((alert) => (
              <div key={alert.id} className={`border rounded-lg p-4 ${
                alert.status === 'active' ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-white'
              }`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-full ${getAlertColor(alert.severity)}`}>
                      {alert.severity === 'critical' ? (
                        <XCircle className="h-5 w-5" />
                      ) : alert.severity === 'high' ? (
                        <AlertTriangle className="h-5 w-5" />
                      ) : (
                        <AlertCircle className="h-5 w-5" />
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{alert.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        <span>Threshold: {alert.threshold_value}</span>
                        <span>Current: {alert.current_value}</span>
                        <span>{new Date(alert.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.status === 'active' ? 'bg-red-100 text-red-800' :
                      alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {alert.status}
                    </span>
                    {alert.status === 'active' && (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                      >
                        Acknowledge
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Alerts</h3>
              <p className="text-gray-600">All risk metrics are within acceptable thresholds</p>
            </div>
          )}
        </div>
      )}

      {/* Position Risk Tab */}
      {activeTab === 'positions' && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Position Risk Analysis</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    VaR Contribution
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Beta
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Concentration
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {positionRisks.map((position) => (
                  <tr key={position.deal_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="font-medium text-gray-900">{position.target_company}</div>
                        <div className="text-sm text-gray-500">← {position.acquirer_company}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium">{formatCurrency(position.position_value)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium">{formatCurrency(position.var_contribution)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium">{position.beta.toFixed(2)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(position.risk_score)}`}>
                        {position.risk_score}/10
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium">{formatPercentage(position.concentration_risk)}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Correlation Tab */}
      {activeTab === 'correlation' && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Position Correlation Matrix</h3>
          {correlationMatrix ? (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr>
                    <th className="text-left py-2 px-3 text-sm font-medium text-gray-600"></th>
                    {correlationMatrix.positions.map((position, index) => (
                      <th key={index} className="text-center py-2 px-2 text-xs font-medium text-gray-600 transform -rotate-45 h-16">
                        {position.length > 10 ? position.substring(0, 10) + '...' : position}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {correlationMatrix.correlations.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      <td className="py-2 px-3 text-sm font-medium text-gray-600">
                        {correlationMatrix.positions[rowIndex].length > 15
                          ? correlationMatrix.positions[rowIndex].substring(0, 15) + '...'
                          : correlationMatrix.positions[rowIndex]}
                      </td>
                      {row.map((correlation, colIndex) => (
                        <td key={colIndex} className="py-1 px-1 text-center">
                          <div
                            className={`w-8 h-8 flex items-center justify-center text-xs font-medium rounded ${
                              correlation > 0.7 ? 'bg-red-100 text-red-800' :
                              correlation > 0.3 ? 'bg-yellow-100 text-yellow-800' :
                              correlation > -0.3 ? 'bg-green-100 text-green-800' :
                              correlation > -0.7 ? 'bg-blue-100 text-blue-800' :
                              'bg-purple-100 text-purple-800'
                            }`}
                          >
                            {correlation.toFixed(2)}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-4 text-xs text-gray-500">
                Last updated: {new Date(correlationMatrix.last_updated).toLocaleString()}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Correlation matrix not available. Ensure you have multiple positions for correlation analysis.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RiskAnalytics;