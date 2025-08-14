import React, { useState, useEffect } from "react";
import { apiRequest } from "../../../utils/api";
import DataTable from "../../common/DataTable";

const CompanyList = ({ onEdit, onView, onDelete }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({
    status: "",
    company_type: "",
    approval_stage: "",
    industry: "",
    is_high_revenue: "",
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0,
  });

  useEffect(() => {
    fetchCompanies();
  }, [search, filters, pagination.skip]);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: pagination.skip,
        limit: pagination.limit,
        ...(search && { search }),
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== "")
        ),
      });

      const response = await apiRequest(`/api/companies?${params}`);
      if (response.status) {
        setCompanies(response.data.companies || []);
        setPagination((prev) => ({
          ...prev,
          total: response.data.total || 0,
        }));
      }
    } catch (err) {
      console.error("Failed to fetch companies:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (company, action, reason = "") => {
    if (
      !window.confirm(
        `Are you sure you want to ${action.toLowerCase()} "${company.name}"?`
      )
    )
      return;

    try {
      const response = await apiRequest(
        `/api/companies/${company.id}/approve`,
        {
          method: "POST",
          body: JSON.stringify({
            action: action,
            reason: reason || undefined,
          }),
        }
      );

      if (response.status) {
        await fetchCompanies();
        alert(`Company ${action.toLowerCase()} successful`);
      } else {
        alert("Failed to process approval: " + response.message);
      }
    } catch (err) {
      alert("Network error occurred");
    }
  };

  const handleDelete = async (companyId, companyName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete "${companyName}"? This action cannot be undone.`
      )
    )
      return;

    try {
      const response = await apiRequest(`/api/companies/${companyId}`, {
        method: "DELETE",
      });

      if (response.status) {
        await fetchCompanies();
        alert("Company deleted successfully");
      } else {
        alert("Failed to delete company: " + response.message);
      }
    } catch (err) {
      alert("Network error occurred");
    }
  };

  const handlePageChange = (newPage) => {
    const newSkip = (newPage - 1) * pagination.limit;
    setPagination((prev) => ({ ...prev, skip: newSkip }));
  };

  const handleFilterChange = (filterName, value) => {
    setFilters((prev) => ({ ...prev, [filterName]: value }));
    setPagination((prev) => ({ ...prev, skip: 0 }));
  };

  const getStatusBadge = (status, approvalStage) => {
    let bgColor, textColor, text;

    switch (status) {
      case "ACTIVE":
        bgColor = "bg-green-100";
        textColor = "text-green-800";
        text = "Active";
        break;
      case "INACTIVE":
        bgColor = "bg-red-100";
        textColor = "text-red-800";
        text = "Inactive";
        break;
      case "PENDING_APPROVAL":
        switch (approvalStage) {
          case "DRAFT":
            bgColor = "bg-gray-100";
            textColor = "text-gray-800";
            text = "Draft";
            break;
          case "L1_PENDING":
            bgColor = "bg-yellow-100";
            textColor = "text-yellow-800";
            text = "L1 Pending";
            break;
          case "ADMIN_PENDING":
            bgColor = "bg-blue-100";
            textColor = "text-blue-800";
            text = "Admin Pending";
            break;
          case "REJECTED":
            bgColor = "bg-red-100";
            textColor = "text-red-800";
            text = "Rejected";
            break;
          default:
            bgColor = "bg-orange-100";
            textColor = "text-orange-800";
            text = "Pending";
        }
        break;
      default:
        bgColor = "bg-gray-100";
        textColor = "text-gray-800";
        text = status;
    }

    return (
      <span
        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${bgColor} ${textColor}`}
      >
        {text}
      </span>
    );
  };

  const getCompanyTypeBadge = (type) => {
    const typeMap = {
      DOMESTIC_GST: {
        label: "Domestic GST",
        color: "bg-blue-100 text-blue-800",
      },
      DOMESTIC_NONGST: {
        label: "Domestic Non-GST",
        color: "bg-purple-100 text-purple-800",
      },
      NGO: { label: "NGO", color: "bg-green-100 text-green-800" },
      OVERSEAS: { label: "Overseas", color: "bg-orange-100 text-orange-800" },
    };

    const typeInfo = typeMap[type] || {
      label: type,
      color: "bg-gray-100 text-gray-800",
    };

    return (
      <span
        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${typeInfo.color}`}
      >
        {typeInfo.label}
      </span>
    );
  };

  const renderApprovalActions = (company) => {
    const actions = [];

    if (company.approval_stage === "L1_PENDING") {
      actions.push(
        <button
          key="l1-approve"
          onClick={() => handleApproval(company, "APPROVE")}
          className="text-green-600 hover:text-green-900 text-xs mr-2"
        >
          L1 Approve
        </button>
      );
      actions.push(
        <button
          key="l1-reject"
          onClick={() => {
            const reason = prompt("Reason for rejection:");
            if (reason) handleApproval(company, "REJECT", reason);
          }}
          className="text-red-600 hover:text-red-900 text-xs"
        >
          Reject
        </button>
      );
    }

    if (company.approval_stage === "ADMIN_PENDING") {
      actions.push(
        <button
          key="admin-approve"
          onClick={() => handleApproval(company, "APPROVE")}
          className="text-green-600 hover:text-green-900 text-xs mr-2"
        >
          Activate
        </button>
      );
      actions.push(
        <button
          key="admin-reject"
          onClick={() => {
            const reason = prompt("Reason for rejection:");
            if (reason) handleApproval(company, "REJECT", reason);
          }}
          className="text-red-600 hover:text-red-900 text-xs"
        >
          Reject
        </button>
      );
    }

    return actions.length > 0 ? <div className="mt-2">{actions}</div> : null;
  };

  // Define columns for DataTable
  const columns = [
    {
      key: "name",
      label: "Company Details",
      render: (company) => (
        <div>
          <div className="text-sm font-medium text-gray-900 flex items-center">
            {company.name}
            {company.is_high_revenue && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                💰 High Revenue
              </span>
            )}
          </div>
          {company.website && (
            <div className="text-sm text-blue-600 hover:text-blue-800">
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
              >
                {company.website}
              </a>
            </div>
          )}
          <div className="text-sm text-gray-500">
            {[company.city, company.state, company.country]
              .filter(Boolean)
              .join(", ")}
          </div>
          {company.parent_company_name && (
            <div className="text-xs text-gray-400">
              Parent: {company.parent_company_name}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "type",
      label: "Type & Industry",
      render: (company) => (
        <div className="space-y-1">
          {getCompanyTypeBadge(company.company_type)}
          <div className="text-sm text-gray-900">
            {company.industry?.replace(/_/g, " ")}
          </div>
          {company.sub_industry && (
            <div className="text-xs text-gray-500">{company.sub_industry}</div>
          )}
        </div>
      ),
    },
    {
      key: "compliance",
      label: "Compliance",
      render: (company) => (
        <div className="text-sm text-gray-900">
          {company.gst_number && (
            <div>
              GST:{" "}
              <span className="font-mono text-xs">{company.gst_number}</span>
            </div>
          )}
          {company.pan_number && (
            <div>
              PAN:{" "}
              <span className="font-mono text-xs">{company.pan_number}</span>
            </div>
          )}
          {company.international_unique_id && (
            <div>
              ID:{" "}
              <span className="font-mono text-xs">
                {company.international_unique_id}
              </span>
            </div>
          )}
          {!company.gst_number &&
            !company.pan_number &&
            !company.international_unique_id && (
              <span className="text-gray-400 text-xs">Not provided</span>
            )}
          {company.verification_source && (
            <div className="text-xs text-gray-500 mt-1">
              Verified: {company.verification_source}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "status",
      label: "Status & Revenue",
      render: (company) => (
        <div className="space-y-2">
          {getStatusBadge(company.status, company.approval_stage)}
          {company.annual_revenue && (
            <div className="text-sm text-gray-600">
              ₹{(company.annual_revenue / 10000000).toFixed(1)}Cr
            </div>
          )}
          {company.sla_breach_date && (
            <div className="text-xs text-red-600 flex items-center">
              ⚠️ SLA Breach
            </div>
          )}
        </div>
      ),
    },
  ];

  // Define actions for DataTable
  const actions = [
    {
      label: "View",
      onClick: (company) => onView(company),
      className: "text-indigo-600 hover:text-indigo-900",
    },
    {
      label: "Edit",
      onClick: (company) => onEdit(company),
      className: "text-blue-600 hover:text-blue-900",
    },
    {
      label: "Delete",
      onClick: (company) => handleDelete(company.id, company.name),
      className: "text-red-600 hover:text-red-900",
    },
  ];

  // Prepare pagination data for DataTable
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  const paginationData = {
    page: currentPage,
    pages: totalPages,
    per_page: pagination.limit,
    total: pagination.total,
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search companies by name, industry, city, GST, or PAN..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPagination((prev) => ({ ...prev, skip: 0 }));
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Advanced Filters */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange("status", e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="PENDING_APPROVAL">Pending Approval</option>
          </select>

          <select
            value={filters.company_type}
            onChange={(e) => handleFilterChange("company_type", e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="DOMESTIC_GST">Domestic GST</option>
            <option value="DOMESTIC_NONGST">Domestic Non-GST</option>
            <option value="NGO">NGO</option>
            <option value="OVERSEAS">Overseas</option>
          </select>

          <select
            value={filters.approval_stage}
            onChange={(e) =>
              handleFilterChange("approval_stage", e.target.value)
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Stages</option>
            <option value="DRAFT">Draft</option>
            <option value="L1_PENDING">L1 Pending</option>
            <option value="ADMIN_PENDING">Admin Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>

          <select
            value={filters.industry}
            onChange={(e) => handleFilterChange("industry", e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Industries</option>
            <option value="BFSI">BFSI</option>
            <option value="Government">Government</option>
            <option value="IT_ITeS">IT/ITeS</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Education">Education</option>
            <option value="Telecom">Telecom</option>
          </select>

          <select
            value={filters.is_high_revenue}
            onChange={(e) =>
              handleFilterChange("is_high_revenue", e.target.value)
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Revenue</option>
            <option value="true">High Revenue ({">₹2Cr"})</option>
            <option value="false">Standard Revenue</option>
          </select>
        </div>
      </div>

      {/* DataTable */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <DataTable
          columns={columns}
          data={companies}
          loading={loading}
          pagination={paginationData}
          onPageChange={handlePageChange}
          actions={actions}
          renderHtml={renderApprovalActions}
          emptyMessage={
            search || Object.values(filters).some((f) => f)
              ? "No companies found matching your criteria"
              : "No companies found"
          }
        />
      </div>
    </div>
  );
};

export default CompanyList;
