import React, { useState, useEffect } from 'react';
import api from '../../../utils/api';

const CompanyList = ({ onEdit, onView, onDelete }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 10,
    total: 0
  });

  useEffect(() => {
    fetchCompanies();
  }, [search, pagination.skip]);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: pagination.skip,
        limit: pagination.limit,
        ...(search && { search })
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

  const handleDelete = async (companyId, companyName) => {
    if (!window.confirm(`Are you sure you want to delete "${companyName}"?`)) return;
    
    try {
      const response = await apiRequest(`/api/companies/${companyId}`, {
        method: 'DELETE'
      });

      if (response.status) {
        await fetchCompanies();
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

  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search companies by name, industry, or city..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPagination(prev => ({ ...prev, skip: 0 }));
          }}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
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
                Industry & Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tax Information
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="4" className="px-6 py-8 text-center">
                  <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  </div>
                </td>
              </tr>
            ) : companies.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                  {search ? 'No companies found matching your search' : 'No companies found'}
                </td>
              </tr>
            ) : (
              companies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{company.name}</div>
                      {company.website && (
                        <div className="text-sm text-blue-600 hover:text-blue-800">
                          <a href={company.website} target="_blank" rel="noopener noreferrer">
                            {company.website}
                          </a>
                        </div>
                      )}
                      {company.description && (
                        <div className="text-sm text-gray-500 truncate max-w-xs">
                          {company.description}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {company.industry_category && (
                        <div className="font-medium">{company.industry_category}</div>
                      )}
                      <div className="text-gray-500">
                        {[company.city, company.state, company.country].filter(Boolean).join(', ')}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {company.gst_number && (
                        <div>GST: <span className="font-mono">{company.gst_number}</span></div>
                      )}
                      {company.pan_number && (
                        <div>PAN: <span className="font-mono">{company.pan_number}</span></div>
                      )}
                      {!company.gst_number && !company.pan_number && (
                        <span className="text-gray-400">Not provided</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => onView(company)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        View
                      </button>
                      <button
                        onClick={() => onEdit(company)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(company.id, company.name)}
                        className="text-red-600 hover:text-red-900"
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

export default CompanyList;