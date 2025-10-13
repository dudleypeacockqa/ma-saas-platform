import { useEffect } from 'react';
import NetInfo from '@react-native-community/netinfo';
import messaging from '@react-native-firebase/messaging';
import BackgroundFetch from 'react-native-background-fetch';

import { useAppDispatch } from '@hooks/useAppDispatch';
import { initializeSessionThunk } from '@store/slices/authSlice';
import { setOffline } from '@store/slices/offlineSlice';
import { registerDeviceTokenThunk } from '@store/slices/notificationsSlice';
import { triggerBackgroundSync } from '@store/slices/syncSlice';

const AppBootstrap = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(initializeSessionThunk());

    const netInfoUnsubscribe = NetInfo.addEventListener((state) => {
      const isOffline = !(state.isConnected && state.isInternetReachable !== false);
      dispatch(setOffline(isOffline));
    });

    const requestPermission = async () => {
      const authorizationStatus = await messaging().requestPermission();
      if (authorizationStatus === messaging.AuthorizationStatus.AUTHORIZED || authorizationStatus === messaging.AuthorizationStatus.PROVISIONAL) {
        const token = await messaging().getToken();
        dispatch(registerDeviceTokenThunk(token));
      }
    };

    requestPermission();

    const onTokenRefresh = messaging().onTokenRefresh((token) => {
      dispatch(registerDeviceTokenThunk(token));
    });

    BackgroundFetch.configure(
      {
        minimumFetchInterval: 15,
        enableHeadless: true,
        stopOnTerminate: false,
        startOnBoot: true
      },
      async () => {
        await dispatch(triggerBackgroundSync()).unwrap().catch(() => undefined);
        BackgroundFetch.finish(BackgroundFetch.FETCH_RESULT_NEW_DATA);
      },
      (error) => {
        console.warn('Background fetch failed to start', error);
      }
    );

    return () => {
      netInfoUnsubscribe();
      onTokenRefresh();
      BackgroundFetch.stop().catch(() => undefined);
    };
  }, [dispatch]);

  return null;
};

export default AppBootstrap;
