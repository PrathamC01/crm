import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import MetricCard from '../../components/dashboard/MetricCard';
import ChartWidget from '../../components/dashboard/ChartWidget';
import RecentActivity from '../../components/dashboard/RecentActivity';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const DashboardOverview = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.dashboard.getOverview();
      if (response.data.status) {
        setDashboardData(response.data.data);
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (error) {
      console.error('Dashboard error:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;
  if (!dashboardData) return <div className="text-gray-600 text-center py-8">No data available</div>;

  const { system_overview, recent_activity } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-gray-600">Welcome to your Enterprise CRM dashboard</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* System Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <MetricCard
          title="Total Users"
          value={system_overview.total_users}
          icon="users"
          color="blue"
        />
        <MetricCard
          title="Departments"
          value={system_overview.total_departments}
          icon="building"
          color="green"
        />
        <MetricCard
          title="Total Leads"
          value={system_overview.total_leads}
          icon="user-group"
          color="yellow"
        />
        <MetricCard
          title="Opportunities"
          value={system_overview.total_opportunities}
          icon="briefcase"
          color="purple"
        />
        <MetricCard
          title="Products"
          value={system_overview.total_products}
          icon="cube"
          color="indigo"
        />
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity (Last 7 Days)</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                <span className="text-gray-700">New Leads</span>
              </div>
              <span className="text-xl font-bold text-blue-600">{recent_activity.new_leads_week}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-gray-700">New Opportunities</span>
              </div>
              <span className="text-xl font-bold text-green-600">{recent_activity.new_opportunities_week}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <button className="p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-left transition-colors">
              <div className="text-blue-600 font-medium">Create Lead</div>
              <div className="text-sm text-gray-600">Add new lead to system</div>
            </button>
            <button className="p-3 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors">
              <div className="text-green-600 font-medium">New Opportunity</div>
              <div className="text-sm text-gray-600">Create new opportunity</div>
            </button>
            <button className="p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors">
              <div className="text-purple-600 font-medium">Add Product</div>
              <div className="text-sm text-gray-600">Add new product to catalog</div>
            </button>
            <button className="p-3 bg-yellow-50 hover:bg-yellow-100 rounded-lg text-left transition-colors">
              <div className="text-yellow-600 font-medium">Generate Report</div>
              <div className="text-sm text-gray-600">Create performance report</div>
            </button>
          </div>
        </div>
      </div>

      {/* Department Links */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Dashboards</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/dashboard/sales"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Sales Dashboard</h4>
                <p className="text-sm text-gray-600">Leads, opportunities, revenue metrics</p>
              </div>
            </div>
          </a>

          <a
            href="/dashboard/presales"
            className="block p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Presales Dashboard</h4>
                <p className="text-sm text-gray-600">Team workload, approvals pending</p>
              </div>
            </div>
          </a>

          <a
            href="/dashboard/product"
            className="block p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Product Dashboard</h4>
                <p className="text-sm text-gray-600">Top products, category performance</p>
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;