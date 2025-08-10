import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const ProductGroupingPage = () => {
  const [productGroupings, setProductGroupings] = useState([]);
  const [products, setProducts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingGrouping, setEditingGrouping] = useState(null);
  const [selectedGrouping, setSelectedGrouping] = useState(null);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchProductGroupings();
    fetchProducts();
    fetchGroups();
  }, []);

  const fetchProductGroupings = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getProductGroupings();
      if (response.data?.status) {
        setProductGroupings(response.data.data?.product_groupings || []);
        setStats(response.data.data?.stats || {});
      }
    } catch (error) {
      console.error('Error fetching product groupings:', error);
      setProductGroupings([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await apiMethods.masters.getProducts();
      if (response.data?.status) {
        setProducts(response.data.data?.products || []);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    }
  };

  const fetchGroups = async () => {
    try {
      const response = await apiMethods.masters.getGroups();
      if (response.data?.status) {
        setGroups(response.data.data?.groups || []);
      }
    } catch (error) {
      console.error('Error fetching groups:', error);
      setGroups([]);
    }
  };

  const handleViewGrouping = (grouping) => {
    setSelectedGrouping(grouping);
  };

  const handleEditGrouping = (grouping) => {
    setEditingGrouping(grouping);
  };

  const handleDeleteGrouping = async (grouping) => {
    if (window.confirm('Are you sure you want to delete this product grouping?')) {
      try {
        await apiMethods.masters.deleteProductGrouping(grouping.id);
        fetchProductGroupings();
      } catch (error) {
        console.error('Error deleting product grouping:', error);
        alert('Failed to delete product grouping');
      }
    }
  };

  const columns = [
    {
      key: 'product_name',
      label: 'Product',
      render: (item) => item.product_name || 'N/A'
    },
    {
      key: 'group_name',
      label: 'Group',
      render: (item) => item.group_name || 'N/A'
    },
    {
      key: 'discount',
      label: 'Discount (%)',
      render: (item) => `${item.discount || 0}%`
    },
    {
      key: 'is_approved',
      label: 'Status',
      render: (item) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          item.is_approved 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {item.is_approved ? 'Approved' : 'Pending'}
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
      onClick: handleViewGrouping,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: handleEditGrouping,
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Delete',
      onClick: handleDeleteGrouping,
      className: 'text-red-600 hover:text-red-900'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Product Groupings</h1>
          <p className="text-gray-600">Manage product group associations and discount configurations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Product Grouping
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Groupings</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total || productGroupings.length}</p>
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
              <p className="text-sm font-medium text-gray-600">Approved</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.approved || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.pending || 0}</p>
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
              <p className="text-sm font-medium text-gray-600">Avg Discount</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.avg_discount || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Product Groupings Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={productGroupings}
            actions={actions}
            emptyMessage="No product groupings found. Create your first product grouping to manage group associations."
          />
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal || !!editingGrouping}
        onClose={() => {
          setShowCreateModal(false);
          setEditingGrouping(null);
        }}
        title={editingGrouping ? "Edit Product Grouping" : "Create New Product Grouping"}
        size="large"
      >
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Product</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Select Product</option>
              {products.length === 0 ? (
                <option disabled>No products found</option>
              ) : (
                products.map(product => (
                  <option key={product.id} value={product.id}>{product.name}</option>
                ))
              )}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Group</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Select Group</option>
              {groups.length === 0 ? (
                <option disabled>No groups found</option>
              ) : (
                groups.map(group => (
                  <option key={group.id} value={group.id}>{group.group_name}</option>
                ))
              )}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Discount (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter discount percentage"
            />
          </div>
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              onClick={() => {
                setShowCreateModal(false);
                setEditingGrouping(null);
              }}
              className="px-6 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setShowCreateModal(false);
                setEditingGrouping(null);
                fetchProductGroupings();
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {editingGrouping ? "Update" : "Create"} Product Grouping
            </button>
          </div>
        </div>
      </Modal>

      {/* View Details Modal */}
      <Modal
        isOpen={!!selectedGrouping}
        onClose={() => setSelectedGrouping(null)}
        title="Product Grouping Details"
      >
        {selectedGrouping && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product</label>
                <p className="mt-1 text-sm text-gray-900">{selectedGrouping.product_name || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Group</label>
                <p className="mt-1 text-sm text-gray-900">{selectedGrouping.group_name || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Discount</label>
                <p className="mt-1 text-sm text-gray-900">{selectedGrouping.discount || 0}%</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <p className="mt-1 text-sm text-gray-900">{selectedGrouping.is_approved ? 'Approved' : 'Pending'}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ProductGroupingPage;