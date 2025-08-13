import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const LeadForm = ({ lead, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    company_id: '',
    location: '',
    lead_source: 'Web',
    sales_person_id: '',
    status: 'New',
    notes: '',
    priority: 'Medium',
    expected_close_date: '',
    products: [],
    services: [],
    leadSubType: '',
    tenderDetails: {
      tenderId: '',
      authority: '',
      bidDueDate: ''
    }
  });
  
  const [companies, setCompanies] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (lead) {
      setFormData({
        company_id: lead.company_id || '',
        location: lead.location || '',
        lead_source: lead.lead_source || 'Web',
        sales_person_id: lead.sales_person_id || '',
        status: lead.status || 'New',
        notes: lead.notes || '',
        priority: lead.priority || 'Medium',
        expected_close_date: lead.expected_close_date || '',
        products: lead.products || [],
        services: lead.services || [],
        leadSubType: lead.leadSubType || '',
        tenderDetails: {
          tenderId: lead.tenderDetails?.tenderId || '',
          authority: lead.tenderDetails?.authority || '',
          bidDueDate: lead.tenderDetails?.bidDueDate || ''
        }
      });
    }
    fetchCompanies();
    fetchUsers();
  }, [lead]);

  const fetchCompanies = async () => {
    try {
      const response = await apiRequest('/api/companies');
      if (response.status) {
        setCompanies(response.data.companies || []);
      }
    } catch (err) {
      console.error('Failed to fetch companies:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await apiRequest('/api/users');
      if (response.status) {
        setUsers(response.data.users || []);
      }
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.company_id) {
      newErrors.company_id = 'Company is required';
    }

    if (!formData.sales_person_id) {
      newErrors.sales_person_id = 'Sales person is required';
    }

    if (formData.expected_close_date) {
      const selectedDate = new Date(formData.expected_close_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        newErrors.expected_close_date = 'Expected close date cannot be in the past';
      }
    }

    // Validate that at least one product or service is selected
    if (formData.products.length === 0 && formData.services.length === 0) {
      newErrors.productsServices = 'Please select at least one product or one service';
    }

    // Validate leadSubType is required
    if (!formData.leadSubType) {
      newErrors.leadSubType = 'Lead sub-type is required';
    }

    // Validate tenderDetails if leadSubType is not NON_TENDER
    if (formData.leadSubType && formData.leadSubType !== 'NON_TENDER') {
      if (!formData.tenderDetails.tenderId || formData.tenderDetails.tenderId.trim().length < 2) {
        newErrors.tenderId = 'Tender ID is required (minimum 2 characters)';
      }
      if (!formData.tenderDetails.authority || formData.tenderDetails.authority.trim().length < 2) {
        newErrors.authority = 'Authority is required (minimum 2 characters)';
      }
      if (!formData.tenderDetails.bidDueDate) {
        newErrors.bidDueDate = 'Bid due date is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const endpoint = lead 
        ? `/api/leads/${lead.id}` 
        : '/api/leads';
      const method = lead ? 'PUT' : 'POST';
      
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
    
    // Handle nested tenderDetails fields
    if (name.startsWith('tenderDetails.')) {
      const fieldName = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        tenderDetails: {
          ...prev.tenderDetails,
          [fieldName]: value
        }
      }));
      
      // Clear tender-specific errors
      if (errors[fieldName]) {
        setErrors(prev => ({ ...prev, [fieldName]: '' }));
      }
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
      
      // Clear tenderDetails when switching to NON_TENDER
      if (name === 'leadSubType' && value === 'NON_TENDER') {
        setFormData(prev => ({
          ...prev,
          tenderDetails: {
            tenderId: '',
            authority: '',
            bidDueDate: ''
          }
        }));
        
        // Clear tender-related errors
        setErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.tenderId;
          delete newErrors.authority;
          delete newErrors.bidDueDate;
          return newErrors;
        });
      }
    }
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleMultiSelectChange = (fieldName, option) => {
    setFormData(prev => {
      const currentValues = prev[fieldName] || [];
      const newValues = currentValues.includes(option)
        ? currentValues.filter(item => item !== option)
        : [...currentValues, option];
      
      return { ...prev, [fieldName]: newValues };
    });

    // Clear validation error when user selects products/services
    if ((fieldName === 'products' || fieldName === 'services') && errors.productsServices) {
      setErrors(prev => ({ ...prev, productsServices: '' }));
    }
  };

  const leadSources = [
    { value: 'Web', label: 'Web' },
    { value: 'Partner', label: 'Partner' },
    { value: 'Campaign', label: 'Campaign' },
    { value: 'Referral', label: 'Referral' },
    { value: 'Cold Call', label: 'Cold Call' },
    { value: 'Event', label: 'Event' }
  ];

  const leadStatuses = [
    { value: 'New', label: 'New' },
    { value: 'Contacted', label: 'Contacted' },
    { value: 'Qualified', label: 'Qualified' },
    { value: 'Proposal', label: 'Proposal' },
    { value: 'Negotiation', label: 'Negotiation' },
    { value: 'Closed Won', label: 'Closed Won' },
    { value: 'Closed Lost', label: 'Closed Lost' },
    { value: 'Dropped', label: 'Dropped' }
  ];

  const priorities = [
    { value: 'Low', label: 'Low' },
    { value: 'Medium', label: 'Medium' },
    { value: 'High', label: 'High' },
    { value: 'Urgent', label: 'Urgent' }
  ];

  const productOptions = [
    'CRM Software',
    'ERP Solutions',
    'Marketing Automation',
    'Sales Analytics',
    'Customer Support Platform',
    'Business Intelligence',
    'Project Management Tools',
    'HR Management System',
    'Financial Management',
    'Inventory Management'
  ];

  const serviceOptions = [
    'Implementation Services',
    'Training & Support',
    'Custom Development',
    'Data Migration',
    'System Integration',
    'Consulting Services',
    'Maintenance & Support',
    'Cloud Migration',
    'Security Audit',
    'Performance Optimization'
  ];

  const leadSubTypes = [
    { value: 'TENDER', label: 'Tender' },
    { value: 'NON_TENDER', label: 'Non-Tender' },
    { value: 'PRE_TENDER', label: 'Pre-Tender' },
    { value: 'POST_TENDER', label: 'Post-Tender' }
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
        <h4 className="text-lg font-medium text-gray-900 mb-4">General Details</h4>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter location"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lead Source <span className="text-red-500">*</span>
            </label>
            <select
              name="lead_source"
              required
              value={formData.lead_source}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {leadSources.map(source => (
                <option key={source.value} value={source.value}>{source.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sales Person <span className="text-red-500">*</span>
            </label>
            <select
              name="sales_person_id"
              required
              value={formData.sales_person_id}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.sales_person_id ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Select sales person</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>{user.name}</option>
              ))}
            </select>
            {errors.sales_person_id && <p className="text-red-500 text-sm mt-1">{errors.sales_person_id}</p>}
          </div>
        </div>

        {/* Products and Services Multi-Select */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          {/* Products Multi-Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Products <span className="text-red-500">*</span>
              <span className="text-xs text-gray-500 ml-2">(Select at least one product or service)</span>
            </label>
            <div className={`border rounded-lg p-3 max-h-48 overflow-y-auto ${
              errors.productsServices ? 'border-red-300' : 'border-gray-300'
            }`}>
              {productOptions.map((product) => (
                <label key={product} className="flex items-center space-x-2 py-1 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.products.includes(product)}
                    onChange={() => handleMultiSelectChange('products', product)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{product}</span>
                </label>
              ))}
              {formData.products.length === 0 && (
                <p className="text-gray-500 text-sm italic">No products selected</p>
              )}
            </div>
            {formData.products.length > 0 && (
              <p className="text-xs text-gray-600 mt-1">
                Selected: {formData.products.join(', ')}
              </p>
            )}
          </div>

          {/* Services Multi-Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Services <span className="text-red-500">*</span>
              <span className="text-xs text-gray-500 ml-2">(Select at least one product or service)</span>
            </label>
            <div className={`border rounded-lg p-3 max-h-48 overflow-y-auto ${
              errors.productsServices ? 'border-red-300' : 'border-gray-300'
            }`}>
              {serviceOptions.map((service) => (
                <label key={service} className="flex items-center space-x-2 py-1 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.services.includes(service)}
                    onChange={() => handleMultiSelectChange('services', service)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{service}</span>
                </label>
              ))}
              {formData.services.length === 0 && (
                <p className="text-gray-500 text-sm italic">No services selected</p>
              )}
            </div>
            {formData.services.length > 0 && (
              <p className="text-xs text-gray-600 mt-1">
                Selected: {formData.services.join(', ')}
              </p>
            )}
          </div>
        </div>

        {/* Products/Services Validation Error */}
        {errors.productsServices && (
          <p className="text-red-500 text-sm mt-2">{errors.productsServices}</p>
        )}
      </div>

      {/* Status & Priority */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Status & Priority</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {leadStatuses.map(status => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {priorities.map(priority => (
                <option key={priority.value} value={priority.value}>{priority.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expected Close Date</label>
            <input
              type="date"
              name="expected_close_date"
              value={formData.expected_close_date}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.expected_close_date ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            {errors.expected_close_date && <p className="text-red-500 text-sm mt-1">{errors.expected_close_date}</p>}
          </div>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleInputChange}
          rows="4"
          maxLength="1000"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Additional notes about the lead..."
        />
        <p className="text-xs text-gray-500 mt-1">
          {formData.notes.length}/1000 characters
        </p>
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
          disabled={loading || (formData.products.length === 0 && formData.services.length === 0)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {lead ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            lead ? 'Update Lead' : 'Create Lead'
          )}
        </button>
      </div>
    </form>
  );
};

export default LeadForm;