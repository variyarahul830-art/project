'use client';

import { useState, useEffect, useRef } from 'react';
import { useChatHistory } from '@/app/hooks/useChatHistory';
import styles from './ChatInterface.module.css';

export default function ChatInterface({ userId = 'user123' }) {
  const {
    sessions,
    currentSession,
    messages,
    loading,
    error,
    createSession,
    loadSession,
    saveMessage,
    deleteSession,
    updateSession,
    clearMessages
  } = useChatHistory(userId);

  const [inputValue, setInputValue] = useState('');
  const [sessionTitle, setSessionTitle] = useState('');
  const [editingSession, setEditingSession] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const messagesEndRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-create first session if none exist
  useEffect(() => {
    if (sessions.length === 0 && !loading && !currentSession) {
      createSession('My First Chat', 'General');
    }
  }, [sessions, loading, currentSession, createSession]);

  const handleNewChat = async () => {
    const title = sessionTitle.trim() || 'New Chat';
    await createSession(title, 'General');
    setSessionTitle('');
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || !currentSession) return;

    const userMessage = inputValue;
    setInputValue('');

    // Save user message
    await saveMessage('user', userMessage);

    // TODO: Call your AI API here
    // const aiResponse = await callAI(userMessage);
    // await saveMessage('assistant', aiResponse);
  };

  const handleDeleteSession = (sessionId) => {
    if (confirm('Are you sure you want to delete this session?')) {
      deleteSession(sessionId);
    }
  };

  const handleEditSession = async (sessionId, currentTitle) => {
    setEditingSession(sessionId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async (sessionId) => {
    if (editTitle.trim()) {
      await updateSession(sessionId, editTitle, 'General');
      setEditingSession(null);
      setEditTitle('');
    }
  };

  const handleClearMessages = (sessionId) => {
    if (confirm('Clear all messages in this session?')) {
      clearMessages(sessionId);
    }
  };

  const currentSessionData = sessions.find(s => s.session_id === currentSession);

  return (
    <div className={styles.chatContainer}>
      {/* Sidebar with Sessions */}
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h3>Chat History</h3>
        </div>

        <div className={styles.newChatSection}>
          <input
            type="text"
            placeholder="Session name..."
            value={sessionTitle}
            onChange={(e) => setSessionTitle(e.target.value)}
            className={styles.titleInput}
            onKeyPress={(e) => e.key === 'Enter' && handleNewChat()}
          />
          <button 
            onClick={handleNewChat} 
            className={styles.newChatBtn}
            disabled={loading}
          >
            + New Chat
          </button>
        </div>

        <div className={styles.sessionsList}>
          {sessions.length === 0 ? (
            <div className={styles.noSessions}>
              No chat sessions yet. Create one to get started!
            </div>
          ) : (
            sessions.map(session => (
              <div
                key={session.session_id}
                className={`${styles.sessionItem} ${
                  currentSession === session.session_id ? styles.active : ''
                }`}
              >
                <div
                  className={styles.sessionContent}
                  onClick={() => loadSession(session.session_id)}
                >
                  {editingSession === session.session_id ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className={styles.editInput}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveEdit(session.session_id);
                        }
                      }}
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <h4>{session.title}</h4>
                      <p>{session.total_messages} messages</p>
                      <span className={styles.date}>
                        {new Date(session.updated_at).toLocaleDateString()}
                      </span>
                    </>
                  )}
                </div>
                
                <div className={styles.sessionActions}>
                  {editingSession === session.session_id ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSaveEdit(session.session_id);
                      }}
                      className={styles.saveBtn}
                    >
                      ✓
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditSession(session.session_id, session.title);
                        }}
                        className={styles.editBtn}
                        title="Edit session"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSession(session.session_id);
                        }}
                        className={styles.deleteSessionBtn}
                        title="Delete session"
                      >
                        ×
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className={styles.chatArea}>
        {currentSession ? (
          <>
            {/* Session Header */}
            <div className={styles.sessionHeader}>
              <div className={styles.headerContent}>
                <h2>{currentSessionData?.title || 'Chat'}</h2>
                <p>{currentSessionData?.category || 'General'}</p>
              </div>
              <button
                onClick={() => handleClearMessages(currentSession)}
                className={styles.clearBtn}
                title="Clear messages"
              >
                Clear Chat
              </button>
            </div>

            {/* Messages Container */}
            <div className={styles.messagesContainer}>
              {messages.length === 0 ? (
                <div className={styles.emptyChat}>
                  <p>No messages yet. Start a conversation!</p>
                </div>
              ) : (
                messages.map(msg => (
                  <div
                    key={msg.message_id}
                    className={styles.messageGroup}
                  >
                    {/* User Question */}
                    <div className={`${styles.message} ${styles.user}`}>
                      <div className={styles.messageBubble}>
                        <p>{msg.question}</p>
                        <span className={styles.msgTime}>
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    
                    {/* Assistant Answer */}
                    {msg.answer && (
                      <div className={`${styles.message} ${styles.assistant}`}>
                        <div className={styles.messageBubble}>
                          <p>{msg.answer}</p>
                          {msg.source && (
                            <span className={styles.source}>Source: {msg.source}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className={styles.inputForm}>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className={styles.messageInput}
                disabled={loading}
              />
              <button 
                type="submit" 
                disabled={loading || !inputValue.trim()}
                className={styles.sendBtn}
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>

            {error && <div className={styles.errorMsg}>{error}</div>}
          </>
        ) : (
          <div className={styles.noSessionSelected}>
            <h2>Welcome to Chat</h2>
            <p>Create a new chat session or select one from the sidebar to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
}
