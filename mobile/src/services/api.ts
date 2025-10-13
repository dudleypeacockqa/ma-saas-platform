import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import Config from 'react-native-config';
import { fetch as secureFetch } from 'react-native-ssl-pinning';

const API_BASE_URL = Config.API_BASE_URL ?? 'https://api.ma-saas.local';
const CERT_ALIAS = Config.API_CERT_ALIAS ?? 'ma_saas_backend';

let accessToken: string | null = null;
let refreshTokenProvider: (() => Promise<string | null>) | null = null;
let onUnauthorized: (() => Promise<void>) | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

export const registerRefreshTokenProvider = (provider: () => Promise<string | null>) => {
  refreshTokenProvider = provider;
};

export const registerUnauthorizedHandler = (handler: () => Promise<void>) => {
  onUnauthorized = handler;
};

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
});

type PendingRequest = {
  resolve: (token: string | null) => void;
  reject: () => void;
};

let isRefreshing = false;
const pendingQueue: PendingRequest[] = [];

const processQueue = (token: string | null) => {
  pendingQueue.forEach((request) => {
    token ? request.resolve(token) : request.reject();
  });
  pendingQueue.length = 0;
};

apiClient.interceptors.request.use(async (config) => {
  if (accessToken) {
    config.headers = {
      ...(config.headers ?? {}),
      Authorization: 'Bearer ' + accessToken
    };
  }
  config.headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(config.headers ?? {})
  };
  return config;
});

type RefreshResponse = {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest: AxiosRequestConfig & { _retry?: boolean } = error.config ?? {};
    if (error.response?.status === 401 && !originalRequest._retry && refreshTokenProvider) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({
            resolve: (token) => {
              if (!token) {
                reject(error);
                return;
              }
              originalRequest.headers = {
                ...(originalRequest.headers ?? {}),
                Authorization: 'Bearer ' + token
              };
              resolve(apiClient(originalRequest));
            },
            reject: () => reject(error)
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = await refreshTokenProvider();
        if (!refreshToken) {
          throw error;
        }
        const refreshResponse = await apiClient.post<RefreshResponse>('/auth/refresh', {
          refreshToken
        });
        accessToken = refreshResponse.data.accessToken;
        processQueue(accessToken);
        originalRequest.headers = {
          ...(originalRequest.headers ?? {}),
          Authorization: 'Bearer ' + (accessToken ?? '')
        };
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(null);
        if (onUnauthorized) {
          await onUnauthorized();
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

type SecureRequestOptions = {
  path: string;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
};

export const securedRequest = async <T>({ path, method = 'GET', body, headers }: SecureRequestOptions): Promise<T> => {
  const response = await secureFetch(API_BASE_URL + path, {
    method,
    timeoutInterval: 15000,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: 'Bearer ' + accessToken } : {}),
      ...(headers ?? {})
    },
    sslPinning: {
      certs: [CERT_ALIAS]
    },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Request failed');
  }

  if (response.status === 204) {
    return {} as T;
  }

  const json = await response.json();
  return json as T;
};

export default apiClient;
