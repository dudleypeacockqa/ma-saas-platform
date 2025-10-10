import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import { AlertTriangle, Shield, Plus, FileText } from 'lucide-react';

interface Risk {
  id: string;
  title: string;
  category: string;
  severity: string;
  probability: number;
  impact_score: number;
  risk_score: number;
  status: string;
  mitigation_plan: string;
}

interface Issue {
  id: string;
  title: string;
  priority: string;
  status: string;
  issue_type: string;
  reported_date: string;
  due_date: string | null;
}

export default function RiskRegister({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [risks, setRisks] = useState<Risk[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [activeTab, setActiveTab] = useState<'risks' | 'issues'>('risks');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchRisks();
      fetchIssues();
    }
  }, [organization?.id, projectId]);

  const fetchRisks = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/risks`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRisks(data);
      }
    } catch (error) {
      console.error('Error fetching risks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIssues = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/issues`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setIssues(data);
      }
    } catch (error) {
      console.error('Error fetching issues:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
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
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Shield className="h-6 w-6 mr-2 text-indigo-600" />
              Risk & Issue Register
            </h2>
            <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
              <Plus className="h-4 w-4 mr-2" />
              Add {activeTab === 'risks' ? 'Risk' : 'Issue'}
            </button>
          </div>

          <div className="mt-4 flex space-x-4">
            <button
              onClick={() => setActiveTab('risks')}
              className={`px-4 py-2 text-sm font-medium rounded-md ${
                activeTab === 'risks'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Risks ({risks.length})
            </button>
            <button
              onClick={() => setActiveTab('issues')}
              className={`px-4 py-2 text-sm font-medium rounded-md ${
                activeTab === 'issues'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Issues ({issues.length})
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'risks' ? (
            risks.length === 0 ? (
              <div className="text-center py-12">
                <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No risks identified yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {risks.map(risk => (
                  <div key={risk.id} className={`border-2 rounded-lg p-5 ${getSeverityColor(risk.severity)}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{risk.title}</h3>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(risk.severity)}`}>
                            {risk.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{risk.category}</p>

                        <div className="grid grid-cols-3 gap-4 mb-3">
                          <div>
                            <p className="text-xs text-gray-500">Probability</p>
                            <p className="text-sm font-medium text-gray-900">{risk.probability}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Impact</p>
                            <p className="text-sm font-medium text-gray-900">{risk.impact_score}/10</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Risk Score</p>
                            <p className="text-sm font-bold text-gray-900">{risk.risk_score.toFixed(1)}</p>
                          </div>
                        </div>

                        {risk.mitigation_plan && (
                          <div className="mt-3 p-3 bg-white bg-opacity-50 rounded">
                            <p className="text-xs font-medium text-gray-700 mb-1">Mitigation Plan</p>
                            <p className="text-sm text-gray-600">{risk.mitigation_plan}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            issues.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No issues reported yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {issues.map(issue => (
                  <div key={issue.id} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{issue.title}</h3>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(issue.priority)}`}>
                            {issue.priority.toUpperCase()}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mt-3">
                          <div>
                            <p className="text-xs text-gray-500">Type</p>
                            <p className="text-sm font-medium text-gray-900 capitalize">{issue.issue_type}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Status</p>
                            <p className="text-sm font-medium text-gray-900 capitalize">{issue.status.replace('_', ' ')}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Reported</p>
                            <p className="text-sm font-medium text-gray-900">
                              {new Date(issue.reported_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        {issue.due_date && (
                          <div className="mt-3">
                            <p className="text-xs text-gray-500">Due Date</p>
                            <p className="text-sm font-medium text-gray-900">
                              {new Date(issue.due_date).toLocaleDateString()}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
