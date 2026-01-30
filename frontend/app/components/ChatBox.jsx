'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { sendDirectChatMessage } from '../services/api';
import { createChatSession, getChatMessages, getChatSession, updateChatSession } from '../services/hasura';
import Message from './Message';

export default function ChatBox({ workflowId, userId = 'user123', continueSessionId = null }) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const urlSessionId = searchParams.get('continue') || continueSessionId;
  
  // ==================== STATE ====================
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionTitle, setSessionTitle] = useState('New Chat');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editTitleValue, setEditTitleValue] = useState('');

  // ==================== HELPER FUNCTIONS ====================
  
  /**
   * Parse API response and extract message content
   * Handles different response formats: knowledge_graph, faq, rag, and fallback
   */
  const parseApiResponse = (response) => {
    let botText = '';
    let answers = [];
    let targetNodes = [];
    let source = 'unknown';
    
    if (response.success === false) {
      botText = response.message || response.answer || "I couldn't find a response. Please try another question.";
    } else if (response.source === 'knowledge_graph' && response.answers?.length > 0) {
      answers = response.answers;
      targetNodes = response.target_nodes || [];
      botText = '';
      source = 'knowledge_graph';
    } else if (response.source === 'faq') {
      botText = response.answer || "FAQ answer not available.";
      source = 'faq';
    } else if (response.source === 'rag') {
      botText = response.answer || "I couldn't find relevant information in documents.";
      source = 'rag';
    } else {
      botText = response.message || response.answer || "I couldn't find a response. Please try another question.";
    }
    
    return { botText, answers, targetNodes, source };
  };

  /**
   * Parse stored message answer from database (handles JSON parsing)
   */
  const parseStoredAnswer = (answerJson, source = 'unknown') => {
    let answerText = answerJson;
    let answers = [];
    let targetNodes = [];
    let finalSource = source;
    
    try {
      const parsed = JSON.parse(answerJson);
      
      if (parsed.answers?.length > 0) {
        answers = parsed.answers;
        targetNodes = parsed.target_nodes || [];
        answerText = '';
      } else if (parsed.answer) {
        answerText = parsed.answer;
      } else {
        answerText = JSON.stringify(parsed);
      }
      
      if (parsed.source) finalSource = parsed.source;
    } catch (e) {
      // Not JSON, keep as is
      answerText = answerJson;
    }
    
    return { answerText, answers, targetNodes, source: finalSource };
  };

  /**
   * Convert database messages to display format
   * Each database message becomes one user message + one bot message
   */
  const convertDbMessagesToDisplay = (dbMessages) => {
    const displayMessages = [];
    
    dbMessages.forEach(msg => {
      // Add user question
      displayMessages.push({
        type: 'user',
        text: msg.question
      });
      
      // Add bot answer if it exists
      if (msg.answer) {
        const { answerText, answers, targetNodes, source } = parseStoredAnswer(
          msg.answer,
          msg.source || 'unknown'
        );
        
        displayMessages.push({
          type: 'bot',
          text: answerText,
          answers: answers,
          targetNodes: targetNodes,
          source: source
        });
      }
    });
    
    return displayMessages;
  };

  /**
   * Load existing session from database
   * Called when URL has continue parameter
   */
  const loadExistingSession = async (sessionIdToLoad) => {
    try {
      const sessionResult = await getChatSession(sessionIdToLoad);
      if (!sessionResult.chat_sessions?.length) return false;
      
      const session = sessionResult.chat_sessions[0];
      setSessionId(session.session_id);
      setSessionTitle(session.title);
      
      // Only load messages if UI is empty (don't overwrite newly added messages)
      if (messages.length === 0) {
        const messagesResult = await getChatMessages(sessionIdToLoad);
        if (messagesResult.chat_messages) {
          const displayMessages = convertDbMessagesToDisplay(messagesResult.chat_messages);
          setMessages(displayMessages);
        }
      }
      
      return true;
    } catch (err) {
      console.error('Failed to load session:', err);
      return false;
    }
  };

  /**
   * Create a new chat session in the database
   * Returns the new session ID
   */
  const createNewSession = async () => {
    try {
      const result = await createChatSession(userId, sessionTitle, 'General');
      if (result.insert_chat_sessions_one) {
        const newSessionId = result.insert_chat_sessions_one.session_id;
        setSessionId(newSessionId);
        return newSessionId;
      }
      return null;
    } catch (err) {
      console.error('Failed to create session:', err);
      return null;
    }
  };

  /**
   * Initialize or restore session based on URL
   */
  useEffect(() => {
    if (urlSessionId) {
      loadExistingSession(urlSessionId);
    }
    // If no URL session, do nothing - wait for first message to create session
  }, [urlSessionId]);

  // ==================== MESSAGE HANDLING ====================

  /**
   * Main message sending logic
   * 1. Add user message to UI immediately
   * 2. Create session if needed
   * 3. Send to backend
   * 4. Add bot response
   */
  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    // Step 1: Add user message to UI immediately
    setMessages(prev => [...prev, { type: 'user', text: messageText }]);
    setInput('');
    setError(null);
    setLoading(true);

    try {
      // Step 2: Ensure we have a session
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        currentSessionId = await createNewSession();
        if (currentSessionId) {
          // Update URL to persist session
          router.push(`/?continue=${currentSessionId}`);
        } else {
          throw new Error('Failed to create session');
        }
      }

      // Step 3: Send message to backend
      const response = await sendDirectChatMessage(messageText, currentSessionId, userId);
      
      // Step 4: Parse response and add to UI
      const { botText, answers, targetNodes, source } = parseApiResponse(response);
      setMessages(prev => [...prev, {
        type: 'bot',
        text: botText,
        answers: answers,
        targetNodes: targetNodes,
        source: source,
      }]);
    } catch (err) {
      const errorText = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorText);
      setMessages(prev => [...prev, {
        type: 'bot',
        text: `Error: ${errorText}`,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleOptionClick = (optionText) => {
    sendMessage(optionText);
  };

  // ==================== SESSION MANAGEMENT ====================

  /**
   * Start a completely new chat
   * Clear URL, session ID, and all messages
   */
  const handleNewChat = () => {
    router.push('/');
    setMessages([]);
    setError(null);
    setSessionId(null);
    setSessionTitle('New Chat');
    setInput('');
  };

  const handleEditTitle = () => {
    setEditTitleValue(sessionTitle);
    setIsEditingTitle(true);
  };

  const handleSaveTitle = async () => {
    if (!editTitleValue.trim() || !sessionId) return;
    
    try {
      await updateChatSession(sessionId, editTitleValue, 'General');
      setSessionTitle(editTitleValue);
      setIsEditingTitle(false);
    } catch (err) {
      console.error('Failed to update session title:', err);
    }
  };

  const handleCancelEdit = () => {
    setIsEditingTitle(false);
    setEditTitleValue('');
  };

  return (
    <div className="chatbox-container">
      <div className="chat-header">
        <div className="header-top">
          <div className="session-title-container">
            {isEditingTitle ? (
              <div className="title-edit-group">
                <input
                  type="text"
                  value={editTitleValue}
                  onChange={(e) => setEditTitleValue(e.target.value)}
                  className="title-edit-input"
                  autoFocus
                  onKeyPress={(e) => e.key === 'Enter' && handleSaveTitle()}
                />
                <button onClick={handleSaveTitle} className="save-title-btn" title="Save">
                  ✓
                </button>
                <button onClick={handleCancelEdit} className="cancel-title-btn" title="Cancel">
                  ✕
                </button>
              </div>
            ) : (
              <div className="title-display-group">
                <h2>💬 {sessionTitle}</h2>
                <button onClick={handleEditTitle} className="edit-title-btn" title="Rename session">
                  ✏️
                </button>
              </div>
            )}
          </div>
          <div className="header-actions">
            <button onClick={handleNewChat} className="action-btn" title="New conversation">
              ➕
            </button>
          </div>
        </div>
        <p className="subtitle">Chat powered by knowledge graph and AI</p>
      </div>

      <div className="chat-window">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>💬 Start a New Conversation</h2>
            <p>Ask me anything and I'll search through your knowledge base</p>
            <div className="tips">
              <h4>💡 Tips:</h4>
              <ul>
                <li>Ask questions about topics in your knowledge base</li>
                <li>I'll search through documents and connected information</li>
                <li>Click on responses to explore related information</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, index) => (
              <Message 
                key={index} 
                type={msg.type} 
                text={msg.text} 
                answers={msg.answers}
                targetNodes={msg.targetNodes}
                onOptionClick={handleOptionClick}
                source={msg.source}
              />
            ))}
          </div>
        )}
      </div>

      <div className="chat-input-area">
        {error && <div className="error-message">⚠️ {error}</div>}
        <form onSubmit={handleSend} className="chat-form">
          <div className="input-wrapper">
            <input
              type="text"
              placeholder="Ask anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading} className="send-btn">
              {loading ? '⏳' : '➤'}
            </button>
          </div>
        </form>
      </div>

      <style jsx>{`
        .chatbox-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          width: 100%;
          background-color: #fff;
        }

        .chat-header {
          padding: 16px 24px;
          border-bottom: 1px solid #e5e5e5;
          background-color: #f9f9f9;
        }

        .header-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .session-title-container {
          flex: 1;
        }

        .title-display-group {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .title-display-group h2 {
          margin: 0;
          font-size: 20px;
          color: #333;
        }

        .edit-title-btn {
          background: #3498db;
          color: white;
          border: none;
          padding: 6px 10px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.3s ease;
        }

        .edit-title-btn:hover {
          background: #2980b9;
          transform: scale(1.05);
        }

        .title-edit-group {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .title-edit-input {
          font-size: 18px;
          padding: 8px 12px;
          border: 2px solid #3498db;
          border-radius: 6px;
          font-weight: 500;
          font-family: inherit;
          flex: 1;
          max-width: 400px;
        }

        .title-edit-input:focus {
          outline: none;
          border-color: #2980b9;
          box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }

        .save-title-btn,
        .cancel-title-btn {
          padding: 8px 14px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
          transition: all 0.3s ease;
        }

        .save-title-btn {
          background: #27ae60;
          color: white;
        }

        .save-title-btn:hover {
          background: #229954;
        }

        .cancel-title-btn {
          background: #e74c3c;
          color: white;
        }

        .cancel-title-btn:hover {
          background: #c0392b;
        }

        .title-area {
          flex: 1;
        }

        .chat-header h2 {
          margin: 0;
          font-size: 20px;
          color: #333;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .chat-header h2:hover {
          background-color: #f0f0f0;
        }

        .title-edit input {
          font-size: 20px;
          padding: 4px 8px;
          border: 2px solid #007bff;
          border-radius: 4px;
          font-weight: 500;
          font-family: inherit;
        }

        .title-edit input:focus {
          outline: none;
          border-color: #0056b3;
        }

        .header-actions {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          padding: 6px 10px;
          background-color: transparent;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background-color: #f0f0f0;
          border-color: #999;
        }

        .chat-header .subtitle {
          margin: 0;
          font-size: 12px;
          color: #999;
        }

        .chat-window {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          padding: 24px;
          gap: 16px;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #999;
          text-align: center;
        }

        .empty-state h2 {
          font-size: 28px;
          margin: 0 0 12px 0;
          color: #333;
        }

        .empty-state p {
          font-size: 16px;
          margin: 0 0 24px 0;
          color: #999;
        }

        .tips {
          margin-top: 20px;
          text-align: left;
          display: inline-block;
          background-color: #f5f5f5;
          padding: 16px;
          border-radius: 8px;
          border-left: 4px solid #007bff;
        }

        .tips h4 {
          margin: 0 0 12px 0;
          color: #333;
        }

        .tips ul {
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .tips li {
          margin-bottom: 8px;
          color: #666;
          font-size: 14px;
        }

        .tips li:last-child {
          margin-bottom: 0;
        }

        .messages-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .chat-input-area {
          padding: 16px 24px 24px 24px;
          border-top: 1px solid #e5e5e5;
          background-color: #fff;
        }

        .chat-form {
          width: 100%;
        }

        .input-wrapper {
          display: flex;
          gap: 8px;
          align-items: flex-end;
        }

        input[type="text"] {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 15px;
          font-family: inherit;
          background-color: #fff;
          color: #333;
          transition: border-color 0.2s ease;
        }

        input[type="text"]:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        input[type="text"]:disabled {
          background-color: #f5f5f5;
          cursor: not-allowed;
        }

        .send-btn {
          padding: 10px 16px;
          background-color: transparent;
          color: #007bff;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 18px;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 40px;
          min-height: 40px;
        }

        .send-btn:hover:not(:disabled) {
          background-color: #007bff;
          color: white;
          border-color: #007bff;
        }

        .send-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          color: #d32f2f;
          background-color: #ffebee;
          border: 1px solid #ffcdd2;
          padding: 12px;
          border-radius: 8px;
          font-size: 14px;
          margin-bottom: 12px;
        }

        @media (max-width: 768px) {
          .chat-window {
            padding: 16px;
          }

          .chat-input-area {
            padding: 12px 16px 16px 16px;
          }

          .header-actions {
            gap: 4px;
          }
        }
      `}</style>
    </div>
  );
}
