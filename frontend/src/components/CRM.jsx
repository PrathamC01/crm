import React from "react";
import { Routes, Route, Navigate, useLocation, Link } from "react-router-dom";
import CompanyManagement from "./CompanyManagement";
import ContactManagement from "./ContactManagement";
import LeadManagement from "./LeadManagement";
import OpportunityManagement from "./OpportunityManagement";
import UserManagement from "./UserManagement";
import Dashboard from "./Dashboard";

const CRM = ({ onLogout }) => {
  const location = useLocation();

  const tabs = [
    { id: "dashboard", name: "Dashboard", icon: "📊", path: "/crm/dashboard" },
    { id: "companies", name: "Companies", icon: "🏢", path: "/crm/companies" },
    { id: "contacts", name: "Contacts", icon: "👥", path: "/crm/contacts" },
    { id: "leads", name: "Leads", icon: "🎯", path: "/crm/leads" },
    { id: "opportunities", name: "Opportunities", icon: "💰", path: "/crm/opportunities" },
    { id: "users", name: "Users", icon: "👤", path: "/crm/users" },
  ];

  const getActiveTab = () => {
    const path = location.pathname;
    return tabs.find(tab => path.startsWith(tab.path))?.id || "dashboard";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">CRM Management System</h1>
              <p className="text-blue-100 mt-1">
                Manage your business relationships
              </p>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <Link
                key={tab.id}
                to={tab.path}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  getActiveTab() === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content with Routing */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="companies" element={<CompanyManagement />} />
          <Route path="contacts" element={<ContactManagement />} />
          <Route path="leads" element={<LeadManagement />} />
          <Route path="opportunities" element={<OpportunityManagement />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="" element={<Navigate to="/crm/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
};

export default CRM;