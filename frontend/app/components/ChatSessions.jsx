'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import { getUserChatSessions, createChatSession, getChatMessages } from '@/app/services/hasura';
import styles from './ChatSessions.module.css';

export default function ChatSessions({ onSelectSession, currentSessionId }) {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [newSessionCategory, setNewSessionCategory] = useState('General');
  const [creating, setCreating] = useState(false);

  // Fetch user's chat sessions
  useEffect(() => {
    if (user?.user_id) {
      fetchSessions();
    }
  }, [user]);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await getUserChatSessions(user.user_id);
      const sessions = data.chat_sessions || [];
      
      // Verify all sessions belong to current user
      const allBelongToUser = sessions.every(session => session.user_id === user.user_id);
      
      if (!allBelongToUser && sessions.length > 0) {
        console.error('Security: Attempting to access sessions from another user');
        setSessions([]);
        return;
      }
      
      setSessions(sessions);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newSessionTitle.trim()) {
      alert('Please enter a session title');
      return;
    }

    setCreating(true);
    try {
      const result = await createChatSession(
        user.user_id,
        newSessionTitle,
        newSessionCategory
      );
      
      if (result.insert_chat_sessions_one) {
        const newSession = result.insert_chat_sessions_one;
        setSessions([newSession, ...sessions]);
        onSelectSession(newSession.session_id);
        setNewSessionTitle('');
        setNewSessionCategory('General');
        setShowCreateModal(false);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
      alert('Failed to create session');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Chat Sessions</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className={styles.createBtn}
          title="Create new session"
        >
          ➕ New
        </button>
      </div>

      {loading && <p className={styles.loading}>Loading sessions...</p>}

      {!loading && sessions.length === 0 && (
        <p className={styles.empty}>No sessions yet. Create one!</p>
      )}

      <div className={styles.sessionsList}>
        {sessions.map(session => (
          <div
            key={session.session_id}
            className={`${styles.sessionItem} ${
              currentSessionId === session.session_id ? styles.active : ''
            }`}
            onClick={() => onSelectSession(session.session_id)}
          >
            <div className={styles.sessionInfo}>
              <h3>{session.title}</h3>
              <p className={styles.category}>{session.category}</p>
              <p className={styles.meta}>
                Messages: {session.total_messages || 0}
              </p>
            </div>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h3>Create New Session</h3>
            <form onSubmit={handleCreateSession}>
              <input
                type="text"
                placeholder="Session title"
                value={newSessionTitle}
                onChange={(e) => setNewSessionTitle(e.target.value)}
                required
                disabled={creating}
              />
              
              <select
                value={newSessionCategory}
                onChange={(e) => setNewSessionCategory(e.target.value)}
                disabled={creating}
              >
                <option value="General">General</option>
                <option value="Work">Work</option>
                <option value="Personal">Personal</option>
                <option value="Support">Support</option>
              </select>

              <div className={styles.modalButtons}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button type="submit" disabled={creating}>
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          ${styles.container} {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}
