/**
 * Authentication Slice
 * Manages authentication state and user information
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  organizationId: string;
  organizationName?: string;
  role: 'admin' | 'member' | 'viewer';
  imageUrl?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  organizationId: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  organizationId: null,
  loading: true,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.organizationId = action.payload.user.organizationId;
      state.loading = false;
      state.error = null;
    },

    clearAuth: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.organizationId = null;
      state.loading = false;
      state.error = null;
    },

    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },

    updateOrganization: (state, action: PayloadAction<{ id: string; name: string }>) => {
      state.organizationId = action.payload.id;
      if (state.user) {
        state.user.organizationId = action.payload.id;
        state.user.organizationName = action.payload.name;
      }
    },
  },
});

export const { setUser, clearAuth, setLoading, setError, updateOrganization } = authSlice.actions;

export default authSlice.reducer;