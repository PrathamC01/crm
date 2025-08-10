import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const TaxesPage = () => {
  const [taxes, setTaxes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTax, setEditingTax] = useState(null);
  const [selectedTax, setSelectedTax] = useState(null);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchTaxes();
  }, []);

  const fetchTaxes = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getTaxes();
      if (response.data?.status) {
        setTaxes(response.data.data?.taxes || []);
        setStats(response.data.data?.stats || {});
      }
    } catch (error) {
      console.error('Error fetching taxes:', error);
      setTaxes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTax = (tax) => {
    setSelectedTax(tax);
  };

  const handleEditTax = (tax) => {
    setEditingTax(tax);
  };

  const handleDeleteTax = async (tax) => {
    if (window.confirm('Are you sure you want to delete this tax?')) {
      try {
        await apiMethods.masters.deleteTax(tax.id);
        fetchTaxes();
      } catch (error) {
        console.error('Error deleting tax:', error);
        alert('Failed to delete tax');
      }
    }
  };

  const columns = [
    { key: 'tax_name', label: 'Tax Name' },
    { key: 'tax_code', label: 'Tax Code' },
    { key: 'financial_year', label: 'Financial Year' },
    {
      key: 'tax_rate',
      label: 'Tax Rate',
      render: (item) => `${item.tax_rate || 0}%`
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (item) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          item.is_active 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          {item.is_active ? 'Active' : 'Inactive'}
        </span>
      )
    },
    {
      key: 'created_at',
      label: 'Created Date',
      render: (item) => item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'
    }
  ];

  const actions = [
    {
      label: 'View',
      onClick: handleViewTax,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: handleEditTax,
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Delete',
      onClick: handleDeleteTax,
      className: 'text-red-600 hover:text-red-900'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tax Management</h1>
          <p className="text-gray-600">Manage tax configurations and rates for financial calculations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Tax
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Taxes</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total || taxes.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.active || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-red-100">
              <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Inactive</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.inactive || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100">
              <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Tax Rate</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.avg_rate || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Taxes Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={taxes}
            actions={actions}
            emptyMessage="No taxes found. Create your first tax configuration to handle financial calculations."
          />
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal || !!editingTax}
        onClose={() => {
          setShowCreateModal(false);
          setEditingTax(null);
        }}
        title={editingTax ? "Edit Tax" : "Create New Tax"}
        size="large"
      >
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tax Name</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter tax name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tax Code</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter tax code"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Financial Year</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter financial year (e.g., 2024-2025)"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tax Rate (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter tax rate percentage"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
              Active Tax
            </label>
          </div>
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              onClick={() => {
                setShowCreateModal(false);
                setEditingTax(null);
              }}
              className="px-6 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setShowCreateModal(false);
                setEditingTax(null);
                fetchTaxes();
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {editingTax ? "Update" : "Create"} Tax
            </button>
          </div>
        </div>
      </Modal>

      {/* View Details Modal */}
      <Modal
        isOpen={!!selectedTax}
        onClose={() => setSelectedTax(null)}
        title="Tax Details"
      >
        {selectedTax && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Tax Name</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTax.tax_name || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Tax Code</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTax.tax_code || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Financial Year</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTax.financial_year || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Tax Rate</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTax.tax_rate || 0}%</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTax.is_active ? 'Active' : 'Inactive'}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TaxesPage;