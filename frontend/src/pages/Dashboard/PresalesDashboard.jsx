import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import MetricCard from '../../components/dashboard/MetricCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const PresalesDashboard = () => {
  const [presalesData, setPresalesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPresalesData();
  }, []);

  const fetchPresalesData = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.dashboard.getPresales();
      if (response.data.status) {
        setPresalesData(response.data.data);
      } else {
        setError('Failed to load presales data');
      }
    } catch (error) {
      console.error('Presales dashboard error:', error);
      setError('Failed to load presales data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;
  if (!presalesData) return <div className="text-gray-600 text-center py-8">No data available</div>;

  const { workload_data, approval_summary } = presalesData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Presales Dashboard</h1>
          <p className="text-gray-600">Solution team workload and approval tracking</p>
        </div>
        <button
          onClick={fetchPresalesData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* Team Workload Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Solution Team Workload</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Team Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Active Opportunities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pending Quotes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Workload
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {workload_data.map((member, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {member.user_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {member.active_opportunities}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      {member.pending_quotes}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="text-lg font-semibold">{member.total_workload}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      member.total_workload <= 5 ? 'bg-green-100 text-green-800' :
                      member.total_workload <= 10 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {member.total_workload <= 5 ? 'Light' :
                       member.total_workload <= 10 ? 'Moderate' : 'Heavy'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {workload_data.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No presales team members found
          </div>
        )}
      </div>

      {/* Approval Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Approval Summary</h3>
          <div className="space-y-3">
            {approval_summary.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${getApprovalStatusColor(item.status)}`}></div>
                  <span className="text-gray-700 capitalize">{item.status.toLowerCase().replace('_', ' ')}</span>
                </div>
                <span className="text-xl font-bold text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
          
          {approval_summary.length === 0 && (
            <div className="text-center py-4 text-gray-500">
              No pending approvals
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-left transition-colors">
              <div className="text-blue-600 font-medium">Review Pending Quotes</div>
              <div className="text-sm text-gray-600">Check quotations awaiting approval</div>
            </button>
            
            <button className="w-full p-3 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors">
              <div className="text-green-600 font-medium">Create New Quote</div>
              <div className="text-sm text-gray-600">Generate quotation for opportunity</div>
            </button>
            
            <button className="w-full p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors">
              <div className="text-purple-600 font-medium">Team Performance</div>
              <div className="text-sm text-gray-600">View detailed team metrics</div>
            </button>
          </div>
        </div>
      </div>

      {/* Workload Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Workload Distribution</h3>
        <div className="space-y-4">
          {workload_data.map((member, index) => {
            const maxWorkload = Math.max(...workload_data.map(m => m.total_workload));
            const percentage = maxWorkload > 0 ? (member.total_workload / maxWorkload) * 100 : 0;
            
            return (
              <div key={index} className="flex items-center">
                <div className="w-32 text-sm font-medium text-gray-700 mr-4">
                  {member.user_name}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-4 mr-4">
                  <div 
                    className={`h-4 rounded-full ${
                      percentage <= 33 ? 'bg-green-500' :
                      percentage <= 66 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
                <div className="w-12 text-sm text-gray-600 text-right">
                  {member.total_workload}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const getApprovalStatusColor = (status) => {
  const colors = {
    'DRAFT': 'bg-gray-500',
    'SUBMITTED': 'bg-blue-500',
    'APPROVED': 'bg-green-500',
    'REJECTED': 'bg-red-500'
  };
  return colors[status] || 'bg-gray-500';
};

export default PresalesDashboard;