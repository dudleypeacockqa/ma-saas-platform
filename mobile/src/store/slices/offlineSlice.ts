import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type OfflineState = {
  isOffline: boolean;
  lastOnlineAt?: number;
};

const initialState: OfflineState = {
  isOffline: false
};

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    setOffline(state, action: PayloadAction<boolean>) {
      state.isOffline = action.payload;
      if (!action.payload) {
        state.lastOnlineAt = Date.now();
      }
    }
  }
});

export const { setOffline } = offlineSlice.actions;

export default offlineSlice.reducer;
