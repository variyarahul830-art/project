-- Hasura Database Schema
-- Create tables for workflows, nodes, edges, and FAQs

-- Workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Nodes table
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Edges table
CREATE TABLE IF NOT EXISTS edges (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    source_node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workflow_id, source_node_id, target_node_id)
);

-- FAQs table
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL UNIQUE,
    answer TEXT NOT NULL,
    category VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_nodes_workflow_id ON nodes(workflow_id);
CREATE INDEX IF NOT EXISTS idx_edges_workflow_id ON edges(workflow_id);
CREATE INDEX IF NOT EXISTS idx_edges_source_node_id ON edges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_target_node_id ON edges(target_node_id);
CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to auto-update updated_at
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nodes_updated_at BEFORE UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_edges_updated_at BEFORE UPDATE ON edges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faqs_updated_at BEFORE UPDATE ON faqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ==================== PDF_DOCUMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS pdf_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    minio_path VARCHAR(500) NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    description VARCHAR(500),
    is_processed INTEGER DEFAULT 0,
    processing_status VARCHAR(255),
    chunk_count INTEGER DEFAULT 0,
    embedding_count INTEGER DEFAULT 0,
    processed_at TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_pdf_documents_filename ON pdf_documents(filename);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_upload_date ON pdf_documents(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_is_processed ON pdf_documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_minio_path ON pdf_documents(minio_path);

-- ==================== CHAT SESSIONS TABLE ====================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) DEFAULT 'New Chat Session',
    category VARCHAR(255) DEFAULT 'General',
    total_messages INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for chat_sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_active ON chat_sessions(is_active);

-- ==================== CHAT MESSAGES TABLE ====================
-- Drop old table if exists
DROP TABLE IF EXISTS chat_messages CASCADE;

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL UNIQUE,
    session_id VARCHAR(255) NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    source VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for chat_messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_message_id ON chat_messages(message_id);