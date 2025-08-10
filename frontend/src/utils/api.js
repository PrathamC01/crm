import axios from 'axios';

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
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
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

    // UOMs
    getUOMs: (params = {}) => api.get('/api/masters/uoms', { params }),
    createUOM: (data) => api.post('/api/masters/uoms', data),

    // Price Lists
    getPriceLists: (params = {}) => api.get('/api/masters/pricelists', { params }),
    createPriceList: (data) => api.post('/api/masters/pricelists', data),
    approvePriceList: (id, data) => api.post(`/api/masters/pricelists/${id}/approve`, data),

    // Product Pricing
    getProductPricing: (productId, params = {}) => api.get(`/api/masters/products/${productId}/pricing`, { params }),
    createProductPricing: (productId, data) => api.post(`/api/masters/products/${productId}/pricing`, data),

    // Users
    getUsers: (params = {}) => api.get('/api/masters/users', { params }),
    createUser: (data) => api.post('/api/masters/users', data),

    // Lookups
    getDepartments: () => api.get('/api/masters/departments'),
    getRoles: () => api.get('/api/masters/roles')
  },

  // Leads APIs
  leads: {
    getLeads: (params = {}) => api.get('/api/leads', { params }),
    createLead: (data) => api.post('/api/leads', data),
    getLead: (id) => api.get(`/api/leads/${id}`),
    updateLead: (id, data) => api.put(`/api/leads/${id}`, data),
    updateLeadStatus: (id, status) => api.patch(`/api/leads/${id}/status`, { status })
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

export default api;