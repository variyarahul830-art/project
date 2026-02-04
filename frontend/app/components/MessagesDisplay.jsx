'use client';
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import { getChatMessages, addChatMessage } from '@/app/services/hasura';
import styles from './MessagesDisplay.module.css';

export default function MessagesDisplay({ sessionId }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch messages when session changes
  useEffect(() => {
    if (sessionId && user?.user_id) {
      fetchMessages();
    }
  }, [sessionId, user?.user_id]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchMessages = async () => {
    setLoading(true);
    try {
      const data = await getChatMessages(sessionId);
      // Verify all messages belong to current user
      const messages = data.chat_messages || [];
      const allBelongToUser = messages.every(msg => msg.user_id === user.user_id);
      
      if (!allBelongToUser && messages.length > 0) {
        console.error('Security: Attempting to access messages from another user');
        setMessages([]);
        return;
      }
      
      setMessages(messages);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setSending(true);
    try {
      const result = await addChatMessage(
        sessionId,
        user.user_id,
        'user',
        newMessage
      );

      if (result.insert_chat_messages_one) {
        const newMsg = result.insert_chat_messages_one;
        setMessages([...messages, newMsg]);
        setNewMessage('');

        // Simulate AI response (you can replace with actual API call)
        setTimeout(async () => {
          const aiResponse = await addChatMessage(
            sessionId,
            user.user_id,
            'assistant',
            'This is an AI response to: ' + newMessage
          );

          if (aiResponse.insert_chat_messages_one) {
            setMessages(prev => [...prev, aiResponse.insert_chat_messages_one]);
          }
        }, 1000);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  if (!sessionId) {
    return (
      <div className={styles.container}>
        <div className={styles.empty}>
          <p>Select a session to view messages</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.messagesArea}>
        {loading && <p className={styles.loading}>Loading messages...</p>}

        {!loading && messages.length === 0 && (
          <p className={styles.empty}>No messages yet. Start the conversation!</p>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`${styles.message} ${styles[msg.role]}`}>
            <div className={styles.messageContent}>
              <p>{msg.content}</p>
              <span className={styles.timestamp}>
                {new Date(msg.created_at).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className={styles.inputArea}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={sending}
          className={styles.input}
        />
        <button
          type="submit"
          disabled={sending || !newMessage.trim()}
          className={styles.sendBtn}
        >
          {sending ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
}
