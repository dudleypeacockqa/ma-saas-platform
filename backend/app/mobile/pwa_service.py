"""
Progressive Web App Service
PWA capabilities including service worker, push notifications, and offline support
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

logger = logging.getLogger(__name__)


class NotificationAction(str, Enum):
    """PWA notification action types"""
    OPEN_DEAL = "open_deal"
    OPEN_DOCUMENT = "open_document"
    MARK_READ = "mark_read"
    DISMISS = "dismiss"
    REPLY = "reply"
    APPROVE = "approve"
    REJECT = "reject"


class PWAFeature(str, Enum):
    """PWA features and capabilities"""
    PUSH_NOTIFICATIONS = "push_notifications"
    OFFLINE_SUPPORT = "offline_support"
    BACKGROUND_SYNC = "background_sync"
    HOME_SCREEN_INSTALL = "home_screen_install"
    FULL_SCREEN_MODE = "full_screen_mode"
    CAMERA_ACCESS = "camera_access"
    FILE_SYSTEM_ACCESS = "file_system_access"
    SHARE_TARGET = "share_target"


@dataclass
class PWANotification:
    """PWA push notification structure"""
    title: str
    body: str
    icon: str
    badge: str
    tag: str
    data: Dict[str, Any]
    actions: List[Dict[str, str]]
    timestamp: datetime
    ttl: int = 86400  # 24 hours default
    urgency: str = "normal"  # low, normal, high
    silent: bool = False
    vibrate: List[int] = None

    def to_webpush_payload(self) -> Dict[str, Any]:
        """Convert to web push payload format"""
        payload = {
            "title": self.title,
            "body": self.body,
            "icon": self.icon,
            "badge": self.badge,
            "tag": self.tag,
            "data": self.data,
            "timestamp": int(self.timestamp.timestamp() * 1000),
            "silent": self.silent
        }

        if self.actions:
            payload["actions"] = self.actions

        if self.vibrate:
            payload["vibrate"] = self.vibrate

        return payload


@dataclass
class PWASubscription:
    """PWA push subscription"""
    user_id: str
    organization_id: str
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str
    created_at: datetime
    last_used: datetime
    is_active: bool = True


class PWAManifestGenerator:
    """Generate PWA manifest and service worker"""

    @staticmethod
    def generate_manifest(
        app_name: str = "M&A Platform",
        app_short_name: str = "M&A Platform",
        app_description: str = "Professional M&A Deal Management Platform",
        theme_color: str = "#1a365d",
        background_color: str = "#ffffff",
        start_url: str = "/",
        scope: str = "/"
    ) -> Dict[str, Any]:
        """Generate PWA manifest.json"""

        return {
            "name": app_name,
            "short_name": app_short_name,
            "description": app_description,
            "start_url": start_url,
            "scope": scope,
            "display": "standalone",
            "orientation": "portrait-primary",
            "theme_color": theme_color,
            "background_color": background_color,
            "lang": "en-US",
            "categories": ["business", "finance", "productivity"],
            "icons": [
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable any"
                }
            ],
            "shortcuts": [
                {
                    "name": "New Deal",
                    "short_name": "New Deal",
                    "description": "Create a new M&A deal",
                    "url": "/deals/new",
                    "icons": [
                        {
                            "src": "/static/icons/shortcut-new-deal.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "Dashboard",
                    "short_name": "Dashboard",
                    "description": "View deal dashboard",
                    "url": "/dashboard",
                    "icons": [
                        {
                            "src": "/static/icons/shortcut-dashboard.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "Documents",
                    "short_name": "Documents",
                    "description": "Manage documents",
                    "url": "/documents",
                    "icons": [
                        {
                            "src": "/static/icons/shortcut-documents.png",
                            "sizes": "96x96"
                        }
                    ]
                }
            ],
            "share_target": {
                "action": "/share",
                "method": "POST",
                "enctype": "multipart/form-data",
                "params": {
                    "title": "title",
                    "text": "text",
                    "url": "url",
                    "files": [
                        {
                            "name": "documents",
                            "accept": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
                        }
                    ]
                }
            },
            "protocol_handlers": [
                {
                    "protocol": "web+maplatform",
                    "url": "/handle/%s"
                }
            ]
        }

    @staticmethod
    def generate_service_worker() -> str:
        """Generate service worker JavaScript code"""

        return """
const CACHE_NAME = 'ma-platform-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/offline.html'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        return fetch(event.request)
          .then(response => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // Network failed, try to serve offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push event - handle push notifications
self.addEventListener('push', event => {
  const options = {
    body: 'New update available!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open',
        icon: '/static/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/xmark.png'
      }
    ]
  };

  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.title = data.title || 'M&A Platform';
    options.icon = data.icon || options.icon;
    options.badge = data.badge || options.badge;
    options.data = data.data || options.data;
    options.actions = data.actions || options.actions;
    if (data.vibrate) options.vibrate = data.vibrate;
  }

  event.waitUntil(
    self.registration.showNotification('M&A Platform', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    // Open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Implement background sync logic
  try {
    // Sync pending data with server
    const pendingData = await getPendingData();
    if (pendingData.length > 0) {
      await syncDataWithServer(pendingData);
      await clearPendingData();
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

async function getPendingData() {
  // Get data from IndexedDB or localStorage
  return [];
}

async function syncDataWithServer(data) {
  // Send data to server
  return fetch('/api/sync', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
}

async function clearPendingData() {
  // Clear synced data from local storage
}

// Share target handling
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  if (url.pathname === '/share' && event.request.method === 'POST') {
    event.respondWith(handleSharedContent(event.request));
  }
});

async function handleSharedContent(request) {
  const formData = await request.formData();
  const title = formData.get('title');
  const text = formData.get('text');
  const url = formData.get('url');
  const files = formData.getAll('documents');

  // Store shared content for processing
  await storeSharedContent({ title, text, url, files });

  // Redirect to app
  return Response.redirect('/documents?shared=true', 303);
}

async function storeSharedContent(content) {
  // Store in IndexedDB for later processing
  // Implementation would use IndexedDB API
}
"""


class PWAService:
    """Progressive Web App service manager"""

    def __init__(self):
        self.subscriptions: Dict[str, PWASubscription] = {}
        self.notification_queue: List[PWANotification] = []
        self.is_running = False

    async def start_service(self):
        """Start PWA service"""
        self.is_running = True
        # Start background tasks
        asyncio.create_task(self._process_notification_queue())

    async def stop_service(self):
        """Stop PWA service"""
        self.is_running = False

    async def register_subscription(
        self,
        user_id: str,
        organization_id: str,
        subscription_data: Dict[str, Any]
    ) -> bool:
        """Register a new push subscription"""

        try:
            subscription = PWASubscription(
                user_id=user_id,
                organization_id=organization_id,
                endpoint=subscription_data["endpoint"],
                p256dh_key=subscription_data["keys"]["p256dh"],
                auth_key=subscription_data["keys"]["auth"],
                user_agent=subscription_data.get("userAgent", ""),
                created_at=datetime.utcnow(),
                last_used=datetime.utcnow()
            )

            subscription_key = f"{user_id}_{organization_id}"
            self.subscriptions[subscription_key] = subscription

            logger.info(f"Registered PWA subscription for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register PWA subscription: {e}")
            return False

    async def unregister_subscription(self, user_id: str, organization_id: str) -> bool:
        """Unregister a push subscription"""

        subscription_key = f"{user_id}_{organization_id}"
        if subscription_key in self.subscriptions:
            del self.subscriptions[subscription_key]
            logger.info(f"Unregistered PWA subscription for user {user_id}")
            return True
        return False

    async def send_notification(
        self,
        user_id: str,
        organization_id: str,
        notification: PWANotification
    ) -> bool:
        """Send push notification to user"""

        subscription_key = f"{user_id}_{organization_id}"
        if subscription_key not in self.subscriptions:
            logger.warning(f"No PWA subscription found for user {user_id}")
            return False

        subscription = self.subscriptions[subscription_key]

        try:
            # Add to notification queue for processing
            self.notification_queue.append(notification)

            # Update subscription last used
            subscription.last_used = datetime.utcnow()

            logger.info(f"Queued PWA notification for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send PWA notification: {e}")
            return False

    async def send_notification_to_organization(
        self,
        organization_id: str,
        notification: PWANotification,
        exclude_users: Optional[List[str]] = None
    ) -> int:
        """Send notification to all users in organization"""

        exclude_users = exclude_users or []
        sent_count = 0

        for subscription_key, subscription in self.subscriptions.items():
            if (subscription.organization_id == organization_id and
                subscription.user_id not in exclude_users and
                subscription.is_active):

                success = await self.send_notification(
                    subscription.user_id,
                    organization_id,
                    notification
                )
                if success:
                    sent_count += 1

        return sent_count

    async def _process_notification_queue(self):
        """Background task to process notification queue"""

        while self.is_running:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    await self._send_push_notification(notification)

                await asyncio.sleep(1)  # Process queue every second

            except Exception as e:
                logger.error(f"Error processing notification queue: {e}")
                await asyncio.sleep(5)

    async def _send_push_notification(self, notification: PWANotification):
        """Actually send the push notification"""

        # In a real implementation, this would use a service like:
        # - Firebase Cloud Messaging (FCM)
        # - Mozilla's Web Push Protocol
        # - Apple Push Notification Service (APNs)

        # For now, we'll simulate the notification sending
        logger.info(f"Sending PWA notification: {notification.title}")

        # Simulate network delay
        await asyncio.sleep(0.1)

        return True

    def get_subscription_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get subscription statistics for organization"""

        org_subscriptions = [
            sub for sub in self.subscriptions.values()
            if sub.organization_id == organization_id
        ]

        active_count = len([sub for sub in org_subscriptions if sub.is_active])
        total_count = len(org_subscriptions)

        return {
            "total_subscriptions": total_count,
            "active_subscriptions": active_count,
            "inactive_subscriptions": total_count - active_count,
            "last_24h": len([
                sub for sub in org_subscriptions
                if sub.last_used > datetime.utcnow() - timedelta(days=1)
            ]),
            "last_7d": len([
                sub for sub in org_subscriptions
                if sub.last_used > datetime.utcnow() - timedelta(days=7)
            ])
        }

    def create_deal_notification(
        self,
        deal_id: str,
        deal_title: str,
        action: str,
        actor_name: str
    ) -> PWANotification:
        """Create a deal-related notification"""

        return PWANotification(
            title=f"Deal Update: {deal_title}",
            body=f"{actor_name} {action} the deal",
            icon="/static/icons/deal-notification.png",
            badge="/static/icons/badge.png",
            tag=f"deal_{deal_id}",
            data={
                "type": "deal_update",
                "deal_id": deal_id,
                "action": action,
                "url": f"/deals/{deal_id}"
            },
            actions=[
                {
                    "action": NotificationAction.OPEN_DEAL,
                    "title": "Open Deal",
                    "icon": "/static/icons/open.png"
                },
                {
                    "action": NotificationAction.MARK_READ,
                    "title": "Mark Read",
                    "icon": "/static/icons/check.png"
                }
            ],
            timestamp=datetime.utcnow(),
            vibrate=[200, 100, 200]
        )

    def create_document_notification(
        self,
        document_id: str,
        document_name: str,
        action: str,
        actor_name: str
    ) -> PWANotification:
        """Create a document-related notification"""

        return PWANotification(
            title=f"Document: {document_name}",
            body=f"{actor_name} {action} the document",
            icon="/static/icons/document-notification.png",
            badge="/static/icons/badge.png",
            tag=f"document_{document_id}",
            data={
                "type": "document_update",
                "document_id": document_id,
                "action": action,
                "url": f"/documents/{document_id}"
            },
            actions=[
                {
                    "action": NotificationAction.OPEN_DOCUMENT,
                    "title": "Open Document",
                    "icon": "/static/icons/open.png"
                },
                {
                    "action": NotificationAction.APPROVE,
                    "title": "Approve",
                    "icon": "/static/icons/approve.png"
                }
            ],
            timestamp=datetime.utcnow()
        )


# Global PWA service instance
pwa_service: Optional[PWAService] = None

def get_pwa_service() -> PWAService:
    """Get the global PWA service instance"""
    global pwa_service
    if pwa_service is None:
        pwa_service = PWAService()
    return pwa_service