import React, { useState } from 'react';
import { LeadList, LeadForm, LeadView } from './modules/lead';

const LeadManagement = () => {
  const [currentView, setCurrentView] = useState('list');
  const [selectedLead, setSelectedLead] = useState(null);

  const handleCreate = () => {
    setSelectedLead(null);
    setCurrentView('form');
  };

  const handleEdit = (lead) => {
    setSelectedLead(lead);
    setCurrentView('form');
  };

  const handleView = (lead) => {
    setSelectedLead(lead);
    setCurrentView('view');
  };

  const handleSave = (savedLead) => {
    setCurrentView('list');
    setSelectedLead(null);
  };

  const handleCancel = () => {
    setCurrentView('list');
    setSelectedLead(null);
  };

  const handleDelete = (leadId) => {
    // Delete is handled within LeadList component
    // This could be used for additional logic if needed
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Lead Management</h2>
          <p className="text-gray-600">Track and manage sales leads through the pipeline</p>
        </div>
        {currentView === 'list' && (
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <span className="mr-2">+</span>
            Add Lead
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'list' && (
        <LeadList
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
        />
      )}

      {currentView === 'form' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-6">
            {selectedLead ? 'Edit Lead' : 'Create New Lead'}
          </h3>
          <LeadForm
            lead={selectedLead}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      {currentView === 'view' && (
        <div className="bg-white rounded-lg shadow p-6">
          <LeadView
            lead={selectedLead}
            onEdit={handleEdit}
            onClose={handleCancel}
          />
        </div>
      )}

      {/* Business Flow Info */}
      {currentView === 'list' && (
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="font-medium text-green-900 mb-2">Lead to Opportunity Conversion</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-800">
            <div>
              <p>• Leads must be "Qualified" status to convert</p>
              <p>• Requires Decision Maker contact for conversion</p>
            </div>
            <div>
              <p>• Auto-close: Inactive leads (4+ weeks) automatically dropped</p>
              <p>• Conversion creates new opportunity in L1 stage</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadManagement;