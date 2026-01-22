from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, func, Boolean
from datetime import datetime
from database import Base

class Workflow(Base):
    """Workflow - represents a collection of nodes and edges"""
    
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Node(Base):
    """Knowledge Graph Node - represents a text/concept"""
    
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('workflow_id', 'text', name='uq_node_workflow_text'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Edge(Base):
    """Knowledge Graph Edge - represents a connection between nodes"""
    
    __tablename__ = "edges"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('workflow_id', 'source_node_id', 'target_node_id', name='uq_workflow_edge'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


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

