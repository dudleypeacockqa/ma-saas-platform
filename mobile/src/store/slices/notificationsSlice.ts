import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';

import { registerDeviceToken } from '@services/auth';

export type NotificationItem = {
  id: string;
  title: string;
  body: string;
  data: Record<string, unknown>;
  receivedAt: number;
  deliveredSilently?: boolean;
  read?: boolean;
};

type NotificationsState = {
  pushToken?: string;
  items: NotificationItem[];
};

const initialState: NotificationsState = {
  items: []
};

export const registerDeviceTokenThunk = createAsyncThunk(
  'notifications/registerDeviceToken',
  async (token: string, { rejectWithValue }) => {
    try {
      await registerDeviceToken(token);
      return token;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    enqueueNotification(state, action: PayloadAction<NotificationItem>) {
      state.items = [action.payload, ...state.items].slice(0, 50);
    },
    markNotificationRead(state, action: PayloadAction<string>) {
      state.items = state.items.map((item) =>
        item.id === action.payload ? { ...item, read: true } : item
      );
    },
    clearNotifications(state) {
      state.items = [];
    }
  },
  extraReducers: (builder) => {
    builder.addCase(registerDeviceTokenThunk.fulfilled, (state, action) => {
      state.pushToken = action.payload;
    });
  }
});

export const { enqueueNotification, markNotificationRead, clearNotifications } =
  notificationsSlice.actions;

export default notificationsSlice.reducer;
