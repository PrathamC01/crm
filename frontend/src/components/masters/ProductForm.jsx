import React, { useState } from 'react';

const ProductForm = ({ product, uoms, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    cat1_type: product?.cat1_type || 'product',
    cat2_category: product?.cat2_category || '',
    cat3_sub_category: product?.cat3_sub_category || '',
    cat4_oem: product?.cat4_oem || '',
    cat5_configuration: product?.cat5_configuration || {},
    description: product?.description || '',
    uom_ids: product?.uoms?.map(uom => uom.uom_id) || []
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleUOMChange = (uomId) => {
    setFormData(prev => ({
      ...prev,
      uom_ids: prev.uom_ids.includes(uomId)
        ? prev.uom_ids.filter(id => id !== uomId)
        : [...prev.uom_ids, uomId]
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.cat2_category.trim()) {
      newErrors.cat2_category = 'Category is required';
    }
    if (!formData.cat3_sub_category.trim()) {
      newErrors.cat3_sub_category = 'Sub Category is required';
    }
    if (formData.uom_ids.length === 0) {
      newErrors.uom_ids = 'At least one UOM must be selected';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Product Name */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700">
            Product Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Auto-generated from categories if empty"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">Leave empty to auto-generate from categories</p>
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Type *
          </label>
          <select
            name="cat1_type"
            value={formData.cat1_type}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="product">Product</option>
            <option value="service">Service</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Category *
          </label>
          <input
            type="text"
            name="cat2_category"
            value={formData.cat2_category}
            onChange={handleChange}
            placeholder="e.g., Security, Infrastructure"
            className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
              errors.cat2_category ? 'border-red-500' : ''
            }`}
          />
          {errors.cat2_category && (
            <p className="mt-1 text-sm text-red-600">{errors.cat2_category}</p>
          )}
        </div>

        {/* Sub Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Sub Category *
          </label>
          <input
            type="text"
            name="cat3_sub_category"
            value={formData.cat3_sub_category}
            onChange={handleChange}
            placeholder="e.g., Firewall, WAF"
            className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
              errors.cat3_sub_category ? 'border-red-500' : ''
            }`}
          />
          {errors.cat3_sub_category && (
            <p className="mt-1 text-sm text-red-600">{errors.cat3_sub_category}</p>
          )}
        </div>

        {/* OEM */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            OEM
          </label>
          <input
            type="text"
            name="cat4_oem"
            value={formData.cat4_oem}
            onChange={handleChange}
            placeholder="e.g., Cisco, Dell, Microsoft"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          placeholder="Product description..."
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* UOMs Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Units of Measure * (Select at least one)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-40 overflow-y-auto border border-gray-300 rounded-md p-3">
          {uoms.map((uom) => (
            <label key={uom.id} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.uom_ids.includes(uom.id)}
                onChange={() => handleUOMChange(uom.id)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                {uom.uom_name} ({uom.uom_code})
              </span>
            </label>
          ))}
        </div>
        {errors.uom_ids && (
          <p className="mt-1 text-sm text-red-600">{errors.uom_ids}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">First selected UOM will be primary</p>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {product ? 'Update Product' : 'Create Product'}
        </button>
      </div>
    </form>
  );
};

export default ProductForm;