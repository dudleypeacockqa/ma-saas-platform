import React from 'react';
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';

import { RootNavigator } from '@navigation/RootNavigator';
import OfflineBanner from '@components/common/OfflineBanner';
import LoadingOverlay from '@components/common/LoadingOverlay';
import NotificationListener from '@components/common/NotificationListener';
import AppBootstrap from '@components/common/AppBootstrap';
import { persistor, store } from '@store/index';

const App = () => (
  <GestureHandlerRootView style={{ flex: 1 }}>
    <Provider store={store}>
      <PersistGate loading={<LoadingOverlay message="Loading application..." />} persistor={persistor}>
        <SafeAreaProvider>
          <NavigationContainer>
            <StatusBar barStyle="light-content" />
            <AppBootstrap />
            <RootNavigator />
            <OfflineBanner />
            <NotificationListener />
          </NavigationContainer>
        </SafeAreaProvider>
      </PersistGate>
    </Provider>
  </GestureHandlerRootView>
);

export default App;
