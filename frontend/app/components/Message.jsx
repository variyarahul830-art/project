'use client';

import ReactMarkdown from 'react-markdown';

export default function Message({ type, text, answers, targetNodes, onOptionClick, source }) {
  const hasAnswers = answers && answers.length > 0;

  return (
    <div className={`message message-${type}`}>
      <div className="message-avatar">{type === 'user' ? '👤' : '🤖'}</div>
      <div className="message-content">
        <div className="message-text">
          {type === 'user' ? (
            <p>{text}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({node, ...props}) => <p style={{margin: '0 0 12px 0'}} {...props} />,
                ul: ({node, ...props}) => <ul style={{marginLeft: '20px', marginBottom: '12px'}} {...props} />,
                ol: ({node, ...props}) => <ol style={{marginLeft: '20px', marginBottom: '12px'}} {...props} />,
                li: ({node, ...props}) => <li style={{marginBottom: '6px'}} {...props} />,
                strong: ({node, ...props}) => <strong style={{fontWeight: 'bold', color: '#1b5e20'}} {...props} />,
                em: ({node, ...props}) => <em style={{fontStyle: 'italic', color: '#2e7d32'}} {...props} />,
                code: ({node, inline, ...props}) => 
                  inline ? (
                    <code style={{backgroundColor: '#e8f5e9', padding: '2px 6px', borderRadius: '3px', fontFamily: 'monospace'}} {...props} />
                  ) : (
                    <pre style={{backgroundColor: '#e8f5e9', padding: '10px', borderRadius: '6px', overflow: 'auto', marginBottom: '12px'}} {...props} />
                  ),
                blockquote: ({node, ...props}) => <blockquote style={{borderLeft: '3px solid #4caf50', paddingLeft: '12px', marginLeft: '0', marginBottom: '12px', color: '#555'}} {...props} />,
                h1: ({node, ...props}) => <h3 style={{margin: '12px 0 8px 0', color: '#1b5e20'}} {...props} />,
                h2: ({node, ...props}) => <h4 style={{margin: '10px 0 6px 0', color: '#2e7d32'}} {...props} />,
                h3: ({node, ...props}) => <h5 style={{margin: '8px 0 4px 0', color: '#388e3c'}} {...props} />,
              }}
            >
              {text}
            </ReactMarkdown>
          )}
        </div>
        {hasAnswers && (
          <div className="answers-container">
            <div className="answers-label">💡 Related Information:</div>
            <div className="answers-list">
              {(targetNodes || answers).map((item, idx) => {
                const nodeData = typeof item === 'string' ? { text: item, is_source: false } : item;
                return (
                  <div key={idx} className={`answer-item ${nodeData.is_source ? 'clickable' : ''}`}>
                    <span className="arrow">→</span>
                    <button
                      type="button"
                      className="answer-button"
                      onClick={() => nodeData.is_source && onOptionClick(nodeData.text)}
                      disabled={!nodeData.is_source}
                    >
                      {nodeData.text}
                    </button>
                    {nodeData.is_source && <span className="source-indicator">🔗</span>}
                  </div>
                );
              })}
            </div>
          </div>
        )}
        {source && <div className="source-badge">{source === 'rag' ? '📚 From Documents' : '🧠 From Knowledge'}</div>}
      </div>

      <style jsx>{`
        .message {
          display: flex;
          gap: 12px;
          animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .message-avatar {
          font-size: 24px;
          min-width: 32px;
          display: flex;
          align-items: flex-start;
          padding-top: 4px;
        }

        .message-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .message-user {
          justify-content: flex-end;
        }

        .message-user .message-avatar {
          order: 2;
        }

        .message-user .message-content {
          align-items: flex-end;
        }

        .message-text {
          margin: 0;
          padding: 10px 14px;
          border-radius: 12px;
          font-size: 15px;
          line-height: 1.6;
          word-wrap: break-word;
          max-width: 80%;
        }

        .message-user .message-text {
          background-color: #007bff;
          color: white;
          border-bottom-right-radius: 4px;
        }

        .message-bot .message-text {
          background-color: #f0f0f0;
          color: #333;
          border-bottom-left-radius: 4px;
        }

        .answers-container {
          margin-top: 8px;
          padding: 12px 14px;
          background: linear-gradient(135deg, #e8f5e9 0%, #f0f9f0 100%);
          border-radius: 10px;
          border-left: 3px solid #4caf50;
        }

        .answers-label {
          font-size: 12px;
          font-weight: 600;
          color: #2e7d32;
          margin-bottom: 8px;
        }

        .answers-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .answer-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #1b5e20;
          background: white;
          padding: 6px 10px;
          border-radius: 6px;
          border: 1px solid #c8e6c9;
          transition: all 0.2s;
        }

        .answer-item.clickable {
          cursor: pointer;
          border-color: #2e7d32;
          background: linear-gradient(135deg, #f1f8f5 0%, #ffffff 100%);
        }

        .answer-item.clickable:hover {
          background-color: #e8f5e9;
          border-color: #1b5e20;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .arrow {
          color: #4caf50;
          font-weight: bold;
          flex-shrink: 0;
        }

        .answer-button {
          background: none;
          border: none;
          color: inherit;
          padding: 0;
          font-size: inherit;
          cursor: inherit;
          text-align: left;
          flex: 1;
          word-break: break-word;
        }

        .answer-button:disabled {
          cursor: default;
        }

        .answer-button:enabled {
          cursor: pointer;
          text-decoration: underline;
          text-decoration-color: #4caf50;
          text-decoration-style: dotted;
          text-underline-offset: 2px;
        }

        .answer-button:enabled:hover {
          text-decoration-style: solid;
          color: #1b5e20;
        }

        .source-indicator {
          flex-shrink: 0;
          font-size: 12px;
          margin-left: 4px;
        }

        .source-badge {
          font-size: 11px;
          padding: 4px 8px;
          background: rgba(100, 100, 100, 0.1);
          border-radius: 4px;
          color: #666;
          margin-top: 4px;
          width: fit-content;
        }
      `}</style>
    </div>
  );
}
