import React, { useState, useEffect } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import { Calendar, CheckCircle, Circle, Clock, AlertCircle } from 'lucide-react';

interface Milestone {
  id: string;
  name: string;
  phase: string;
  target_date: string;
  actual_completion_date: string | null;
  is_completed: boolean;
  completion_percentage: number;
  deliverables_completed: number;
  deliverables_total: number;
}

export default function IntegrationTimeline({ projectId }: { projectId: string }) {
  const { organization } = useOrganization();
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (organization?.id && projectId) {
      fetchMilestones();
    }
  }, [organization?.id, projectId]);

  const fetchMilestones = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects/${projectId}/milestones`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMilestones(data);
      }
    } catch (error) {
      console.error('Error fetching milestones:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMilestoneIcon = (milestone: Milestone) => {
    if (milestone.is_completed) {
      return <CheckCircle className="h-6 w-6 text-green-600" />;
    } else if (new Date(milestone.target_date) < new Date()) {
      return <AlertCircle className="h-6 w-6 text-red-600" />;
    } else {
      return <Circle className="h-6 w-6 text-gray-400" />;
    }
  };

  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      pre_closing: 'bg-purple-100 text-purple-800',
      day_1: 'bg-blue-100 text-blue-800',
      day_30: 'bg-green-100 text-green-800',
      day_100: 'bg-yellow-100 text-yellow-800',
      month_6: 'bg-indigo-100 text-indigo-800',
      month_12: 'bg-pink-100 text-pink-800',
      month_24: 'bg-orange-100 text-orange-800'
    };
    return colors[phase] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <Calendar className="h-6 w-6 mr-2 text-indigo-600" />
        Integration Timeline
      </h2>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Milestones */}
        <div className="space-y-8">
          {milestones.map((milestone, index) => (
            <div key={milestone.id} className="relative flex items-start">
              {/* Icon */}
              <div className="absolute left-5 -ml-3 bg-white">
                {getMilestoneIcon(milestone)}
              </div>

              {/* Content */}
              <div className="ml-16 flex-1">
                <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{milestone.name}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPhaseColor(milestone.phase)}`}>
                      {milestone.phase.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                    <div>
                      <p className="text-xs text-gray-500">Target Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(milestone.target_date).toLocaleDateString()}
                      </p>
                    </div>

                    {milestone.actual_completion_date && (
                      <div>
                        <p className="text-xs text-gray-500">Completed</p>
                        <p className="text-sm font-medium text-green-600">
                          {new Date(milestone.actual_completion_date).toLocaleDateString()}
                        </p>
                      </div>
                    )}

                    <div>
                      <p className="text-xs text-gray-500">Progress</p>
                      <p className="text-sm font-medium text-gray-900">{milestone.completion_percentage}%</p>
                    </div>

                    <div>
                      <p className="text-xs text-gray-500">Deliverables</p>
                      <p className="text-sm font-medium text-gray-900">
                        {milestone.deliverables_completed}/{milestone.deliverables_total}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${milestone.is_completed ? 'bg-green-500' : 'bg-indigo-600'}`}
                        style={{ width: `${milestone.completion_percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
