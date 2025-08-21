import React, { useState, useEffect } from "react";
import { apiRequest } from "../../../utils/api";

const CompanyForm = ({ company, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    // Basic Information - ALL REQUIRED
    name: "",
    parent_company_name: null,
    company_type: "",
    industry: "",
    sub_industry: "",
    annual_revenue: "",

    // gst_number, pan_number, tax_identification_number, company_registration_number
    gst_number: "",
    pan_number: "",
    tax_identification_number: "",
    company_registration_number: "",
    supporting_documents: [],
    verification_source: "",
    verification_date: "",
    verified_by: "",

    // Registered Address - ALL REQUIRED
    address: "",
    country: "India",
    state: "",
    city: "",
    pin_code: "",

    // Hierarchy & Linkages - ALL REQUIRED
    parent_child_mapping_confirmed: false,
    linked_subsidiaries: ["None"],
    associated_channel_partner: "",

    // Optional fields
    website: "",
    description: "",
  });

  const [companies, setCompanies] = useState([]);
  const [industryMasters, setIndustryMasters] = useState({});
  const [countries, setCountries] = useState([]);
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [selectedCountryCode, setSelectedCountryCode] = useState("IN"); // Default to India
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [duplicateCheck, setDuplicateCheck] = useState(null);

  useEffect(() => {
    if (company) {
      setFormData({
        name: company.name || "",
        parent_company_name: company.parent_company_name || "",
        company_type: company.company_type || "",
        industry: company.industry || "",
        sub_industry: company.sub_industry || "",
        annual_revenue: company.annual_revenue || "",
        gst_number: company.gst_number || "",
        pan_number: company.pan_number || "",
        tax_identification_number: company.tax_identification_number || "",
        company_registration_number: company.company_registration_number || "",
        supporting_documents: company.supporting_documents,
        verification_source: company.verification_source || "",
        verification_date: company.verification_date
          ? company.verification_date.split("T")[0]
          : "",
        verified_by: company.verified_by || "",
        address: company.address || "",
        country: company.country || "India",
        state: company.state || "",
        city: company.city || "",
        pin_code: company.pin_code || "",
        parent_child_mapping_confirmed:
          company.parent_child_mapping_confirmed || false,
        linked_subsidiaries: company.linked_subsidiaries || ["None"],
        associated_channel_partner: company.associated_channel_partner || "",
        website: company.website || "",
        description: company.description || "",
      });
    }
    fetchMasterData();
  }, [company]);

  const fetchMasterData = async () => {
    try {
      const [companiesRes, industriesRes, countriesRes] = await Promise.all([
        apiRequest("/api/companies"),
        apiRequest("/api/companies/masters/industries"),
        apiRequest("/api/companies/masters/countries"),
      ]);

      if (companiesRes.status) {
        setCompanies(companiesRes.data.companies || []);
      }
      if (industriesRes.status) {
        setIndustryMasters(industriesRes.data || {});
      }
      if (countriesRes.status) {
        setCountries(countriesRes.data || []);
      }
    } catch (err) {
      console.error("Failed to fetch master data:", err);
    }
  };

  // Fetch states when country changes
  const fetchStates = async (countryCode) => {
    if (!countryCode) return;
    
    try {
      const response = await apiRequest(`/api/companies/masters/states/${countryCode}`);
      if (response.status && response.data.states) {
        setStates(response.data.states);
      } else {
        setStates([]);
        // Show message if no states available
        if (response.data?.message) {
          console.log(response.data.message);
        }
      }
      // Clear cities when states change
      setCities([]);
      setFormData(prev => ({ ...prev, state: "", city: "" }));
    } catch (err) {
      console.error("Failed to fetch states:", err);
      setStates([]);
    }
  };

  // Fetch cities when state changes
  const fetchCities = async (countryCode, stateName) => {
    if (!countryCode || !stateName) return;
    
    try {
      const response = await apiRequest(`/api/companies/masters/cities/${countryCode}/${encodeURIComponent(stateName)}`);
      if (response.status && response.data.cities) {
        setCities(response.data.cities);
      } else {
        setCities([]);
      }
      // Clear city when cities change
      setFormData(prev => ({ ...prev, city: "" }));
    } catch (err) {
      console.error("Failed to fetch cities:", err);
      setCities([]);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Basic Information - All Required
    if (!formData.name.trim()) {
      newErrors.name = "Company name is required";
    } else if (formData.name.length < 2) {
      newErrors.name = "Company name must be at least 2 characters";
    }

    if (!formData.company_type) {
      newErrors.company_type = "Company type is required";
    }

    if (!formData.industry) {
      newErrors.industry = "Industry is required";
    }

    if (!formData.sub_industry) {
      newErrors.sub_industry = "Sub-industry is required";
    }

    if (!formData.annual_revenue || formData.annual_revenue <= 0) {
      newErrors.annual_revenue =
        "Annual revenue is required and must be positive";
    }

    // Conditional validation based on company type
    if (["DOMESTIC_GST", "DOMESTIC_NONGST"].includes(formData.company_type)) {
      // GST validation for domestic companies
      if (!formData.gst_number) {
        newErrors.gst_number = "GST number is required for domestic companies";
      } else if (!/^[0-9A-Z]{15}$/.test(formData.gst_number)) {
        newErrors.gst_number =
          "GST must be exactly 15 alphanumeric characters (0-9, A-Z)";
      }

      // PAN validation for domestic companies
      if (!formData.pan_number) {
        newErrors.pan_number = "PAN number is required for domestic companies";
      } else if (!/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(formData.pan_number)) {
        newErrors.pan_number =
          "Invalid PAN format. Expected: AAAAA0000A (5 letters, 4 digits, 1 letter)";
      }
    }

    if (["INTERNATIONAL", "OVERSEAS"].includes(formData.company_type)) {
      // Tax ID validation for international/overseas companies
      if (!formData.tax_identification_number) {
        newErrors.tax_identification_number =
          "Tax Identification Number is required for international/overseas companies";
      } else if (
        !/^[A-Z0-9\-]{6,20}$/.test(formData.tax_identification_number)
      ) {
        newErrors.tax_identification_number =
          "Tax ID must be 6-20 characters (A-Z, 0-9, -)";
      }

      // Company Registration Number validation for international/overseas companies
      if (!formData.company_registration_number) {
        newErrors.company_registration_number =
          "Company Registration Number is required for international/overseas companies";
      } else if (
        !/^[A-Z0-9\-\/]{5,30}$/.test(formData.company_registration_number)
      ) {
        newErrors.company_registration_number =
          "CRN must be 5-30 characters (A-Z, 0-9, -, /)";
      }
    }

    if (formData.company_type === "OVERSEAS") {
      if (!formData.international_unique_id) {
        newErrors.international_unique_id =
          "International unique identifier is required for overseas companies";
      } else if (!/^[A-Z0-9-]{5,20}$/.test(formData.international_unique_id)) {
        newErrors.international_unique_id =
          "Invalid international ID format (5-20 alphanumeric characters)";
      }
    }

    // Supporting documents validation
    if (
      uploadedFiles.length === 0 &&
      (!formData.supporting_documents ||
        formData.supporting_documents.length === 0)
    ) {
      newErrors.supporting_documents =
        "At least one supporting document is required";
    }

    if (!formData.verification_source) {
      newErrors.verification_source = "Verification source is required";
    }

    if (!formData.verification_date) {
      newErrors.verification_date = "Verification date is required";
    }

    if (!formData.verified_by) {
      newErrors.verified_by = "Verified by (Admin name) is required";
    }

    // Address validation - All Required
    if (!formData.address.trim() || formData.address.length < 10) {
      newErrors.address =
        "Complete address is required (minimum 10 characters)";
    }

    if (!formData.country) {
      newErrors.country = "Country is required";
    }

    if (!formData.state) {
      newErrors.state = "State is required";
    }

    if (!formData.city.trim()) {
      newErrors.city = "City is required";
    }

    if (!formData.pin_code || !/^[0-9]{6}$/.test(formData.pin_code)) {
      newErrors.pin_code = "Valid 6-digit PIN code is required";
    }

    // Hierarchy validation
    if (
      formData.parent_child_mapping_confirmed === undefined ||
      formData.parent_child_mapping_confirmed === null
    ) {
      newErrors.parent_child_mapping_confirmed =
        "Parent-child mapping confirmation is required";
    }

    if (
      !formData.linked_subsidiaries ||
      formData.linked_subsidiaries.length === 0
    ) {
      newErrors.linked_subsidiaries =
        "Please specify linked subsidiaries or select 'None'";
    }

    // Website validation (optional but must be valid if provided)
    if (formData.website && !formData.website.match(/^https?:\/\/.+/)) {
      if (!formData.website.startsWith("http")) {
        setFormData((prev) => ({
          ...prev,
          website: "https://" + prev.website,
        }));
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const checkDuplicates = async () => {
    try {
      const response = await apiRequest("/api/companies/check-duplicates", {
        method: "POST",
        body: JSON.stringify(formData),
      });

      if (response.status && response.data) {
        setDuplicateCheck(response.data);
        if (response.data.is_duplicate) {
          setErrors((prev) => ({
            ...prev,
            duplicate: `${response.data.match_type} duplicate detected. You can continue anyway.`,
          }));
          return false;
        }
      }
      return true;
    } catch (err) {
      console.error("Duplicate check failed:", err);
      return true; // Continue if check fails
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    const allowedTypes = ["application/pdf", "image/jpeg", "image/png"];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (const file of files) {
      if (!allowedTypes.includes(file.type)) {
        setErrors((prev) => ({
          ...prev,
          supporting_documents: "Only PDF, JPEG, and PNG files are allowed",
        }));
        return;
      }
      if (file.size > maxSize) {
        setErrors((prev) => ({
          ...prev,
          supporting_documents: `File ${file.name} exceeds 10MB limit`,
        }));
        return;
      }
    }

    setUploadedFiles((prev) => [...prev, ...files]);

    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors.supporting_documents;
      return newErrors;
    });
  };

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(uploadedFiles);
    // Block submit until all validations pass
    if (!validateForm()) {
      return;
    }

    // Additional validation check for industry-dependent sub-type
    if (formData.industry && !formData.sub_industry) {
      setErrors((prev) => ({
        ...prev,
        sub_industry: "Sub-industry is required when industry is selected",
      }));
      return;
    }
    if (!company.id) {
      const noDuplicates = await checkDuplicates();
      if (
        !noDuplicates &&
        !window.confirm(
          "Duplicate company detected. Continue anyway?"
        )
      ) {
        return;
      }
    }
    // Check for duplicates before submission

    setLoading(true);
    try {
      const endpoint = company
        ? `/api/companies/${company.id}`
        : "/api/companies";
      const method = company ? "PUT" : "POST";

      // Prepare form data with proper types
      const submitData = {
        ...formData,
        annual_revenue: parseFloat(formData.annual_revenue),
        parent_child_mapping_confirmed: Boolean(
          formData.parent_child_mapping_confirmed
        ),
        verification_date: new Date(formData.verification_date).toISOString(),
      };

      const response = await apiRequest(endpoint, {
        method,
        body: JSON.stringify(submitData),
      });

      if (response.status) {
        // Upload files if any
        if (uploadedFiles.length > 0 && response.data?.id) {
          const formDataFiles = new FormData();
          uploadedFiles.forEach((file) => {
            formDataFiles.append("files", file);
          });

          await apiRequest(`/api/companies/${response.data.id}/documents`, {
            method: "POST",
            body: formDataFiles,
            headers: {}, // Let browser set content-type for FormData
          });
        }

        onSave(response.data);
      } else {
        setErrors({ submit: response.message || "Operation failed" });
      }
    } catch (err) {
      setErrors({ submit: "Network error occurred" });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    // Handle country change - update country code and fetch states
    if (name === "country") {
      const selectedCountry = countries.find(c => c.name === value);
      const countryCode = selectedCountry ? selectedCountry.code : "";
      
      setSelectedCountryCode(countryCode);
      setFormData((prev) => ({
        ...prev,
        [name]: newValue,
        state: "", // Clear state when country changes
        city: "" // Clear city when country changes
      }));
      
      // Fetch states for the new country
      if (countryCode) {
        fetchStates(countryCode);
      } else {
        setStates([]);
        setCities([]);
      }
    }
    // Handle state change - fetch cities
    else if (name === "state") {
      setFormData((prev) => ({
        ...prev,
        [name]: newValue,
        city: "" // Clear city when state changes
      }));
      
      // Fetch cities for the new state
      if (newValue && selectedCountryCode) {
        fetchCities(selectedCountryCode, newValue);
      } else {
        setCities([]);
      }
    }
    // Clear conditional fields when company type changes
    else if (name === "company_type") {
      setFormData((prev) => ({
        ...prev,
        [name]: newValue,
        // Clear all compliance fields when company type changes
        gst_number: "",
        pan_number: "",
        tax_identification_number: "",
        company_registration_number: "",
      }));
    } else if (name === "industry") {
      // Clear sub-industry when industry changes
      setFormData((prev) => ({
        ...prev,
        [name]: newValue,
        sub_industry: "", // Reset sub-industry when industry changes
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: newValue }));
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }

    // Clear related errors when company type changes
    if (name === "company_type") {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.gst_number;
        delete newErrors.pan_number;
        delete newErrors.tax_identification_number;
        delete newErrors.company_registration_number;
        return newErrors;
      });
    }

    // Clear sub_industry error when industry changes
    if (name === "industry" && errors.sub_industry) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.sub_industry;
        return newErrors;
      });
    }

    // Clear duplicate check when key fields change
    if (["name", "gst_number", "city", "country"].includes(name)) {
      setDuplicateCheck(null);
      if (errors.duplicate) {
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors.duplicate;
          return newErrors;
        });
      }
    }
  };

  const companyTypes = [
    { value: "DOMESTIC_GST", label: "Domestic GST" },
    { value: "DOMESTIC_NONGST", label: "Domestic Non-GST" },
    { value: "INTERNATIONAL", label: "International" },
    { value: "OVERSEAS", label: "Overseas" },
  ];

  const industryTypes = [
    { value: "Government", label: "Government" },
    { value: "BFSI", label: "BFSI" },
    { value: "Enterprise", label: "Enterprise" },
  ];

  const subTypeOptions = {
    Government: [
      "CENTRAL / FEDERAL — Ministries & Departments",
      "CENTRAL / FEDERAL — National Agencies & Regulatory Authorities",
      "CENTRAL / FEDERAL — Law Enforcement & Security Forces",
      "STATE / PROVINCIAL — State Departments & Authorities",
      "STATE / PROVINCIAL — State Regulatory Agencies",
      "STATE / PROVINCIAL — State Police & Emergency Services",
      "LOCAL — Municipal Corporations & City Councils",
      "LOCAL — District / County Administrations",
      "LOCAL — Local Utility Boards (Water, Power, Waste)",
      "SPECIALIZED — Judiciary & Courts",
      "SPECIALIZED — Public Sector Undertakings (PSUs)",
      "SPECIALIZED — Research & Development Institutions",
    ],
    BFSI: [
      "BANKING — Retail Banking",
      "BANKING — Corporate Banking",
      "BANKING — Private Banking / Wealth Management",
      "BANKING — Cooperative Banks",
      "BANKING — Central Banks & Monetary Authorities",
      "FINANCIAL SERVICES — Capital Markets (Exchanges, Brokerages)",
      "FINANCIAL SERVICES — Asset Management Companies (AMCs)",
      "FINANCIAL SERVICES — Investment Banking",
      "FINANCIAL SERVICES — Payment Gateways & Fintech",
      "FINANCIAL SERVICES — Microfinance & NBFCs",
      "INSURANCE — Life Insurance",
      "INSURANCE — General Insurance (Health, Auto, Property)",
      "INSURANCE — Reinsurance",
      "INSURANCE — Insurtech Companies",
    ],
    Enterprise: [
      "TECHNOLOGY & IT SERVICES — Software Development",
      "TECHNOLOGY & IT SERVICES — Cloud Computing & Data Centers",
      "TECHNOLOGY & IT SERVICES — Cybersecurity & Networking",
      "TECHNOLOGY & IT SERVICES — IT Consulting",
      "MANUFACTURING & INDUSTRIAL — Automotive",
      "MANUFACTURING & INDUSTRIAL — Electronics & Electricals",
      "MANUFACTURING & INDUSTRIAL — Heavy Engineering",
      "MANUFACTURING & INDUSTRIAL — FMCG",
      "HEALTHCARE & LIFE SCIENCES — Hospitals & Clinics",
      "HEALTHCARE & LIFE SCIENCES — Pharmaceuticals",
      "HEALTHCARE & LIFE SCIENCES — Medical Devices",
      "HEALTHCARE & LIFE SCIENCES — Biotechnology",
      "RETAIL & CONSUMER — E-commerce",
      "RETAIL & CONSUMER — Fashion & Apparel",
      "RETAIL & CONSUMER — Food & Beverage Chains",
      "RETAIL & CONSUMER — Consumer Electronics",
      "ENERGY & UTILITIES — Oil & Gas",
      "ENERGY & UTILITIES — Renewable Energy",
      "ENERGY & UTILITIES — Power Generation & Distribution",
      "ENERGY & UTILITIES — Water Management",
      "TRANSPORT & LOGISTICS — Airlines & Airports",
      "TRANSPORT & LOGISTICS — Shipping & Ports",
      "TRANSPORT & LOGISTICS — Rail & Road Freight",
      "TRANSPORT & LOGISTICS — Warehousing",
    ],
  };

  const verificationSources = [
    { value: "GST", label: "GST" },
    { value: "MCA", label: "MCA" },
    { value: "PAN_NSDL", label: "PAN/NSDL" },
    { value: "DIGILOCKER", label: "Digilocker" },
    { value: "GARTNER", label: "Gartner" },
    { value: "MANUAL", label: "Manual" },
  ];

  const getSubIndustries = () => {
    return industryMasters[formData.industry] || [];
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {errors.submit}
        </div>
      )}

      {errors.duplicate && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg">
          {errors.duplicate}
        </div>
      )}

      {/* Basic Information */}
      <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
            1
          </span>
          Basic Information (All Required)
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.name ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="Enter company name"
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parent Company
            </label>
            <select
              name="parent_company_name"
              value={formData.parent_company_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select parent company or create new</option>
              <option value="Create New">Create New</option>
              {companies
                .filter((c) => c.id !== company?.id)
                .map((c) => (
                  <option key={c.id} value={c.name}>
                    {c.name}
                  </option>
                ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Type <span className="text-red-500">*</span>
            </label>
            <select
              name="company_type"
              required
              value={formData.company_type}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.company_type ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select company type</option>
              {companyTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {errors.company_type && (
              <p className="text-red-500 text-sm mt-1">{errors.company_type}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry <span className="text-red-500">*</span>
            </label>
            <select
              name="industry"
              required
              value={formData.industry}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.industry ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select industry</option>
              {industryTypes.map((industry) => (
                <option key={industry.value} value={industry.value}>
                  {industry.label}
                </option>
              ))}
            </select>
            {errors.industry && (
              <p className="text-red-500 text-sm mt-1">{errors.industry}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sub-Industry <span className="text-red-500">*</span>
            </label>
            <select
              name="sub_industry"
              required
              value={formData.sub_industry}
              onChange={handleInputChange}
              disabled={!formData.industry}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.sub_industry ? "border-red-300" : "border-gray-300"
              }`}
            >
              <option value="">Select sub-industry</option>
              {formData.industry &&
                subTypeOptions[formData.industry] &&
                subTypeOptions[formData.industry].map((subType) => (
                  <option key={subType} value={subType}>
                    {subType}
                  </option>
                ))}
            </select>
            {errors.sub_industry && (
              <p className="text-red-500 text-sm mt-1">{errors.sub_industry}</p>
            )}
            {!formData.industry && (
              <p className="text-gray-500 text-sm mt-1">
                Select industry first to see sub-industries
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Annual Revenue (₹) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="annual_revenue"
              required
              min="0"
              step="0.01"
              value={formData.annual_revenue}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.annual_revenue ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="Enter annual revenue"
            />
            {errors.annual_revenue && (
              <p className="text-red-500 text-sm mt-1">
                {errors.annual_revenue}
              </p>
            )}
            {formData.annual_revenue > 20000000 && (
              <p className="text-green-600 text-sm mt-1">
                ✓ Will be auto-tagged as High Revenue Company
              </p>
            )}
          </div>

          {/* Conditional fields based on company type - Domestic companies */}
          {["DOMESTIC_GST", "DOMESTIC_NONGST"].includes(
            formData.company_type
          ) && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  GST Number <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">
                    (15 alphanumeric characters)
                  </span>
                </label>
                <input
                  type="text"
                  name="gst_number"
                  required
                  value={formData.gst_number}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                    errors.gst_number ? "border-red-300" : "border-gray-300"
                  }`}
                  placeholder="ABCDE1234FGHIJ5"
                  maxLength="15"
                  style={{ textTransform: "uppercase" }}
                  onInput={(e) => {
                    e.target.value = e.target.value
                      .toUpperCase()
                      .replace(/[^0-9A-Z]/g, "");
                  }}
                />
                {errors.gst_number && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.gst_number}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Manual entry - 15 characters (A-Z, 0-9)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  PAN Number <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">
                    (Indian PAN format)
                  </span>
                </label>
                <input
                  type="text"
                  name="pan_number"
                  required
                  value={formData.pan_number}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                    errors.pan_number ? "border-red-300" : "border-gray-300"
                  }`}
                  placeholder="ABCDE1234F"
                  maxLength="10"
                  style={{ textTransform: "uppercase" }}
                  onInput={(e) => {
                    e.target.value = e.target.value
                      .toUpperCase()
                      .replace(/[^A-Z0-9]/g, "");
                  }}
                />
                {errors.pan_number && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.pan_number}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Manual entry - Format: AAAAA0000A
                </p>
              </div>
            </>
          )}

          {/* Conditional fields based on company type - International/Overseas companies */}
          {["INTERNATIONAL", "OVERSEAS"].includes(formData.company_type) && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tax Identification Number{" "}
                  <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">
                    (VAT/GST/TIN)
                  </span>
                </label>
                <input
                  type="text"
                  name="tax_identification_number"
                  required
                  value={formData.tax_identification_number}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                    errors.tax_identification_number
                      ? "border-red-300"
                      : "border-gray-300"
                  }`}
                  placeholder="VAT123456789"
                  maxLength="20"
                  style={{ textTransform: "uppercase" }}
                  onInput={(e) => {
                    e.target.value = e.target.value
                      .toUpperCase()
                      .replace(/[^A-Z0-9\-]/g, "");
                  }}
                />
                {errors.tax_identification_number && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.tax_identification_number}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  6-20 characters (A-Z, 0-9, -)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Registration Number{" "}
                  <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">(CRN)</span>
                </label>
                <input
                  type="text"
                  name="company_registration_number"
                  required
                  value={formData.company_registration_number}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                    errors.company_registration_number
                      ? "border-red-300"
                      : "border-gray-300"
                  }`}
                  placeholder="CRN12345/67890"
                  maxLength="30"
                  style={{ textTransform: "uppercase" }}
                  onInput={(e) => {
                    e.target.value = e.target.value
                      .toUpperCase()
                      .replace(/[^A-Z0-9\-\/]/g, "");
                  }}
                />
                {errors.company_registration_number && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.company_registration_number}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  5-30 characters (A-Z, 0-9, -, /)
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Identification & Compliance */}
      <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
            2
          </span>
          Identification & Compliance
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {formData.company_type === "OVERSEAS" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                International Unique ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="international_unique_id"
                required
                value={formData.international_unique_id}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                  errors.international_unique_id
                    ? "border-red-300"
                    : "border-gray-300"
                }`}
                placeholder="VAT/DUNS/EIN/etc."
                maxLength="20"
              />
              {errors.international_unique_id && (
                <p className="text-red-500 text-sm mt-1">
                  {errors.international_unique_id}
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Verification Source <span className="text-red-500">*</span>
            </label>
            <select
              name="verification_source"
              required
              value={formData.verification_source}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.verification_source
                  ? "border-red-300"
                  : "border-gray-300"
              }`}
            >
              <option value="">Select verification source</option>
              {verificationSources.map((source) => (
                <option key={source.value} value={source.value}>
                  {source.label}
                </option>
              ))}
            </select>
            {errors.verification_source && (
              <p className="text-red-500 text-sm mt-1">
                {errors.verification_source}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Verification Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              name="verification_date"
              required
              value={formData.verification_date}
              onChange={handleInputChange}
              max={new Date().toISOString().split("T")[0]}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.verification_date ? "border-red-300" : "border-gray-300"
              }`}
            />
            {errors.verification_date && (
              <p className="text-red-500 text-sm mt-1">
                {errors.verification_date}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Verified By (Admin Name) <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="verified_by"
              required
              value={formData.verified_by}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.verified_by ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="Admin username/name"
            />
            {errors.verified_by && (
              <p className="text-red-500 text-sm mt-1">{errors.verified_by}</p>
            )}
          </div>
        </div>

        {/* Supporting Documents */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Supporting Documents <span className="text-red-500">*</span>
            <span className="text-xs text-gray-500 ml-2">
              (PDF, JPEG, PNG only, max 10MB each)
            </span>
          </label>
          <input
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileUpload}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {errors.supporting_documents && (
            <p className="text-red-500 text-sm mt-1">
              {errors.supporting_documents}
            </p>
          )}

          {/* Display uploaded files */}
          <div className="mt-2 space-y-1">
            {uploadedFiles.length > 0 &&
              uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-gray-100 px-3 py-2 rounded"
                >
                  <span className="text-sm">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            {console.log(formData.supporting_documents.length > 0)}
            {formData.supporting_documents.length > 0
              ? formData.supporting_documents.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-gray-100 px-3 py-2 rounded"
                  >
                    <span className="text-sm">
                      <a href={file} target="_blank" rel="noopener noreferrer">
                        {file.split("/").pop()} {/* show just the filename */}
                      </a>
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))
              : console.log(formData.supporting_documents)}
          </div>
        </div>
      </div>

      {/* Registered Address */}
      <div className="bg-purple-50 p-6 rounded-lg border-l-4 border-purple-500">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="bg-purple-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
            3
          </span>
          Registered Address (All Required)
        </h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Complete Address <span className="text-red-500">*</span>
            </label>
            <textarea
              name="address"
              required
              value={formData.address}
              onChange={handleInputChange}
              rows="3"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.address ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="Enter complete registered address (minimum 10 characters)"
            />
            {errors.address && (
              <p className="text-red-500 text-sm mt-1">{errors.address}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                name="country"
                required
                value={formData.country}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.country ? "border-red-300" : "border-gray-300"
                }`}
              >
                {Object.keys(countryStateMasters).map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
              {errors.country && (
                <p className="text-red-500 text-sm mt-1">{errors.country}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State <span className="text-red-500">*</span>
              </label>
              <select
                name="state"
                required
                value={formData.state}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.state ? "border-red-300" : "border-gray-300"
                }`}
              >
                <option value="">Select state</option>
                {getStatesForCountry().map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
              {errors.state && (
                <p className="text-red-500 text-sm mt-1">{errors.state}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="city"
                required
                value={formData.city}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.city ? "border-red-300" : "border-gray-300"
                }`}
                placeholder="Enter city"
              />
              {errors.city && (
                <p className="text-red-500 text-sm mt-1">{errors.city}</p>
              )}
            </div>
          </div>

          <div className="w-full md:w-1/3">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              PIN Code <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="pin_code"
              required
              value={formData.pin_code}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.pin_code ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="000000"
              maxLength="6"
              pattern="[0-9]{6}"
            />
            {errors.pin_code && (
              <p className="text-red-500 text-sm mt-1">{errors.pin_code}</p>
            )}
          </div>
        </div>
      </div>

      {/* Hierarchy & Linkages */}
      <div className="bg-yellow-50 p-6 rounded-lg border-l-4 border-yellow-500">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="bg-yellow-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
            4
          </span>
          Hierarchy & Linkages (All Required)
        </h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parent-Child Mapping Confirmation{" "}
              <span className="text-red-500">*</span>
            </label>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="parent_child_mapping_confirmed"
                  value="true"
                  checked={formData.parent_child_mapping_confirmed === true}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      parent_child_mapping_confirmed: true,
                    }))
                  }
                  className="mr-2"
                  required
                />
                Yes
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="parent_child_mapping_confirmed"
                  value="false"
                  checked={formData.parent_child_mapping_confirmed === false}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      parent_child_mapping_confirmed: false,
                    }))
                  }
                  className="mr-2"
                  required
                />
                No
              </label>
            </div>
            {errors.parent_child_mapping_confirmed && (
              <p className="text-red-500 text-sm mt-1">
                {errors.parent_child_mapping_confirmed}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Linked Subsidiaries <span className="text-red-500">*</span>
            </label>
            <select
              name="linked_subsidiaries"
              multiple
              value={formData.linked_subsidiaries || ["None"]}
              onChange={(e) => {
                let values = Array.from(
                  e.target.selectedOptions,
                  (option) => option.value
                );

                // If "None" is selected with other options, remove "None"
                if (values.includes("None") && values.length > 1) {
                  values = values.filter((v) => v !== "None");
                }

                // If nothing is selected, default back to "None"
                if (values.length === 0) {
                  values = ["None"];
                }

                setFormData((prev) => ({
                  ...prev,
                  linked_subsidiaries: values,
                }));
              }}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.linked_subsidiaries
                  ? "border-red-300"
                  : "border-gray-300"
              }`}
              size="4"
            >
              <option value="None">None</option>
              {companies
                .filter((c) => c.id !== company?.id)
                .map((c) => (
                  <option key={c.id} value={c.name}>
                    {c.name}
                  </option>
                ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Hold Ctrl (Cmd on Mac) to select multiple. Select "None" if no
              subsidiaries.
            </p>
            {errors.linked_subsidiaries && (
              <p className="text-red-500 text-sm mt-1">
                {errors.linked_subsidiaries}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Associated Channel Partner
            </label>
            <input
              type="text"
              name="associated_channel_partner"
              value={formData.associated_channel_partner}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter channel partner name (if applicable)"
            />
          </div>
        </div>
      </div>

      {/* Optional Information */}
      <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-gray-400">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="bg-gray-400 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
            5
          </span>
          Additional Information (Optional)
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Website
            </label>
            <input
              type="url"
              name="website"
              value={formData.website}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="https://company.com"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Brief description about the company..."
            />
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          // disabled={
          //   loading ||
          //   Object.keys(errors).length > 0 ||
          //   !formData.name ||
          //   !formData.industry ||
          //   !formData.sub_industry ||
          //   !formData.company_type
          // }
          className="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {company ? "Updating..." : "Creating..."}
            </div>
          ) : company ? (
            "Update Company"
          ) : (
            "Create Company"
          )}
        </button>
      </div>
    </form>
  );
};

export default CompanyForm;
