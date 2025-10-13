import { configureStore } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { persistReducer, persistStore } from 'redux-persist';
import { combineReducers } from 'redux';

import authReducer from './slices/authSlice';
import dealsReducer from './slices/dealsSlice';
import documentsReducer from './slices/documentsSlice';
import annotationsReducer from './slices/annotationsSlice';
import notificationsReducer from './slices/notificationsSlice';
import offlineReducer from './slices/offlineSlice';
import syncReducer from './slices/syncSlice';

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'deals', 'documents', 'annotations', 'offline']
};

const rootReducer = combineReducers({
  auth: authReducer,
  deals: dealsReducer,
  documents: documentsReducer,
  annotations: annotationsReducer,
  notifications: notificationsReducer,
  offline: offlineReducer,
  sync: syncReducer
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE']
      }
    })
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;
