import React, { useState, useEffect } from "react";
import { apiRequest, uploadFile } from "../../../utils/api";

const CompanyForm = ({ company, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: "",
    gst_number: "",
    pan_number: "",
    parent_company_id: null,
    industry_category: "",
    address: "",
    city: "",
    state: "",
    country: "India",
    postal_code: "",
    website: "",
    description: "",
  });

  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [documents, setDocuments] = useState([]);
  const [uploadingDoc, setUploadingDoc] = useState(false);

  useEffect(() => {
    if (company) {
      setFormData({
        name: company.name || "",
        gst_number: company.gst_number || "",
        pan_number: company.pan_number || "",
        parent_company_id: company.parent_company_id || "",
        industry_category: company.industry_category || "",
        address: company.address || "",
        city: company.city || "",
        state: company.state || "",
        country: company.country || "India",
        postal_code: company.postal_code || "",
        website: company.website || "",
        description: company.description || "",
      });
      // Load documents if editing existing company
      if (company.id) {
        fetchDocuments(company.id);
      }
    }
    fetchCompanies();
  }, [company]);

  const fetchCompanies = async () => {
    try {
      const response = await apiRequest("/api/companies");
      if (response.status) {
        setCompanies(response.data.companies || []);
      }
    } catch (err) {
      console.error("Failed to fetch companies:", err);
    }
  };

  const fetchDocuments = async (companyId) => {
    try {
      const response = await apiRequest(`/api/companies/${companyId}/documents`);
      if (response.status) {
        setDocuments(response.data.documents || []);
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Company name is required";
    }

    if (
      formData.gst_number &&
      !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$/.test(
        formData.gst_number
      )
    ) {
      newErrors.gst_number = "Invalid GST format. Expected: 22AAAAA0000A1Z5";
    }

    if (
      formData.pan_number &&
      !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(formData.pan_number)
    ) {
      newErrors.pan_number = "Invalid PAN format. Expected: AAAAA0000A";
    }

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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      const endpoint = company
        ? `/api/companies/${company.id}`
        : "/api/companies";
      const method = company ? "PUT" : "POST";

      const response = await apiRequest(endpoint, {
        method,
        body: JSON.stringify(formData),
      });

      if (response.status) {
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
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    const documentType = e.target.getAttribute('data-doc-type');
    
    if (!file || !company?.id) return;

    setUploadingDoc(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);

      const response = await uploadFile(`/api/companies/${company.id}/upload`, formData);
      
      if (response.status) {
        // Refresh documents list
        fetchDocuments(company.id);
        // Clear file input
        e.target.value = '';
      } else {
        alert('Upload failed: ' + response.message);
      }
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploadingDoc(false);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      const response = await apiRequest(`/api/companies/${company.id}/documents/${documentId}`, {
        method: 'DELETE'
      });

      if (response.status) {
        fetchDocuments(company.id);
      } else {
        alert('Delete failed: ' + response.message);
      }
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const industryCategories = [
    "Technology",
    "Manufacturing",
    "Healthcare",
    "Finance",
    "Education",
    "Retail",
    "Construction",
    "Agriculture",
    "Transportation",
    "Energy",
    "Telecommunications",
    "Media",
    "Real Estate",
    "Hospitality",
    "Other",
  ];

  const indianStates = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
  ];

  const documentTypes = [
    { value: 'GST_CERTIFICATE', label: 'GST Certificate' },
    { value: 'PAN_CARD', label: 'PAN Card' },
    { value: 'INCORPORATION_CERTIFICATE', label: 'Incorporation Certificate' },
    { value: 'TAX_DOCUMENT', label: 'Tax Document' },
    { value: 'BANK_STATEMENT', label: 'Bank Statement' },
    { value: 'OTHER', label: 'Other' }
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
        <h4 className="text-lg font-medium text-gray-900 mb-4">
          Basic Information
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
              name="parent_company_id"
              value={formData.parent_company_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select parent company (optional)</option>
              {companies
                .filter((c) => c.id !== company?.id) // Don't show self as parent
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry Category
            </label>
            <select
              name="industry_category"
              value={formData.industry_category}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select industry</option>
              {industryCategories.map((industry) => (
                <option key={industry} value={industry}>
                  {industry}
                </option>
              ))}
            </select>
          </div>

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
        </div>
      </div>

      {/* Tax Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">
          Tax Information
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              GST Number
            </label>
            <input
              type="text"
              name="gst_number"
              value={formData.gst_number}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                errors.gst_number ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="22AAAAA0000A1Z5"
              maxLength="15"
            />
            {errors.gst_number && (
              <p className="text-red-500 text-sm mt-1">{errors.gst_number}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              PAN Number
            </label>
            <input
              type="text"
              name="pan_number"
              value={formData.pan_number}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono ${
                errors.pan_number ? "border-red-300" : "border-gray-300"
              }`}
              placeholder="AAAAA0000A"
              maxLength="10"
            />
            {errors.pan_number && (
              <p className="text-red-500 text-sm mt-1">{errors.pan_number}</p>
            )}
          </div>
        </div>
      </div>

      {/* Address Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-4">
          Address Information
        </h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Address
            </label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter complete address"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter city"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <select
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select state</option>
                {indianStates.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Postal Code
              </label>
              <input
                type="text"
                name="postal_code"
                value={formData.postal_code}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="000000"
                maxLength="6"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleInputChange}
          rows="4"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Brief description about the company..."
        />
      </div>

      {/* Document Upload - Only show for existing companies */}
      {company?.id && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-lg font-medium text-gray-900 mb-4">
            Documents
          </h4>
          
          {/* Upload Section */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Documents
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documentTypes.map((docType) => (
                <div key={docType.value} className="border border-gray-200 rounded-lg p-3">
                  <label className="text-xs font-medium text-gray-600 mb-2 block">
                    {docType.label}
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    data-doc-type={docType.value}
                    onChange={handleDocumentUpload}
                    disabled={uploadingDoc}
                    className="text-xs text-gray-500 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
              ))}
            </div>
            {uploadingDoc && (
              <p className="text-blue-600 text-sm mt-2">Uploading document...</p>
            )}
          </div>

          {/* Documents List */}
          {documents.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Uploaded Documents</h5>
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between bg-white border border-gray-200 rounded p-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{doc.original_filename}</p>
                      <p className="text-xs text-gray-500">
                        {doc.document_type.replace('_', ' ')} • {Math.round(doc.file_size / 1024)} KB
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <a
                        href={`/api/companies/${company.id}/documents/${doc.id}/download`}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Download
                      </a>
                      <button
                        type="button"
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

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
