import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';

const MyLeadsPage = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    search: ''
  });
  const { user } = useAuth();

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'New', label: 'New' },
    { value: 'Contacted', label: 'Contacted' },
    { value: 'Qualified', label: 'Qualified' },
    { value: 'Unqualified', label: 'Unqualified' }
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
      key: 'status',
      label: 'Status',
      render: (lead) => {
        const statusColors = {
          'New': 'bg-gray-100 text-gray-800',
          'Contacted': 'bg-blue-100 text-blue-800',
          'Qualified': 'bg-green-100 text-green-800',
          'Unqualified': 'bg-red-100 text-red-800'
        };
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[lead.status] || 'bg-gray-100 text-gray-800'}`}>
            {lead.status}
          </span>
        );
      }
    },
    {
      key: 'expected_revenue',
      label: 'Expected Revenue',
      render: (lead) => (
        <div className="text-right font-medium">
          ₹{Number(lead.expected_revenue).toLocaleString()}
        </div>
      )
    },
    {
      key: 'conversion_requested',
      label: 'Conversion Status',
      render: (lead) => {
        if (lead.converted) {
          return <span className="text-purple-600 font-medium">Converted</span>;
        } else if (lead.conversion_requested) {
          return <span className="text-yellow-600 font-medium">Pending Review</span>;
        } else if (lead.can_request_conversion) {
          return <span className="text-green-600 font-medium">Ready for Conversion</span>;
        }
        return <span className="text-gray-500">Not Ready</span>;
      }
    },
    {
      key: 'updated_on',
      label: 'Last Updated',
      render: (lead) => new Date(lead.updated_on).toLocaleDateString()
    }
  ];

  useEffect(() => {
    fetchMyLeads();
  }, [filters, user]);

  const fetchMyLeads = async () => {
    try {
      setLoading(true);
      // Filter leads created by current user
      const response = await apiMethods.leads.getLeads({
        ...filters,
        created_by: user?.id
      });
      if (response.data?.data?.leads) {
        setLeads(response.data.data.leads);
      }
    } catch (error) {
      console.error('Error fetching my leads:', error);
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestConversion = async (leadId) => {
    try {
      const notes = prompt("Enter conversion request notes:");
      if (notes !== null) {
        // Call conversion request API
        console.log(`Requesting conversion for lead ${leadId} with notes: ${notes}`);
        fetchMyLeads(); // Refresh the list
      }
    } catch (error) {
      console.error('Error requesting conversion:', error);
    }
  };

  const handleUpdateStatus = async (leadId, newStatus) => {
    try {
      await apiMethods.leads.updateLeadStatus(leadId, newStatus);
      fetchMyLeads(); // Refresh the list
    } catch (error) {
      console.error('Error updating lead status:', error);
    }
  };

  const actions = [
    {
      label: 'Edit',
      onClick: (lead) => {
        // Handle edit
        console.log('Editing lead:', lead.id);
      },
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Request Conversion',
      onClick: (lead) => handleRequestConversion(lead.id),
      className: 'text-green-600 hover:text-green-900',
      show: (lead) => lead.can_request_conversion && !lead.conversion_requested
    },
    {
      label: 'Update Status',
      onClick: (lead) => {
        const newStatus = prompt("Enter new status (New/Contacted/Qualified/Unqualified):");
        if (newStatus && ['New', 'Contacted', 'Qualified', 'Unqualified'].includes(newStatus)) {
          handleUpdateStatus(lead.id, newStatus);
        }
      },
      className: 'text-orange-600 hover:text-orange-900',
      show: (lead) => !lead.converted
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Leads</h1>
        <div className="text-sm text-gray-600">
          Showing leads created by you
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total My Leads</p>
              <p className="text-2xl font-bold text-gray-900">{leads.length}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Ready for Conversion</p>
              <p className="text-2xl font-bold text-green-600">
                {leads.filter(lead => lead.can_request_conversion && !lead.conversion_requested).length}
              </p>
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
              <p className="text-sm font-medium text-gray-600">Pending Review</p>
              <p className="text-2xl font-bold text-yellow-600">
                {leads.filter(lead => lead.conversion_requested && !lead.reviewed).length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Converted</p>
              <p className="text-2xl font-bold text-purple-600">
                {leads.filter(lead => lead.converted).length}
              </p>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search your leads..."
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
            emptyMessage="You haven't created any leads yet. Create your first lead to get started."
          />
        )}
      </div>
    </div>
  );
};

export default MyLeadsPage;