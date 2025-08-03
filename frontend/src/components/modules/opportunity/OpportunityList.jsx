import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

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
      const params = new URLSearchParams({
        skip: pagination.skip,
        limit: pagination.limit,
        ...(search && { search }),
        ...(stageFilter && { stage: stageFilter }),
        ...(statusFilter && { status: statusFilter })
      });
      
      const response = await apiRequest(`/api/opportunities?${params}`);
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

  const handleDelete = async (opportunityId, opportunityName) => {
    if (!window.confirm(`Are you sure you want to delete "${opportunityName}"?`)) return;
    
    try {
      const response = await apiRequest(`/api/opportunities/${opportunityId}`, {
        method: 'DELETE'
      });

      if (response.status) {
        await fetchOpportunities();
      } else {
        alert('Failed to delete opportunity: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handleStageUpdate = async (opportunityId, stage) => {
    try {
      const response = await apiRequest(`/api/opportunities/${opportunityId}/stage`, {
        method: 'PATCH',
        body: JSON.stringify({ stage })
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

  const handleCloseOpportunity = async (opportunityId, status) => {
    const notes = prompt(`Enter notes for closing as ${status}:`);
    if (notes === null) return; // User cancelled
    
    try {
      const response = await apiRequest(`/api/opportunities/${opportunityId}/close`, {
        method: 'PATCH',
        body: JSON.stringify({ 
          status, 
          close_date: new Date().toISOString().split('T')[0],
          notes 
        })
      });

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
      'L1': 'bg-blue-100 text-blue-800',
      'L2': 'bg-indigo-100 text-indigo-800',
      'L3': 'bg-purple-100 text-purple-800',
      'L4': 'bg-pink-100 text-pink-800',
      'L5': 'bg-red-100 text-red-800',
      'L6': 'bg-orange-100 text-orange-800',
      'L7': 'bg-yellow-100 text-yellow-800'
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

  const opportunityStages = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'];
  const opportunityStatuses = ['Open', 'Won', 'Lost', 'Dropped'];
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search opportunities by name, company, or contact..."
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
            <option key={stage} value={stage}>{stage}</option>
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

      {/* Table */}
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
                Amount & Stage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status & Probability
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center">
                  <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  </div>
                </td>
              </tr>
            ) : opportunities.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                  {search || stageFilter || statusFilter ? 'No opportunities found matching your criteria' : 'No opportunities found'}
                </td>
              </tr>
            ) : (
              opportunities.map((opportunity) => (
                <tr key={opportunity.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{opportunity.name}</div>
                      {opportunity.close_date && (
                        <div className="text-sm text-gray-500">
                          Close: {new Date(opportunity.close_date).toLocaleDateString()}
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-1">
                        Score: {opportunity.scoring}/100
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
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(opportunity.amount)}
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(opportunity.stage)}`}>
                        {opportunity.stage}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(opportunity.status)}`}>
                        {opportunity.status}
                      </span>
                      <div className="text-xs text-gray-500">
                        {opportunity.probability}% probability
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex flex-col space-y-2">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onView(opportunity)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          View
                        </button>
                        <button
                          onClick={() => onEdit(opportunity)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                      </div>
                      {opportunity.status === 'Open' && (
                        <div className="flex flex-col space-y-1">
                          <select
                            value={opportunity.stage}
                            onChange={(e) => handleStageUpdate(opportunity.id, e.target.value)}
                            className="text-xs px-2 py-1 border border-gray-300 rounded"
                          >
                            {opportunityStages.map(stage => (
                              <option key={stage} value={stage}>{stage}</option>
                            ))}
                          </select>
                          <div className="flex space-x-1">
                            <button
                              onClick={() => handleCloseOpportunity(opportunity.id, 'Won')}
                              className="text-xs text-green-600 hover:text-green-900"
                            >
                              Win
                            </button>
                            <button
                              onClick={() => handleCloseOpportunity(opportunity.id, 'Lost')}
                              className="text-xs text-red-600 hover:text-red-900"
                            >
                              Lose
                            </button>
                          </div>
                        </div>
                      )}
                      <button
                        onClick={() => handleDelete(opportunity.id, opportunity.name)}
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

        {/* Pagination */}
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