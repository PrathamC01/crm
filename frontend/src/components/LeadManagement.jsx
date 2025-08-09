import React, { useState, useEffect } from 'react';
import { AddNewLeadForm, LeadList, LeadView } from './modules/lead';
import { apiRequest } from '../utils/api';

const LeadManagement = () => {
  const [view, setView] = useState('list'); // 'list', 'form', 'view'
  const [selectedLead, setSelectedLead] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    qualified: 0,
    converted: 0,
    value: 0
  });

  useEffect(() => {
    if (view === 'list') {
      fetchLeads();
      fetchStats();
    }
  }, [view]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await apiRequest('/api/leads');
      if (response.status) {
        setLeads(response.data.leads || []);
      }
    } catch (err) {
      console.error('Failed to fetch leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiRequest('/api/leads/stats');
      if (response.status) {
        setStats(response.data || {
          total: 0,
          qualified: 0,
          converted: 0,
          value: 0
        });
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleAddLead = () => {
    setSelectedLead(null);
    setView('form');
  };

  const handleEditLead = (lead) => {
    setSelectedLead(lead);
    setView('form');
  };

  const handleViewLead = (lead) => {
    setSelectedLead(lead);
    setView('view');
  };

  const handleSave = (savedLead) => {
    console.log('Lead saved:', savedLead);
    setView('list');
    setSelectedLead(null);
    fetchLeads(); // Refresh the list
  };

  const handleCancel = () => {
    setView('list');
    setSelectedLead(null);
  };

  const handleDelete = async (lead) => {
    if (!window.confirm(`Are you sure you want to delete "${lead.project_title}"?`)) return;
    
    try {
      const response = await apiRequest(`/api/leads/${lead.id}`, {
        method: 'DELETE'
      });

      if (response.status) {
        fetchLeads(); // Refresh the list
      } else {
        alert('Failed to delete lead: ' + response.message);
      }
    } catch (err) {
      alert('Network error occurred');
    }
  };

  const renderHeader = () => (
    <div className="mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {view === 'form' 
              ? (selectedLead ? 'Edit Lead' : 'Add New Lead')
              : view === 'view'
              ? 'Lead Details'
              : 'Lead Management'
            }
          </h1>
          <p className="text-gray-600 mt-1">
            {view === 'form' 
              ? 'Complete multi-tab form with lead details, contacts, tender information, and documents'
              : view === 'view'
              ? 'Comprehensive lead information and conversion tracking'
              : 'Manage your sales leads from capture to opportunity conversion'
            }
          </p>
        </div>
        {view === 'list' && (
          <button
            onClick={handleAddLead}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <span className="text-lg">+</span>
            <span>Add New Lead</span>
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

  const renderQuickStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-blue-100 text-blue-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-500">Total Leads</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-green-100 text-green-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-500">Qualified</div>
            <div className="text-2xl font-bold text-gray-900">{stats.qualified}</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-orange-100 text-orange-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-500">Pending Review</div>
            <div className="text-2xl font-bold text-gray-900">{stats.pending_review || 0}</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-indigo-100 text-indigo-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-500">Approved</div>
            <div className="text-2xl font-bold text-gray-900">{stats.approved_for_conversion || 0}</div>
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
            <div className="text-sm font-medium text-gray-500">Converted</div>
            <div className="text-2xl font-bold text-gray-900">{stats.converted}</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
            </svg>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-500">Total Value</div>
            <div className="text-2xl font-bold text-gray-900">
              ₹{stats.total_value ? new Intl.NumberFormat('en-IN').format(stats.total_value) : '0'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'form':
        return (
          <AddNewLeadForm
            lead={selectedLead}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        );
      case 'view':
        return (
          <LeadView
            lead={selectedLead}
            onEdit={handleEditLead}
            onClose={handleCancel}
          />
        );
      default:
        return (
          <LeadList
            leads={leads}
            loading={loading}
            onEdit={handleEditLead}
            onView={handleViewLead}
            onDelete={handleDelete}
            onRefresh={fetchLeads}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {renderHeader()}
      
      {/* Quick Stats - Only show on list view */}
      {view === 'list' && renderQuickStats()}

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow">
        {renderContent()}
      </div>

      {/* Lead Process Guide - Only show on list view */}
      {view === 'list' && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Management & Conversion Process</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Lead Capture & Management</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• <strong>General Details:</strong> Project info, lead source, company details</li>
                <li>• <strong>Contact Management:</strong> Decision makers and stakeholders</li>
                <li>• <strong>Tender Information:</strong> Fees, dates, submission requirements</li>
                <li>• <strong>Documentation:</strong> Upload tender docs and specifications</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Lead Progression</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• <strong>Qualification:</strong> BANT/CHAMP scoring and validation</li>
                <li>• <strong>Nurturing:</strong> Follow-ups and relationship building</li>
                <li>• <strong>Conversion:</strong> Convert qualified leads to opportunities</li>
                <li>• <strong>Tracking:</strong> Monitor progress and update status</li>
              </ul>
            </div>
          </div>
          
          {/* Conversion Workflow */}
          <div className="mt-6 p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-3">🔸 Convert to Opportunity Workflow</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div className="space-y-2">
                <div className="font-medium text-purple-900">1. Lead Qualified</div>
                <div className="text-purple-800">Lead reaches "Qualified" status through proper assessment</div>
              </div>
              <div className="space-y-2">
                <div className="font-medium text-purple-900">2. Request Conversion</div>
                <div className="text-purple-800">Sales team clicks "Convert to Opportunity" button</div>
              </div>
              <div className="space-y-2">
                <div className="font-medium text-purple-900">3. Admin Review</div>
                <div className="text-purple-800">Admin/Reviewer approves or rejects conversion request</div>
              </div>
              <div className="space-y-2">
                <div className="font-medium text-purple-900">4. Create Opportunity</div>
                <div className="text-purple-800">Approved leads get converted to opportunities with POT-ID</div>
              </div>
            </div>
          </div>

          {/* Role-Based Permissions */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">🔐 Role-Based Permissions</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="font-medium text-blue-900">Sales/User Role:</div>
                <ul className="text-blue-800 mt-1">
                  <li>✅ Can request conversion (after qualification)</li>
                  <li>✅ Can convert (only after admin approval)</li>
                  <li>❌ Cannot approve/reject conversion requests</li>
                </ul>
              </div>
              <div>
                <div className="font-medium text-blue-900">Admin/Reviewer Role:</div>
                <ul className="text-blue-800 mt-1">
                  <li>✅ Can approve/reject conversion requests</li>
                  <li>✅ Can convert without approval requirement</li>
                  <li>✅ Access to Admin Review Panel</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span className="text-sm font-medium text-green-900">Pro Tip:</span>
            </div>
            <p className="text-sm text-green-800 mt-1">
              Use the multi-tab form to capture comprehensive lead information. Once qualified, use the 
              "Convert to Opportunity" workflow with proper admin review to ensure quality opportunity creation 
              and maintain audit trails for all conversions.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadManagement;