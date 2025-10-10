import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import { Activity, TrendingUp, TrendingDown, Minus, Target } from 'lucide-react';

interface KPI {
  id: string;
  name: string;
  category: string;
  measurement_unit: string;
  baseline_value: number;
  target_value: number;
  current_value: number;
  health_indicator: string;
  trend_direction: string;
  variance_percentage: number;
  last_measured_date: string;
}

export default function PerformanceMonitor({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchKPIs();
    }
  }, [organization?.id, projectId, filterCategory]);

  const fetchKPIs = async () => {
    try {
      const url = filterCategory === 'all'
        ? `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/kpis`
        : `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/kpis?category=${filterCategory}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${await organization?.getToken()}`,
          'X-Organization-ID': organization?.id || ''
        }
      });

      if (response.ok) {
        const data = await response.json();
        setKpis(data);
      }
    } catch (error) {
      console.error('Error fetching KPIs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (indicator: string) => {
    const colors: Record<string, string> = {
      green: 'bg-green-100 text-green-800 border-green-200',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      red: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[indicator] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'declining':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      default:
        return <Minus className="h-5 w-5 text-gray-600" />;
    }
  };

  const formatValue = (value: number, unit: string) => {
    if (unit === 'percentage' || unit === '%') {
      return `${value.toFixed(1)}%`;
    } else if (unit === 'dollars' || unit === '$') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
      }).format(value);
    } else {
      return value.toLocaleString();
    }
  };

  const categories = ['all', 'financial', 'operational', 'cultural', 'customer', 'employee'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Activity className="h-6 w-6 mr-2 text-indigo-600" />
            Performance Monitor
          </h2>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
        </div>

        {kpis.length === 0 ? (
          <div className="text-center py-12">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No KPIs configured yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {kpis.map(kpi => (
              <div key={kpi.id} className={`border-2 rounded-lg p-5 ${getHealthColor(kpi.health_indicator)}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{kpi.name}</h3>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-white bg-opacity-50">
                      {kpi.category}
                    </span>
                  </div>
                  {getTrendIcon(kpi.trend_direction)}
                </div>

                <div className="mt-4">
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-3xl font-bold text-gray-900">
                      {formatValue(kpi.current_value, kpi.measurement_unit)}
                    </span>
                    {kpi.variance_percentage !== null && (
                      <span className={`text-sm font-medium ${
                        kpi.variance_percentage > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {kpi.variance_percentage > 0 ? '+' : ''}{kpi.variance_percentage.toFixed(1)}%
                      </span>
                    )}
                  </div>

                  <div className="relative pt-1">
                    <div className="flex mb-2 items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold inline-block text-gray-600">
                          Baseline: {formatValue(kpi.baseline_value, kpi.measurement_unit)}
                        </span>
                      </div>
                      <div>
                        <span className="text-xs font-semibold inline-block text-gray-600">
                          Target: {formatValue(kpi.target_value, kpi.measurement_unit)}
                        </span>
                      </div>
                    </div>
                    <div className="overflow-hidden h-2 mb-2 text-xs flex rounded bg-white bg-opacity-50">
                      <div
                        style={{ width: `${Math.min(Math.abs((kpi.current_value - kpi.baseline_value) / (kpi.target_value - kpi.baseline_value)) * 100, 100)}%` }}
                        className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                          kpi.health_indicator === 'green' ? 'bg-green-500' :
                          kpi.health_indicator === 'yellow' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                      />
                    </div>
                  </div>

                  {kpi.last_measured_date && (
                    <p className="text-xs text-gray-600 mt-2">
                      Last updated: {new Date(kpi.last_measured_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
