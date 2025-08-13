import axios from 'axios';
import { showGlobalError } from "./errorHandler"; // we'll create this


const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for enhanced error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = "Something went wrong.";

    if (error.response) {
      // Server responded with a status outside 2xx
      message = error.response.data?.message || `Error ${error.response.status}`;
    } else if (error.request) {
      // No response received
      message = "No response from server.";
    } else {
      // Request setup error
      message = error.message;
    }

    // Trigger global error popup
    showGlobalError(message);

    return Promise.reject(error);
  }
);


// Enhanced API methods
export const apiMethods = {
  // Dashboard APIs
  dashboard: {
    getOverview: () => api.get('/api/dashboard/overview'),
    getSales: () => api.get('/api/dashboard/sales'),
    getPresales: () => api.get('/api/dashboard/presales'),
    getProduct: () => api.get('/api/dashboard/product'),
    getMetrics: (type = 'default') => api.get(`/api/dashboard/metrics?dashboard_type=${type}`)
  },

  // Masters APIs
  masters: {
    // Products
    getProducts: (params = {}) => api.get('/api/masters/products', { params }),
    createProduct: (data) => api.post('/api/masters/products', data),
    getProduct: (id) => api.get(`/api/masters/products/${id}`),
    updateProduct: (id, data) => api.put(`/api/masters/products/${id}`, data),
    deleteProduct: (id) => api.delete(`/api/masters/products/${id}`),

    // Product Categories
    getProductCategories: (params = {}) => api.get('/api/masters/product-categories', { params }),
    createProductCategory: (data) => api.post('/api/masters/product-categories', data),
    updateProductCategory: (id, data) => api.put(`/api/masters/product-categories/${id}`, data),
    deleteProductCategory: (id) => api.delete(`/api/masters/product-categories/${id}`),

    // UOMs
    getUOMs: (params = {}) => api.get('/api/masters/uoms', { params }),
    createUOM: (data) => api.post('/api/masters/uoms', data),
    updateUOM: (id, data) => api.put(`/api/masters/uoms/${id}`, data),
    deleteUOM: (id) => api.delete(`/api/masters/uoms/${id}`),

    // Price Lists
    getPriceLists: (params = {}) => api.get('/api/masters/price-lists', { params }),
    createPriceList: (data) => api.post('/api/masters/price-lists', data),
    updatePriceList: (id, data) => api.put(`/api/masters/price-lists/${id}`, data),
    deletePriceList: (id) => api.delete(`/api/masters/price-lists/${id}`),
    approvePriceList: (id, data) => api.post(`/api/masters/price-lists/${id}/approve`, data),

    // Product Pricing
    getProductPricing: (params = {}) => api.get('/api/masters/product-pricing', { params }),
    createProductPricing: (data) => api.post('/api/masters/product-pricing', data),
    updateProductPricing: (id, data) => api.put(`/api/masters/product-pricing/${id}`, data),
    deleteProductPricing: (id) => api.delete(`/api/masters/product-pricing/${id}`),

    // Groups
    getGroups: (params = {}) => api.get('/api/masters/groups', { params }),
    createGroup: (data) => api.post('/api/masters/groups', data),
    updateGroup: (id, data) => api.put(`/api/masters/groups/${id}`, data),
    deleteGroup: (id) => api.delete(`/api/masters/groups/${id}`),

    // Product Groupings
    getProductGroupings: (params = {}) => api.get('/api/masters/product-groupings', { params }),
    createProductGrouping: (data) => api.post('/api/masters/product-groupings', data),
    updateProductGrouping: (id, data) => api.put(`/api/masters/product-groupings/${id}`, data),
    deleteProductGrouping: (id) => api.delete(`/api/masters/product-groupings/${id}`),

    // Taxes
    getTaxes: (params = {}) => api.get('/api/masters/taxes', { params }),
    createTax: (data) => api.post('/api/masters/taxes', data),
    updateTax: (id, data) => api.put(`/api/masters/taxes/${id}`, data),
    deleteTax: (id) => api.delete(`/api/masters/taxes/${id}`),

    // Users
    getUsers: (params = {}) => api.get('/api/masters/users', { params }),
    createUser: (data) => api.post('/api/masters/users', data),
    updateUser: (id, data) => api.put(`/api/masters/users/${id}`, data),
    deleteUser: (id) => api.delete(`/api/masters/users/${id}`),

    // Roles
    getRoles: (params = {}) => api.get('/api/masters/roles', { params }),
    createRole: (data) => api.post('/api/masters/roles', data),
    updateRole: (id, data) => api.put(`/api/masters/roles/${id}`, data),
    deleteRole: (id) => api.delete(`/api/masters/roles/${id}`),

    // Departments
    getDepartments: (params = {}) => api.get('/api/masters/departments', { params }),
    createDepartment: (data) => api.post('/api/masters/departments', data),
    updateDepartment: (id, data) => api.put(`/api/masters/departments/${id}`, data),
    deleteDepartment: (id) => api.delete(`/api/masters/departments/${id}`),

    // Designations
    getDesignations: (params = {}) => api.get('/api/masters/designations', { params }),
    createDesignation: (data) => api.post('/api/masters/designations', data),
    updateDesignation: (id, data) => api.put(`/api/masters/designations/${id}`, data),
    deleteDesignation: (id) => api.delete(`/api/masters/designations/${id}`),

    // Permissions
    getPermissions: (params = {}) => api.get('/api/masters/permissions', { params }),
    createPermission: (data) => api.post('/api/masters/permissions', data),
    updatePermission: (id, data) => api.put(`/api/masters/permissions/${id}`, data),
    deletePermission: (id) => api.delete(`/api/masters/permissions/${id}`),

    // Other masters...
    getStates: (params = {}) => api.get('/api/masters/states', { params }),
    getCities: (params = {}) => api.get('/api/masters/cities', { params }),
    getIndustryCategories: (params = {}) => api.get('/api/masters/industry-categories', { params }),
    getDiscounts: (params = {}) => api.get('/api/masters/discounts', { params }),
    getProductCalculations: (params = {}) => api.get('/api/masters/product-calculations', { params })
  },

  // Leads APIs
  leads: {
    getLeads: (params = {}) => api.get('/api/leads', { params }),
    createLead: (data) => api.post('/api/leads', data),
    getLead: (id) => api.get(`/api/leads/${id}`),
    updateLead: (id, data) => api.put(`/api/leads/${id}`, data),
    updateLeadStatus: (id, status) => api.put(`/api/leads/${id}`, { status }),
    approveLead: (id, data) => api.post(`/api/leads/${id}/review`, data),
    convertToOpportunity: (id, data = {}) => api.post(`/api/leads/${id}/convert-to-opportunity`, data)
  },

  // Opportunities APIs
  opportunities: {
    getOpportunities: (params = {}) => api.get('/api/opportunities', { params }),
    createOpportunity: (data) => api.post('/api/opportunities', data),
    getOpportunity: (id) => api.get(`/api/opportunities/${id}`),
    updateOpportunity: (id, data) => api.put(`/api/opportunities/${id}`, data)
  },

  // Quotations APIs
  quotations: {
    getQuotations: (params = {}) => api.get('/api/quotations', { params }),
    createQuotation: (data) => api.post('/api/quotations', data),
    getQuotation: (id) => api.get(`/api/quotations/${id}`),
    updateQuotation: (id, data) => api.put(`/api/quotations/${id}`, data)
  },

  // Companies APIs
  companies: {
    getCompanies: (params = {}) => api.get('/api/companies', { params }),
    createCompany: (data) => api.post('/api/companies', data),
    getCompany: (id) => api.get(`/api/companies/${id}`),
    updateCompany: (id, data) => api.put(`/api/companies/${id}`, data)
  },

  // Contacts APIs
  contacts: {
    getContacts: (params = {}) => api.get('/api/contacts', { params }),
    createContact: (data) => api.post('/api/contacts', data),
    getContact: (id) => api.get(`/api/contacts/${id}`),
    updateContact: (id, data) => api.put(`/api/contacts/${id}`, data)
  },

  // File upload APIs
  files: {
    upload: (file, folder = 'uploads') => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', folder);
      return api.post('/api/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    getUrl: (filePath, expiresInMinutes = 60) =>
      api.get(`/api/files/${filePath}?expires_in_minutes=${expiresInMinutes}`),
    delete: (filePath) => api.delete(`/api/files/${filePath}`)
  },

  // Session APIs
  session: {
    getInfo: () => api.get('/api/session/info'),
    refresh: () => api.post('/api/session/refresh')
  },

  // Auth APIs
  auth: {
    login: (credentials) => api.post('/api/login', credentials),
    logout: () => api.post('/api/logout')
  }
};




//  opportunity-specific API functions
export const opportunityAPI = {
  // Get all opportunities
  getOpportunities: (params = {}) => {
    const queryParams = new URLSearchParams(params);
    return api.get(`/api/opportunities?${queryParams}`);
  },

  // Get single opportunity
  getOpportunity: (id) => api.get(`/api/opportunities/${id}`),

  // Create opportunity
  createOpportunity: (data) => api.post('/api/opportunities', JSON.stringify(data)),

  // Update opportunity
  updateOpportunity: (id, data) => api.put(`/api/opportunities/${id}`, JSON.stringify(data)),

  // Update stage
  updateStage: (id, stageData) => api.patch(`/api/opportunities/${id}/stage`, JSON.stringify(stageData)
  ),

  // Stage-specific task updates
  updateQualificationTasks: (id, data) => api.patch(`/api/opportunities/${id}/qualification`, JSON.stringify(data)),

  updateDemoTasks: (id, data) => api.patch(`/api/opportunities/${id}/demo`, JSON.stringify(data)),

  updateProposalTasks: (id, data) => api.patch(`/api/opportunities/${id}/proposal`, JSON.stringify(data)),

  updateNegotiationTasks: (id, data) => api.patch(`/api/opportunities/${id}/negotiation`, JSON.stringify(data)),

  updateWonTasks: (id, data) => api.patch(`/api/opportunities/${id}/won-tasks`, JSON.stringify(data)),

  // Close opportunity
  closeOpportunity: (id, closeData) => api.patch(`/api/opportunities/${id}/close`, JSON.stringify(closeData)),

  // Delete opportunity
  deleteOpportunity: (id) => api.delete(`/api/opportunities/${id}`),

  // Upload document
  uploadDocument: (id, file, documentType) => {
    const formData = new FormData();
    formData.append('file', file);
    return uploadFile(`/api/opportunities/${id}/upload?document_type=${documentType}`, formData);
  },

  // Get pipeline summary
  getPipelineSummary: (userId) => {
    const params = userId ? `?user_id=${userId}` : '';
    return api.get(`/api/opportunities/pipeline/summary${params}`);
  },

  // Get metrics
  getMetrics: (userId) => {
    const params = userId ? `?user_id=${userId}` : '';
    return api.get(`/api/opportunities/analytics/metrics${params}`);
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

export default api;

// Legacy apiRequest function for backward compatibility
export const apiRequest = async (url, options = {}) => {
  try {
    const config = {
      ...options,
      url,
      method: options.method || 'GET',
    };
    
    // Handle FormData
    if (options.body instanceof FormData) {
      config.data = options.body;
      if (options.headers) {
        config.headers = { ...config.headers, ...options.headers };
      }
    } else if (options.body) {
      config.data = options.body;
    }
    
    const response = await api.request(config);
    return response.data;
  } catch (error) {
    // Let the interceptor handle the error display
    throw error;
  }
};