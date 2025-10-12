/**
 * Service Worker for M&A SaaS Platform PWA
 * Provides offline capabilities, caching, and background sync
 */

const CACHE_NAME = 'ma-platform-v1.0.0';
const OFFLINE_CACHE = 'ma-platform-offline-v1.0.0';
const API_CACHE = 'ma-platform-api-v1.0.0';

// Core application files to cache
const CORE_ASSETS = [
  '/',
  '/manifest.json',
  '/index.html',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/offline.html',
];

// API endpoints to cache for offline access
const API_ENDPOINTS = ['/api/deals', '/api/deals/pipeline/board', '/api/ai/models/status'];

// Routes that should work offline
const OFFLINE_ROUTES = ['/deals', '/deals/pipeline', '/ai-dashboard', '/analytics', '/profile'];

self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');

  event.waitUntil(
    Promise.all([
      // Cache core application assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[SW] Caching core assets');
        return cache.addAll(CORE_ASSETS);
      }),

      // Cache offline fallback page
      caches.open(OFFLINE_CACHE).then((cache) => {
        console.log('[SW] Caching offline fallbacks');
        return cache.add('/offline.html');
      }),
    ]),
  );

  // Activate immediately
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (
              cacheName !== CACHE_NAME &&
              cacheName !== OFFLINE_CACHE &&
              cacheName !== API_CACHE
            ) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          }),
        );
      }),

      // Take control of all clients
      self.clients.claim(),
    ]),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request));
    return;
  }

  // Handle static assets
  event.respondWith(handleStaticAssets(request));
});

async function handleApiRequest(request) {
  const url = new URL(request.url);

  try {
    // Always try network first for API requests
    const networkResponse = await fetch(request);

    // Cache successful GET responses
    if (networkResponse.ok && request.method === 'GET') {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW] API request failed, checking cache:', url.pathname);

    // Try to serve from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] Serving API from cache:', url.pathname);
      return cachedResponse;
    }

    // Return offline response for specific endpoints
    if (isOfflineApiEndpoint(url.pathname)) {
      return new Response(
        JSON.stringify({
          error: 'offline',
          message: 'This feature is not available offline',
          cached: false,
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    throw error;
  }
}

async function handleNavigationRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('[SW] Navigation request failed, serving offline page');

    // Check if this is a known offline route
    const url = new URL(request.url);
    if (isOfflineRoute(url.pathname)) {
      // Return cached app shell
      const cache = await caches.open(CACHE_NAME);
      const cachedResponse = await cache.match('/index.html');
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Return offline fallback page
    const offlineCache = await caches.open(OFFLINE_CACHE);
    return await offlineCache.match('/offline.html');
  }
}

async function handleStaticAssets(request) {
  // Try cache first for static assets
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    // Try network
    const networkResponse = await fetch(request);

    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW] Static asset request failed:', request.url);
    throw error;
  }
}

function isOfflineApiEndpoint(pathname) {
  return API_ENDPOINTS.some((endpoint) => pathname.startsWith(endpoint));
}

function isOfflineRoute(pathname) {
  return OFFLINE_ROUTES.some((route) => pathname.startsWith(route));
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);

  if (event.tag === 'background-sync-deals') {
    event.waitUntil(syncFailedRequests());
  }
});

async function syncFailedRequests() {
  console.log('[SW] Syncing failed requests...');

  // Get failed requests from IndexedDB and retry them
  try {
    const db = await openDB();
    const tx = db.transaction(['failed_requests'], 'readonly');
    const store = tx.objectStore('failed_requests');
    const requests = await store.getAll();

    for (const failedRequest of requests) {
      try {
        await fetch(failedRequest.url, failedRequest.options);
        console.log('[SW] Successfully synced request:', failedRequest.url);

        // Remove from failed requests
        const deleteTx = db.transaction(['failed_requests'], 'readwrite');
        const deleteStore = deleteTx.objectStore('failed_requests');
        await deleteStore.delete(failedRequest.id);
      } catch (error) {
        console.log('[SW] Failed to sync request:', failedRequest.url, error);
      }
    }
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');

  if (!event.data) {
    return;
  }

  const data = event.data.json();

  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: data.tag || 'default',
    data: data.data || {},
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: '/icons/view-24x24.png',
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/icons/dismiss-24x24.png',
      },
    ],
    requireInteraction: data.requireInteraction || false,
    silent: data.silent || false,
    vibrate: data.vibrate || [200, 100, 200],
  };

  event.waitUntil(self.registration.showNotification(data.title || 'M&A Platform', options));
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.notification.tag);

  event.notification.close();

  const action = event.action;
  const data = event.notification.data;

  if (action === 'dismiss') {
    return;
  }

  // Handle notification click
  let targetUrl = '/';

  if (data.dealId) {
    targetUrl = `/deals/${data.dealId}`;
  } else if (data.url) {
    targetUrl = data.url;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      // Try to focus existing window
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus().then(() => {
            client.postMessage({
              type: 'NOTIFICATION_CLICK',
              url: targetUrl,
              data: data,
            });
          });
        }
      }

      // Open new window if no existing window found
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    }),
  );
});

// Message handling from main thread
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);

  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'SKIP_WAITING':
        self.skipWaiting();
        break;

      case 'GET_VERSION':
        event.ports[0].postMessage({ version: CACHE_NAME });
        break;

      case 'CLEAR_CACHE':
        clearAllCaches().then(() => {
          event.ports[0].postMessage({ success: true });
        });
        break;

      default:
        console.log('[SW] Unknown message type:', event.data.type);
    }
  }
});

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map((name) => caches.delete(name)));
  console.log('[SW] All caches cleared');
}

// IndexedDB helper for storing failed requests
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('ma-platform-sw', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('failed_requests')) {
        const store = db.createObjectStore('failed_requests', {
          keyPath: 'id',
          autoIncrement: true,
        });
        store.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
}

console.log('[SW] Service worker loaded successfully');
