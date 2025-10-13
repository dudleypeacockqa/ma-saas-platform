import EncryptedStorage from 'react-native-encrypted-storage';
import * as Keychain from 'react-native-keychain';
import Config from 'react-native-config';

import apiClient, {
  registerRefreshTokenProvider,
  registerUnauthorizedHandler,
  securedRequest,
  setAccessToken
} from './api';
import type { AuthProfile, AuthSession } from '@types/auth';

const SESSION_STORAGE_KEY = 'ma_saas_auth_session';
const BIOMETRIC_KEY = 'ma_saas_biometric_token';
const PLATFORM_CLIENT_ID = Config.MOBILE_CLIENT_ID ?? 'mobile-client';

type SignInRequest = {
  email: string;
  password: string;
};

type SignInResponse = {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  profile: AuthProfile;
  clerkSessionId?: string;
  biometricKey?: string;
};

type RefreshResponse = {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
};

export const signIn = async ({ email, password }: SignInRequest): Promise<AuthSession> => {
  const response = await apiClient.post<SignInResponse>('/auth/mobile/login', {
    email,
    password,
    clientId: PLATFORM_CLIENT_ID
  });

  const session = buildSession(response.data);
  await persistSession(session);
  return session;
};

export const refreshSession = async (refreshToken: string): Promise<AuthSession> => {
  const response = await apiClient.post<RefreshResponse>('/auth/refresh', { refreshToken });
  const current = await loadSession();
  if (!current) {
    throw new Error('No session to refresh');
  }

  const updated: AuthSession = {
    ...current,
    accessToken: response.data.accessToken,
    refreshToken: response.data.refreshToken,
    expiresAt: Date.now() + response.data.expiresIn * 1000
  };
  await persistSession(updated);
  return updated;
};

export const loadSession = async (): Promise<AuthSession | null> => {
  const raw = await EncryptedStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const session: AuthSession = JSON.parse(raw);
    if (!session.accessToken || !session.refreshToken) {
      return null;
    }
    setAccessToken(session.accessToken);
    return session;
  } catch (error) {
    await EncryptedStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
};

export const persistSession = async (session: AuthSession) => {
  setAccessToken(session.accessToken);
  await EncryptedStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
};

export const clearSession = async () => {
  setAccessToken(null);
  await EncryptedStorage.removeItem(SESSION_STORAGE_KEY);
  await Keychain.resetGenericPassword({ service: BIOMETRIC_KEY }).catch(() => undefined);
};

export const enableBiometrics = async (accessToken: string) => {
  await Keychain.setGenericPassword('biometric-user', accessToken, {
    service: BIOMETRIC_KEY,
    accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_CURRENT_SET,
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED
  });
};

export const getBiometricToken = async (): Promise<string | null> => {
  const credentials = await Keychain.getGenericPassword({ service: BIOMETRIC_KEY });
  if (!credentials) {
    return null;
  }
  return typeof credentials.password === 'string' ? credentials.password : null;
};

export const validateSession = async (): Promise<boolean> => {
  const session = await loadSession();
  if (!session) {
    return false;
  }

  const isExpired = session.expiresAt <= Date.now();
  if (isExpired) {
    const refreshed = await refreshSession(session.refreshToken);
    return Boolean(refreshed.accessToken);
  }

  return true;
};

type DeviceRegistrationRequest = {
  token: string;
};

export const registerDeviceToken = async (token: string): Promise<void> => {
  const payload: DeviceRegistrationRequest = { token };
  await securedRequest<void>({
    path: '/devices/register',
    method: 'POST',
    body: payload
  });
};

const buildSession = (response: SignInResponse): AuthSession => ({
  accessToken: response.accessToken,
  refreshToken: response.refreshToken,
  expiresAt: Date.now() + response.expiresIn * 1000,
  profile: response.profile,
  clerkSessionId: response.clerkSessionId,
  biometricKey: response.biometricKey
});

registerUnauthorizedHandler(async () => {
  await clearSession();
});

registerRefreshTokenProvider(async () => {
  const session = await loadSession();
  return session?.refreshToken ?? null;
});
