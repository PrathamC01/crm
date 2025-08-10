import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';

const LeadForm = ({ lead = null, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    project_title: '',
    company_name: '',
    company_id: '',
    end_customer_id: '',
    lead_source: 'Direct Marketing',
    lead_sub_type: 'Business',
    tender_sub_type: 'B2B',
    status: 'New',
    priority: 'Medium',
    expected_revenue: '',
    revenue_currency: 'INR',
    expected_closure_date: '',
    description: '',
    remarks: ''
  });

  const [companies, setCompanies] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const leadSourceOptions = [
    'Direct Marketing',
    'Referral', 
    'Advertisement',
    'Event',
    'Other'
  ];

  const leadSubTypeOptions = [
    'Business',
    'Technical',
    'Commercial'
  ];

  const tenderSubTypeOptions = [
    'B2B',
    'B2C',
    'Government',
    'Enterprise'
  ];

  const statusOptions = [
    'New',
    'Active', 
    'Contacted',
    'Qualified',
    'Unqualified',
    'Converted',
    'Rejected'
  ];

  const priorityOptions = [
    'Low',
    'Medium',
    'High',
    'Urgent'
  ];

  useEffect(() => {
    fetchCompanies();
    fetchContacts();
    
    // If editing, populate form
    if (lead) {
      setFormData({
        project_title: lead.project_title || '',
        company_name: lead.company_name || '',
        company_id: lead.company_id || '',
        end_customer_id: lead.end_customer_id || '',
        lead_source: lead.lead_source || 'Direct Marketing',
        lead_sub_type: lead.lead_sub_type || 'Business',
        tender_sub_type: lead.tender_sub_type || 'B2B',
        status: lead.status || 'New',
        priority: lead.priority || 'Medium',
        expected_revenue: lead.expected_revenue || '',
        revenue_currency: lead.revenue_currency || 'INR',
        expected_closure_date: lead.expected_closure_date ? lead.expected_closure_date.split('T')[0] : '',
        description: lead.description || '',
        remarks: lead.remarks || ''
      });
    }
  }, [lead]);

  const fetchCompanies = async () => {
    try {
      const response = await apiMethods.companies.getCompanies();
      if (response.data?.data?.companies) {
        setCompanies(response.data.data.companies);
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  };

  const fetchContacts = async () => {
    try {
      const response = await apiMethods.contacts.getContacts();
      if (response.data?.data?.contacts) {
        setContacts(response.data.data.contacts);
      }
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };

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
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.project_title.trim()) {
      newErrors.project_title = 'Project title is required';
    }
    
    if (!formData.company_id) {
      newErrors.company_id = 'Please select a company';
    }
    
    if (!formData.end_customer_id) {
      newErrors.end_customer_id = 'Please select an end customer contact';
    }
    
    if (!formData.expected_revenue || parseFloat(formData.expected_revenue) <= 0) {
      newErrors.expected_revenue = 'Please enter a valid expected revenue';
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
      const leadData = {
        ...formData,
        expected_revenue: parseFloat(formData.expected_revenue),
        expected_closure_date: formData.expected_closure_date || null
      };

      let response;
      if (lead) {
        // Edit existing lead
        response = await apiMethods.leads.updateLead(lead.id, leadData);
      } else {
        // Create new lead
        response = await apiMethods.leads.createLead(leadData);
      }

      if (response.data?.status) {
        onSave && onSave(response.data.data);
      } else {
        throw new Error(response.data?.message || 'Failed to save lead');
      }
    } catch (error) {
      console.error('Error saving lead:', error);
      // Handle validation errors from backend
      if (error.response?.data?.error && typeof error.response.data.error === 'object') {
        setErrors(error.response.data.error);
      } else {
        setErrors({ submit: error.response?.data?.message || error.message || 'Failed to save lead' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {errors.submit}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Project Title */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project Title *
          </label>
          <input
            type="text"
            name="project_title"
            value={formData.project_title}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.project_title ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter project title"
          />
          {errors.project_title && (
            <p className="text-red-500 text-sm mt-1">{errors.project_title}</p>
          )}
        </div>

        {/* Company */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company *
          </label>
          <select
            name="company_id"
            value={formData.company_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.company_id ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select Company</option>
            {companies.length === 0 ? (
              <option disabled>No companies found</option>
            ) : (
              companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))
            )}
          </select>
          {errors.company_id && (
            <p className="text-red-500 text-sm mt-1">{errors.company_id}</p>
          )}
        </div>

        {/* End Customer Contact */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End Customer Contact *
          </label>
          <select
            name="end_customer_id"
            value={formData.end_customer_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.end_customer_id ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select Contact</option>
            {contacts.length === 0 ? (
              <option disabled>No contacts found</option>
            ) : (
              contacts.map(contact => (
                <option key={contact.id} value={contact.id}>
                  {contact.full_name} ({contact.company_name})
                </option>
              ))
            )}
          </select>
          {errors.end_customer_id && (
            <p className="text-red-500 text-sm mt-1">{errors.end_customer_id}</p>
          )}
        </div>

        {/* Lead Source */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lead Source
          </label>
          <select
            name="lead_source"
            value={formData.lead_source}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {leadSourceOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Lead Sub Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lead Sub Type
          </label>
          <select
            name="lead_sub_type"
            value={formData.lead_sub_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {leadSubTypeOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Tender Sub Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tender Sub Type
          </label>
          <select
            name="tender_sub_type"
            value={formData.tender_sub_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {tenderSubTypeOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {statusOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Priority
          </label>
          <select
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {priorityOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Expected Revenue */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expected Revenue *
          </label>
          <input
            type="number"
            name="expected_revenue"
            value={formData.expected_revenue}
            onChange={handleChange}
            min="0"
            step="0.01"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.expected_revenue ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter expected revenue"
          />
          {errors.expected_revenue && (
            <p className="text-red-500 text-sm mt-1">{errors.expected_revenue}</p>
          )}
        </div>

        {/* Expected Closure Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expected Closure Date
          </label>
          <input
            type="date"
            name="expected_closure_date"
            value={formData.expected_closure_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter project description"
          />
        </div>

        {/* Remarks */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Remarks
          </label>
          <textarea
            name="remarks"
            value={formData.remarks}
            onChange={handleChange}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Additional remarks"
          />
        </div>
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
          {loading ? 'Saving...' : (lead ? 'Update Lead' : 'Create Lead')}
        </button>
      </div>
    </form>
  );
};

export default LeadForm;