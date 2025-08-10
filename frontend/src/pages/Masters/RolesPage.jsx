import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const RolesPage = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    status: ''
  });

  const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'system', label: 'System' },
    { value: 'custom', label: 'Custom' }
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
  ];

  const roleColumns = [
    {
      key: 'name',
      label: 'Role Name',
      sortable: true,
      render: (role) => (
        <div>
          <div className="font-medium text-gray-900">{role.name}</div>
          <div className="text-sm text-gray-500">{role.code}</div>
        </div>
      )
    },
    {
      key: 'description',
      label: 'Description',
      render: (role) => (
        <div className="text-sm text-gray-600 max-w-xs truncate">
          {role.description || 'No description'}
        </div>
      )
    },
    {
      key: 'type',
      label: 'Type',
      render: (role) => (
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
          role.type === 'system' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
        }`}>
          {role.type === 'system' ? 'System' : 'Custom'}
        </span>
      )
    },
    {
      key: 'user_count',
      label: 'Users',
      render: (role) => (
        <div className="text-center">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-semibold">
            {role.user_count || 0}
          </span>
        </div>
      )
    },
    {
      key: 'permissions_count',
      label: 'Permissions',
      render: (role) => (
        <div className="text-center">
          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm font-semibold">
            {role.permissions_count || 0}
          </span>
        </div>
      )
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (role) => {
        const isActive = role.is_active !== false;
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
      render: (role) => new Date(role.created_on).toLocaleDateString()
    }
  ];

  const availablePermissions = [
    'users:read', 'users:write', 'users:delete',
    'leads:read', 'leads:write', 'leads:delete',
    'opportunities:read', 'opportunities:write', 'opportunities:delete',
    'companies:read', 'companies:write', 'companies:delete',
    'contacts:read', 'contacts:write', 'contacts:delete',
    'quotations:read', 'quotations:write', 'quotations:delete',
    'masters:read', 'masters:write', 'masters:delete',
    'dashboard:read', 'reports:read',
    'admin:all'
  ];

  useEffect(() => {
    fetchRoles();
  }, [filters]);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getRoles(filters);
      if (response.data?.data) {
        setRoles(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRole = () => {
    setShowCreateModal(true);
  };

  const handleViewRole = (role) => {
    setSelectedRole(role);
  };

  const handleToggleStatus = async (roleId, currentStatus) => {
    try {
      await apiMethods.masters.updateRole(roleId, { is_active: !currentStatus });
      fetchRoles(); // Refresh the list
    } catch (error) {
      console.error('Error updating role status:', error);
    }
  };

  const actions = [
    {
      label: 'View',
      onClick: handleViewRole,
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: (role) => {
        console.log('Editing role:', role.id);
      },
      className: 'text-green-600 hover:text-green-900',
      show: (role) => role.type !== 'system'
    },
    {
      label: 'Activate',
      onClick: (role) => handleToggleStatus(role.id, role.is_active),
      className: 'text-green-600 hover:text-green-900',
      show: (role) => !role.is_active && role.type !== 'system'
    },
    {
      label: 'Deactivate',
      onClick: (role) => handleToggleStatus(role.id, role.is_active),
      className: 'text-red-600 hover:text-red-900',
      show: (role) => role.is_active && role.type !== 'system'
    },
    {
      label: 'Duplicate',
      onClick: (role) => {
        console.log('Duplicating role:', role.id);
      },
      className: 'text-orange-600 hover:text-orange-900'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Roles & Permissions</h1>
        <button
          onClick={handleCreateRole}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Role
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Roles</p>
              <p className="text-2xl font-bold text-gray-900">{roles.length}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {roles.filter(role => role.is_active !== false).length}
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
              <p className="text-sm font-medium text-gray-600">System Roles</p>
              <p className="text-2xl font-bold text-purple-600">
                {roles.filter(role => role.type === 'system').length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Custom Roles</p>
              <p className="text-2xl font-bold text-yellow-600">
                {roles.filter(role => role.type === 'custom').length}
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
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
              placeholder="Search roles..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type
            </label>
            <select
              value={filters.type}
              onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {typeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
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

      {/* Roles Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={roleColumns}
            data={roles}
            actions={actions}
            emptyMessage="No roles found. Create your first role to get started."
          />
        )}
      </div>

      {/* Create Role Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Role"
        size="xl"
      >
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role Name *
              </label>
              <input
                type="text"
                placeholder="Sales Manager"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role Code *
              </label>
              <input
                type="text"
                placeholder="SALES_MANAGER"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              rows="3"
              placeholder="Role description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Permissions
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-60 overflow-y-auto border border-gray-200 rounded-lg p-4">
              {availablePermissions.map(permission => (
                <div key={permission} className="flex items-center">
                  <input
                    type="checkbox"
                    id={permission}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor={permission} className="ml-2 block text-sm text-gray-900">
                    {permission}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center mb-6">
            <input
              type="checkbox"
              id="isActiveRole"
              defaultChecked
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="isActiveRole" className="ml-2 block text-sm text-gray-900">
              Active role
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
              Create Role
            </button>
          </div>
        </div>
      </Modal>

      {/* Role Detail Modal */}
      <Modal
        isOpen={!!selectedRole}
        onClose={() => setSelectedRole(null)}
        title="Role Details"
        size="xl"
      >
        {selectedRole && (
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-700">Role Name</h3>
                <p className="text-gray-900">{selectedRole.name}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Role Code</h3>
                <p className="text-gray-900">{selectedRole.code}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Type</h3>
                <p className="text-gray-900">{selectedRole.type === 'system' ? 'System' : 'Custom'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Status</h3>
                <p className="text-gray-900">{selectedRole.is_active !== false ? 'Active' : 'Inactive'}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Users Count</h3>
                <p className="text-gray-900">{selectedRole.user_count || 0}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700">Created On</h3>
                <p className="text-gray-900">{new Date(selectedRole.created_on).toLocaleDateString()}</p>
              </div>
            </div>
            
            {selectedRole.description && (
              <div>
                <h3 className="font-semibold text-gray-700">Description</h3>
                <p className="text-gray-900">{selectedRole.description}</p>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-700 mb-3">Permissions</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {(selectedRole.permissions || availablePermissions.slice(0, 6)).map(permission => (
                  <div key={permission} className="flex items-center p-2 bg-gray-50 rounded">
                    <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-gray-700">{permission}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Users with this Role</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">
                  List of users with this role will be displayed here.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={() => setSelectedRole(null)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              {selectedRole.type !== 'system' && (
                <>
                  <button
                    onClick={() => {
                      console.log('Editing role');
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      console.log('Duplicating role');
                    }}
                    className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
                  >
                    Duplicate
                  </button>
                  <button
                    onClick={() => {
                      handleToggleStatus(selectedRole.id, selectedRole.is_active);
                      setSelectedRole(null);
                    }}
                    className={`px-4 py-2 rounded-md ${
                      selectedRole.is_active !== false
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {selectedRole.is_active !== false ? 'Deactivate' : 'Activate'}
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default RolesPage;