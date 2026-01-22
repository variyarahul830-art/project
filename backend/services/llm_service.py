"""
LLM Service for answering questions using Hugging Face Inference API (OpenAI-compatible endpoint)
"""

from typing import List, Dict, Any, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations using Hugging Face Inference API"""
    
    def __init__(self, 
                 huggingface_token: str,
                 model_name: str = "openai/gpt-oss-120b:groq"):
        """
        Initialize LLMService with Hugging Face OpenAI-compatible endpoint
        
        Args:
            huggingface_token: Hugging Face API token (required)
            model_name: Model to use from Hugging Face (default: openai/gpt-oss-120b:groq)
                       Other working options:
                       - "meta-llama/Llama-2-7b-chat-hf"
                       - "mistralai/Mistral-7B-Instruct-v0.2"
        """
        if not huggingface_token:
            raise ValueError("Hugging Face token is required!")
        
        self.huggingface_token = huggingface_token
        self.model_name = model_name
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        
        logger.info(f"LLMService initialized: provider=HuggingFace, model={model_name}")
    
    def generate_answer_with_context(self, 
                                    question: str,
                                    context_chunks: List[Dict[str, Any]],
                                    system_prompt: Optional[str] = None,
                                    max_length: int = 512,
                                    temperature: float = 0.7) -> str:
        """
        Generate an answer using the question and context chunks
        
        Args:
            question: User's question
            context_chunks: List of relevant chunks from Milvus
            system_prompt: Optional custom system prompt for the LLM
            max_length: Maximum length of generated text
            temperature: Temperature for generation (0-1)
            
        Returns:
            Generated answer from LLM
        """
        try:
            return self._generate_with_huggingface(question, context_chunks, system_prompt, max_length, temperature)
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {str(e)}")
            return self._create_simple_answer(question, context_chunks)
    
    def _generate_with_huggingface(self, question: str, context_chunks: List[Dict[str, Any]], 
                                  system_prompt: Optional[str] = None,
                                  max_length: int = 2048, temperature: float = 0.7) -> str:
        """Generate answer using Hugging Face OpenAI-compatible Chat API"""
        try:
            # Build context with all chunks
            context_text = self._build_context(context_chunks)
            
            logger.info(f"Calling Hugging Face API for model: {self.model_name}")
            logger.info(f"Processing {len(context_chunks)} chunks with question: {question[:50]}...")
            
            # Default system prompt with formatting rules
            default_system_prompt = """You are a helpful AI assistant. Answer questions based on the provided context. Follow these formatting rules STRICTLY:

FORMATTING RULES (MANDATORY):
1. Start with a direct, concise answer (1-2 sentences)
2. Use markdown bullet points (- or •) for lists
3. Use **bold** for important terms and section headers
4. Use *italic* for emphasis
5. Use numbered lists (1. 2. 3.) for steps
6. Use line breaks between sections
7. Use markdown code blocks with triple backticks for code
8. Use > for blockquotes
9. NEVER use HTML or tables - convert to bullet points
10. Be specific and cite document sources

EXAMPLE FORMAT:
**Answer Summary**
Your direct answer here in 1-2 sentences.

**Key Points**
- Point 1
- Point 2
- Point 3

**Details**
1. First step
2. Second step
3. Third step

**Sources**
- Document name, Page X"""
            
            # Use provided system prompt or default
            final_system_prompt = system_prompt if system_prompt else default_system_prompt
            
            # Prepare API request using OpenAI-compatible format
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": final_system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"""Based on the following context chunks from documents, answer the user's question precisely and thoroughly using markdown formatting.

CONTEXT CHUNKS:
{context_text}

USER QUESTION: {question}

Remember: Use markdown formatting (**, -, >, etc.) for proper structure."""
                    }
                ],
                "max_tokens": max_length,
                "temperature": temperature,
                "top_p": 0.95, 
            }
            
            # Make API request
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle OpenAI-compatible response format
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0].get("message", {}).get("content", "")
                else:
                    answer = ""
                
                answer = answer.strip()
                
                logger.info(f"✅ Hugging Face answer generated (length: {len(answer)})")
                return answer if answer else self._create_simple_answer(question, context_chunks)
            else:
                logger.error(f"❌ Hugging Face API error: {response.status_code} - {response.text}")
                return self._create_simple_answer(question, context_chunks)
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Request timeout - model might be loading, trying fallback")
            return self._create_simple_answer(question, context_chunks)
        except Exception as e:
            logger.error(f"❌ Error with Hugging Face: {str(e)}")
            return self._create_simple_answer(question, context_chunks)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a detailed prompt that instructs the LLM to analyze and refine chunks"""
        prompt = f"""Based on the following context chunks from documents, answer the user's question precisely and thoroughly.

Instructions:
1. Analyze each chunk provided
2. Identify relevant information that answers the question
3. Refine and synthesize the information into a clear, coherent answer
4. Cite which chunk(s) you used if relevant
5. If information is incomplete, indicate what's missing

CONTEXT CHUNKS:
{context}

USER QUESTION: {question}

REFINED ANSWER:"""
        return prompt
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build detailed context string from all chunks with source information"""
        if not chunks:
            return "No context available."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get('text_chunk', '')
            doc_name = chunk.get('document_name', 'Unknown')
            page_num = chunk.get('page_number', 'Unknown')
            score = chunk.get('score', 0)
            
            context_part = f"""
CHUNK {i}: [Source: {doc_name}, Page: {page_num}, Relevance Score: {score:.4f}]
{text}
---"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_simple_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """Create a simple answer by combining relevant chunks when LLM fails"""
        logger.info("Creating simple answer from context chunks")
        
        try:
            # Combine the most relevant chunks
            answer_parts = []
            for i, chunk in enumerate(chunks[:3], 1):  # Use top 3 chunks
                text = chunk.get('text_chunk', '')
                doc_name = chunk.get('document_name', 'Unknown')
                page_num = chunk.get('page_number', 'Unknown')
                if text:
                    answer_parts.append(f"[{doc_name}, Page {page_num}]: {text[:300]}")
            
            if answer_parts:
                combined = "\n".join(answer_parts)
                answer = f"Based on the documents:\n\n{combined}"
                return answer
            else:
                return "I found relevant documents but could not extract specific information to answer your question."
        except Exception as e:
            logger.error(f"Error creating simple answer: {str(e)}")
            return "I found relevant documents but encountered an error generating an answer."


