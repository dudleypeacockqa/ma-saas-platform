/**
 * WebSocket Service for Real-time Updates
 * Sprint 23 Phase 2: Real-time notifications and live collaboration
 */

import { io, Socket } from 'socket.io-client';

export interface NotificationData {
  id: string;
  type: 'deal_update' | 'pipeline_change' | 'ai_analysis' | 'comment' | 'mention' | 'system';
  title: string;
  message: string;
  dealId?: string;
  userId?: string;
  organizationId: string;
  timestamp: string;
  data?: Record<string, any>;
  read?: boolean;
  priority?: 'low' | 'medium' | 'high';
}

export interface WebSocketEvents {
  // Incoming events
  notification: (data: NotificationData) => void;
  deal_updated: (dealId: string, updates: any) => void;
  pipeline_changed: (dealId: string, oldStage: string, newStage: string) => void;
  user_activity: (userId: string, activity: string) => void;
  ai_analysis_complete: (dealId: string, analysis: any) => void;
  connection_status: (status: 'connected' | 'disconnected' | 'reconnecting') => void;

  // Outgoing events
  join_deal: (dealId: string) => void;
  leave_deal: (dealId: string) => void;
  mark_notification_read: (notificationId: string) => void;
  user_typing: (dealId: string, isTyping: boolean) => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnected = false;
  private eventListeners: Map<string, Set<Function>> = new Map();
  private joinedDeals: Set<string> = new Set();

  constructor() {
    this.setupEventListeners();
  }

  /**
   * Initialize WebSocket connection
   */
  connect(token: string, organizationId: string): void {
    if (this.socket?.connected) {
      console.log('[WebSocket] Already connected');
      return;
    }

    const wsUrl = process.env.NODE_ENV === 'production'
      ? 'wss://your-domain.com'
      : 'ws://localhost:8000';

    console.log('[WebSocket] Connecting to:', wsUrl);

    this.socket = io(wsUrl, {
      auth: {
        token,
        organizationId,
      },
      transports: ['websocket', 'polling'],
      timeout: 10000,
      forceNew: true,
    });

    this.setupSocketListeners();
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      console.log('[WebSocket] Disconnecting...');
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.joinedDeals.clear();
      this.emit('connection_status', 'disconnected');
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isSocketConnected(): boolean {
    return this.isConnected && this.socket?.connected === true;
  }

  /**
   * Join a deal room for real-time updates
   */
  joinDeal(dealId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_deal', dealId);
      this.joinedDeals.add(dealId);
      console.log('[WebSocket] Joined deal room:', dealId);
    }
  }

  /**
   * Leave a deal room
   */
  leaveDeal(dealId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_deal', dealId);
      this.joinedDeals.delete(dealId);
      console.log('[WebSocket] Left deal room:', dealId);
    }
  }

  /**
   * Mark notification as read
   */
  markNotificationRead(notificationId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('mark_notification_read', notificationId);
    }
  }

  /**
   * Send typing indicator
   */
  sendTypingIndicator(dealId: string, isTyping: boolean): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('user_typing', { dealId, isTyping });
    }
  }

  /**
   * Send custom event
   */
  emitEvent(event: string, data?: any): void {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    }
  }

  /**
   * Subscribe to WebSocket events
   */
  on<K extends keyof WebSocketEvents>(event: K, callback: WebSocketEvents[K]): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback);
  }

  /**
   * Unsubscribe from WebSocket events
   */
  off<K extends keyof WebSocketEvents>(event: K, callback: WebSocketEvents[K]): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  /**
   * Emit event to local listeners
   */
  private emit<K extends keyof WebSocketEvents>(event: K, ...args: Parameters<WebSocketEvents[K]>): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          (callback as any)(...args);
        } catch (error) {
          console.error('[WebSocket] Error in event listener:', error);
        }
      });
    }
  }

  /**
   * Setup Socket.IO event listeners
   */
  private setupSocketListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected successfully');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connection_status', 'connected');

      // Rejoin all previously joined deals
      this.joinedDeals.forEach(dealId => {
        this.socket!.emit('join_deal', dealId);
      });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
      this.isConnected = false;
      this.emit('connection_status', 'disconnected');

      // Auto-reconnect unless manually disconnected
      if (reason !== 'io client disconnect') {
        this.handleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error);
      this.isConnected = false;
      this.handleReconnect();
    });

    // Business event listeners
    this.socket.on('notification', (data: NotificationData) => {
      console.log('[WebSocket] Notification received:', data);
      this.emit('notification', data);
      this.showBrowserNotification(data);
    });

    this.socket.on('deal_updated', (dealId: string, updates: any) => {
      console.log('[WebSocket] Deal updated:', dealId, updates);
      this.emit('deal_updated', dealId, updates);
    });

    this.socket.on('pipeline_changed', (dealId: string, oldStage: string, newStage: string) => {
      console.log('[WebSocket] Pipeline changed:', dealId, oldStage, '->', newStage);
      this.emit('pipeline_changed', dealId, oldStage, newStage);
    });

    this.socket.on('user_activity', (userId: string, activity: string) => {
      this.emit('user_activity', userId, activity);
    });

    this.socket.on('ai_analysis_complete', (dealId: string, analysis: any) => {
      console.log('[WebSocket] AI analysis complete:', dealId);
      this.emit('ai_analysis_complete', dealId, analysis);
    });

    this.socket.on('user_typing', (data: { userId: string; dealId: string; isTyping: boolean }) => {
      console.log('[WebSocket] User typing:', data);
      // Emit to local listeners if needed
    });
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      this.emit('connection_status', 'disconnected');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.emit('connection_status', 'reconnecting');

    setTimeout(() => {
      if (this.socket && !this.socket.connected) {
        this.socket.connect();
      }
    }, delay);
  }

  /**
   * Show browser notification
   */
  private async showBrowserNotification(data: NotificationData): Promise<void> {
    // Check if notifications are supported and permitted
    if (!('Notification' in window)) {
      return;
    }

    if (Notification.permission === 'denied') {
      return;
    }

    if (Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        return;
      }
    }

    // Don't show notification if page is visible
    if (!document.hidden) {
      return;
    }

    const notification = new Notification(data.title, {
      body: data.message,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      tag: data.id,
      requireInteraction: data.priority === 'high',
      data: data.data,
    });

    notification.onclick = () => {
      window.focus();
      if (data.dealId) {
        window.location.href = `/deals/${data.dealId}`;
      }
      notification.close();
    };

    // Auto-close after 5 seconds for non-critical notifications
    if (data.priority !== 'high') {
      setTimeout(() => {
        notification.close();
      }, 5000);
    }
  }

  /**
   * Setup global event listeners
   */
  private setupEventListeners(): void {
    // Listen for page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.socket && !this.socket.connected) {
        // Page became visible and we're disconnected, try to reconnect
        console.log('[WebSocket] Page visible, checking connection...');
        if (!this.isConnected) {
          this.socket.connect();
        }
      }
    });

    // Listen for online/offline events
    window.addEventListener('online', () => {
      console.log('[WebSocket] Browser back online');
      if (this.socket && !this.socket.connected) {
        this.socket.connect();
      }
    });

    window.addEventListener('offline', () => {
      console.log('[WebSocket] Browser went offline');
      this.emit('connection_status', 'disconnected');
    });
  }

  /**
   * Get connection statistics
   */
  getStats(): {
    connected: boolean;
    reconnectAttempts: number;
    joinedDeals: string[];
    transport?: string;
  } {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      joinedDeals: Array.from(this.joinedDeals),
      transport: this.socket?.io.engine?.transport?.name,
    };
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();

// React hook for easier component integration
export function useWebSocket() {
  return {
    connect: webSocketService.connect.bind(webSocketService),
    disconnect: webSocketService.disconnect.bind(webSocketService),
    isConnected: webSocketService.isSocketConnected.bind(webSocketService),
    joinDeal: webSocketService.joinDeal.bind(webSocketService),
    leaveDeal: webSocketService.leaveDeal.bind(webSocketService),
    markNotificationRead: webSocketService.markNotificationRead.bind(webSocketService),
    sendTypingIndicator: webSocketService.sendTypingIndicator.bind(webSocketService),
    on: webSocketService.on.bind(webSocketService),
    off: webSocketService.off.bind(webSocketService),
    emit: webSocketService.emitEvent.bind(webSocketService),
    getStats: webSocketService.getStats.bind(webSocketService),
  };
}

export default webSocketService;