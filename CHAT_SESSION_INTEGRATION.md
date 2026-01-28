# Integration Guide: Chat Sessions with Existing Chat API

This guide shows how to integrate the new chat session history feature with your existing chat API.

## Architecture Overview

```
Frontend (ChatInterface Component)
    ↓
    ├── Session Management (useChatHistory hook)
    │   └── /api/chat-sessions/* (CRUD operations)
    │       └── Hasura GraphQL (PostgreSQL)
    │
    └── Chat Logic (/api/chat)
        ├── Search knowledge graph
        ├── Search FAQs
        └── RAG with LLM
```

## Complete Chat Flow with Session Storage

### Step 1: User Creates or Selects Session
```javascript
// In ChatInterface component
const handleNewChat = async () => {
  const sessionId = await createSession('New Chat');
  // sessionId is now ready for messages
};

const handleSelectSession = (sessionId) => {
  loadSession(sessionId); // Loads all previous messages
};
```

### Step 2: User Sends Message
```javascript
const handleSendMessage = async (e) => {
  e.preventDefault();
  
  // 1. Save user message to session
  await saveMessage('user', userMessage);
  
  // 2. Call existing chat API for response
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question: userMessage,
      workflow_id: null // or specific workflow
    })
  });
  
  const data = await response.json();
  
  // 3. Save AI response to session
  await saveMessage('assistant', data.answer);
  
  // 4. UI updates automatically via state
};
```

## Implementation Options

### Option A: Use ChatInterface Component (Recommended)

The easiest way - use the provided component directly:

```jsx
// pages/chat.jsx
import ChatInterface from '@/components/ChatInterface';

export default function ChatPage() {
  return <ChatInterface userId={getCurrentUserId()} />;
}
```

Modify the `handleSendMessage` in `ChatInterface.jsx` to call your AI:

```jsx
const handleSendMessage = async (e) => {
  e.preventDefault();
  if (!inputValue.trim() || !currentSession) return;

  const userMessage = inputValue;
  setInputValue('');

  // Save user message
  await saveMessage('user', userMessage);

  try {
    // Call your existing chat API
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: userMessage })
    });

    const data = await response.json();

    // Save AI response
    if (data.success && data.answer) {
      await saveMessage('assistant', data.answer);
    }
  } catch (error) {
    console.error('Chat error:', error);
  }
};
```

### Option B: Use Hook in Custom Component

Build your own chat UI using the hook:

```jsx
import { useChatHistory } from '@/hooks/useChatHistory';

export default function CustomChat() {
  const { currentSession, messages, saveMessage } = useChatHistory(userId);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    // Save user message
    await saveMessage('user', input);

    // Get AI response
    const aiResponse = await getAIResponse(input);
    
    // Save response
    await saveMessage('assistant', aiResponse);
    
    setInput('');
  };

  return (
    <div>
      {/* Your custom UI */}
      {messages.map(msg => (
        <div key={msg.id} className={msg.role}>
          {msg.content}
        </div>
      ))}
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

## Connecting to Your Existing Chat API

### Update Chat Route to Use Sessions

Optionally, you can modify your backend chat route to accept session_id:

```python
# backend/routes/chat.py
from schemas import ChatRequest
from services import hasura_client

@router.post("/", response_model=dict)
async def chat(request: ChatRequest):
    """
    Enhanced chat endpoint with optional session tracking
    """
    try:
        # ... existing chat logic ...
        answer = llm_service.generate_answer_with_context(
            question=request.question,
            context_chunks=similar_chunks
        )
        
        # Optionally save to session if session_id provided
        if hasattr(request, 'session_id') and request.session_id:
            await hasura_client.add_chat_message(
                message_id=f"msg_{uuid.uuid4()}",
                session_id=request.session_id,
                user_id=request.user_id,
                role="assistant",
                content=answer
            )
        
        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "source": "rag"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Update ChatRequest Schema

```python
# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    workflow_id: Optional[int] = None
    session_id: Optional[str] = None  # New field
    user_id: Optional[str] = None     # New field
```

## Complete Example: Full Chat Page

```jsx
'use client';

import { useState, useEffect } from 'react';
import { useChatHistory } from '@/hooks/useChatHistory';
import styles from './page.module.css';

export default function ChatPage() {
  const userId = 'user123'; // Get from auth
  
  const {
    sessions,
    currentSession,
    messages,
    loading,
    createSession,
    loadSession,
    saveMessage
  } = useChatHistory(userId);

  const [input, setInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    if (!currentSession && sessions.length === 0) {
      createSession('Welcome Chat');
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim() || !currentSession) return;

    const userMessage = input;
    setInput('');

    // Save user message
    await saveMessage('user', userMessage);

    setAiLoading(true);
    try {
      // Call existing chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage,
          session_id: currentSession,
          user_id: userId
        })
      });

      const data = await response.json();

      if (data.success) {
        // Save AI response
        await saveMessage('assistant', data.answer);
      }
    } catch (error) {
      console.error('Error:', error);
      await saveMessage('assistant', 'Sorry, there was an error processing your request.');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <button onClick={() => createSession('New Chat')}>+ New Chat</button>
        <ul>
          {sessions.map(s => (
            <li key={s.session_id}>
              <button
                onClick={() => loadSession(s.session_id)}
                className={currentSession === s.session_id ? styles.active : ''}
              >
                {s.title}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main Chat */}
      <main className={styles.main}>
        <div className={styles.messages}>
          {messages.map(msg => (
            <div key={msg.message_id} className={`${styles.msg} ${styles[msg.role]}`}>
              <p>{msg.content}</p>
            </div>
          ))}
        </div>

        <form onSubmit={e => { e.preventDefault(); handleSend(); }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type message..."
            disabled={loading || aiLoading}
          />
          <button type="submit" disabled={!input.trim() || aiLoading}>
            {aiLoading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </main>
    </div>
  );
}
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│              (ChatInterface Component)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
        ┌───────────▼────────┐   ┌────▼──────────────┐
        │ Session Management │   │  Chat API Calls   │
        │ (useChatHistory)   │   │  (/api/chat)      │
        └───────────┬────────┘   └────┬──────────────┘
                    │                 │
        ┌───────────▼────────┐   ┌────▼──────────────┐
        │  /api/chat-        │   │ Knowledge Graph   │
        │  sessions/*        │   │ FAQ Search        │
        │  (REST API)        │   │ RAG + LLM         │
        └───────────┬────────┘   └───────────────────┘
                    │
        ┌───────────▼────────┐
        │  Hasura GraphQL    │
        │  (Mutations/       │
        │   Queries)         │
        └───────────┬────────┘
                    │
        ┌───────────▼────────┐
        │   PostgreSQL DB    │
        │ (chat_sessions,    │
        │  chat_messages)    │
        └────────────────────┘
```

## Testing the Integration

### 1. Create Session & Send Message
```bash
# Create session
curl -X POST http://localhost:8000/api/chat-sessions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user1","title":"Test"}'

# Get session_id from response

# Send chat message via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Python?","session_id":"session_xyz"}'

# Add response to session
curl -X POST http://localhost:8000/api/chat-sessions/session_xyz/messages \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user1","role":"assistant","content":"Python is..."}'
```

### 2. View Session History
```bash
curl http://localhost:8000/api/chat-sessions/session_xyz/messages
```

## Troubleshooting

### Messages Not Saving
- Check if session exists: `GET /api/chat-sessions/user/{userId}`
- Verify session_id format
- Check Hasura/PostgreSQL logs

### Hook State Not Updating
- Ensure userId is valid
- Check browser console for errors
- Verify Hasura URL in environment variables

### GraphQL Errors
- Check Hasura admin secret
- Verify tables created in database
- Check Hasura permissions/roles

## Performance Tips

1. **Pagination** - Add limit/offset for large message counts
2. **Caching** - Cache session list with 30s TTL
3. **Lazy Loading** - Load messages on demand
4. **Compression** - Compress message content for storage

## Security Considerations

1. **User Verification** - Always verify user_id matches token
2. **Rate Limiting** - Limit messages per session/user
3. **Data Validation** - Validate all inputs
4. **Access Control** - Only return user's own sessions
