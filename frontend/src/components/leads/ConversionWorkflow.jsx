import React, { useState } from "react";
import api, { apiMethods } from "../../utils/api";

const ConversionWorkflow = ({ lead, currentUser, onUpdate, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Check user role
  const userRoles = currentUser?.roles || [];
  const isAdmin = userRoles.includes("admin") || userRoles.includes("reviewer");
  const canApprove = isAdmin;
  const canConvert =
    isAdmin || (lead.review_status === "Approved" && lead.reviewed);

  const handleRequestConversion = async () => {
    const notes = prompt("Enter any notes for the conversion request:");
    if (notes === null) return; // User cancelled

    setLoading(true);
    setError("");

    try {
      const response = await api.post(
        `/api/leads/${lead.id}/request-conversion`,
        JSON.stringify({ notes })
      );
      // const response = await apiMethods.leads.

      if (response.status) {
        alert(
          "Conversion request submitted successfully. Waiting for admin review."
        );
        onUpdate();
      } else {
        setError(response.message || "Failed to request conversion");
      }
    } catch (err) {
      setError("Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReject = async (decision) => {
    const actionText = decision === "Approved" ? "approve" : "reject";
    const comments = prompt(
      `Enter comments to ${actionText} this conversion request:`
    );
    if (!comments || comments.trim() === "") {
      alert(`Comments are required to ${actionText} the request.`);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.post(
        `/api/leads/${lead.id}/review`,
        JSON.stringify({
          decision: decision,
          comments: comments.trim(),
        })
      );

      if (response.status) {
        alert(`Conversion request ${decision.toLowerCase()} successfully.`);
        onUpdate();
      } else {
        setError(
          response.message || `Failed to ${actionText} conversion request`
        );
      }
    } catch (err) {
      setError("Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleConvertToOpportunity = async () => {
    // Check if user has permission
    if (!canConvert) {
      alert(
        "❗ This opportunity needs to be reviewed by an Admin before it can be converted."
      );
      return;
    }

    const opportunityName = prompt(
      "Enter opportunity name:",
      `${lead.project_title} Opportunity`
    );
    if (opportunityName === null) return; // User cancelled

    const notes = prompt("Enter any additional notes for the opportunity:");
    if (notes === null) return; // User cancelled

    setLoading(true);
    setError("");

    try {
      const response = await api.post(
        `/api/leads/${lead.id}/convert-to-opportunity`,
        JSON.stringify({
          opportunity_name: opportunityName,
          notes,
        })
      );

      if (response.status) {
        alert(
          `Lead successfully converted to opportunity: ${response.data.opportunity_pot_id}`
        );
        onUpdate();
        onClose();
      } else {
        setError(response.message || "Failed to convert to opportunity");
      }
    } catch (err) {
      setError("Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-2xl mx-auto">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg text-left font-medium text-gray-900">
          Convert to Opportunity Workflow
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {lead.project_title} - {lead.company_name}
        </p>
      </div>

      <div className="p-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Current Status */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Current Status</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Lead Status:</span>
              <span
                className={`ml-2 px-2 py-1 rounded-full text-xs font-semibold ${
                  lead.status === "Qualified"
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {lead.status}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Review Status:</span>
              <span
                className={`ml-2 px-2 py-1 rounded-full text-xs font-semibold ${
                  lead.review_status === "Approved"
                    ? "bg-green-100 text-green-800"
                    : lead.review_status === "Rejected"
                    ? "bg-red-100 text-red-800"
                    : "bg-yellow-100 text-yellow-800"
                }`}
              >
                {lead.review_status}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Conversion Requested:</span>
              <span
                className={`ml-2 ${
                  lead.conversion_requested ? "text-green-600" : "text-gray-600"
                }`}
              >
                {lead.conversion_requested ? "✓ Yes" : "✗ No"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Already Converted:</span>
              <span
                className={`ml-2 ${
                  lead.converted ? "text-green-600" : "text-gray-600"
                }`}
              >
                {lead.converted ? "✓ Yes" : "✗ No"}
              </span>
            </div>
          </div>
        </div>

        {/* Workflow Progress */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-3">
            Conversion Workflow
          </h4>
          <div className="flex items-center space-x-4">
            {/* Step 1: Qualification */}
            <div className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  lead.status === "Qualified"
                    ? "bg-green-500 text-white"
                    : "bg-gray-300 text-gray-600"
                }`}
              >
                1
              </div>
              <span className="ml-2 text-sm">Qualified</span>
            </div>

            <div
              className={`flex-1 h-1 ${
                lead.conversion_requested ? "bg-green-500" : "bg-gray-300"
              }`}
            ></div>

            {/* Step 2: Request Conversion */}
            <div className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  lead.conversion_requested
                    ? "bg-green-500 text-white"
                    : "bg-gray-300 text-gray-600"
                }`}
              >
                2
              </div>
              <span className="ml-2 text-sm">Request</span>
            </div>

            <div
              className={`flex-1 h-1 ${
                lead.reviewed && lead.review_status === "Approved"
                  ? "bg-green-500"
                  : "bg-gray-300"
              }`}
            ></div>

            {/* Step 3: Admin Review */}
            <div className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  lead.reviewed && lead.review_status === "Approved"
                    ? "bg-green-500 text-white"
                    : lead.reviewed && lead.review_status === "Rejected"
                    ? "bg-red-500 text-white"
                    : "bg-gray-300 text-gray-600"
                }`}
              >
                3
              </div>
              <span className="ml-2 text-sm">Review</span>
            </div>

            <div
              className={`flex-1 h-1 ${
                lead.converted ? "bg-green-500" : "bg-gray-300"
              }`}
            ></div>

            {/* Step 4: Convert */}
            <div className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  lead.converted
                    ? "bg-green-500 text-white"
                    : "bg-gray-300 text-gray-600"
                }`}
              >
                4
              </div>
              <span className="ml-2 text-sm">Convert</span>
            </div>
          </div>
        </div>

        {/* Review Information */}
        {lead.conversion_requested && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-3">
              Review Information
            </h4>
            <div className="space-y-2 text-sm">
              {lead.conversion_request_date && (
                <div>
                  <span className="text-gray-500">Request Date:</span>
                  <span className="ml-2">
                    {new Date(lead.conversion_request_date).toLocaleString()}
                  </span>
                </div>
              )}
              {lead.conversion_requester_name && (
                <div>
                  <span className="text-gray-500">Requested By:</span>
                  <span className="ml-2">{lead.conversion_requester_name}</span>
                </div>
              )}
              {lead.reviewed && lead.reviewer_name && (
                <div>
                  <span className="text-gray-500">Reviewed By:</span>
                  <span className="ml-2">{lead.reviewer_name}</span>
                </div>
              )}
              {lead.review_date && (
                <div>
                  <span className="text-gray-500">Review Date:</span>
                  <span className="ml-2">
                    {new Date(lead.review_date).toLocaleString()}
                  </span>
                </div>
              )}
              {lead.review_comments && (
                <div>
                  <span className="text-gray-500">Review Comments:</span>
                  <div className="mt-1 p-2 bg-white rounded border text-gray-900">
                    {lead.review_comments}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Conversion Information */}
        {lead.converted && (
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-900 mb-3">
              Conversion Complete
            </h4>
            <div className="space-y-2 text-sm">
              {lead.conversion_date && (
                <div>
                  <span className="text-gray-700">Converted On:</span>
                  <span className="ml-2">
                    {new Date(lead.conversion_date).toLocaleString()}
                  </span>
                </div>
              )}
              {lead.converted_to_opportunity_id && (
                <div>
                  <span className="text-gray-700">Opportunity ID:</span>
                  <span className="ml-2">
                    #{lead.converted_to_opportunity_id}
                  </span>
                </div>
              )}
              {lead.conversion_notes && (
                <div>
                  <span className="text-gray-700">Conversion Notes:</span>
                  <div className="mt-1 p-2 bg-white rounded border text-gray-900">
                    {lead.conversion_notes}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        {!lead.converted && (
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-gray-500">
              {isAdmin ? (
                <span className="text-green-600">
                  ✓ You have admin privileges
                </span>
              ) : (
                <span>Sales/User role - Limited permissions</span>
              )}
            </div>

            <div className="flex space-x-3">
              {/* Request Conversion Button */}
              {lead.can_request_conversion && (
                <button
                  onClick={handleRequestConversion}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
                >
                  {loading ? "Requesting..." : "Request Conversion"}
                </button>
              )}

              {/* Admin Review Buttons */}
              {canApprove && lead.needs_admin_review && (
                <>
                  <button
                    onClick={() => handleApproveReject("Approved")}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
                  >
                    {loading ? "Processing..." : "Approve"}
                  </button>
                  <button
                    onClick={() => handleApproveReject("Rejected")}
                    disabled={loading}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
                  >
                    {loading ? "Processing..." : "Reject"}
                  </button>
                </>
              )}

              {/* Convert to Opportunity Button */}
              {lead.can_convert_to_opportunity ||
              (isAdmin && lead.status === "Qualified") ? (
                <button
                  onClick={handleConvertToOpportunity}
                  disabled={loading}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
                >
                  {loading ? "Converting..." : "Convert to Opportunity"}
                </button>
              ) : lead.status === "Qualified" && !lead.reviewed && !isAdmin ? (
                <button
                  onClick={() =>
                    alert(
                      "❗ This opportunity needs to be reviewed by an Admin before it can be converted."
                    )
                  }
                  className="bg-gray-400 text-white px-4 py-2 rounded-lg font-medium cursor-not-allowed"
                >
                  Convert to Opportunity
                </button>
              ) : null}
            </div>
          </div>
        )}

        {/* Close Button */}
        <div className="flex justify-end pt-4 border-t">
          <button
            onClick={onClose}
            className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConversionWorkflow;
