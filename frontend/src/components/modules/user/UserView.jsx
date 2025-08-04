import React from "react";

const UserView = ({ user, onEdit, onClose }) => {
  if (!user) return null;

  const getRoleBadgeColor = (role) => {
    const colors = {
      super_admin: "bg-red-100 text-red-800",
      admin: "bg-purple-100 text-purple-800",
      sales_manager: "bg-blue-100 text-blue-800",
      sales_executive: "bg-green-100 text-green-800",
      marketing: "bg-yellow-100 text-yellow-800",
      user: "bg-gray-100 text-gray-800",
    };
    return colors[role] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-center">
          <div className="flex-shrink-0 h-16 w-16">
            <div className="h-16 w-16 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center text-white text-2xl font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
          </div>
          <div className="ml-4">
            <h3 className="text-2xl font-bold text-gray-900 text-left">
              {user.name}
            </h3>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-gray-500">@{user.username}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(user)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Edit User
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>

      {/* User Information Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Account Information */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
            Account Information
          </h4>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">
                Full Name
              </label>
              <p className="text-gray-900">{user.name}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">
                Email Address
              </label>
              <p className="text-gray-900">{user.email}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">
                Username
              </label>
              <p className="text-gray-900 font-mono">@{user.username}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">
                Account Status
              </label>
              <div>
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user.is_active
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {user.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Role & Department */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-purple-600 rounded-full mr-2"></span>
            Role & Department
          </h4>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Role</label>
              <div>
                <span
                  className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getRoleBadgeColor(
                    user.role_name
                  )}`}
                >
                  {user.role_name?.replace("_", " ").toUpperCase() ||
                    "No Role Assigned"}
                </span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">
                Department
              </label>
              <p className="text-gray-900">
                {user.department_name || "No Department Assigned"}
              </p>
            </div>
          </div>
        </div>

        {/* Login Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
            Login Activity
          </h4>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">
                Last Login
              </label>
              <p className="text-gray-900">
                {user.last_login
                  ? new Date(user.last_login).toLocaleDateString("en-IN", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "Never logged in"}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">
                Account Created
              </label>
              <p className="text-gray-900">
                {new Date(user.created_on).toLocaleDateString("en-IN", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>

            {user.updated_on &&
              new Date(user.updated_on) > new Date(user.created_on) && (
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Last Updated
                  </label>
                  <p className="text-gray-900">
                    {new Date(user.updated_on).toLocaleDateString("en-IN", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              )}
          </div>
        </div>

        {/* Permissions Overview */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-yellow-600 rounded-full mr-2"></span>
            Permissions Overview
          </h4>
          <div className="space-y-3">
            {user.role_name ? (
              <div>
                <p className="text-sm text-gray-600 mb-2">
                  This user has{" "}
                  <strong>{user.role_name.replace("_", " ")}</strong>{" "}
                  permissions which include:
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {user.role_name === "super_admin" && (
                    <span className="text-red-600 font-medium">
                      • All System Access
                    </span>
                  )}
                  {(user.role_name === "admin" ||
                    user.role_name === "super_admin") && (
                    <>
                      <span className="text-blue-600">• User Management</span>
                      <span className="text-blue-600">• Full CRM Access</span>
                    </>
                  )}
                  {user.role_name.includes("sales") && (
                    <>
                      <span className="text-green-600">• Lead Management</span>
                      <span className="text-green-600">
                        • Opportunity Access
                      </span>
                    </>
                  )}
                  {user.role_name === "marketing" && (
                    <span className="text-yellow-600">• Lead Creation</span>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic">
                No role assigned - limited access
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border border-indigo-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">🔑</div>
              <div className="text-sm font-medium text-gray-900">
                Reset Password
              </div>
              <div className="text-xs text-gray-500">Send reset link</div>
            </div>
          </button>

          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">🎯</div>
              <div className="text-sm font-medium text-gray-900">
                View Leads
              </div>
              <div className="text-xs text-gray-500">Assigned leads</div>
            </div>
          </button>

          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">💰</div>
              <div className="text-sm font-medium text-gray-900">
                View Opportunities
              </div>
              <div className="text-xs text-gray-500">Created opportunities</div>
            </div>
          </button>

          <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <div className="text-sm font-medium text-gray-900">
                Activity Log
              </div>
              <div className="text-xs text-gray-500">View user activity</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserView;
