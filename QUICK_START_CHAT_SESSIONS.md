# Quick Start: Chat Sessions Feature

## What Was Added?

A complete **session-wise chat history** system using:
- ✅ PostgreSQL with Hasura GraphQL
- ✅ Two tables: `chat_sessions` & `chat_messages`
- ✅ REST API endpoints for session management
- ✅ React hook for easy integration
- ✅ Pre-built UI component (ChatInterface)

---

## 5-Minute Setup

### 1. Apply Database Schema
The schema is already added to `hasura_schema.sql`. Run Hasura migrations:

```bash
# Via Hasura CLI
hasura migrate apply

# Or via Hasura Console (http://localhost:8081)
# Upload the SQL file
```

### 2. Restart Backend
```bash
cd backend
uvicorn main:app --reload
```

### 3. Use in Your App

**Option A: Drop-in Component**
```jsx
import ChatInterface from '@/components/ChatInterface';

export default function Chat() {
  return <ChatInterface userId="current-user-id" />;
}
```

**Option B: Custom Implementation**
```jsx
import { useChatHistory } from '@/hooks/useChatHistory';

export default function MyChat() {
  const { sessions, currentSession, messages, createSession, saveMessage } 
    = useChatHistory('user123');

  return (
    // Your custom UI using the hook
  );
}
```

---

## API Endpoints (Quick Reference)

```
POST   /api/chat-sessions/create
GET    /api/chat-sessions/user/:userId
GET    /api/chat-sessions/:sessionId
GET    /api/chat-sessions/:sessionId/messages
POST   /api/chat-sessions/:sessionId/messages
PUT    /api/chat-sessions/:sessionId
DELETE /api/chat-sessions/:sessionId
DELETE /api/chat-sessions/:sessionId/messages
```

---

## Testing

### Create a Chat Session
```bash
curl -X POST http://localhost:8000/api/chat-sessions/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "My First Chat",
    "category": "General"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "session_id": "session_1234567890_abc123",
    "title": "My First Chat",
    "total_messages": 0,
    ...
  }
}
```

### Add a Message
```bash
curl -X POST http://localhost:8000/api/chat-sessions/session_1234567890_abc123/messages \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "role": "user",
    "content": "Hello, how are you?"
  }'
```

### Get All Sessions for User
```bash
curl http://localhost:8000/api/chat-sessions/user/user123
```

### Get Messages in Session
```bash
curl http://localhost:8000/api/chat-sessions/session_1234567890_abc123/messages
```

---

## Files Added/Modified

### New Files
- ✅ `backend/routes/chat_sessions.py` - API endpoints
- ✅ `frontend/app/hooks/useChatHistory.js` - React hook
- ✅ `frontend/app/components/ChatInterface.jsx` - UI component
- ✅ `frontend/app/components/ChatInterface.module.css` - Styling
- ✅ `CHAT_SESSION_IMPLEMENTATION.md` - Full documentation
- ✅ `CHAT_SESSION_SUMMARY.md` - Summary
- ✅ `CHAT_SESSION_INTEGRATION.md` - Integration guide

### Modified Files
- ✅ `hasura_schema.sql` - Added 2 tables
- ✅ `backend/main.py` - Added router import
- ✅ `backend/services/hasura_client.py` - Added 9 functions
- ✅ `frontend/app/services/hasura.js` - Added 10 functions

---

## Architecture at a Glance

```
ChatInterface Component
        ↓
    useChatHistory Hook
        ↓
  Hasura GraphQL
        ↓
   PostgreSQL
   - chat_sessions
   - chat_messages
```

---

## Hook Usage Reference

```javascript
import { useChatHistory } from '@/hooks/useChatHistory';

const {
  // State
  sessions,        // All user's sessions
  currentSession,  // Current session ID
  messages,        // Messages in current session
  loading,         // Loading state
  error,           // Error messages

  // Methods
  createSession,   // (title?, category?) => sessionId
  loadSession,     // (sessionId) => void
  saveMessage,     // (role, content) => void
  deleteSession,   // (sessionId) => void
  updateSession,   // (sessionId, title, category) => void
  clearMessages,   // (sessionId) => void
  loadAllSessions  // () => void
} = useChatHistory(userId);
```

---

## Integration with AI Chat

To connect messages with your AI API:

```jsx
const handleSendMessage = async (userMessage) => {
  // Save user message
  await saveMessage('user', userMessage);

  // Call your AI API
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ question: userMessage })
  });
  const data = await response.json();

  // Save AI response
  await saveMessage('assistant', data.answer);
};
```

---

## Database Schema Summary

**chat_sessions table:**
```sql
id (PRIMARY KEY)
session_id (UNIQUE)
user_id (indexed)
title
category
total_messages
is_active (soft delete)
created_at
updated_at
```

**chat_messages table:**
```sql
id (PRIMARY KEY)
message_id (UNIQUE)
session_id (FOREIGN KEY, indexed)
user_id (indexed)
role ('user' or 'assistant')
content (TEXT)
timestamp (indexed)
```

---

## Common Tasks

### Display Sessions in UI
```jsx
{sessions.map(session => (
  <button key={session.session_id} onClick={() => loadSession(session.session_id)}>
    {session.title} ({session.total_messages} messages)
  </button>
))}
```

### Display Messages
```jsx
{messages.map(msg => (
  <div key={msg.message_id} className={msg.role}>
    {msg.content}
    <small>{new Date(msg.timestamp).toLocaleTimeString()}</small>
  </div>
))}
```

### Create New Session
```jsx
const newSessionId = await createSession('Important Discussion');
```

### Send Message
```jsx
await saveMessage('user', 'What is the weather?');
```

---

## Environment Setup

Add to `frontend/.env.local`:
```
NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
NEXT_PUBLIC_HASURA_ADMIN_SECRET=myadminsecret
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Session not found" | Verify session_id exists via GET /api/chat-sessions/user/{userId} |
| Messages not saving | Check Hasura GraphQL errors in browser console |
| Hook not updating | Ensure userId is valid and consistent |
| 404 on endpoints | Restart backend after adding routes |
| GraphQL errors | Check PostgreSQL is running, tables exist |

---

## Next Steps

1. ✅ Apply database schema
2. ✅ Restart backend
3. ✅ Test API endpoints with curl
4. ✅ Add ChatInterface component to your app
5. ✅ Connect to AI API
6. ✅ Customize styling as needed

---

## Documentation Files

For detailed information, refer to:
- 📖 `CHAT_SESSION_IMPLEMENTATION.md` - Complete technical details
- 📖 `CHAT_SESSION_INTEGRATION.md` - Integration examples
- 📖 `CHAT_SESSION_SUMMARY.md` - Overview of changes

---

## Support

### API Documentation
- All endpoints documented in `backend/routes/chat_sessions.py`
- GraphQL queries in `frontend/app/services/hasura.js`

### Component Props
- ChatInterface accepts `userId` prop
- useChatHistory hook returns 13 items

### Examples
See `CHAT_SESSION_INTEGRATION.md` for complete examples

---

**You're all set! Start using chat sessions in your app now! 🚀**
