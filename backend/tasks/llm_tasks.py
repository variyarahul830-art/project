"""
Task definitions for Celery workers - async processing for LLM and PDF operations
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime
import json

logger = get_task_logger(__name__)

@shared_task(bind=True, name='tasks.llm_tasks.generate_llm_answer_task', max_retries=2, default_retry_delay=60, queue='llm_tasks')
def generate_llm_answer_task(self, question, similar_chunks, session_id, user_id, message_id, client_id=None):
    """
    Async Celery task to generate LLM answer using RAG (Retrieval Augmented Generation) approach.
    
    This task:
    1. Generates LLM answer from question and context chunks
    2. Saves the message to database
    3. Returns the answer for caching
    
    Args:
        message_id (str): Unique message ID
        session_id (str): Chat session ID
        user_id (str): User ID
        question (str): User's question
        similar_chunks (list): List of similar chunks from Milvus
    
    Returns:
        dict: Task result with answer and metadata
    """
    try:
        import asyncio
        from config import settings
        from services.llm_service import LLMService
        from services import hasura_client
        
        logger.info(f"🚀 [Celery Task {message_id}] Starting RAG answer generation")
        logger.info(f"📊 Processing {len(similar_chunks)} context chunks")
        
        # Initialize LLM service with settings
        hf_token = settings.HUGGINGFACE_TOKEN if hasattr(settings, 'HUGGINGFACE_TOKEN') else None
        if not hf_token:
            logger.error(f"[{message_id}] HUGGINGFACE_TOKEN not configured")
            raise ValueError("HUGGINGFACE_TOKEN not configured in settings")
        
        llm_service = LLMService(
            huggingface_token=hf_token,
            model_name=settings.LLM_MODEL if hasattr(settings, 'LLM_MODEL') else "meta-llama/Llama-2-7b-chat-hf"
        )
        
        # Generate answer using LLM with context
        logger.info(f"🤖 [Celery Task {message_id}] Generating answer with LLM...")
        answer = llm_service.generate_answer_with_context(
            question=question,
            context_chunks=similar_chunks,
            max_length=512,
            temperature=0.7
        )
        logger.info(f"✅ [Celery Task {message_id}] Answer generated successfully")
        
        # Create response data with source information
        response_data = {
            "success": True,
            "question": question,
            "answer": answer,
            "source": "rag",
            "data_source": "RAG",
            "chunks_used": len(similar_chunks),
            "source_documents": [
                {
                    "document": chunk.get("document_name"),
                    "page": chunk.get("page_number"),
                    "relevance_score": round(chunk.get("score", 0), 4)
                } for chunk in similar_chunks
            ]
        }
        
        # Save message to database asynchronously
        try:
            logger.info(f"💾 [Celery Task {message_id}] Saving RAG message to database...")
            
            # Run async function in sync context using asyncio
            async def save_message():
                await hasura_client.add_chat_message(
                    message_id=message_id,
                    session_id=session_id,
                    user_id=user_id,
                    question=question,
                    answer=answer,
                    source="rag"
                )
            
            # Create new event loop or use existing one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(save_message())
            logger.info(f"✅ [Celery Task {message_id}] Message saved to database")
        except Exception as db_exc:
            logger.error(f"❌ [Celery Task {message_id}] Failed to save message: {str(db_exc)}", exc_info=True)
            # Continue even if save fails - client can still get the answer
        
        return {
            'status': 'success',
            'message_id': message_id,
            'answer': answer,
            'response_data': response_data,
            'timestamp': datetime.utcnow().isoformat(),
            'client_id': client_id,
            'session_id': session_id,
            'user_id': user_id,
            'question': question,
        }
        
    except Exception as exc:
        logger.error(f"❌ [Celery Task {message_id}] Error in RAG answer generation: {str(exc)}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
