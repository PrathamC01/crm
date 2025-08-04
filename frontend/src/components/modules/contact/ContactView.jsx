import React from 'react';

const ContactView = ({ contact, onEdit, onClose }) => {
  if (!contact) return null;

  const getRoleTypeColor = (roleType) => {
    switch (roleType) {
      case 'Decision Maker':
        return 'bg-green-100 text-green-800';
      case 'Admin':
        return 'bg-blue-100 text-blue-800';
      case 'Influencer':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold text-gray-900 text-left">{contact.full_name}</h3>
          {contact.designation && (
            <p className="text-gray-600 mt-1">{contact.designation}</p>
          )}
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => onEdit(contact)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit Contact
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Email</label>
            <p className="text-gray-900">{contact.email}</p>
          </div>
          
          {contact.phone_number && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Phone Number</label>
              <p className="text-gray-900">{contact.phone_number}</p>
            </div>
          )}
        </div>
      </div>

      {/* Company & Role Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Company & Role</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Company</label>
            <p className="text-gray-900 font-medium">{contact.company_name}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Role Type</label>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getRoleTypeColor(contact.role_type)}`}>
              {contact.role_type}
            </span>
          </div>
        </div>
      </div>

      {/* Business Card */}
      {contact.business_card_path && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Business Card</h4>
          <div className="text-sm text-gray-600">
            <a 
              href={contact.business_card_path} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              View Business Card
            </a>
          </div>
        </div>
      )}

      {/* System Information */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">System Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Contact ID</label>
            <p className="text-gray-900 font-mono text-sm">{contact.id}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              contact.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {contact.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Created On</label>
            <p className="text-gray-900">{new Date(contact.created_on).toLocaleDateString()}</p>
          </div>
          
          {contact.updated_on && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Last Updated</label>
              <p className="text-gray-900">{new Date(contact.updated_on).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContactView;