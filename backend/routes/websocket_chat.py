from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging
import json
import uuid
from datetime import datetime
import asyncio
import redis.asyncio as aioredis
from services import hasura_client
from services.embeddings import EmbeddingGenerator
from services.milvus_service import MilvusService
from services.llm_service import LLMService
from services.redis_cache import get_redis_cache
from tasks.llm_tasks import generate_llm_answer_task
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Store active WebSocket connections mapped by client_id
# Also track pending tasks: task_id -> client_id
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_tasks: Dict[str, str] = {}  # task_id -> client_id

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
        
        # Clean up pending tasks for this client
        tasks_to_remove = [task_id for task_id, cid in self.pending_tasks.items() if cid == client_id]
        for task_id in tasks_to_remove:
            del self.pending_tasks[task_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    def register_pending_task(self, task_id: str, client_id: str):
        """Register a pending task for a client"""
        self.pending_tasks[task_id] = client_id
    
    async def send_to_task_client(self, task_id: str, message: dict):
        """Send message to the client waiting for this task"""
        if task_id in self.pending_tasks:
            client_id = self.pending_tasks[task_id]
            await self.send_message(client_id, message)
            del self.pending_tasks[task_id]
            logger.info(f"Sent result to client for task {task_id}")
        else:
            logger.warning(f"No client found for task {task_id}")
    
    async def subscribe_to_redis_results(self, client_id: str, websocket: WebSocket):
        """Subscribe to Redis pub/sub for task results for this client"""
        try:
            redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
                decode_responses=True
            )
            pubsub = redis_client.pubsub()
            channel = f"rag_result:{client_id}"
            await pubsub.subscribe(channel)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await self.send_message(client_id, data)
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")
        except Exception as e:
            logger.error(f"Error subscribing to Redis: {e}")

manager = ConnectionManager()


async def process_chat_message(question: str, user_id: str, session_id: str, client_id: str = None):
    """
    Process chat message using the same logic as the REST API
    Returns the response data
    """
    try:
        logger.info(f"Question: {question[:80]}...")
        
        # Resolve session_id if numeric
        actual_session_id = session_id
        if session_id and user_id:
            if session_id.isdigit():
                sessions = await hasura_client.get_user_chat_sessions(user_id)
                session = next((s for s in sessions if str(s.get("id")) == session_id), None)
                if session:
                    actual_session_id = session.get("session_id")

        # Step 1: Try exact match on source node
        source_node = await hasura_client.get_node_by_text(question, workflow_id=None)
        
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
                
                # Save to database
                if actual_session_id and user_id:
                    try:
                        message_id = f"msg_{uuid.uuid4().hex[:16]}"
                        await hasura_client.add_chat_message(
                            message_id=message_id,
                            session_id=actual_session_id,
                            user_id=user_id,
                            question=question,
                            answer=json.dumps(response_data),
                            source="knowledge_graph"
                        )
                    except Exception as e:
                        logger.error(f"Failed to save chat message: {e}")
                
                return response_data

        # Step 2: Try partial/fuzzy matching
        matching_nodes = await hasura_client.search_nodes_by_text(question, workflow_id=None)
        
        if matching_nodes:
            all_target_nodes = []
            for source in matching_nodes:
                targets = await hasura_client.get_target_nodes(source["id"])
                all_target_nodes.extend(targets)
            
            # Remove duplicates
            seen = set()
            unique_targets = []
            for node in all_target_nodes:
                if node["id"] not in seen:
                    seen.add(node["id"])
                    unique_targets.append(node)
            
            if unique_targets:
                clickable_answers = []
                for target_node in unique_targets:
                    further_nodes = await hasura_client.get_further_options(target_node["id"])
                    is_source = len(further_nodes) > 0 if further_nodes else False
                    clickable_answers.append({
                        "text": target_node["text"],
                        "id": target_node["id"],
                        "is_source": is_source
                    })
                
                response_data = {
                    "success": True,
                    "question": question,
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
                
                # Save to database
                if actual_session_id and user_id:
                    try:
                        message_id = f"msg_{uuid.uuid4().hex[:16]}"
                        await hasura_client.add_chat_message(
                            message_id=message_id,
                            session_id=actual_session_id,
                            user_id=user_id,
                            question=question,
                            answer=json.dumps(response_data),
                            source="knowledge_graph"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to save chat message: {e}")
                
                return response_data

        # Step 3: Check Redis cache and FAQs
        redis_cache = get_redis_cache()
        
        cached_answer = redis_cache.get(question)
        if cached_answer:
            logger.info("Answer from REDIS")
            response_data = {
                "success": True,
                "question": question,
                "answer": cached_answer.get("answer"),
                "source": cached_answer.get("source"),
                "faq_id": cached_answer.get("faq_id"),
                "category": cached_answer.get("category"),
                "from_cache": True,
            }
            
            # Save to database
            if actual_session_id and user_id:
                try:
                    message_id = f"msg_{uuid.uuid4().hex[:16]}"
                    await hasura_client.add_chat_message(
                        message_id=message_id,
                        session_id=actual_session_id,
                        user_id=user_id,
                        question=question,
                        answer=cached_answer.get("answer"),
                        source=cached_answer.get("source")
                    )
                except Exception as e:
                    logger.warning(f"Failed to save chat message: {e}")
            
            return response_data

        # Check FAQs
        faqs = await hasura_client.search_faq_partial(question)
        if faqs and len(faqs) > 0:
            logger.info("Answer from FAQ")
            best_faq = faqs[0]
            response_data = {
                "success": True,
                "question": question,
                "answer": best_faq.get("answer"),
                "source": "faq",
                "faq_id": best_faq.get("id"),
                "category": best_faq.get("category"),
            }
            
            # Cache the FAQ answer
            redis_cache.set(question, {
                "answer": best_faq.get("answer"),
                "source": "faq",
                "faq_id": best_faq.get("id"),
                "category": best_faq.get("category"),
            })
            
            # Save to database
            if actual_session_id and user_id:
                try:
                    message_id = f"msg_{uuid.uuid4().hex[:16]}"
                    await hasura_client.add_chat_message(
                        message_id=message_id,
                        session_id=actual_session_id,
                        user_id=user_id,
                        question=question,
                        answer=best_faq.get("answer"),
                        source="faq"
                    )
                except Exception as e:
                    logger.warning(f"Failed to save chat message: {e}")
            
            return response_data

        # Step 4: RAG fallback - submit async task to RabbitMQ
        logger.info("Submitting to RabbitMQ for LLM processing...")
        try:
            embedding_generator = EmbeddingGenerator()
            milvus_service = MilvusService()
            
            # Get token from settings
            from config import settings
            hf_token = settings.HUGGINGFACE_TOKEN if hasattr(settings, 'HUGGINGFACE_TOKEN') else None
            if not hf_token:
                logger.error("HUGGINGFACE_TOKEN not configured in settings")
                return {
                    "success": False,
                    "question": question,
                    "answer": None,
                    "source": "rag",
                    "message": "LLM service not properly configured. Please set HUGGINGFACE_TOKEN."
                }
            
            llm_service = LLMService(
                huggingface_token=hf_token,
                model_name=settings.LLM_MODEL if hasattr(settings, 'LLM_MODEL') else "meta-llama/Llama-2-7b-chat-hf"
            )
            
            query_embedding = embedding_generator.generate_embedding(question)
            search_results = milvus_service.search_embeddings(query_embedding, limit=5)
            
            if search_results and len(search_results) > 0:
                message_id = f"msg_{uuid.uuid4().hex[:16]}"
                
                # Register pending task for this client
                if client_id:
                    manager.register_pending_task(message_id, client_id)
                
                # Submit async task to RabbitMQ with client_id for result notification
                logger.info(f"Task submitted: {message_id}")
                celery_task = generate_llm_answer_task.apply_async(
                    args=[
                        question,
                        search_results,
                        actual_session_id,
                        user_id,
                        message_id,
                        client_id  # Pass client_id to task
                    ],
                    queue='llm_tasks',
                    task_id=message_id
                )
                
                # Return pending response to client
                response_data = {
                    "success": True,
                    "question": question,
                    "task_id": celery_task.id,
                    "source": "rag",
                    "status": "processing",
                    "message": "Your question is being processed by the LLM..."
                }
                
                return response_data
            else:
                logger.info("No context found, using LLM without context")
                message_id = f"msg_{uuid.uuid4().hex[:16]}"
                
                # Register pending task
                if client_id:
                    manager.register_pending_task(message_id, client_id)
                
                logger.info(f"Task submitted (no context): {message_id}")
                # Submit task without context
                celery_task = generate_llm_answer_task.apply_async(
                    args=[
                        question,
                        [],
                        actual_session_id,
                        user_id,
                        message_id,
                        client_id  # Pass client_id to task
                    ],
                    queue='llm_tasks',
                    task_id=message_id
                )
                
                response_data = {
                    "success": True,
                    "question": question,
                    "task_id": celery_task.id,
                    "source": "rag",
                    "status": "processing",
                    "message": "Your question is being processed..."
                }
                
                return response_data
        except Exception as e:
            if "Collection not initialized" in str(e):
                logger.info("Milvus collection not initialized - no PDFs uploaded yet. Returning friendly error.")
                return {
                    "success": False,
                    "question": question,
                    "answer": "No documents found in knowledge base. Please upload PDFs first to use the search feature.",
                    "source": "rag",
                    "message": "Collection not initialized"
                }
            else:
                raise

    except Exception as e:
        logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "source": "error"
        }


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with automatic result pushing via Redis pub/sub
    """
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    # Start background task to subscribe to Redis for task results
    redis_subscribe_task = asyncio.create_task(manager.subscribe_to_redis_results(client_id, websocket))
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle normal chat questions
            question = data.get("question", "")
            user_id = data.get("user_id", "")
            session_id = data.get("session_id", "")
            
            if not question:
                await manager.send_message(client_id, {
                    "success": False,
                    "message": "Question is required",
                    "source": "error"
                })
                continue
            
            # Send acknowledgment
            await manager.send_message(client_id, {
                "type": "processing",
                "message": "Processing your question..."
            })
            
            # Process the message
            response = await process_chat_message(question, user_id, session_id, client_id)
            
            # Send response
            await manager.send_message(client_id, {
                "type": "response",
                **response
            })
            
    except WebSocketDisconnect:
        redis_subscribe_task.cancel()
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        redis_subscribe_task.cancel()
        manager.disconnect(client_id)
