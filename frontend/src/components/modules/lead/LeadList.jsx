import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';
import ConversionButton from './ConversionButton';
import AdminReviewPanel from './AdminReviewPanel';

const LeadList = ({ leads, loading, onEdit, onView, onDelete, onRefresh }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [reviewStatusFilter, setReviewStatusFilter] = useState('');
  const [filteredLeads, setFilteredLeads] = useState([]);

  useEffect(() => {
    // Get current user info (this would come from your auth context)
    const token = localStorage.getItem('token');
    if (token) {
      // Decode token or fetch user info
      setCurrentUser({ 
        id: 1, 
        name: 'Current User', 
        roles: ['admin'] // This should come from actual auth
      });
    }
  }, []);

  useEffect(() => {
    // Filter leads based on search and filters
    let filtered = leads || [];

    if (search) {
      const searchTerm = search.toLowerCase();
      filtered = filtered.filter(lead =>
        lead.project_title?.toLowerCase().includes(searchTerm) ||
        lead.company_name?.toLowerCase().includes(searchTerm) ||
        lead.tender_authority?.toLowerCase().includes(searchTerm)
      );
    }

    if (statusFilter) {
      filtered = filtered.filter(lead => lead.status === statusFilter);
    }

    if (reviewStatusFilter) {
      filtered = filtered.filter(lead => lead.review_status === reviewStatusFilter);
    }

    setFilteredLeads(filtered);
  }, [leads, search, statusFilter, reviewStatusFilter]);

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStatusColor = (status) => {
    const colors = {
      'New': 'bg-blue-100 text-blue-800',
      'Contacted': 'bg-yellow-100 text-yellow-800',
      'Qualified': 'bg-green-100 text-green-800',
      'Unqualified': 'bg-red-100 text-red-800',
      'Converted': 'bg-purple-100 text-purple-800',
      'Rejected': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getReviewStatusColor = (status) => {
    const colors = {
      'Pending': 'bg-yellow-100 text-yellow-800',
      'Approved': 'bg-green-100 text-green-800',
      'Rejected': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const isAdmin = currentUser?.roles?.includes('admin') || currentUser?.roles?.includes('reviewer');

  return (
    <div className="space-y-4">
      {/* Header with Admin Panel Button */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Lead List</h3>
          <p className="text-sm text-gray-600">
            Showing {filteredLeads.length} of {leads?.length || 0} leads
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowAdminPanel(true)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Admin Review Panel</span>
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Search leads by title, company, or authority..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Statuses</option>
          <option value="New">New</option>
          <option value="Contacted">Contacted</option>
          <option value="Qualified">Qualified</option>
          <option value="Unqualified">Unqualified</option>
          <option value="Converted">Converted</option>
          <option value="Rejected">Rejected</option>
        </select>

        <select
          value={reviewStatusFilter}
          onChange={(e) => setReviewStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Review Status</option>
          <option value="Pending">Pending Review</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>

        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Enhanced Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lead Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company & Authority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue & Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Conversion Status
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
            ) : filteredLeads.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                  {search || statusFilter || reviewStatusFilter ? 'No leads found matching your criteria' : 'No leads found'}
                </td>
              </tr>
            ) : (
              filteredLeads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{lead.project_title}</div>
                      <div className="text-sm text-gray-500">
                        Source: {lead.lead_source} | Type: {lead.lead_sub_type}
                      </div>
                      <div className="text-sm text-gray-500">
                        {lead.tender_sub_type}
                      </div>
                      {lead.convert_to_opportunity_date && (
                        <div className="text-xs text-blue-600">
                          Target: {new Date(lead.convert_to_opportunity_date).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{lead.company_name}</div>
                      <div className="text-sm text-gray-500">{lead.end_customer_name}</div>
                      {lead.tender_authority && (
                        <div className="text-xs text-gray-400">{lead.tender_authority}</div>
                      )}
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(lead.expected_revenue)}
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(lead.status)}`}>
                        {lead.status}
                      </span>
                      {lead.priority && (
                        <div className={`text-xs inline-flex px-2 py-1 rounded-full ${
                          lead.priority === 'High' ? 'bg-red-100 text-red-800' :
                          lead.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {lead.priority}
                        </div>
                      )}
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      {/* Conversion Status */}
                      {lead.converted ? (
                        <div className="space-y-1">
                          <div className="text-xs text-green-600 font-medium">✓ Converted</div>
                          {lead.converted_to_opportunity_id && (
                            <div className="text-xs text-gray-500">
                              Opp ID: #{lead.converted_to_opportunity_id}
                            </div>
                          )}
                          {lead.conversion_date && (
                            <div className="text-xs text-gray-500">
                              {new Date(lead.conversion_date).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      ) : lead.status === 'Qualified' ? (
                        <div className="space-y-1">
                          {/* Review Status */}
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getReviewStatusColor(lead.review_status)}`}>
                            {lead.review_status === 'Pending' ? 'Pending Review' : lead.review_status}
                          </span>
                          
                          {/* Conversion Request Status */}
                          {lead.conversion_requested && (
                            <div className="text-xs text-blue-600">
                              ⏳ Conversion Requested
                            </div>
                          )}
                          
                          {/* Can Convert Status */}
                          {lead.can_convert_to_opportunity && (
                            <div className="text-xs text-green-600">
                              ✅ Ready to Convert
                            </div>
                          )}
                          
                          {/* Needs Review */}
                          {lead.needs_admin_review && (
                            <div className="text-xs text-orange-600">
                              ⚠️ Needs Admin Review
                            </div>
                          )}

                          {/* Review Info */}
                          {lead.reviewed && lead.reviewer_name && (
                            <div className="text-xs text-gray-500">
                              By: {lead.reviewer_name}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-500">Not qualified yet</div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex flex-col space-y-2">
                      {/* Regular Actions */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onView(lead)}
                          className="text-indigo-600 hover:text-indigo-900 text-sm"
                        >
                          View
                        </button>
                        <button
                          onClick={() => onEdit(lead)}
                          className="text-blue-600 hover:text-blue-900 text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => onDelete(lead)}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Delete
                        </button>
                      </div>

                      {/* Conversion Button */}
                      <ConversionButton
                        lead={lead}
                        currentUser={currentUser}
                        onUpdate={onRefresh}
                      />
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Conversion Workflow Legend</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>✅ Ready to Convert - Approved by admin</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span>⏳ Conversion Requested - Waiting for review</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
            <span>⚠️ Needs Admin Review - Admin action required</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>✓ Converted - Successfully converted to opportunity</span>
          </div>
        </div>
      </div>

      {/* Admin Review Panel */}
      {showAdminPanel && (
        <AdminReviewPanel
          onClose={() => {
            setShowAdminPanel(false);
            onRefresh(); // Refresh leads after admin actions
          }}
        />
      )}
    </div>
  );
};

export default LeadList;