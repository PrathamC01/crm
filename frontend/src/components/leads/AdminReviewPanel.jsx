import React, { useState, useEffect } from "react";
import api, { apiMethods } from "../../utils/api";

const AdminReviewPanel = ({ onClose }) => {
  const [pendingLeads, setPendingLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [reviewComments, setReviewComments] = useState("");
  const [reviewAction, setReviewAction] = useState(""); // 'approve' or 'reject'
  const fetchPendingLeads = async () => {
    try {
      setLoading(true);
      const response = await api("/api/leads/pending-review");
      if (response.status) {
        setPendingLeads(response.data.data.leads || []);
      }
    } catch (err) {
      console.error("Failed to fetch pending leads:", err);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchPendingLeads();
  }, []);

  const handleReviewAction = async (leadId, decision) => {
    if (!reviewComments.trim()) {
      alert("Please enter comments for your review decision.");
      return;
    }

    setActionLoading(true);
    try {
      const response = await apiMethods.leads.approveLead(
        leadId,
        JSON.stringify({
          decision: decision,
          comments: reviewComments.trim(),
        })
      );

      if (response.status) {
        alert(`Lead ${decision.toLowerCase()} successfully!`);
        setSelectedLead(null);
        setReviewComments("");
        setReviewAction("");
        fetchPendingLeads(); // Refresh the list
      } else {
        alert("Failed to process review: " + response.message);
      }
    } catch (err) {
      console.log(err);
      alert("Network error occurred");
    } finally {
      setActionLoading(false);
    }
  };

  const openReviewModal = (lead, action) => {
    setSelectedLead(lead);
    setReviewAction(action);
    setReviewComments("");
  };

  const closeReviewModal = () => {
    setSelectedLead(null);
    setReviewAction("");
    setReviewComments("");
  };

  const formatCurrency = (amount) => {
    if (!amount) return "Not specified";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Admin Review Panel
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Review and approve/reject lead conversion requests
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <svg
              className="w-6 h-6"
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
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : pendingLeads.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 text-lg">✅ No pending reviews</div>
              <p className="text-gray-400 mt-2">
                All conversion requests have been reviewed.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="mb-4">
                <h4 className="text-md font-medium text-gray-900">
                  Pending Reviews ({pendingLeads.length})
                </h4>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lead Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Revenue
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Request Info
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {pendingLeads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {lead.project_title}
                            </div>
                            <div className="text-sm text-gray-500">
                              Status: {lead.status} | Review:{" "}
                              {lead.review_status}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {lead.company_name}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {formatCurrency(lead.expected_revenue)}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            <div>By: {lead.conversion_requester_name}</div>
                            <div className="text-gray-500">
                              {new Date(
                                lead.conversion_request_date
                              ).toLocaleDateString()}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => openReviewModal(lead, "Approved")}
                              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => openReviewModal(lead, "Rejected")}
                              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                            >
                              Reject
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-60">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h4 className="text-lg font-medium text-gray-900">
                {reviewAction} Conversion Request
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                {selectedLead.project_title}
              </p>
            </div>

            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Comments <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={reviewComments}
                  onChange={(e) => setReviewComments(e.target.value)}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={`Enter your comments for ${reviewAction.toLowerCase()}ing this conversion request...`}
                />
              </div>

              <div className="bg-gray-50 p-3 rounded-lg mb-4">
                <div className="text-sm">
                  <div>
                    <strong>Lead:</strong> {selectedLead.project_title}
                  </div>
                  <div>
                    <strong>Company:</strong> {selectedLead.company_name}
                  </div>
                  <div>
                    <strong>Expected Revenue:</strong>{" "}
                    {formatCurrency(selectedLead.expected_revenue)}
                  </div>
                  <div>
                    <strong>Requested By:</strong>{" "}
                    {selectedLead.conversion_requester_name}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={closeReviewModal}
                  disabled={actionLoading}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() =>
                    handleReviewAction(selectedLead.id, reviewAction)
                  }
                  disabled={actionLoading || !reviewComments.trim()}
                  className={`px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors ${
                    reviewAction === "Approved"
                      ? "bg-green-600 hover:bg-green-700 text-white"
                      : "bg-red-600 hover:bg-red-700 text-white"
                  }`}
                >
                  {actionLoading ? "Processing..." : `${reviewAction}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminReviewPanel;
