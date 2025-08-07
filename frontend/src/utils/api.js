// Enhanced API utility functions
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, finalOptions);
    const data = await response.json();
    
    // Handle unauthorized responses
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export const uploadFile = async (endpoint, formData) => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: formData,
    });
    
    const data = await response.json();
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('File upload failed:', error);
    throw error;
  }
};

// Enhanced opportunity-specific API functions
export const opportunityAPI = {
  // Get all opportunities
  getOpportunities: (params = {}) => {
    const queryParams = new URLSearchParams(params);
    return apiRequest(`/api/opportunities?${queryParams}`);
  },

  // Get single opportunity
  getOpportunity: (id) => apiRequest(`/api/opportunities/${id}`),

  // Create opportunity
  createOpportunity: (data) => apiRequest('/api/opportunities', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Update opportunity
  updateOpportunity: (id, data) => apiRequest(`/api/opportunities/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),

  // Update stage
  updateStage: (id, stageData) => apiRequest(`/api/opportunities/${id}/stage`, {
    method: 'PATCH',
    body: JSON.stringify(stageData)
  }),

  // Stage-specific task updates
  updateQualificationTasks: (id, data) => apiRequest(`/api/opportunities/${id}/qualification`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  updateDemoTasks: (id, data) => apiRequest(`/api/opportunities/${id}/demo`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  updateProposalTasks: (id, data) => apiRequest(`/api/opportunities/${id}/proposal`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  updateNegotiationTasks: (id, data) => apiRequest(`/api/opportunities/${id}/negotiation`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  updateWonTasks: (id, data) => apiRequest(`/api/opportunities/${id}/won-tasks`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  // Close opportunity
  closeOpportunity: (id, closeData) => apiRequest(`/api/opportunities/${id}/close`, {
    method: 'PATCH',
    body: JSON.stringify(closeData)
  }),

  // Delete opportunity
  deleteOpportunity: (id) => apiRequest(`/api/opportunities/${id}`, {
    method: 'DELETE'
  }),

  // Upload document
  uploadDocument: (id, file, documentType) => {
    const formData = new FormData();
    formData.append('file', file);
    return uploadFile(`/api/opportunities/${id}/upload?document_type=${documentType}`, formData);
  },

  // Get pipeline summary
  getPipelineSummary: (userId) => {
    const params = userId ? `?user_id=${userId}` : '';
    return apiRequest(`/api/opportunities/pipeline/summary${params}`);
  },

  // Get metrics
  getMetrics: (userId) => {
    const params = userId ? `?user_id=${userId}` : '';
    return apiRequest(`/api/opportunities/analytics/metrics${params}`);
  }
};

// Opportunity stage constants
export const OPPORTUNITY_STAGES = {
  L1_PROSPECT: 'L1_Prospect',
  L1_QUALIFICATION: 'L1_Qualification',
  L2_NEED_ANALYSIS: 'L2_Need_Analysis',
  L3_PROPOSAL: 'L3_Proposal',
  L4_NEGOTIATION: 'L4_Negotiation',
  L5_WON: 'L5_Won',
  L6_LOST: 'L6_Lost',
  L7_DROPPED: 'L7_Dropped'
};

export const OPPORTUNITY_STAGE_LABELS = {
  [OPPORTUNITY_STAGES.L1_PROSPECT]: 'L1 - Prospect',
  [OPPORTUNITY_STAGES.L1_QUALIFICATION]: 'L1 - Qualification (15%)',
  [OPPORTUNITY_STAGES.L2_NEED_ANALYSIS]: 'L2 - Need Analysis / Demo (40%)',
  [OPPORTUNITY_STAGES.L3_PROPOSAL]: 'L3 - Proposal / Bid Submission (60%)',
  [OPPORTUNITY_STAGES.L4_NEGOTIATION]: 'L4 - Negotiation (80%)',
  [OPPORTUNITY_STAGES.L5_WON]: 'L5 - Won (100%)',
  [OPPORTUNITY_STAGES.L6_LOST]: 'L6 - Lost',
  [OPPORTUNITY_STAGES.L7_DROPPED]: 'L7 - Dropped'
};

export const OPPORTUNITY_STATUSES = {
  OPEN: 'Open',
  WON: 'Won',
  LOST: 'Lost',
  DROPPED: 'Dropped'
};

export const QUALIFICATION_STATUSES = {
  QUALIFIED: 'Qualified',
  NOT_NOW: 'Not_Now',
  DISQUALIFIED: 'Disqualified'
};

export const GO_NO_GO_STATUSES = {
  GO: 'Go',
  NO_GO: 'No_Go',
  PENDING: 'Pending'
};

export const QUOTATION_STATUSES = {
  DRAFT: 'Draft',
  SUBMITTED: 'Submitted',
  APPROVED: 'Approved',
  REVISION_REQUIRED: 'Revision_Required'
};