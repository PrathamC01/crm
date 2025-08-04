import React, { useState } from 'react';
import { UserList, UserForm, UserView } from './modules/user';

const UserManagement = () => {
  const [currentView, setCurrentView] = useState('list');
  const [selectedUser, setSelectedUser] = useState(null);

  const handleCreate = () => {
    setSelectedUser(null);
    setCurrentView('form');
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setCurrentView('form');
  };

  const handleView = (user) => {
    setSelectedUser(user);
    setCurrentView('view');
  };

  const handleSave = (savedUser) => {
    setCurrentView('list');
    setSelectedUser(null);
  };

  const handleCancel = () => {
    setCurrentView('list');
    setSelectedUser(null);
  };

  const handleDelete = (userId) => {
    // Delete is handled within UserList component
    // This could be used for additional logic if needed
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 text-left">User Management</h2>
          <p className="text-gray-600">Manage users, roles & permissions</p>
        </div>
        {currentView === 'list' && (
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <span className="mr-2">+</span>
            Add User
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'list' && (
        <UserList
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
        />
      )}

      {currentView === 'form' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-6">
            {selectedUser ? 'Edit User' : 'Create New User'}
          </h3>
          <UserForm
            user={selectedUser}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      {currentView === 'view' && (
        <div className="bg-white rounded-lg shadow p-6">
          <UserView
            user={selectedUser}
            onEdit={handleEdit}
            onClose={handleCancel}
          />
        </div>
      )}
    </div>
  );
};

export default UserManagement;