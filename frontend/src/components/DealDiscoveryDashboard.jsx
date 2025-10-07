import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@clerk/clerk-react';

const DealDiscoveryDashboard = () => {
  const { getToken } = useAuth();
  const [activeTab, setActiveTab] = useState('opportunities');
  const [opportunities, setOpportunities] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    stage: '',
    priority: '',
    industry: '',
    revenueMin: '',
    revenueMax: ''
  });
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState('');

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      const config = { headers: { Authorization: `Bearer ${token}` } };

      if (activeTab === 'opportunities') {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/deal-discovery/opportunities`,
          config
        );
        setOpportunities(response.data);
      } else if (activeTab === 'companies') {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/deal-discovery/companies`,
          config
        );
        setCompanies(response.data);
      } else if (activeTab === 'ranked') {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/deal-discovery/opportunities/ranked?limit=25`,
          config
        );
        setOpportunities(response.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStageUpdate = async (opportunityId, newStage) => {
    try {
      const token = await getToken();
      await axios.patch(
        `${import.meta.env.VITE_API_URL}/api/deal-discovery/opportunities/${opportunityId}/stage`,
        newStage,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      fetchData();
    } catch (error) {
      console.error('Error updating stage:', error);
    }
  };

  const calculateScore = async (opportunityId) => {
    try {
      const token = await getToken();
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/deal-discovery/opportunities/${opportunityId}/score`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
      return response.data;
    } catch (error) {
      console.error('Error calculating score:', error);
    }
  };

  const getStageColor = (stage) => {
    const colors = {
      discovery: 'bg-gray-100 text-gray-800',
      initial_review: 'bg-blue-100 text-blue-800',
      due_diligence: 'bg-yellow-100 text-yellow-800',
      negotiation: 'bg-purple-100 text-purple-800',
      closing: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      on_hold: 'bg-gray-100 text-gray-600'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      1: 'text-red-600',
      2: 'text-orange-600',
      3: 'text-yellow-600',
      4: 'text-blue-600',
      5: 'text-gray-600'
    };
    return colors[priority] || 'text-gray-600';
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount * 1000000);
  };

  const OpportunityCard = ({ opportunity, isRanked = false }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{opportunity.title}</h3>
          <p className="text-sm text-gray-600 mt-1">
            {opportunity.company?.name || 'Company Name'}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-2xl ${getPriorityColor(opportunity.priority)}`}>
            {'★'.repeat(6 - opportunity.priority)}
          </span>
          {isRanked && opportunity.overall_score && (
            <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold">
              {opportunity.overall_score.toFixed(1)}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">Stage</p>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStageColor(opportunity.stage)}`}>
            {opportunity.stage.replace('_', ' ')}
          </span>
        </div>
        <div>
          <p className="text-xs text-gray-500">Valuation</p>
          <p className="text-sm font-medium text-gray-900">
            {formatCurrency(opportunity.estimated_valuation)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Target IRR</p>
          <p className="text-sm font-medium text-gray-900">
            {opportunity.target_irr ? `${(opportunity.target_irr * 100).toFixed(1)}%` : 'N/A'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Source</p>
          <p className="text-sm font-medium text-gray-900">
            {opportunity.source?.replace('_', ' ') || 'N/A'}
          </p>
        </div>
      </div>

      {opportunity.overall_score && (
        <div className="border-t pt-4">
          <p className="text-xs text-gray-500 mb-2">Score Breakdown</p>
          <div className="grid grid-cols-4 gap-2">
            <div className="text-center">
              <div className="text-xs text-gray-500">Financial</div>
              <div className="text-sm font-semibold">{opportunity.financial_score?.toFixed(0) || 'N/A'}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Strategic</div>
              <div className="text-sm font-semibold">{opportunity.strategic_fit_score?.toFixed(0) || 'N/A'}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Risk</div>
              <div className="text-sm font-semibold">{opportunity.risk_score?.toFixed(0) || 'N/A'}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Overall</div>
              <div className="text-sm font-semibold text-blue-600">{opportunity.overall_score?.toFixed(0) || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => setSelectedOpportunity(opportunity)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View Details →
        </button>
        <div className="flex space-x-2">
          {!opportunity.overall_score && (
            <button
              onClick={() => calculateScore(opportunity.id)}
              className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded hover:bg-gray-200"
            >
              Calculate Score
            </button>
          )}
          <select
            value={opportunity.stage}
            onChange={(e) => handleStageUpdate(opportunity.id, e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="discovery">Discovery</option>
            <option value="initial_review">Initial Review</option>
            <option value="due_diligence">Due Diligence</option>
            <option value="negotiation">Negotiation</option>
            <option value="closing">Closing</option>
            <option value="completed">Completed</option>
            <option value="rejected">Rejected</option>
            <option value="on_hold">On Hold</option>
          </select>
        </div>
      </div>
    </div>
  );

  const CompanyCard = ({ company }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
          <p className="text-sm text-gray-600 mt-1">
            {company.industry?.replace('_', ' ') || 'Industry'} • {company.country || 'Country'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">Revenue Range</p>
          <p className="text-sm font-medium text-gray-900">
            {company.revenue_range_min && company.revenue_range_max
              ? `£${company.revenue_range_min}M - £${company.revenue_range_max}M`
              : 'N/A'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Employees</p>
          <p className="text-sm font-medium text-gray-900">
            {company.employee_count || 'N/A'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">EBITDA Margin</p>
          <p className="text-sm font-medium text-gray-900">
            {company.ebitda_margin ? `${(company.ebitda_margin * 100).toFixed(1)}%` : 'N/A'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Growth Rate</p>
          <p className="text-sm font-medium text-gray-900">
            {company.growth_rate ? `${(company.growth_rate * 100).toFixed(1)}%` : 'N/A'}
          </p>
        </div>
      </div>

      <div className="flex justify-between items-center mt-4 pt-4 border-t">
        <p className="text-xs text-gray-500">
          Founded: {company.year_founded || 'N/A'}
        </p>
        <button
          onClick={() => {
            setCreateType('opportunity');
            setShowCreateModal(true);
          }}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          Create Opportunity
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Deal Discovery & Sourcing</h1>
          <p className="mt-2 text-gray-600">
            Identify, evaluate, and track potential acquisition opportunities
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border-b mb-6">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {['opportunities', 'companies', 'ranked', 'screening'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'ranked' ? 'Top Ranked' : tab}
              </button>
            ))}
          </nav>
        </div>

        {activeTab === 'screening' && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Advanced Screening Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                <select
                  value={filters.industry}
                  onChange={(e) => setFilters({ ...filters, industry: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Industries</option>
                  <option value="technology">Technology</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="services">Services</option>
                  <option value="retail">Retail</option>
                  <option value="finance">Finance</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Revenue (£M)
                </label>
                <input
                  type="number"
                  value={filters.revenueMin}
                  onChange={(e) => setFilters({ ...filters, revenueMin: e.target.value })}
                  placeholder="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Revenue (£M)
                </label>
                <input
                  type="number"
                  value={filters.revenueMax}
                  onChange={(e) => setFilters({ ...filters, revenueMax: e.target.value })}
                  placeholder="50"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="mt-4 flex space-x-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Apply Filters
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                Find Distressed
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                Succession Opportunities
              </button>
            </div>
          </div>
        )}

        <div className="mb-4 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {loading ? 'Loading...' : `${opportunities.length || companies.length} results`}
          </div>
          <button
            onClick={() => {
              setCreateType(activeTab === 'companies' ? 'company' : 'opportunity');
              setShowCreateModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + Add {activeTab === 'companies' ? 'Company' : 'Opportunity'}
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeTab === 'opportunities' && opportunities.map((opp) => (
              <OpportunityCard key={opp.id} opportunity={opp} />
            ))}
            {activeTab === 'companies' && companies.map((company) => (
              <CompanyCard key={company.id} company={company} />
            ))}
            {activeTab === 'ranked' && opportunities.map((item) => (
              <OpportunityCard
                key={item.opportunity?.id || item.id}
                opportunity={item.opportunity || item}
                isRanked={true}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DealDiscoveryDashboard;