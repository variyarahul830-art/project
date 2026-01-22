"""
Embedding Generation Service
Generates embeddings using Sentence Transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Service for generating embeddings using Sentence Transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", huggingface_token: Optional[str] = None):
        """
        Initialize EmbeddingGenerator
        
        Args:
            model_name: Name of the Hugging Face model to use
            huggingface_token: Optional Hugging Face API token for private models or higher rate limits
        """
        self.model_name = model_name
        self.huggingface_token = huggingface_token
        # Load model on first use (lazy loading)
        self.model = None
    
    def _load_model(self):
        """Lazy load the model"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                # Load model with token if provided
                if self.huggingface_token:
                    logger.info(f"Using Hugging Face token for authentication")
                    self.model = SentenceTransformer(self.model_name, token=self.huggingface_token)
                else:
                    self.model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Model loaded successfully: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {str(e)}")
                raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        self._load_model()
        # Don't use convert_to_numpy=True, convert manually
        embedding = self.model.encode(text)
        if hasattr(embedding, 'numpy'):
            embedding = embedding.numpy()
        elif hasattr(embedding, 'cpu'):
            embedding = embedding.cpu().numpy()
        return np.asarray(embedding, dtype=np.float32)
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors as numpy arrays
        """
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        try:
            self._load_model()
            # Encode without convert_to_numpy, convert manually
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Convert to numpy if needed
            if hasattr(embeddings, 'numpy'):
                embeddings = embeddings.numpy()
            elif hasattr(embeddings, 'cpu'):
                embeddings = embeddings.cpu().numpy()
            
            embeddings = np.asarray(embeddings, dtype=np.float32)
            logger.info(f"✅ Successfully generated {len(embeddings)} embeddings")
            
            # Ensure output is a list of arrays
            if len(texts) == 1:
                return [embeddings]
            return [np.asarray(emb, dtype=np.float32) for emb in embeddings]
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    def generate_embedding_for_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings with batching for better performance on small batches
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors as numpy arrays
        """
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
        
        logger.info(f"Generating {len(texts)} embeddings with batch_size={batch_size}...")
        
        try:
            self._load_model()
            # Encode without convert_to_numpy, convert manually
            embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
            
            # Convert to numpy if needed
            if hasattr(embeddings, 'numpy'):
                embeddings = embeddings.numpy()
            elif hasattr(embeddings, 'cpu'):
                embeddings = embeddings.cpu().numpy()
            
            embeddings = np.asarray(embeddings, dtype=np.float32)
            logger.info(f"✅ Successfully generated {len(embeddings)} embeddings")
            
            if len(texts) == 1:
                return [embeddings]
            return [np.asarray(emb, dtype=np.float32) for emb in embeddings]
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        self._load_model()
        # Generate a dummy embedding to get dimension
        dummy_embedding = self.model.encode("test")
        return len(dummy_embedding)
