import React, { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, Text, TextInput, TouchableOpacity, View } from 'react-native';

import LoadingOverlay from '@components/common/LoadingOverlay';
import { colors } from '@theme/index';
import { useAppDispatch } from '@hooks/useAppDispatch';
import { useAppSelector } from '@hooks/useAppSelector';
import { authenticateThunk } from '@store/slices/authSlice';

import styles from './styles/SignInScreen.styles';

const SignInScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const status = useAppSelector((state) => state.auth.status);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignIn = async () => {
    const result = await dispatch(
      authenticateThunk({
        email,
        password
      })
    );

    if (authenticateThunk.rejected.match(result)) {
      Alert.alert('Sign-in failed', result.error.message ?? 'Please check your credentials.');
    }
  };

  const isLoading = status === 'loading';

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={64}
    >
      <Text style={styles.title}>Welcome back</Text>
      <Text style={styles.subtitle}>Sign in with your M&A workspace account</Text>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Email</Text>
        <TextInput
          autoCapitalize="none"
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          placeholder="you@example.com"
          placeholderTextColor={colors.textSecondary}
        />
      </View>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Password</Text>
        <TextInput
          secureTextEntry
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="••••••••"
          placeholderTextColor={colors.textSecondary}
        />
      </View>

      <TouchableOpacity style={styles.button} onPress={handleSignIn} disabled={isLoading}>
        <Text style={styles.buttonText}>{isLoading ? 'Signing in...' : 'Sign in'}</Text>
      </TouchableOpacity>

      {isLoading && <LoadingOverlay transparent message="Signing in..." />}
    </KeyboardAvoidingView>
  );
};

export default SignInScreen;
