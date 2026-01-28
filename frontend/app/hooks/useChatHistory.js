import { useState, useCallback, useEffect } from 'react';
import * as hasura from '../services/hasura';

export const useChatHistory = (userId) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Create new session
  const createSession = useCallback(async (title = 'New Chat', category = 'General') => {
    try {
      setLoading(true);
      setError(null);
      const result = await hasura.createChatSession(userId, title, category);
      if (result.insert_chat_sessions_one) {
        const newSession = result.insert_chat_sessions_one;
        setSessions(prev => [newSession, ...prev]);
        setCurrentSession(newSession.session_id);
        setMessages([]);
        return newSession.session_id;
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to create chat session';
      setError(errorMsg);
      console.error('Error creating session:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Load all sessions for user
  const loadAllSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await hasura.getUserChatSessions(userId);
      if (result.chat_sessions) {
        setSessions(result.chat_sessions);
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to load chat sessions';
      setError(errorMsg);
      console.error('Error loading sessions:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Load specific session messages
  const loadSession = useCallback(async (sessionId) => {
    try {
      setLoading(true);
      setError(null);
      const result = await hasura.getChatMessages(sessionId);
      if (result.chat_messages) {
        setCurrentSession(sessionId);
        setMessages(result.chat_messages);
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to load chat messages';
      setError(errorMsg);
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save message to session
  const saveMessage = useCallback(async (role, content) => {
    if (!currentSession) {
      setError('No active chat session');
      return;
    }

    try {
      setError(null);
      const result = await hasura.addChatMessage(currentSession, userId, role, content);
      if (result.insert_chat_messages_one) {
        setMessages(prev => [...prev, result.insert_chat_messages_one]);
        
        // Update session's total_messages in the sessions list
        setSessions(prev =>
          prev.map(s =>
            s.session_id === currentSession
              ? { ...s, total_messages: s.total_messages + 1 }
              : s
          )
        );
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to save message';
      setError(errorMsg);
      console.error('Error saving message:', err);
    }
  }, [currentSession, userId]);

  // Delete session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      setError(null);
      await hasura.deleteChatSession(sessionId);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (currentSession === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to delete session';
      setError(errorMsg);
      console.error('Error deleting session:', err);
    }
  }, [currentSession]);

  // Update session details
  const updateSession = useCallback(async (sessionId, title, category) => {
    try {
      setError(null);
      await hasura.updateChatSession(sessionId, title, category);
      setSessions(prev =>
        prev.map(s =>
          s.session_id === sessionId
            ? { ...s, title, category }
            : s
        )
      );
    } catch (err) {
      const errorMsg = err.message || 'Failed to update session';
      setError(errorMsg);
      console.error('Error updating session:', err);
    }
  }, []);

  // Clear all messages in session
  const clearMessages = useCallback(async (sessionId) => {
    try {
      setError(null);
      await hasura.clearChatMessages(sessionId);
      if (currentSession === sessionId) {
        setMessages([]);
      }
      setSessions(prev =>
        prev.map(s =>
          s.session_id === sessionId
            ? { ...s, total_messages: 0 }
            : s
        )
      );
    } catch (err) {
      const errorMsg = err.message || 'Failed to clear messages';
      setError(errorMsg);
      console.error('Error clearing messages:', err);
    }
  }, [currentSession]);

  // Load sessions on mount
  useEffect(() => {
    if (userId) {
      loadAllSessions();
    }
  }, [userId, loadAllSessions]);

  return {
    sessions,
    currentSession,
    messages,
    loading,
    error,
    createSession,
    loadSession,
    loadAllSessions,
    saveMessage,
    deleteSession,
    updateSession,
    clearMessages
  };
};
