import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../api/auth';

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  initial_balance: number;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  updateTokens: (accessToken: string, refreshToken: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, refreshToken, user) => set({ token, refreshToken, user, isAuthenticated: true }),
      logout: () => set({ token: null, refreshToken: null, user: null, isAuthenticated: false }),
      updateTokens: (accessToken, refreshToken) => set({ token: accessToken, refreshToken }),
      login: async (email, password) => {
        const res = await authApi.login({ email, password });
        set({ token: res.tokens.access_token, refreshToken: res.tokens.refresh_token, user: res.user, isAuthenticated: true });
      },
      register: async (data) => {
        const res = await authApi.register(data);
        set({ token: res.tokens.access_token, refreshToken: res.tokens.refresh_token, user: res.user, isAuthenticated: true });
      }
    }),
    {
      name: 'auth-storage', // unique name
    }
  )
);
