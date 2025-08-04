import React, { useState } from 'react';
import { CompanyList, CompanyForm, CompanyView } from './modules/company';

const CompanyManagement = () => {
  const [currentView, setCurrentView] = useState('list');
  const [selectedCompany, setSelectedCompany] = useState(null);

  const handleCreate = () => {
    setSelectedCompany(null);
    setCurrentView('form');
  };

  const handleEdit = (company) => {
    setSelectedCompany(company);
    setCurrentView('form');
  };

  const handleView = (company) => {
    setSelectedCompany(company);
    setCurrentView('view');
  };

  const handleSave = (savedCompany) => {
    setCurrentView('list');
    setSelectedCompany(null);
  };

  const handleCancel = () => {
    setCurrentView('list');
    setSelectedCompany(null);
  };

  const handleDelete = (companyId) => {
    // Delete is handled within CompanyList component
    // This could be used for additional logic if needed
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 text-left">Company Management</h2>
          <p className="text-gray-600">Manage companies with GST/PAN compliance</p>
        </div>
        {currentView === 'list' && (
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <span className="mr-2">+</span>
            Add Company
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'list' && (
        <CompanyList
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
        />
      )}

      {currentView === 'form' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-6">
            {selectedCompany ? 'Edit Company' : 'Create New Company'}
          </h3>
          <CompanyForm
            company={selectedCompany}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      {currentView === 'view' && (
        <div className="bg-white rounded-lg shadow p-6">
          <CompanyView
            company={selectedCompany}
            onEdit={handleEdit}
            onClose={handleCancel}
          />
        </div>
      )}
    </div>
  );
};

export default CompanyManagement;