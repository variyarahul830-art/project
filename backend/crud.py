from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Node, Edge, PDFDocument, Workflow, FAQ
from schemas import NodeCreate, EdgeCreate, WorkflowCreate
from datetime import datetime
import json

# Workflow CRUD Operations

def create_workflow(db: Session, workflow: WorkflowCreate) -> Workflow:
    """Create a new workflow"""
    db_workflow = Workflow(
        name=workflow.name.strip(),
        description=workflow.description
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def get_workflow_by_id(db: Session, workflow_id: int) -> Workflow:
    """Get workflow by ID"""
    return db.query(Workflow).filter(Workflow.id == workflow_id).first()

def get_all_workflows(db: Session) -> list[Workflow]:
    """Get all workflows"""
    return db.query(Workflow).order_by(Workflow.created_at.desc()).all()

def delete_workflow(db: Session, workflow_id: int) -> bool:
    """Delete a workflow and all its nodes and edges"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if workflow:
        db.delete(workflow)
        db.commit()
        return True
    return False

# Node CRUD Operations

def create_node(db: Session, node: NodeCreate) -> Node:
    """Create a new node"""
    db_node = Node(
        text=node.text.strip(),
        workflow_id=node.workflow_id
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

def get_node_by_text(db: Session, text: str, workflow_id: int = None) -> Node:
    """Get node by exact text match. If workflow_id is provided, search only in that workflow. Otherwise search across all workflows"""
    query = db.query(Node).filter(
        func.lower(Node.text) == func.lower(text.strip())
    )
    if workflow_id:
        query = query.filter(Node.workflow_id == workflow_id)
    return query.first()

def search_nodes_by_text(db: Session, text: str, workflow_id: int = None) -> list[Node]:
    """Search for nodes using partial/fuzzy matching (case-insensitive substring). 
    If workflow_id is provided, search only in that workflow. Otherwise search across all workflows"""
    search_term = text.strip().lower()
    query = db.query(Node).filter(
        func.lower(Node.text).contains(search_term)
    )
    if workflow_id:
        query = query.filter(Node.workflow_id == workflow_id)
    return query.all()

def get_node_by_id(db: Session, node_id: int) -> Node:
    """Get node by ID"""
    return db.query(Node).filter(Node.id == node_id).first()

def get_all_nodes(db: Session, workflow_id: int = None) -> list[Node]:
    """Get all nodes, optionally filtered by workflow"""
    query = db.query(Node)
    if workflow_id:
        query = query.filter(Node.workflow_id == workflow_id)
    return query.order_by(Node.created_at.desc()).all()

def get_workflow_nodes(db: Session, workflow_id: int) -> list[Node]:
    """Get all nodes in a workflow"""
    return db.query(Node).filter(Node.workflow_id == workflow_id).order_by(Node.created_at.desc()).all()

def delete_node(db: Session, node_id: int) -> bool:
    """Delete a node and its connected edges"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if node:
        db.delete(node)
        db.commit()
        return True
    return False

def node_exists(db: Session, text: str, workflow_id: int) -> bool:
    """Check if node text already exists in workflow"""
    return get_node_by_text(db, text, workflow_id) is not None

# Edge CRUD Operations

def create_edge(db: Session, edge: EdgeCreate) -> Edge:
    """Create a new edge between nodes"""
    # Check if nodes exist and belong to the workflow
    source = db.query(Node).filter(
        Node.id == edge.source_node_id,
        Node.workflow_id == edge.workflow_id
    ).first()
    target = db.query(Node).filter(
        Node.id == edge.target_node_id,
        Node.workflow_id == edge.workflow_id
    ).first()
    
    if not source or not target:
        raise ValueError("Source or target node does not exist in this workflow")
    
    # Check if edge already exists
    existing = db.query(Edge).filter(
        Edge.source_node_id == edge.source_node_id,
        Edge.target_node_id == edge.target_node_id,
        Edge.workflow_id == edge.workflow_id
    ).first()
    
    if existing:
        raise ValueError("Edge already exists between these nodes")
    
    db_edge = Edge(
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        workflow_id=edge.workflow_id
    )
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

def get_target_nodes(db: Session, source_node_id: int) -> list[Node]:
    """Get all target nodes connected to a source node"""
    edges = db.query(Edge).filter(Edge.source_node_id == source_node_id).all()
    target_nodes = []
    for edge in edges:
        node = get_node_by_id(db, edge.target_node_id)
        if node:
            target_nodes.append(node)
    return target_nodes

def get_target_nodes_by_text(db: Session, source_text: str, workflow_id: int = None) -> list[Node]:
    """Get target nodes by source node text. If workflow_id is provided, only search in that workflow. Otherwise search across all workflows"""
    source_node = get_node_by_text(db, source_text, workflow_id)
    if not source_node:
        return []
    return get_target_nodes(db, source_node.id)

def get_further_options(db: Session, node_id: int) -> list[Node]:
    """Get nodes that this node points to (nodes that have this as source) - for further exploration"""
    edges = db.query(Edge).filter(Edge.source_node_id == node_id).all()
    target_nodes = []
    for edge in edges:
        node = get_node_by_id(db, edge.target_node_id)
        if node:
            target_nodes.append(node)
    return target_nodes

def get_all_edges(db: Session, workflow_id: int = None) -> list[Edge]:
    """Get all edges, optionally filtered by workflow"""
    query = db.query(Edge)
    if workflow_id:
        query = query.filter(Edge.workflow_id == workflow_id)
    return query.order_by(Edge.created_at.desc()).all()

def get_workflow_edges(db: Session, workflow_id: int) -> list[Edge]:
    """Get all edges in a workflow"""
    return db.query(Edge).filter(Edge.workflow_id == workflow_id).order_by(Edge.created_at.desc()).all()

def delete_edge(db: Session, edge_id: int) -> bool:
    """Delete an edge"""
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    if edge:
        db.delete(edge)
        db.commit()
        return True
    return False

def get_graph_data(db: Session, workflow_id: int = None):
    """Get all nodes and edges for graph visualization"""
    nodes = get_all_nodes(db, workflow_id) if workflow_id else get_all_nodes(db)
    edges = get_all_edges(db, workflow_id) if workflow_id else get_all_edges(db)
    edges = get_all_edges(db)
    return {"nodes": nodes, "edges": edges}

# PDF Document CRUD Operations

def create_pdf_document(db: Session, filename: str, minio_path: str, file_size: int, description: str = None) -> PDFDocument:
    """Create a new PDF document record in database"""
    db_pdf = PDFDocument(
        filename=filename,
        minio_path=minio_path,
        file_size=file_size,
        description=description
    )
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

def get_pdf_by_id(db: Session, pdf_id: int) -> PDFDocument:
    """Get PDF document by ID"""
    return db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()

def get_all_pdfs(db: Session) -> list[PDFDocument]:
    """Get all PDF documents"""
    return db.query(PDFDocument).order_by(PDFDocument.upload_date.desc()).all()

def delete_pdf(db: Session, pdf_id: int) -> bool:
    """Delete a PDF document record"""
    pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
    if pdf:
        db.delete(pdf)
        db.commit()
        return True
    return False

def pdf_exists_by_path(db: Session, minio_path: str) -> bool:
    """Check if a PDF document with the given MinIO path already exists"""
    return db.query(PDFDocument).filter(PDFDocument.minio_path == minio_path).first() is not None

def update_pdf_processing_status(db: Session, pdf_id: int, status: int, status_message: str = None, chunk_count: int = 0, embedding_count: int = 0) -> PDFDocument:
    """
    Update PDF processing status
    
    Args:
        pdf_id: PDF document ID
        status: 0=pending, 1=processing, 2=completed, -1=failed
        status_message: Status description
        chunk_count: Number of chunks created
        embedding_count: Number of embeddings stored
    """
    from datetime import datetime
    
    pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
    if pdf:
        pdf.is_processed = status
        pdf.processing_status = status_message
        if chunk_count > 0:
            pdf.chunk_count = chunk_count
        if embedding_count > 0:
            pdf.embedding_count = embedding_count
        if status == 2:  # completed
            pdf.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pdf)
    
    return pdf


# FAQ CRUD Operations

def create_faq(db: Session, question: str, answer: str, category: str = None) -> FAQ:
    """Create a new FAQ"""
    db_faq = FAQ(
        question=question.strip(),
        answer=answer.strip(),
        category=category.strip() if category else None
    )
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

def get_faq_by_id(db: Session, faq_id: int) -> FAQ:
    """Get FAQ by ID"""
    return db.query(FAQ).filter(FAQ.id == faq_id).first()

def get_all_faqs(db: Session, category: str = None) -> list:
    """Get all FAQs, optionally filtered by category"""
    query = db.query(FAQ)
    if category:
        query = query.filter(FAQ.category == category)
    return query.order_by(FAQ.created_at.desc()).all()

def search_faq_by_question(db: Session, question_text: str) -> FAQ:
    """Search for FAQ by exact question match (case-insensitive)"""
    normalized_question = question_text.strip().lower()
    return db.query(FAQ).filter(
        func.lower(FAQ.question) == normalized_question
    ).first()

def search_faq_partial(db: Session, question_text: str) -> list:
    """Search for FAQs by partial question match (case-insensitive)"""
    search_term = f"%{question_text.strip().lower()}%"
    return db.query(FAQ).filter(
        func.lower(FAQ.question).ilike(search_term)
    ).all()

def update_faq(db: Session, faq_id: int, question: str = None, answer: str = None, category: str = None) -> FAQ:
    """Update an FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if faq:
        if question:
            faq.question = question.strip()
        if answer:
            faq.answer = answer.strip()
        if category:
            faq.category = category.strip()
        faq.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(faq)
    return faq

def delete_faq(db: Session, faq_id: int) -> bool:
    """Delete an FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if faq:
        db.delete(faq)
        db.commit()
        return True
    return False

def get_faq_categories(db: Session) -> list:
    """Get all unique FAQ categories"""
    categories = db.query(FAQ.category).distinct().filter(FAQ.category != None).all()
    return [cat[0] for cat in categories]
