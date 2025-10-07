import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import {
  Users,
  TrendingUp,
  MessageSquare,
  BookOpen,
  Plus,
  Award,
  Heart
} from 'lucide-react';

interface CulturalAssessment {
  id: string;
  assessment_name: string;
  assessment_date: string;
  overall_compatibility_score: number;
  compatibility_level: string;
  acquirer_sentiment_score: number;
  target_sentiment_score: number;
  key_strengths: any[];
  key_risks: any[];
}

interface ChangeInitiative {
  id: string;
  name: string;
  initiative_type: string;
  status: string;
  target_audience: string;
  progress_percentage: number;
  impacted_employee_count: number;
  training_completion_rate: number;
  satisfaction_score: number;
}

export default function ChangeManagement({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [assessments, setAssessments] = useState<CulturalAssessment[]>([]);
  const [initiatives, setInitiatives] = useState<ChangeInitiative[]>([]);
  const [showAssessmentModal, setShowAssessmentModal] = useState(false);
  const [showInitiativeModal, setShowInitiativeModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchAssessments();
      fetchInitiatives();
    }
  }, [organization?.id, projectId]);

  const fetchAssessments = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/cultural-assessments`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAssessments(data);
      }
    } catch (error) {
      console.error('Error fetching assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInitiatives = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/change-initiatives`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setInitiatives(data);
      }
    } catch (error) {
      console.error('Error fetching initiatives:', error);
    }
  };

  const getCompatibilityColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getInitiativeTypeIcon = (type: string) => {
    switch (type) {
      case 'communication':
        return <MessageSquare className="h-5 w-5" />;
      case 'training':
        return <BookOpen className="h-5 w-5" />;
      case 'culture':
        return <Heart className="h-5 w-5" />;
      default:
        return <Users className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      planned: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const latestAssessment = assessments[0];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Users className="h-6 w-6 mr-2 text-indigo-600" />
            Change Management & Culture
          </h2>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowAssessmentModal(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              New Assessment
            </button>
            <button
              onClick={() => setShowInitiativeModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Initiative
            </button>
          </div>
        </div>
      </div>

      {/* Latest Cultural Assessment */}
      {latestAssessment && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Latest Cultural Assessment</h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-indigo-100 mb-3">
                <span className="text-3xl font-bold text-indigo-600">
                  {latestAssessment.overall_compatibility_score}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-900">Overall Compatibility</p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${getCompatibilityColor(latestAssessment.compatibility_level)}`}>
                {latestAssessment.compatibility_level}
              </span>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-100 mb-3">
                <span className="text-3xl font-bold text-blue-600">
                  {latestAssessment.acquirer_sentiment_score}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-900">Acquirer Sentiment</p>
              <p className="text-xs text-gray-500 mt-1">Employee satisfaction</p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-100 mb-3">
                <span className="text-3xl font-bold text-purple-600">
                  {latestAssessment.target_sentiment_score}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-900">Target Sentiment</p>
              <p className="text-xs text-gray-500 mt-1">Employee satisfaction</p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-100 mb-3">
                <Award className="h-10 w-10 text-green-600" />
              </div>
              <p className="text-sm font-medium text-gray-900">Key Strengths</p>
              <p className="text-xs text-gray-500 mt-1">{latestAssessment.key_strengths?.length || 0} identified</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Cultural Strengths</h4>
              {latestAssessment.key_strengths?.length > 0 ? (
                <ul className="space-y-2">
                  {latestAssessment.key_strengths.slice(0, 3).map((strength: any, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-sm text-gray-700">{strength.description || strength}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No strengths identified yet</p>
              )}
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Cultural Risks</h4>
              {latestAssessment.key_risks?.length > 0 ? (
                <ul className="space-y-2">
                  {latestAssessment.key_risks.slice(0, 3).map((risk: any, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-2">⚠</span>
                      <span className="text-sm text-gray-700">{risk.description || risk}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No risks identified yet</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Change Initiatives */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Change Initiatives</h3>

        {initiatives.length === 0 ? (
          <div className="text-center py-8">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No change initiatives yet</p>
            <button
              onClick={() => setShowInitiativeModal(true)}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create First Initiative
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {initiatives.map((initiative) => (
              <div key={initiative.id} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    <div className="p-2 bg-indigo-100 rounded-lg mr-3">
                      {getInitiativeTypeIcon(initiative.initiative_type)}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{initiative.name}</h4>
                      <p className="text-sm text-gray-500 capitalize">{initiative.initiative_type}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(initiative.status)}`}>
                    {initiative.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="space-y-3 mt-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600">Progress</span>
                      <span className="text-xs font-medium text-gray-900">{initiative.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${initiative.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100">
                    <div>
                      <p className="text-xs text-gray-500">Impact</p>
                      <p className="text-sm font-medium text-gray-900">
                        {initiative.impacted_employee_count?.toLocaleString() || 0} employees
                      </p>
                    </div>
                    {initiative.training_completion_rate !== null && (
                      <div>
                        <p className="text-xs text-gray-500">Training</p>
                        <p className="text-sm font-medium text-gray-900">
                          {initiative.training_completion_rate}% complete
                        </p>
                      </div>
                    )}
                  </div>

                  {initiative.satisfaction_score !== null && (
                    <div className="pt-3 border-t border-gray-100">
                      <p className="text-xs text-gray-500 mb-1">Satisfaction Score</p>
                      <div className="flex items-center">
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                initiative.satisfaction_score >= 75 ? 'bg-green-500' :
                                initiative.satisfaction_score >= 50 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${initiative.satisfaction_score}%` }}
                            />
                          </div>
                        </div>
                        <span className="ml-3 text-sm font-medium text-gray-900">
                          {initiative.satisfaction_score}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Initiative Types Summary */}
      {initiatives.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Initiative Breakdown</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['communication', 'training', 'culture', 'process'].map(type => {
              const typeInitiatives = initiatives.filter(i => i.initiative_type === type);
              const avgProgress = typeInitiatives.length > 0
                ? typeInitiatives.reduce((sum, i) => sum + i.progress_percentage, 0) / typeInitiatives.length
                : 0;

              return (
                <div key={type} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center mb-2">
                    {getInitiativeTypeIcon(type)}
                    <span className="ml-2 text-sm font-medium text-gray-900 capitalize">{type}</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{typeInitiatives.length}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {avgProgress.toFixed(0)}% avg progress
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Assessment Modal - Placeholder */}
      {showAssessmentModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 p-6">
            <h3 className="text-lg font-semibold mb-4">Cultural Assessment</h3>
            <p className="text-gray-600 mb-4">Assessment form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowAssessmentModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowAssessmentModal(false);
                  fetchAssessments();
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Save Assessment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Initiative Modal - Placeholder */}
      {showInitiativeModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <h3 className="text-lg font-semibold mb-4">Create Change Initiative</h3>
            <p className="text-gray-600 mb-4">Initiative form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowInitiativeModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowInitiativeModal(false);
                  fetchInitiatives();
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Create Initiative
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
