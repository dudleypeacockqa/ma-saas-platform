"""
Simple FastAPI app for testing PWA functionality
This bypasses complex dependencies and focuses on core WebSocket features
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from datetime import datetime

# Import WebSocket manager
from app.websockets.websocket_manager import websocket_manager

# Initialize FastAPI app
app = FastAPI(
    title="M&A SaaS Platform - PWA Test",
    description="Simplified API for testing PWA and WebSocket functionality",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app for real-time communication
socket_app = socketio.ASGIApp(websocket_manager.sio, other_asgi_app=app, socketio_path='/socket.io')

@app.get("/")
async def root():
    return {
        "message": "M&A SaaS Platform PWA Test API",
        "status": "running",
        "version": "1.0.0",
        "websocket": "enabled",
        "documentation": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_enabled": True
    }

# WebSocket status endpoints
@app.get("/api/websocket/status")
async def websocket_status():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_stats()

@app.get("/api/websocket/activity/{organization_id}")
async def websocket_activity(organization_id: str):
    """Get user activity for an organization"""
    return websocket_manager.get_user_activity(organization_id)

# Simple test endpoints
@app.post("/api/test/notification")
async def test_notification(data: dict):
    """Test endpoint to send notifications"""
    from app.websockets.websocket_manager import NotificationData

    notification = NotificationData(
        id=f"test_{datetime.now().timestamp()}",
        type="system",
        title=data.get("title", "Test Notification"),
        message=data.get("message", "This is a test notification"),
        organization_id=data.get("organization_id", "test_org"),
        priority="medium"
    )

    await websocket_manager.send_notification(notification)
    return {"message": "Notification sent", "notification_id": notification.id}

@app.post("/api/test/deal-update")
async def test_deal_update(data: dict):
    """Test endpoint to broadcast deal updates"""
    deal_id = data.get("deal_id", "test_deal")
    updates = data.get("updates", {"stage": "negotiation", "value": 1000000})
    user_id = data.get("user_id", "test_user")

    await websocket_manager.broadcast_deal_update(deal_id, updates, user_id)
    return {"message": "Deal update broadcasted", "deal_id": deal_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)