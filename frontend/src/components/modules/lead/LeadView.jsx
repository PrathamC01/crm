import React from 'react';

const LeadView = ({ lead, onEdit, onClose }) => {
  if (!lead) return null;

  const getStatusColor = (status) => {
    const colors = {
      'New': 'bg-blue-100 text-blue-800',
      'Contacted': 'bg-yellow-100 text-yellow-800',
      'Qualified': 'bg-green-100 text-green-800',
      'Proposal': 'bg-purple-100 text-purple-800',
      'Negotiation': 'bg-orange-100 text-orange-800',
      'Closed Won': 'bg-green-200 text-green-900',
      'Closed Lost': 'bg-red-100 text-red-800',
      'Dropped': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'Urgent': 'bg-red-100 text-red-800',
      'High': 'bg-red-50 text-red-700',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-gray-100 text-gray-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{lead.company_name}</h3>
          {lead.location && (
            <p className="text-gray-600 mt-1">📍 {lead.location}</p>
          )}
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => onEdit(lead)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit Lead
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Lead Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Lead Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Lead Source</label>
            <p className="text-gray-900">{lead.lead_source}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Sales Person</label>
            <p className="text-gray-900">{lead.sales_person_name}</p>
          </div>

          {lead.expected_close_date && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Expected Close Date</label>
              <p className="text-gray-900">{new Date(lead.expected_close_date).toLocaleDateString()}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Last Activity</label>
            <p className="text-gray-900">{new Date(lead.last_activity_date).toLocaleDateString()}</p>
          </div>
        </div>
      </div>

      {/* Status & Priority */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Status & Priority</h4>
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-2">Status</label>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(lead.status)}`}>
              {lead.status}
            </span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-2">Priority</label>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getPriorityColor(lead.priority)}`}>
              {lead.priority}
            </span>
          </div>
        </div>
      </div>

      {/* Notes */}
      {lead.notes && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Notes</h4>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{lead.notes}</p>
          </div>
        </div>
      )}

      {/* Business Flow Information */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-blue-900 mb-4">Business Flow & Conversion</h4>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Leads can be converted to Opportunities when status is "Qualified"</p>
          <p>• Opportunities must be linked to a Decision Maker contact</p>
          <p>• Auto-close mechanism: Leads inactive for 4+ weeks will be automatically dropped</p>
          {lead.status === 'Qualified' && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium">✅ This lead is qualified and ready for conversion to opportunity!</p>
            </div>
          )}
        </div>
      </div>

      {/* System Information */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">System Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Lead ID</label>
            <p className="text-gray-900 font-mono text-sm">{lead.id}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              lead.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {lead.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Created On</label>
            <p className="text-gray-900">{new Date(lead.created_on).toLocaleDateString()}</p>
          </div>
          
          {lead.updated_on && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Last Updated</label>
              <p className="text-gray-900">{new Date(lead.updated_on).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeadView;