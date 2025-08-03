// API utility functions
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';

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