import React, { useState, useEffect } from "react";
import { apiMethods } from "../../utils/api";
import DataTable from "../../components/common/DataTable";
import Modal from "../../components/common/Modal";
import LoadingSpinner from "../../components/common/LoadingSpinner";
import OpportunityView from "../../components/opportunies/OpportunityView";
import OpportunityForm from "../../components/opportunies/OpportunityForm";

const OpportunitiesPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [showSalesProcessModal, setShowSalesProcessModal] = useState(false);
  const [stats, setStats] = useState({});
  const [filters, setFilters] = useState({
    stage: "",
    status: "",
    search: "",
  });

  const [view, setView] = useState("list"); // 'list', 'form', 'view'
  const handleAddOpportunity = () => {
    setSelectedOpportunity(null);
    setView("form");
  };

  const handleEditOpportunity = (opportunity) => {
    // console.log("first")
    setSelectedOpportunity(opportunity);
    setView("form");
  };

  const handleViewOpportunity = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setView("view");
  };

  const handleSave = (savedOpportunity) => {
    console.log("Opportunity saved:", savedOpportunity);
    setView("list");
    setSelectedOpportunity(null);
  };

  const handleCancel = () => {
    setView("list");
    setSelectedOpportunity(null);
  };

  const handleDelete = (opportunity) => {
    console.log("Delete opportunity:", opportunity);
    // The delete is handled in the list component itself
  };

  const handleClose = () => {
    setView("list");
    setSelectedOpportunity(null);
  };

  const renderContent = () => {
    switch (view) {
      case "form":
        return (
          <OpportunityForm
            opportunity={selectedOpportunity}
            opportunity_id={selectedOpportunity.id}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        );
      case "view":
        return (
          <OpportunityView
            opportunity={selectedOpportunity}
            onEdit={handleEditOpportunity}
            onClose={handleClose}
          />
        );
      default:
        return;
    }
  };

  const stageOptions = [
    { value: "", label: "All Stages" },
    { value: "L1_Prospect", label: "L1 Prospect" },
    { value: "L2_Need_Analysis", label: "L2 Need Analysis" },
    { value: "L3_Proposal", label: "L3 Proposal" },
    { value: "Win", label: "Win" },
    { value: "Loss", label: "Loss" },
  ];

  const statusOptions = [
    { value: "", label: "All Statuses" },
    { value: "Open", label: "Open" },
    { value: "Won", label: "Won" },
    { value: "Lost", label: "Lost" },
  ];

  const opportunityColumns = [
    {
      key: "pot_id",
      label: "POT ID",
      render: (opportunity) => (
        <div className="font-medium text-blue-600">{opportunity.pot_id}</div>
      ),
    },
    {
      key: "name",
      label: "Opportunity",
      sortable: true,
      render: (opportunity) => (
        <div>
          <div className="font-medium text-gray-900">{opportunity.name}</div>
          <div className="text-sm text-gray-500">
            {opportunity.company_name}
          </div>
        </div>
      ),
    },
    {
      key: "current_stage",
      label: "Stage",
      render: (opportunity) => {
        const stageColors = {
          L1_Prospect: "bg-blue-100 text-blue-800",
          L2_Need_Analysis: "bg-yellow-100 text-yellow-800",
          L3_Proposal: "bg-orange-100 text-orange-800",
          Win: "bg-green-100 text-green-800",
          Loss: "bg-red-100 text-red-800",
        };
        const stageLabels = {
          L1_Prospect: "L1 Prospect",
          L2_Need_Analysis: "L2 Need Analysis",
          L3_Proposal: "L3 Proposal",
          Win: "Win",
          Loss: "Loss",
        };
        return (
          <span
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
              stageColors[opportunity.current_stage] ||
              "bg-gray-100 text-gray-800"
            }`}
          >
            {stageLabels[opportunity.current_stage] ||
              opportunity.current_stage}
          </span>
        );
      },
    },
    {
      key: "status",
      label: "Status",
      render: (opportunity) => {
        const statusColors = {
          Open: "bg-green-100 text-green-800",
          Won: "bg-blue-100 text-blue-800",
          Lost: "bg-red-100 text-red-800",
        };
        return (
          <span
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
              statusColors[opportunity.status] || "bg-gray-100 text-gray-800"
            }`}
          >
            {opportunity.status}
          </span>
        );
      },
    },
    {
      key: "amount",
      label: "Value",
      render: (opportunity) => (
        <div className="text-right">
          <div className="font-medium">
            ₹{Number(opportunity.amount || 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-500">
            {opportunity.currency || "INR"}
          </div>
        </div>
      ),
    },
    {
      key: "probability",
      label: "Probability",
      render: (opportunity) => (
        <div className="text-right">
          <div className="font-medium">{opportunity.probability}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${opportunity.probability}%` }}
            ></div>
          </div>
        </div>
      ),
    },
    {
      key: "close_date",
      label: "Close Date",
      render: (opportunity) =>
        opportunity.close_date
          ? new Date(opportunity.close_date).toLocaleDateString()
          : "-",
    },
    {
      key: "converted_by_name",
      label: "Owner",
      render: (opportunity) => (
        <div className="text-sm text-gray-600">
          {opportunity.converted_by_name}
        </div>
      ),
    },
  ];

  useEffect(() => {
    fetchOpportunities();
    fetchStats();
  }, [filters]);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.opportunities.getOpportunities(filters);
      if (response.data?.data?.opportunities) {
        setOpportunities(response.data.data.opportunities);
      }
    } catch (error) {
      console.error("Error fetching opportunities:", error);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      // Mock stats for now
      setStats({
        total: opportunities.length,
        open: opportunities.filter((o) => o.status === "Open").length,
        won: opportunities.filter((o) => o.status === "Won").length,
        lost: opportunities.filter((o) => o.status === "Lost").length,
        totalValue: opportunities.reduce(
          (sum, o) => sum + (Number(o.amount) || 0),
          0
        ),
        winRate:
          opportunities.length > 0
            ? Math.round(
                (opportunities.filter((o) => o.status === "Won").length /
                  opportunities.length) *
                  100
              )
            : 0,
      });
    } catch (error) {
      console.error("Error fetching opportunity stats:", error);
      setStats({
        total: 0,
        open: 0,
        won: 0,
        lost: 0,
        totalValue: 0,
        winRate: 0,
      });
    }
  };

  const handleUpdateStage = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setShowSalesProcessModal(true);
  };

  const actions = [
    {
      label: "View",
      onClick: handleViewOpportunity,
      className: "text-blue-600 hover:text-blue-900",
    },
    {
      label: "Edit",
      onClick: handleEditOpportunity,
      className: "text-green-600 hover:text-green-900",
      show: (opportunity) => opportunity.status === "Open",
    },
    {
      label: "Create Quotation",
      onClick: (opportunity) => {
        console.log("Creating quotation for opportunity:", opportunity.id);
      },
      className: "text-purple-600 hover:text-purple-900",
      show: (opportunity) =>
        opportunity.current_stage === "L3_Proposal" &&
        opportunity.status === "Open",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Opportunities</h1>
        <div className="text-sm text-gray-600">
          Opportunities converted from qualified leads
        </div>
      </div>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
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
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Open</p>
              <p className="text-2xl font-bold text-green-600">{stats.open}</p>
            </div>
            <div className="p-3 rounded-md bg-green-50">
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
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Won</p>
              <p className="text-2xl font-bold text-blue-600">{stats.won}</p>
            </div>
            <div className="p-3 rounded-md bg-blue-50">
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
                  d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Lost</p>
              <p className="text-2xl font-bold text-red-600">{stats.lost}</p>
            </div>
            <div className="p-3 rounded-md bg-red-50">
              <svg
                className="w-6 h-6 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-purple-600">
                ₹{(stats.totalValue / 1000000).toFixed(1)}M
              </p>
            </div>
            <div className="p-3 rounded-md bg-purple-50">
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
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Win Rate</p>
              <p className="text-2xl font-bold text-yellow-600">
                {stats.winRate}%
              </p>
            </div>
            <div className="p-3 rounded-md bg-yellow-50">
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
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search opportunities..."
              value={filters.search}
              onChange={(e) =>
                setFilters((prev) => ({ ...prev, search: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stage
            </label>
            <select
              value={filters.stage}
              onChange={(e) =>
                setFilters((prev) => ({ ...prev, stage: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {stageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) =>
                setFilters((prev) => ({ ...prev, status: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Opportunities Table */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={opportunityColumns}
            data={opportunities}
            actions={actions}
            emptyMessage="No opportunities found. Convert leads to opportunities or create one directly."
          />
        )}
      </div>

      {/* Opportunity Detail Modal */}
      <Modal
        isOpen={!!selectedOpportunity && !showSalesProcessModal}
        onClose={() => setSelectedOpportunity(null)}
        title="Opportunity Details"
        size="xl"
      >
        {selectedOpportunity && renderContent()}
      </Modal>

      {/* Sales Process Update Modal */}
      <Modal
        isOpen={showSalesProcessModal}
        onClose={() => setShowSalesProcessModal(false)}
        title="Update Sales Process Stage"
        size="lg"
      >
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            Sales process update functionality will be implemented here.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowSalesProcessModal(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Handle stage update
                setShowSalesProcessModal(false);
                setSelectedOpportunity(null);
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Update Stage
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default OpportunitiesPage;
