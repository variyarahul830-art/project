from sqlalchemy import Column, Integer, String, Text, DateTime, func
from datetime import datetime
from database import Base


class PDFDocument(Base):
    """PDF Document - represents an uploaded PDF stored in MinIO"""
    
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    minio_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    # Processing tracking fields
    is_processed = Column(Integer, default=0, nullable=False)  # 0=pending, 1=processing, 2=completed, -1=failed
    processing_status = Column(String(255), nullable=True)  # Status message
    chunk_count = Column(Integer, default=0, nullable=False)  # Number of text chunks created
    embedding_count = Column(Integer, default=0, nullable=False)  # Number of embeddings stored
    processed_at = Column(DateTime, nullable=True)  # Timestamp when processing completed
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'minio_path': self.minio_path,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'description': self.description,
            'is_processed': self.is_processed,
            'processing_status': self.processing_status,
            'chunk_count': self.chunk_count,
            'embedding_count': self.embedding_count,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }


