import { apiClient } from './client';

export const watchlistApi = {
  getAll: async () => {
    const response = await apiClient.get('/api/v1/watchlist');
    return response.data;
  },
  create: async (name: string) => {
    const response = await apiClient.post('/api/v1/watchlist', { name });
    return response.data;
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/v1/watchlist/${id}`);
    return response.data;
  },
  addSymbol: async (id: string, symbol: string) => {
    const response = await apiClient.post(`/api/v1/watchlist/${id}/symbols`, { symbol });
    return response.data;
  },
  removeSymbol: async (id: string, symbol: string) => {
    const response = await apiClient.delete(`/api/v1/watchlist/${id}/symbols/${symbol}`);
    return response.data;
  },
};
