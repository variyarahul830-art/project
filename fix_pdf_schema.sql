-- Fix pdf_documents table schema - add missing columns if they don't exist

-- Add description column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'description'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN description VARCHAR(500);
    END IF;
END $$;

-- Add minio_path column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'minio_path'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN minio_path VARCHAR(500);
    END IF;
END $$;

-- Add processing_status column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'processing_status'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN processing_status VARCHAR(255);
    END IF;
END $$;

-- Add chunk_count column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'chunk_count'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN chunk_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- Add embedding_count column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'embedding_count'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN embedding_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- Add processed_at column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pdf_documents' AND column_name = 'processed_at'
    ) THEN
        ALTER TABLE pdf_documents ADD COLUMN processed_at TIMESTAMP;
    END IF;
END $$;

-- Backfill minio_path for existing rows (if null)
UPDATE pdf_documents 
SET minio_path = CONCAT('pdf/', id, '_', filename) 
WHERE minio_path IS NULL;

-- Create unique constraint on minio_path if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'pdf_documents_minio_path_key'
    ) THEN
        ALTER TABLE pdf_documents ADD CONSTRAINT pdf_documents_minio_path_key UNIQUE (minio_path);
    END IF;
END $$;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_pdf_documents_filename ON pdf_documents(filename);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_upload_date ON pdf_documents(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_is_processed ON pdf_documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_minio_path ON pdf_documents(minio_path);
