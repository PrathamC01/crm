import React, { useState, useEffect } from 'react';
import DefaultDashboard from './DefaultDashboard';
import SalesDashboard from './SalesDashboard';
import PresalesDashboard from './PresalesDashboard';
import ProductDashboard from './ProductDashboard';
import { apiRequest } from '../../utils/api';

const DashboardContainer = ({ dashboardType = 'default', user }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint = '/api/dashboard/';
      
      switch (dashboardType) {
        case 'sales':
          endpoint = '/api/dashboard/sales';
          break;
        case 'presales':
          endpoint = '/api/dashboard/presales';
          break;
        case 'product':
          endpoint = '/api/dashboard/product';
          break;
        default:
          endpoint = '/api/dashboard/stats';
      }
      
      const response = await apiRequest(endpoint);
      if (response.status) {
        setDashboardData(response.data);
      } else {
        setError(response.message || 'Failed to load dashboard data');
      }
    } catch (err) {
      setError('Error loading dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshDashboard = () => {
    fetchDashboardData();
  };

  useEffect(() => {
    fetchDashboardData();
  }, [dashboardType]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={refreshDashboard}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const renderDashboard = () => {
    const props = { data: dashboardData, user, onRefresh: refreshDashboard };
    
    switch (dashboardType) {
      case 'sales':
        return <SalesDashboard {...props} />;
      case 'presales':
        return <PresalesDashboard {...props} />;
      case 'product':
        return <ProductDashboard {...props} />;
      default:
        return <DefaultDashboard {...props} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {dashboardType === 'default' ? 'Dashboard Overview' : 
             dashboardType.charAt(0).toUpperCase() + dashboardType.slice(1) + ' Dashboard'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back, {user?.name}. Here's what's happening today.
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={refreshDashboard}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Dashboard Content */}
      {renderDashboard()}
    </div>
  );
};

export default DashboardContainer;