import { apiClient } from './client';

export const ordersApi = {
  create: async (orderData: any) => {
    const response = await apiClient.post('/api/v1/orders', orderData);
    return response.data;
  },
  getAll: async (skip = 0, limit = 50, status?: string) => {
    const url = `/api/v1/orders?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`;
    const response = await apiClient.get(url);
    return response.data;
  },
  getOne: async (orderId: string) => {
    const response = await apiClient.get(`/api/v1/orders/${orderId}`);
    return response.data;
  },
  cancel: async (orderId: string) => {
    const response = await apiClient.post(`/api/v1/orders/${orderId}/cancel`);
    return response.data;
  },
};
