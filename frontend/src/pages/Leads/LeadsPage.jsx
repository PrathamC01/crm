import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import LeadForm from '../../components/leads/LeadForm';

const LeadsPage = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [editingLead, setEditingLead] = useState(null);
  const [stats, setStats] = useState({});
  const [filters, setFilters] = useState({
    status: '',
    search: ''
  });

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'New', label: 'New' },
    { value: 'Contacted', label: 'Contacted' },
    { value: 'Qualified', label: 'Qualified' },
    { value: 'Unqualified', label: 'Unqualified' },
    { value: 'Converted', label: 'Converted' },
    { value: 'Rejected', label: 'Rejected' }
  ];

  const leadColumns = [
    {
      key: 'project_title',
      label: 'Project Title',
      sortable: true,
      render: (lead) => (
        <div>
          <div className="font-medium text-gray-900">{lead.project_title}</div>
          <div className="text-sm text-gray-500">{lead.company_name}</div>
        </div>
      )
    },
    {
      key: 'lead_source',
      label: 'Source',
      render: (lead) => (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
          {lead.lead_source}
        </span>
      )
    },
    {
      key: 'status',
      label: 'Status',
      render: (lead) => {
        const statusColors = {
          'New': 'bg-gray-100 text-gray-800',
          'Contacted': 'bg-blue-100 text-blue-800',
          'Qualified': 'bg-green-100 text-green-800',
          'Unqualified': 'bg-red-100 text-red-800',
          'Converted': 'bg-purple-100 text-purple-800',
          'Rejected': 'bg-red-100 text-red-800'
        };
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[lead.status] || 'bg-gray-100 text-gray-800'}`}>
            {lead.status}
          </span>
        );
      }
    },
    {
      key: 'priority',
      label: 'Priority',
      render: (lead) => {
        const priorityColors = {
          'High': 'text-red-600',
          'Medium': 'text-yellow-600',
          'Low': 'text-green-600'
        };
        return (
          <span className={`font-medium ${priorityColors[lead.priority] || 'text-gray-600'}`}>
            {lead.priority}
          </span>
        );
      }
    },
    {
      key: 'expected_revenue',
      label: 'Expected Revenue',
      render: (lead) => (
        <div className="text-right">
          <div className="font-medium">₹{Number(lead.expected_revenue).toLocaleString()}</div>
          <div className="text-sm text-gray-500">{lead.revenue_currency}</div>
        </div>
      )
    },
    {
      key: 'created_on',
      label: 'Created',
      render: (lead) => new Date(lead.created_on).toLocaleDateString()
    }
  ];

  useEffect(() => {
    fetchLeads();
    fetchStats();
  }, [filters]);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.leads.getLeads(filters);
      if (response.data?.data?.leads) {
        setLeads(response.data.data.leads);
      }
    } catch (error) {
      console.error('Error fetching leads:', error);
      // For now, set empty array on error
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiMethods.leads.getLeads(); // Get stats endpoint
      if (response.data?.data) {
        setStats({
          total: response.data.data.total || 0,
          new: 0,
          qualified: 0,
          converted: 0
        });
      }
    } catch (error) {
      console.error('Error fetching lead stats:', error);
      setStats({ total: 0, new: 0, qualified: 0, converted: 0 });
    }
  };

  const handleStatusChange = async (leadId, newStatus) => {
    try {
      await apiMethods.leads.updateLeadStatus(leadId, newStatus);
      fetchLeads(); // Refresh the list
    } catch (error) {
      console.error('Error updating lead status:', error);
    }
  };

  const handleViewLead = (lead) => {
    setSelectedLead(lead);
  };

  const handleEditLead = (lead) => {
    setEditingLead(lead);
  };

  const handleConvertLead = async (lead) => {
    if (lead.status === 'Qualified') {
      try {
        // Call conversion API
        const response = await apiMethods.leads.convertToOpportunity(lead.id);
        if (response.data?.status) {
          alert('Lead converted to opportunity successfully!');
          fetchLeads(); // Refresh the list
        }
      } catch (error) {
        console.error('Error converting lead:', error);
        alert('Failed to convert lead to opportunity');
      }
    }
  };

  const handleCreateLead = () => {
    setShowCreateModal(true);
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewLead,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Convert',
      onClick: (lead) => {
        if (lead.status === 'Qualified') {
          // Handle conversion to opportunity
          console.log('Converting lead to opportunity:', lead.id);
        }
      },
      className: 'text-green-600 hover:text-green-900',
      show: (lead) => lead.status === 'Qualified'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Leads Management</h1>
        <button
          onClick={handleCreateLead}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Lead
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Leads</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">New Leads</p>
              <p className="text-3xl font-bold text-blue-600">{stats.new}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Qualified</p>
              <p className="text-3xl font-bold text-green-600">{stats.qualified}</p>
            </div>
            <div className="p-3 rounded-md bg-green-50">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Converted</p>
              <p className="text-3xl font-bold text-purple-600">{stats.converted}</p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search leads..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={leadColumns}
            data={leads}
            actions={actions}
            emptyMessage="No leads found. Create your first lead to get started."
          />
        )}
      </div>

      {/* Create Lead Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Lead"
        size="large"
      >
        <LeadForm
          onSave={(newLead) => {
            setShowCreateModal(false);
            fetchLeads(); // Refresh the leads list
          }}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* Lead Detail Modal */}
      <Modal
        isOpen={!!selectedLead}
        onClose={() => setSelectedLead(null)}
        title="Lead Details"
        size="xl"
      >
        {selectedLead && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Project Title</h3>
                <p className="text-gray-900">{selectedLead.project_title}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Company</h3>
                <p className="text-gray-900">{selectedLead.company_name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedLead.status}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Expected Revenue</h3>
                <p className="text-gray-900">₹{Number(selectedLead.expected_revenue).toLocaleString()}</p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedLead(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              {selectedLead.status === 'Qualified' && (
                <button
                  onClick={() => {
                    // Handle conversion
                    console.log('Converting to opportunity');
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Convert to Opportunity
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default LeadsPage;