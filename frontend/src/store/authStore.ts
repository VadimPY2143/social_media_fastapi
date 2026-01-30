import { create } from 'zustand';
import { User, AuthState } from '../types';
import { apiClient } from '../api/client';

interface AuthStore extends AuthState {
  register: (username: string, email: string, password: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.register(username, email, password);
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await apiClient.login(email, password);
      localStorage.setItem('access_token', tokenData.access_token);
      apiClient.setAuthHeader(tokenData.access_token);
      set({
        token: tokenData.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    apiClient.clearAuth();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  setUser: (user: User | null) => {
    set({ user });
  },

  setToken: (token: string | null) => {
    if (token) {
      localStorage.setItem('access_token', token);
      apiClient.setAuthHeader(token);
    } else {
      localStorage.removeItem('access_token');
      apiClient.clearAuth();
    }
    set({
      token,
      isAuthenticated: !!token,
    });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const user = await apiClient.getCurrentUser();
      set({ user, isLoading: false });
    } catch (error: any) {
      set({ isLoading: false });
      if (error.response?.status === 401) {
        set({ user: null, token: null, isAuthenticated: false });
      }
      throw error;
    }
  },
}));
