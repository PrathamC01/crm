import React, { useState, useEffect } from 'react';
import { PlusIcon, PencilIcon, EyeIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import DataTable from '../common/DataTable';
import Modal from '../common/Modal';
import FormBuilder from '../common/FormBuilder';
import { apiRequest } from '../../utils/api';

const ProductMaster = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    cat1_type: '',
    cat2_category: '',
    page: 1,
    per_page: 20
  });
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // Lookup data
  const [uoms, setUoms] = useState([]);
  const [categories, setCategories] = useState([]);

  const productTypes = [
    { value: 'product', label: 'Product' },
    { value: 'service', label: 'Service' },
    { value: 'other', label: 'Other' }
  ];

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await apiRequest('/api/masters/products', {
        method: 'GET',
        params: filters
      });
      
      if (response.status) {
        setProducts(response.data.items || []);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLookupData = async () => {
    try {
      // Fetch UOMs
      const uomResponse = await apiRequest('/api/masters/uoms');
      if (uomResponse.status) {
        setUoms(uomResponse.data.items || []);
      }
      
      // Fetch categories (can be hardcoded or from API)
      setCategories([
        'Security', 'Infrastructure', 'Software', 'Hardware', 'Services', 'Cloud', 'Network'
      ]);
    } catch (error) {
      console.error('Error fetching lookup data:', error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  useEffect(() => {
    fetchLookupData();
  }, []);

  const handleCreate = async (formData) => {
    try {
      const response = await apiRequest('/api/masters/products', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      if (response.status) {
        setShowCreateModal(false);
        fetchProducts();
        // Show success message
      } else {
        // Show error message
        console.error('Create failed:', response.message);
      }
    } catch (error) {
      console.error('Error creating product:', error);
    }
  };

  const handleEdit = async (formData) => {
    try {
      const response = await apiRequest(`/api/masters/products/${selectedProduct.id}`, {
        method: 'PUT',
        body: JSON.stringify(formData)
      });
      
      if (response.status) {
        setShowEditModal(false);
        setSelectedProduct(null);
        fetchProducts();
      }
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const columns = [
    {
      key: 'sku_code',
      title: 'SKU Code',
      sortable: true,
      render: (value) => (
        <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: 'name',
      title: 'Product Name',
      sortable: true
    },
    {
      key: 'cat1_type',
      title: 'Type',
      render: (value) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          value === 'product' ? 'bg-blue-100 text-blue-800' :
          value === 'service' ? 'bg-green-100 text-green-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {value?.charAt(0).toUpperCase() + value?.slice(1)}
        </span>
      )
    },
    {
      key: 'cat2_category',
      title: 'Category',
      sortable: true
    },
    {
      key: 'cat3_sub_category',
      title: 'Sub Category',
      sortable: true
    },
    {
      key: 'uoms',
      title: 'UOMs',
      render: (value) => (
        <div className="flex flex-wrap gap-1">
          {(value || []).slice(0, 2).map((uom, index) => (
            <span key={index} className="inline-flex px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
              {uom.uom_code}
            </span>
          ))}
          {value?.length > 2 && (
            <span className="text-xs text-gray-500">+{value.length - 2} more</span>
          )}
        </div>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (_, product) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setSelectedProduct(product);
              setShowViewModal(true);
            }}
            className="text-blue-600 hover:text-blue-900"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              setSelectedProduct(product);
              setShowEditModal(true);
            }}
            className="text-green-600 hover:text-green-900"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
        </div>
      )
    }
  ];

  const productFormFields = [
    {
      name: 'name',
      label: 'Product Name',
      type: 'text',
      placeholder: 'Leave empty for auto-generation from categories',
      required: false
    },
    {
      name: 'cat1_type',
      label: 'Type',
      type: 'select',
      options: productTypes,
      required: true
    },
    {
      name: 'cat2_category',
      label: 'Category',
      type: 'select',
      options: categories.map(cat => ({ value: cat, label: cat })),
      required: true
    },
    {
      name: 'cat3_sub_category',
      label: 'Sub Category',
      type: 'text',
      required: true
    },
    {
      name: 'cat4_oem',
      label: 'OEM',
      type: 'text',
      required: false
    },
    {
      name: 'cat5_configuration',
      label: 'Configuration (JSON)',
      type: 'textarea',
      placeholder: '{"memory": "16GB", "storage": "1TB"}',
      required: false
    },
    {
      name: 'description',
      label: 'Description',
      type: 'textarea',
      required: false
    },
    {
      name: 'uom_ids',
      label: 'Units of Measure',
      type: 'multi-select',
      options: uoms.map(uom => ({ value: uom.id, label: `${uom.uom_name} (${uom.uom_code})` })),
      required: true
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Product Master</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your product catalog with categories and UOM mappings
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Product
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              placeholder="Search products..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.cat1_type}
              onChange={(e) => setFilters({ ...filters, cat1_type: e.target.value, page: 1 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {productTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={filters.cat2_category}
              onChange={(e) => setFilters({ ...filters, cat2_category: e.target.value, page: 1 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ search: '', cat1_type: '', cat2_category: '', page: 1, per_page: 20 })}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          columns={columns}
          data={products}
          loading={loading}
          pagination={{
            current: filters.page,
            pageSize: filters.per_page,
            total: products.length,
            onChange: (page) => setFilters({ ...filters, page })
          }}
        />
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Product"
        size="lg"
      >
        <FormBuilder
          fields={productFormFields}
          onSubmit={handleCreate}
          onCancel={() => setShowCreateModal(false)}
          submitText="Create Product"
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedProduct(null);
        }}
        title="Edit Product"
        size="lg"
      >
        {selectedProduct && (
          <FormBuilder
            fields={productFormFields}
            initialData={selectedProduct}
            onSubmit={handleEdit}
            onCancel={() => {
              setShowEditModal(false);
              setSelectedProduct(null);
            }}
            submitText="Update Product"
          />
        )}
      </Modal>

      {/* View Modal */}
      <Modal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setSelectedProduct(null);
        }}
        title="Product Details"
        size="lg"
      >
        {selectedProduct && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">SKU Code</label>
                <p className="mt-1 font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                  {selectedProduct.sku_code}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.cat1_type}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.cat2_category}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Sub Category</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.cat3_sub_category}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">OEM</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.cat4_oem || 'N/A'}</p>
              </div>
            </div>
            
            {selectedProduct.description && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-sm text-gray-900">{selectedProduct.description}</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Units of Measure</label>
              <div className="flex flex-wrap gap-2">
                {(selectedProduct.uoms || []).map((uom, index) => (
                  <span
                    key={index}
                    className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
                      uom.is_primary ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {uom.uom_name} ({uom.uom_code})
                    {uom.is_primary && <span className="ml-1">•</span>}
                  </span>
                ))}
              </div>
            </div>

            {selectedProduct.cat5_configuration && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Configuration</label>
                <pre className="mt-1 text-sm text-gray-900 bg-gray-100 p-2 rounded overflow-auto">
                  {JSON.stringify(selectedProduct.cat5_configuration, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ProductMaster;