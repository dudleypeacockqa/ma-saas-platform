/**
 * Redux Store Configuration
 * Centralized state management with RTK Query integration
 */

import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

// Import API slices
import { dealsApi } from '@/features/deals/api/dealsApi';
import { pipelineApi } from '@/features/deals/api/pipelineApi';
import { analyticsApi } from '@/features/deals/api/analyticsApi';
import { documentsApi } from '@/features/documents/api/documentsApi';

// Import feature slices
import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    // Add RTK Query reducers
    [dealsApi.reducerPath]: dealsApi.reducer,
    [pipelineApi.reducerPath]: pipelineApi.reducer,
    [analyticsApi.reducerPath]: analyticsApi.reducer,
    [documentsApi.reducerPath]: documentsApi.reducer,

    // Add feature reducers
    auth: authReducer,
    ui: uiReducer,
  },

  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['auth/setUser'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['auth.user'],
      },
    }).concat(
      // Add RTK Query middleware
      dealsApi.middleware,
      pipelineApi.middleware,
      analyticsApi.middleware,
      documentsApi.middleware,
    ),

  devTools: process.env.NODE_ENV !== 'production',
});

// Setup listeners for refetch behaviors
setupListeners(store.dispatch);

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;