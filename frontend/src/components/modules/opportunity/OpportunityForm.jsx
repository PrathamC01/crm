import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const OpportunityForm = ({ opportunity, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    lead_id: '',
    company_id: '',
    contact_id: '',
    name: '',
    stage: 'L1',
    amount: '',
    scoring: 0,
    costing: '',
    status: 'Open',
    justification: '',
    close_date: '',
    probability: 10,
    notes: ''
  });
  
  const [leads, setLeads] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [decisionMakers, setDecisionMakers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (opportunity) {
      setFormData({
        lead_id: opportunity.lead_id || '',
        company_id: opportunity.company_id || '',
        contact_id: opportunity.contact_id || '',
        name: opportunity.name || '',
        stage: opportunity.stage || 'L1',
        amount: opportunity.amount || '',
        scoring: opportunity.scoring || 0,
        costing: opportunity.costing || '',
        status: opportunity.status || 'Open',
        justification: opportunity.justification || '',
        close_date: opportunity.close_date || '',
        probability: opportunity.probability || 10,
        notes: opportunity.notes || ''
      });
    }
    fetchLeads();
    fetchCompanies();
  }, [opportunity]);

  useEffect(() => {
    if (formData.company_id) {
      fetchDecisionMakers(formData.company_id);
    }
  }, [formData.company_id]);

  const fetchLeads = async () => {
    try {
      const response = await apiRequest('/api/leads&status=Qualified');
      if (response.status) {
        setLeads(response.data.leads || []);
      }
    } catch (err) {
      console.error('Failed to fetch leads:', err);
    }
  };

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

  const fetchDecisionMakers = async (companyId) => {
    try {
      const response = await apiRequest(`/api/contacts/company/${companyId}/decision-makers`);
      if (response.status) {
        setDecisionMakers(response.data.decision_makers || []);
      }
    } catch (err) {
      console.error('Failed to fetch decision makers:', err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Opportunity name is required';
    }

    if (!formData.company_id) {
      newErrors.company_id = 'Company is required';
    }

    if (!formData.contact_id) {
      newErrors.contact_id = 'Decision maker contact is required';
    }

    if (formData.amount) {
      const amount = parseFloat(formData.amount);
      if (isNaN(amount) || amount < 0) {
        newErrors.amount = 'Amount must be a valid positive number';
      } else if (amount >= 1000000 && !formData.justification.trim()) {
        newErrors.justification = 'Justification required for amounts ≥₹10L';
      }
    }

    if (formData.costing) {
      const costing = parseFloat(formData.costing);
      if (isNaN(costing) || costing < 0) {
        newErrors.costing = 'Costing must be a valid positive number';
      }
    }

    if (formData.scoring < 0 || formData.scoring > 100) {
      newErrors.scoring = 'Scoring must be between 0 and 100';
    }

    if (formData.probability < 0 || formData.probability > 100) {
      newErrors.probability = 'Probability must be between 0 and 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const endpoint = opportunity 
        ? `/api/opportunities/${opportunity.id}` 
        : '/api/opportunities';
      const method = opportunity ? 'PUT' : 'POST';
      
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

  const handleLeadSelect = (leadId) => {
    const selectedLead = leads.find(lead => lead.id === leadId);
    if (selectedLead) {
      setFormData(prev => ({
        ...prev,
        lead_id: leadId,
        company_id: selectedLead.company_id || '',
        name: `${selectedLead.company_name} Opportunity`
      }));
    }
  };

  const opportunityStages = [
    { value: 'L1', label: 'L1 - Initial' },
    { value: 'L2', label: 'L2 - Qualified' },
    { value: 'L3', label: 'L3 - Needs Analysis' },
    { value: 'L4', label: 'L4 - Proposal' },
    { value: 'L5', label: 'L5 - Negotiation' },
    { value: 'L6', label: 'L6 - Decision' },
    { value: 'L7', label: 'L7 - Closing' }
  ];

  const opportunityStatuses = [
    { value: 'Open', label: 'Open' },
    { value: 'Won', label: 'Won' },
    { value: 'Lost', label: 'Lost' },
    { value: 'Dropped', label: 'Dropped' }
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
        <h4 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Source Lead</label>
            <select
              name="lead_id"
              value={formData.lead_id}
              onChange={(e) => handleLeadSelect(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select source lead (optional)</option>
              {leads.map(lead => (
                <option key={lead.id} value={lead.id}>
                  {lead.company_name} - {lead.lead_source}
                </option>
              ))}
            </select>
          </div>

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
              Opportunity Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter opportunity name"
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Decision Maker Contact <span className="text-red-500">*</span>
            </label>
            <select
              name="contact_id"
              required
              value={formData.contact_id}
              onChange={handleInputChange}
              disabled={!formData.company_id}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.contact_id ? 'border-red-300' : 'border-gray-300'
              } ${!formData.company_id ? 'bg-gray-100' : ''}`}
            >
              <option value="">Select decision maker</option>
              {decisionMakers.map(contact => (
                <option key={contact.id} value={contact.id}>
                  {contact.full_name} - {contact.designation}
                </option>
              ))}
            </select>
            {errors.contact_id && <p className="text-red-500 text-sm mt-1">{errors.contact_id}</p>}
            {formData.company_id && decisionMakers.length === 0 && (
              <p className="text-yellow-600 text-sm mt-1">No decision makers found for this company</p>
            )}
          </div>
        </div>
      </div>

      {/* Stage & Status */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Stage & Status</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Stage</label>
            <select
              name="stage"
              value={formData.stage}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {opportunityStages.map(stage => (
                <option key={stage.value} value={stage.value}>{stage.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {opportunityStatuses.map(status => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Close Date</label>
            <input
              type="date"
              name="close_date"
              value={formData.close_date}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Financial Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Financial Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹)</label>
            <input
              type="number"
              name="amount"
              min="0"
              step="0.01"
              value={formData.amount}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.amount ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter amount"
            />
            {errors.amount && <p className="text-red-500 text-sm mt-1">{errors.amount}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Costing (₹)</label>
            <input
              type="number"
              name="costing"
              min="0"
              step="0.01"
              value={formData.costing}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.costing ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter costing"
            />
            {errors.costing && <p className="text-red-500 text-sm mt-1">{errors.costing}</p>}
          </div>
        </div>
      </div>

      {/* Scoring & Probability */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Scoring & Probability</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scoring (0-100) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="scoring"
              min="0"
              max="100"
              required
              value={formData.scoring}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.scoring ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            {errors.scoring && <p className="text-red-500 text-sm mt-1">{errors.scoring}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Probability (%) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="probability"
              min="0"
              max="100"
              required
              value={formData.probability}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.probability ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            {errors.probability && <p className="text-red-500 text-sm mt-1">{errors.probability}</p>}
          </div>
        </div>
      </div>

      {/* Justification */}
      {parseFloat(formData.amount || 0) >= 1000000 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Justification <span className="text-red-500">*</span>
          </label>
          <textarea
            name="justification"
            required
            rows="3"
            value={formData.justification}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.justification ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Justification required for amounts ≥₹10L"
          />
          {errors.justification && <p className="text-red-500 text-sm mt-1">{errors.justification}</p>}
        </div>
      )}

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          name="notes"
          rows="4"
          value={formData.notes}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Additional notes about the opportunity..."
        />
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
              {opportunity ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            opportunity ? 'Update Opportunity' : 'Create Opportunity'
          )}
        </button>
      </div>
    </form>
  );
};

export default OpportunityForm;