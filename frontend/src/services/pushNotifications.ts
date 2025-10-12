/**
 * Push Notifications Service
 * Sprint 24: Advanced push notification management with service worker integration
 */

import { webSocketService } from './websocket';

export interface PushSubscriptionData {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
  userId?: string;
  organizationId?: string;
}

export interface NotificationPayload {
  title: string;
  body: string;
  icon?: string;
  badge?: string;
  tag?: string;
  data?: any;
  actions?: NotificationAction[];
  requireInteraction?: boolean;
  silent?: boolean;
}

class PushNotificationService {
  private registration: ServiceWorkerRegistration | null = null;
  private subscription: PushSubscription | null = null;
  private vapidPublicKey: string = process.env.VITE_VAPID_PUBLIC_KEY || '';

  constructor() {
    this.initialize();
  }

  /**
   * Initialize push notification service
   */
  async initialize(): Promise<void> {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service workers not supported');
      return;
    }

    if (!('PushManager' in window)) {
      console.warn('Push messaging not supported');
      return;
    }

    try {
      // Register service worker
      this.registration = await navigator.serviceWorker.register('/sw.js');

      // Wait for service worker to be ready
      await navigator.serviceWorker.ready;

      console.log('Push notification service initialized');
    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
    }
  }

  /**
   * Request notification permission from user
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      throw new Error('Notifications not supported');
    }

    const permission = await Notification.requestPermission();

    if (permission === 'granted') {
      console.log('Notification permission granted');
    } else if (permission === 'denied') {
      console.warn('Notification permission denied');
    } else {
      console.log('Notification permission dismissed');
    }

    return permission;
  }

  /**
   * Subscribe to push notifications
   */
  async subscribe(userId: string, organizationId: string): Promise<PushSubscription | null> {
    if (!this.registration) {
      await this.initialize();
    }

    if (!this.registration || !this.vapidPublicKey) {
      console.error('Service worker not registered or VAPID key missing');
      return null;
    }

    try {
      // Check if already subscribed
      const existingSubscription = await this.registration.pushManager.getSubscription();
      if (existingSubscription) {
        this.subscription = existingSubscription;
        await this.sendSubscriptionToServer(userId, organizationId);
        return existingSubscription;
      }

      // Create new subscription
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });

      this.subscription = subscription;

      // Send subscription to server
      await this.sendSubscriptionToServer(userId, organizationId);

      console.log('Push subscription created:', subscription);
      return subscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      return null;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (!this.subscription) {
      return true;
    }

    try {
      const result = await this.subscription.unsubscribe();
      this.subscription = null;

      // Notify server about unsubscription
      await this.removeSubscriptionFromServer();

      console.log('Push subscription removed');
      return result;
    } catch (error) {
      console.error('Failed to unsubscribe from push notifications:', error);
      return false;
    }
  }

  /**
   * Get current subscription status
   */
  async getSubscription(): Promise<PushSubscription | null> {
    if (!this.registration) {
      return null;
    }

    try {
      const subscription = await this.registration.pushManager.getSubscription();
      this.subscription = subscription;
      return subscription;
    } catch (error) {
      console.error('Failed to get subscription:', error);
      return null;
    }
  }

  /**
   * Check if notifications are supported and permitted
   */
  isSupported(): boolean {
    return (
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  }

  /**
   * Get current notification permission status
   */
  getPermissionStatus(): NotificationPermission {
    if (!('Notification' in window)) {
      return 'denied';
    }
    return Notification.permission;
  }

  /**
   * Show local notification (fallback when push is not available)
   */
  async showLocalNotification(payload: NotificationPayload): Promise<void> {
    if (this.getPermissionStatus() !== 'granted') {
      console.warn('Notification permission not granted');
      return;
    }

    try {
      const notification = new Notification(payload.title, {
        body: payload.body,
        icon: payload.icon || '/icons/icon-192x192.png',
        badge: payload.badge || '/icons/badge-72x72.png',
        tag: payload.tag,
        data: payload.data,
        requireInteraction: payload.requireInteraction || false,
        silent: payload.silent || false,
      });

      // Handle notification click
      notification.onclick = (event) => {
        event.preventDefault();
        window.focus();

        // Handle navigation based on notification data
        if (payload.data?.url) {
          window.location.href = payload.data.url;
        }

        notification.close();
      };

      // Auto-close after 5 seconds for non-critical notifications
      if (!payload.requireInteraction) {
        setTimeout(() => {
          notification.close();
        }, 5000);
      }
    } catch (error) {
      console.error('Failed to show local notification:', error);
    }
  }

  /**
   * Send subscription to server
   */
  private async sendSubscriptionToServer(userId: string, organizationId: string): Promise<void> {
    if (!this.subscription) {
      return;
    }

    try {
      const subscriptionData: PushSubscriptionData = {
        endpoint: this.subscription.endpoint,
        keys: {
          p256dh: this.arrayBufferToBase64(this.subscription.getKey('p256dh')!),
          auth: this.arrayBufferToBase64(this.subscription.getKey('auth')!)
        },
        userId,
        organizationId
      };

      const response = await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscriptionData)
      });

      if (!response.ok) {
        throw new Error('Failed to send subscription to server');
      }

      console.log('Subscription sent to server successfully');
    } catch (error) {
      console.error('Failed to send subscription to server:', error);
    }
  }

  /**
   * Remove subscription from server
   */
  private async removeSubscriptionFromServer(): Promise<void> {
    try {
      const response = await fetch('/api/push/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove subscription from server');
      }

      console.log('Subscription removed from server successfully');
    } catch (error) {
      console.error('Failed to remove subscription from server:', error);
    }
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  /**
   * Convert ArrayBuffer to base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let result = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      result += String.fromCharCode(bytes[i]);
    }
    return window.btoa(result);
  }
}

// Export singleton instance
export const pushNotificationService = new PushNotificationService();

// React hook for push notifications
export function usePushNotifications() {
  return {
    isSupported: pushNotificationService.isSupported.bind(pushNotificationService),
    getPermissionStatus: pushNotificationService.getPermissionStatus.bind(pushNotificationService),
    requestPermission: pushNotificationService.requestPermission.bind(pushNotificationService),
    subscribe: pushNotificationService.subscribe.bind(pushNotificationService),
    unsubscribe: pushNotificationService.unsubscribe.bind(pushNotificationService),
    getSubscription: pushNotificationService.getSubscription.bind(pushNotificationService),
    showLocalNotification: pushNotificationService.showLocalNotification.bind(pushNotificationService),
  };
}

export default pushNotificationService;