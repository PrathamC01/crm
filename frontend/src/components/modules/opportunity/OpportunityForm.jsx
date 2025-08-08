import React, { useState, useEffect } from "react";
import {
  opportunityAPI,
  apiRequest,
  OPPORTUNITY_STAGES,
  OPPORTUNITY_STAGE_LABELS,
  OPPORTUNITY_STATUSES,
  QUALIFICATION_STATUSES,
  GO_NO_GO_STATUSES,
  QUOTATION_STATUSES,
} from "../../../utils/api";

const OpportunityForm = ({ opportunity, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    // Core fields
    lead_id: "",
    company_id: "",
    contact_id: "",
    name: "",
    stage: OPPORTUNITY_STAGES.L1_PROSPECT,
    amount: "",
    scoring: 0,
    costing: "",
    status: OPPORTUNITY_STATUSES.OPEN,
    justification: "",
    close_date: null,
    probability: 10,
    notes: "",

    // L1 - Qualification fields
    requirement_gathering_notes: "",
    go_no_go_status: GO_NO_GO_STATUSES.PENDING,
    qualification_completed_by: "",
    qualification_status: "",
    qualification_scorecard: {},

    // L2 - Need Analysis / Demo fields
    demo_completed: false,
    demo_date: null,
    demo_summary: "",
    presentation_materials: [],
    qualification_meeting_completed: false,
    qualification_meeting_date: null,
    qualification_meeting_notes: "",

    // L3 - Proposal / Bid Submission fields
    quotation_created: false,
    quotation_status: QUOTATION_STATUSES.DRAFT,
    quotation_version: 1,
    proposal_prepared: false,
    proposal_submitted: false,
    proposal_submission_date: null,
    poc_completed: false,
    poc_notes: "",
    solutions_team_approval_notes: "",

    // L4 - Negotiation fields
    customer_discussion_notes: "",
    proposal_updated: false,
    updated_proposal_submitted: false,
    negotiation_rounds: 0,
    commercial_approval_required: false,
    commercial_approval_status: "",

    // L5 - Won fields
    kickoff_meeting_scheduled: false,
    kickoff_meeting_date: null,
    loi_received: false,
    order_verified: false,
    handoff_to_delivery: false,
    delivery_team_assigned: "",

    // Lost/Dropped fields
    lost_reason: "",
    competitor_name: "",
    follow_up_date: null,
    drop_reason: "",
    reactivate_date: null,
  });

  const [leads, setLeads] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [decisionMakers, setDecisionMakers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [currentTab, setCurrentTab] = useState("basic");

  useEffect(() => {
    if (opportunity) {
      setFormData({
        ...opportunity,
        // Handle date fields
        demo_date: opportunity.demo_date
          ? new Date(opportunity.demo_date).toISOString().slice(0, 16)
          : null,
        qualification_meeting_date: opportunity.qualification_meeting_date
          ? new Date(opportunity.qualification_meeting_date)
              .toISOString()
              .slice(0, 16)
          : null,
        proposal_submission_date: opportunity.proposal_submission_date
          ? new Date(opportunity.proposal_submission_date)
              .toISOString()
              .slice(0, 16)
          : null,
        kickoff_meeting_date: opportunity.kickoff_meeting_date
          ? new Date(opportunity.kickoff_meeting_date)
              .toISOString()
              .slice(0, 16)
          : null,
        close_date: opportunity.close_date || null,
        follow_up_date: opportunity.follow_up_date || null,
        reactivate_date: opportunity.reactivate_date || null,

        // Ensure proper defaults
        qualification_scorecard: opportunity.qualification_scorecard || {},
        presentation_materials: opportunity.presentation_materials || [],
      });
    }

    fetchInitialData();
  }, [opportunity]);

  useEffect(() => {
    if (formData.company_id) {
      fetchDecisionMakers(formData.company_id);
    }
  }, [formData.company_id]);

  const fetchInitialData = async () => {
    try {
      const [leadsRes, companiesRes, usersRes] = await Promise.all([
        apiRequest("/api/leads?status=Qualified"),
        apiRequest("/api/companies"),
        apiRequest("/api/users"),
      ]);

      if (leadsRes.status) setLeads(leadsRes.data.leads || []);
      if (companiesRes.status) setCompanies(companiesRes.data.companies || []);
      if (usersRes.status) setUsers(usersRes.data.users || []);
    } catch (err) {
      console.error("Failed to fetch initial data:", err);
    }
  };

  const fetchDecisionMakers = async (companyId) => {
    try {
      const response = await apiRequest(
        `/api/contacts/company/${companyId}/decision-makers`
      );
      if (response.status) {
        setDecisionMakers(response.data.decision_makers || []);
      }
    } catch (err) {
      console.error("Failed to fetch decision makers:", err);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Opportunity name is required";
    }

    if (!formData.company_id) {
      newErrors.company_id = "Company is required";
    }

    if (!formData.contact_id) {
      newErrors.contact_id = "Decision maker contact is required";
    }

    if (formData.amount) {
      const amount = parseFloat(formData.amount);
      if (isNaN(amount) || amount < 0) {
        newErrors.amount = "Amount must be a valid positive number";
      } else if (amount >= 1000000 && !formData.justification.trim()) {
        newErrors.justification = "Justification required for amounts ≥₹10L";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      const response = opportunity
        ? await opportunityAPI.updateOpportunity(opportunity.id, formData)
        : await opportunityAPI.createOpportunity(formData);

      if (response.status) {
        onSave(response.data);
      } else {
        setErrors({ submit: response.message || "Operation failed" });
      }
    } catch (err) {
      setErrors({ submit: "Network error occurred" });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === "checkbox" ? checked : value;

    setFormData((prev) => ({ ...prev, [name]: fieldValue }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleLeadSelect = (leadId) => {
    const selectedLead = leads.find((lead) => lead.id === leadId);
    if (selectedLead) {
      setFormData((prev) => ({
        ...prev,
        lead_id: leadId,
        company_id: selectedLead.company_id || "",
        name: `${selectedLead.company_name} Opportunity`,
      }));
    }
  };

  const tabs = [
    { id: "basic", name: "Basic Info", icon: "📋" },
    { id: "qualification", name: "L1 - Qualification", icon: "✅" },
    { id: "demo", name: "L2 - Demo", icon: "🎯" },
    { id: "proposal", name: "L3 - Proposal", icon: "📄" },
    { id: "negotiation", name: "L4 - Negotiation", icon: "🤝" },
    { id: "won", name: "L5 - Won Tasks", icon: "🏆" },
  ];

  const renderBasicInfo = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Source Lead
          </label>
          <select
            name="lead_id"
            value={formData.lead_id}
            onChange={(e) => handleLeadSelect(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select source lead (optional)</option>
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>
                {lead.company_name} - {lead.lead_source}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company <span className="text-red-500">*</span>
          </label>
          <select
            name="company_id"
            required
            value={formData.company_id}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.company_id ? "border-red-300" : "border-gray-300"
            }`}
          >
            <option value="">Select a company</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
          {errors.company_id && (
            <p className="text-red-500 text-sm mt-1">{errors.company_id}</p>
          )}
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Opportunity Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="name"
            required
            value={formData.name}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.name ? "border-red-300" : "border-gray-300"
            }`}
            placeholder="Enter opportunity name"
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1">{errors.name}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Decision Maker Contact <span className="text-red-500">*</span>
          </label>
          <select
            name="contact_id"
            required
            value={formData.contact_id}
            onChange={handleInputChange}
            disabled={!formData.company_id}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.contact_id ? "border-red-300" : "border-gray-300"
            } ${!formData.company_id ? "bg-gray-100" : ""}`}
          >
            <option value="">Select decision maker</option>
            {decisionMakers.map((contact) => (
              <option key={contact.id} value={contact.id}>
                {contact.full_name} - {contact.designation}
              </option>
            ))}
          </select>
          {errors.contact_id && (
            <p className="text-red-500 text-sm mt-1">{errors.contact_id}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Stage
          </label>
          <select
            name="stage"
            value={formData.stage}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {Object.entries(OPPORTUNITY_STAGE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount (₹)
          </label>
          <input
            type="number"
            name="amount"
            min="0"
            step="0.01"
            value={formData.amount}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.amount ? "border-red-300" : "border-gray-300"
            }`}
            placeholder="Enter amount"
          />
          {errors.amount && (
            <p className="text-red-500 text-sm mt-1">{errors.amount}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Probability (%)
          </label>
          <input
            type="number"
            name="probability"
            min="0"
            max="100"
            value={formData.probability}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {parseFloat(formData.amount || 0) >= 1000000 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Justification <span className="text-red-500">*</span>
          </label>
          <textarea
            name="justification"
            required
            rows="3"
            value={formData.justification}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.justification ? "border-red-300" : "border-gray-300"
            }`}
            placeholder="Justification required for amounts ≥₹10L"
          />
          {errors.justification && (
            <p className="text-red-500 text-sm mt-1">{errors.justification}</p>
          )}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          name="notes"
          rows="4"
          value={formData.notes}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Additional notes about the opportunity..."
        />
      </div>
    </div>
  );

  const renderQualificationTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-blue-900 mb-2">
          L1 - Qualification Stage (15%)
        </h4>
        <p className="text-blue-800 text-sm">
          Validate if the lead meets basic qualification criteria and capture
          BANT/CHAMP data.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Requirement Gathering Notes
          </label>
          <textarea
            name="requirement_gathering_notes"
            rows="4"
            value={formData.requirement_gathering_notes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document the customer's requirements and needs..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Go/No Go Call Status
          </label>
          <select
            name="go_no_go_status"
            value={formData.go_no_go_status}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={GO_NO_GO_STATUSES.PENDING}>Pending</option>
            <option value={GO_NO_GO_STATUSES.GO}>Go</option>
            <option value={GO_NO_GO_STATUSES.NO_GO}>No Go</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Qualification Status
          </label>
          <select
            name="qualification_status"
            value={formData.qualification_status}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select Status</option>
            <option value={QUALIFICATION_STATUSES.QUALIFIED}>Qualified</option>
            <option value={QUALIFICATION_STATUSES.NOT_NOW}>Not Now</option>
            <option value={QUALIFICATION_STATUSES.DISQUALIFIED}>
              Disqualified
            </option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Completed By
          </label>
          <select
            name="qualification_completed_by"
            value={formData.qualification_completed_by}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select User</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Scoring (0-100)
          </label>
          <input
            type="number"
            name="scoring"
            min="0"
            max="100"
            value={formData.scoring}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderDemoTab = () => (
    <div className="space-y-6">
      <div className="bg-indigo-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-indigo-900 mb-2">
          L2 - Need Analysis / Demo (40%)
        </h4>
        <p className="text-indigo-800 text-sm">
          Conduct product demos and qualification meetings to understand
          customer needs.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="demo_completed"
            name="demo_completed"
            checked={formData.demo_completed}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="demo_completed"
            className="text-sm font-medium text-gray-700"
          >
            Product Demo / Presentation Completed
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Demo Date
          </label>
          <input
            type="datetime-local"
            name="demo_date"
            value={formData.demo_date}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Demo Summary
          </label>
          <textarea
            name="demo_summary"
            rows="3"
            value={formData.demo_summary}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Summarize the demo session and customer feedback..."
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="qualification_meeting_completed"
            name="qualification_meeting_completed"
            checked={formData.qualification_meeting_completed}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="qualification_meeting_completed"
            className="text-sm font-medium text-gray-700"
          >
            Qualification Meeting with Customer Completed
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Qualification Meeting Date
          </label>
          <input
            type="datetime-local"
            name="qualification_meeting_date"
            value={formData.qualification_meeting_date}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Qualification Meeting Notes
          </label>
          <textarea
            name="qualification_meeting_notes"
            rows="3"
            value={formData.qualification_meeting_notes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document meeting outcomes and next steps..."
          />
        </div>
      </div>
    </div>
  );

  const renderProposalTab = () => (
    <div className="space-y-6">
      <div className="bg-purple-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-purple-900 mb-2">
          L3 - Proposal / Bid Submission (60%)
        </h4>
        <p className="text-purple-800 text-sm">
          Prepare and submit quotations, proposals, and conduct POCs with
          approval workflows.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="quotation_created"
            name="quotation_created"
            checked={formData.quotation_created}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="quotation_created"
            className="text-sm font-medium text-gray-700"
          >
            Quotation Created
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Quotation Status
          </label>
          <select
            name="quotation_status"
            value={formData.quotation_status}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={QUOTATION_STATUSES.DRAFT}>Draft</option>
            <option value={QUOTATION_STATUSES.SUBMITTED}>Submitted</option>
            <option value={QUOTATION_STATUSES.APPROVED}>Approved</option>
            <option value={QUOTATION_STATUSES.REVISION_REQUIRED}>
              Revision Required
            </option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Quotation Version
          </label>
          <input
            type="number"
            name="quotation_version"
            min="1"
            value={formData.quotation_version}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="proposal_prepared"
            name="proposal_prepared"
            checked={formData.proposal_prepared}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="proposal_prepared"
            className="text-sm font-medium text-gray-700"
          >
            Proposal Preparation Completed
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="proposal_submitted"
            name="proposal_submitted"
            checked={formData.proposal_submitted}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="proposal_submitted"
            className="text-sm font-medium text-gray-700"
          >
            Proposal Submitted
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Proposal Submission Date
          </label>
          <input
            type="datetime-local"
            name="proposal_submission_date"
            value={formData.proposal_submission_date}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="poc_completed"
            name="poc_completed"
            checked={formData.poc_completed}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="poc_completed"
            className="text-sm font-medium text-gray-700"
          >
            POC Completed
          </label>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            POC Notes
          </label>
          <textarea
            name="poc_notes"
            rows="3"
            value={formData.poc_notes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document POC results and feedback..."
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Solutions Team Approval Notes
          </label>
          <textarea
            name="solutions_team_approval_notes"
            rows="2"
            value={formData.solutions_team_approval_notes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Solutions team feedback and approval comments..."
          />
        </div>
      </div>
    </div>
  );

  const renderNegotiationTab = () => (
    <div className="space-y-6">
      <div className="bg-pink-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-pink-900 mb-2">
          L4 - Negotiation (80%)
        </h4>
        <p className="text-pink-800 text-sm">
          Handle commercial negotiations, proposal updates, and approval
          workflows.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Discussion with Customer
          </label>
          <textarea
            name="customer_discussion_notes"
            rows="4"
            value={formData.customer_discussion_notes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document customer discussions and negotiations..."
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="proposal_updated"
            name="proposal_updated"
            checked={formData.proposal_updated}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="proposal_updated"
            className="text-sm font-medium text-gray-700"
          >
            Proposal Updated
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="updated_proposal_submitted"
            name="updated_proposal_submitted"
            checked={formData.updated_proposal_submitted}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="updated_proposal_submitted"
            className="text-sm font-medium text-gray-700"
          >
            Updated Proposal Submitted
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Negotiation Rounds
          </label>
          <input
            type="number"
            name="negotiation_rounds"
            min="0"
            value={formData.negotiation_rounds}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="commercial_approval_required"
            name="commercial_approval_required"
            checked={formData.commercial_approval_required}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="commercial_approval_required"
            className="text-sm font-medium text-gray-700"
          >
            Commercial Approval Required
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Commercial Approval Status
          </label>
          <input
            type="text"
            name="commercial_approval_status"
            value={formData.commercial_approval_status}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Pending, Approved, Rejected"
          />
        </div>
      </div>
    </div>
  );

  const renderWonTab = () => (
    <div className="space-y-6">
      <div className="bg-green-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-green-900 mb-2">
          L5 - Won Stage (100%)
        </h4>
        <p className="text-green-800 text-sm">
          Handle post-win activities including kick-off meetings and delivery
          handoffs.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="kickoff_meeting_scheduled"
            name="kickoff_meeting_scheduled"
            checked={formData.kickoff_meeting_scheduled}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="kickoff_meeting_scheduled"
            className="text-sm font-medium text-gray-700"
          >
            Kick Off Meeting Scheduled
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Kick Off Meeting Date
          </label>
          <input
            type="datetime-local"
            name="kickoff_meeting_date"
            value={formData.kickoff_meeting_date}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="loi_received"
            name="loi_received"
            checked={formData.loi_received}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="loi_received"
            className="text-sm font-medium text-gray-700"
          >
            LOI / Order Received
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="order_verified"
            name="order_verified"
            checked={formData.order_verified}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="order_verified"
            className="text-sm font-medium text-gray-700"
          >
            Order Verification Completed
          </label>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="handoff_to_delivery"
            name="handoff_to_delivery"
            checked={formData.handoff_to_delivery}
            onChange={handleInputChange}
            className="mr-2"
          />
          <label
            htmlFor="handoff_to_delivery"
            className="text-sm font-medium text-gray-700"
          >
            Handoff to Delivery Team
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Delivery Team Assigned
          </label>
          <select
            name="delivery_team_assigned"
            value={formData.delivery_team_assigned}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select Team Member</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (currentTab) {
      case "qualification":
        return renderQualificationTab();
      case "demo":
        return renderDemoTab();
      case "proposal":
        return renderProposalTab();
      case "negotiation":
        return renderNegotiationTab();
      case "won":
        return renderWonTab();
      default:
        return renderBasicInfo();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {errors.submit}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setCurrentTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                currentTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">{renderActiveTab()}</div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {opportunity ? "Updating..." : "Creating..."}
            </div>
          ) : opportunity ? (
            "Update Opportunity"
          ) : (
            "Create Opportunity"
          )}
        </button>
      </div>
    </form>
  );
};

export default OpportunityForm;
