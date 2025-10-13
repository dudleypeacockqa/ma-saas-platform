import messaging from '@react-native-firebase/messaging';
import Config from 'react-native-config';
import { io, Socket } from 'socket.io-client';

import { registerDeviceToken } from './auth';

const SOCKET_URL = Config.REALTIME_SOCKET_URL ?? 'https://api.ma-saas.local/ws';

let socket: Socket | null = null;

export const requestNotificationPermission = async (): Promise<boolean> => {
  const authorizationStatus = await messaging().requestPermission();
  return (
    authorizationStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authorizationStatus === messaging.AuthorizationStatus.PROVISIONAL
  );
};

export const registerForPushNotifications = async (): Promise<string | null> => {
  const granted = await requestNotificationPermission();
  if (!granted) {
    return null;
  }
  const token = await messaging().getToken();
  await registerDeviceToken(token);
  return token;
};

export const initializeSocket = (accessToken: string) => {
  if (socket) {
    return socket;
  }

  socket = io(SOCKET_URL, {
    transports: ['websocket'],
    auth: {
      token: accessToken
    }
  });

  socket.on('connect_error', (error) => {
    console.warn('Socket connection error', error.message);
  });

  return socket;
};

export const subscribeToDealChannel = (
  dealId: string,
  handler: (payload: unknown) => void
) => {
  if (!socket) {
    return;
  }
  socket.emit('join', { room: deal: });
  socket.on(deal:, handler);
};

export const unsubscribeFromDealChannel = (dealId: string) => {
  if (!socket) {
    return;
  }
  socket.emit('leave', { room: deal: });
  socket.removeAllListeners(deal:);
};

export const disconnectSocket = () => {
  if (!socket) {
    return;
  }
  socket.disconnect();
  socket = null;
};
