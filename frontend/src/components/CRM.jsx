import React, { useState } from "react";
import CompanyManagement from "./CompanyManagement";
import ContactManagement from "./ContactManagement";
import LeadManagement from "./LeadManagement";
import OpportunityManagement from "./OpportunityManagement";
import UserManagement from "./UserManagement";
import Dashboard from "./Dashboard";

const CRM = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState("dashboard");

  const tabs = [
    { id: "dashboard", name: "Dashboard", icon: "👤" },
    { id: "companies", name: "Companies", icon: "🏢" },
    { id: "contacts", name: "Contacts", icon: "👥" },
    { id: "leads", name: "Leads", icon: "🎯" },
    { id: "opportunities", name: "Opportunities", icon: "💰" },
    { id: "users", name: "Users", icon: "👤" },
  ];

  const renderActiveComponent = () => {
    switch (activeTab) {
      case "companies":
        return <CompanyManagement />;
      case "contacts":
        return <ContactManagement />;
      case "leads":
        return <LeadManagement />;
      case "opportunities":
        return <OpportunityManagement />;
      case "users":
        return <UserManagement />;
      default:
        return <Dashboard />;
    }
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
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveComponent()}
      </main>
    </div>
  );
};

export default CRM;
