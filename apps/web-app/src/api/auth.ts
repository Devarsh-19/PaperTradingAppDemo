import { apiClient } from './client';

export const authApi = {
  login: async (credentials: any) => {
    const response = await apiClient.post('/api/v1/auth/login', credentials);
    return response.data;
  },
  register: async (data: any) => {
    const response = await apiClient.post('/api/v1/auth/register', data);
    return response.data;
  },
  getMe: async () => {
    const response = await apiClient.get('/api/v1/auth/me');
    return response.data;
  },
  refresh: async (refreshToken: string) => {
    // We use axios directly here to avoid interceptor loops if using apiClient
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const response = await import('axios').then(axios => 
      axios.default.post(`${API_URL}/api/v1/auth/refresh`, { refresh_token: refreshToken })
    );
    return response.data;
  },
};
