import React, { useState, useEffect } from "react";
import { apiRequest } from "../utils/api";

const LeadsList = ({ onEditLead, onViewLead }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  // Lead status options from backend enum
  const statusOptions = [
    { value: "New", label: "New", color: "blue" },
    { value: "Active", label: "Active", color: "green" },
    { value: "Contacted", label: "Contacted", color: "yellow" },
    { value: "Qualified", label: "Qualified", color: "purple" },
    { value: "Unqualified", label: "Unqualified", color: "red" },
    { value: "Converted", label: "Converted", color: "indigo" },
    { value: "Rejected", label: "Rejected", color: "gray" },
  ];

  const getStatusColor = (status) => {
    const option = statusOptions.find((opt) => opt.value === status);
    return option ? option.color : "gray";
  };

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter !== "all") {
        params.append("status", statusFilter);
      }
      if (searchTerm) {
        params.append("search", searchTerm);
      }

      const response = await apiRequest(`/api/leads/?${params.toString()}`);
      if (response && response.status) {
        setLeads(response.data.leads || []);
      }
    } catch (error) {
      console.error("Failed to fetch leads:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (leadId, newStatus) => {
    try {
      const response = await apiRequest(`/api/leads/${leadId}`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus }),
      });

      if (response && response.status) {
        // Update the lead in the local state
        setLeads((prevLeads) =>
          prevLeads.map((lead) =>
            lead.id === leadId ? { ...lead, status: newStatus } : lead
          )
        );

        // Show success message
        alert(`Lead status updated to ${newStatus} successfully!`);
      } else {
        alert("Failed to update lead status. Please try again.");
      }
    } catch (error) {
      console.error("Failed to update lead status:", error);
      alert("Error updating lead status. Please try again.");
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [statusFilter, searchTerm]);

  const StatusBadge = ({ status }) => {
    const color = getStatusColor(status);
    const colorClasses = {
      blue: "bg-blue-100 text-blue-800 border-blue-200",
      green: "bg-green-100 text-green-800 border-green-200",
      yellow: "bg-yellow-100 text-yellow-800 border-yellow-200",
      purple: "bg-purple-100 text-purple-800 border-purple-200",
      red: "bg-red-100 text-red-800 border-red-200",
      indigo: "bg-indigo-100 text-indigo-800 border-indigo-200",
      gray: "bg-gray-100 text-gray-800 border-gray-200",
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-medium rounded-full border ${colorClasses[color]}`}
      >
        {status} test
      </span>
    );
  };

  const StatusDropdown = ({ currentStatus, leadId }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown on outside click
    useEffect(() => {
      const handleClickOutside = (event) => {
        if (
          dropdownRef.current &&
          !dropdownRef.current.contains(event.target)
        ) {
          setIsOpen(false);
        }
      };
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }, []);
    return (
      <div className="relative overlflow">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Change Status
          <svg
            className="w-4 h-4 ml-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute right-0 z-20 mt-1 w-48 max-h-64 overflow-y-auto bg-white border border-gray-200 rounded-md shadow-lg">
            <div className="py-1">
              {statusOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    handleStatusChange(leadId, option.value);
                    setIsOpen(false);
                  }}
                  className={`block w-full px-4 py-2 text-sm text-left hover:bg-gray-100 ${
                    currentStatus === option.value
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700"
                  }`}
                  disabled={currentStatus === option.value}
                >
                  <div className="flex items-center">
                    <StatusBadge status={option.value + "test"} />
                    <span className="ml-2">{option.label} test</span>
                    {currentStatus === option.value && (
                      <svg
                        className="w-4 h-4 ml-auto text-blue-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div>
            <label
              htmlFor="status-filter"
              className="block text-sm font-medium text-gray-700"
            >
              Status Filter
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="mt-1 block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">All Statuses</option>
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="search"
              className="block text-sm font-medium text-gray-700"
            >
              Search Leads
            </label>
            <input
              type="text"
              id="search"
              placeholder="Search by project title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mt-1 block w-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="p-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading leads...</p>
          </div>
        ) : leads.length === 0 ? (
          <div className="p-6 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No leads found
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {statusFilter !== "all" || searchTerm
                ? "Try adjusting your filters or search terms."
                : "Get started by creating your first lead."}
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {leads.map((lead) => (
              <li key={lead.id} className="px-6 py-4 hover:bg-gray-50 relative">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {lead.project_title
                            ? lead.project_title.charAt(0).toUpperCase()
                            : "L"}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900">
                          {lead.project_title || "Untitled Lead"}
                        </div>
                        <StatusBadge status={lead.status} />
                      </div>
                      <div className="text-sm text-gray-500">
                        {lead.company_name && (
                          <span>Company: {lead.company_name} • </span>
                        )}
                        Priority: {lead.priority || "Medium"}
                        {lead.expected_revenue && (
                          <span>
                            {" "}
                            • Expected Revenue: ₹
                            {parseFloat(lead.expected_revenue).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <StatusDropdown
                      currentStatus={lead.status}
                      leadId={lead.id}
                    />

                    <button
                      onClick={() => onViewLead && onViewLead(lead)}
                      className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      View
                    </button>

                    <button
                      onClick={() => onEditLead && onEditLead(lead)}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      Edit
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Status Change Legend */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-3">
          Lead Status Workflow
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-blue-800">
          <div>
            <StatusBadge status="New" /> → <StatusBadge status="Active" /> →{" "}
            <StatusBadge status="Contacted" />
          </div>
          <div>
            <StatusBadge status="Contacted" /> →{" "}
            <StatusBadge status="Qualified" /> →{" "}
            <StatusBadge status="Converted" />
          </div>
          <div>
            Or → <StatusBadge status="Unqualified" /> /{" "}
            <StatusBadge status="Rejected" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadsList;
