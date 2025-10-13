import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import DealDetailScreen from '@screens/DealDetailScreen';
import DealListScreen from '@screens/DealListScreen';
import DocumentViewerScreen from '@screens/DocumentViewerScreen';
import SignInScreen from '@screens/SignInScreen';
import BiometricUnlockScreen from '@screens/BiometricUnlockScreen';
import { useAppSelector } from '@hooks/useAppSelector';

export type RootStackParamList = {
  SignIn: undefined;
  BiometricUnlock: undefined;
  DealList: undefined;
  DealDetail: { dealId: string };
  DocumentViewer: { dealId: string; documentId: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator = () => {
  const isAuthenticated = useAppSelector((state) => state.auth.status === 'authenticated');
  const requiresBiometric = useAppSelector((state) => state.auth.requiresBiometricUnlock);

  if (!isAuthenticated) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="SignIn" component={SignInScreen} />
      </Stack.Navigator>
    );
  }

  if (requiresBiometric) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="BiometricUnlock" component={BiometricUnlockScreen} />
        <Stack.Screen
          name="DealList"
          component={DealListScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="DealDetail"
          component={DealDetailScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="DocumentViewer"
          component={DocumentViewerScreen}
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    );
  }

  return (
    <Stack.Navigator>
      <Stack.Screen name="DealList" component={DealListScreen} options={{ title: 'Deals' }} />
      <Stack.Screen name="DealDetail" component={DealDetailScreen} options={{ title: 'Deal Detail' }} />
      <Stack.Screen
        name="DocumentViewer"
        component={DocumentViewerScreen}
        options={{ title: 'Document Viewer' }}
      />
    </Stack.Navigator>
  );
};
