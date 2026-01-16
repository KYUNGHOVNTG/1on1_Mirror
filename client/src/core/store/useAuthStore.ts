/**
 * Auth Store (Google OAuth + JWT)
 *
 * 인증 상태 관리 및 토큰 저장
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: number;
  email: string;
  name: string;
  profile_image?: string;
  role: string;
  company_id: number;
  department_id?: number;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  // Actions
  login: (user: User, tokens: Tokens) => void;
  logout: () => void;
  updateTokens: (tokens: Tokens) => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (user: User, tokens: Tokens) => {
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      updateTokens: (tokens: Tokens) => {
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage', // localStorage key
    }
  )
);
