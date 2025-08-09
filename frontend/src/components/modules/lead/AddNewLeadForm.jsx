import React, { useState, useEffect } from "react";
import { apiRequest } from "../../../utils/api";

const AddNewLeadForm = ({ lead, onSave, onCancel }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    // Tab 1: General Lead Details - Lead Details Section
    project_title: "",
    lead_source: "",
    lead_sub_type: "",
    tender_sub_type: "",
    products_services: [],
    
    // Company Details Section
    company_id: "",
    sub_business_type: "",
    
    // End Customer Section
    end_customer_id: "",
    end_customer_region: "",
    
    // Partner Details Section
    partner_involved: false,
    partner_type: "",
    partner_name: "",
    billing_type: "",
    payment_terms: "",
    partner_engagement_type: "",
    expected_orc: 0,
    partners_data: [], // Table data for added partners

    // Tab 2: Contact Details
    contacts: [],

    // Tab 3: Tender Details - Tender Info Section
    tender_fee: 0,
    currency: "INR",
    submission_type: "",
    tender_authority: "",
    tender_for: "",
    emd_required: false,
    emd_amount: 0,
    emd_currency: "INR",
    bg_required: false,
    bg_amount: 0,
    bg_currency: "INR",
    
    // Important Dates Section
    important_dates: [
      { label: "Tender Publish Date", key: "tender_publish_date", value: "" },
      { label: "Query Submission Date", key: "query_submission_date", value: "" },
      { label: "Pre-Bid Meeting Date", key: "pre_bid_meeting_date", value: "" },
      { label: "Tender Submission Date", key: "tender_submission_date", value: "" },
      { label: "Technical Opening Date", key: "technical_opening_date", value: "" },
      { label: "Presentation Date", key: "presentation_date", value: "" },
    ],
    
    // Clauses Section
    clauses: [],

    // Tab 4: Other Details
    expected_revenue: 0,
    revenue_currency: "INR",
    convert_to_opportunity_date: "",
    
    // Competitors Section
    competitor: "",
    competitor_description: "",
    competitors: [],
    
    // Upload Documents Section
    document_type: "",
    quotation_name: "",
    document_description: "",
    documents: [],
    
    // Additional fields
    status: "New",
    priority: "Medium",
    qualification_notes: "",
    lead_score: 0,
  });

  const [dropdownData, setDropdownData] = useState({
    companies: [],
    products: [],
    partners: [],
    competitors: [],
    documentTypes: [
      "Quotation", "Proposal", "Technical Specification", "Brochure", 
      "Certificate", "Reference", "Other"
    ]
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const tabs = [
    {
      id: 0,
      name: "General Lead Details",
      icon: "📋",
      fields: ["project_title", "lead_source", "company_id", "end_customer_id"],
    },
    { 
      id: 1, 
      name: "Contact Details", 
      icon: "👥", 
      fields: ["contacts"] 
    },
    {
      id: 2,
      name: "Tender Details",
      icon: "📄",
      fields: ["tender_fee", "tender_authority", "tender_for"],
    },
    { 
      id: 3, 
      name: "Other Details", 
      icon: "💰", 
      fields: ["expected_revenue", "convert_to_opportunity_date"] 
    },
  ];

  // Dropdown Options
  const LEAD_STATUS_OPTIONS = [
    { value: "New", label: "New" },
    { value: "Contacted", label: "Contacted" },
    { value: "Qualified", label: "Qualified" },
    { value: "Unqualified", label: "Unqualified" },
    { value: "Converted", label: "Converted" },
    { value: "Rejected", label: "Rejected" }
  ];

  const PRIORITY_OPTIONS = [
    { value: "High", label: "High" },
    { value: "Medium", label: "Medium" },
    { value: "Low", label: "Low" }
  ];

  const PRODUCTS_SERVICES = [
    "Hardware Support", "Software Support", "Cloud Services", "Consulting", 
    "Additional Services: RAM", "Additional Services: Storage", "AMC", "Installation"
  ];

  const PARTNER_TYPES = ["Channel", "Reseller", "Distributor"];
  const ENGAGEMENT_TYPES = ["ORC", "NRC", "AMC"];
  const BILLING_TYPES = ["Client Billing", "Partner Billing"];
  const CURRENCY_OPTIONS = ["INR", "USD", "EUR"];
  const REGIONS = ["North", "South", "East", "West", "Central"];
  const SALUTATIONS = ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."];

  useEffect(() => {
    if (lead) {
      setFormData(lead);
    }
    fetchDropdownData();
  }, [lead]);

  const fetchDropdownData = async () => {
    try {
      const [companiesRes] = await Promise.all([
        apiRequest("/api/companies", "GET"),
      ]);

      setDropdownData(prev => ({
        ...prev,
        companies: companiesRes.status ? companiesRes.data.companies || [] : [],
        competitors: [
          { id: 1, name: "TCS" },
          { id: 2, name: "Infosys" },
          { id: 3, name: "Wipro" },
          { id: 4, name: "HCL" },
          { id: 5, name: "Tech Mahindra" }
        ]
      }));
    } catch (error) {
      console.error("Error fetching dropdown data:", error);
    }
  };

  const handleInputChange = (field, value) => {
    // Handle numeric fields properly
    if (['tender_fee', 'expected_revenue', 'emd_amount', 'bg_amount', 'expected_orc'].includes(field)) {
      const numericValue = value === '' ? 0 : parseFloat(value) || 0;
      setFormData(prev => ({ ...prev, [field]: numericValue }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }

    // Clear errors when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleArrayChange = (field, index, subField, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) =>
        i === index ? { ...item, [subField]: value } : item
      ),
    }));
  };

  const addArrayItem = (field, newItem) => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], { ...newItem, id: Date.now() }],
    }));
  };

  const removeArrayItem = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  // Partner Management
  const addPartner = () => {
    const newPartner = {
      id: Date.now(),
      partner_type: formData.partner_type,
      partner_name: formData.partner_name,
      engagement_type: formData.partner_engagement_type,
      payment_terms: formData.payment_terms,
      billing_type: formData.billing_type,
      expected_orc: formData.expected_orc
    };
    
    setFormData(prev => ({
      ...prev,
      partners_data: [...prev.partners_data, newPartner],
      partner_type: "",
      partner_name: "",
      partner_engagement_type: "",
      payment_terms: "",
      billing_type: "",
      expected_orc: 0
    }));
  };

  // Competitor Management
  const addCompetitor = () => {
    if (formData.competitor && formData.competitor_description) {
      const competitorName = dropdownData.competitors.find(c => c.id == formData.competitor)?.name || formData.competitor;
      const newCompetitor = {
        id: Date.now(),
        name: competitorName,
        description: formData.competitor_description
      };
      
      setFormData(prev => ({
        ...prev,
        competitors: [...prev.competitors, newCompetitor],
        competitor: "",
        competitor_description: ""
      }));
    }
  };

  // Clause Management  
  const addClause = () => {
    addArrayItem("clauses", {
      clause_type: "",
      criteria_description: ""
    });
  };

  const validateForm = () => {
    const newErrors = {};

    // Required field validations
    if (!formData.project_title?.trim()) {
      newErrors.project_title = "Project title is required";
    }
    if (!formData.lead_source) {
      newErrors.lead_source = "Lead source is required";
    }
    if (!formData.lead_sub_type) {
      newErrors.lead_sub_type = "Lead sub type is required";
    }
    if (!formData.tender_sub_type) {
      newErrors.tender_sub_type = "Tender sub type is required";
    }
    if (formData.products_services.length === 0) {
      newErrors.products_services = "At least one product/service is required";
    }
    if (!formData.company_id) {
      newErrors.company_id = "Company selection is required";
    }
    if (!formData.end_customer_id) {
      newErrors.end_customer_id = "End customer selection is required";
    }
    if (!formData.expected_revenue || formData.expected_revenue <= 0) {
      newErrors.expected_revenue = "Expected revenue must be greater than 0";
    }
    if (!formData.convert_to_opportunity_date) {
      newErrors.convert_to_opportunity_date = "Convert to opportunity date is required";
    }
    if (!formData.tender_fee || formData.tender_fee <= 0) {
      newErrors.tender_fee = "Tender fee is required";
    }
    if (!formData.tender_authority?.trim()) {
      newErrors.tender_authority = "Tender authority is required";
    }
    if (!formData.tender_for?.trim()) {
      newErrors.tender_for = "Tender for is required";
    }
    if (formData.contacts.length === 0) {
      newErrors.contacts = "At least one contact is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (isDraft = false) => {
    if (!isDraft && !validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        status: isDraft ? "New" : formData.status,
        // Ensure numeric fields are properly formatted
        tender_fee: parseFloat(formData.tender_fee) || 0,
        expected_revenue: parseFloat(formData.expected_revenue) || 0,
        emd_amount: parseFloat(formData.emd_amount) || 0,
        bg_amount: parseFloat(formData.bg_amount) || 0,
        expected_orc: parseFloat(formData.expected_orc) || 0,
      };

      const response = await apiRequest("/api/leads", "POST", payload);
      
      if (response.status) {
        onSave?.(response.data);
      } else {
        console.error("Failed to save lead:", response.error);
        alert("Failed to save lead: " + (response.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error saving lead:", error);
      alert("Error saving lead: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderGeneralDetails = () => (
    <div className="space-y-6">
      {/* Lead Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Lead Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Project Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.project_title}
              onChange={(e) => handleInputChange("project_title", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.project_title ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="Enter project title"
            />
            {errors.project_title && (
              <p className="text-red-500 text-sm mt-1">{errors.project_title}</p>
            )}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Lead Source <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.lead_source}
              onChange={(e) => handleInputChange("lead_source", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.lead_source ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select Lead Source</option>
              <option value="Direct Marketing">Direct Marketing</option>
              <option value="Referral">Referral</option>
              <option value="Advertisement">Advertisement</option>
              <option value="Event">Event</option>
              <option value="Other">Other</option>
            </select>
            {errors.lead_source && (
              <p className="text-red-500 text-sm mt-1">{errors.lead_source}</p>
            )}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Lead Sub Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.lead_sub_type}
              onChange={(e) => handleInputChange("lead_sub_type", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.lead_sub_type ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select Lead Sub Type</option>
              <option value="Pre-Tender">Pre-Tender</option>
              <option value="Post-Tender">Post-Tender</option>
            </select>
            {errors.lead_sub_type && (
              <p className="text-red-500 text-sm mt-1">{errors.lead_sub_type}</p>
            )}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender Sub Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.tender_sub_type}
              onChange={(e) => handleInputChange("tender_sub_type", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.tender_sub_type ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select Tender Sub Type</option>
              <option value="GeM Tender">GeM Tender</option>
              <option value="Limited Tender">Limited Tender</option>
              <option value="Open Tender">Open Tender</option>
              <option value="Single Tender">Single Tender</option>
            </select>
            {errors.tender_sub_type && (
              <p className="text-red-500 text-sm mt-1">{errors.tender_sub_type}</p>
            )}
          </div>
        </div>

        {/* Products & Services Multi-select */}
        <div className="mt-4">
          <label className="block text-left text-sm font-medium text-gray-700 mb-1">
            Products & Services <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
            {PRODUCTS_SERVICES.map((product) => (
              <label key={product} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.products_services.includes(product)}
                  onChange={(e) => {
                    const newProducts = e.target.checked
                      ? [...formData.products_services, product]
                      : formData.products_services.filter(p => p !== product);
                    handleInputChange("products_services", newProducts);
                  }}
                  className="mr-2"
                />
                <span className="text-sm">{product}</span>
              </label>
            ))}
          </div>
          {errors.products_services && (
            <p className="text-red-500 text-sm mt-1">{errors.products_services}</p>
          )}
        </div>
      </div>

      {/* Company Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Company Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Company <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.company_id}
              onChange={(e) => handleInputChange("company_id", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.company_id ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select Company</option>
              {dropdownData.companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name} - {company.city}
                </option>
              ))}
            </select>
            {errors.company_id && (
              <p className="text-red-500 text-sm mt-1">{errors.company_id}</p>
            )}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Sub Business Type
            </label>
            <select
              value={formData.sub_business_type}
              onChange={(e) => handleInputChange("sub_business_type", e.target.value)}
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

      {/* End Customer Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          End Customer / Billing Customer
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              End Customer <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.end_customer_id}
              onChange={(e) => handleInputChange("end_customer_id", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.end_customer_id ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select End Customer</option>
              {dropdownData.companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name} - {company.city}
                </option>
              ))}
            </select>
            {errors.end_customer_id && (
              <p className="text-red-500 text-sm mt-1">{errors.end_customer_id}</p>
            )}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              End Customer Region
            </label>
            <select
              value={formData.end_customer_region}
              onChange={(e) => handleInputChange("end_customer_region", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Region</option>
              {REGIONS.map(region => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Partner Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Partner Details
        </h3>

        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.partner_involved}
              onChange={(e) => handleInputChange("partner_involved", e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">
              Partner Involved
            </span>
          </label>
        </div>

        {formData.partner_involved && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  Partner Type
                </label>
                <select
                  value={formData.partner_type}
                  onChange={(e) => handleInputChange("partner_type", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Select Partner Type</option>
                  {PARTNER_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  Partner Name
                </label>
                <input
                  type="text"
                  value={formData.partner_name}
                  onChange={(e) => handleInputChange("partner_name", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Enter partner name"
                />
              </div>

              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  Billing Type
                </label>
                <select
                  value={formData.billing_type}
                  onChange={(e) => handleInputChange("billing_type", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Select Billing Type</option>
                  {BILLING_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  Partner Engagement Type
                </label>
                <select
                  value={formData.partner_engagement_type}
                  onChange={(e) => handleInputChange("partner_engagement_type", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Select Engagement Type</option>
                  {ENGAGEMENT_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  Expected ORC
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.expected_orc}
                  onChange={(e) => handleInputChange("expected_orc", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                Payment Terms with Partner
              </label>
              <textarea
                value={formData.payment_terms}
                onChange={(e) => handleInputChange("payment_terms", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows="3"
                placeholder="Enter payment terms"
              />
            </div>

            <button
              type="button"
              onClick={addPartner}
              className="mb-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              disabled={!formData.partner_type || !formData.partner_name}
            >
              Add Partner
            </button>

            {/* Partners Table */}
            {formData.partners_data.length > 0 && (
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Partner Type</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Partner Name</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Engagement Type</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Payment Terms</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Billing Type</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Expected ORC</th>
                      <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {formData.partners_data.map((partner, index) => (
                      <tr key={partner.id} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-sm border-b">{partner.partner_type}</td>
                        <td className="px-4 py-2 text-sm border-b">{partner.partner_name}</td>
                        <td className="px-4 py-2 text-sm border-b">{partner.engagement_type}</td>
                        <td className="px-4 py-2 text-sm border-b">{partner.payment_terms}</td>
                        <td className="px-4 py-2 text-sm border-b">{partner.billing_type}</td>
                        <td className="px-4 py-2 text-sm border-b">{partner.expected_orc}</td>
                        <td className="px-4 py-2 text-sm border-b">
                          <button
                            type="button"
                            onClick={() => removeArrayItem("partners_data", index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );

  const renderContactDetails = () => (
    <div className="space-y-6">
      <div className="bg-gray-50 p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-left text-lg font-medium text-gray-900">
            Contact Information
          </h3>
          <button
            type="button"
            onClick={() => addArrayItem("contacts", {
              sr_no: formData.contacts.length + 1,
              designation: "",
              salutation: "Mr.",
              first_name: "",
              middle_name: "",
              last_name: "",
              email: "",
              primary_phone: "",
              decision_maker: false,
              decision_maker_percentage: 0,
              comments: "",
            })}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add Contact
          </button>
        </div>

        {formData.contacts.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No contacts added yet. Click "Add Contact" to add the first contact.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Sr. No.</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Designation</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Salutation</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">First Name *</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Middle Name</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Last Name *</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Email *</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Primary Phone *</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Decision Maker</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Decision Maker %</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Comments</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.contacts.map((contact, index) => (
                  <tr key={contact.id || index} className="hover:bg-gray-50">
                    <td className="px-2 py-2 text-sm border-b">{index + 1}</td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="text"
                        value={contact.designation}
                        onChange={(e) => handleArrayChange("contacts", index, "designation", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Designation"
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <select
                        value={contact.salutation}
                        onChange={(e) => handleArrayChange("contacts", index, "salutation", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        {SALUTATIONS.map(sal => (
                          <option key={sal} value={sal}>{sal}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="text"
                        value={contact.first_name}
                        onChange={(e) => handleArrayChange("contacts", index, "first_name", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="First Name"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="text"
                        value={contact.middle_name}
                        onChange={(e) => handleArrayChange("contacts", index, "middle_name", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Middle Name"
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="text"
                        value={contact.last_name}
                        onChange={(e) => handleArrayChange("contacts", index, "last_name", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Last Name"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="email"
                        value={contact.email}
                        onChange={(e) => handleArrayChange("contacts", index, "email", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Email"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="tel"
                        value={contact.primary_phone}
                        onChange={(e) => handleArrayChange("contacts", index, "primary_phone", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="Phone"
                        required
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b text-center">
                      <input
                        type="checkbox"
                        checked={contact.decision_maker}
                        onChange={(e) => handleArrayChange("contacts", index, "decision_maker", e.target.checked)}
                        className="form-checkbox"
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={contact.decision_maker_percentage}
                        onChange={(e) => handleArrayChange("contacts", index, "decision_maker_percentage", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="%"
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <textarea
                        value={contact.comments}
                        onChange={(e) => handleArrayChange("contacts", index, "comments", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        rows="1"
                        placeholder="Comments"
                      />
                    </td>
                    <td className="px-2 py-2 text-sm border-b">
                      <button
                        type="button"
                        onClick={() => removeArrayItem("contacts", index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {errors.contacts && (
          <p className="text-red-500 text-sm mt-2">{errors.contacts}</p>
        )}
      </div>
    </div>
  );

  const renderTenderDetails = () => (
    <div className="space-y-6">
      {/* Tender Info Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Tender Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender Fee <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.tender_fee}
              onChange={(e) => handleInputChange("tender_fee", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.tender_fee ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="0.00"
            />
            {errors.tender_fee && (
              <p className="text-red-500 text-sm mt-1">{errors.tender_fee}</p>
            )}
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Currency <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.currency}
              onChange={(e) => handleInputChange("currency", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {CURRENCY_OPTIONS.map(currency => (
                <option key={currency} value={currency}>{currency}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Submission Type
            </label>
            <select
              value={formData.submission_type}
              onChange={(e) => handleInputChange("submission_type", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select Type</option>
              <option value="Online">Online</option>
              <option value="Offline">Offline</option>
              <option value="Both">Both</option>
            </select>
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender Authority <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.tender_authority}
              onChange={(e) => handleInputChange("tender_authority", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.tender_authority ? "border-red-300" : "border-gray-300"
              }`}
            />
            {errors.tender_authority && (
              <p className="text-red-500 text-sm mt-1">{errors.tender_authority}</p>
            )}
          </div>
          
          <div className="md:col-span-3">
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender For <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.tender_for}
              onChange={(e) => handleInputChange("tender_for", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.tender_for ? "border-red-300" : "border-gray-300"
              }`}
              rows="3"
            />
            {errors.tender_for && (
              <p className="text-red-500 text-sm mt-1">{errors.tender_for}</p>
            )}
          </div>
        </div>

        {/* EMD Section */}
        <div className="mt-6">
          <div className="flex items-center mb-4">
            <input
              type="checkbox"
              id="emd_required"
              checked={formData.emd_required}
              onChange={(e) => handleInputChange("emd_required", e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="emd_required" className="text-sm font-medium text-gray-700">
              EMD Required
            </label>
          </div>
          
          {formData.emd_required && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  EMD Amount
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.emd_amount}
                  onChange={(e) => handleInputChange("emd_amount", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  EMD Currency
                </label>
                <select
                  value={formData.emd_currency}
                  onChange={(e) => handleInputChange("emd_currency", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {CURRENCY_OPTIONS.map(currency => (
                    <option key={currency} value={currency}>{currency}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* BG Section */}
        <div className="mt-6">
          <div className="flex items-center mb-4">
            <input
              type="checkbox"
              id="bg_required"
              checked={formData.bg_required}
              onChange={(e) => handleInputChange("bg_required", e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="bg_required" className="text-sm font-medium text-gray-700">
              Bank Guarantee Required
            </label>
          </div>
          
          {formData.bg_required && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  BG Amount
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.bg_amount}
                  onChange={(e) => handleInputChange("bg_amount", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                  BG Currency
                </label>
                <select
                  value={formData.bg_currency}
                  onChange={(e) => handleInputChange("bg_currency", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {CURRENCY_OPTIONS.map(currency => (
                    <option key={currency} value={currency}>{currency}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Important Dates Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Important Dates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {formData.important_dates.map((date, index) => (
            <div key={date.key}>
              <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                {date.label}
              </label>
              <input
                type="date"
                value={date.value}
                onChange={(e) => handleArrayChange("important_dates", index, "value", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Clauses Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-left text-lg font-medium text-gray-900">
            Clauses Details
          </h3>
          <button
            type="button"
            onClick={addClause}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add Clause
          </button>
        </div>

        {formData.clauses.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No clauses added yet. Click "Add Clause" to add clauses.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Clause Type</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Criteria Description</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.clauses.map((clause, index) => (
                  <tr key={clause.id || index} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm border-b">
                      <input
                        type="text"
                        value={clause.clause_type}
                        onChange={(e) => handleArrayChange("clauses", index, "clause_type", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                        placeholder="Clause Type"
                      />
                    </td>
                    <td className="px-4 py-2 text-sm border-b">
                      <textarea
                        value={clause.criteria_description}
                        onChange={(e) => handleArrayChange("clauses", index, "criteria_description", e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                        rows="2"
                        placeholder="Criteria Description"
                      />
                    </td>
                    <td className="px-4 py-2 text-sm border-b">
                      <button
                        type="button"
                        onClick={() => removeArrayItem("clauses", index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  const renderOtherDetails = () => (
    <div className="space-y-6">
      {/* Revenue & Conversion Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Revenue & Conversion Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Expected Revenue <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.expected_revenue}
              onChange={(e) => handleInputChange("expected_revenue", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.expected_revenue ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="0.00"
            />
            {errors.expected_revenue && (
              <p className="text-red-500 text-sm mt-1">{errors.expected_revenue}</p>
            )}
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Currency <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.revenue_currency}
              onChange={(e) => handleInputChange("revenue_currency", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {CURRENCY_OPTIONS.map(currency => (
                <option key={currency} value={currency}>{currency}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Convert to Opportunity Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={formData.convert_to_opportunity_date}
              onChange={(e) => handleInputChange("convert_to_opportunity_date", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.convert_to_opportunity_date ? "border-red-300" : "border-gray-300"
              }`}
            />
            {errors.convert_to_opportunity_date && (
              <p className="text-red-500 text-sm mt-1">{errors.convert_to_opportunity_date}</p>
            )}
          </div>
        </div>
      </div>

      {/* Competitors Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Competitors Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Competitor
            </label>
            <select
              value={formData.competitor}
              onChange={(e) => handleInputChange("competitor", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select Competitor</option>
              {dropdownData.competitors.map(competitor => (
                <option key={competitor.id} value={competitor.id}>{competitor.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.competitor_description}
              onChange={(e) => handleInputChange("competitor_description", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows="3"
              placeholder="Enter competitor description"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={addCompetitor}
          className="mb-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          disabled={!formData.competitor || !formData.competitor_description}
        >
          Add Competitor
        </button>

        {/* Competitors List */}
        {formData.competitors.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Competitor Name</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Description</th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-700 border-b">Actions</th>
                </tr>
              </thead>
              <tbody>
                {formData.competitors.map((competitor, index) => (
                  <tr key={competitor.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm border-b">{competitor.name}</td>
                    <td className="px-4 py-2 text-sm border-b">{competitor.description}</td>
                    <td className="px-4 py-2 text-sm border-b">
                      <button
                        type="button"
                        onClick={() => removeArrayItem("competitors", index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload Documents Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Upload Documents
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Document Type
            </label>
            <select
              value={formData.document_type}
              onChange={(e) => handleInputChange("document_type", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select Document Type</option>
              {dropdownData.documentTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Quotation Name
            </label>
            <input
              type="text"
              value={formData.quotation_name}
              onChange={(e) => handleInputChange("quotation_name", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter quotation name"
            />
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Upload File (Max 10MB)
            </label>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.jpg,.png,.xls,.xlsx,.zip,.eml,.msg"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              onChange={(e) => {
                const file = e.target.files[0];
                if (file && file.size > 10 * 1024 * 1024) {
                  alert("File size must be less than 10MB");
                  e.target.value = "";
                }
              }}
            />
            <p className="text-xs text-gray-500 mt-1">
              Supported formats: PDF, DOC, DOCX, JPG, PNG, XLS, XLSX, ZIP, EML, MSG
            </p>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.document_description}
              onChange={(e) => handleInputChange("document_description", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows="3"
              placeholder="Enter document description"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            // Document upload logic would go here
            alert("Document upload functionality to be implemented");
          }}
          className="mb-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          disabled={!formData.document_type || !formData.quotation_name}
        >
          Add Document
        </button>

        {/* Documents Table Placeholder */}
        <div className="bg-white border border-gray-300 rounded-lg p-4">
          <p className="text-gray-500 text-center">
            Uploaded documents will appear here
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-left text-2xl font-bold text-gray-900">
          {lead ? "Edit Lead" : "Add New Lead"}
        </h2>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.icon} {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="px-6 py-6">
        {activeTab === 0 && renderGeneralDetails()}
        {activeTab === 1 && renderContactDetails()}
        {activeTab === 2 && renderTenderDetails()}
        {activeTab === 3 && renderOtherDetails()}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => handleSubmit(true)}
            disabled={loading}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            Save as Draft
          </button>
          <button
            type="button"
            onClick={() => handleSubmit(false)}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Saving..." : "Submit"}
          </button>
        </div>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default AddNewLeadForm;