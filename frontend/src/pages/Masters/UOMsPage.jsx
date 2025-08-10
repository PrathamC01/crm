import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const UOMsPage = () => {
  const [uoms, setUOMs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedUOM, setSelectedUOM] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    status: ''
  });

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    { value: 'length', label: 'Length' },
    { value: 'weight', label: 'Weight' },
    { value: 'volume', label: 'Volume' },
    { value: 'area', label: 'Area' },
    { value: 'count', label: 'Count' },
    { value: 'time', label: 'Time' }
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
  ];

  const uomColumns = [
    {
      key: 'name',
      label: 'UOM Name',
      sortable: true,
      render: (uom) => (
        <div>
          <div className="font-medium text-gray-900">{uom.name}</div>
          <div className="text-sm text-gray-500">{uom.code}</div>
        </div>
      )
    },
    {
      key: 'symbol',
      label: 'Symbol',
      render: (uom) => (
        <span className="px-2 py-1 text-sm font-semibold bg-blue-100 text-blue-800 rounded">
          {uom.symbol}
        </span>
      )
    },
    {
      key: 'category',
      label: 'Category',
      render: (uom) => (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
          {uom.category || 'General'}
        </span>
      )
    },
    {
      key: 'conversion_factor',
      label: 'Base Conversion',
      render: (uom) => (
        <div className="text-sm">
          {uom.conversion_factor ? `1 ${uom.symbol} = ${uom.conversion_factor} base` : 'Base unit'}
        </div>
      )
    },
    {
      key: 'is_base',
      label: 'Type',
      render: (uom) => (
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
          uom.is_base ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {uom.is_base ? 'Base Unit' : 'Derived'}
        </span>
      )
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (uom) => {
        const isActive = uom.is_active !== false;
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
            isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isActive ? 'Active' : 'Inactive'}
          </span>
        );
      }
    },
    {
      key: 'created_on',
      label: 'Created',
      render: (uom) => new Date(uom.created_on).toLocaleDateString()
    }
  ];

  useEffect(() => {
    fetchUOMs();
  }, [filters]);

  const fetchUOMs = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getUOMs(filters);
      if (response.data?.data) {
        setUOMs(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching UOMs:', error);
      setUOMs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUOM = () => {
    setShowCreateModal(true);
  };

  const handleViewUOM = (uom) => {
    setSelectedUOM(uom);
  };

  const handleToggleStatus = async (uomId, currentStatus) => {
    try {
      await apiMethods.masters.updateUOM(uomId, { is_active: !currentStatus });
      fetchUOMs(); // Refresh the list
    } catch (error) {
      console.error('Error updating UOM status:', error);
    }
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewUOM,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: (uom) => {
        console.log('Editing UOM:', uom.id);
      },
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Activate',
      onClick: (uom) => handleToggleStatus(uom.id, uom.is_active),
      className: 'text-green-600 hover:text-green-900',
      show: (uom) => !uom.is_active
    },
    {
      label: 'Deactivate',
      onClick: (uom) => handleToggleStatus(uom.id, uom.is_active),
      className: 'text-red-600 hover:text-red-900',
      show: (uom) => uom.is_active && !uom.is_base
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Units of Measure</h1>
        <button
          onClick={handleCreateUOM}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create UOM
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total UOMs</p>
              <p className="text-2xl font-bold text-gray-900">{uoms.length}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {uoms.filter(uom => uom.is_active !== false).length}
              </p>
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
              <p className="text-sm font-medium text-gray-600">Base Units</p>
              <p className="text-2xl font-bold text-purple-600">
                {uoms.filter(uom => uom.is_base).length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Categories</p>
              <p className="text-2xl font-bold text-yellow-600">
                {new Set(uoms.map(uom => uom.category).filter(Boolean)).size}
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
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
              placeholder="Search UOMs..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categoryOptions.map(option => (
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

      {/* UOMs Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={uomColumns}
            data={uoms}
            actions={actions}
            emptyMessage="No units of measure found. Create your first UOM to get started."
          />
        )}
      </div>

      {/* Create UOM Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New UOM"
        size="lg"
      >
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name *
              </label>
              <input
                type="text"
                placeholder="Meter"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code *
              </label>
              <input
                type="text"
                placeholder="MTR"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol *
              </label>
              <input
                type="text"
                placeholder="m"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Select Category</option>
                {categoryOptions.slice(1).map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Conversion Factor
              </label>
              <input
                type="number"
                step="0.001"
                placeholder="1.0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="isBase"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="isBase" className="ml-2 block text-sm text-gray-900">
                Base unit for this category
              </label>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              rows="3"
              placeholder="Unit of measure description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div className="flex items-center mb-6">
            <input
              type="checkbox"
              id="isActiveUOM"
              defaultChecked
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="isActiveUOM" className="ml-2 block text-sm text-gray-900">
              Active UOM
            </label>
          </div>

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
              Create UOM
            </button>
          </div>
        </div>
      </Modal>

      {/* UOM Detail Modal */}
      <Modal
        isOpen={!!selectedUOM}
        onClose={() => setSelectedUOM(null)}
        title="UOM Details"
        size="lg"
      >
        {selectedUOM && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Name</h3>
                <p className="text-gray-900">{selectedUOM.name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Code</h3>
                <p className="text-gray-900">{selectedUOM.code}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Symbol</h3>
                <p className="text-gray-900">{selectedUOM.symbol}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Category</h3>
                <p className="text-gray-900">{selectedUOM.category || 'General'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Type</h3>
                <p className="text-gray-900">{selectedUOM.is_base ? 'Base Unit' : 'Derived Unit'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedUOM.is_active !== false ? 'Active' : 'Inactive'}</p>
              </div>
            </div>
            
            {selectedUOM.conversion_factor && (
              <div>
                <h3 className="font-semibold text-gray-700">Conversion Factor</h3>
                <p className="text-gray-900">1 {selectedUOM.symbol} = {selectedUOM.conversion_factor} base unit</p>
              </div>
            )}

            {selectedUOM.description && (
              <div>
                <h3 className="font-semibold text-gray-700">Description</h3>
                <p className="text-gray-900">{selectedUOM.description}</p>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-700">Created On</h3>
              <p className="text-gray-900">{new Date(selectedUOM.created_on).toLocaleDateString()}</p>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedUOM(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              <button
                onClick={() => {
                  console.log('Editing UOM');
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Edit
              </button>
              {!selectedUOM.is_base && (
                <button
                  onClick={() => {
                    handleToggleStatus(selectedUOM.id, selectedUOM.is_active);
                    setSelectedUOM(null);
                  }}
                  className={`px-4 py-2 rounded-md ${
                    selectedUOM.is_active !== false
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {selectedUOM.is_active !== false ? 'Deactivate' : 'Activate'}
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default UOMsPage;