import { apiClient } from './client';

export const marketApi = {
  getQuote: async (symbol: string) => {
    const response = await apiClient.get(`/api/v1/market/quote/${symbol}`);
    return response.data;
  },
  getBatchQuotes: async (symbols: string[]) => {
    const response = await apiClient.post('/api/v1/market/quotes', { symbols });
    return response.data;
  },
  getHistory: async (symbol: string, period = '1mo', interval = '1d') => {
    const response = await apiClient.get(`/api/v1/market/history/${symbol}?period=${period}&interval=${interval}`);
    return response.data;
  },
  searchSymbols: async (query: string) => {
    const response = await apiClient.get(`/api/v1/market/search?q=${query}`);
    return response.data;
  },
  getIndicators: async (symbol: string) => {
    // Note: uses intelligence service route which is proxied
    const response = await apiClient.get(`/intelligence/v1/indicators/${symbol}`);
    return response.data;
  }
};
