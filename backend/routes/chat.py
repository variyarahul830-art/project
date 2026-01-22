from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from config import settings
from schemas import ChatRequest
import crud
from services.embeddings import EmbeddingGenerator
from services.milvus_service import MilvusService
from services.llm_service import LLMService
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=dict)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
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
        
        # Step 1: Try exact match on source node (search ALL workflows)
        logger.info("Step 1: Trying exact text match on source nodes across ALL workflows...")
        source_node = crud.get_node_by_text(db, request.question, workflow_id=None)
        
        if source_node:
            logger.info(f"Found exact source node: {source_node.text}")
            target_nodes = crud.get_target_nodes(db, source_node.id)
            
            if target_nodes:
                logger.info(f"Found {len(target_nodes)} target nodes from exact source match")
                clickable_answers = []
                for target_node in target_nodes:
                    further_nodes = crud.get_further_options(db, target_node.id)
                    is_source = len(further_nodes) > 0
                    clickable_answers.append({
                        "text": target_node.text,
                        "id": target_node.id,
                        "is_source": is_source
                    })
                
                return {
                    "success": True,
                    "question": source_node.text,
                    "answers": [node.text for node in target_nodes],
                    "target_nodes": [{"id": node.id, "text": node.text, "is_source": clickable_answers[[t.id for t in target_nodes].index(node.id)]["is_source"]} for node in target_nodes],
                    "source": "knowledge_graph",
                    "count": len(target_nodes)
                }
        
        # Step 2: Try partial/fuzzy matching on all source nodes (search ALL workflows)
        logger.info("Step 2: Trying partial text match on source nodes across ALL workflows...")
        matching_nodes = crud.search_nodes_by_text(db, request.question, workflow_id=None)
        
        if matching_nodes:
            logger.info(f"Found {len(matching_nodes)} matching source nodes via partial search")
            # Get all target nodes for all matching nodes
            all_target_nodes = []
            for source in matching_nodes:
                targets = crud.get_target_nodes(db, source.id)
                all_target_nodes.extend(targets)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_targets = []
            for node in all_target_nodes:
                if node.id not in seen:
                    seen.add(node.id)
                    unique_targets.append(node)
            
            if unique_targets:
                logger.info(f"Found {len(unique_targets)} unique target nodes from partial source matches")
                clickable_answers = []
                for target_node in unique_targets:
                    further_nodes = crud.get_further_options(db, target_node.id)
                    is_source = len(further_nodes) > 0
                    clickable_answers.append({
                        "text": target_node.text,
                        "id": target_node.id,
                        "is_source": is_source
                    })
                
                return {
                    "success": True,
                    "question": request.question,
                    "answers": [node.text for node in unique_targets],
                    "target_nodes": [{"id": node.id, "text": node.text, "is_source": clickable_answers[[t.id for t in unique_targets].index(node.id)]["is_source"]} for node in unique_targets],
                    "source": "knowledge_graph",
                    "count": len(unique_targets)
                }
            else:
                logger.info("Partial match found source nodes, but they have no target connections")
        
        logger.info("No nodes found in knowledge graph, trying RAG approach with PDF embeddings")
        
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
        
        # Return answer with source information
        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "source": "rag",
            "chunks_used": len(similar_chunks),
            "source_documents": [
                {
                    "document": chunk.get("document_name"),
                    "page": chunk.get("page_number"),
                    "relevance_score": round(chunk.get("score", 0), 4)
                } for chunk in similar_chunks
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )
