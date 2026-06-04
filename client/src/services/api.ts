import axios from 'axios';
import { tokenStorage } from './tokenStorage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically add JWT token to every secure request
api.interceptors.request.use(
  (config) => {
    const token = tokenStorage.getToken();
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Flag to track refreshing state and queue to hold concurrent requests
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: any) => void;
  reject: (reason: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor to handle session expiration or global errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Check for 401 errors that are not from the auth process itself
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const url = originalRequest.url || '';
      
      // If we are already calling login/register/refresh and get 401, clear storage and reject
      if (url.includes('/auth/login') || url.includes('/auth/register') || url.includes('/auth/refresh')) {
        tokenStorage.clearAll();
        return Promise.reject(error);
      }
      
      // Get the refresh token
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        tokenStorage.clearAll();
        if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
      
      // If another request is currently refreshing the token, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      return new Promise((resolve, reject) => {
        // Use standard axios to avoid interceptor loop, sending the refresh_token in body
        axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken }, { withCredentials: true })
          .then(({ data }) => {
            // Server responds with APIResponse[TokenResponse]
            const authData = data.data;
            const accessToken = authData.access_token;
            const newRefreshToken = authData.refresh_token;
            
            tokenStorage.setToken(accessToken);
            if (newRefreshToken) {
              tokenStorage.setRefreshToken(newRefreshToken);
            }
            
            // Retry the original request
            originalRequest.headers['Authorization'] = `Bearer ${accessToken}`;
            processQueue(null, accessToken);
            resolve(api(originalRequest));
          })
          .catch((err) => {
            processQueue(err, null);
            tokenStorage.clearAll();
            if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
              window.location.href = '/login';
            }
            reject(err);
          })
          .finally(() => {
            isRefreshing = false;
          });
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
