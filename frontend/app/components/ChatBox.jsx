'use client';

import { useState, useEffect } from 'react';
import { sendDirectChatMessage } from '../services/api';
import Message from './Message';

export default function ChatBox({ workflowId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) {
      return;
    }

    // Add user message to UI
    const userMessage = { type: 'user', text: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError(null);
    setLoading(true);

    try {
      // Send message to backend
      const response = await sendDirectChatMessage(messageText);

      // Add bot response to chat
      const botText = response.message || response.answer || "I couldn't find a response. Please try another question.";

      const botMessage = {
        type: 'bot',
        text: botText,
        answers: response.answers || [],
        targetNodes: response.target_nodes || [],
        source: response.source || 'knowledge_graph',
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorText = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorText);
      const errorMessage = {
        type: 'bot',
        text: `Error: ${errorText}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionClick = (optionText) => {
    sendMessage(optionText);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleNewChat = async () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="chatbox-container">
      <div className="chat-header">
        <div className="header-top">
          <h2>💬 Chat Assistant</h2>
          <div className="header-actions">
            <button onClick={handleNewChat} className="action-btn" title="Clear conversation">
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
