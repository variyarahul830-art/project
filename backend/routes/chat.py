from fastapi import APIRouter, HTTPException, status
from config import settings
from schemas import ChatRequest
from services.embeddings import EmbeddingGenerator
from services.milvus_service import MilvusService
from services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=dict)
async def chat(request: ChatRequest):
    """Answer a question using PDF-based RAG (Milvus + LLM)."""
    try:
        logger.info(f"Processing question via RAG: {request.question}")

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
        
        # Generate answer using LLM with context
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
