from fastapi import APIRouter, HTTPException, status
from config import settings
from schemas import ChatRequest
from services import hasura_client
from services.embeddings import EmbeddingGenerator
from services.milvus_service import MilvusService
from services.llm_service import LLMService
from services.redis_cache import get_redis_cache
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=dict)
async def chat(request: ChatRequest):
    """
    Send a question and get connected target nodes from the knowledge graph.
    IMPORTANT: Searches across ALL workflows regardless of workflow_id parameter.
    
    Priority:
    1. Exact match on source nodes (across all workflows) -> return their targets
    2. Partial/fuzzy match on source nodes (across all workflows) -> return their targets
    3. Fallback to RAG (PDF embeddings + LLM)
    
    - **question**: The user's question/source node text (required)
    - **workflow_id**: Ignored - always searches across all workflows
    """
    try:
        logger.info(f"Processing question: {request.question}")
        logger.info(f"Searching across ALL workflows (workflow_id parameter ignored)")
        
        # Resolve session_id if numeric (convert id -> session_id)
        actual_session_id = request.session_id
        if request.session_id and request.user_id:
            # Check if session_id is numeric (meaning it's the 'id' field)
            if request.session_id.isdigit():
                logger.info(f"Converting numeric session ID {request.session_id} to actual session_id")
                # Get all user sessions and find the one with this id
                sessions = await hasura_client.get_user_chat_sessions(request.user_id)
                session = next((s for s in sessions if str(s.get("id")) == request.session_id), None)
                if session:
                    actual_session_id = session.get("session_id")
                    logger.info(f"Resolved session_id: {actual_session_id}")
                else:
                    logger.warning(f"Session with id={request.session_id} not found for user={request.user_id}")
        
        # Initialize variables for saving to database
        answer_text = None
        source_type = None
        
        # Step 1: Try exact match on source node (search ALL workflows)
        logger.info("Step 1: Trying exact text match on source nodes across ALL workflows...")
        source_node = await hasura_client.get_node_by_text(request.question, workflow_id=None)
        
        if source_node:
            logger.info(f"Found exact source node: {source_node['text']}")
            target_nodes = await hasura_client.get_target_nodes(source_node["id"])
            
            if target_nodes:
                logger.info(f"Found {len(target_nodes)} target nodes from exact source match")
                clickable_answers = []
                for target_node in target_nodes:
                    further_nodes = await hasura_client.get_further_options(target_node["id"])
                    is_source = len(further_nodes) > 0 if further_nodes else False
                    clickable_answers.append({
                        "text": target_node["text"],
                        "id": target_node["id"],
                        "is_source": is_source
                    })
                
                logger.info(f"📍 Answer from NODE")
                response_data = {
                    "success": True,
                    "question": source_node["text"],
                    "answers": [node["text"] for node in target_nodes],
                    "target_nodes": [
                        {
                            "id": node["id"],
                            "text": node["text"],
                            "is_source": clickable_answers[[t["id"] for t in target_nodes].index(node["id"])]["is_source"],
                        }
                        for node in target_nodes
                    ],
                    "source": "knowledge_graph",
                    "data_source": "NODE",
                    "count": len(target_nodes)
                }
                
                # Save question and answer to chat history
                if actual_session_id and request.user_id:
                    try:
                        message_id = f"msg_{uuid.uuid4().hex[:16]}"
                        logger.info(f"💾 Saving knowledge_graph message (session={actual_session_id}, user={request.user_id})")
                        await hasura_client.add_chat_message(
                            message_id=message_id,
                            session_id=actual_session_id,
                            user_id=request.user_id,
                            question=request.question,
                            answer=json.dumps(response_data),
                            source="knowledge_graph"
                        )
                        logger.info(f"✅ Saved message {message_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to save chat message: {e}", exc_info=True)
                else:
                    logger.warning(f"⚠️  Skipping save - session_id={actual_session_id}, user_id={request.user_id}")
                
                return response_data
        
        # Step 2: Try partial/fuzzy matching on all source nodes (search ALL workflows)
        logger.info("Step 2: Trying partial text match on source nodes across ALL workflows...")
        matching_nodes = await hasura_client.search_nodes_by_text(request.question, workflow_id=None)
        
        if matching_nodes:
            logger.info(f"Found {len(matching_nodes)} matching source nodes via partial search")
            # Get all target nodes for all matching nodes
            all_target_nodes = []
            for source in matching_nodes:
                targets = await hasura_client.get_target_nodes(source["id"])
                all_target_nodes.extend(targets)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_targets = []
            for node in all_target_nodes:
                if node["id"] not in seen:
                    seen.add(node["id"])
                    unique_targets.append(node)
            
            if unique_targets:
                logger.info(f"Found {len(unique_targets)} unique target nodes from partial source matches")
                clickable_answers = []
                for target_node in unique_targets:
                    further_nodes = await hasura_client.get_further_options(target_node["id"])
                    is_source = len(further_nodes) > 0 if further_nodes else False
                    clickable_answers.append({
                        "text": target_node["text"],
                        "id": target_node["id"],
                        "is_source": is_source
                    })
                
                logger.info(f"📍 Answer from NODE")
                response_data = {
                    "success": True,
                    "question": request.question,
                    "answers": [node["text"] for node in unique_targets],
                    "target_nodes": [
                        {
                            "id": node["id"],
                            "text": node["text"],
                            "is_source": clickable_answers[[t["id"] for t in unique_targets].index(node["id"])]["is_source"],
                        }
                        for node in unique_targets
                    ],
                    "source": "knowledge_graph",
                    "data_source": "NODE",
                    "count": len(unique_targets)
                }
                
                # Save question and answer to chat history
                if actual_session_id and request.user_id:
                    try:
                        message_id = f"msg_{uuid.uuid4().hex[:16]}"
                        await hasura_client.add_chat_message(
                            message_id=message_id,
                            session_id=actual_session_id,
                            user_id=request.user_id,
                            question=request.question,
                            answer=json.dumps(response_data),
                            source="knowledge_graph"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to save chat message: {e}")
                
                return response_data
            else:
                logger.info("Partial match found source nodes, but they have no target connections")
        
        # Step 2: Try to find answer in FAQs (with Redis caching)
        logger.info("Step 3: Checking Redis cache and FAQs...")
        
        # Initialize Redis cache
        redis_cache = get_redis_cache()
        
        # Step 3a: Check Redis cache first
        cached_answer = redis_cache.get(request.question)
        if cached_answer:
            logger.info(f"⚡ Answer from REDIS")
            response_data = {
                "success": True,
                "question": request.question,
                "answer": cached_answer.get("answer"),
                "source": cached_answer.get("source"),
                "faq_id": cached_answer.get("faq_id"),
                "category": cached_answer.get("category"),
                "from_cache": True,
                "data_source": "REDIS"
            }
            
            # Save question and answer to chat history
            if actual_session_id and request.user_id:
                try:
                    message_id = f"msg_{uuid.uuid4().hex[:16]}"
                    await hasura_client.add_chat_message(
                        message_id=message_id,
                        session_id=actual_session_id,
                        user_id=request.user_id,
                        question=request.question,
                        answer=cached_answer.get("answer"),
                        source="faq_cache"
                    )
                except Exception as e:
                    logger.warning(f"Failed to save cached chat message: {e}")
            
            return response_data
        
        # Step 3b: Search FAQs (exact match)
        logger.info("Cache miss - Searching FAQs for exact match...")
        faq_exact = await hasura_client.search_faq_exact(request.question)
        
        if faq_exact:
            logger.info(f"📚 Answer from FAQ")
            response_data = {
                "success": True,
                "question": request.question,
                "answer": faq_exact["answer"],
                "source": "faq",
                "faq_id": faq_exact["id"],
                "category": faq_exact.get("category"),
                "from_cache": False,
                "data_source": "FAQ"
            }
            
            # ✨ NEW: Cache this FAQ answer for future queries (20 min TTL)
            ttl = settings.REDIS_FAQ_TTL_MINUTES
            logger.info(f"💾 Caching FAQ answer in Redis (TTL: {ttl}min)...")
            redis_cache.set(
                request.question,
                {
                    "answer": faq_exact["answer"],
                    "source": "faq",
                    "faq_id": faq_exact["id"],
                    "category": faq_exact.get("category")
                },
                ttl_minutes=ttl
            )
            
            # Save question and answer to chat history
            if actual_session_id and request.user_id:
                try:
                    message_id = f"msg_{uuid.uuid4().hex[:16]}"
                    await hasura_client.add_chat_message(
                        message_id=message_id,
                        session_id=actual_session_id,
                        user_id=request.user_id,
                        question=request.question,
                        answer=faq_exact["answer"],
                        source="faq"
                    )
                except Exception as e:
                    logger.warning(f"Failed to save chat message: {e}")
            
            return response_data
        
        # Step 3c: Try partial FAQ match
        logger.info("No exact match found - Searching for partial FAQ match...")
        faq_partial = await hasura_client.search_faq_partial(request.question)
        if faq_partial:
            logger.info(f"📚 Answer from FAQ")
            # Return the first (most relevant) partial match
            best_faq = faq_partial[0]
            response_data = {
                "success": True,
                "question": request.question,
                "answer": best_faq["answer"],
                "source": "faq",
                "faq_id": best_faq["id"],
                "category": best_faq.get("category"),
                "match_type": "partial",
                "from_cache": False,
                "data_source": "FAQ"
            }
            
            # ✨ NEW: Cache this partial FAQ answer for future queries (20 min TTL)
            ttl = settings.REDIS_FAQ_TTL_MINUTES
            logger.info(f"💾 Caching partial FAQ answer in Redis (TTL: {ttl}min)...")
            redis_cache.set(
                request.question,
                {
                    "answer": best_faq["answer"],
                    "source": "faq",
                    "faq_id": best_faq["id"],
                    "category": best_faq.get("category"),
                    "match_type": "partial"
                },
                ttl_minutes=ttl
            )
            
            # Save question and answer to chat history
            if actual_session_id and request.user_id:
                try:
                    message_id = f"msg_{uuid.uuid4().hex[:16]}"
                    await hasura_client.add_chat_message(
                        message_id=message_id,
                        session_id=actual_session_id,
                        user_id=request.user_id,
                        question=request.question,
                        answer=best_faq["answer"],
                        source="faq"
                    )
                except Exception as e:
                    logger.warning(f"Failed to save chat message: {e}")
            
            return response_data
        
        logger.info("No FAQs found, trying RAG approach with PDF embeddings")
        
        # Step 2: If not found in knowledge graph, use RAG approach
        # Generate embedding for the question
        logger.info("Generating embedding for question...")
        embedding_generator = EmbeddingGenerator(
            model_name=settings.EMBEDDING_MODEL,
            huggingface_token=settings.HUGGINGFACE_TOKEN if settings.HUGGINGFACE_TOKEN else None
        )
        question_embedding = embedding_generator.generate_embedding(request.question)
        logger.info(f"✅ Embedding generated (dimension: {len(question_embedding)})")
        
        # Search for similar chunks in Milvus
        logger.info("Searching for similar chunks in Milvus...")
        milvus_service = MilvusService(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            collection_name=settings.MILVUS_COLLECTION_NAME
        )
        
        try:
            # Create collection if it doesn't exist
            milvus_service.create_collection(embedding_dim=len(question_embedding))
        except Exception as e:
            logger.warning(f"Collection creation/verification had an issue: {str(e)}")
        
        # Search for top 5 similar chunks
        similar_chunks = milvus_service.search_embeddings(question_embedding, limit=5)
        
        if not similar_chunks:
            logger.warning("No similar chunks found in Milvus")
            return {
                "success": False,
                "question": request.question,
                "answer": None,
                "source": "rag",
                "message": "No relevant information found in documents. Please try another question or upload documents.",
                "chunks_found": 0
            }
        
        logger.info(f"✅ Found {len(similar_chunks)} similar chunks")
        
        # Step 3: Generate answer using LLM with context
        logger.info("Generating answer using LLM with Hugging Face...")
        
        # Get token from settings
        hf_token = settings.HUGGINGFACE_TOKEN if hasattr(settings, 'HUGGINGFACE_TOKEN') else None
        if not hf_token:
            logger.error("HUGGINGFACE_TOKEN not configured in settings")
            return {
                "success": False,
                "question": request.question,
                "answer": None,
                "source": "rag",
                "message": "LLM service not properly configured. Please set HUGGINGFACE_TOKEN.",
                "chunks_found": len(similar_chunks)
            }
        
        llm_service = LLMService(
            huggingface_token=hf_token,
            model_name=settings.LLM_MODEL if hasattr(settings, 'LLM_MODEL') else "meta-llama/Llama-2-7b-chat-hf"
        )
        print(request.question)
        answer = llm_service.generate_answer_with_context(
            question=request.question,
            context_chunks=similar_chunks,
            max_length=512,
            temperature=0.7
        )
        
        logger.info("✅ Answer generated successfully")
        
        # Get unique PDFs with their IDs for download links
        pdf_doc_map = {}
        for chunk in similar_chunks:
            doc_name = chunk.get("document_name")
            if doc_name and doc_name not in pdf_doc_map:
                # Get PDF ID from database
                pdf_id = await hasura_client.get_pdf_id_by_name(doc_name)
                if pdf_id:
                    pdf_doc_map[doc_name] = pdf_id
        
        # Return answer with source information
        logger.info("🤖 Answer from RAG")
        response_data = {
            "success": True,
            "question": request.question,
            "answer": answer,
            "source": "rag",
            "data_source": "RAG",
            "chunks_used": len(similar_chunks),
            "source_documents": [
                {
                    "document": chunk.get("document_name"),
                    "page": chunk.get("page_number"),
                    "relevance_score": round(chunk.get("score", 0), 4),
                    "pdf_id": pdf_doc_map.get(chunk.get("document_name"))
                } for chunk in similar_chunks
            ]
        }
        
        # Save question and answer to chat history
        if actual_session_id and request.user_id:
            try:
                message_id = f"msg_{uuid.uuid4().hex[:16]}"
                logger.info(f"💾 Saving RAG message (session={actual_session_id}, user={request.user_id})")
                await hasura_client.add_chat_message(
                    message_id=message_id,
                    session_id=actual_session_id,
                    user_id=request.user_id,
                    question=request.question,
                    answer=answer,
                    source="rag"
                )
                logger.info(f"✅ RAG message saved")
            except Exception as e:
                logger.error(f"❌ Failed to save RAG chat message: {e}", exc_info=True)
        else:
            logger.warning(f"⚠️  Skipping RAG save - session_id={actual_session_id}, user_id={request.user_id}")
        
        return response_data
    
    except Exception as e:
        logger.error(f"❌ Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/cache/info", response_model=dict)
async def get_cache_info():
    """
    Get Redis cache statistics and information (Requires Authentication)
    
    Returns:
    - connected: Whether Redis is connected
    - faq_cached_items: Number of cached FAQ answers
    - redis_memory_used: Memory usage by Redis
    - redis_version: Redis server version
    - uptime_seconds: Redis server uptime
    """
    try:
        redis_cache = get_redis_cache()
        cache_info = redis_cache.get_cache_info()
        
        if cache_info:
            logger.info(f"Cache info retrieved: {cache_info['faq_cached_items']} items cached")
            return {
                "success": True,
                "cache_info": cache_info
            }
        else:
            logger.warning("Redis cache not available")
            return {
                "success": False,
                "cache_info": {
                    "connected": False,
                    "message": "Redis cache not available"
                }
            }
    except Exception as e:
        logger.error(f"❌ Error getting cache info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache info: {str(e)}"
        )


@router.delete("/cache/clear", response_model=dict)
async def clear_faq_cache():
    """
    Clear all FAQ cache entries (use with caution - Requires Authentication)
    
    Returns:
    - success: Whether cache was cleared
    - message: Status message
    """
    try:
        redis_cache = get_redis_cache()
        result = redis_cache.clear_all()
        
        if result:
            logger.info("✅ FAQ cache cleared successfully")
            return {
                "success": True,
                "message": "All FAQ cache entries cleared successfully"
            }
        else:
            logger.warning("Redis cache not available for clearing")
            return {
                "success": False,
                "message": "Redis cache not available"
            }
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

