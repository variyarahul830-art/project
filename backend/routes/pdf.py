from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from minio import Minio
from minio.error import S3Error
from config import settings
from schemas import PDFUploadResponse, PDFDocumentResponse
from datetime import datetime, timedelta
import io
import logging
from services import hasura_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from services.pdf_processor import PDFProcessor
from services.text_chunker import TextChunker
from services.embeddings import EmbeddingGenerator
from services.milvus_service import MilvusService

router = APIRouter(prefix="/api/pdf", tags=["PDF"])

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL
)

# Ensure bucket exists
def ensure_bucket_exists():
    """Create bucket if it doesn't exist"""
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
    except S3Error as e:
        print(f"Error creating bucket: {e}")

ensure_bucket_exists()


async def process_pdf_async(pdf_id: int, file_content: bytes, filename: str):
    """
    Async task: Extract text, chunk with streaming, generate embeddings incrementally, and store in Milvus
    Chunks are sent for embedding as soon as they are created, not waiting for all chunks to be ready
    """
    total_chunks_processed = 0
    total_embeddings_inserted = 0

    try:
        logger.info(f"[PDF {pdf_id}] Starting PDF processing for: {filename}")

        # Update status to processing
        await hasura_client.update_pdf_processing_status(pdf_id, 1, "Extracting text from PDF...")
        logger.info(f"[PDF {pdf_id}] Extracting text from PDF...")
        
        # Step 1: Extract text from PDF
        pdf_processor = PDFProcessor()
        pages_data = pdf_processor.extract_text_with_pages(file_content)
        logger.info(f"[PDF {pdf_id}] Extracted {len(pages_data)} pages from PDF")
        
        if not pages_data:
            error_msg = "Failed: No text could be extracted from PDF"
            logger.error(f"[PDF {pdf_id}] {error_msg}")
            await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
            return
        
        # Step 2: Initialize Milvus and create collection BEFORE chunking
        await hasura_client.update_pdf_processing_status(pdf_id, 1, "Initializing Milvus collection...")
        logger.info(f"[PDF {pdf_id}] Initializing Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        
        try:
            milvus_service = MilvusService(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                collection_name=settings.MILVUS_COLLECTION_NAME
            )
            logger.info(f"[PDF {pdf_id}] Connected to Milvus")
        except Exception as e:
            error_msg = f"Failed to connect to Milvus: {str(e)}"
            logger.error(f"[PDF {pdf_id}] {error_msg}")
            await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
            return
        
        # Create collection and initialize embedding generator
        embedding_generator = EmbeddingGenerator(
            model_name=settings.EMBEDDING_MODEL,
            huggingface_token=settings.HUGGINGFACE_TOKEN if settings.HUGGINGFACE_TOKEN else None
        )
        embedding_dim = embedding_generator.get_embedding_dimension()
        logger.info(f"[PDF {pdf_id}] Creating/verifying collection with embedding dimension: {embedding_dim}")
        
        try:
            milvus_service.create_collection(embedding_dim=embedding_dim)
            logger.info(f"[PDF {pdf_id}] Milvus collection ready: {settings.MILVUS_COLLECTION_NAME}")
        except Exception as e:
            error_msg = f"Failed to create Milvus collection: {str(e)}"
            logger.error(f"[PDF {pdf_id}] {error_msg}")
            await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
            return
        
        # Step 3: Stream chunks, generate embeddings, and insert into Milvus incrementally
        await hasura_client.update_pdf_processing_status(pdf_id, 1, "Chunking text and generating embeddings...")
        logger.info(f"[PDF {pdf_id}] Starting streaming chunk processing with incremental embedding generation...")
        
        text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Process chunks in batches for better embedding performance
        batch_size = 5  # Number of chunks to process together before inserting
        chunk_batch = []
        
        try:
            # Use the streaming chunk generator to process chunks as they're created
            logger.info(f"[PDF {pdf_id}] Creating streaming generator for {len(pages_data)} pages...")
            chunk_generator = text_chunker.chunk_documents_with_cross_page_overlap_streaming(pages_data)
            logger.info(f"[PDF {pdf_id}] Generator created, starting to iterate through chunks...")
            
            chunk_count = 0
            for chunk in chunk_generator:
                chunk_count += 1
                logger.info(f"[PDF {pdf_id}] ✓ Chunk #{chunk_count} created (chunk_index: {chunk['chunk_index']}, pages: {chunk['page_numbers']}, spans_multiple: {chunk['spans_multiple_pages']}, size: {len(chunk['text'])} chars)")
                chunk_batch.append(chunk)
                
                # When batch is full or this is the last chunk, process and insert
                if len(chunk_batch) >= batch_size:
                    logger.info(f"[PDF {pdf_id}] 🔄 Processing batch of {len(chunk_batch)} chunks (batch starts at chunk #{chunk_count - len(chunk_batch) + 1})...")
                    
                    # Generate embeddings for this batch
                    chunk_texts = [c['text'] for c in chunk_batch]
                    try:
                        logger.info(f"[PDF {pdf_id}] 🧠 Generating embeddings for {len(chunk_texts)} texts...")
                        embeddings = embedding_generator.generate_embedding_for_batch(chunk_texts, batch_size=8)
                        logger.info(f"[PDF {pdf_id}] 🧠 Generated {len(embeddings)} embeddings successfully")
                    except Exception as e:
                        error_msg = f"Failed to generate embeddings for batch: {str(e)}"
                        logger.error(f"[PDF {pdf_id}] {error_msg}")
                        await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
                        return
                    
                    # Prepare data for insertion
                    embeddings_data = []
                    for i, chunk in enumerate(chunk_batch):
                        embeddings_data.append({
                            'embedding': embeddings[i],
                            'text_chunk': chunk['text'],
                            'document_name': filename,
                            'page_number': chunk['page_numbers'][0] if chunk['page_numbers'] else 1,  # Use first page if spans multiple
                            'chunk_index': chunk['chunk_index'],
                            'token_count': chunk['token_count'],
                        })
                    
                    # Insert batch into Milvus
                    try:
                        logger.info(f"[PDF {pdf_id}] 💾 Inserting {len(embeddings_data)} embeddings into Milvus...")
                        inserted_count = milvus_service.insert_embeddings(embeddings_data)
                        total_embeddings_inserted += inserted_count
                        total_chunks_processed += len(chunk_batch)
                        logger.info(f"[PDF {pdf_id}] ✅ Inserted {inserted_count} embeddings into Milvus (Total processed: {total_chunks_processed} chunks, {total_embeddings_inserted} embeddings)")
                    except Exception as e:
                        error_msg = f"Failed to insert embeddings into Milvus: {str(e)}"
                        logger.error(f"[PDF {pdf_id}] {error_msg}")
                        await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
                        return
                    
                    # Update status with progress
                    await hasura_client.update_pdf_processing_status(
                        pdf_id,
                        1,
                        f"Processed {total_chunks_processed} chunks, inserted {total_embeddings_inserted} embeddings...",
                        chunk_count=total_chunks_processed,
                        embedding_count=total_embeddings_inserted,
                    )
                    
                    # Clear batch for next round
                    chunk_batch = []
            
            logger.info(f"[PDF {pdf_id}] Generator iteration complete. Total chunks created: {chunk_count}")
            
            # Process any remaining chunks in the final batch
            if chunk_batch:
                logger.info(f"[PDF {pdf_id}] Processing final batch of {len(chunk_batch)} chunks...")
                
                chunk_texts = [c['text'] for c in chunk_batch]
                try:
                    logger.info(f"[PDF {pdf_id}] 🧠 Generating embeddings for final batch ({len(chunk_texts)} texts)...")
                    embeddings = embedding_generator.generate_embedding_for_batch(chunk_texts, batch_size=8)
                    logger.info(f"[PDF {pdf_id}] 🧠 Generated {len(embeddings)} embeddings for final batch")
                except Exception as e:
                    error_msg = f"Failed to generate embeddings for final batch: {str(e)}"
                    logger.error(f"[PDF {pdf_id}] {error_msg}")
                    await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
                    return
                
                embeddings_data = []
                for i, chunk in enumerate(chunk_batch):
                    embeddings_data.append({
                        'embedding': embeddings[i],
                        'text_chunk': chunk['text'],
                        'document_name': filename,
                        'page_number': chunk['page_numbers'][0] if chunk['page_numbers'] else 1,  # Use first page if spans multiple
                        'chunk_index': chunk['chunk_index'],
                        'token_count': chunk['token_count'],
                    })
                
                try:
                    logger.info(f"[PDF {pdf_id}] 💾 Inserting final batch of {len(embeddings_data)} embeddings into Milvus...")
                    inserted_count = milvus_service.insert_embeddings(embeddings_data)
                    total_embeddings_inserted += inserted_count
                    total_chunks_processed += len(chunk_batch)
                    logger.info(f"[PDF {pdf_id}] ✅ Inserted {inserted_count} embeddings into Milvus (Final total: {total_chunks_processed} chunks, {total_embeddings_inserted} embeddings)")
                except Exception as e:
                    error_msg = f"Failed to insert embeddings into Milvus: {str(e)}"
                    logger.error(f"[PDF {pdf_id}] {error_msg}")
                    await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
                    return
        
        except Exception as e:
            error_msg = f"Error during streaming chunk processing: {str(e)}"
            logger.error(f"[PDF {pdf_id}] ❌ {error_msg}", exc_info=True)
            await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)
            return
        
        # Step 4: Update PDF processing status to completed
        await hasura_client.update_pdf_processing_status(
            pdf_id,
            2,
            "Processing completed successfully",
            chunk_count=total_chunks_processed,
            embedding_count=total_embeddings_inserted,
        )
        
        logger.info(f"[PDF {pdf_id}] ✅ PDF processing completed successfully")
        logger.info(f"[PDF {pdf_id}] Summary: {total_chunks_processed} chunks, {total_embeddings_inserted} embeddings stored in Milvus collection '{settings.MILVUS_COLLECTION_NAME}'")
        
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        logger.error(f"[PDF {pdf_id}] ❌ {error_msg}", exc_info=True)
        await hasura_client.update_pdf_processing_status(pdf_id, -1, error_msg)


@router.post("/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    description: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Upload a PDF file to MinIO and store metadata in PostgreSQL
    Text extraction and embedding generation happens in background
    
    - **file**: The PDF file to upload (required)
    - **description**: Optional description of the PDF
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check if PDF with same filename already exists
    if await hasura_client.pdf_exists_by_filename(file.filename):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PDF already uploaded"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create MinIO path with UTC timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
        minio_path = f"{settings.MINIO_BUCKET_NAME}/{timestamp}{file.filename}"
        
        # Get current time in ISO format for database storage
        upload_date = datetime.utcnow().isoformat()
        
        # Upload to MinIO
        file_stream = io.BytesIO(file_content)
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            f"{timestamp}{file.filename}",
            file_stream,
            file_size,
            content_type="application/pdf"
        )
        
        # Store metadata in Hasura/PostgreSQL
        pdf_doc = await hasura_client.create_pdf_document(
            filename=file.filename,
            minio_path=minio_path,
            file_size=file_size,
            description=description,
            processing_status="Pending processing",
            is_processed=0,
            upload_date=upload_date,
        )
        
        # Add background task to process PDF
        background_tasks.add_task(
            process_pdf_async,
            pdf_doc["id"],
            file_content,
            file.filename,
        )
        
        return PDFUploadResponse(
            success=True,
            message=f"PDF '{file.filename}' uploaded successfully. Processing started in background.",
            pdf=PDFDocumentResponse.model_validate(pdf_doc)
        )
        
    except HTTPException:
        raise
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading to MinIO: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading PDF: {str(e)}"
        )


@router.get("/documents", response_model=list[PDFDocumentResponse])
async def get_all_pdfs():
    """
    Get all uploaded PDF documents (via Hasura GraphQL)
    """
    pdfs = await hasura_client.get_all_pdfs()
    return [PDFDocumentResponse.model_validate(pdf) for pdf in pdfs]


@router.get("/documents/{pdf_id}", response_model=PDFDocumentResponse)
async def get_pdf(pdf_id: int):
    """
    Get a specific PDF document by ID (via Hasura GraphQL)
    """
    pdf = await hasura_client.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF document not found"
        )
    return PDFDocumentResponse.model_validate(pdf)


@router.delete("/documents/{pdf_id}", status_code=status.HTTP_200_OK)
async def delete_pdf(pdf_id: int):
    """
    Delete a PDF document from MinIO, database, and Milvus (metadata and embeddings)
    """
    pdf = await hasura_client.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF document not found"
        )
    
    try:
        # Extract filename from minio_path (e.g., "pdf/20240121_120000_document.pdf" -> "20240121_120000_document.pdf")
        minio_filename = pdf.get("minio_path", "").split('/')[-1]
        pdf_filename = pdf.get("filename")
        
        # Delete from MinIO
        minio_client.remove_object(settings.MINIO_BUCKET_NAME, minio_filename)
        logger.info(f"Deleted PDF from MinIO: {minio_filename}")
        
        # Delete embeddings from Milvus
        try:
            milvus_service = MilvusService(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                collection_name=settings.MILVUS_COLLECTION_NAME
            )
            deleted_count = milvus_service.delete_by_document_name(pdf_filename)
            logger.info(f"Deleted {deleted_count} embeddings from Milvus for document: {pdf_filename}")
        except Exception as e:
            logger.error(f"Error deleting embeddings from Milvus: {str(e)}")
            # Continue with deletion even if Milvus delete fails
        
        # Delete metadata via Hasura
        await hasura_client.delete_pdf(pdf_id)
        logger.info(f"Deleted PDF metadata from database: {pdf_id}")
        
        return {
            "success": True,
            "message": f"PDF '{pdf_filename}' and its embeddings deleted successfully"
        }
        
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting from MinIO: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting PDF: {str(e)}"
        )


@router.get("/documents/{pdf_id}/download")
async def download_pdf(pdf_id: int):
    """
    Stream PDF file directly from MinIO through the backend
    This avoids presigned URL hostname issues in Docker environments
    """
    pdf = await hasura_client.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF document not found"
        )
    
    try:
        # Extract filename from minio_path
        minio_filename = pdf.get("minio_path", "").split('/')[-1]
        
        # Get the file from MinIO
        response = minio_client.get_object(
            settings.MINIO_BUCKET_NAME,
            minio_filename
        )
        
        # Stream the file to the client
        return StreamingResponse(
            response.stream(32*1024),  # 32KB chunks
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{pdf.get("filename")}"'
            }
        )
        
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/documents/{pdf_id}/processing-status")
async def get_processing_status(pdf_id: int):
    """
    Get processing status of a PDF document
    """
    pdf = await hasura_client.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF document not found"
        )
    
    status_map = {
        0: "pending",
        1: "processing",
        2: "completed",
        -1: "failed"
    }
    
    return {
        "pdf_id": pdf.get("id"),
        "filename": pdf.get("filename"),
        "status": status_map.get(pdf.get("is_processed"), "unknown"),
        "status_code": pdf.get("is_processed"),
        "message": pdf.get("processing_status"),
        "chunk_count": pdf.get("chunk_count"),
        "embedding_count": pdf.get("embedding_count"),
        "processed_at": pdf.get("processed_at"),
    }
