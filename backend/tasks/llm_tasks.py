"""
Task definitions for Celery workers - async processing for LLM and PDF operations
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime
import json

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def generate_llm_answer_task(self, question, chunks, session_id, user_id, message_id):
    """
    Async task to generate LLM answer from question and context chunks.
    
    Args:
        question (str): User's question
        chunks (list): List of relevant context chunks from PDF
        session_id (str): Chat session ID
        user_id (str): User ID
        message_id (str): Message ID
    
    Returns:
        dict: Task result with answer and metadata
    """
    try:
        from services.llm_service import LLMService
        from services.hasura_client import HasuraClient
        from services.redis_cache import RedisCache
        
        logger.info(f"Processing LLM task for message {message_id}")
        
        # Generate answer from chunks
        llm_service = LLMService()
        answer = llm_service.generate_answer(question, chunks)
        
        logger.info(f"LLM answer generated for message {message_id}")
        
        # Save message to database
        hasura_client = HasuraClient()
        message_data = {
            'message_id': message_id,
            'session_id': session_id,
            'user_id': user_id,
            'question': question,
            'answer': answer,
            'source': 'pdf',
            'created_at': datetime.utcnow().isoformat(),
        }
        
        hasura_client.save_chat_message(message_data)
        logger.info(f"Message {message_id} saved to database")
        
        # Cache result
        cache = RedisCache()
        cache.set(f"llm_answer:{message_id}", answer, ttl=3600)
        
        return {
            'status': 'success',
            'message_id': message_id,
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error processing LLM task: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def save_chat_message_task(self, message_id, session_id, user_id, question, answer, source='pdf'):
    """
    Async task to save chat message to database.
    
    Args:
        message_id (str): Unique message ID
        session_id (str): Chat session ID
        user_id (str): User ID
        question (str): User's question
        answer (str): LLM's answer
        source (str): Message source (pdf, chat, etc)
    
    Returns:
        dict: Save result with status
    """
    try:
        from services.hasura_client import HasuraClient
        
        logger.info(f"Saving message {message_id} to database")
        
        hasura_client = HasuraClient()
        message_data = {
            'message_id': message_id,
            'session_id': session_id,
            'user_id': user_id,
            'question': question,
            'answer': answer,
            'source': source,
            'created_at': datetime.utcnow().isoformat(),
        }
        
        result = hasura_client.save_chat_message(message_data)
        logger.info(f"Message {message_id} saved successfully")
        
        return {
            'status': 'success',
            'message_id': message_id,
            'saved_at': datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error saving message {message_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def process_pdf_embeddings_task(self, pdf_id, pdf_path):
    """
    Async task to process PDF and generate embeddings.
    
    Args:
        pdf_id (str): PDF document ID
        pdf_path (str): Path to PDF file
    
    Returns:
        dict: Processing result with embedding count
    """
    try:
        from services.pdf_processor import PDFProcessor
        from services.embeddings import EmbeddingService
        
        logger.info(f"Processing PDF {pdf_id} from {pdf_path}")
        
        # Extract text from PDF
        pdf_processor = PDFProcessor()
        chunks = pdf_processor.process_pdf(pdf_path)
        logger.info(f"Extracted {len(chunks)} chunks from PDF {pdf_id}")
        
        # Generate embeddings
        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(chunks)
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")
        
        return {
            'status': 'success',
            'pdf_id': pdf_id,
            'chunks_processed': len(chunks),
            'embeddings_generated': len(embeddings),
            'completed_at': datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error processing PDF {pdf_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=120 * (2 ** self.request.retries))
