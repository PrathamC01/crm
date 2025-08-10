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
      // For JWT-based auth, we'll skip the session info call for now
      // and use the token directly
      const mockUser = {
        name: 'Sales User',
        email: 'sales@company.com',
        role_name: 'Sales'
      };
      
      setUser(mockUser);
      setSessionId(token);
      localStorage.setItem('authToken', token);
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
      // Convert username to email_or_username for backend compatibility
      const loginData = {
        email_or_username: credentials.username,
        password: credentials.password
      };
      
      const response = await api.post('/api/login', loginData);
      
      if (response.data.status && response.data.data.token) {
        const token = response.data.data.token;
        localStorage.setItem('authToken', token);
        
        // For now, create a mock user object since we have the token
        const mockUser = {
          name: 'Sales User',
          email: credentials.username,
          role_name: 'Sales'
        };
        
        setUser(mockUser);
        setSessionId(token); // Use token as session ID for compatibility
        return { success: true, user: mockUser };
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message || 'Login failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (sessionId) {
        await api.post('/api/logout', {}, {
          headers: { 'x-session-id': sessionId }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('sessionId');
      setSessionId(null);
      setUser(null);
    }
  };

  const refreshSession = async () => {
    if (!sessionId) return false;
    
    try {
      const response = await api.post('/api/session/refresh', {}, {
        headers: { 'x-session-id': sessionId }
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