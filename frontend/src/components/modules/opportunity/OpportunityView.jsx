import React from 'react';

const OpportunityView = ({ opportunity, onEdit, onClose }) => {
  if (!opportunity) return null;

  const getStageColor = (stage) => {
    const colors = {
      'L1': 'bg-blue-100 text-blue-800',
      'L2': 'bg-indigo-100 text-indigo-800',
      'L3': 'bg-purple-100 text-purple-800',
      'L4': 'bg-pink-100 text-pink-800',
      'L5': 'bg-red-100 text-red-800',
      'L6': 'bg-orange-100 text-orange-800',
      'L7': 'bg-yellow-100 text-yellow-800'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status) => {
    const colors = {
      'Open': 'bg-green-100 text-green-800',
      'Won': 'bg-green-200 text-green-900',
      'Lost': 'bg-red-100 text-red-800',
      'Dropped': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStageLabel = (stage) => {
    const labels = {
      'L1': 'L1 - Initial',
      'L2': 'L2 - Qualified',
      'L3': 'L3 - Needs Analysis',
      'L4': 'L4 - Proposal',
      'L5': 'L5 - Negotiation',
      'L6': 'L6 - Decision',
      'L7': 'L7 - Closing'
    };
    return labels[stage] || stage;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{opportunity.name}</h3>
          <p className="text-gray-600 mt-1">{opportunity.company_name}</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => onEdit(opportunity)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit Opportunity
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Amount</h4>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(opportunity.amount)}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Stage</h4>
          <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStageColor(opportunity.stage)}`}>
            {getStageLabel(opportunity.stage)}
          </span>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Probability</h4>
          <p className="text-2xl font-bold text-gray-900">{opportunity.probability}%</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Scoring</h4>
          <p className="text-2xl font-bold text-gray-900">{opportunity.scoring}/100</p>
        </div>
      </div>

      {/* Company & Contact Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Company & Contact</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Company</label>
            <p className="text-gray-900 font-medium">{opportunity.company_name}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Decision Maker Contact</label>
            <div>
              <p className="text-gray-900 font-medium">{opportunity.contact_name}</p>
              {opportunity.contact_email && (
                <p className="text-gray-600 text-sm">{opportunity.contact_email}</p>
              )}
            </div>
          </div>

          {opportunity.lead_source && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Lead Source</label>
              <p className="text-gray-900">{opportunity.lead_source}</p>
            </div>
          )}

          {opportunity.created_by_name && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Created By</label>
              <p className="text-gray-900">{opportunity.created_by_name}</p>
            </div>
          )}
        </div>
      </div>

      {/* Status & Timeline */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Status & Timeline</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-2">Status</label>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(opportunity.status)}`}>
              {opportunity.status}
            </span>
          </div>

          {opportunity.close_date && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Expected Close Date</label>
              <p className="text-gray-900">{new Date(opportunity.close_date).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>

      {/* Financial Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Financial Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Opportunity Value</label>
            <p className="text-gray-900 text-xl font-semibold">{formatCurrency(opportunity.amount)}</p>
          </div>
          
          {opportunity.costing && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Costing</label>
              <p className="text-gray-900 text-xl font-semibold">{formatCurrency(opportunity.costing)}</p>
            </div>
          )}
        </div>

        {opportunity.costing && opportunity.amount && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-500 mb-1">Estimated Margin</label>
            <p className="text-gray-900 font-semibold">
              {formatCurrency(opportunity.amount - opportunity.costing)} 
              ({(((opportunity.amount - opportunity.costing) / opportunity.amount) * 100).toFixed(1)}%)
            </p>
          </div>
        )}
      </div>

      {/* Justification */}
      {opportunity.justification && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Justification</h4>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{opportunity.justification}</p>
          </div>
        </div>
      )}

      {/* Notes */}
      {opportunity.notes && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Notes</h4>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{opportunity.notes}</p>
          </div>
        </div>
      )}

      {/* Stage Progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Stage Progress</h4>
        <div className="flex justify-between items-center">
          {['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'].map((stage, index) => {
            const isActive = stage === opportunity.stage;
            const isCompleted = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'].indexOf(stage) < 
                               ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'].indexOf(opportunity.stage);
            
            return (
              <div key={stage} className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  isActive ? 'bg-blue-600 text-white' : 
                  isCompleted ? 'bg-green-600 text-white' : 
                  'bg-gray-200 text-gray-600'
                }`}>
                  {stage}
                </div>
                <span className="text-xs text-gray-500 mt-1">{getStageLabel(stage).split(' - ')[1]}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Business Rules Information */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-blue-900 mb-4">Business Rules & Validations</h4>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Opportunities must be linked to Decision Maker contacts only</p>
          <p>• Amounts ≥₹10L require justification</p>
          <p>• Stage-driven workflow: L1 → L2 → L3 → L4 → L5 → L6 → L7</p>
          <p>• Scoring range: 0-100 (indicates opportunity quality)</p>
          <p>• Probability helps in revenue forecasting</p>
        </div>
        
        {opportunity.amount >= 1000000 && opportunity.justification && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">✅ High-value opportunity with required justification</p>
          </div>
        )}
      </div>

      {/* System Information */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">System Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Opportunity ID</label>
            <p className="text-gray-900 font-mono text-sm">{opportunity.id}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              opportunity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {opportunity.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Created On</label>
            <p className="text-gray-900">{new Date(opportunity.created_on).toLocaleDateString()}</p>
          </div>
          
          {opportunity.updated_on && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Last Updated</label>
              <p className="text-gray-900">{new Date(opportunity.updated_on).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpportunityView;