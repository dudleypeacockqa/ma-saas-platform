import { useEffect } from 'react';
import messaging from '@react-native-firebase/messaging';
import { AppState } from 'react-native';

import { useAppDispatch } from '@hooks/useAppDispatch';
import { enqueueNotification } from '@store/slices/notificationsSlice';

const NotificationListener = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsubscribe = messaging().onMessage((message) => {
      dispatch(
        enqueueNotification({
          id: message.messageId ?? `${Date.now()}`,
          title: message.notification?.title ?? 'Update',
          body: message.notification?.body ?? '',
          data: message.data ?? {},
          receivedAt: Date.now()
        })
      );
    });

    const backgroundSub = messaging().setBackgroundMessageHandler(async (message) => {
      dispatch(
        enqueueNotification({
          id: message.messageId ?? `${Date.now()}`,
          title: message.notification?.title ?? 'Update',
          body: message.notification?.body ?? '',
          data: message.data ?? {},
          receivedAt: Date.now(),
          deliveredSilently: true
        })
      );
    });

    const appStateListener = AppState.addEventListener('change', (nextState) => {
      if (nextState === 'active') {
        messaging().setBadge(0);
      }
    });

    return () => {
      unsubscribe();
      backgroundSub.catch(() => undefined);
      appStateListener.remove();
    };
  }, [dispatch]);

  return null;
};

export default NotificationListener;
