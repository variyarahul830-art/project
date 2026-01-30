"""
Text Chunking Service
Splits text into overlapping chunks based on token count
"""

import tiktoken
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Service for splitting text into chunks with overlap"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, model: str = "cl100k_base"):
        """
        Initialize TextChunker
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of overlapping tokens between chunks
            model: Tiktoken encoding model
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        tokens = self.encoding.encode(text)
        return len(tokens)
    
    def chunk_text(self, text: str, page_number: int = 1, page_count: int = 1) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks based on token count
        
        Args:
            text: Text to chunk
            page_number: Page number this text is from
            page_count: Total pages in document
            
        Returns:
            List of dicts with keys: 'text', 'chunk_index', 'page_number', 'page_count'
        """
        # Encode text to tokens
        logger.info(f"[chunk_text] Encoding {len(text)} chars for page {page_number}...")
        tokens = self.encoding.encode(text)
        logger.info(f"[chunk_text] Encoded to {len(tokens)} tokens (chunk_size: {self.chunk_size}, overlap: {self.chunk_overlap})")
        
        if len(tokens) == 0:
            logger.warning(f"[chunk_text] No tokens for page {page_number}, returning empty list")
            return []
        
        chunks = []
        chunk_index = 0
        
        start_idx = 0
        iteration = 0
        max_iterations = len(tokens) * 2  # Safety limit to prevent infinite loops
        
        while start_idx < len(tokens):
            iteration += 1
            logger.info(f"[chunk_text] Iteration {iteration}: start_idx={start_idx}, end_idx will be calculated...")
            
            if iteration > max_iterations:
                logger.error(f"[chunk_text] Max iterations ({max_iterations}) exceeded! Breaking loop to prevent infinite loop.")
                break
            
            # Get chunk tokens
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            
            logger.info(f"[chunk_text] Iteration {iteration}: chunk_tokens length={len(chunk_tokens)}, start={start_idx}, end={end_idx}")
            
            # Decode tokens back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append({
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'page_number': page_number,
                    'page_count': page_count,
                    'token_count': len(chunk_tokens)
                })
                logger.debug(f"[chunk_text] Created chunk {chunk_index}: {len(chunk_text)} chars, {len(chunk_tokens)} tokens")
                chunk_index += 1
            
            # Check if we're at the end
            if end_idx >= len(tokens):
                logger.info(f"[chunk_text] Reached end of tokens at iteration {iteration}")
                break
            
            # Move start position with overlap
            start_idx = end_idx - self.chunk_overlap
            logger.info(f"[chunk_text] Iteration {iteration}: Moving start_idx to {start_idx} (overlap={self.chunk_overlap})")
        
        logger.info(f"[chunk_text] Page {page_number} produced {len(chunks)} chunks after {iteration} iterations")
        return chunks
    
    def chunk_documents(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple pages of text
        
        Args:
            pages_data: List of dicts with 'text', 'page_number', 'page_count'
            
        Returns:
            List of chunked data with metadata
        """
        all_chunks = []
        global_chunk_index = 0
        
        for page_data in pages_data:
            page_chunks = self.chunk_text(
                text=page_data['text'],
                page_number=page_data['page_number'],
                page_count=page_data['page_count']
            )
            
            # Update global chunk index and add page data
            for chunk in page_chunks:
                chunk['global_chunk_index'] = global_chunk_index
                all_chunks.append(chunk)
                global_chunk_index += 1
        
        return all_chunks
    
    def chunk_documents_streaming(self, pages_data: List[Dict[str, Any]]):
        """
        Generator that yields chunks as they are created (streaming)
        Allows processing chunks immediately without waiting for all chunks to be ready
        
        Args:
            pages_data: List of dicts with 'text', 'page_number', 'page_count'
            
        Yields:
            Dict with chunked data and metadata
        """
        global_chunk_index = 0
        logger.info(f"[TextChunker] Starting streaming chunk generation for {len(pages_data)} pages...")
        
        for page_idx, page_data in enumerate(pages_data, start=1):
            page_text = page_data['text']
            logger.info(f"[TextChunker] Processing page {page_idx}: {len(page_text)} chars, {page_data.get('page_number', 'unknown')} page_number")
            
            page_chunks = self.chunk_text(
                text=page_text,
                page_number=page_data['page_number'],
                page_count=page_data['page_count']
            )
            
            logger.info(f"[TextChunker] Page {page_idx} generated {len(page_chunks)} chunks")
            
            # Yield each chunk immediately as it's created
            for chunk_idx, chunk in enumerate(page_chunks, start=1):
                chunk['global_chunk_index'] = global_chunk_index
                logger.info(f"[TextChunker] Yielding chunk {chunk_idx} from page {page_idx} (global_index: {global_chunk_index})")
                yield chunk
                global_chunk_index += 1
        
        logger.info(f"[TextChunker] Streaming generation complete. Total chunks yielded: {global_chunk_index}")
    
    def chunk_documents_with_cross_page_overlap(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple pages with overlap that can span across page boundaries
        
        This method allows chunks to overlap across page boundaries, unlike the standard
        chunk_documents method which resets overlap for each new page.
        
        Args:
            pages_data: List of dicts with 'text', 'page_number', 'page_count'
            
        Returns:
            List of chunked data with metadata including page_numbers that chunk spans
        """
        # Concatenate all text and track page boundaries
        all_tokens = []
        page_boundaries = []  # Track where each page starts in token stream
        
        logger.info(f"[chunk_documents_with_cross_page_overlap] Starting cross-page overlap chunking for {len(pages_data)} pages...")
        
        for page_data in pages_data:
            page_boundaries.append(len(all_tokens))
            tokens = self.encoding.encode(page_data['text'])
            all_tokens.extend(tokens)
            logger.info(f"[chunk_documents_with_cross_page_overlap] Page {page_data['page_number']}: {len(tokens)} tokens (boundary at {page_boundaries[-1]})")
        
        logger.info(f"[chunk_documents_with_cross_page_overlap] Total tokens: {len(all_tokens)}")
        
        # Now chunk the entire token stream with overlap that spans pages
        chunks = []
        chunk_index = 0
        start_idx = 0
        iteration = 0
        max_iterations = len(all_tokens) * 2
        
        while start_idx < len(all_tokens):
            iteration += 1
            
            if iteration > max_iterations:
                logger.error(f"[chunk_documents_with_cross_page_overlap] Max iterations ({max_iterations}) exceeded! Breaking loop.")
                break
            
            end_idx = min(start_idx + self.chunk_size, len(all_tokens))
            chunk_tokens = all_tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Determine which page(s) this chunk belongs to
            pages_in_chunk = []
            for i, boundary in enumerate(page_boundaries):
                next_boundary = page_boundaries[i + 1] if i + 1 < len(page_boundaries) else len(all_tokens)
                if start_idx < next_boundary and end_idx > boundary:
                    pages_in_chunk.append(pages_data[i]['page_number'])
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'page_numbers': pages_in_chunk,  # Can span multiple pages
                    'token_count': len(chunk_tokens),
                    'spans_multiple_pages': len(pages_in_chunk) > 1
                })
                logger.info(f"[chunk_documents_with_cross_page_overlap] Chunk {chunk_index}: pages {pages_in_chunk}, {len(chunk_tokens)} tokens, spans_multiple={len(pages_in_chunk) > 1}")
                chunk_index += 1
            
            if end_idx >= len(all_tokens):
                logger.info(f"[chunk_documents_with_cross_page_overlap] Reached end of tokens at iteration {iteration}")
                break
            
            start_idx = end_idx - self.chunk_overlap
        
        logger.info(f"[chunk_documents_with_cross_page_overlap] Complete. Created {len(chunks)} chunks across {len(pages_data)} pages")
        return chunks
    
    def chunk_documents_with_cross_page_overlap_streaming(self, pages_data: List[Dict[str, Any]]):
        """
        Generator that yields chunks with cross-page overlap as they are created (streaming)
        
        Allows processing chunks immediately without waiting for all chunks to be ready.
        Chunks can overlap across page boundaries.
        
        Args:
            pages_data: List of dicts with 'text', 'page_number', 'page_count'
            
        Yields:
            Dict with chunked data and metadata including page_numbers that chunk spans
        """
        # Concatenate all text and track page boundaries
        all_tokens = []
        page_boundaries = []  # Track where each page starts in token stream
        
        logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Starting streaming cross-page overlap chunking for {len(pages_data)} pages...")
        
        for page_data in pages_data:
            page_boundaries.append(len(all_tokens))
            tokens = self.encoding.encode(page_data['text'])
            all_tokens.extend(tokens)
            logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Page {page_data['page_number']}: {len(tokens)} tokens (boundary at {page_boundaries[-1]})")
        
        logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Total tokens: {len(all_tokens)}")
        
        # Now chunk the entire token stream with overlap that spans pages
        chunk_index = 0
        start_idx = 0
        iteration = 0
        max_iterations = len(all_tokens) * 2
        
        while start_idx < len(all_tokens):
            iteration += 1
            
            if iteration > max_iterations:
                logger.error(f"[chunk_documents_with_cross_page_overlap_streaming] Max iterations ({max_iterations}) exceeded! Breaking loop.")
                break
            
            end_idx = min(start_idx + self.chunk_size, len(all_tokens))
            chunk_tokens = all_tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Determine which page(s) this chunk belongs to
            pages_in_chunk = []
            for i, boundary in enumerate(page_boundaries):
                next_boundary = page_boundaries[i + 1] if i + 1 < len(page_boundaries) else len(all_tokens)
                if start_idx < next_boundary and end_idx > boundary:
                    pages_in_chunk.append(pages_data[i]['page_number'])
            
            if chunk_text.strip():
                chunk = {
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'page_numbers': pages_in_chunk,  # Can span multiple pages
                    'token_count': len(chunk_tokens),
                    'spans_multiple_pages': len(pages_in_chunk) > 1
                }
                logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Yielding chunk {chunk_index}: pages {pages_in_chunk}, {len(chunk_tokens)} tokens, spans_multiple={len(pages_in_chunk) > 1}")
                yield chunk
                chunk_index += 1
            
            if end_idx >= len(all_tokens):
                logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Reached end of tokens at iteration {iteration}")
                break
            
            start_idx = end_idx - self.chunk_overlap
        
        logger.info(f"[chunk_documents_with_cross_page_overlap_streaming] Complete. Total chunks yielded: {chunk_index}")
