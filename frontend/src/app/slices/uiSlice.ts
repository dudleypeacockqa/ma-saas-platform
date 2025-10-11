/**
 * UI Slice
 * Manages UI state like sidebar, theme, notifications
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface UiState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  isLoading: boolean;
  breadcrumbs: Array<{ label: string; path?: string }>;
}

const initialState: UiState = {
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  isLoading: false,
  breadcrumbs: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },

    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },

    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },

    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
      };
      state.notifications.push(notification);
    },

    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },

    clearNotifications: (state) => {
      state.notifications = [];
    },

    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    setBreadcrumbs: (state, action: PayloadAction<Array<{ label: string; path?: string }>>) => {
      state.breadcrumbs = action.payload;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  addNotification,
  removeNotification,
  clearNotifications,
  setLoading,
  setBreadcrumbs,
} = uiSlice.actions;

export default uiSlice.reducer;