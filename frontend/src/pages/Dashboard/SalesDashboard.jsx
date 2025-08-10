import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import MetricCard from '../../components/dashboard/MetricCard';
import ChartWidget from '../../components/dashboard/ChartWidget';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const SalesDashboard = () => {
  const [salesData, setSalesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSalesData();
  }, []);

  const fetchSalesData = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.dashboard.getSales();
      if (response.data.status) {
        setSalesData(response.data.data);
      } else {
        setError('Failed to load sales data');
      }
    } catch (error) {
      console.error('Sales dashboard error:', error);
      setError('Failed to load sales data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;
  if (!salesData) return <div className="text-gray-600 text-center py-8">No data available</div>;

  const { metrics, assignment_overview, lead_status_breakdown, opportunity_pipeline } = salesData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sales Dashboard</h1>
          <p className="text-gray-600">Track leads, opportunities, and revenue performance</p>
        </div>
        <button
          onClick={fetchSalesData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Leads"
          value={metrics.total_leads}
          subtitle={`${metrics.active_leads} active`}
          icon="user-group"
          color="blue"
        />
        <MetricCard
          title="Conversion Rate"
          value={`${metrics.conversion_rate}%`}
          subtitle={`${metrics.converted_leads} converted`}
          icon="trending-up"
          color="green"
        />
        <MetricCard
          title="Total Opportunities"
          value={metrics.total_opportunities}
          subtitle={`${metrics.open_opportunities} open`}
          icon="briefcase"
          color="purple"
        />
        <MetricCard
          title="Win Rate"
          value={`${metrics.win_rate}%`}
          subtitle={`${metrics.won_opportunities} won`}
          icon="trophy"
          color="yellow"
        />
      </div>

      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Total Revenue"
          value={`$${metrics.total_revenue.toLocaleString()}`}
          icon="currency-dollar"
          color="green"
          size="large"
        />
        <MetricCard
          title="Monthly Revenue"
          value={`$${metrics.monthly_revenue.toLocaleString()}`}
          subtitle="This month"
          icon="calendar"
          color="blue"
          size="large"
        />
        <MetricCard
          title="Pending Approvals"
          value={metrics.pending_approvals}
          subtitle="Quotations"
          icon="clock"
          color="orange"
          size="large"
        />
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lead Status Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Status Breakdown</h3>
          <div className="space-y-3">
            {lead_status_breakdown.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 bg-${getStatusColor(item.status)}-500`}></div>
                  <span className="text-gray-700 capitalize">{item.status.toLowerCase().replace('_', ' ')}</span>
                </div>
                <span className="font-semibold text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Opportunity Pipeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Opportunity Pipeline</h3>
          <div className="space-y-3">
            {opportunity_pipeline.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 bg-${getStatusColor(item.status)}-500`}></div>
                  <span className="text-gray-700 capitalize">{item.status.toLowerCase().replace('_', ' ')}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900">{item.count}</div>
                  <div className="text-sm text-gray-500">${item.total_value.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Assignment Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Assignment Overview</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Team Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Leads
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Opportunities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Workload
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {assignment_overview.map((member, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {member.user_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {member.leads}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {member.opportunities}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {member.leads + member.opportunities}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const getStatusColor = (status) => {
  const colors = {
    'NEW': 'blue',
    'ACTIVE': 'green',
    'CONTACTED': 'yellow',
    'QUALIFIED': 'purple',
    'CONVERTED': 'green',
    'REJECTED': 'red',
    'OPEN': 'blue',
    'WON': 'green',
    'LOST': 'red'
  };
  return colors[status] || 'gray';
};

export default SalesDashboard;