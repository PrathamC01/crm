import React, { useState } from 'react';
import { opportunityAPI, OPPORTUNITY_STAGE_LABELS } from '../../../utils/api';

const OpportunityView = ({ opportunity, onEdit, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!opportunity) {
    return <div>Loading...</div>;
  }

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleString();
  };

  const getStageColor = (stage) => {
    const colors = {
      'L1_Prospect': 'bg-gray-100 text-gray-800',
      'L1_Qualification': 'bg-blue-100 text-blue-800',
      'L2_Need_Analysis': 'bg-indigo-100 text-indigo-800',
      'L3_Proposal': 'bg-purple-100 text-purple-800',
      'L4_Negotiation': 'bg-pink-100 text-pink-800',
      'L5_Won': 'bg-green-100 text-green-800',
      'L6_Lost': 'bg-red-100 text-red-800',
      'L7_Dropped': 'bg-gray-100 text-gray-800'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📋' },
    { id: 'qualification', name: 'L1 - Qualification', icon: '✅' },
    { id: 'demo', name: 'L2 - Demo', icon: '🎯' },
    { id: 'proposal', name: 'L3 - Proposal', icon: '📄' },
    { id: 'negotiation', name: 'L4 - Negotiation', icon: '🤝' },
    { id: 'won', name: 'L5 - Won Tasks', icon: '🏆' },
    { id: 'timeline', name: 'Timeline', icon: '📅' }
  ];

  const renderOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Basic Information */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
        <dl className="space-y-3">
          <div>
            <dt className="text-sm font-medium text-gray-500">POT ID</dt>
            <dd className="text-sm text-gray-900 font-mono">{opportunity.pot_id}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Opportunity Name</dt>
            <dd className="text-sm text-gray-900">{opportunity.name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Company</dt>
            <dd className="text-sm text-gray-900">{opportunity.company_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Decision Maker</dt>
            <dd className="text-sm text-gray-900">
              {opportunity.contact_name}
              {opportunity.contact_email && (
                <span className="text-gray-500"> ({opportunity.contact_email})</span>
              )}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Created By</dt>
            <dd className="text-sm text-gray-900">{opportunity.created_by_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Created On</dt>
            <dd className="text-sm text-gray-900">{formatDate(opportunity.created_on)}</dd>
          </div>
        </dl>
      </div>

      {/* Stage & Progress */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Stage & Progress</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Current Stage</span>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(opportunity.stage)}`}>
                {opportunity.stage_display_name}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div 
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${opportunity.stage_percentage}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {opportunity.stage_percentage}% Complete
            </div>
          </div>

          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className={`text-sm inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                opportunity.status === 'Open' ? 'bg-green-100 text-green-800' :
                opportunity.status === 'Won' ? 'bg-green-200 text-green-900' :
                opportunity.status === 'Lost' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {opportunity.status}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Probability</dt>
              <dd className="text-sm text-gray-900">{opportunity.probability}%</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Scoring</dt>
              <dd className="text-sm text-gray-900">{opportunity.scoring}/100</dd>
            </div>
            {opportunity.close_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Target Close Date</dt>
                <dd className="text-sm text-gray-900">{new Date(opportunity.close_date).toLocaleDateString()}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Financial Information */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Information</h3>
        <dl className="space-y-3">
          <div>
            <dt className="text-sm font-medium text-gray-500">Amount</dt>
            <dd className="text-sm text-gray-900">{formatCurrency(opportunity.amount)}</dd>
          </div>
          {opportunity.costing && (
            <div>
              <dt className="text-sm font-medium text-gray-500">Costing</dt>
              <dd className="text-sm text-gray-900">{formatCurrency(opportunity.costing)}</dd>
            </div>
          )}
          {opportunity.amount && opportunity.costing && (
            <div>
              <dt className="text-sm font-medium text-gray-500">Margin</dt>
              <dd className="text-sm text-gray-900">
                {formatCurrency(opportunity.amount - opportunity.costing)} 
                ({((((opportunity.amount - opportunity.costing) / opportunity.amount) * 100)).toFixed(2)}%)
              </dd>
            </div>
          )}
          {opportunity.justification && (
            <div>
              <dt className="text-sm font-medium text-gray-500">Justification</dt>
              <dd className="text-sm text-gray-900">{opportunity.justification}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* Notes */}
      {opportunity.notes && (
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Notes</h3>
          <div className="text-sm text-gray-900 whitespace-pre-wrap">{opportunity.notes}</div>
        </div>
      )}
    </div>
  );

  const renderQualificationTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-blue-900 mb-2">L1 - Qualification Stage (15%)</h4>
        <p className="text-blue-800 text-sm">Validate if the lead meets basic qualification criteria and capture BANT/CHAMP data.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Qualification Status</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Go/No Go Status</dt>
              <dd className={`text-sm inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                opportunity.go_no_go_status === 'Go' ? 'bg-green-100 text-green-800' :
                opportunity.go_no_go_status === 'No_Go' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {opportunity.go_no_go_status?.replace('_', ' ') || 'Pending'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Qualification Status</dt>
              <dd className={`text-sm inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                opportunity.qualification_status === 'Qualified' ? 'bg-green-100 text-green-800' :
                opportunity.qualification_status === 'Disqualified' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {opportunity.qualification_status?.replace('_', ' ') || 'Pending'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Completed By</dt>
              <dd className="text-sm text-gray-900">{opportunity.qualification_completer_name || 'Not assigned'}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Requirement Gathering</h3>
          {opportunity.requirement_gathering_notes ? (
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {opportunity.requirement_gathering_notes}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No requirement notes captured yet</div>
          )}
        </div>

        {opportunity.qualification_scorecard && (
          <div className="bg-white p-6 rounded-lg border md:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Qualification Scorecard</h3>
            <div className="text-sm text-gray-900">
              <pre className="whitespace-pre-wrap">{JSON.stringify(opportunity.qualification_scorecard, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderDemoTab = () => (
    <div className="space-y-6">
      <div className="bg-indigo-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-indigo-900 mb-2">L2 - Need Analysis / Demo (40%)</h4>
        <p className="text-indigo-800 text-sm">Conduct product demos and qualification meetings to understand customer needs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Demo Activities</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Demo Completed</dt>
              <dd className={`text-sm ${opportunity.demo_completed ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.demo_completed ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            {opportunity.demo_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Demo Date</dt>
                <dd className="text-sm text-gray-900">{formatDate(opportunity.demo_date)}</dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">Qualification Meeting</dt>
              <dd className={`text-sm ${opportunity.qualification_meeting_completed ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.qualification_meeting_completed ? '✓ Completed' : '✗ Pending'}
              </dd>
            </div>
            {opportunity.qualification_meeting_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Meeting Date</dt>
                <dd className="text-sm text-gray-900">{formatDate(opportunity.qualification_meeting_date)}</dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Demo Summary</h3>
          {opportunity.demo_summary ? (
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {opportunity.demo_summary}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No demo summary available</div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg border md:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Meeting Notes</h3>
          {opportunity.qualification_meeting_notes ? (
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {opportunity.qualification_meeting_notes}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No meeting notes available</div>
          )}
        </div>

        {opportunity.presentation_materials && opportunity.presentation_materials.length > 0 && (
          <div className="bg-white p-6 rounded-lg border md:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Presentation Materials</h3>
            <div className="space-y-2">
              {opportunity.presentation_materials.map((material, index) => (
                <div key={index} className="flex items-center p-2 border rounded">
                  <div className="text-sm text-gray-900">{material.name || `Material ${index + 1}`}</div>
                  {material.url && (
                    <a
                      href={material.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderProposalTab = () => (
    <div className="space-y-6">
      <div className="bg-purple-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-purple-900 mb-2">L3 - Proposal / Bid Submission (60%)</h4>
        <p className="text-purple-800 text-sm">Prepare and submit quotations, proposals, and conduct POCs with approval workflows.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quotation Status</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Quotation Created</dt>
              <dd className={`text-sm ${opportunity.quotation_created ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.quotation_created ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className={`text-sm inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                opportunity.quotation_status === 'Approved' ? 'bg-green-100 text-green-800' :
                opportunity.quotation_status === 'Submitted' ? 'bg-blue-100 text-blue-800' :
                opportunity.quotation_status === 'Revision_Required' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {opportunity.quotation_status?.replace('_', ' ') || 'Draft'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Version</dt>
              <dd className="text-sm text-gray-900">{opportunity.quotation_version || 1}</dd>
            </div>
            {opportunity.quotation_file_path && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Quotation File</dt>
                <dd className="text-sm">
                  <a
                    href={opportunity.quotation_file_path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View Document
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Proposal Status</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Proposal Prepared</dt>
              <dd className={`text-sm ${opportunity.proposal_prepared ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.proposal_prepared ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Proposal Submitted</dt>
              <dd className={`text-sm ${opportunity.proposal_submitted ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.proposal_submitted ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            {opportunity.proposal_submission_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Submission Date</dt>
                <dd className="text-sm text-gray-900">{formatDate(opportunity.proposal_submission_date)}</dd>
              </div>
            )}
            {opportunity.proposal_file_path && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Proposal File</dt>
                <dd className="text-sm">
                  <a
                    href={opportunity.proposal_file_path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View Document
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">POC Status</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">POC Completed</dt>
              <dd className={`text-sm ${opportunity.poc_completed ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.poc_completed ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
          </dl>
          {opportunity.poc_notes && (
            <div className="mt-4">
              <dt className="text-sm font-medium text-gray-500 mb-2">POC Notes</dt>
              <dd className="text-sm text-gray-900 whitespace-pre-wrap">{opportunity.poc_notes}</dd>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Solutions Team Approval</h3>
          {opportunity.solutions_team_approval_notes ? (
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {opportunity.solutions_team_approval_notes}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No approval notes available</div>
          )}
        </div>
      </div>
    </div>
  );

  const renderNegotiationTab = () => (
    <div className="space-y-6">
      <div className="bg-pink-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-pink-900 mb-2">L4 - Negotiation (80%)</h4>
        <p className="text-pink-800 text-sm">Handle commercial negotiations, proposal updates, and approval workflows.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Negotiation Status</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Negotiation Rounds</dt>
              <dd className="text-sm text-gray-900">{opportunity.negotiation_rounds || 0}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Proposal Updated</dt>
              <dd className={`text-sm ${opportunity.proposal_updated ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.proposal_updated ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Updated Proposal Submitted</dt>
              <dd className={`text-sm ${opportunity.updated_proposal_submitted ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.updated_proposal_submitted ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            {opportunity.updated_proposal_file_path && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Updated Proposal</dt>
                <dd className="text-sm">
                  <a
                    href={opportunity.updated_proposal_file_path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View Document
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Commercial Approval</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Approval Required</dt>
              <dd className={`text-sm ${opportunity.commercial_approval_required ? 'text-yellow-600' : 'text-gray-600'}`}>
                {opportunity.commercial_approval_required ? '⚠ Yes' : '○ No'}
              </dd>
            </div>
            {opportunity.commercial_approval_required && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Approval Status</dt>
                <dd className={`text-sm inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  opportunity.commercial_approval_status === 'Approved' ? 'bg-green-100 text-green-800' :
                  opportunity.commercial_approval_status === 'Rejected' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {opportunity.commercial_approval_status || 'Pending'}
                </dd>
              </div>
            )}
            {opportunity.negotiated_quotation_file_path && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Negotiated Quotation</dt>
                <dd className="text-sm">
                  <a
                    href={opportunity.negotiated_quotation_file_path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View Document
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border md:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Customer Discussion Notes</h3>
          {opportunity.customer_discussion_notes ? (
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {opportunity.customer_discussion_notes}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No discussion notes available</div>
          )}
        </div>
      </div>
    </div>
  );

  const renderWonTab = () => (
    <div className="space-y-6">
      <div className="bg-green-50 p-4 rounded-lg mb-4">
        <h4 className="font-medium text-green-900 mb-2">L5 - Won Stage (100%)</h4>
        <p className="text-green-800 text-sm">Handle post-win activities including kick-off meetings and delivery handoffs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Kick-off Activities</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Meeting Scheduled</dt>
              <dd className={`text-sm ${opportunity.kickoff_meeting_scheduled ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.kickoff_meeting_scheduled ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            {opportunity.kickoff_meeting_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Meeting Date</dt>
                <dd className="text-sm text-gray-900">{formatDate(opportunity.kickoff_meeting_date)}</dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Order Processing</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">LOI Received</dt>
              <dd className={`text-sm ${opportunity.loi_received ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.loi_received ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Order Verified</dt>
              <dd className={`text-sm ${opportunity.order_verified ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.order_verified ? '✓ Yes' : '✗ No'}
              </dd>
            </div>
            {opportunity.loi_file_path && (
              <div>
                <dt className="text-sm font-medium text-gray-500">LOI Document</dt>
                <dd className="text-sm">
                  <a
                    href={opportunity.loi_file_path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View Document
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg border md:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Delivery Handoff</h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Handoff to Delivery</dt>
              <dd className={`text-sm ${opportunity.handoff_to_delivery ? 'text-green-600' : 'text-red-600'}`}>
                {opportunity.handoff_to_delivery ? '✓ Completed' : '✗ Pending'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Delivery Team Assigned</dt>
              <dd className="text-sm text-gray-900">
                {opportunity.delivery_team_member_name || 'Not assigned'}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );

  const renderTimelineTab = () => (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Timeline</h3>
        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 pl-4">
            <div className="text-sm font-medium text-gray-900">Opportunity Created</div>
            <div className="text-sm text-gray-500">{formatDate(opportunity.created_on)}</div>
            <div className="text-xs text-gray-400">by {opportunity.created_by_name}</div>
          </div>
          
          {opportunity.updated_on && opportunity.updated_on !== opportunity.created_on && (
            <div className="border-l-4 border-yellow-500 pl-4">
              <div className="text-sm font-medium text-gray-900">Last Updated</div>
              <div className="text-sm text-gray-500">{formatDate(opportunity.updated_on)}</div>
            </div>
          )}

          {opportunity.demo_date && (
            <div className="border-l-4 border-indigo-500 pl-4">
              <div className="text-sm font-medium text-gray-900">Demo Conducted</div>
              <div className="text-sm text-gray-500">{formatDate(opportunity.demo_date)}</div>
            </div>
          )}

          {opportunity.proposal_submission_date && (
            <div className="border-l-4 border-purple-500 pl-4">
              <div className="text-sm font-medium text-gray-900">Proposal Submitted</div>
              <div className="text-sm text-gray-500">{formatDate(opportunity.proposal_submission_date)}</div>
            </div>
          )}

          {opportunity.kickoff_meeting_date && (
            <div className="border-l-4 border-green-500 pl-4">
              <div className="text-sm font-medium text-gray-900">Kick-off Meeting</div>
              <div className="text-sm text-gray-500">{formatDate(opportunity.kickoff_meeting_date)}</div>
            </div>
          )}

          {opportunity.status !== 'Open' && opportunity.close_date && (
            <div className={`border-l-4 pl-4 ${
              opportunity.status === 'Won' ? 'border-green-500' : 'border-red-500'
            }`}>
              <div className="text-sm font-medium text-gray-900">Opportunity {opportunity.status}</div>
              <div className="text-sm text-gray-500">{new Date(opportunity.close_date).toLocaleDateString()}</div>
              {opportunity.lost_reason && (
                <div className="text-xs text-gray-400">Reason: {opportunity.lost_reason}</div>
              )}
              {opportunity.competitor_name && (
                <div className="text-xs text-gray-400">Competitor: {opportunity.competitor_name}</div>
              )}
              {opportunity.drop_reason && (
                <div className="text-xs text-gray-400">Reason: {opportunity.drop_reason}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'qualification': return renderQualificationTab();
      case 'demo': return renderDemoTab();
      case 'proposal': return renderProposalTab();
      case 'negotiation': return renderNegotiationTab();
      case 'won': return renderWonTab();
      case 'timeline': return renderTimelineTab();
      default: return renderOverview();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-gray-900">{opportunity.name}</h2>
            <span className="text-lg font-mono text-blue-600">{opportunity.pot_id}</span>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStageColor(opportunity.stage)}`}>
              {opportunity.stage_display_name}
            </span>
          </div>
          <p className="text-gray-600 mt-1">
            {opportunity.company_name} | {opportunity.contact_name} | {formatCurrency(opportunity.amount)}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => onEdit(opportunity)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Edit Opportunity
          </button>
          <button
            onClick={onClose}
            className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${opportunity.stage_percentage}%` }}
          ></div>
        </div>
        <div className="text-sm text-gray-600">
          {opportunity.stage_percentage}% Complete | Probability: {opportunity.probability}% | Score: {opportunity.scoring}/100
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {renderActiveTab()}
      </div>
    </div>
  );
};

export default OpportunityView;