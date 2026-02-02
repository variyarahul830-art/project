'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Sidebar from './Sidebar';
import ChatBox from './ChatBox';
import GraphBuilderWrapper from './GraphBuilderWrapper';
import PDFUpload from './PDFUpload';
import FAQManagement from './FAQManagement';

export default function HomeClient() {
  const searchParams = useSearchParams();
  const continueSessionId = searchParams.get('continue');
  
  const [activeMode, setActiveMode] = useState('chat');
  const [currentWorkflowId, setCurrentWorkflowId] = useState(null);

  return (
    <div className="app-container">
      <Sidebar activeMode={activeMode} onModeChange={setActiveMode} />

      <main className="main-content">
        {activeMode === 'chat' && <ChatBox workflowId={currentWorkflowId} continueSessionId={continueSessionId} />}
        {activeMode === 'builder' && <GraphBuilderWrapper workflowId={currentWorkflowId} onWorkflowChange={setCurrentWorkflowId} />}
        {activeMode === 'pdf' && <PDFUpload />}
        {activeMode === 'faq' && <FAQManagement />}
      </main>

      <style jsx global>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        html,
        body {
          width: 100%;
          height: 100%;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
          background-color: #fff;
          color: #333;
          overflow-x: hidden;
        }

        #__next {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
        }
      `}</style>

      <style jsx>{`
        .app-container {
          display: flex;
          width: 100%;
          min-height: 100vh;
          background-color: #fff;
        }

        .main-content {
          flex: 1;
          margin-left: 260px;
          background-color: #fff;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          overflow-x: hidden;
          max-height: 100vh;
          scroll-behavior: smooth;
        }

        /* Scrollbar styling */
        .main-content::-webkit-scrollbar {
          width: 10px;
        }

        .main-content::-webkit-scrollbar-track {
          background: #f1f1f1;
        }

        .main-content::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 5px;
        }

        .main-content::-webkit-scrollbar-thumb:hover {
          background: #555;
        }

        @media (max-width: 768px) {
          .app-container {
            flex-direction: column;
            min-height: auto;
          }

          .main-content {
            margin-left: 0;
            margin-top: 0;
            max-height: none;
          }
        }
      `}</style>
    </div>
  );
}
