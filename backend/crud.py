from sqlalchemy.orm import Session
from models import PDFDocument


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
    """Update PDF processing status"""
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
