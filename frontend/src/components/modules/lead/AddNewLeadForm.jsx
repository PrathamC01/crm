import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../utils/api';

const AddNewLeadForm = ({ lead, onSave, onCancel }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    // Tab 1: General Lead Details
    project_title: '',
    lead_source: '',
    lead_sub_type: '',
    tender_sub_type: '',
    products_services: [],
    company_id: '',
    sub_business_type: '',
    end_customer_id: '',
    end_customer_region: '',
    partner_involved: false,
    partners: [],
    
    // Tab 2: Contact Details
    contacts: [],
    
    // Tab 3: Tender Details
    tender_fee: '',
    currency: 'INR',
    submission_type: '',
    tender_authority: '',
    tender_for: '',
    emd_required: false,
    emd_amount: '',
    emd_currency: 'INR',
    bg_required: false,
    bg_amount: '',
    bg_currency: 'INR',
    important_dates: [],
    clauses: [],
    
    // Tab 4: Other Details
    expected_revenue: '',
    revenue_currency: 'INR',
    convert_to_opportunity_date: '',
    competitors: [],
    documents: []
  });

  const [dropdownData, setDropdownData] = useState({
    companies: [],
    products: [],
    partners: [],
    competitors: []
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const tabs = [
    { id: 0, name: 'General Details', icon: '📋', fields: ['project_title', 'lead_source', 'company_id'] },
    { id: 1, name: 'Contact Details', icon: '👥', fields: ['contacts'] },
    { id: 2, name: 'Tender Details', icon: '📄', fields: ['tender_fee', 'tender_authority'] },
    { id: 3, name: 'Other Details', icon: '💰', fields: ['expected_revenue'] }
  ];

  useEffect(() => {
    fetchDropdownData();
    if (lead) {
      setFormData({ ...lead });
    } else {
      // Initialize with default structures
      setFormData(prev => ({
        ...prev,
        important_dates: [
          { label: 'Tender Publish Date', key: 'tender_publish_date', value: '' },
          { label: 'Query Submission Date', key: 'query_submission_date', value: '' },
          { label: 'Pre-Bid Meeting Date', key: 'pre_bid_meeting_date', value: '' },
          { label: 'Tender Submission Date', key: 'tender_submission_date', value: '' },
          { label: 'Technical Opening Date', key: 'technical_opening_date', value: '' },
          { label: 'Presentation Date', key: 'presentation_date', value: '' }
        ]
      }));
    }
  }, [lead]);

  const fetchDropdownData = async () => {
    try {
      const [companiesRes, productsRes] = await Promise.all([
        apiRequest('/api/companies'),
        apiRequest('/api/products')
      ]);

      setDropdownData({
        companies: companiesRes.status ? companiesRes.data.companies || [] : [],
        products: productsRes.status ? productsRes.data.products || [] : [],
        partners: [], // Mock data for now
        competitors: [] // Mock data for now
      });
    } catch (err) {
      console.error('Failed to fetch dropdown data:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateTab = (tabIndex) => {
    const newErrors = {};
    const tab = tabs[tabIndex];
    
    tab.fields.forEach(field => {
      if (field === 'contacts' && formData.contacts.length === 0) {
        newErrors.contacts = 'At least one contact is required';
      } else if (!formData[field] || formData[field] === '') {
        newErrors[field] = `${field.replace('_', ' ')} is required`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleTabChange = (newTab) => {
    if (newTab < activeTab || validateTab(activeTab)) {
      setActiveTab(newTab);
    }
  };

  const handleSubmit = async (isDraft = false) => {
    if (!isDraft && !validateAllTabs()) return;

    setLoading(true);
    try {
      const endpoint = lead ? `/api/leads/${lead.id}` : '/api/leads';
      const method = lead ? 'PUT' : 'POST';
      
      const response = await apiRequest(endpoint, {
        method,
        body: JSON.stringify({ ...formData, status: isDraft ? 'Draft' : 'Active' })
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

  const validateAllTabs = () => {
    let allValid = true;
    tabs.forEach((tab, index) => {
      if (!validateTab(index)) {
        allValid = false;
      }
    });
    return allValid;
  };

  // Tab 1: General Lead Details
  const renderGeneralDetails = () => (
    <div className="space-y-8">
      {/* Lead Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.project_title}
              onChange={(e) => handleInputChange('project_title', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.project_title ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter project title"
            />
            {errors.project_title && <p className="text-red-500 text-sm mt-1">{errors.project_title}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lead Source <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.lead_source}
              onChange={(e) => handleInputChange('lead_source', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.lead_source ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Select Lead Source</option>
              <option value="Direct Marketing">Direct Marketing</option>
              <option value="Referral">Referral</option>
              <option value="Advertisement">Advertisement</option>
              <option value="Event">Event</option>
              <option value="Other">Other</option>
            </select>
            {errors.lead_source && <p className="text-red-500 text-sm mt-1">{errors.lead_source}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lead Sub Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.lead_sub_type}
              onChange={(e) => handleInputChange('lead_sub_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Lead Sub Type</option>
              <option value="Pre-Tender">Pre-Tender</option>
              <option value="Post-Tender">Post-Tender</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tender Sub Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.tender_sub_type}
              onChange={(e) => handleInputChange('tender_sub_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Tender Sub Type</option>
              <option value="GeM Tender">GeM Tender</option>
              <option value="Limited Tender">Limited Tender</option>
              <option value="Open Tender">Open Tender</option>
              <option value="Single Tender">Single Tender</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Products & Services <span className="text-red-500">*</span>
            </label>
            <select
              multiple
              value={formData.products_services}
              onChange={(e) => handleInputChange('products_services', Array.from(e.target.selectedOptions, option => option.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
            >
              <option value="Additional Services: RAM">Additional Services: RAM</option>
              <option value="Hardware Support">Hardware Support</option>
              <option value="Software Services">Software Services</option>
              <option value="Consulting">Consulting</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple options</p>
          </div>
        </div>
      </div>

      {/* Company Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Company Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.company_id}
              onChange={(e) => handleInputChange('company_id', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.company_id ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Select Company</option>
              {dropdownData.companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name} - {company.city}
                </option>
              ))}
            </select>
            {errors.company_id && <p className="text-red-500 text-sm mt-1">{errors.company_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sub Business Type</label>
            <select
              value={formData.sub_business_type}
              onChange={(e) => handleInputChange('sub_business_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Sub Business Type</option>
              <option value="Upgrade">Upgrade</option>
              <option value="Downgrade">Downgrade</option>
              <option value="AMC">AMC</option>
            </select>
          </div>
        </div>
      </div>

      {/* End Customer Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">End Customer / Billing Customer</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Customer <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.end_customer_id}
              onChange={(e) => handleInputChange('end_customer_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select End Customer</option>
              {dropdownData.companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name} - {company.city}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Customer Region</label>
            <select
              value={formData.end_customer_region}
              onChange={(e) => handleInputChange('end_customer_region', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Region</option>
              <option value="North">North</option>
              <option value="South">South</option>
              <option value="East">East</option>
              <option value="West">West</option>
              <option value="Central">Central</option>
            </select>
          </div>
        </div>
      </div>

      {/* Partner Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Partner Details</h3>
        
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.partner_involved}
              onChange={(e) => handleInputChange('partner_involved', e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Partner Involved</span>
          </label>
        </div>

        {formData.partner_involved && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Partner Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">Select Partner Type</option>
                  <option value="Channel">Channel</option>
                  <option value="Reseller">Reseller</option>
                  <option value="Distributor">Distributor</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Partner Name</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">Select Partner</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Billing Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">Select Billing Type</option>
                  <option value="Client Billing">Client Billing</option>
                  <option value="Partner Billing">Partner Billing</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Partner Engagement Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">Select Engagement Type</option>
                  <option value="ORC">ORC</option>
                  <option value="NRC">NRC</option>
                  <option value="AMC">AMC</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expected ORC</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter amount"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Terms</label>
                <textarea
                  rows="2"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter payment terms"
                />
              </div>
            </div>

            <button
              type="button"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Add Partner
            </button>

            {/* Partners Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-300 rounded-lg">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Partner Type</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Engagement Type</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Payment Terms</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Billing Type</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Expected ORC</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {formData.partners.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-4 py-8 text-center text-gray-500">No partners added yet</td>
                    </tr>
                  ) : (
                    formData.partners.map((partner, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2 border-t">{partner.type}</td>
                        <td className="px-4 py-2 border-t">{partner.name}</td>
                        <td className="px-4 py-2 border-t">{partner.engagement_type}</td>
                        <td className="px-4 py-2 border-t">{partner.payment_terms}</td>
                        <td className="px-4 py-2 border-t">{partner.billing_type}</td>
                        <td className="px-4 py-2 border-t">{partner.expected_orc}</td>
                        <td className="px-4 py-2 border-t">
                          <button className="text-red-600 hover:text-red-900 text-sm">Delete</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Tab 2: Contact Details
  const renderContactDetails = () => {
    const addContact = () => {
      const newContact = {
        id: Date.now(),
        designation: '',
        salutation: '',
        first_name: '',
        middle_name: '',
        last_name: '',
        email: '',
        primary_phone: '',
        decision_maker: false,
        decision_maker_percentage: 0,
        comments: ''
      };
      setFormData(prev => ({
        ...prev,
        contacts: [...prev.contacts, newContact]
      }));
    };

    const removeContact = (id) => {
      setFormData(prev => ({
        ...prev,
        contacts: prev.contacts.filter(contact => contact.id !== id)
      }));
    };

    const updateContact = (id, field, value) => {
      setFormData(prev => ({
        ...prev,
        contacts: prev.contacts.map(contact =>
          contact.id === id ? { ...contact, [field]: value } : contact
        )
      }));
    };

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Contact Details</h3>
          <button
            type="button"
            onClick={addContact}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Add Contact
          </button>
        </div>

        {errors.contacts && <p className="text-red-500 text-sm">{errors.contacts}</p>}

        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300 rounded-lg">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sr. No.</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Salutation</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">First Name*</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Middle Name</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Last Name*</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email*</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Phone*</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Decision Maker</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">DM %</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Comments</th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {formData.contacts.length === 0 ? (
                <tr>
                  <td colSpan="12" className="px-4 py-8 text-center text-gray-500">
                    No contacts added yet. Click "Add Contact" to get started.
                  </td>
                </tr>
              ) : (
                formData.contacts.map((contact, index) => (
                  <tr key={contact.id}>
                    <td className="px-2 py-2 border-t text-center">{index + 1}</td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="text"
                        value={contact.designation}
                        onChange={(e) => updateContact(contact.id, 'designation', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Designation"
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <select
                        value={contact.salutation}
                        onChange={(e) => updateContact(contact.id, 'salutation', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="">Select</option>
                        <option value="Mr.">Mr.</option>
                        <option value="Ms.">Ms.</option>
                        <option value="Dr.">Dr.</option>
                        <option value="Prof.">Prof.</option>
                      </select>
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="text"
                        value={contact.first_name}
                        onChange={(e) => updateContact(contact.id, 'first_name', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="First Name"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="text"
                        value={contact.middle_name}
                        onChange={(e) => updateContact(contact.id, 'middle_name', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Middle Name"
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="text"
                        value={contact.last_name}
                        onChange={(e) => updateContact(contact.id, 'last_name', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Last Name"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="email"
                        value={contact.email}
                        onChange={(e) => updateContact(contact.id, 'email', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Email"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="tel"
                        value={contact.primary_phone}
                        onChange={(e) => updateContact(contact.id, 'primary_phone', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Phone"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 border-t text-center">
                      <input
                        type="checkbox"
                        checked={contact.decision_maker}
                        onChange={(e) => updateContact(contact.id, 'decision_maker', e.target.checked)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <input
                        type="number"
                        value={contact.decision_maker_percentage}
                        onChange={(e) => updateContact(contact.id, 'decision_maker_percentage', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        min="0"
                        max="100"
                        disabled={!contact.decision_maker}
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <textarea
                        value={contact.comments}
                        onChange={(e) => updateContact(contact.id, 'comments', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        rows="2"
                        placeholder="Comments"
                      />
                    </td>
                    <td className="px-2 py-2 border-t">
                      <button
                        type="button"
                        onClick={() => removeContact(contact.id)}
                        className="text-red-600 hover:text-red-900 text-sm"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Tab 3: Tender Details
  const renderTenderDetails = () => {
    const addClause = () => {
      const newClause = {
        id: Date.now(),
        clause_type: '',
        criteria_description: ''
      };
      setFormData(prev => ({
        ...prev,
        clauses: [...prev.clauses, newClause]
      }));
    };

    const removeClause = (id) => {
      setFormData(prev => ({
        ...prev,
        clauses: prev.clauses.filter(clause => clause.id !== id)
      }));
    };

    const updateClause = (id, field, value) => {
      setFormData(prev => ({
        ...prev,
        clauses: prev.clauses.map(clause =>
          clause.id === id ? { ...clause, [field]: value } : clause
        )
      }));
    };

    const updateImportantDate = (key, value) => {
      setFormData(prev => ({
        ...prev,
        important_dates: prev.important_dates.map(date =>
          date.key === key ? { ...date, value } : date
        )
      }));
    };

    return (
      <div className="space-y-8">
        {/* Tender Information Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Tender Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tender Fee <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.tender_fee}
                onChange={(e) => handleInputChange('tender_fee', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.tender_fee ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter tender fee"
              />
              {errors.tender_fee && <p className="text-red-500 text-sm mt-1">{errors.tender_fee}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Currency <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.currency}
                onChange={(e) => handleInputChange('currency', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Submission Type</label>
              <select
                value={formData.submission_type}
                onChange={(e) => handleInputChange('submission_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Submission Type</option>
                <option value="Online">Online</option>
                <option value="Offline">Offline</option>
                <option value="Both">Both</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tender Authority <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.tender_authority}
                onChange={(e) => handleInputChange('tender_authority', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.tender_authority ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter tender authority"
              />
              {errors.tender_authority && <p className="text-red-500 text-sm mt-1">{errors.tender_authority}</p>}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tender For <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.tender_for}
                onChange={(e) => handleInputChange('tender_for', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter what the tender is for"
              />
            </div>

            {/* EMD Section */}
            <div>
              <label className="flex items-center mb-2">
                <input
                  type="checkbox"
                  checked={formData.emd_required}
                  onChange={(e) => handleInputChange('emd_required', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-700">EMD Required</span>
              </label>
              {formData.emd_required && (
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    value={formData.emd_amount}
                    onChange={(e) => handleInputChange('emd_amount', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="EMD Amount"
                  />
                  <select
                    value={formData.emd_currency}
                    onChange={(e) => handleInputChange('emd_currency', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="INR">INR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>
              )}
            </div>

            {/* BG Section */}
            <div>
              <label className="flex items-center mb-2">
                <input
                  type="checkbox"
                  checked={formData.bg_required}
                  onChange={(e) => handleInputChange('bg_required', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-700">BG Required</span>
              </label>
              {formData.bg_required && (
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    value={formData.bg_amount}
                    onChange={(e) => handleInputChange('bg_amount', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="BG Amount"
                  />
                  <select
                    value={formData.bg_currency}
                    onChange={(e) => handleInputChange('bg_currency', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="INR">INR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Important Dates Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Important Dates</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {formData.important_dates.map((dateItem) => (
              <div key={dateItem.key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {dateItem.label}
                </label>
                <input
                  type="date"
                  value={dateItem.value}
                  onChange={(e) => updateImportantDate(dateItem.key, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Clauses Details Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Clauses Details</h3>
            <button
              type="button"
              onClick={addClause}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Add Clause
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clause Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Criteria Description</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.clauses.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="px-4 py-8 text-center text-gray-500">No clauses added yet</td>
                  </tr>
                ) : (
                  formData.clauses.map((clause) => (
                    <tr key={clause.id}>
                      <td className="px-4 py-2 border-t">
                        <input
                          type="text"
                          value={clause.clause_type}
                          onChange={(e) => updateClause(clause.id, 'clause_type', e.target.value)}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                          placeholder="Enter clause type"
                        />
                      </td>
                      <td className="px-4 py-2 border-t">
                        <textarea
                          value={clause.criteria_description}
                          onChange={(e) => updateClause(clause.id, 'criteria_description', e.target.value)}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                          rows="2"
                          placeholder="Enter criteria description"
                        />
                      </td>
                      <td className="px-4 py-2 border-t">
                        <button
                          type="button"
                          onClick={() => removeClause(clause.id)}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // Tab 4: Other Details
  const renderOtherDetails = () => {
    const addCompetitor = () => {
      const competitor = prompt('Enter competitor name:');
      const description = prompt('Enter description:');
      
      if (competitor) {
        const newCompetitor = {
          id: Date.now(),
          name: competitor,
          description: description || ''
        };
        setFormData(prev => ({
          ...prev,
          competitors: [...prev.competitors, newCompetitor]
        }));
      }
    };

    const addDocument = () => {
      // This would typically handle file upload
      console.log('Document upload functionality would be implemented here');
    };

    return (
      <div className="space-y-8">
        {/* Revenue Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expected Revenue <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.expected_revenue}
                onChange={(e) => handleInputChange('expected_revenue', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.expected_revenue ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter expected revenue"
              />
              {errors.expected_revenue && <p className="text-red-500 text-sm mt-1">{errors.expected_revenue}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Currency <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.revenue_currency}
                onChange={(e) => handleInputChange('revenue_currency', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Convert to Opportunity Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.convert_to_opportunity_date}
                onChange={(e) => handleInputChange('convert_to_opportunity_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Competitor Info Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Competitor Information</h3>
            <button
              type="button"
              onClick={addCompetitor}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Add Competitor
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Competitor Name</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.competitors.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="px-4 py-8 text-center text-gray-500">No competitors added yet</td>
                  </tr>
                ) : (
                  formData.competitors.map((competitor) => (
                    <tr key={competitor.id}>
                      <td className="px-4 py-2 border-t">{competitor.name}</td>
                      <td className="px-4 py-2 border-t">{competitor.description}</td>
                      <td className="px-4 py-2 border-t">
                        <button
                          type="button"
                          onClick={() => setFormData(prev => ({
                            ...prev,
                            competitors: prev.competitors.filter(c => c.id !== competitor.id)
                          }))}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Upload Documents Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Upload Documents</h3>
            <button
              type="button"
              onClick={addDocument}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Upload Document
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="">Select Document Type</option>
                <option value="Tender Document">Tender Document</option>
                <option value="Technical Specification">Technical Specification</option>
                <option value="Commercial Terms">Commercial Terms</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quotation Name</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter quotation name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Upload File</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.jpg,.png,.xls,.xlsx,.zip,.eml,.msg"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Max size: 10 MB. Accepted: pdf, doc, docx, jpg, png, xls, xlsx, zip, eml, msg</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter document description"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Document Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Document Name</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.documents.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-4 py-8 text-center text-gray-500">No documents uploaded yet</td>
                  </tr>
                ) : (
                  formData.documents.map((document, index) => (
                    <tr key={index}>
                      <td className="px-4 py-2 border-t">{document.type}</td>
                      <td className="px-4 py-2 border-t">{document.name}</td>
                      <td className="px-4 py-2 border-t">{document.description}</td>
                      <td className="px-4 py-2 border-t">
                        <button className="text-red-600 hover:text-red-900 text-sm">Remove</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 0: return renderGeneralDetails();
      case 1: return renderContactDetails();
      case 2: return renderTenderDetails();
      case 3: return renderOtherDetails();
      default: return renderGeneralDetails();
    }
  };

  return (
    <div className="max-w-7xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">
          {lead ? 'Edit Lead' : 'Add New Lead'}
        </h2>
      </div>

      {/* Tab Navigation with Progress Indicators */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex space-x-8">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(index)}
              className={`flex items-center space-x-2 py-2 px-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === index
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
              {index < activeTab && (
                <span className="text-green-500">✓</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="px-6 py-6">
        {errors.submit && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {errors.submit}
          </div>
        )}
        
        {renderTabContent()}
      </div>

      {/* Footer Buttons */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between items-center">
        <div className="flex space-x-3">
          {activeTab > 0 && (
            <button
              type="button"
              onClick={() => setActiveTab(activeTab - 1)}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Previous
            </button>
          )}
        </div>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
          
          <button
            type="button"
            onClick={() => handleSubmit(true)}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-yellow-200 rounded-lg hover:bg-yellow-300 disabled:opacity-50 transition-colors"
          >
            Save as Draft
          </button>

          {activeTab < tabs.length - 1 ? (
            <button
              type="button"
              onClick={() => handleTabChange(activeTab + 1)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={() => handleSubmit(false)}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Submitting...
                </div>
              ) : (
                'Submit'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddNewLeadForm;