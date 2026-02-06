'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/context/AuthContext';
import { getSessions, getMessages, updateSession, deleteSession } from '../services/sessions';
import styles from './ChatHistory.module.css';

export default function ChatHistory() {
  const router = useRouter();
  const { user, token, loading: authLoading } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingSession, setEditingSession] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [authLoading, user, router]);

  // Load all sessions when user is available or token changes
  useEffect(() => {
    if (!authLoading && user?.user_id && token) {
      console.log('Loading sessions for user:', user.user_id);
      loadSessions();
    }
  }, [user?.user_id, authLoading, token]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching sessions from backend');
      
      const result = await getSessions();
      console.log('Sessions result:', result);
      
      if (result.sessions) {
        const sessionsWithMessages = result.sessions.filter(s => s.total_messages > 0);
        setSessions(sessionsWithMessages);
      }
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Failed to load sessions');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (sessionId) => {
    try {
      setLoading(true);
      setError(null);
      setSelectedSession(sessionId);
      console.log('Fetching messages for session:', sessionId);
      
      const result = await getMessages(sessionId);
      console.log('Messages result:', result);
      
      if (result.messages) {
        setMessages(result.messages);
      }
    } catch (err) {
      console.error('Error loading messages:', err);
      setError('Failed to load messages');
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEditSession = (sessionId, currentTitle) => {
    setEditingSession(sessionId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async (sessionId) => {
    if (!editTitle.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const session = sessions.find(s => s.session_id === sessionId);
      await updateSession(sessionId, editTitle);
      
      setSessions(prev => prev.map(s => 
        s.session_id === sessionId ? { ...s, title: editTitle } : s
      ));
      setEditingSession(null);
      setEditTitle('');
    } catch (err) {
      setError('Failed to update session title');
      console.error('Error updating session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingSession(null);
    setEditTitle('');
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await deleteSession(sessionId);
      
      const updatedSessions = sessions.filter(s => s.session_id !== sessionId);
      setSessions(updatedSessions);
      
      if (selectedSession === sessionId) {
        setSelectedSession(null);
        setMessages([]);
      }
    } catch (err) {
      setError('Failed to delete session');
      console.error('Error deleting session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueChat = (sessionId) => {
    router.push(`/?continue=${sessionId}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const parseAnswer = (answer) => {
    try {
      const parsed = JSON.parse(answer);
      if (parsed.answers && Array.isArray(parsed.answers)) {
        return parsed.answers.join(', ');
      }
      if (parsed.answer) {
        return parsed.answer;
      }
      return answer;
    } catch {
      return answer;
    }
  };

  return (
    <div className={styles.historyContainer}>
      <div className={styles.header}>
        <button 
          onClick={() => window.history.back()}
          className={styles.backButton}
          title="Back to Dashboard"
        >
          ← Back
        </button>
        <h1>Chat History</h1>
        <p>View your previous conversations</p>
      </div>

      <div className={styles.content}>
        {/* Sessions List */}
        <div className={styles.sessionsList}>
          <h2>Sessions ({sessions.length})</h2>
          
          {loading && !selectedSession ? (
            <div className={styles.loading}>Loading sessions...</div>
          ) : sessions.length === 0 ? (
            <div className={styles.empty}>
              <p>No chat history yet</p>
              <p>Start chatting to build your history!</p>
            </div>
          ) : (
            <div className={styles.sessionsGrid}>
              {sessions.map(session => (
                <div
                  key={session.session_id}
                  className={`${styles.sessionCard} ${
                    selectedSession === session.session_id ? styles.active : ''
                  }`}
                  onClick={() => !editingSession && loadMessages(session.session_id)}
                >
                  <div className={styles.sessionHeader}>
                    {editingSession === session.session_id ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className={styles.editInput}
                        autoFocus
                      />
                    ) : (
                      <h3>{session.title}</h3>
                    )}
                  </div>
                  <div className={styles.sessionInfo}>
                    <span className={styles.messageCount}>
                      💬 {session.total_messages} messages
                    </span>
                    <span className={styles.date}>
                      📅 {formatDate(session.created_at)}
                    </span>
                  </div>
                  {session.updated_at !== session.created_at && (
                    <span className={styles.lastUpdated}>
                      Last updated: {formatDate(session.updated_at)}
                    </span>
                  )}
                  
                  {/* Edit buttons */}
                  <div className={styles.sessionActions} onClick={(e) => e.stopPropagation()}>
                    {editingSession === session.session_id ? (
                      <>
                        <button onClick={() => handleSaveEdit(session.session_id)} className={styles.saveBtn}>
                          ✓ Save
                        </button>
                        <button onClick={handleCancelEdit} className={styles.cancelBtn}>
                          ✕ Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          onClick={() => handleEditSession(session.session_id, session.title)}
                          className={styles.editBtn}
                          title="Edit session name"
                        >
                          ✏️ Edit
                        </button>
                        <button 
                          onClick={() => handleDeleteSession(session.session_id)}
                          className={styles.deleteBtn}
                          title="Delete session"
                        >
                          🗑️ Delete
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Messages View */}
        <div className={styles.messagesView}>
          {!selectedSession ? (
            <div className={styles.placeholder}>
              <h2>Select a session</h2>
              <p>Click on a session to view its conversation history</p>
            </div>
          ) : (
            <>
              <div className={styles.messagesHeader}>
                <h2>
                  {sessions.find(s => s.session_id === selectedSession)?.title || 'Conversation'}
                </h2>
                <div className={styles.headerActions}>
                  <button onClick={() => handleContinueChat(selectedSession)} className={styles.continueBtn}>
                    ▶ Continue Chat
                  </button>
                  <button onClick={() => setSelectedSession(null)} className={styles.closeBtn}>
                    ← Back
                  </button>
                </div>
              </div>

              <div className={styles.messagesContainer}>
                {loading ? (
                  <div className={styles.loading}>Loading messages...</div>
                ) : messages.length === 0 ? (
                  <div className={styles.empty}>No messages in this session</div>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx} className={styles.messageGroup}>
                      {/* Question */}
                      <div className={styles.questionBubble}>
                        <div className={styles.bubbleHeader}>
                          <span className={styles.label}>You asked:</span>
                          <span className={styles.time}>{formatDate(msg.created_at)}</span>
                        </div>
                        <p>{msg.question}</p>
                      </div>

                      {/* Answer */}
                      {msg.answer && (
                        <div className={styles.answerBubble}>
                          <div className={styles.bubbleHeader}>
                            <span className={styles.label}>Assistant:</span>
                            {msg.source && (
                              <span className={styles.source}>
                                Source: {msg.source}
                              </span>
                            )}
                          </div>
                          <p>{parseAnswer(msg.answer)}</p>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className={styles.error}>
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  );
}
