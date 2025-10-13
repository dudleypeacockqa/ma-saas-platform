import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Text, TouchableOpacity, View } from 'react-native';
import ReactNativeBiometrics from 'react-native-biometrics';

import LoadingOverlay from '@components/common/LoadingOverlay';
import { useAppDispatch } from '@hooks/useAppDispatch';
import { useAppSelector } from '@hooks/useAppSelector';
import { completeBiometricUnlockThunk } from '@store/slices/authSlice';

import styles from './styles/BiometricUnlockScreen.styles';

const BiometricUnlockScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const [isAttempting, setIsAttempting] = useState(false);
  const sessionOwner = useAppSelector((state) => state.auth.profile?.fullName ?? '');

  const handleUnlock = useCallback(async () => {
    setIsAttempting(true);
    const biometrics = new ReactNativeBiometrics();
    const { available } = await biometrics.isSensorAvailable();

    if (!available) {
      Alert.alert('Biometric unavailable', 'Unlock with password from the web portal.');
      setIsAttempting(false);
      return;
    }

    const { success } = await biometrics.simplePrompt({ promptMessage: 'Authenticate' });

    if (!success) {
      Alert.alert('Authentication cancelled');
      setIsAttempting(false);
      return;
    }

    const result = await dispatch(completeBiometricUnlockThunk());
    if (completeBiometricUnlockThunk.rejected.match(result)) {
      Alert.alert('Unlock failed', result.error.message ?? 'Please try again.');
    }
    setIsAttempting(false);
  }, [dispatch]);

  useEffect(() => {
    handleUnlock();
  }, [handleUnlock]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hi {sessionOwner || 'there'} 👋</Text>
      <Text style={styles.subtitle}>Use Touch ID / Face ID to continue</Text>
      <TouchableOpacity style={styles.button} onPress={handleUnlock} disabled={isAttempting}>
        <Text style={styles.buttonText}>Unlock</Text>
      </TouchableOpacity>
      {isAttempting && <LoadingOverlay transparent message="Verifying..." />}
    </View>
  );
};

export default BiometricUnlockScreen;
