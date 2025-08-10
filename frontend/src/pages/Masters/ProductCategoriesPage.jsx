import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const ProductCategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(1);
  const [stats, setStats] = useState({});
  
  const [formData, setFormData] = useState({
    category_name: '',
    parent_category_id: '',
    level: 1,
    abbreviation: ''
  });

  const categoryLevels = [
    { level: 1, name: 'Category 1', key: 'cat1' },
    { level: 2, name: 'Category 2', key: 'cat2' },
    { level: 3, name: 'Category 3', key: 'cat3' },
    { level: 4, name: 'Category 4', key: 'cat4' },
    { level: 5, name: 'Category 5', key: 'cat5' }
  ];

  useEffect(() => {
    fetchCategories();
    fetchAllCategories();
  }, [selectedLevel]);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getProductCategories({ level: selectedLevel });
      if (response.data?.status) {
        setCategories(response.data.data?.categories || []);
        setStats(response.data.data?.stats || {});
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllCategories = async () => {
    try {
      const response = await apiMethods.masters.getProductCategories();
      if (response.data?.status) {
        setAllCategories(response.data.data?.categories || []);
      }
    } catch (error) {
      console.error('Error fetching all categories:', error);
      setAllCategories([]);
    }
  };

  const generateAbbreviation = (categoryName) => {
    if (!categoryName) return '';
    
    // Extract first 2 characters of each word, uppercase
    const words = categoryName.split(' ');
    let abbreviation = '';
    
    if (words.length === 1) {
      // Single word - take first 2 characters
      abbreviation = words[0].substring(0, 2).toUpperCase();
    } else {
      // Multiple words - take first character of each word, max 2
      abbreviation = words
        .slice(0, 2)
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase();
    }
    
    return abbreviation.padEnd(2, 'X'); // Ensure 2 digits
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updated = { ...prev, [name]: value };
      
      // Auto-generate abbreviation when category name changes
      if (name === 'category_name') {
        updated.abbreviation = generateAbbreviation(value);
      }
      
      return updated;
    });
  };

  const handleCreate = () => {
    setFormData({
      category_name: '',
      parent_category_id: '',
      level: selectedLevel,
      abbreviation: ''
    });
    setEditingCategory(null);
    setShowCreateModal(true);
  };

  const handleEdit = (category) => {
    setFormData({
      category_name: category.category_name,
      parent_category_id: category.parent_category_id || '',
      level: category.level,
      abbreviation: category.abbreviation
    });
    setEditingCategory(category);
    setShowCreateModal(true);
  };

  const handleSave = async () => {
    try {
      const categoryData = {
        ...formData,
        level: selectedLevel
      };

      if (editingCategory) {
        await apiMethods.masters.updateProductCategory(editingCategory.id, categoryData);
      } else {
        await apiMethods.masters.createProductCategory(categoryData);
      }

      setShowCreateModal(false);
      fetchCategories();
      fetchAllCategories();
    } catch (error) {
      console.error('Error saving category:', error);
      alert('Failed to save category');
    }
  };

  const handleDelete = async (category) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await apiMethods.masters.deleteProductCategory(category.id);
        fetchCategories();
        fetchAllCategories();
      } catch (error) {
        console.error('Error deleting category:', error);
        alert('Failed to delete category');
      }
    }
  };

  const getParentCategories = () => {
    return allCategories.filter(cat => cat.level === (selectedLevel - 1));
  };

  const columns = [
    { key: 'category_name', label: 'Category Name' },
    { key: 'abbreviation', label: 'Abbreviation' },
    {
      key: 'parent_category_name',
      label: 'Parent Category',
      render: (item) => item.parent_category_name || 'Root Level'
    },
    { key: 'level', label: 'Level' },
    {
      key: 'children_count',
      label: 'Sub-Categories',
      render: (item) => `${item.children_count || 0} items`
    },
    {
      key: 'created_at',
      label: 'Created Date',
      render: (item) => item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'
    }
  ];

  const actions = [
    {
      label: 'Edit',
      onClick: handleEdit,
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Delete',
      onClick: handleDelete,
      className: 'text-red-600 hover:text-red-900'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Product Categories</h1>
          <p className="text-gray-600">Manage hierarchical product categorization system</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Category
        </button>
      </div>

      {/* Category Level Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            {categoryLevels.map((levelInfo) => (
              <button
                key={levelInfo.level}
                onClick={() => setSelectedLevel(levelInfo.level)}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  selectedLevel === levelInfo.level
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {levelInfo.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Categories Table */}
        <div className="p-6">
          {loading ? (
            <div className="p-8 text-center">
              <LoadingSpinner />
            </div>
          ) : (
            <DataTable
              columns={columns}
              data={categories}
              actions={actions}
              emptyMessage={`No ${categoryLevels.find(l => l.level === selectedLevel)?.name.toLowerCase()} found. Create your first category to start organizing products.`}
            />
          )}
        </div>
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
              <p className="text-sm font-medium text-gray-600">Total Categories</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total || categories.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Current Level</p>
              <p className="text-2xl font-semibold text-gray-900">{selectedLevel}</p>
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
              <p className="text-sm font-medium text-gray-600">Max Depth</p>
              <p className="text-2xl font-semibold text-gray-900">5</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">SKU Length</p>
              <p className="text-2xl font-semibold text-gray-900">16 chars</p>
            </div>
          </div>
        </div>
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={editingCategory ? "Edit Category" : `Create ${categoryLevels.find(l => l.level === selectedLevel)?.name}`}
        size="large"
      >
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category Name *
            </label>
            <input
              type="text"
              name="category_name"
              value={formData.category_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter category name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-Generated Abbreviation
            </label>
            <input
              type="text"
              name="abbreviation"
              value={formData.abbreviation}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Auto-generated from name"
              maxLength={2}
            />
            <p className="text-xs text-gray-500 mt-1">
              2-digit code auto-generated from category name. Used in SKU generation.
            </p>
          </div>

          {selectedLevel > 1 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Parent Category *
              </label>
              <select
                name="parent_category_id"
                value={formData.parent_category_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select Parent Category</option>
                {getParentCategories().length === 0 ? (
                  <option disabled>No parent categories found</option>
                ) : (
                  getParentCategories().map(category => (
                    <option key={category.id} value={category.id}>
                      {category.category_name} ({category.abbreviation})
                    </option>
                  ))
                )}
              </select>
            </div>
          )}

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">SKU Generation Info</h4>
            <p className="text-xs text-gray-600">
              Each product SKU will be 16 characters composed of abbreviations from all 5 category levels.
              Example: {formData.abbreviation || 'XX'}YYZZ11AABB22 where each pair represents a category level.
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-6 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {editingCategory ? "Update" : "Create"} Category
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ProductCategoriesPage;