import React from 'react';

const UserManagement = () => {
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">User & Role Management</h3>
      <p className="text-gray-600">User and role management functionality coming soon...</p>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-indigo-50 rounded-lg">
          <h4 className="font-medium text-indigo-900">Role-Based Access Control</h4>
          <p className="text-indigo-700 text-sm mt-1">Super Admin, Admin, Sales Manager, Sales Executive, Marketing, User</p>
        </div>
        <div className="p-4 bg-teal-50 rounded-lg">
          <h4 className="font-medium text-teal-900">Department Management</h4>
          <p className="text-teal-700 text-sm mt-1">IT, Sales, Marketing, Finance, HR, Operations</p>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;