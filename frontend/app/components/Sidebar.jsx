'use client';

import { useState } from 'react';

export default function Sidebar({ activeMode, onModeChange }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>🤖 ChatBot</h1>
        <p className="subtitle">AI-Powered Chat</p>
      </div>

      <nav className="sidebar-nav">
        <button
          onClick={() => onModeChange('chat')}
          className={`nav-btn ${activeMode === 'chat' ? 'active' : ''}`}
          title="Chat with AI"
        >
          <span className="icon">💬</span>
          <span className="label">Chat</span>
        </button>

        <button
          onClick={() => onModeChange('builder')}
          className={`nav-btn ${activeMode === 'builder' ? 'active' : ''}`}
          title="Build knowledge"
        >
          <span className="icon">🏗️</span>
          <span className="label">Build</span>
        </button>

        <button
          onClick={() => onModeChange('pdf')}
          className={`nav-btn ${activeMode === 'pdf' ? 'active' : ''}`}
          title="Upload documents"
        >
          <span className="icon">📄</span>
          <span className="label">Documents</span>
        </button>
      </nav>

      <style jsx>{`
        .sidebar {
          width: 260px;
          height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-right: 1px solid #e5e5e5;
          display: flex;
          flex-direction: column;
          padding: 20px 0;
          position: fixed;
          left: 0;
          top: 0;
          overflow-y: auto;
          color: white;
        }

        .sidebar-header {
          padding: 20px 20px 30px 20px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          text-align: center;
        }

        .sidebar-header h1 {
          font-size: 24px;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .subtitle {
          font-size: 12px;
          opacity: 0.8;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .sidebar-nav {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 20px 12px;
        }

        .nav-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 16px;
          background-color: rgba(255, 255, 255, 0.1);
          border: 2px solid transparent;
          border-radius: 10px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .nav-btn:hover {
          background-color: rgba(255, 255, 255, 0.2);
          border-color: rgba(255, 255, 255, 0.3);
          transform: translateX(4px);
        }

        .nav-btn.active {
          background-color: rgba(255, 255, 255, 0.3);
          border-color: white;
          color: white;
        }

        .icon {
          font-size: 18px;
        }

        .label {
          flex: 1;
          text-align: left;
        }
      `}</style>
    </aside>
  );
}
