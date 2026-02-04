'use client';

import { useState } from 'react';

export default function DebugChat() {
  const [sessionId, setSessionId] = useState('');
  const [userId, setUserId] = useState('user123');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    const body = {
      question,
      session_id: sessionId || undefined,
      user_id: userId || undefined
    };

    console.log('Sending request:', body);

    try {
      const res = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await res.json();
      console.log('Response:', data);
      setResponse(data);
    } catch (err) {
      console.error('Error:', err);
      setResponse({ error: err.message });
    }
  };

  const checkMessages = async () => {
    try {
      const query = `query{chat_messages(where:{session_id:{_eq:"${sessionId}"}},order_by:{timestamp:desc}){id message_id question answer source timestamp}}`;
      const res = await fetch('http://localhost:8081/v1/graphql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-hasura-admin-secret': 'myadminsecret'
        },
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      console.log('Messages:', data);
      setMessages(data.data?.chat_messages || []);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Chat History Debug Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Send Message</h2>
        <div>
          <label>Session ID: </label>
          <input 
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="test-session-123"
            style={{ width: '300px', padding: '5px' }}
          />
        </div>
        <div>
          <label>User ID: </label>
          <input 
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="user123"
            style={{ width: '300px', padding: '5px' }}
          />
        </div>
        <div>
          <label>Question: </label>
          <input 
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What is git?"
            style={{ width: '300px', padding: '5px' }}
          />
        </div>
        <button onClick={sendMessage} style={{ padding: '10px 20px', marginTop: '10px' }}>
          Send Message
        </button>
      </div>

      {response && (
        <div style={{ marginBottom: '20px', padding: '10px', background: '#f0f0f0' }}>
          <h3>API Response:</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}

      <div>
        <h2>Check Saved Messages</h2>
        <button onClick={checkMessages} style={{ padding: '10px 20px' }}>
          Fetch Messages from Database
        </button>
        
        {messages.length > 0 && (
          <div style={{ marginTop: '10px' }}>
            <h3>Saved Messages ({messages.length}):</h3>
            {messages.map((msg) => (
              <div key={msg.id} style={{ padding: '10px', background: '#e8f4f8', marginBottom: '10px' }}>
                <div><strong>ID:</strong> {msg.message_id}</div>
                <div><strong>Question:</strong> {msg.question}</div>
                <div><strong>Answer:</strong> {msg.answer?.substring(0, 100)}...</div>
                <div><strong>Source:</strong> {msg.source}</div>
                <div><strong>Time:</strong> {msg.timestamp}</div>
              </div>
            ))}
          </div>
        )}
        
        {messages.length === 0 && (
          <div style={{ marginTop: '10px', color: 'red' }}>
            No messages found for this session
          </div>
        )}
      </div>
    </div>
  );
}
