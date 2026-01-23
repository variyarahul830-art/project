from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Workflow Schemas
class WorkflowBase(BaseModel):
    """Base Workflow schema"""
    name: str = Field(..., min_length=1, description="Workflow name")
    description: Optional[str] = None

class WorkflowCreate(WorkflowBase):
    """Schema for creating a Workflow"""
    pass

class WorkflowResponse(WorkflowBase):
    """Schema for Workflow response"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# Node Schemas
class NodeBase(BaseModel):
    """Base Node schema"""
    text: str = Field(..., min_length=1, description="The node text/concept")
    workflow_id: int = Field(..., description="Workflow ID")

class NodeCreate(NodeBase):
    """Schema for creating a Node"""
    pass

class NodeResponse(NodeBase):
    """Schema for Node response"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# Edge Schemas
class EdgeBase(BaseModel):
    """Base Edge schema"""
    source_node_id: int = Field(..., description="Source node ID")
    target_node_id: int = Field(..., description="Target node ID")
    workflow_id: int = Field(..., description="Workflow ID")

class EdgeCreate(EdgeBase):
    """Schema for creating an Edge"""
    pass

class EdgeResponse(EdgeBase):
    """Schema for Edge response"""
    id: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# Graph Schemas
class GraphData(BaseModel):
    """Complete graph data with nodes and edges"""
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]

class ChatRequest(BaseModel):
    """Schema for chat request"""
    question: str = Field(..., min_length=1, description="User's question/source node text")
    workflow_id: Optional[int] = Field(None, description="Workflow ID (optional - if not provided, searches across all workflows)")

class ChatResponse(BaseModel):
    """Schema for chat response"""
    question: str
    answers: Optional[List[str]] = None
    message: Optional[str] = None
    target_nodes: Optional[List[int]] = None
    success: bool = True

class ErrorResponse(BaseModel):
    """Schema for error response"""
    error: str
    details: Optional[str] = None

# PDF Schemas
class PDFDocumentBase(BaseModel):
    """Base PDF Document schema"""
    filename: str = Field(..., min_length=1, description="Name of the PDF file")
    description: Optional[str] = Field(None, description="Optional description of the PDF")

class PDFDocumentCreate(PDFDocumentBase):
    """Schema for creating a PDF Document"""
    pass

class PDFDocumentResponse(PDFDocumentBase):
    """Schema for PDF Document response"""
    id: int
    minio_path: str
    file_size: int
    upload_date: Optional[str] = None
    is_processed: int = 0  # 0=pending, 1=processing, 2=completed, -1=failed
    processing_status: Optional[str] = None
    chunk_count: int = 0
    embedding_count: int = 0
    processed_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class PDFUploadResponse(BaseModel):
    """Schema for PDF upload response"""
    success: bool
    message: str
    pdf: Optional[PDFDocumentResponse] = None
    error: Optional[str] = None
# FAQ Schemas
class FAQBase(BaseModel):
    """Base FAQ schema"""
    question: str = Field(..., min_length=1, description="FAQ question")
    answer: str = Field(..., min_length=1, description="FAQ answer")
    category: Optional[str] = Field(None, description="FAQ category")

class FAQCreate(FAQBase):
    """Schema for creating an FAQ"""
    pass

class FAQUpdate(BaseModel):
    """Schema for updating an FAQ"""
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None

class FAQResponse(FAQBase):
    """Schema for FAQ response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Schema for chat request"""
    question: str
    workflow_id: Optional[int] = None