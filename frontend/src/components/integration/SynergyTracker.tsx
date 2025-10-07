import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Plus,
  BarChart3,
  Target,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface Synergy {
  id: string;
  name: string;
  synergy_type: string;
  target_value: number;
  probability_weighted_value: number;
  status: string;
  realization_start_date: string;
  full_run_rate_date: string;
}

interface WaterfallData {
  total_target: number;
  total_probability_weighted: number;
  total_realized: number;
  overall_capture_rate: number;
  by_type: Array<{
    type: string;
    target: number;
    probability_weighted: number;
    realized: number;
    capture_rate: number;
  }>;
}

export default function SynergyTracker({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [synergies, setSynergies] = useState<Synergy[]>([]);
  const [waterfallData, setWaterfallData] = useState<WaterfallData | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedSynergy, setSelectedSynergy] = useState<Synergy | null>(null);
  const [showRealizationModal, setShowRealizationModal] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchSynergies();
      fetchWaterfallData();
    }
  }, [organization?.id, projectId, filterType]);

  const fetchSynergies = async () => {
    try {
      const url = filterType === 'all'
        ? `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/synergies`
        : `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/synergies?synergy_type=${filterType}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${await organization?.getToken()}`,
          'X-Organization-ID': organization?.id || ''
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSynergies(data);
      }
    } catch (error) {
      console.error('Error fetching synergies:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWaterfallData = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/synergies/waterfall`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setWaterfallData(data);
      }
    } catch (error) {
      console.error('Error fetching waterfall data:', error);
    }
  };

  const getSynergyTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      revenue: 'bg-green-100 text-green-800',
      cost: 'bg-blue-100 text-blue-800',
      operational: 'bg-purple-100 text-purple-800',
      technology: 'bg-indigo-100 text-indigo-800',
      market: 'bg-yellow-100 text-yellow-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      identified: 'bg-gray-100 text-gray-800',
      approved: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      realized: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatType = (type: string) => {
    return type.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Summary */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Synergy Tracker</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Identify Synergy
          </button>
        </div>

        {waterfallData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600 font-medium mb-1">Total Target</p>
              <p className="text-2xl font-bold text-blue-900">
                {formatCurrency(waterfallData.total_target)}
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-purple-600 font-medium mb-1">Probability Weighted</p>
              <p className="text-2xl font-bold text-purple-900">
                {formatCurrency(waterfallData.total_probability_weighted)}
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600 font-medium mb-1">Total Realized</p>
              <p className="text-2xl font-bold text-green-900">
                {formatCurrency(waterfallData.total_realized)}
              </p>
            </div>

            <div className="p-4 bg-indigo-50 rounded-lg">
              <p className="text-sm text-indigo-600 font-medium mb-1">Capture Rate</p>
              <p className="text-2xl font-bold text-indigo-900">
                {waterfallData.overall_capture_rate.toFixed(1)}%
              </p>
              <div className="mt-2 w-full bg-indigo-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(waterfallData.overall_capture_rate, 100)}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Waterfall Chart by Type */}
      {waterfallData && waterfallData.by_type.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2 text-indigo-600" />
            Synergy Waterfall by Type
          </h3>

          <div className="space-y-4">
            {waterfallData.by_type.map((item) => (
              <div key={item.type} className="border-l-4 border-indigo-600 pl-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-gray-900">{formatType(item.type)}</h4>
                    <p className="text-sm text-gray-500">
                      Capture Rate: {item.capture_rate.toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {formatCurrency(item.realized)} / {formatCurrency(item.target)}
                    </p>
                  </div>
                </div>
                <div className="relative pt-1">
                  <div className="overflow-hidden h-4 mb-2 text-xs flex rounded bg-gray-200">
                    <div
                      style={{ width: `${Math.min(item.capture_rate, 100)}%` }}
                      className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all ${
                        item.capture_rate >= 75 ? 'bg-green-500' :
                        item.capture_rate >= 50 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Filter by Type:</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
          >
            <option value="all">All Types</option>
            <option value="revenue">Revenue</option>
            <option value="cost">Cost</option>
            <option value="operational">Operational</option>
            <option value="technology">Technology</option>
            <option value="market">Market</option>
          </select>
        </div>
      </div>

      {/* Synergies List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Synergy Opportunities</h3>
        </div>

        {synergies.length === 0 ? (
          <div className="p-8 text-center">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No synergies identified yet</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Identify First Synergy
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {synergies.map((synergy) => (
              <div
                key={synergy.id}
                className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => {
                  setSelectedSynergy(synergy);
                  setShowRealizationModal(true);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-lg font-medium text-gray-900">{synergy.name}</h4>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSynergyTypeColor(synergy.synergy_type)}`}>
                        {formatType(synergy.synergy_type)}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(synergy.status)}`}>
                        {formatType(synergy.status)}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mt-3">
                      <div>
                        <p className="text-xs text-gray-500">Target Value</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {formatCurrency(synergy.target_value)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Probability Weighted</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {formatCurrency(synergy.probability_weighted_value)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Timeline</p>
                        <p className="text-sm font-medium text-gray-900">
                          {synergy.realization_start_date ? new Date(synergy.realization_start_date).toLocaleDateString() : 'Not set'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="ml-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedSynergy(synergy);
                        setShowRealizationModal(true);
                      }}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <DollarSign className="h-4 w-4 mr-1" />
                      Record
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Synergy Modal - Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <h3 className="text-lg font-semibold mb-4">Identify New Synergy</h3>
            <p className="text-gray-600 mb-4">Synergy creation form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  fetchSynergies();
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Create Synergy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Record Realization Modal - Placeholder */}
      {showRealizationModal && selectedSynergy && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Record Realization: {selectedSynergy.name}
            </h3>
            <p className="text-gray-600 mb-4">Realization tracking form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRealizationModal(false);
                  setSelectedSynergy(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowRealizationModal(false);
                  setSelectedSynergy(null);
                  fetchSynergies();
                  fetchWaterfallData();
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Save Realization
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
