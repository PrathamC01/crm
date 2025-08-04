import React, { useState } from 'react';
import { OpportunityList, OpportunityForm, OpportunityView } from './modules/opportunity';

const OpportunityManagement = () => {
  const [currentView, setCurrentView] = useState('list');
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);

  const handleCreate = () => {
    setSelectedOpportunity(null);
    setCurrentView('form');
  };

  const handleEdit = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setCurrentView('form');
  };

  const handleView = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setCurrentView('view');
  };

  const handleSave = (savedOpportunity) => {
    setCurrentView('list');
    setSelectedOpportunity(null);
  };

  const handleCancel = () => {
    setCurrentView('list');
    setSelectedOpportunity(null);
  };

  const handleDelete = (opportunityId) => {
    // Delete is handled within OpportunityList component
    // This could be used for additional logic if needed
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 text-left">Opportunity Management</h2>
          <p className="text-gray-600">Manage sales opportunities through the stage-driven workflow</p>
        </div>
        {currentView === 'list' && (
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <span className="mr-2">+</span>
            Add Opportunity
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'list' && (
        <OpportunityList
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
        />
      )}

      {currentView === 'form' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-6">
            {selectedOpportunity ? 'Edit Opportunity' : 'Create New Opportunity'}
          </h3>
          <OpportunityForm
            opportunity={selectedOpportunity}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      {currentView === 'view' && (
        <div className="bg-white rounded-lg shadow p-6">
          <OpportunityView
            opportunity={selectedOpportunity}
            onEdit={handleEdit}
            onClose={handleCancel}
          />
        </div>
      )}

      {/* Business Rules Info */}
      {currentView === 'list' && (
        <div className="bg-purple-50 rounded-lg p-4">
          <h4 className="font-medium text-purple-900 mb-2">Opportunity Workflow</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-purple-800">
            <div>
              <p className="font-semibold">Stage Workflow:</p>
              <p>L1 → L2 → L3 → L4 → L5 → L6 → L7</p>
            </div>
            <div>
              <p className="font-semibold">Amount Validation:</p>
              <p>≥₹10L requires justification</p>
            </div>
            <div>
              <p className="font-semibold">Decision Makers:</p>
              <p>Only Decision Maker contacts allowed</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OpportunityManagement;