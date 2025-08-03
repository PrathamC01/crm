import React from 'react';

const OpportunityManagement = () => {
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Opportunity Management</h3>
      <p className="text-gray-600">Opportunity management functionality coming soon...</p>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-green-50 rounded-lg">
          <h4 className="font-medium text-green-900">Stage Workflow</h4>
          <p className="text-green-700 text-sm mt-1">L1 → L2 → L3 → L4 → L5 → L6 → L7</p>
        </div>
        <div className="p-4 bg-yellow-50 rounded-lg">
          <h4 className="font-medium text-yellow-900">Amount Validation</h4>
          <p className="text-yellow-700 text-sm mt-1">≥₹10L requires justification</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <h4 className="font-medium text-purple-900">Decision Makers</h4>
          <p className="text-purple-700 text-sm mt-1">Only Decision Maker contacts allowed</p>
        </div>
      </div>
    </div>
  );
};

export default OpportunityManagement;