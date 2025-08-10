import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const PriceListsPage = () => {
  const [priceLists, setPriceLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPriceList, setSelectedPriceList] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    status: ''
  });

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'pending_approval', label: 'Pending Approval' }
  ];

  const priceListColumns = [
    {
      key: 'name',
      label: 'Price List Name',
      sortable: true,
      render: (priceList) => (
        <div>
          <div className="font-medium text-gray-900">{priceList.name}</div>
          <div className="text-sm text-gray-500">{priceList.code}</div>
        </div>
      )
    },
    {
      key: 'currency',
      label: 'Currency',
      render: (priceList) => (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
          {priceList.currency || 'INR'}
        </span>
      )
    },
    {
      key: 'type',
      label: 'Type',
      render: (priceList) => (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
          {priceList.type || 'Standard'}
        </span>
      )
    },
    {
      key: 'status',
      label: 'Status',
      render: (priceList) => {
        const statusColors = {
          'active': 'bg-green-100 text-green-800',
          'inactive': 'bg-gray-100 text-gray-800',
          'pending_approval': 'bg-yellow-100 text-yellow-800'
        };
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[priceList.status] || 'bg-gray-100 text-gray-800'}`}>
            {priceList.status === 'pending_approval' ? 'Pending Approval' : 
             priceList.status ? priceList.status.charAt(0).toUpperCase() + priceList.status.slice(1) : 'Active'}
          </span>
        );
      }
    },
    {
      key: 'effective_from',
      label: 'Effective From',
      render: (priceList) => 
        priceList.effective_from ? new Date(priceList.effective_from).toLocaleDateString() : '-'
    },
    {
      key: 'effective_to',
      label: 'Effective To',
      render: (priceList) => 
        priceList.effective_to ? new Date(priceList.effective_to).toLocaleDateString() : 'Ongoing'
    },
    {
      key: 'created_on',
      label: 'Created',
      render: (priceList) => new Date(priceList.created_on).toLocaleDateString()
    }
  ];

  useEffect(() => {
    fetchPriceLists();
  }, [filters]);

  const fetchPriceLists = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getPriceLists(filters);
      if (response.data?.data) {
        setPriceLists(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching price lists:', error);
      setPriceLists([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePriceList = () => {
    setShowCreateModal(true);
  };

  const handleViewPriceList = (priceList) => {
    setSelectedPriceList(priceList);
  };

  const handleApprovePriceList = async (priceListId) => {
    try {
      await apiMethods.masters.approvePriceList(priceListId, { approved: true });
      fetchPriceLists(); // Refresh the list
    } catch (error) {
      console.error('Error approving price list:', error);
    }
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewPriceList,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: (priceList) => {
        console.log('Editing price list:', priceList.id);
      },
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Approve',
      onClick: (priceList) => handleApprovePriceList(priceList.id),
      className: 'text-purple-600 hover:text-purple-900',
      show: (priceList) => priceList.status === 'pending_approval'
    },
    {
      label: 'Duplicate',
      onClick: (priceList) => {
        console.log('Duplicating price list:', priceList.id);
      },
      className: 'text-orange-600 hover:text-orange-900'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Price Lists</h1>
        <button
          onClick={handleCreatePriceList}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Price List
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Price Lists</p>
              <p className="text-2xl font-bold text-gray-900">{priceLists.length}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {priceLists.filter(pl => pl.status === 'active').length}
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
              <p className="text-sm font-medium text-gray-600">Pending Approval</p>
              <p className="text-2xl font-bold text-yellow-600">
                {priceLists.filter(pl => pl.status === 'pending_approval').length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Inactive</p>
              <p className="text-2xl font-bold text-gray-600">
                {priceLists.filter(pl => pl.status === 'inactive').length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-gray-50">
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
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
              placeholder="Search price lists..."
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

      {/* Price Lists Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={priceListColumns}
            data={priceLists}
            actions={actions}
            emptyMessage="No price lists found. Create your first price list to get started."
          />
        )}
      </div>

      {/* Create Price List Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Price List"
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
                placeholder="Price List Name"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code *
              </label>
              <input
                type="text"
                placeholder="PL001"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Currency
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="standard">Standard</option>
                <option value="promotional">Promotional</option>
                <option value="wholesale">Wholesale</option>
                <option value="retail">Retail</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Effective From
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Effective To
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              rows="3"
              placeholder="Price list description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
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
              Create Price List
            </button>
          </div>
        </div>
      </Modal>

      {/* Price List Detail Modal */}
      <Modal
        isOpen={!!selectedPriceList}
        onClose={() => setSelectedPriceList(null)}
        title="Price List Details"
        size="xl"
      >
        {selectedPriceList && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Name</h3>
                <p className="text-gray-900">{selectedPriceList.name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Code</h3>
                <p className="text-gray-900">{selectedPriceList.code}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Currency</h3>
                <p className="text-gray-900">{selectedPriceList.currency || 'INR'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Type</h3>
                <p className="text-gray-900">{selectedPriceList.type || 'Standard'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedPriceList.status || 'Active'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Effective Period</h3>
                <p className="text-gray-900">
                  {selectedPriceList.effective_from ? new Date(selectedPriceList.effective_from).toLocaleDateString() : 'N/A'} - 
                  {selectedPriceList.effective_to ? new Date(selectedPriceList.effective_to).toLocaleDateString() : 'Ongoing'}
                </p>
              </div>
            </div>
            
            {selectedPriceList.description && (
              <div>
                <h3 className="font-semibold text-gray-700">Description</h3>
                <p className="text-gray-900">{selectedPriceList.description}</p>
              </div>
            )}
            
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Product Pricing</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">
                  Product pricing details will be displayed here. This includes all products in this price list with their respective prices and configurations.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedPriceList(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              <button
                onClick={() => {
                  console.log('Editing price list');
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Edit
              </button>
              {selectedPriceList.status === 'pending_approval' && (
                <button
                  onClick={() => {
                    handleApprovePriceList(selectedPriceList.id);
                    setSelectedPriceList(null);
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                  Approve
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PriceListsPage;