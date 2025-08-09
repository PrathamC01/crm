import React, { useState, useEffect } from "react";
import { apiRequest } from "../../../utils/api";

const AddNewLeadForm = ({ lead, onSave, onCancel }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    // Tab 1: General Lead Details
    project_title: "",
    lead_source: "",
    lead_sub_type: "",
    tender_sub_type: "",
    products_services: [],
    company_id: "",
    sub_business_type: "",
    end_customer_id: "",
    end_customer_region: "",
    partner_involved: false,
    partners: [],
    status: "New", // Proper lead status
    priority: "Medium",

    // Tab 2: Contact Details
    contacts: [],

    // Tab 3: Tender Details
    tender_fee: 0, // Number, not string
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
    important_dates: [],
    clauses: [],

    // Tab 4: Other Details
    expected_revenue: 0, // Number, not string
    revenue_currency: "INR",
    convert_to_opportunity_date: "",
    competitors: [],
    documents: [],
  });

  const [dropdownData, setDropdownData] = useState({
    companies: [],
    products: [],
    partners: [],
    competitors: [],
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const tabs = [
    {
      id: 0,
      name: "General Details",
      icon: "📋",
      fields: ["project_title", "lead_source", "company_id"],
    },
    { id: 1, name: "Contact Details", icon: "👥", fields: ["contacts"] },
    {
      id: 2,
      name: "Tender Details",
      icon: "📄",
      fields: ["tender_fee", "tender_authority"],
    },
    { id: 3, name: "Other Details", icon: "💰", fields: ["expected_revenue"] },
  ];

  // Lead Status Options
  const LEAD_STATUS_OPTIONS = [
    { value: "New", label: "New" },
    { value: "Contacted", label: "Contacted" },
    { value: "Qualified", label: "Qualified" },
    { value: "Unqualified", label: "Unqualified" },
    { value: "Converted", label: "Converted" },
    { value: "Rejected", label: "Rejected" }
  ];

  // Priority Options
  const PRIORITY_OPTIONS = [
    { value: "High", label: "High" },
    { value: "Medium", label: "Medium" },
    { value: "Low", label: "Low" }
  ];

  useEffect(() => {
    if (lead) {
      setFormData(lead);
    }
    fetchDropdownData();
  }, [lead]);

  const fetchDropdownData = async () => {
    try {
      const [companiesRes, productsRes] = await Promise.all([
        apiRequest("/api/companies", "GET"),
        apiRequest("/api/products", "GET").catch(() => ({ 
          status: false, 
          data: { products: [
            { id: 1, name: "Hardware Support" },
            { id: 2, name: "Software Support" },
            { id: 3, name: "Cloud Services" },
            { id: 4, name: "Consulting" }
          ]} 
        })),
      ]);

      setDropdownData({
        companies: companiesRes.status ? companiesRes.data.companies || [] : [],
        products: productsRes.status ? productsRes.data.products || [] : [],
        partners: [],
        competitors: [],
      });
    } catch (error) {
      console.error("Error fetching dropdown data:", error);
    }
  };

  const handleInputChange = (field, value) => {
    // Handle numeric fields properly
    if (['tender_fee', 'expected_revenue', 'emd_amount', 'bg_amount'].includes(field)) {
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

  const validateForm = () => {
    const newErrors = {};

    // Required field validations
    if (!formData.project_title?.trim()) {
      newErrors.project_title = "Project title is required";
    }
    if (!formData.lead_source) {
      newErrors.lead_source = "Lead source is required";
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
      {/* Project Details Section */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Project Details
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
              <p className="text-red-500 text-sm mt-1">
                {errors.project_title}
              </p>
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
              onChange={(e) =>
                handleInputChange("lead_sub_type", e.target.value)
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Lead Sub Type</option>
              <option value="Pre-Tender">Pre-Tender</option>
              <option value="Post-Tender">Post-Tender</option>
            </select>
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender Sub Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.tender_sub_type}
              onChange={(e) =>
                handleInputChange("tender_sub_type", e.target.value)
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Tender Sub Type</option>
              <option value="GeM Tender">GeM Tender</option>
              <option value="Limited Tender">Limited Tender</option>
              <option value="Open Tender">Open Tender</option>
              <option value="Single Tender">Single Tender</option>
            </select>
          </div>
        </div>

        {/* Lead Status and Priority */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Lead Status <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleInputChange("status", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {LEAD_STATUS_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={formData.priority}
              onChange={(e) => handleInputChange("priority", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {PRIORITY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Products & Services */}
        <div className="mt-4">
          <label className="block text-left text-sm font-medium text-gray-700 mb-1">
            Products & Services
          </label>
          <div className="flex flex-wrap gap-2">
            {["Hardware Support", "Software Support", "Cloud Services", "Consulting"].map((product) => (
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
              onChange={(e) =>
                handleInputChange("sub_business_type", e.target.value)
              }
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
              onChange={(e) =>
                handleInputChange("end_customer_id", e.target.value)
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select End Customer</option>
              {dropdownData.companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name} - {company.city}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              End Customer Region
            </label>
            <select
              value={formData.end_customer_region}
              onChange={(e) =>
                handleInputChange("end_customer_region", e.target.value)
              }
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
          <div className="space-y-4">
            {formData.contacts.map((contact, index) => (
              <div key={contact.id || index} className="bg-white p-4 rounded-lg border">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-left text-md font-medium">Contact #{index + 1}</h4>
                  <button
                    type="button"
                    onClick={() => removeArrayItem("contacts", index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Designation
                    </label>
                    <input
                      type="text"
                      value={contact.designation}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "designation", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Salutation
                    </label>
                    <select
                      value={contact.salutation}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "salutation", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="Mr.">Mr.</option>
                      <option value="Mrs.">Mrs.</option>
                      <option value="Ms.">Ms.</option>
                      <option value="Dr.">Dr.</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      First Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={contact.first_name}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "first_name", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Middle Name
                    </label>
                    <input
                      type="text"
                      value={contact.middle_name}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "middle_name", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Last Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={contact.last_name}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "last_name", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Email <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      value={contact.email}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "email", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                      Primary Phone <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={contact.primary_phone}
                      onChange={(e) =>
                        handleArrayChange("contacts", index, "primary_phone", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={contact.decision_maker}
                        onChange={(e) =>
                          handleArrayChange("contacts", index, "decision_maker", e.target.checked)
                        }
                        className="mr-2"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        Decision Maker
                      </span>
                    </label>
                  </div>
                  
                  {contact.decision_maker && (
                    <div>
                      <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                        Decision Maker %
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={contact.decision_maker_percentage}
                        onChange={(e) =>
                          handleArrayChange("contacts", index, "decision_maker_percentage", e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  )}
                </div>
                
                <div className="mt-4">
                  <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                    Comments
                  </label>
                  <textarea
                    value={contact.comments}
                    onChange={(e) =>
                      handleArrayChange("contacts", index, "comments", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    rows="2"
                  />
                </div>
              </div>
            ))}
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
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-left text-lg font-medium text-gray-900 mb-4">
          Tender Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender Fee
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.tender_fee}
              onChange={(e) => handleInputChange("tender_fee", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="0.00"
            />
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Currency
            </label>
            <select
              value={formData.currency}
              onChange={(e) => handleInputChange("currency", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="INR">INR</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
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
              Tender Authority
            </label>
            <input
              type="text"
              value={formData.tender_authority}
              onChange={(e) => handleInputChange("tender_authority", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          
          <div className="md:col-span-3">
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Tender For
            </label>
            <textarea
              value={formData.tender_for}
              onChange={(e) => handleInputChange("tender_for", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows="3"
            />
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
                  <option value="INR">INR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
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
                  <option value="INR">INR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderOtherDetails = () => (
    <div className="space-y-6">
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
              Revenue Currency
            </label>
            <select
              value={formData.revenue_currency}
              onChange={(e) => handleInputChange("revenue_currency", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="INR">INR</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              Convert to Opportunity Date
            </label>
            <input
              type="date"
              value={formData.convert_to_opportunity_date}
              onChange={(e) => handleInputChange("convert_to_opportunity_date", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-lg">
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