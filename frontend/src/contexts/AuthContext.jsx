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
    // Check for existing session on app load
    const savedSessionId = localStorage.getItem('sessionId');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      fetchUserInfo(savedSessionId);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (sessionIdParam) => {
    try {
      const response = await api.get('/api/session/info', {
        headers: { 'x-session-id': sessionIdParam }
      });
      
      if (response.data.status) {
        setUser(response.data.data);
        setSessionId(sessionIdParam);
        localStorage.setItem('sessionId', sessionIdParam);
      } else {
        throw new Error('Session invalid');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('sessionId');
      setSessionId(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      const response = await api.post('/api/login', credentials);
      
      if (response.data.status && response.data.data.session_id) {
        const newSessionId = response.data.data.session_id;
        await fetchUserInfo(newSessionId);
        return { success: true, user: response.data.data.user };
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