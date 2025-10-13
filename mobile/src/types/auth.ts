export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated' | 'error';

export type AuthProfile = {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string;
  organizationId: string;
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  profile: AuthProfile;
  clerkSessionId?: string;
  biometricKey?: string;
};
