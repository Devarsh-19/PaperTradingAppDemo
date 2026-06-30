import { apiClient } from './client';

export const portfolioApi = {
  getSummary: async () => {
    const response = await apiClient.get('/api/v1/portfolio/summary');
    return response.data;
  },
  getPositions: async () => {
    const response = await apiClient.get('/api/v1/portfolio/positions');
    return response.data;
  },
  getTrades: async (skip = 0, limit = 50) => {
    const response = await apiClient.get(`/api/v1/portfolio/trades?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  reset: async () => {
    const response = await apiClient.post('/api/v1/portfolio/reset');
    return response.data;
  },
};
