/**
 * Offline Data Synchronization Service
 * Sprint 24: Handles offline data storage and synchronization when connection is restored
 */

import { openDB, DBSchema, IDBPDatabase } from 'idb';

export interface PendingRequest {
  id: string;
  url: string;
  method: string;
  headers: Record<string, string>;
  body?: string;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  priority: 'low' | 'medium' | 'high';
  entityType?: string;
  entityId?: string;
}

export interface CachedData {
  id: string;
  key: string;
  data: any;
  timestamp: number;
  expiresAt?: number;
  version: number;
  tags: string[];
}

export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  pendingRequests: number;
  lastSyncTime?: number;
  syncErrors: number;
}

interface OfflineDB extends DBSchema {
  pending_requests: {
    key: string;
    value: PendingRequest;
    indexes: {
      'by-timestamp': number;
      'by-priority': string;
      'by-entity': string;
    };
  };
  cached_data: {
    key: string;
    value: CachedData;
    indexes: {
      'by-timestamp': number;
      'by-expiry': number;
      'by-tags': string;
    };
  };
  sync_metadata: {
    key: string;
    value: {
      key: string;
      lastSync: number;
      syncCount: number;
      errorCount: number;
    };
  };
}

class OfflineSyncService {
  private db: IDBPDatabase<OfflineDB> | null = null;
  private isOnline: boolean = navigator.onLine;
  private isSyncing: boolean = false;
  private syncListeners: Set<(status: SyncStatus) => void> = new Set();
  private syncInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.initialize();
    this.setupNetworkListeners();
  }

  /**
   * Initialize the offline database
   */
  private async initialize(): Promise<void> {
    try {
      this.db = await openDB<OfflineDB>('ma-platform-offline', 1, {
        upgrade(db) {
          // Pending requests store
          const requestsStore = db.createObjectStore('pending_requests', {
            keyPath: 'id',
          });
          requestsStore.createIndex('by-timestamp', 'timestamp');
          requestsStore.createIndex('by-priority', 'priority');
          requestsStore.createIndex('by-entity', ['entityType', 'entityId']);

          // Cached data store
          const cacheStore = db.createObjectStore('cached_data', {
            keyPath: 'id',
          });
          cacheStore.createIndex('by-timestamp', 'timestamp');
          cacheStore.createIndex('by-expiry', 'expiresAt');
          cacheStore.createIndex('by-tags', 'tags', { multiEntry: true });

          // Sync metadata store
          db.createObjectStore('sync_metadata', {
            keyPath: 'key',
          });
        },
      });

      console.log('Offline sync service initialized');

      // Start periodic sync if online
      if (this.isOnline) {
        this.startPeriodicSync();
      }
    } catch (error) {
      console.error('Failed to initialize offline sync service:', error);
    }
  }

  /**
   * Setup network status listeners
   */
  private setupNetworkListeners(): void {
    window.addEventListener('online', () => {
      console.log('Network connection restored');
      this.isOnline = true;
      this.notifyListeners();
      this.startPeriodicSync();
      this.syncPendingRequests();
    });

    window.addEventListener('offline', () => {
      console.log('Network connection lost');
      this.isOnline = false;
      this.notifyListeners();
      this.stopPeriodicSync();
    });
  }

  /**
   * Add a request to the pending queue for later sync
   */
  async addPendingRequest(request: Omit<PendingRequest, 'id' | 'timestamp' | 'retryCount'>): Promise<string> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const id = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const pendingRequest: PendingRequest = {
      id,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: 3,
      ...request,
    };

    await this.db.add('pending_requests', pendingRequest);
    this.notifyListeners();

    console.log('Added pending request:', id, request.url);

    // Try to sync immediately if online
    if (this.isOnline) {
      this.syncPendingRequests();
    }

    return id;
  }

  /**
   * Cache data for offline access
   */
  async cacheData(key: string, data: any, options: {
    expiresIn?: number;
    tags?: string[];
    version?: number;
  } = {}): Promise<void> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const now = Date.now();
    const cachedData: CachedData = {
      id: key,
      key,
      data,
      timestamp: now,
      expiresAt: options.expiresIn ? now + options.expiresIn : undefined,
      version: options.version || 1,
      tags: options.tags || [],
    };

    await this.db.put('cached_data', cachedData);
    console.log('Cached data:', key);
  }

  /**
   * Retrieve cached data
   */
  async getCachedData<T = any>(key: string): Promise<T | null> {
    if (!this.db) {
      return null;
    }

    try {
      const cached = await this.db.get('cached_data', key);

      if (!cached) {
        return null;
      }

      // Check if data has expired
      if (cached.expiresAt && Date.now() > cached.expiresAt) {
        await this.db.delete('cached_data', key);
        return null;
      }

      return cached.data as T;
    } catch (error) {
      console.error('Error retrieving cached data:', error);
      return null;
    }
  }

  /**
   * Sync all pending requests
   */
  async syncPendingRequests(): Promise<void> {
    if (!this.db || !this.isOnline || this.isSyncing) {
      return;
    }

    this.isSyncing = true;
    this.notifyListeners();

    try {
      const requests = await this.db.getAll('pending_requests');
      const sortedRequests = requests.sort((a, b) => {
        // Sort by priority first, then by timestamp
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
        return priorityDiff !== 0 ? priorityDiff : a.timestamp - b.timestamp;
      });

      console.log(`Syncing ${sortedRequests.length} pending requests`);

      for (const request of sortedRequests) {
        try {
          await this.executeRequest(request);
          await this.db.delete('pending_requests', request.id);
          console.log('Successfully synced request:', request.id);
        } catch (error) {
          console.error('Failed to sync request:', request.id, error);

          // Increment retry count
          request.retryCount++;

          if (request.retryCount >= request.maxRetries) {
            // Max retries reached, remove from queue
            await this.db.delete('pending_requests', request.id);
            console.log('Max retries reached for request:', request.id);
          } else {
            // Update retry count
            await this.db.put('pending_requests', request);
          }
        }
      }

      // Update last sync time
      await this.updateSyncMetadata('last_sync', {
        key: 'last_sync',
        lastSync: Date.now(),
        syncCount: sortedRequests.length,
        errorCount: 0,
      });

    } catch (error) {
      console.error('Error during sync:', error);
    } finally {
      this.isSyncing = false;
      this.notifyListeners();
    }
  }

  /**
   * Execute a pending request
   */
  private async executeRequest(request: PendingRequest): Promise<Response> {
    const { url, method, headers, body } = request;

    const response = await fetch(url, {
      method,
      headers,
      body: body || undefined,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response;
  }

  /**
   * Clear expired cached data
   */
  async clearExpiredCache(): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      const now = Date.now();
      const tx = this.db.transaction('cached_data', 'readwrite');
      const index = tx.store.index('by-expiry');

      // Get all expired entries
      const expiredCursor = await index.openCursor(IDBKeyRange.upperBound(now));
      let deletedCount = 0;

      if (expiredCursor) {
        do {
          await expiredCursor.delete();
          deletedCount++;
        } while (await expiredCursor.continue());
      }

      await tx.done;

      if (deletedCount > 0) {
        console.log(`Cleared ${deletedCount} expired cache entries`);
      }
    } catch (error) {
      console.error('Error clearing expired cache:', error);
    }
  }

  /**
   * Clear cache by tags
   */
  async clearCacheByTags(tags: string[]): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      const tx = this.db.transaction('cached_data', 'readwrite');
      const index = tx.store.index('by-tags');

      for (const tag of tags) {
        const cursor = await index.openCursor(tag);
        if (cursor) {
          do {
            await cursor.delete();
          } while (await cursor.continue());
        }
      }

      await tx.done;
      console.log('Cleared cache for tags:', tags);
    } catch (error) {
      console.error('Error clearing cache by tags:', error);
    }
  }

  /**
   * Get sync status
   */
  async getSyncStatus(): Promise<SyncStatus> {
    const pendingCount = this.db ? (await this.db.count('pending_requests')) : 0;
    const lastSyncMetadata = this.db ? (await this.db.get('sync_metadata', 'last_sync')) : null;

    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingRequests: pendingCount,
      lastSyncTime: lastSyncMetadata?.lastSync,
      syncErrors: lastSyncMetadata?.errorCount || 0,
    };
  }

  /**
   * Subscribe to sync status changes
   */
  onSyncStatusChange(listener: (status: SyncStatus) => void): () => void {
    this.syncListeners.add(listener);

    // Send initial status
    this.getSyncStatus().then(listener);

    // Return unsubscribe function
    return () => {
      this.syncListeners.delete(listener);
    };
  }

  /**
   * Start periodic sync
   */
  private startPeriodicSync(): void {
    if (this.syncInterval) {
      return;
    }

    this.syncInterval = setInterval(() => {
      if (this.isOnline && !this.isSyncing) {
        this.syncPendingRequests();
        this.clearExpiredCache();
      }
    }, 30000); // Sync every 30 seconds
  }

  /**
   * Stop periodic sync
   */
  private stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * Notify listeners of status changes
   */
  private async notifyListeners(): Promise<void> {
    const status = await this.getSyncStatus();
    this.syncListeners.forEach(listener => {
      try {
        listener(status);
      } catch (error) {
        console.error('Error in sync status listener:', error);
      }
    });
  }

  /**
   * Update sync metadata
   */
  private async updateSyncMetadata(key: string, data: any): Promise<void> {
    if (!this.db) {
      return;
    }

    await this.db.put('sync_metadata', data);
  }

  /**
   * Clear all offline data
   */
  async clearAllData(): Promise<void> {
    if (!this.db) {
      return;
    }

    await this.db.clear('pending_requests');
    await this.db.clear('cached_data');
    await this.db.clear('sync_metadata');

    console.log('Cleared all offline data');
    this.notifyListeners();
  }
}

// Export singleton instance
export const offlineSyncService = new OfflineSyncService();

// React hook for offline sync
export function useOfflineSync() {
  return {
    addPendingRequest: offlineSyncService.addPendingRequest.bind(offlineSyncService),
    cacheData: offlineSyncService.cacheData.bind(offlineSyncService),
    getCachedData: offlineSyncService.getCachedData.bind(offlineSyncService),
    syncPendingRequests: offlineSyncService.syncPendingRequests.bind(offlineSyncService),
    clearExpiredCache: offlineSyncService.clearExpiredCache.bind(offlineSyncService),
    clearCacheByTags: offlineSyncService.clearCacheByTags.bind(offlineSyncService),
    getSyncStatus: offlineSyncService.getSyncStatus.bind(offlineSyncService),
    onSyncStatusChange: offlineSyncService.onSyncStatusChange.bind(offlineSyncService),
    clearAllData: offlineSyncService.clearAllData.bind(offlineSyncService),
  };
}

export default offlineSyncService;