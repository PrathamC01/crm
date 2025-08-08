import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const LeadConversionModal = ({ lead, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    contact_id: '',
    opportunity_name: '',
    amount: '',
    justification: '',
    stage: 'L1_Prospect',
    notes: ''
  });
  
  const [decisionMakers, setDecisionMakers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (lead) {
      setFormData(prev => ({
        ...prev,
        opportunity_name: `${lead.company_name} Opportunity`
      }));
      fetchDecisionMakers();
    }
  }, [lead]);

  const fetchDecisionMakers = async () => {
    try {
      const response = await apiRequest(`/api/contacts/company/${lead.company_id}/decision-makers`);
      if (response.status) {
        setDecisionMakers(response.data.decision_makers || []);
      }
    } catch (err) {
      console.error('Failed to fetch decision makers:', err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.contact_id) {
      newErrors.contact_id = 'Decision maker contact is required';
    }

    if (!formData.opportunity_name.trim()) {
      newErrors.opportunity_name = 'Opportunity name is required';
    }

    if (formData.amount) {
      const amount = parseFloat(formData.amount);
      if (isNaN(amount) || amount < 0) {
        newErrors.amount = 'Amount must be a valid positive number';
      } else if (amount >= 1000000 && !formData.justification.trim()) {
        newErrors.justification = 'Justification required for amounts ≥₹10L';
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
      const response = await apiRequest(`/api/leads/${lead.id}/convert`, {
        method: 'POST',
        body: JSON.stringify(formData)
      });

      if (response.status) {
        onSuccess();
      } else {
        setErrors({ submit: response.message || 'Conversion failed' });
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

  const opportunityStages = [
    { value: 'L1_Prospect', label: 'L1 - Prospect' },
    { value: 'L1_Qualification', label: 'L1 - Initial' },
    { value: 'L2_Need_Analysis', label: 'L2 - Qualified' },
    { value: 'L3_Proposal', label: 'L3 - Needs Analysis' },
    { value: 'L4_Negotiation', label: 'L4 - Proposal' },
    { value: 'L5_Won', label: 'L5 - Negotiation' },
    { value: 'L6_Lost', label: 'L6 - Decision' },
    { value: 'L7_Dropped', label: 'L7 - Closing' }
  ];

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Convert Lead to Opportunity
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          {/* Lead Info */}
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h4 className="font-medium text-blue-900">Lead Information</h4>
            <p className="text-blue-700">Company: {lead?.company_name}</p>
            <p className="text-blue-700">Status: {lead?.status}</p>
          </div>

          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {errors.submit}
            </div>
          )}

          {decisionMakers.length === 0 && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg mb-4">
              <p className="font-medium">No Decision Makers Found</p>
              <p className="text-sm">Please create a Decision Maker contact for this company before converting the lead.</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Contact Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Decision Maker Contact <span className="text-red-500">*</span>
              </label>
              <select
                name="contact_id"
                required
                value={formData.contact_id}
                onChange={handleInputChange}
                disabled={decisionMakers.length === 0}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.contact_id ? 'border-red-300' : 'border-gray-300'
                } ${decisionMakers.length === 0 ? 'bg-gray-100' : ''}`}
              >
                <option value="">Select decision maker</option>
                {decisionMakers.map(contact => (
                  <option key={contact.id} value={contact.id}>
                    {contact.full_name} - {contact.designation} ({contact.email})
                  </option>
                ))}
              </select>
              {errors.contact_id && <p className="text-red-500 text-sm mt-1">{errors.contact_id}</p>}
            </div>

            {/* Opportunity Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Opportunity Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="opportunity_name"
                  required
                  value={formData.opportunity_name}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                    errors.opportunity_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Enter opportunity name"
                />
                {errors.opportunity_name && <p className="text-red-500 text-sm mt-1">{errors.opportunity_name}</p>}
              </div>

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
            </div>

            {/* Amount */}
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
                rows="3"
                value={formData.notes}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Additional notes..."
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || decisionMakers.length === 0}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Converting...
                  </div>
                ) : (
                  'Convert to Opportunity'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LeadConversionModal;