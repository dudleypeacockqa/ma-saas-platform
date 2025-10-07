import React, { useState } from 'react';
import { useOrganization } from '@clerk/clerk-react';
import {
  Calendar,
  Users,
  DollarSign,
  Target,
  Plus,
  X,
  Check,
  AlertCircle
} from 'lucide-react';

interface IntegrationProjectFormData {
  deal_id: string;
  project_name: string;
  description: string;
  integration_approach: string;
  start_date: string;
  target_completion_date: string;
  integration_lead_id: string;
  executive_sponsor_id: string;
  core_team_member_ids: string[];
  integration_budget: number | null;
  target_synergies: number | null;
  employee_retention_target: number;
}

interface Deal {
  id: string;
  deal_name: string;
  company_name: string;
  stage: string;
}

export default function IntegrationPlanner() {
  const { organization } = useOrganization();
  const [step, setStep] = useState(1);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<IntegrationProjectFormData>({
    deal_id: '',
    project_name: '',
    description: '',
    integration_approach: 'symbiosis',
    start_date: '',
    target_completion_date: '',
    integration_lead_id: '',
    executive_sponsor_id: '',
    core_team_member_ids: [],
    integration_budget: null,
    target_synergies: null,
    employee_retention_target: 90
  });

  React.useEffect(() => {
    if (organization?.id) {
      fetchClosedDeals();
    }
  }, [organization?.id]);

  const fetchClosedDeals = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/deals?stage=closed_won`,
        {
          headers: {
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      }
    } catch (err) {
      console.error('Error fetching deals:', err);
    }
  };

  const handleInputChange = (field: keyof IntegrationProjectFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/integration/projects`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await organization?.getToken()}`,
            'X-Organization-ID': organization?.id || ''
          },
          body: JSON.stringify(formData)
        }
      );

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          window.location.href = '/integration/dashboard';
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to create integration plan');
      }
    } catch (err) {
      setError('An error occurred while creating the plan');
    } finally {
      setLoading(false);
    }
  };

  const integrationApproaches = [
    {
      value: 'absorption',
      label: 'Absorption',
      description: 'Fully integrate target into acquirer operations'
    },
    {
      value: 'preservation',
      label: 'Preservation',
      description: 'Keep target operating independently'
    },
    {
      value: 'symbiosis',
      label: 'Symbiosis',
      description: 'Blend best practices from both organizations'
    },
    {
      value: 'best_of_breed',
      label: 'Best of Breed',
      description: 'Select best processes and systems from each'
    }
  ];

  const selectedDeal = deals.find(d => d.id === formData.deal_id);

  if (success) {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <Check className="h-12 w-12 text-green-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-green-900 mb-2">
            Integration Plan Created Successfully!
          </h3>
          <p className="text-green-700">
            Redirecting to dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: 'Select Deal' },
            { num: 2, label: 'Approach' },
            { num: 3, label: 'Timeline' },
            { num: 4, label: 'Team & Budget' }
          ].map((stepItem, idx) => (
            <React.Fragment key={stepItem.num}>
              <div className="flex flex-col items-center">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
                    ${step >= stepItem.num
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                    }
                  `}
                >
                  {stepItem.num}
                </div>
                <span className="text-xs mt-2 text-gray-600">{stepItem.label}</span>
              </div>
              {idx < 3 && (
                <div
                  className={`flex-1 h-1 mx-4 ${
                    step > stepItem.num ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mr-3 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-red-900">Error</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Step 1: Select Deal */}
      {step === 1 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Select Closed Deal</h2>

          {deals.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No closed deals available for integration planning.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {deals.map(deal => (
                <label
                  key={deal.id}
                  className={`
                    block p-4 border-2 rounded-lg cursor-pointer transition-colors
                    ${formData.deal_id === deal.id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="deal"
                    value={deal.id}
                    checked={formData.deal_id === deal.id}
                    onChange={(e) => {
                      handleInputChange('deal_id', e.target.value);
                      handleInputChange('plan_name', `${deal.company_name} Integration Plan`);
                    }}
                    className="sr-only"
                  />
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{deal.deal_name}</p>
                      <p className="text-sm text-gray-500">{deal.company_name}</p>
                    </div>
                    {formData.deal_id === deal.id && (
                      <Check className="h-5 w-5 text-indigo-600" />
                    )}
                  </div>
                </label>
              ))}
            </div>
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={() => setStep(2)}
              disabled={!formData.deal_id}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Integration Approach */}
      {step === 2 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Integration Approach</h2>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Plan Name
            </label>
            <input
              type="text"
              value={formData.plan_name}
              onChange={(e) => handleInputChange('plan_name', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Describe the integration objectives and key considerations..."
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Integration Approach
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {integrationApproaches.map(approach => (
                <label
                  key={approach.value}
                  className={`
                    block p-4 border-2 rounded-lg cursor-pointer transition-colors
                    ${formData.integration_approach === approach.value
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="approach"
                    value={approach.value}
                    checked={formData.integration_approach === approach.value}
                    onChange={(e) => handleInputChange('integration_approach', e.target.value)}
                    className="sr-only"
                  />
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-gray-900">{approach.label}</p>
                      {formData.integration_approach === approach.value && (
                        <Check className="h-5 w-5 text-indigo-600" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{approach.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => setStep(1)}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Timeline */}
      {step === 3 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Integration Timeline</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline h-4 w-4 mr-2" />
                Start Date (Day 1)
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => handleInputChange('start_date', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline h-4 w-4 mr-2" />
                Target Completion (24 months)
              </label>
              <input
                type="date"
                value={formData.target_completion_date}
                onChange={(e) => handleInputChange('target_completion_date', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>Key Milestones:</strong> The system will automatically create standard integration milestones including Day 1, Day 30, Day 100, 6-month, 12-month, and 24-month checkpoints.
            </p>
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => setStep(2)}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={() => setStep(4)}
              disabled={!formData.start_date || !formData.target_completion_date}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Team & Budget */}
      {step === 4 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-6">Team & Budget</h2>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <DollarSign className="inline h-4 w-4 mr-2" />
                  Total Budget
                </label>
                <input
                  type="number"
                  value={formData.total_budget || ''}
                  onChange={(e) => handleInputChange('total_budget', e.target.value ? parseFloat(e.target.value) : null)}
                  placeholder="0"
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Target className="inline h-4 w-4 mr-2" />
                  Total Synergy Target
                </label>
                <input
                  type="number"
                  value={formData.total_synergy_target || ''}
                  onChange={(e) => handleInputChange('total_synergy_target', e.target.value ? parseFloat(e.target.value) : null)}
                  placeholder="0"
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline h-4 w-4 mr-2" />
                Employee Retention Target (%)
              </label>
              <input
                type="number"
                value={formData.employee_retention_target}
                onChange={(e) => handleInputChange('employee_retention_target', parseFloat(e.target.value))}
                min="0"
                max="100"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> Integration lead, executive sponsor, and team members can be assigned after plan creation from the dashboard.
              </p>
            </div>
          </div>

          <div className="mt-8 flex justify-between">
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Plan...' : 'Create Integration Plan'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
