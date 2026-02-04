'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

export default function Sidebar({ activeMode, onModeChange }) {
  const pathname = usePathname();
  const router = useRouter();
  const isHistoryPage = pathname === '/history';
  const [username, setUsername] = useState('');

  useEffect(() => {
    const user = localStorage.getItem('username');
    setUsername(user || 'User');
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    // Force full page reload to clear all state
    window.location.href = '/login';
  };

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

        <Link href="/history" style={{ textDecoration: 'none', width: '100%' }}>
          <button
            className={`nav-btn ${isHistoryPage ? 'active' : ''}`}
            title="View chat history"
            style={{ width: '100%' }}
          >
            <span className="icon">📜</span>
            <span className="label">History</span>
          </button>
        </Link>

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

        <button
          onClick={() => onModeChange('faq')}
          className={`nav-btn ${activeMode === 'faq' ? 'active' : ''}`}
          title="Manage FAQs"
        >
          <span className="icon">📚</span>
          <span className="label">FAQs</span>
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <span className="user-icon">👤</span>
          <span className="user-name">{username}</span>
        </div>
        <button onClick={handleLogout} className="logout-btn" title="Logout">
          <span className="icon">🚪</span>
          <span className="label">Logout</span>
        </button>
      </div>

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

        .sidebar-footer {
          margin-top: auto;
          padding: 20px 12px;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          text-align: left;
        }

        .user-icon {
          font-size: 18px;
        }

        .user-name {
          font-size: 13px;
          color: rgba(255, 255, 255, 0.9);
          font-weight: 500;
          word-break: break-word;
        }

        .logout-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background-color: rgba(255, 74, 74, 0.2);
          border: 2px solid transparent;
          border-radius: 8px;
          color: rgba(255, 255, 255, 0.9);
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .logout-btn:hover {
          background-color: rgba(255, 74, 74, 0.4);
          border-color: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </aside>
  );
}
