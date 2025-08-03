import React from 'react';

const CompanyView = ({ company, onEdit, onClose }) => {
  if (!company) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{company.name}</h3>
          {company.website && (
            <a 
              href={company.website} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              {company.website}
            </a>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(company)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Edit
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>

      {/* Company Information Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Basic Information */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
            Basic Information
          </h4>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Company Name</label>
              <p className="text-gray-900">{company.name}</p>
            </div>
            
            {company.industry_category && (
              <div>
                <label className="text-sm font-medium text-gray-500">Industry</label>
                <p className="text-gray-900">{company.industry_category}</p>
              </div>
            )}
            
            {company.parent_company_name && (
              <div>
                <label className="text-sm font-medium text-gray-500">Parent Company</label>
                <p className="text-gray-900">{company.parent_company_name}</p>
              </div>
            )}
            
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                company.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {company.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* Tax Information */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
            Tax Information
          </h4>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">GST Number</label>
              <p className="text-gray-900 font-mono">
                {company.gst_number || 'Not provided'}
              </p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-500">PAN Number</label>
              <p className="text-gray-900 font-mono">
                {company.pan_number || 'Not provided'}
              </p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-500">Country</label>
              <p className="text-gray-900">{company.country || 'India'}</p>
            </div>
          </div>
        </div>

        {/* Address Information */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-purple-600 rounded-full mr-2"></span>
            Address Information
          </h4>
          <div className="space-y-3">
            {company.address && (
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-gray-900 whitespace-pre-line">{company.address}</p>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              {company.city && (
                <div>
                  <label className="text-sm font-medium text-gray-500">City</label>
                  <p className="text-gray-900">{company.city}</p>
                </div>
              )}
              
              {company.state && (
                <div>
                  <label className="text-sm font-medium text-gray-500">State</label>
                  <p className="text-gray-900">{company.state}</p>
                </div>
              )}
            </div>
            
            {company.postal_code && (
              <div>
                <label className="text-sm font-medium text-gray-500">Postal Code</label>
                <p className="text-gray-900 font-mono">{company.postal_code}</p>
              </div>
            )}
          </div>
        </div>

        {/* Additional Information */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-yellow-600 rounded-full mr-2"></span>
            Additional Information
          </h4>
          <div className="space-y-3">
            {company.description ? (
              <div>
                <label className="text-sm font-medium text-gray-500">Description</label>
                <p className="text-gray-900 whitespace-pre-line">{company.description}</p>
              </div>
            ) : (
              <p className="text-gray-500 italic">No description provided</p>
            )}
            
            <div>
              <label className="text-sm font-medium text-gray-500">Created On</label>
              <p className="text-gray-900">
                {new Date(company.created_on).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
            
            {company.updated_on && new Date(company.updated_on) > new Date(company.created_on) && (
              <div>
                <label className="text-sm font-medium text-gray-500">Last Updated</label>
                <p className="text-gray-900">
                  {new Date(company.updated_on).toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Company Stats/Actions */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">👥</div>
              <div className="text-sm font-medium text-gray-900">View Contacts</div>
              <div className="text-xs text-gray-500">Manage company contacts</div>
            </div>
          </button>
          
          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">🎯</div>
              <div className="text-sm font-medium text-gray-900">View Leads</div>
              <div className="text-xs text-gray-500">Track company leads</div>
            </div>
          </button>
          
          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">💰</div>
              <div className="text-sm font-medium text-gray-900">View Opportunities</div>
              <div className="text-xs text-gray-500">Track opportunities</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompanyView;