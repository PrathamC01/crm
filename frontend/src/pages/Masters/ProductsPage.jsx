import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import ProductForm from '../../components/masters/ProductForm';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { PlusIcon, PencilIcon, EyeIcon } from '@heroicons/react/24/outline';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [uoms, setUoms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [viewingProduct, setViewingProduct] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    fetchProducts();
    fetchUOMs();
  }, []);

  const fetchProducts = async (page = 1) => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getProducts({ page, per_page: 20 });
      if (response.data.status) {
        setProducts(response.data.data.items);
        setPagination({
          page: response.data.data.page,
          per_page: response.data.data.per_page,
          total: response.data.data.total,
          pages: response.data.data.pages
        });
      } else {
        setError('Failed to load products');
      }
    } catch (error) {
      console.error('Products fetch error:', error);
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const fetchUOMs = async () => {
    try {
      const response = await apiMethods.masters.getUOMs();
      if (response.data.status) {
        setUoms(response.data.data.items);
      }
    } catch (error) {
      console.error('UOMs fetch error:', error);
    }
  };

  const handleCreateProduct = async (productData) => {
    try {
      const response = await apiMethods.masters.createProduct(productData);
      if (response.data.status) {
        setShowModal(false);
        await fetchProducts(pagination.page);
        alert('Product created successfully!');
      } else {
        alert('Failed to create product');
      }
    } catch (error) {
      console.error('Create product error:', error);
      alert('Failed to create product');
    }
  };

  const handleUpdateProduct = async (productData) => {
    try {
      const response = await apiMethods.masters.updateProduct(editingProduct.id, productData);
      if (response.data.status) {
        setShowModal(false);
        setEditingProduct(null);
        await fetchProducts(pagination.page);
        alert('Product updated successfully!');
      } else {
        alert('Failed to update product');
      }
    } catch (error) {
      console.error('Update product error:', error);
      alert('Failed to update product');
    }
  };

  const columns = [
    {
      key: 'name',
      title: 'Product Name',
      render: (item) => (
        <div>
          <div className="font-medium text-gray-900">{item.name}</div>
          <div className="text-sm text-gray-500">SKU: {item.sku_code}</div>
        </div>
      )
    },
    {
      key: 'cat2_category',
      title: 'Category',
      render: (item) => (
        <div>
          <div className="text-sm text-gray-900">{item.cat2_category}</div>
          <div className="text-xs text-gray-500">{item.cat3_sub_category}</div>
        </div>
      )
    },
    {
      key: 'cat1_type',
      title: 'Type',
      render: (item) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          item.cat1_type === 'product' ? 'bg-blue-100 text-blue-800' :
          item.cat1_type === 'service' ? 'bg-green-100 text-green-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {item.cat1_type}
        </span>
      )
    },
    {
      key: 'uoms',
      title: 'UOMs',
      render: (item) => (
        <div className="flex flex-wrap gap-1">
          {item.uoms?.map((uom, index) => (
            <span 
              key={index}
              className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                uom.is_primary ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
              }`}
            >
              {uom.uom_code}
              {uom.is_primary && <span className="ml-1">★</span>}
            </span>
          ))}
        </div>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (item) => (
        <div className="flex space-x-2">
          <button
            onClick={() => setViewingProduct(item)}
            className="text-blue-600 hover:text-blue-900"
            title="View"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              setEditingProduct(item);
              setShowModal(true);
            }}
            className="text-green-600 hover:text-green-900"
            title="Edit"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
        </div>
      )
    }
  ];

  if (loading && products.length === 0) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600">Manage your product catalog</p>
        </div>
        <button
          onClick={() => {
            setEditingProduct(null);
            setShowModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Product
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          columns={columns}
          data={products}
          pagination={pagination}
          onPageChange={fetchProducts}
          loading={loading}
          emptyMessage="No products found. Create your first product to get started."
        />
      </div>

      {/* Product Form Modal */}
      <Modal
        show={showModal}
        onClose={() => {
          setShowModal(false);
          setEditingProduct(null);
        }}
        title={editingProduct ? 'Edit Product' : 'Create New Product'}
        size="large"
      >
        <ProductForm
          product={editingProduct}
          uoms={uoms}
          onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct}
          onCancel={() => {
            setShowModal(false);
            setEditingProduct(null);
          }}
        />
      </Modal>

      {/* Product View Modal */}
      <Modal
        show={!!viewingProduct}
        onClose={() => setViewingProduct(null)}
        title="Product Details"
        size="large"
      >
        {viewingProduct && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <p className="mt-1 text-sm text-gray-900">{viewingProduct.name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">SKU Code</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{viewingProduct.sku_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <p className="mt-1 text-sm text-gray-900 capitalize">{viewingProduct.cat1_type}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <p className="mt-1 text-sm text-gray-900">{viewingProduct.cat2_category}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Sub Category</label>
                <p className="mt-1 text-sm text-gray-900">{viewingProduct.cat3_sub_category}</p>
              </div>
              {viewingProduct.cat4_oem && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">OEM</label>
                  <p className="mt-1 text-sm text-gray-900">{viewingProduct.cat4_oem}</p>
                </div>
              )}
            </div>
            
            {viewingProduct.description && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-sm text-gray-900">{viewingProduct.description}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Units of Measure</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {viewingProduct.uoms?.map((uom, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${uom.is_primary ? 'border-green-300 bg-green-50' : 'border-gray-200'}`}>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">{uom.uom_name} ({uom.uom_code})</p>
                        {uom.conversion_factor && (
                          <p className="text-sm text-gray-600">Factor: {uom.conversion_factor}</p>
                        )}
                      </div>
                      {uom.is_primary && (
                        <span className="text-green-600 text-sm font-medium">Primary</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setViewingProduct(null)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ProductsPage;