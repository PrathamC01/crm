import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const CompanyList = ({ onEdit, onView, onDelete }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    company_type: '',
    approval_stage: '',
    industry: '',
    is_high_revenue: ''
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  });

  useEffect(() => {
    fetchCompanies();
  }, [search, filters, pagination.skip]);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: pagination.skip,
        limit: pagination.limit,
        ...(search && { search }),
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      });
      
      const response = await apiRequest(`/api/companies?${params}`);
      if (response.status) {
        setCompanies(response.data.companies || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }));
      }
    } catch (err) {
      console.error('Failed to fetch companies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (company, action, reason = '') => {
    if (!window.confirm(`Are you sure you want to ${action.toLowerCase()} "${company.name}"?`)) return;
    
    try {
      const response = await apiRequest(`/api/companies/${company.id}/approve`, {
        method: 'POST',
        body: JSON.stringify({
          action: action,
          reason: reason || undefined
        })
      });

      if (response.status) {
        await fetchCompanies();
        alert(`Company ${action.toLowerCase()} successful`);
      } else {
        alert('Failed to process approval: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handleDelete = async (companyId, companyName) => {
    if (!window.confirm(`Are you sure you want to delete "${companyName}"? This action cannot be undone.`)) return;
    
    try {
      const response = await apiRequest(`/api/companies/${companyId}`, {
        method: 'DELETE'
      });

      if (response.status) {
        await fetchCompanies();
        alert('Company deleted successfully');
      } else {
        alert('Failed to delete company: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const getStatusBadge = (status, approvalStage) => {
    let bgColor, textColor, text;
    
    switch (status) {
      case 'ACTIVE':
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        text = 'Active';
        break;
      case 'INACTIVE':
        bgColor = 'bg-red-100';
        textColor = 'text-red-800';
        text = 'Inactive';
        break;
      case 'PENDING_APPROVAL':
        switch (approvalStage) {
          case 'DRAFT':
            bgColor = 'bg-gray-100';
            textColor = 'text-gray-800';
            text = 'Draft';
            break;
          case 'L1_PENDING':
            bgColor = 'bg-yellow-100';
            textColor = 'text-yellow-800';
            text = 'L1 Pending';
            break;
          case 'ADMIN_PENDING':
            bgColor = 'bg-blue-100';
            textColor = 'text-blue-800';
            text = 'Admin Pending';
            break;
          case 'REJECTED':
            bgColor = 'bg-red-100';
            textColor = 'text-red-800';
            text = 'Rejected';
            break;
          default:
            bgColor = 'bg-orange-100';
            textColor = 'text-orange-800';
            text = 'Pending';
        }
        break;
      default:
        bgColor = 'bg-gray-100';
        textColor = 'text-gray-800';
        text = status;
    }

    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${bgColor} ${textColor}`}>
        {text}
      </span>
    );
  };

  const getCompanyTypeBadge = (type) => {
    const typeMap = {
      'DOMESTIC_GST': { label: 'Domestic GST', color: 'bg-blue-100 text-blue-800' },
      'DOMESTIC_NONGST': { label: 'Domestic Non-GST', color: 'bg-purple-100 text-purple-800' },
      'NGO': { label: 'NGO', color: 'bg-green-100 text-green-800' },
      'OVERSEAS': { label: 'Overseas', color: 'bg-orange-100 text-orange-800' }
    };
    
    const typeInfo = typeMap[type] || { label: type, color: 'bg-gray-100 text-gray-800' };
    
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${typeInfo.color}`}>
        {typeInfo.label}
      </span>
    );
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search companies by name, industry, city, GST, or PAN..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPagination(prev => ({ ...prev, skip: 0 }));
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        {/* Advanced Filters */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="PENDING_APPROVAL">Pending Approval</option>
          </select>

          <select
            value={filters.company_type}
            onChange={(e) => handleFilterChange('company_type', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="DOMESTIC_GST">Domestic GST</option>
            <option value="DOMESTIC_NONGST">Domestic Non-GST</option>
            <option value="NGO">NGO</option>
            <option value="OVERSEAS">Overseas</option>
          </select>

          <select
            value={filters.approval_stage}
            onChange={(e) => handleFilterChange('approval_stage', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Stages</option>
            <option value="DRAFT">Draft</option>
            <option value="L1_PENDING">L1 Pending</option>
            <option value="ADMIN_PENDING">Admin Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>

          <select
            value={filters.industry}
            onChange={(e) => handleFilterChange('industry', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Industries</option>
            <option value="BFSI">BFSI</option>
            <option value="Government">Government</option>
            <option value="IT_ITeS">IT/ITeS</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Education">Education</option>
            <option value="Telecom">Telecom</option>
          </select>

          <select
            value={filters.is_high_revenue}
            onChange={(e) => handleFilterChange('is_high_revenue', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Revenue</option>
            <option value="true">High Revenue (>₹2Cr)</option>
            <option value="false">Standard Revenue</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type & Industry
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Compliance
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status & Revenue
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
            ) : companies.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                  {search || Object.values(filters).some(f => f) ? 'No companies found matching your criteria' : 'No companies found'}
                </td>
              </tr>
            ) : (
              companies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900 flex items-center">
                        {company.name}
                        {company.is_high_revenue && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                            💰 High Revenue
                          </span>
                        )}
                      </div>
                      {company.website && (
                        <div className="text-sm text-blue-600 hover:text-blue-800">
                          <a href={company.website} target="_blank" rel="noopener noreferrer">
                            {company.website}
                          </a>
                        </div>
                      )}
                      <div className="text-sm text-gray-500">
                        {[company.city, company.state, company.country].filter(Boolean).join(', ')}
                      </div>
                      {company.parent_company_name && (
                        <div className="text-xs text-gray-400">
                          Parent: {company.parent_company_name}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      {getCompanyTypeBadge(company.company_type)}
                      <div className="text-sm text-gray-900">
                        {company.industry?.replace(/_/g, ' ')}
                      </div>
                      {company.sub_industry && (
                        <div className="text-xs text-gray-500">
                          {company.sub_industry}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {company.gst_number && (
                        <div>GST: <span className="font-mono text-xs">{company.gst_number}</span></div>
                      )}
                      {company.pan_number && (
                        <div>PAN: <span className="font-mono text-xs">{company.pan_number}</span></div>
                      )}
                      {company.international_unique_id && (
                        <div>ID: <span className="font-mono text-xs">{company.international_unique_id}</span></div>
                      )}
                      {!company.gst_number && !company.pan_number && !company.international_unique_id && (
                        <span className="text-gray-400 text-xs">Not provided</span>
                      )}
                      {company.verification_source && (
                        <div className="text-xs text-gray-500 mt-1">
                          Verified: {company.verification_source}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      {getStatusBadge(company.status, company.approval_stage)}
                      {company.annual_revenue && (
                        <div className="text-sm text-gray-600">
                          ₹{(company.annual_revenue / 10000000).toFixed(1)}Cr
                        </div>
                      )}
                      {company.sla_breach_date && (
                        <div className="text-xs text-red-600 flex items-center">
                          ⚠️ SLA Breach
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex flex-col space-y-1">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onView(company)}
                          className="text-indigo-600 hover:text-indigo-900 text-sm"
                        >
                          View
                        </button>
                        <button
                          onClick={() => onEdit(company)}
                          className="text-blue-600 hover:text-blue-900 text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(company.id, company.name)}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                      
                      {/* Approval Actions */}
                      {company.approval_stage === 'L1_PENDING' && (
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleApproval(company, 'APPROVE')}
                            className="text-green-600 hover:text-green-900 text-xs"
                          >
                            L1 Approve
                          </button>
                          <button
                            onClick={() => {
                              const reason = prompt('Reason for rejection:');
                              if (reason) handleApproval(company, 'REJECT', reason);
                            }}
                            className="text-red-600 hover:text-red-900 text-xs"
                          >
                            Reject
                          </button>
                        </div>
                      )}
                      
                      {company.approval_stage === 'ADMIN_PENDING' && (
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleApproval(company, 'APPROVE')}
                            className="text-green-600 hover:text-green-900 text-xs"
                          >
                            Activate
                          </button>
                          <button
                            onClick={() => {
                              const reason = prompt('Reason for rejection:');
                              if (reason) handleApproval(company, 'REJECT', reason);
                            }}
                            className="text-red-600 hover:text-red-900 text-xs"
                          >
                            Reject
                          </button>
                        </div>
                      )}
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

export default CompanyList;