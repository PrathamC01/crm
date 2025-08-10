import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const QuotationsPage = () => {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    search: ''
  });

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'Draft', label: 'Draft' },
    { value: 'Sent', label: 'Sent' },
    { value: 'Accepted', label: 'Accepted' },
    { value: 'Rejected', label: 'Rejected' },
    { value: 'Expired', label: 'Expired' }
  ];

  const quotationColumns = [
    {
      key: 'quotation_number',
      label: 'Quote #',
      render: (quotation) => (
        <div className="font-medium text-blue-600">{quotation.quotation_number || `Q-${quotation.id}`}</div>
      )
    },
    {
      key: 'opportunity_name',
      label: 'Opportunity',
      sortable: true,
      render: (quotation) => (
        <div>
          <div className="font-medium text-gray-900">{quotation.opportunity_name}</div>
          <div className="text-sm text-gray-500">{quotation.company_name}</div>
        </div>
      )
    },
    {
      key: 'total_amount',
      label: 'Total Amount',
      render: (quotation) => (
        <div className="text-right">
          <div className="font-medium">₹{Number(quotation.total_amount || 0).toLocaleString()}</div>
          <div className="text-sm text-gray-500">{quotation.currency || 'INR'}</div>
        </div>
      )
    },
    {
      key: 'status',
      label: 'Status',
      render: (quotation) => {
        const statusColors = {
          'Draft': 'bg-gray-100 text-gray-800',
          'Sent': 'bg-blue-100 text-blue-800',
          'Accepted': 'bg-green-100 text-green-800',
          'Rejected': 'bg-red-100 text-red-800',
          'Expired': 'bg-yellow-100 text-yellow-800'
        };
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[quotation.status] || 'bg-gray-100 text-gray-800'}`}>
            {quotation.status || 'Draft'}
          </span>
        );
      }
    },
    {
      key: 'valid_until',
      label: 'Valid Until',
      render: (quotation) => 
        quotation.valid_until ? new Date(quotation.valid_until).toLocaleDateString() : '-'
    },
    {
      key: 'created_on',
      label: 'Created',
      render: (quotation) => new Date(quotation.created_on).toLocaleDateString()
    },
    {
      key: 'created_by_name',
      label: 'Created By',
      render: (quotation) => (
        <div className="text-sm text-gray-600">{quotation.created_by_name}</div>
      )
    }
  ];

  useEffect(() => {
    fetchQuotations();
  }, [filters]);

  const fetchQuotations = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.quotations.getQuotations(filters);
      if (response.data?.data?.quotations) {
        setQuotations(response.data.data.quotations);
      }
    } catch (error) {
      console.error('Error fetching quotations:', error);
      // Mock data for demonstration
      setQuotations([
        {
          id: 1,
          quotation_number: 'Q-2024-001',
          opportunity_name: 'Enterprise CRM Implementation',
          company_name: 'TechCorp Solutions',
          total_amount: 2500000,
          currency: 'INR',
          status: 'Sent',
          valid_until: '2024-12-31',
          created_on: '2024-11-01',
          created_by_name: 'John Doe'
        },
        {
          id: 2,
          quotation_number: 'Q-2024-002',
          opportunity_name: 'Cloud Migration Project',
          company_name: 'DataFlow Inc',
          total_amount: 1800000,
          currency: 'INR',
          status: 'Draft',
          valid_until: '2024-12-15',
          created_on: '2024-11-05',
          created_by_name: 'Jane Smith'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewQuotation = (quotation) => {
    setSelectedQuotation(quotation);
  };

  const handleCreateQuotation = () => {
    setShowCreateModal(true);
  };

  const handleUpdateStatus = async (quotationId, newStatus) => {
    try {
      await apiMethods.quotations.updateQuotation(quotationId, { status: newStatus });
      fetchQuotations(); // Refresh the list
    } catch (error) {
      console.error('Error updating quotation status:', error);
    }
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewQuotation,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: (quotation) => {
        console.log('Editing quotation:', quotation.id);
      },
      className: 'text-green-600 hover:text-green-900',
      show: (quotation) => quotation.status === 'Draft'
    },
    {
      label: 'Send',
      onClick: (quotation) => handleUpdateStatus(quotation.id, 'Sent'),
      className: 'text-purple-600 hover:text-purple-900',
      show: (quotation) => quotation.status === 'Draft'
    },
    {
      label: 'Download PDF',
      onClick: (quotation) => {
        console.log('Downloading PDF for quotation:', quotation.id);
      },
      className: 'text-orange-600 hover:text-orange-900'
    }
  ];

  // Calculate stats
  const stats = {
    total: quotations.length,
    draft: quotations.filter(q => q.status === 'Draft').length,
    sent: quotations.filter(q => q.status === 'Sent').length,
    accepted: quotations.filter(q => q.status === 'Accepted').length,
    totalValue: quotations.reduce((sum, q) => sum + (Number(q.total_amount) || 0), 0),
    acceptanceRate: quotations.length > 0 
      ? Math.round((quotations.filter(q => q.status === 'Accepted').length / quotations.filter(q => q.status !== 'Draft').length) * 100) || 0
      : 0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quotations</h1>
        <button
          onClick={handleCreateQuotation}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Quotation
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Draft</p>
              <p className="text-2xl font-bold text-gray-600">{stats.draft}</p>
            </div>
            <div className="p-3 rounded-md bg-gray-50">
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Sent</p>
              <p className="text-2xl font-bold text-blue-600">{stats.sent}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Accepted</p>
              <p className="text-2xl font-bold text-green-600">{stats.accepted}</p>
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
              <p className="text-sm font-medium text-gray-600">Acceptance Rate</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.acceptanceRate}%</p>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search quotations..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
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

      {/* Quotations Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={quotationColumns}
            data={quotations}
            actions={actions}
            emptyMessage="No quotations found. Create your first quotation from an opportunity."
          />
        )}
      </div>

      {/* Create Quotation Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Quotation"
        size="xl"
      >
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            Quotation creation form will be implemented here. This includes opportunity selection, product/service configuration, pricing, terms, and conditions.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Handle form submission
                setShowCreateModal(false);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create Quotation
            </button>
          </div>
        </div>
      </Modal>

      {/* Quotation Detail Modal */}
      <Modal
        isOpen={!!selectedQuotation}
        onClose={() => setSelectedQuotation(null)}
        title="Quotation Details"
        size="xl"
      >
        {selectedQuotation && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Quotation Number</h3>
                <p className="text-blue-600 font-medium">{selectedQuotation.quotation_number}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Opportunity</h3>
                <p className="text-gray-900">{selectedQuotation.opportunity_name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Company</h3>
                <p className="text-gray-900">{selectedQuotation.company_name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedQuotation.status}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Total Amount</h3>
                <p className="text-gray-900">₹{Number(selectedQuotation.total_amount || 0).toLocaleString()}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Valid Until</h3>
                <p className="text-gray-900">
                  {selectedQuotation.valid_until ? new Date(selectedQuotation.valid_until).toLocaleDateString() : '-'}
                </p>
              </div>
            </div>
            
            <div className="pt-4">
              <h3 className="font-semibold text-gray-700 mb-2">Items & Pricing</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">
                  Detailed quotation items, pricing breakdown, terms and conditions will be displayed here.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedQuotation(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              {selectedQuotation.status === 'Draft' && (
                <>
                  <button
                    onClick={() => {
                      console.log('Editing quotation');
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      handleUpdateStatus(selectedQuotation.id, 'Sent');
                      setSelectedQuotation(null);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Send Quotation
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default QuotationsPage;