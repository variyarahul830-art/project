# Chat Session Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Next.js Frontend                         │  │
│  │                                                              │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │         ChatInterface Component                        │ │  │
│  │  │  ┌──────────────────┐  ┌──────────────────────────┐  │ │  │
│  │  │  │  Session Sidebar │  │   Message Display Area  │  │ │  │
│  │  │  │                  │  │                          │  │ │  │
│  │  │  │ - New Chat Btn   │  │ - User messages (dark)  │  │ │  │
│  │  │  │ - Session List   │  │ - AI messages (light)   │  │ │  │
│  │  │  │ - Edit/Delete    │  │ - Timestamps            │  │ │  │
│  │  │  │ - Message Count  │  │ - Auto-scroll           │  │ │  │
│  │  │  └──────────────────┘  ├──────────────────────────┤  │ │  │
│  │  │                         │   Input Form            │  │ │  │
│  │  │                         │   - Text input          │  │ │  │
│  │  │                         │   - Send button         │  │ │  │
│  │  │                         └──────────────────────────┘  │ │  │
│  │  └────────────────────────────────────────────────────────┘ │  │
│  │                           ↓                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │      useChatHistory Custom Hook                        │ │  │
│  │  │                                                        │ │  │
│  │  │  State:                Functions:                     │ │  │
│  │  │  - sessions            - createSession()             │ │  │
│  │  │  - currentSession      - loadSession()               │ │  │
│  │  │  - messages            - saveMessage()               │ │  │
│  │  │  - loading             - deleteSession()             │ │  │
│  │  │  - error               - updateSession()             │ │  │
│  │  │                        - clearMessages()              │ │  │
│  │  │                        - loadAllSessions()            │ │  │
│  │  └────────────────────────────────────────────────────────┘ │  │
│  │                           ↓                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │       Hasura GraphQL Service                           │ │  │
│  │  │  (frontend/app/services/hasura.js)                    │ │  │
│  │  │                                                        │ │  │
│  │  │  - createChatSession()                                │ │  │
│  │  │  - getUserChatSessions()                              │ │  │
│  │  │  - getChatMessages()                                  │ │  │
│  │  │  - addChatMessage()                                   │ │  │
│  │  │  - updateChatSession()                                │ │  │
│  │  │  - deleteChatSession()                                │ │  │
│  │  │  - clearChatMessages()                                │ │  │
│  │  └────────────────────────────────────────────────────────┘ │  │
│  └────────────────┬───────────────────────────────────────────┘  │
│                   │ HTTP POST/GET                                 │
└───────────────────┼─────────────────────────────────────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Hasura GraphQL Engine   │
        │  (Port: 8081)            │
        │                          │
        │  - Execute queries       │
        │  - Execute mutations     │
        │  - Manage permissions    │
        │  - Connect to DB         │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────────────┐
        │   PostgreSQL Database            │
        │   (Port: 5433)                   │
        │                                  │
        │  ┌────────────────────────────┐ │
        │  │   chat_sessions Table      │ │
        │  │                            │ │
        │  │  - id (PK)                 │ │
        │  │  - session_id (UNQ)        │ │
        │  │  - user_id (IDX)           │ │
        │  │  - title                   │ │
        │  │  - category                │ │
        │  │  - total_messages          │ │
        │  │  - is_active               │ │
        │  │  - created_at (IDX)        │ │
        │  │  - updated_at              │ │
        │  └────────────────────────────┘ │
        │                                  │
        │  ┌────────────────────────────┐ │
        │  │   chat_messages Table      │ │
        │  │                            │ │
        │  │  - id (PK)                 │ │
        │  │  - message_id (UNQ)        │ │
        │  │  - session_id (FK, IDX)    │ │
        │  │  - user_id (IDX)           │ │
        │  │  - role                    │ │
        │  │  - content                 │ │
        │  │  - timestamp (IDX)         │ │
        │  └────────────────────────────┘ │
        └────────────────────────────────┘
```

---

## Backend API Architecture

```
┌────────────────────────────────────────────────────────┐
│            FastAPI Backend                             │
│            (Port: 8000)                                │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  main.py                                         │ │
│  │  - CORS configuration                           │ │
│  │  - Router registration                          │ │
│  │  ├── chat.py router                             │ │
│  │  ├── pdf.py router                              │ │
│  │  └── chat_sessions.py router ← NEW             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  routes/chat_sessions.py ← NEW                  │ │
│  │                                                  │ │
│  │  POST   /create                                 │ │
│  │  GET    /user/{user_id}                         │ │
│  │  GET    /{session_id}                           │ │
│  │  GET    /{session_id}/messages                  │ │
│  │  POST   /{session_id}/messages                  │ │
│  │  PUT    /{session_id}                           │ │
│  │  DELETE /{session_id}                           │ │
│  │  DELETE /{session_id}/messages                  │ │
│  └──────────────────────────────────────────────────┘ │
│                           ↓                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │  services/hasura_client.py                      │ │
│  │                                                  │ │
│  │  ✓ create_chat_session()                        │ │
│  │  ✓ get_user_chat_sessions()                     │ │
│  │  ✓ get_chat_session()                           │ │
│  │  ✓ get_chat_messages()                          │ │
│  │  ✓ add_chat_message()                           │ │
│  │  ✓ update_chat_session()                        │ │
│  │  ✓ delete_chat_session()                        │ │
│  │  ✓ clear_chat_messages()                        │ │
│  │  ✓ update_session_message_count()               │ │
│  └──────────────────────────────────────────────────┘ │
│                           ↓                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Hasura GraphQL Execution                       │ │
│  │  - Query execution                              │ │
│  │  - Mutation execution                           │ │
│  │  - Response handling                            │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Data Flow: Create Session

```
User clicks "New Chat"
        ↓
  handleNewChat()
        ↓
  createSession(title)
        ↓
  useChatHistory hook
        ↓
  hasura.createChatSession()
        ↓
  GraphQL Mutation:
  mutation CreateChatSession {
    insert_chat_sessions_one(
      object: {...}
    ) { session_id ... }
  }
        ↓
  Hasura GraphQL Engine
        ↓
  PostgreSQL INSERT
        ↓
  Return session_id
        ↓
  Update React state
        ↓
  UI renders new session
```

---

## Data Flow: Send Message

```
User types & sends message
        ↓
  handleSendMessage()
        ↓
  saveMessage('user', content)
        ↓
  useChatHistory hook
        ↓
  hasura.addChatMessage()
        ↓
  GraphQL Mutation:
  mutation AddMessage {
    insert_chat_messages_one(...) {
      id, timestamp, ...
    }
  }
        ↓
  Hasura GraphQL Engine
        ↓
  PostgreSQL INSERT
        ↓
  Update session.total_messages
        ↓
  Return message object
        ↓
  Update React state
        ↓
  Message appears in UI
        ↓
(Optional) Call /api/chat for AI
        ↓
(Optional) Save AI response as message
```

---

## Component Hierarchy

```
App
 └── ChatInterface
      ├── Sidebar
      │    ├── SidebarHeader
      │    ├── NewChatSection
      │    └── SessionsList
      │         └── SessionItem (×n)
      │              ├── SessionContent
      │              └── SessionActions
      │
      └── ChatArea
           ├── SessionHeader
           ├── MessagesContainer
           │    └── Message (×n)
           │         └── MessageBubble
           │
           ├── InputForm
           │    ├── MessageInput
           │    └── SendButton
           │
           └── ErrorDisplay (if error)
```

---

## Database Schema Relationships

```
┌─────────────────────────────────────────────────────────┐
│                  chat_sessions                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ PK: id                                             │ │
│  │ UQ: session_id ──────────────────────┐            │ │
│  │ IDX: user_id                         │ (1:N)      │ │
│  │ IDX: created_at                      │            │ │
│  │ IDX: is_active                       │            │ │
│  │ title, category, total_messages      │            │ │
│  │ is_active, timestamps                │            │ │
│  └────────────────────────────────────────┼──────────┘ │
│                                           │            │
└──────────────────────────────────────────┼────────────┘
                                           │
                                    ┌──────▼──────────────┐
                                    │  chat_messages      │
                                    │  ┌────────────────┐ │
                                    │  │ PK: id         │ │
                                    │  │ UQ: message_id │ │
                                    │  │ FK: session_id │ │
                                    │  │ IDX: user_id   │ │
                                    │  │ IDX: timestamp │ │
                                    │  │                │ │
                                    │  │ role, content  │ │
                                    │  └────────────────┘ │
                                    └────────────────────┘
```

---

## Technology Stack

```
Frontend          Backend           Database          Infrastructure
─────────────────────────────────────────────────────────────────────
Next.js 13        FastAPI           PostgreSQL 15     Docker
React 18          Python 3.8+       Hasura 2.0+       Docker Compose
JavaScript ES6    SQLAlchemy        pgAdmin           
TailwindCSS       httpx             Milvus (existing) 
                  Pydantic          MinIO (existing)  
```

---

## File Organization

```
project/
│
├── backend/
│   ├── main.py (modified)
│   ├── routes/
│   │   ├── chat.py
│   │   ├── pdf.py
│   │   └── chat_sessions.py (NEW)
│   └── services/
│       └── hasura_client.py (modified)
│
├── frontend/
│   └── app/
│       ├── services/
│       │   └── hasura.js (modified)
│       ├── hooks/
│       │   └── useChatHistory.js (NEW)
│       └── components/
│           ├── ChatInterface.jsx (NEW)
│           └── ChatInterface.module.css (NEW)
│
├── hasura_schema.sql (modified)
│
└── Documentation/
    ├── QUICK_START_CHAT_SESSIONS.md
    ├── CHAT_SESSION_SUMMARY.md
    ├── CHAT_SESSION_INTEGRATION.md
    ├── CHAT_SESSION_IMPLEMENTATION.md
    ├── CHANGELOG_CHAT_SESSIONS.md
    └── IMPLEMENTATION_COMPLETE.md (this file)
```

---

## State Management Flow

```
ChatInterface (Local State)
    ↓
useChatHistory Hook
    ├── sessions (useState)
    ├── currentSession (useState)
    ├── messages (useState)
    ├── loading (useState)
    ├── error (useState)
    └── useEffect (load on mount)
         ↓
    Hasura GraphQL
         ↓
    PostgreSQL

User Interactions → Hook Functions → State Updates → Component Re-render
```

---

## Security Layers

```
Frontend              Backend               Database
──────────────────────────────────────────────────────
Input validation      Input validation      Row-level
                      User isolation        security policies
Error handling        Error handling        
                      Rate limiting         SQL injection
User auth check       Auth verification     prevention
                      CORS policies         
HTTPS/TLS            HTTPS/TLS             Encrypted
                                           connections
```

---

## Performance Optimization

```
Database Level:
├── Indexes on frequently queried fields
├── Denormalized total_messages count
├── Soft deletes (no expensive deletes)
└── Partitioning (future)

Backend Level:
├── Async/await for non-blocking ops
├── Connection pooling (Hasura)
├── Query result caching (optional)
└── Pagination (future)

Frontend Level:
├── React.memo for components
├── useCallback for functions
├── Virtual scrolling (future)
└── Lazy loading messages
```

---

## Monitoring & Logging

```
PostgreSQL Logs
    ↓
Monitor Query Performance
    ↓
Check Slow Queries
    ↓
Analyze Index Usage

Backend Logs
    ↓
Log API Requests/Responses
    ↓
Track Errors
    ↓
Monitor Performance

Frontend Console
    ↓
Monitor GraphQL Requests
    ↓
Check JavaScript Errors
    ↓
Track User Actions
```

---

**This architecture provides:**
- ✅ Scalability
- ✅ Security
- ✅ Performance
- ✅ Maintainability
- ✅ Extensibility
