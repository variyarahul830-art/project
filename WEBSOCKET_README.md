# WebSocket Chat Feature

This document describes the WebSocket feature added to the chat system.

## Overview

WebSocket support has been added to enable real-time chat communication between the frontend and backend. Users can toggle between the traditional REST API and WebSocket for their chat experience.

## Backend Changes

### 1. Dependencies
- Added `websockets==12.0` to `requirements.txt`

### 2. New WebSocket Route
- Created `backend/routes/websocket_chat.py`
- Endpoint: `ws://localhost:8000/ws/chat`
- Features:
  - Connection management (multiple clients supported)
  - Same chat logic as REST API (knowledge graph → FAQ → RAG)
  - Automatic reconnection support
  - Session and message persistence

### 3. Main App Update
- Updated `backend/main.py` to include WebSocket router

## Frontend Changes

### 1. WebSocket Client Service
- Created `frontend/app/services/websocket.js`
- Features:
  - Singleton WebSocket client
  - Automatic reconnection (up to 5 attempts)
  - Message and status callbacks
  - Connection state management

### 2. ChatBox Component Updates
- Added WebSocket toggle button in header
- Visual indicator for WebSocket status (connected/connecting/error)
- Seamless switching between REST API and WebSocket
- No impact on existing features (all features work with both methods)

## Usage

### For Users

1. **Toggle WebSocket**: Click the toggle button in the chat header
   - `📡 API` - Using REST API (default)
   - `🔌 WS` - Using WebSocket (real-time)

2. **Status Indicator**: When WebSocket is active, you'll see the connection status:
   - `• WebSocket Connected` (green) - Ready to use
   - `• Connecting...` (orange) - Establishing connection
   - `• Connection Error` (red) - Connection failed (auto-switches to REST)

### For Developers

#### Backend WebSocket Message Format

**Client → Server**:
```json
{
  "question": "What is AI?",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

**Server → Client** (Processing):
```json
{
  "type": "processing",
  "message": "Processing your question..."
}
```

**Server → Client** (Response):
```json
{
  "type": "response",
  "success": true,
  "question": "What is AI?",
  "answer": "...",
  "source": "knowledge_graph|faq|rag",
  ...
}
```

#### Installing Dependencies

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend (no new dependencies needed):
```bash
cd frontend
npm install
```

## Testing

### 1. Install Backend Dependencies
```bash
cd backend
pip install websockets==12.0
```

### 2. Start Backend
```bash
cd backend
uvicorn main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

### 4. Test WebSocket
1. Open the chat interface
2. Click the `📡 API` button to switch to `🔌 WS`
3. Verify status shows "WebSocket Connected"
4. Send a message and verify it works the same as REST API

## Features Preserved

All existing features work identically with both REST API and WebSocket:
- ✅ Knowledge graph search
- ✅ FAQ matching
- ✅ RAG (PDF embeddings + LLM)
- ✅ Redis caching
- ✅ Session management
- ✅ Message history
- ✅ User authentication
- ✅ Clickable answers
- ✅ Source tracking

## Advantages of WebSocket

1. **Real-time**: Lower latency for chat messages
2. **Bi-directional**: Server can push updates to client
3. **Efficient**: Single persistent connection instead of multiple HTTP requests
4. **Scalable**: Better for high-frequency messaging

## Fallback Behavior

- If WebSocket connection fails, automatically switches back to REST API
- User sees error message and can continue chatting without interruption
- No data loss - all messages are still saved to database

## Configuration

WebSocket URL is configured in `frontend/app/services/websocket.js`:
```javascript
// Default: ws://localhost:8000/ws/chat
wsClient.connect('ws://localhost:8000/ws/chat');
```

For production, update to your production WebSocket URL.

## Troubleshooting

### WebSocket won't connect
- Check backend is running: `http://localhost:8000/health`
- Verify WebSocket endpoint: `ws://localhost:8000/ws/chat`
- Check browser console for errors
- Ensure firewall allows WebSocket connections

### Messages not saving
- Verify session_id and user_id are being sent
- Check backend logs for database errors
- Ensure Hasura is running and accessible

### Auto-switching to REST
- This is normal if WebSocket fails to connect
- Check backend logs for WebSocket errors
- Verify WebSocket server is properly configured
