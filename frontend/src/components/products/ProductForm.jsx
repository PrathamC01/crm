import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import SearchableDropdown from '../common/SearchableDropdown';
import Modal from '../common/Modal';

const ProductForm = ({ product = null, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'product', // product, service, other
    cat1: '',
    cat2: '',
    cat3: '',
    cat4: '',
    cat5: '',
    oem: '',
    configuration: '',
    price: '',
    description: '',
    sku_code: ''
  });

  const [categories, setCategories] = useState({
    cat1: [],
    cat2: [],
    cat3: [],
    cat4: [],
    cat5: []
  });

  const [showCategoryModal, setShowCategoryModal] = useState(null);
  const [newCategoryData, setNewCategoryData] = useState({
    category_name: '',
    parent_category_id: '',
    level: 1
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const productTypes = [
    { value: 'product', label: 'Product' },
    { value: 'service', label: 'Service' },
    { value: 'other', label: 'Other' }
  ];

  useEffect(() => {
    fetchCategories(1);
    
    if (product) {
      setFormData({
        name: product.name || '',
        type: product.type || 'product',
        cat1: product.cat1 || '',
        cat2: product.cat2 || '',
        cat3: product.cat3 || '',
        cat4: product.cat4 || '',
        cat5: product.cat5 || '',
        oem: product.oem || '',
        configuration: product.configuration || '',
        price: product.price || '',
        description: product.description || '',
        sku_code: product.sku_code || ''
      });
    }
  }, [product]);

  // Watch for category changes to update dependent dropdowns and SKU
  useEffect(() => {
    generateSkuCode();
  }, [formData.cat1, formData.cat2, formData.cat3, formData.cat4, formData.cat5]);

  useEffect(() => {
    if (formData.cat1) fetchCategories(2, formData.cat1);
  }, [formData.cat1]);

  useEffect(() => {
    if (formData.cat2) fetchCategories(3, formData.cat2);
  }, [formData.cat2]);

  useEffect(() => {
    if (formData.cat3) fetchCategories(4, formData.cat3);
  }, [formData.cat3]);

  useEffect(() => {
    if (formData.cat4) fetchCategories(5, formData.cat4);
  }, [formData.cat4]);

  const fetchCategories = async (level, parentId = null) => {
    try {
      const params = { level };
      if (parentId) params.parent_id = parentId;

      const response = await apiMethods.masters.getProductCategories(params);
      if (response.data?.status) {
        const fetchedCategories = response.data.data?.categories || [];
        const categoryOptions = fetchedCategories.map(cat => ({
          value: cat.id,
          label: cat.category_name,
          abbreviation: cat.abbreviation,
          description: `Level ${cat.level} - ${cat.abbreviation}`
        }));

        setCategories(prev => ({
          ...prev,
          [`cat${level}`]: categoryOptions
        }));
      }
    } catch (error) {
      console.error(`Error fetching categories level ${level}:`, error);
    }
  };

  const generateSkuCode = () => {
    // Get abbreviations from selected categories
    const getAbbreviation = (categoryId, level) => {
      const categoryList = categories[`cat${level}`];
      const category = categoryList.find(cat => cat.value === categoryId);
      return category ? category.abbreviation : 'XX';
    };

    const cat1Abbr = getAbbreviation(formData.cat1, 1);
    const cat2Abbr = getAbbreviation(formData.cat2, 2);
    const cat3Abbr = getAbbreviation(formData.cat3, 3);
    const cat4Abbr = getAbbreviation(formData.cat4, 4);
    const cat5Abbr = getAbbreviation(formData.cat5, 5);

    // Generate random 6-digit suffix for uniqueness
    const randomSuffix = Math.random().toString(36).substring(2, 8).toUpperCase();

    // 16-character SKU: 5 categories (2 chars each) + 6 random chars = 16 total
    const skuCode = `${cat1Abbr}${cat2Abbr}${cat3Abbr}${cat4Abbr}${cat5Abbr}${randomSuffix}`;

    setFormData(prev => ({ ...prev, sku_code: skuCode }));
  };

  const handleChange = (name, value) => {
    setFormData(prev => {
      const updated = { ...prev, [name]: value };

      // Reset dependent categories when parent changes
      if (name === 'cat1') {
        updated.cat2 = '';
        updated.cat3 = '';
        updated.cat4 = '';
        updated.cat5 = '';
      } else if (name === 'cat2') {
        updated.cat3 = '';
        updated.cat4 = '';
        updated.cat5 = '';
      } else if (name === 'cat3') {
        updated.cat4 = '';
        updated.cat5 = '';
      } else if (name === 'cat4') {
        updated.cat5 = '';
      }

      return updated;
    });

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleAddNewCategory = (level) => {
    setNewCategoryData({
      category_name: '',
      parent_category_id: level > 1 ? formData[`cat${level - 1}`] : '',
      level: level
    });
    setShowCategoryModal(level);
  };

  const handleSaveNewCategory = async () => {
    try {
      const response = await apiMethods.masters.createProductCategory(newCategoryData);
      if (response.data?.status) {
        // Refresh the categories for this level
        await fetchCategories(newCategoryData.level, newCategoryData.parent_category_id);
        
        // Select the newly created category
        const newCategoryId = response.data.data?.id;
        if (newCategoryId) {
          handleChange(`cat${newCategoryData.level}`, newCategoryId);
        }

        setShowCategoryModal(null);
        setNewCategoryData({ category_name: '', parent_category_id: '', level: 1 });
      }
    } catch (error) {
      console.error('Error creating category:', error);
      alert('Failed to create category');
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    }

    if (!formData.type) {
      newErrors.type = 'Product type is required';
    }

    if (!formData.cat1) {
      newErrors.cat1 = 'Category 1 is required';
    }

    if (formData.type === 'product' && !formData.price) {
      newErrors.price = 'Price is required for products';
    }

    if (formData.type === 'product' && formData.price && parseFloat(formData.price) <= 0) {
      newErrors.price = 'Price must be greater than 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const productData = {
        ...formData,
        price: parseFloat(formData.price) || 0,
        configuration: formData.configuration || null
      };

      let response;
      if (product) {
        response = await apiMethods.products.updateProduct(product.id, productData);
      } else {
        response = await apiMethods.products.createProduct(productData);
      }

      if (response.data?.status) {
        onSave && onSave(response.data.data);
      } else {
        throw new Error(response.data?.message || 'Failed to save product');
      }
    } catch (error) {
      console.error('Error saving product:', error);
      if (error.response?.data?.error && typeof error.response.data.error === 'object') {
        setErrors(error.response.data.error);
      } else {
        setErrors({ submit: error.response?.data?.message || error.message || 'Failed to save product' });
      }
    } finally {
      setLoading(false);
    }
  };

  const getFieldVisibility = () => {
    const type = formData.type;
    return {
      oem: type === 'product' || type === 'service',
      configuration: type === 'product',
      price: true,
      categories: type !== 'other'
    };
  };

  const fieldVisibility = getFieldVisibility();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {errors.submit}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Product Name */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.name ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter product name"
          />
          {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
        </div>

        {/* Product Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Type *
          </label>
          <select
            value={formData.type}
            onChange={(e) => handleChange('type', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.type ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            {productTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {errors.type && <p className="text-red-500 text-sm mt-1">{errors.type}</p>}
        </div>

        {/* SKU Code */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SKU Code (Auto-generated)
          </label>
          <input
            type="text"
            value={formData.sku_code}
            readOnly
            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
            placeholder="Auto-generated based on categories"
          />
          <p className="text-xs text-gray-500 mt-1">
            16-character code generated from category abbreviations
          </p>
        </div>
      </div>

      {/* Categories Section */}
      {fieldVisibility.categories && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Product Categories</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5].map(level => (
              <div key={level}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category {level} {level === 1 ? '*' : ''}
                </label>
                <SearchableDropdown
                  options={categories[`cat${level}`]}
                  value={formData[`cat${level}`]}
                  onChange={(value) => handleChange(`cat${level}`, value)}
                  onAddNew={() => handleAddNewCategory(level)}
                  placeholder={`Select Category ${level}...`}
                  searchPlaceholder={`Search Category ${level}...`}
                  emptyMessage={`No categories found for level ${level}`}
                  addNewLabel="Add New Category"
                  required={level === 1}
                  disabled={level > 1 && !formData[`cat${level - 1}`]}
                  className={errors[`cat${level}`] ? 'border-red-500' : ''}
                />
                {errors[`cat${level}`] && (
                  <p className="text-red-500 text-sm mt-1">{errors[`cat${level}`]}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* OEM Field */}
      {fieldVisibility.oem && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              OEM/Vendor {formData.type === 'product' ? '*' : ''}
            </label>
            <input
              type="text"
              value={formData.oem}
              onChange={(e) => handleChange('oem', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter OEM or vendor name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Price *
            </label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => handleChange('price', e.target.value)}
              min="0"
              step="0.01"
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.price ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter price"
            />
            {errors.price && <p className="text-red-500 text-sm mt-1">{errors.price}</p>}
          </div>
        </div>
      )}

      {/* Configuration Field */}
      {fieldVisibility.configuration && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Configuration
          </label>
          <textarea
            value={formData.configuration}
            onChange={(e) => handleChange('configuration', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter product configuration details (JSON or text)"
          />
        </div>
      )}

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter product description"
        />
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Saving...' : (product ? 'Update Product' : 'Create Product')}
        </button>
      </div>

      {/* Add New Category Modal */}
      <Modal
        isOpen={!!showCategoryModal}
        onClose={() => setShowCategoryModal(null)}
        title={`Add New Category ${showCategoryModal}`}
      >
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category Name *
            </label>
            <input
              type="text"
              value={newCategoryData.category_name}
              onChange={(e) => setNewCategoryData(prev => ({
                ...prev, 
                category_name: e.target.value,
                abbreviation: e.target.value.substring(0, 2).toUpperCase()
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter category name"
            />
          </div>

          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Auto-generated abbreviation:</strong> {
                newCategoryData.category_name.substring(0, 2).toUpperCase() || 'XX'
              }
            </p>
            <p className="text-xs text-gray-500 mt-1">
              This will be used in SKU generation
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={() => setShowCategoryModal(null)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveNewCategory}
              disabled={!newCategoryData.category_name.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Add Category
            </button>
          </div>
        </div>
      </Modal>
    </form>
  );
};

export default ProductForm;