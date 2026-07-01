import { apiClient } from './client';

export const leaderboardApi = {
  getTop: async (limit = 100) => {
    const response = await apiClient.get(`/api/v1/leaderboard?limit=${limit}`);
    return response.data;
  },
  getMe: async () => {
    const response = await apiClient.get('/api/v1/leaderboard/me');
    return response.data;
  },
};
