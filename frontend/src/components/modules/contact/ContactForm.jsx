import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const ContactForm = ({ contact, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    designation: '',
    email: '',
    phone_number: '',
    company_id: '',
    role_type: 'Influencer',
    business_card_file: null
  });
  
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (contact) {
      setFormData({
        full_name: contact.full_name || '',
        designation: contact.designation || '',
        email: contact.email || '',
        phone_number: contact.phone_number || '',
        company_id: contact.company_id || '',
        role_type: contact.role_type || 'Influencer',
        business_card_file: null
      });
    }
    fetchCompanies();
  }, [contact]);

  const fetchCompanies = async () => {
    try {
      const response = await apiRequest('/api/companies?limit=1000');
      if (response.status) {
        setCompanies(response.data.companies || []);
      }
    } catch (err) {
      console.error('Failed to fetch companies:', err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.company_id) {
      newErrors.company_id = 'Company is required';
    }

    if (formData.phone_number && !/^(\+91|91)?[-.\s]?[6-9]\d{9}$/.test(formData.phone_number.replace(/\s+/g, ''))) {
      newErrors.phone_number = 'Invalid phone number format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const endpoint = contact 
        ? `/api/contacts/${contact.id}` 
        : '/api/contacts';
      const method = contact ? 'PUT' : 'POST';
      
      const response = await apiRequest(endpoint, {
        method,
        body: JSON.stringify(formData)
      });

      if (response.status) {
        onSave(response.data);
      } else {
        setErrors({ submit: response.message || 'Operation failed' });
      }
    } catch (err) {
      setErrors({ submit: 'Network error occurred' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const roleTypes = [
    { value: 'Admin', label: 'Admin' },
    { value: 'Influencer', label: 'Influencer' },
    { value: 'Decision Maker', label: 'Decision Maker' }
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {errors.submit}
        </div>
      )}

      {/* Basic Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="full_name"
              required
              value={formData.full_name}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.full_name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter full name"
            />
            {errors.full_name && <p className="text-red-500 text-sm mt-1">{errors.full_name}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Designation</label>
            <input
              type="text"
              name="designation"
              value={formData.designation}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter designation"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.email ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter email address"
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.phone_number ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="+91-9876543210"
            />
            {errors.phone_number && <p className="text-red-500 text-sm mt-1">{errors.phone_number}</p>}
          </div>
        </div>
      </div>

      {/* Company & Role Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Company & Role</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company <span className="text-red-500">*</span>
            </label>
            <select
              name="company_id"
              required
              value={formData.company_id}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.company_id ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Select a company</option>
              {companies.map(company => (
                <option key={company.id} value={company.id}>{company.name}</option>
              ))}
            </select>
            {errors.company_id && <p className="text-red-500 text-sm mt-1">{errors.company_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role Type <span className="text-red-500">*</span>
            </label>
            <select
              name="role_type"
              required
              value={formData.role_type}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {roleTypes.map(role => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Decision Makers can be linked to opportunities
            </p>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {contact ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            contact ? 'Update Contact' : 'Create Contact'
          )}
        </button>
      </div>
    </form>
  );
};

export default ContactForm;