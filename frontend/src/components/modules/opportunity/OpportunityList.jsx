import React, { useState, useEffect } from 'react';
import { opportunityAPI, OPPORTUNITY_STAGE_LABELS, OPPORTUNITY_STATUSES } from '../../../utils/api';

const OpportunityList = ({ onEdit, onView, onDelete }) => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 10,
    total: 0
  });

  useEffect(() => {
    fetchOpportunities();
  }, [search, stageFilter, statusFilter, pagination.skip]);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const params = {
        skip: pagination.skip,
        limit: pagination.limit,
        ...(search && { search }),
        ...(stageFilter && { stage: stageFilter }),
        ...(statusFilter && { status: statusFilter })
      };
      
      const response = await opportunityAPI.getOpportunities(params);
      if (response.status) {
        setOpportunities(response.data.opportunities || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }));
      }
    } catch (err) {
      console.error('Failed to fetch opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (opportunity) => {
    if (!window.confirm(`Are you sure you want to delete "${opportunity.name}" (${opportunity.pot_id})?`)) return;
    
    try {
      const response = await opportunityAPI.deleteOpportunity(opportunity.id);

      if (response.status) {
        await fetchOpportunities();
      } else {
        alert('Failed to delete opportunity: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handleStageUpdate = async (opportunity, newStage) => {
    try {
      const response = await opportunityAPI.updateStage(opportunity.id, { 
        stage: newStage,
        notes: `Stage updated to ${OPPORTUNITY_STAGE_LABELS[newStage]} via quick action`
      });

      if (response.status) {
        await fetchOpportunities();
      } else {
        alert('Failed to update stage: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handleCloseOpportunity = async (opportunity, status) => {
    const notes = prompt(`Enter notes for closing ${opportunity.pot_id} as ${status}:`);
    if (notes === null) return; // User cancelled
    
    const closeData = { 
      status, 
      close_date: new Date().toISOString().split('T')[0],
      notes
    };

    if (status === 'Lost') {
      const reason = prompt('Enter reason for losing this opportunity:');
      if (reason) closeData.lost_reason = reason;

      const competitor = prompt('Enter competitor name (if applicable):');
      if (competitor) closeData.competitor_name = competitor;
    } else if (status === 'Dropped') {
      const reason = prompt('Enter reason for dropping this opportunity:');
      if (reason) closeData.drop_reason = reason;
    }
    
    try {
      const response = await opportunityAPI.closeOpportunity(opportunity.id, closeData);

      if (response.status) {
        await fetchOpportunities();
      } else {
        alert('Failed to close opportunity: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
  };

  const getStageColor = (stage) => {
    const colors = {
      'L1_Prospect': 'bg-gray-100 text-gray-800',
      'L1_Qualification': 'bg-blue-100 text-blue-800',
      'L2_Need_Analysis': 'bg-indigo-100 text-indigo-800',
      'L3_Proposal': 'bg-purple-100 text-purple-800',
      'L4_Negotiation': 'bg-pink-100 text-pink-800',
      'L5_Won': 'bg-green-100 text-green-800',
      'L6_Lost': 'bg-red-100 text-red-800',
      'L7_Dropped': 'bg-gray-100 text-gray-800'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status) => {
    const colors = {
      'Open': 'bg-green-100 text-green-800',
      'Won': 'bg-green-200 text-green-900',
      'Lost': 'bg-red-100 text-red-800',
      'Dropped': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const opportunityStages = Object.keys(OPPORTUNITY_STAGE_LABELS);
  const opportunityStatuses = Object.values(OPPORTUNITY_STATUSES);
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search opportunities by name, POT ID, company, or contact..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPagination(prev => ({ ...prev, skip: 0 }));
          }}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select
          value={stageFilter}
          onChange={(e) => {
            setStageFilter(e.target.value);
            setPagination(prev => ({ ...prev, skip: 0 }));
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Stages</option>
          {opportunityStages.map(stage => (
            <option key={stage} value={stage}>{OPPORTUNITY_STAGE_LABELS[stage]}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPagination(prev => ({ ...prev, skip: 0 }));
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Statuses</option>
          {opportunityStatuses.map(status => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </div>

      {/*  Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Opportunity Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company & Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stage & Progress
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Value & Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stage Tasks
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center">
                  <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  </div>
                </td>
              </tr>
            ) : opportunities.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                  {search || stageFilter || statusFilter ? 'No opportunities found matching your criteria' : 'No opportunities found'}
                </td>
              </tr>
            ) : (
              opportunities.map((opportunity) => (
                <tr key={opportunity.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{opportunity.name}</div>
                      <div className="text-sm text-blue-600 font-mono">{opportunity.pot_id}</div>
                      {opportunity.close_date && (
                        <div className="text-sm text-gray-500">
                          Target Close: {new Date(opportunity.close_date).toLocaleDateString()}
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-1">
                        Score: {opportunity.scoring}/100 | Prob: {opportunity.probability}%
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{opportunity.company_name}</div>
                      <div className="text-sm text-gray-500">{opportunity.contact_name}</div>
                      {opportunity.contact_email && (
                        <div className="text-xs text-gray-400">{opportunity.contact_email}</div>
                      )}
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(opportunity.stage)}`}>
                        {opportunity.stage_display_name}
                      </span>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${opportunity.stage_percentage}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {opportunity.stage_percentage}% Complete
                      </div>
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(opportunity.amount)}
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(opportunity.status)}`}>
                        {opportunity.status}
                      </span>
                      {opportunity.costing && (
                        <div className="text-xs text-gray-500">
                          Cost: {formatCurrency(opportunity.costing)}
                        </div>
                      )}
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      {/* L1 - Qualification Tasks */}
                      {opportunity.stage === 'L1_Qualification' && (
                        <div className="space-y-1">
                          <div className={`text-xs ${opportunity.requirement_gathering_notes ? 'text-green-600' : 'text-gray-400'}`}>
                            📝 Requirements: {opportunity.requirement_gathering_notes ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.go_no_go_status === 'Go' ? 'text-green-600' : opportunity.go_no_go_status === 'No_Go' ? 'text-red-600' : 'text-gray-400'}`}>
                            🎯 Go/No-Go: {opportunity.go_no_go_status?.replace('_', ' ') || 'Pending'}
                          </div>
                          <div className={`text-xs ${opportunity.qualification_status ? 'text-green-600' : 'text-gray-400'}`}>
                            ✅ Qualified: {opportunity.qualification_status?.replace('_', ' ') || 'Pending'}
                          </div>
                        </div>
                      )}

                      {/* L2 - Demo Tasks */}
                      {opportunity.stage === 'L2_Need_Analysis' && (
                        <div className="space-y-1">
                          <div className={`text-xs ${opportunity.demo_completed ? 'text-green-600' : 'text-gray-400'}`}>
                            🎥 Demo: {opportunity.demo_completed ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.qualification_meeting_completed ? 'text-green-600' : 'text-gray-400'}`}>
                            🤝 Meeting: {opportunity.qualification_meeting_completed ? '✓' : '○'}
                          </div>
                          {opportunity.demo_date && (
                            <div className="text-xs text-gray-500">
                              📅 {new Date(opportunity.demo_date).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      )}

                      {/* L3 - Proposal Tasks */}
                      {opportunity.stage === 'L3_Proposal' && (
                        <div className="space-y-1">
                          <div className={`text-xs ${opportunity.quotation_created ? 'text-green-600' : 'text-gray-400'}`}>
                            💰 Quotation: {opportunity.quotation_created ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.proposal_prepared ? 'text-green-600' : 'text-gray-400'}`}>
                            📄 Proposal: {opportunity.proposal_prepared ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.proposal_submitted ? 'text-green-600' : 'text-gray-400'}`}>
                            📤 Submitted: {opportunity.proposal_submitted ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.poc_completed ? 'text-green-600' : 'text-gray-400'}`}>
                            🧪 POC: {opportunity.poc_completed ? '✓' : '○'}
                          </div>
                          {opportunity.quotation_status && (
                            <div className="text-xs text-gray-500">
                              Status: {opportunity.quotation_status.replace('_', ' ')}
                            </div>
                          )}
                        </div>
                      )}

                      {/* L4 - Negotiation Tasks */}
                      {opportunity.stage === 'L4_Negotiation' && (
                        <div className="space-y-1">
                          <div className={`text-xs ${opportunity.customer_discussion_notes ? 'text-green-600' : 'text-gray-400'}`}>
                            💬 Discussions: {opportunity.customer_discussion_notes ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.proposal_updated ? 'text-green-600' : 'text-gray-400'}`}>
                            🔄 Updated Proposal: {opportunity.proposal_updated ? '✓' : '○'}
                          </div>
                          <div className="text-xs text-gray-500">
                            🔄 Rounds: {opportunity.negotiation_rounds || 0}
                          </div>
                          {opportunity.commercial_approval_required && (
                            <div className={`text-xs ${opportunity.commercial_approval_status === 'Approved' ? 'text-green-600' : 'text-yellow-600'}`}>
                              📋 Approval: {opportunity.commercial_approval_status || 'Pending'}
                            </div>
                          )}
                        </div>
                      )}

                      {/* L5 - Won Tasks */}
                      {opportunity.stage === 'L5_Won' && (
                        <div className="space-y-1">
                          <div className={`text-xs ${opportunity.kickoff_meeting_scheduled ? 'text-green-600' : 'text-gray-400'}`}>
                            🚀 Kickoff: {opportunity.kickoff_meeting_scheduled ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.loi_received ? 'text-green-600' : 'text-gray-400'}`}>
                            📋 LOI: {opportunity.loi_received ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.order_verified ? 'text-green-600' : 'text-gray-400'}`}>
                            ✅ Verified: {opportunity.order_verified ? '✓' : '○'}
                          </div>
                          <div className={`text-xs ${opportunity.handoff_to_delivery ? 'text-green-600' : 'text-gray-400'}`}>
                            🎯 Handoff: {opportunity.handoff_to_delivery ? '✓' : '○'}
                          </div>
                        </div>
                      )}

                      {/* Default for other stages */}
                      {!['L1_Qualification', 'L2_Need_Analysis', 'L3_Proposal', 'L4_Negotiation', 'L5_Won'].includes(opportunity.stage) && (
                        <div className="text-xs text-gray-400">
                          {opportunity.stage_display_name}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex flex-col space-y-2">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onView(opportunity)}
                          className="text-indigo-600 hover:text-indigo-900 text-xs"
                        >
                          View
                        </button>
                        <button
                          onClick={() => onEdit(opportunity)}
                          className="text-blue-600 hover:text-blue-900 text-xs"
                        >
                          Edit
                        </button>
                      </div>
                      
                      {opportunity.status === 'Open' && (
                        <div className="flex flex-col space-y-1">
                          <select
                            value={opportunity.stage}
                            onChange={(e) => handleStageUpdate(opportunity, e.target.value)}
                            className="text-xs px-2 py-1 border border-gray-300 rounded"
                          >
                            {opportunityStages.map(stage => (
                              <option key={stage} value={stage}>
                                {OPPORTUNITY_STAGE_LABELS[stage]}
                              </option>
                            ))}
                          </select>
                          
                          <div className="flex space-x-1">
                            <button
                              onClick={() => handleCloseOpportunity(opportunity, 'Won')}
                              className="text-xs text-green-600 hover:text-green-900 px-1 py-1 border border-green-300 rounded"
                            >
                              Win
                            </button>
                            <button
                              onClick={() => handleCloseOpportunity(opportunity, 'Lost')}
                              className="text-xs text-red-600 hover:text-red-900 px-1 py-1 border border-red-300 rounded"
                            >
                              Lose
                            </button>
                            <button
                              onClick={() => handleCloseOpportunity(opportunity, 'Dropped')}
                              className="text-xs text-gray-600 hover:text-gray-900 px-1 py-1 border border-gray-300 rounded"
                            >
                              Drop
                            </button>
                          </div>
                        </div>
                      )}
                      
                      <button
                        onClick={() => handleDelete(opportunity)}
                        className="text-red-600 hover:text-red-900 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/*  Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(Math.max(0, pagination.skip - pagination.limit))}
                disabled={pagination.skip === 0}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange(pagination.skip + pagination.limit)}
                disabled={pagination.skip + pagination.limit >= pagination.total}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{pagination.skip + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(pagination.skip + pagination.limit, pagination.total)}
                  </span>{' '}
                  of <span className="font-medium">{pagination.total}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => handlePageChange(Math.max(0, pagination.skip - pagination.limit))}
                    disabled={pagination.skip === 0}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                    {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => handlePageChange(pagination.skip + pagination.limit)}
                    disabled={pagination.skip + pagination.limit >= pagination.total}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpportunityList;