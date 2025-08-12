import React, { useState, useEffect } from "react";
import api from "../utils/api";

const Dashboard = ({ onLogout }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [metrics, setMetrics] = useState({
    leads: { total: 0, new: 0, qualified: 0, conversion_rate: 0 },
    opportunities: { total: 0, open: 0, won: 0, total_value: 0, win_rate: 0 },
    contacts: { total: 0, decision_makers: 0 },
    companies: { total: 0 },
  });

  useEffect(() => {
    fetchUserData();
    fetchDashboardMetrics();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      const backendUrl =
        import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

      const response = await fetch(`${backendUrl}/api/dashboard`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status) {
        setUser(data.data);
      } else {
        setError("Failed to fetch user data");
        // If token is invalid, logout user
        if (response.status === 401) {
          onLogout();
        }
      }
    } catch (err) {
      setError("Network error. Please check your connection.");
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardMetrics = async () => {
    try {
      // Fetch leads summary
      const leadsResponse = await apiRequest("/api/leads/stats");
      if (leadsResponse.status) {
        const leadData = leadsResponse.data;
        setMetrics((prev) => ({
          ...prev,
          leads: {
            total: leadData.total_leads || 0,
            new: leadData.new_leads || 0,
            qualified: leadData.qualified_leads || 0,
            conversion_rate: leadData.conversion_rate || 0,
          },
        }));
      }

      // Fetch opportunities pipeline
      const opportunitiesResponse = await apiRequest(
        "/api/opportunities/statistics/overview"
      );
      if (opportunitiesResponse.status) {
        const oppData = opportunitiesResponse.data;
        setMetrics((prev) => ({
          ...prev,
          opportunities: {
            total: oppData.summary?.total_opportunities || 0,
            open: oppData.summary?.total_opportunities || 0,
            won: 0, // Will be calculated from status
            total_value: oppData.summary?.total_value || 0,
            win_rate: 0, // Will be calculated
          },
        }));
      }

      // Fetch companies count
      const companiesResponse = await apiRequest("/api/companies?limit=1");
      if (companiesResponse.status) {
        setMetrics((prev) => ({
          ...prev,
          companies: { total: companiesResponse.data.total || 0 },
        }));
      }

      // Fetch contacts count
      const contactsResponse = await apiRequest("/api/contacts?limit=1");
      if (contactsResponse.status) {
        setMetrics((prev) => ({
          ...prev,
          contacts: {
            total: contactsResponse.data.total || 0,
            decision_makers: 0, // We'll estimate this
          },
        }));
      }
    } catch (err) {
      console.error("Failed to fetch dashboard metrics:", err);
    }
  };

  const handleLogout = () => {
    onLogout();
  };

  const formatCurrency = (amount) => {
    if (!amount) return "₹0";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
            <svg
              className="w-12 h-12 mx-auto mb-4 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 15.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <p className="font-medium">{error}</p>
            <button
              onClick={fetchUserData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Companies */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Companies</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics.companies.total}
                </p>
              </div>
            </div>
          </div>

          {/* Contacts */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Contacts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics.contacts.total}
                </p>
                <p className="text-xs text-green-600">
                  Decision Makers: {Math.floor(metrics.contacts.total * 0.3)}
                </p>
              </div>
            </div>
          </div>

          {/* Leads */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-yellow-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  Active Leads
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics.leads.total}
                </p>
                <p className="text-xs text-yellow-600">
                  Qualified: {metrics.leads.qualified}
                </p>
              </div>
            </div>
          </div>

          {/* Opportunities */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  Opportunities
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics.opportunities.total}
                </p>
                <p className="text-xs text-purple-600">
                  {formatCurrency(metrics.opportunities.total_value)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Lead Conversion Funnel */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Lead Conversion Funnel
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Leads</span>
                <span className="font-medium">{metrics.leads.total}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: "100%" }}
                ></div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Qualified Leads</span>
                <span className="font-medium">{metrics.leads.qualified}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{
                    width: `${
                      metrics.leads.total > 0
                        ? (metrics.leads.qualified / metrics.leads.total) * 100
                        : 0
                    }%`,
                  }}
                ></div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Opportunities</span>
                <span className="font-medium">
                  {metrics.opportunities.total}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full"
                  style={{
                    width: `${
                      metrics.leads.total > 0
                        ? (metrics.opportunities.total / metrics.leads.total) *
                          100
                        : 0
                    }%`,
                  }}
                ></div>
              </div>

              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  Conversion Rate:{" "}
                  <span className="font-semibold text-green-600">
                    {metrics.leads.total > 0
                      ? (
                          (metrics.opportunities.total / metrics.leads.total) *
                          100
                        ).toFixed(1)
                      : 0}
                    %
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* Opportunity Pipeline Value */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Pipeline Value
            </h3>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600 mb-2">
                {formatCurrency(metrics.opportunities.total_value)}
              </p>
              <p className="text-sm text-gray-600 mb-4">Total Pipeline Value</p>

              <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-lg font-semibold text-blue-600">
                    {metrics.opportunities.open}
                  </p>
                  <p className="text-xs text-blue-600">Open</p>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-lg font-semibold text-green-600">
                    {metrics.opportunities.won}
                  </p>
                  <p className="text-xs text-green-600">Won</p>
                </div>
              </div>

              {metrics.opportunities.total > 0 && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Average Deal Size:{" "}
                    <span className="font-semibold">
                      {formatCurrency(
                        metrics.opportunities.total_value /
                          metrics.opportunities.total
                      )}
                    </span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* User Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="user-card bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">
                Profile Information
              </h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium text-gray-900">{user?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{user?.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Username</p>
                <p className="font-medium text-gray-900">{user?.username}</p>
              </div>
            </div>
          </div>

          <div className="user-card bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6"
                  />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">
                Work Information
              </h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Role</p>
                <p className="font-medium text-gray-900 capitalize">
                  {user?.role}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Department</p>
                <p className="font-medium text-gray-900">{user?.department}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user?.is_active
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {user?.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          </div>

          <div className="user-card bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">
                Today's Activity
              </h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">New Leads</p>
                <p className="font-medium text-gray-900">{metrics.leads.new}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Pipeline Value</p>
                <p className="font-medium text-gray-900">
                  {formatCurrency(metrics.opportunities.total_value)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Opportunities</p>
                <p className="font-medium text-gray-900">
                  {metrics.opportunities.total}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <svg
                  className="w-4 h-4 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <p className="font-medium text-gray-900">Add Company</p>
              <p className="text-sm text-gray-500">Create new company record</p>
            </button>

            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mb-2">
                <svg
                  className="w-4 h-4 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <p className="font-medium text-gray-900">Add Contact</p>
              <p className="text-sm text-gray-500">Create new contact</p>
            </button>

            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center mb-2">
                <svg
                  className="w-4 h-4 text-yellow-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <p className="font-medium text-gray-900">Add Lead</p>
              <p className="text-sm text-gray-500">Create new sales lead</p>
            </button>

            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                <svg
                  className="w-4 h-4 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <p className="font-medium text-gray-900">Add Opportunity</p>
              <p className="text-sm text-gray-500">Create new opportunity</p>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
