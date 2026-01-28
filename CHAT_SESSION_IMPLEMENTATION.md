# Chat Session History Implementation Guide

## Overview
This implementation provides session-wise chat history storage using Hasura GraphQL and PostgreSQL. Users can create multiple chat sessions, view chat history session-wise, and manage their conversations.

## Architecture

### Database Schema (PostgreSQL)

#### Tables

**1. chat_sessions**
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) DEFAULT 'New Chat Session',
    category VARCHAR(255) DEFAULT 'General',
    total_messages INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**2. chat_messages**
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL UNIQUE,
    session_id VARCHAR(255) NOT NULL REFERENCES chat_sessions(session_id),
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Key Features

1. **Two Table Design**
   - `chat_sessions`: Stores session metadata
   - `chat_messages`: Stores individual messages with session reference

2. **Soft Deletes**
   - Sessions are marked inactive (not permanently deleted)
   - Allows audit trail and potential recovery

3. **Message Tracking**
   - Auto-incremented message count per session
   - Indexed for fast queries

4. **Timestamps**
   - Created and updated timestamps for audit
   - Message timestamps for conversation flow

---

## Backend Implementation

### 1. Database Operations (`backend/services/hasura_client.py`)

Functions added:
- `create_chat_session()` - Create new session
- `get_user_chat_sessions()` - Get all sessions for user
- `get_chat_session()` - Get specific session
- `get_chat_messages()` - Get messages in session
- `add_chat_message()` - Add message to session
- `update_chat_session()` - Update session title/category
- `delete_chat_session()` - Soft delete session
- `clear_chat_messages()` - Delete all messages in session
- `update_session_message_count()` - Auto-update message count

### 2. API Routes (`backend/routes/chat_sessions.py`)

**Endpoints:**

```
POST   /api/chat-sessions/create              - Create new session
GET    /api/chat-sessions/user/{user_id}     - Get user's sessions
GET    /api/chat-sessions/{session_id}       - Get session details
GET    /api/chat-sessions/{session_id}/messages - Get messages
POST   /api/chat-sessions/{session_id}/messages - Add message
PUT    /api/chat-sessions/{session_id}       - Update session
DELETE /api/chat-sessions/{session_id}       - Delete session
DELETE /api/chat-sessions/{session_id}/messages - Clear messages
```

### 3. Request/Response Examples

**Create Session:**
```bash
curl -X POST http://localhost:8000/api/chat-sessions/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Python Discussion",
    "category": "Programming"
  }'
```

**Add Message:**
```bash
curl -X POST http://localhost:8000/api/chat-sessions/session_123/messages \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "role": "user",
    "content": "How do I use async/await in Python?"
  }'
```

---

## Frontend Implementation

### 1. GraphQL Service (`frontend/app/services/hasura.js`)

Functions added:
- `createChatSession()` - Create session via GraphQL
- `getUserChatSessions()` - Query user sessions
- `getChatSession()` - Query specific session
- `getChatMessages()` - Query session messages
- `addChatMessage()` - Mutate add message
- `updateChatSession()` - Mutate update session
- `deleteChatSession()` - Mutate delete session
- `clearChatMessages()` - Mutate clear messages

### 2. Custom Hook (`frontend/app/hooks/useChatHistory.js`)

React hook providing:
```javascript
const {
  sessions,           // Array of chat sessions
  currentSession,     // Current session ID
  messages,          // Messages in current session
  loading,           // Loading state
  error,             // Error messages
  createSession,     // Function to create new session
  loadSession,       // Function to load session messages
  loadAllSessions,   // Function to load user's sessions
  saveMessage,       // Function to add message
  deleteSession,     // Function to delete session
  updateSession,     // Function to update session
  clearMessages      // Function to clear session messages
} = useChatHistory(userId);
```

### 3. UI Components

**ChatInterface Component** (`frontend/app/components/ChatInterface.jsx`)

Features:
- Sidebar with session list
- New chat creation
- Session editing
- Message display with roles
- Auto-scroll to latest message
- Error handling
- Loading states

**Styling** (`frontend/app/components/ChatInterface.module.css`)

- Professional design with formal colors
- Responsive layout (mobile-friendly)
- Dark/light mode support for messages
- Smooth animations

---

## Usage Example

### Setting up in Your App

```jsx
import ChatInterface from '@/components/ChatInterface';

export default function ChatPage() {
  return <ChatInterface userId="user123" />;
}
```

### Using the Hook Directly

```jsx
import { useChatHistory } from '@/hooks/useChatHistory';

function MyChat() {
  const { sessions, currentSession, createSession, saveMessage } = useChatHistory('user123');

  return (
    <div>
      <button onClick={() => createSession('New Chat')}>New Session</button>
      <button onClick={() => saveMessage('user', 'Hello!')}>Send</button>
    </div>
  );
}
```

---

## Hasura GraphQL Integration

### Queries

```graphql
# Get all sessions for user
query GetUserSessions($userId: String!) {
  chat_sessions(where: {user_id: {_eq: $userId}, is_active: {_eq: true}}) {
    session_id
    title
    total_messages
    updated_at
  }
}

# Get messages in session
query GetMessages($sessionId: String!) {
  chat_messages(where: {session_id: {_eq: $sessionId}}, order_by: {timestamp: asc}) {
    message_id
    role
    content
    timestamp
  }
}
```

### Mutations

```graphql
# Create session
mutation CreateSession($sessionId: String!, $userId: String!) {
  insert_chat_sessions_one(object: {session_id: $sessionId, user_id: $userId}) {
    session_id
  }
}

# Add message
mutation AddMessage($messageId: String!, $sessionId: String!, $role: String!, $content: String!) {
  insert_chat_messages_one(object: {
    message_id: $messageId
    session_id: $sessionId
    role: $role
    content: $content
  }) {
    message_id
    timestamp
  }
}
```

---

## Database Indexes

Indexes for performance:
- `idx_chat_sessions_user_id` - Fast user session lookup
- `idx_chat_sessions_created_at` - Sort by date
- `idx_chat_messages_session_id` - Fast message query
- `idx_chat_messages_timestamp` - Sort by time

---

## Integration with Existing Chat Routes

The new chat session feature works alongside existing chat functionality:

1. **Chat Route** (`/api/chat`) - Handles AI response logic
2. **Chat Session Routes** (`/api/chat-sessions`) - Handles session storage
3. **Hasura GraphQL** - Manages data persistence

### Complete Flow

```
User Input → ChatInterface Component
    ↓
saveMessage() hook → add_chat_message() GraphQL
    ↓
Chat Message saved in DB
    ↓
(Optional) Call /api/chat for AI response
    ↓
Save AI response as message
    ↓
UI updates with new message
```

---

## Security Considerations

1. **User Isolation**: Queries filtered by user_id
2. **Session Ownership**: Verify user_id matches session owner
3. **Soft Deletes**: Data not permanently removed
4. **Indexed Queries**: Fast lookups prevent DoS

---

## Environment Variables

Add to `.env`:
```
NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
NEXT_PUBLIC_HASURA_ADMIN_SECRET=myadminsecret
```

---

## Testing the Feature

### 1. Create a Session
```bash
curl -X POST http://localhost:8000/api/chat-sessions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","title":"Test Chat"}'
```

### 2. Add a Message
```bash
curl -X POST http://localhost:8000/api/chat-sessions/session_123/messages \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","role":"user","content":"Hello!"}'
```

### 3. Get Sessions
```bash
curl http://localhost:8000/api/chat-sessions/user/test_user
```

---

## Future Enhancements

1. **Search Messages** - Full-text search in chat history
2. **Export Chat** - Download chat as PDF/TXT
3. **Sharing** - Share sessions with other users
4. **Reactions** - Add emoji reactions to messages
5. **Archiving** - Archive old sessions
6. **Real-time Updates** - WebSocket for live messaging
