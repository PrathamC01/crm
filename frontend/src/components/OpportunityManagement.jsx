import React, { useState } from 'react';
import { 
  EnhancedOpportunityForm, 
  EnhancedOpportunityList, 
  EnhancedOpportunityView 
} from './modules/opportunity';

const OpportunityManagement = () => {
  const [view, setView] = useState('list'); // 'list', 'form', 'view'
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);

  const handleAddOpportunity = () => {
    setSelectedOpportunity(null);
    setView('form');
  };

  const handleEditOpportunity = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setView('form');
  };

  const handleViewOpportunity = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setView('view');
  };

  const handleSave = (savedOpportunity) => {
    console.log('Opportunity saved:', savedOpportunity);
    setView('list');
    setSelectedOpportunity(null);
  };

  const handleCancel = () => {
    setView('list');
    setSelectedOpportunity(null);
  };

  const handleDelete = (opportunity) => {
    console.log('Delete opportunity:', opportunity);
    // The delete is handled in the list component itself
  };

  const handleClose = () => {
    setView('list');
    setSelectedOpportunity(null);
  };

  const renderHeader = () => (
    <div className="mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {view === 'form' 
              ? (selectedOpportunity ? 'Edit Opportunity' : 'Add New Opportunity')
              : view === 'view'
              ? 'Opportunity Details'
              : 'Opportunity Management'
            }
          </h1>
          <p className="text-gray-600 mt-1">
            {view === 'form' 
              ? 'Fill in the comprehensive opportunity details with stage-specific information'
              : view === 'view'
              ? 'Complete opportunity information and stage progression'
              : 'Manage your sales opportunities with enhanced tracking and stage management'
            }
          </p>
        </div>
        {view === 'list' && (
          <button
            onClick={handleAddOpportunity}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <span className="text-lg">+</span>
            <span>Add New Opportunity</span>
          </button>
        )}
        {(view === 'form' || view === 'view') && (
          <button
            onClick={handleCancel}
            className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            ← Back to List
          </button>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'form':
        return (
          <EnhancedOpportunityForm
            opportunity={selectedOpportunity}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        );
      case 'view':
        return (
          <EnhancedOpportunityView
            opportunity={selectedOpportunity}
            onEdit={handleEditOpportunity}
            onClose={handleClose}
          />
        );
      default:
        return (
          <EnhancedOpportunityList
            onEdit={handleEditOpportunity}
            onView={handleViewOpportunity}
            onDelete={handleDelete}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {renderHeader()}
      
      {/* Quick Stats - Only show on list view */}
      {view === 'list' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <div className="ml-4">
                <div className="text-sm font-medium text-gray-500">Total Opportunities</div>
                <div className="text-2xl font-bold text-gray-900">-</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 text-green-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                </svg>
              </div>
              <div className="ml-4">
                <div className="text-sm font-medium text-gray-500">Pipeline Value</div>
                <div className="text-2xl font-bold text-gray-900">₹-</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-100 text-purple-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
              </div>
              <div className="ml-4">
                <div className="text-sm font-medium text-gray-500">Win Rate</div>
                <div className="text-2xl font-bold text-gray-900">-%</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div className="ml-4">
                <div className="text-sm font-medium text-gray-500">Avg. Deal Size</div>
                <div className="text-2xl font-bold text-gray-900">₹-</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow">
        {renderContent()}
      </div>

      {/* Stage Legend - Only show on list view */}
      {view === 'list' && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Opportunity Stages</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span><strong>L1 - Qualification (15%)</strong>: Requirement gathering, Go/No-Go decisions</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-indigo-500 rounded-full"></div>
              <span><strong>L2 - Need Analysis (40%)</strong>: Demos, presentations, customer meetings</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span><strong>L3 - Proposal (60%)</strong>: Quotations, proposals, POCs, approvals</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-pink-500 rounded-full"></div>
              <span><strong>L4 - Negotiation (80%)</strong>: Commercial discussions and final approvals</span>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span><strong>L5 - Won (100%)</strong>: Kick-off meetings, LOI processing, delivery handoff</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span><strong>L6 - Lost</strong>: Opportunity lost to competitors or other reasons</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span><strong>L7 - Dropped</strong>: Opportunity dropped due to internal decisions</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OpportunityManagement;