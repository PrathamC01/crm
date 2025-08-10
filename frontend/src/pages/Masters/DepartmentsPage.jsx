import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const DepartmentsPage = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    status: ''
  });

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
  ];

  const departmentColumns = [
    {
      key: 'name',
      label: 'Department Name',
      sortable: true,
      render: (department) => (
        <div>
          <div className="font-medium text-gray-900">{department.name}</div>
          <div className="text-sm text-gray-500">{department.code}</div>
        </div>
      )
    },
    {
      key: 'description',
      label: 'Description',
      render: (department) => (
        <div className="text-sm text-gray-600 max-w-xs truncate">
          {department.description || 'No description'}
        </div>
      )
    },
    {
      key: 'head_name',
      label: 'Department Head',
      render: (department) => (
        <div className="text-sm text-gray-900">
          {department.head_name || 'Not assigned'}
        </div>
      )
    },
    {
      key: 'user_count',
      label: 'Users',
      render: (department) => (
        <div className="text-center">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-semibold">
            {department.user_count || 0}
          </span>
        </div>
      )
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (department) => {
        const isActive = department.is_active !== false;
        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
            isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isActive ? 'Active' : 'Inactive'}
          </span>
        );
      }
    },
    {
      key: 'created_on',
      label: 'Created',
      render: (department) => new Date(department.created_on).toLocaleDateString()
    }
  ];

  useEffect(() => {
    fetchDepartments();
  }, [filters]);

  const fetchDepartments = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getDepartments(filters);
      if (response.data?.data) {
        setDepartments(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching departments:', error);
      setDepartments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDepartment = () => {
    setShowCreateModal(true);
  };

  const handleViewDepartment = (department) => {
    setSelectedDepartment(department);
  };

  const handleToggleStatus = async (departmentId, currentStatus) => {
    try {
      await apiMethods.masters.updateDepartment(departmentId, { is_active: !currentStatus });
      fetchDepartments(); // Refresh the list
    } catch (error) {
      console.error('Error updating department status:', error);
    }
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewDepartment,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: (department) => {
        console.log('Editing department:', department.id);
      },
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'Activate',
      onClick: (department) => handleToggleStatus(department.id, department.is_active),
      className: 'text-green-600 hover:text-green-900',
      show: (department) => !department.is_active
    },
    {
      label: 'Deactivate',
      onClick: (department) => handleToggleStatus(department.id, department.is_active),
      className: 'text-red-600 hover:text-red-900',
      show: (department) => department.is_active
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Departments</h1>
        <button
          onClick={handleCreateDepartment}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Department
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Departments</p>
              <p className="text-2xl font-bold text-gray-900">{departments.length}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {departments.filter(dept => dept.is_active !== false).length}
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
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-purple-600">
                {departments.reduce((sum, dept) => sum + (dept.user_count || 0), 0)}
              </p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">With Heads</p>
              <p className="text-2xl font-bold text-yellow-600">
                {departments.filter(dept => dept.head_name).length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
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
              placeholder="Search departments..."
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

      {/* Departments Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={departmentColumns}
            data={departments}
            actions={actions}
            emptyMessage="No departments found. Create your first department to get started."
          />
        )}
      </div>

      {/* Create Department Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Department"
        size="lg"
      >
        <div className="p-6">
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department Name *
              </label>
              <input
                type="text"
                placeholder="Sales Department"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department Code *
              </label>
              <input
                type="text"
                placeholder="SALES"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                rows="3"
                placeholder="Department description..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department Head
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Select Department Head</option>
                <option value="1">John Doe</option>
                <option value="2">Jane Smith</option>
                <option value="3">Mike Johnson</option>
              </select>
            </div>
          </div>
          
          <div className="flex items-center mb-6">
            <input
              type="checkbox"
              id="isActive"
              defaultChecked
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="isActive" className="ml-2 block text-sm text-gray-900">
              Active department
            </label>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Handle form submission
                setShowCreateModal(false);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create Department
            </button>
          </div>
        </div>
      </Modal>

      {/* Department Detail Modal */}
      <Modal
        isOpen={!!selectedDepartment}
        onClose={() => setSelectedDepartment(null)}
        title="Department Details"
        size="lg"
      >
        {selectedDepartment && (
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Department Name</h3>
                <p className="text-gray-900">{selectedDepartment.name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Department Code</h3>
                <p className="text-gray-900">{selectedDepartment.code}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Department Head</h3>
                <p className="text-gray-900">{selectedDepartment.head_name || 'Not assigned'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedDepartment.is_active !== false ? 'Active' : 'Inactive'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Total Users</h3>
                <p className="text-gray-900">{selectedDepartment.user_count || 0}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Created On</h3>
                <p className="text-gray-900">{new Date(selectedDepartment.created_on).toLocaleDateString()}</p>
              </div>
            </div>
            
            {selectedDepartment.description && (
              <div>
                <h3 className="font-semibold text-gray-700">Description</h3>
                <p className="text-gray-900">{selectedDepartment.description}</p>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Department Users</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">
                  List of users in this department will be displayed here.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedDepartment(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              <button
                onClick={() => {
                  console.log('Editing department');
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Edit
              </button>
              <button
                onClick={() => {
                  handleToggleStatus(selectedDepartment.id, selectedDepartment.is_active);
                  setSelectedDepartment(null);
                }}
                className={`px-4 py-2 rounded-md ${
                  selectedDepartment.is_active !== false
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {selectedDepartment.is_active !== false ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DepartmentsPage;