import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Check for existing token on app load
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
      setSessionId(savedToken);
      fetchUserInfo(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      // For development, since we have a working JWT, we'll create a mock user
      // In production, this would call /api/user/me or similar
      const mockUser = {
        name: 'Sales User',
        email: 'sales@company.com',
        role_name: 'Sales',
        id: 1
      };
      
      setUser(mockUser);
      setSessionId(token);
      console.log('✅ User authenticated successfully:', mockUser);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('authToken');
      setSessionId(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      console.log('🔍 Starting login process with:', credentials.username);
      
      // Convert username to email_or_username for backend compatibility
      const loginData = {
        email_or_username: credentials.username,
        password: credentials.password
      };
      
      console.log('📡 Sending login request to backend...');
      const response = await api.post('/api/login', loginData);
      console.log('📡 Login response received:', response.data);
      
      if (response.data.status && response.data.data.token) {
        const token = response.data.data.token;
        console.log('✅ Token received, saving to localStorage');
        localStorage.setItem('authToken', token);
        
        // For now, create a mock user object since we have the token
        const mockUser = {
          name: 'Sales User',
          email: credentials.username,
          role_name: 'Sales',
          id: 1
        };
        
        setUser(mockUser);
        setSessionId(token); // Use token as session ID for compatibility
        console.log('✅ Login successful, user set:', mockUser);
        return { success: true, user: mockUser };
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message || 'Login failed' 
      };
    } finally {
      setLoading(false);
      console.log('🔍 Login process completed, loading set to false');
    }
  };

  const logout = async () => {
    try {
      // For JWT-based auth, we just clear the local storage
      localStorage.removeItem('authToken');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
      setSessionId(null);
      setUser(null);
    }
  };

  const refreshSession = async () => {
    if (!sessionId) return false;
    
    try {
      const response = await api.post('/api/session/refresh', {}, {
        headers: { 'Authorization': sessionId }
      });
      return response.data.status;
    } catch (error) {
      console.error('Session refresh failed:', error);
      return false;
    }
  };

  // Auto-refresh session every 15 minutes
  useEffect(() => {
    if (sessionId) {
      const interval = setInterval(refreshSession, 15 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [sessionId]);

  const value = {
    user,
    sessionId,
    loading,
    login,
    logout,
    refreshSession,
    isAuthenticated: !!user && !!sessionId
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};