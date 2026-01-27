-- Hasura PostgreSQL Schema
-- Execute these commands in PostgreSQL to create tables for Hasura

-- ==================== WORKFLOWS TABLE ====================
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);

-- ==================== NODES TABLE ====================
CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workflow_id, text)
);

CREATE INDEX idx_nodes_workflow_id ON nodes(workflow_id);
CREATE INDEX idx_nodes_text ON nodes(text);

-- ==================== EDGES TABLE ====================
CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    source_node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workflow_id, source_node_id, target_node_id)
);

CREATE INDEX idx_edges_workflow_id ON edges(workflow_id);
CREATE INDEX idx_edges_source_node_id ON edges(source_node_id);
CREATE INDEX idx_edges_target_node_id ON edges(target_node_id);

-- ==================== FAQs TABLE ====================
CREATE TABLE faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_faqs_question ON faqs(question);
CREATE INDEX idx_faqs_category ON faqs(category);
CREATE INDEX idx_faqs_created_at ON faqs(created_at DESC);

-- ==================== PDF_DOCUMENTS TABLE ====================
CREATE TABLE pdf_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    minio_path VARCHAR(500) NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(500),
    is_processed INTEGER DEFAULT 0,
    processing_status VARCHAR(255),
    chunk_count INTEGER DEFAULT 0,
    embedding_count INTEGER DEFAULT 0,
    processed_at TIMESTAMP
);

CREATE INDEX idx_pdf_documents_filename ON pdf_documents(filename);
CREATE INDEX idx_pdf_documents_upload_date ON pdf_documents(upload_date DESC);
CREATE INDEX idx_pdf_documents_is_processed ON pdf_documents(is_processed);
