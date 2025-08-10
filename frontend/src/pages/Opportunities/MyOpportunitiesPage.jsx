import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';

const MyOpportunitiesPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    stage: '',
    status: '',
    search: ''
  });
  const { user } = useAuth();

  const stageOptions = [
    { value: '', label: 'All Stages' },
    { value: 'L1_Prospect', label: 'L1 Prospect' },
    { value: 'L2_Need_Analysis', label: 'L2 Need Analysis' },
    { value: 'L3_Proposal', label: 'L3 Proposal' },
    { value: 'Win', label: 'Win' },
    { value: 'Loss', label: 'Loss' }
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'Open', label: 'Open' },
    { value: 'Won', label: 'Won' },
    { value: 'Lost', label: 'Lost' }
  ];

  const opportunityColumns = [
    {
      key: 'pot_id',
      label: 'POT ID',
      render: (opportunity) => (
        <div className="font-medium text-blue-600">{opportunity.pot_id}</div>
      )
    },
    {
      key: 'name',
      label: 'Opportunity',
      sortable: true,
      render: (opportunity) => (
        <div>
          <div className="font-medium text-gray-900">{opportunity.name}</div>
          <div className="text-sm text-gray-500">{opportunity.company_name}</div>
        </div>
      )
    },
    {
      key: 'current_stage',
      label: 'Current Stage',
      render: (opportunity) => {
        const stageColors = {
          'L1_Prospect': 'bg-blue-100 text-blue-800',
          'L2_Need_Analysis': 'bg-yellow-100 text-yellow-800',
          'L3_Proposal': 'bg-orange-100 text-orange-800',
          'Win': 'bg-green-100 text-green-800',
          'Loss': 'bg-red-100 text-red-800'
        };
        const stageLabels = {
          'L1_Prospect': 'L1 Prospect',
          'L2_Need_Analysis': 'L2 Need Analysis',
          'L3_Proposal': 'L3 Proposal',
          'Win': 'Win',
          'Loss': 'Loss'
        };
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${stageColors[opportunity.current_stage] || 'bg-gray-100 text-gray-800'}`}>
            {stageLabels[opportunity.current_stage] || opportunity.current_stage}
          </span>
        );
      }
    },
    {
      key: 'amount',
      label: 'Value',
      render: (opportunity) => (
        <div className="text-right font-medium">
          ₹{Number(opportunity.amount || 0).toLocaleString()}
        </div>
      )
    },
    {
      key: 'probability',
      label: 'Win Probability',
      render: (opportunity) => (
        <div className="text-center">
          <div className="font-medium">{opportunity.probability}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
            <div 
              className="bg-green-600 h-2 rounded-full" 
              style={{ width: `${opportunity.probability}%` }}
            ></div>
          </div>
        </div>
      )
    },
    {
      key: 'close_date',
      label: 'Expected Close',
      render: (opportunity) => 
        opportunity.close_date ? new Date(opportunity.close_date).toLocaleDateString() : '-'
    },
    {
      key: 'quotations_count',
      label: 'Quotations',
      render: (opportunity) => (
        <div className="text-center">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
            {opportunity.quotations_count || 0}
          </span>
        </div>
      )
    }
  ];

  useEffect(() => {
    fetchMyOpportunities();
  }, [filters, user]);

  const fetchMyOpportunities = async () => {
    try {
      setLoading(true);
      // Filter opportunities converted by current user
      const response = await apiMethods.opportunities.getOpportunities({
        ...filters,
        user_filter: user?.id
      });
      if (response.data?.data?.opportunities) {
        setOpportunities(response.data.data.opportunities);
      }
    } catch (error) {
      console.error('Error fetching my opportunities:', error);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStage = async (opportunityId, newStage) => {
    try {
      console.log(`Updating opportunity ${opportunityId} to stage ${newStage}`);
      // Call API to update stage
      fetchMyOpportunities(); // Refresh the list
    } catch (error) {
      console.error('Error updating opportunity stage:', error);
    }
  };

  const handleCreateQuotation = (opportunityId) => {
    console.log(`Creating quotation for opportunity ${opportunityId}`);
    // Navigate to quotation creation or show modal
  };

  const actions = [
    {
      label: 'View Details',
      onClick: (opportunity) => {
        console.log('Viewing opportunity:', opportunity.id);
      },
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Next Stage',
      onClick: (opportunity) => {
        const stageOrder = ['L1_Prospect', 'L2_Need_Analysis', 'L3_Proposal', 'Win'];
        const currentIndex = stageOrder.indexOf(opportunity.current_stage);
        if (currentIndex < stageOrder.length - 1) {
          const nextStage = stageOrder[currentIndex + 1];
          handleUpdateStage(opportunity.id, nextStage);
        }
      },
      className: 'text-green-600 hover:text-green-900',
      show: (opportunity) => 
        opportunity.status === 'Open' && 
        ['L1_Prospect', 'L2_Need_Analysis', 'L3_Proposal'].includes(opportunity.current_stage)
    },
    {
      label: 'Create Quote',
      onClick: (opportunity) => handleCreateQuotation(opportunity.id),
      className: 'text-purple-600 hover:text-purple-900',
      show: (opportunity) => 
        opportunity.current_stage === 'L3_Proposal' && 
        opportunity.status === 'Open'
    },
    {
      label: 'Mark Won',
      onClick: (opportunity) => handleUpdateStage(opportunity.id, 'Win'),
      className: 'text-green-600 hover:text-green-900',
      show: (opportunity) => opportunity.status === 'Open' && opportunity.current_stage === 'L3_Proposal'
    },
    {
      label: 'Mark Lost',
      onClick: (opportunity) => {
        const reason = prompt("Please provide reason for marking as lost:");
        if (reason) {
          handleUpdateStage(opportunity.id, 'Loss');
        }
      },
      className: 'text-red-600 hover:text-red-900',
      show: (opportunity) => opportunity.status === 'Open'
    }
  ];

  // Calculate stats
  const stats = {
    total: opportunities.length,
    open: opportunities.filter(o => o.status === 'Open').length,
    won: opportunities.filter(o => o.status === 'Won').length,
    lost: opportunities.filter(o => o.status === 'Lost').length,
    totalValue: opportunities.reduce((sum, o) => sum + (Number(o.amount) || 0), 0),
    avgProbability: opportunities.length > 0 
      ? Math.round(opportunities.reduce((sum, o) => sum + o.probability, 0) / opportunities.length) 
      : 0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Opportunities</h1>
        <div className="text-sm text-gray-600">
          Opportunities you converted from leads
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">My Total</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Open</p>
              <p className="text-2xl font-bold text-green-600">{stats.open}</p>
            </div>
            <div className="p-3 rounded-md bg-green-50">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Won</p>
              <p className="text-2xl font-bold text-blue-600">{stats.won}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Lost</p>
              <p className="text-2xl font-bold text-red-600">{stats.lost}</p>
            </div>
            <div className="p-3 rounded-md bg-red-50">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-purple-600">₹{(stats.totalValue / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Avg. Probability</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.avgProbability}%</p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search your opportunities..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stage
            </label>
            <select
              value={filters.stage}
              onChange={(e) => setFilters(prev => ({ ...prev, stage: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {stageOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Opportunities Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={opportunityColumns}
            data={opportunities}
            actions={actions}
            emptyMessage="You haven't created any opportunities yet. Convert qualified leads to create opportunities."
          />
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Update All Open Stages</h3>
                <p className="text-sm text-gray-500">Batch update multiple opportunities</p>
              </div>
            </div>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Generate Report</h3>
                <p className="text-sm text-gray-500">Download your opportunities report</p>
              </div>
            </div>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Schedule Follow-ups</h3>
                <p className="text-sm text-gray-500">Set reminders for key opportunities</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyOpportunitiesPage;