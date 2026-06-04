import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import api from '../services/api';
import { tokenStorage } from '../services/tokenStorage';
import type { User } from '../services/tokenStorage';

interface ToastState {
  show: boolean;
  message: string;
  type: 'success' | 'error';
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  toast: ToastState;
  showToast: (message: string, type: 'success' | 'error') => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', type: 'success' });

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ show: true, message, type });
  };

  useEffect(() => {
    if (toast.show) {
      const timer = setTimeout(() => {
        setToast((prev) => ({ ...prev, show: false }));
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toast.show]);

  // Load user and token from tokenStorage on initialization
  useEffect(() => {
    const storedToken = tokenStorage.getToken();
    const storedUser = tokenStorage.getUser();

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      const authData = response.data.data;
      const { access_token, refresh_token, user: userData } = authData;

      tokenStorage.setToken(access_token);
      tokenStorage.setRefreshToken(refresh_token);
      tokenStorage.setUser(userData);

      setToken(access_token);
      setUser(userData);
      showToast('Logged in successfully!', 'success');
    } catch (error: any) {
      const errData = error.response?.data?.error;
      const errorMsg = typeof errData === 'object' && errData !== null && errData.message 
        ? errData.message 
        : (error.response?.data?.message || 'Login failed. Please verify credentials.');
      showToast(errorMsg, 'error');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // Map username to full_name for backend compatibility
      const response = await api.post('/auth/register', { 
        email, 
        password, 
        full_name: username
      });
      const authData = response.data.data;
      const { access_token, refresh_token, user: userData } = authData;

      tokenStorage.setToken(access_token);
      tokenStorage.setRefreshToken(refresh_token);
      tokenStorage.setUser(userData);

      setToken(access_token);
      setUser(userData);
      showToast('Registration successful! Logged in automatically.', 'success');
    } catch (error: any) {
      const errData = error.response?.data?.error;
      const errorMsg = typeof errData === 'object' && errData !== null && errData.message 
        ? errData.message 
        : (error.response?.data?.message || 'Registration failed. Try a different email.');
      showToast(errorMsg, 'error');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch (error) {
        // Proceed even if network logout fails
      }
    }
    tokenStorage.clearAll();
    setToken(null);
    setUser(null);
    showToast('Logged out successfully.', 'success');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
        toast,
        showToast,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
