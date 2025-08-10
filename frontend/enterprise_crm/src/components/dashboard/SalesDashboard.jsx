import React from 'react';
import KPICard from '../common/KPICard';
import Chart from '../common/Chart';
import ApprovalsList from '../common/ApprovalsList';
import ActivityFeed from '../common/ActivityFeed';

const SalesDashboard = ({ data, user, onRefresh }) => {
  if (!data) return null;

  const {
    total_leads = {},
    total_opportunities = {},
    revenue_generated = {},
    assignment_overview = {},
    approvals_pending = []
  } = data;

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Leads"
          value={total_leads.value || "0"}
          change={total_leads.change}
          trend={total_leads.trend}
          color="blue"
          icon="users"
        />
        <KPICard
          title="Total Opportunities"
          value={total_opportunities.value || "0"}
          change={total_opportunities.change}
          trend={total_opportunities.trend}
          color="green"
          icon="briefcase"
        />
        <KPICard
          title="Revenue Generated"
          value={revenue_generated.value || "₹0"}
          change={revenue_generated.change}
          trend={revenue_generated.trend}
          color="purple"
          icon="currency-rupee"
        />
        <KPICard
          title="Conversion Rate"
          value={data.conversion_rate?.value || "0%"}
          change={data.conversion_rate?.change}
          trend={data.conversion_rate?.trend}
          color="orange"
          icon="trending-up"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Assignment Overview Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Assignment Overview
          </h3>
          {assignment_overview && (
            <Chart
              type="doughnut"
              data={assignment_overview}
              height={300}
            />
          )}
        </div>

        {/* Pipeline Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Sales Pipeline
          </h3>
          {data.pipeline_chart && (
            <Chart
              type="bar"
              data={data.pipeline_chart}
              height={300}
            />
          )}
        </div>
      </div>

      {/* Bottom Row - Approvals and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Approvals Pending */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Approvals Pending
              {approvals_pending.length > 0 && (
                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  {approvals_pending.length}
                </span>
              )}
            </h3>
          </div>
          <ApprovalsList items={approvals_pending} />
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Recent Activities
            </h3>
          </div>
          <ActivityFeed items={data.recent_activities || []} />
        </div>
      </div>

      {/* Additional Metrics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Source Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Lead Sources
          </h3>
          {data.lead_sources && (
            <Chart
              type="pie"
              data={data.lead_sources}
              height={200}
            />
          )}
        </div>

        {/* Monthly Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Monthly Trends
          </h3>
          {data.monthly_trends && (
            <Chart
              type="line"
              data={data.monthly_trends}
              height={200}
            />
          )}
        </div>

        {/* Top Performers */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Top Performers
          </h3>
          <div className="space-y-3">
            {(data.top_performers || []).map((performer, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600">
                      {performer.name?.charAt(0)}
                    </span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">
                      {performer.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {performer.department}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    ₹{performer.revenue?.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500">
                    {performer.deals} deals
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesDashboard;