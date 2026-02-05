"""
Milvus Vector Database Service
Handles connection and operations with Milvus
"""

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MilvusService:
    """Service for Milvus vector database operations"""
    
    def __init__(self, host: str = "localhost", port: int = 19530, collection_name: str = "pdf_embeddings"):
        """
        Initialize MilvusService
        
        Args:
            host: Milvus host
            port: Milvus port
            collection_name: Name of the collection to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to Milvus"""
        try:
            # Disconnect any existing connections
            connections.disconnect(alias="default")
        except Exception:
            pass
        
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"✅ Connected to Milvus at {self.host}:{self.port}")
            
            # Try to load existing collection
            if utility.has_collection(self.collection_name):
                self.collection = Collection(name=self.collection_name)
                logger.info(f"✓ Loaded existing collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Milvus: {str(e)}")
            raise
    
    def create_collection(self, embedding_dim: int = 384):
        """
        Create collection for PDF embeddings if it doesn't exist
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                logger.info(f"✓ Collection '{self.collection_name}' already exists, loading it...")
                self.collection = Collection(name=self.collection_name)
                logger.info(f"✓ Collection '{self.collection_name}' loaded successfully")
                return
            
            logger.info(f"Creating new collection: {self.collection_name} with dimension {embedding_dim}")
            
            # Define collection schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim),
                FieldSchema(name="text_chunk", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="page_number", dtype=DataType.INT32),
                FieldSchema(name="chunk_index", dtype=DataType.INT32),
                FieldSchema(name="token_count", dtype=DataType.INT32),
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="PDF document embeddings with metadata"
            )
            
            # Create collection
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )
            logger.info(f"✓ Collection schema created: {self.collection_name}")
            
            # Create index on embedding field
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            logger.info(f"Creating index on embedding field...")
            self.collection.create_index(field_name="embedding", index_params=index_params)
            
            logger.info(f"✅ Collection '{self.collection_name}' created successfully with index")
            
        except Exception as e:
            logger.error(f"❌ Error creating collection: {str(e)}")
            raise
    
    def insert_embeddings(self, embeddings_data: List[Dict[str, Any]]) -> int:
        """
        Insert embedding vectors and metadata into Milvus
        
        Args:
            embeddings_data: List of dicts with keys:
                - 'embedding': numpy array of embedding vector
                - 'text_chunk': text content
                - 'document_name': name of source document
                - 'page_number': page number
                - 'chunk_index': index of chunk
                - 'token_count': number of tokens
                
        Returns:
            Number of inserted vectors
        """
        if not embeddings_data:
            logger.warning("No embeddings data to insert")
            return 0
        
        if self.collection is None:
            raise Exception("Collection not initialized")
        
        try:
            logger.info(f"Preparing {len(embeddings_data)} embeddings for insertion...")
            
            # Prepare data in list-of-lists format as Milvus expects
            # Format: [[id_field_data], [embedding_field_data], [text_chunk_field_data], ...]
            embeddings_list = []
            text_chunks_list = []
            document_names_list = []
            page_numbers_list = []
            chunk_indices_list = []
            token_counts_list = []
            
            for idx, item in enumerate(embeddings_data):
                # Convert embedding to list if it's numpy array and ensure float32
                embedding = item['embedding']
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.astype(np.float32).tolist()
                elif isinstance(embedding, list):
                    embedding = [float(x) for x in embedding]
                
                logger.info(f"[Insert] Item {idx}: embedding_len={len(embedding)}, text_len={len(item['text_chunk'])}, page={item['page_number']}")
                
                embeddings_list.append(embedding)
                text_chunks_list.append(item['text_chunk'][:65535])  # Ensure within max_length
                document_names_list.append(item['document_name'][:255])  # Ensure within max_length
                page_numbers_list.append(int(item['page_number']))
                chunk_indices_list.append(int(item['chunk_index']))
                token_counts_list.append(int(item['token_count']))
            
            # Create data structure in the format Milvus expects
            data = [
                embeddings_list,
                text_chunks_list,
                document_names_list,
                page_numbers_list,
                chunk_indices_list,
                token_counts_list,
            ]
            
            logger.info(f"Data structure prepared (list-of-lists format):")
            logger.info(f"  - embeddings count: {len(embeddings_list)}")
            logger.info(f"  - text_chunks count: {len(text_chunks_list)}")
            logger.info(f"  - page_numbers: {page_numbers_list}")
            logger.info(f"  - chunk_indices: {chunk_indices_list}")
            logger.info(f"  - token_counts: {token_counts_list}")
            logger.info(f"  - document_names: {document_names_list}")
            if len(embeddings_list) > 0:
                logger.info(f"  - First embedding: length={len(embeddings_list[0])}, sample=[{embeddings_list[0][0]}, {embeddings_list[0][1]}, ...]")
            
            logger.info(f"Inserting {len(embeddings_data)} embeddings into collection '{self.collection_name}'...")
            
            # Insert into collection
            result = self.collection.insert(data)
            logger.info(f"✓ Insert operation returned: {result}")
            
            # Flush to make sure data is persisted
            logger.info(f"Flushing data to disk...")
            self.collection.flush()
            logger.info(f"✓ Data flushed successfully")
            
            logger.info(f"✅ Successfully inserted {len(embeddings_data)} embeddings into Milvus collection '{self.collection_name}'")
            return len(embeddings_data)
            
        except Exception as e:
            logger.error(f"❌ Error inserting embeddings: {str(e)}")
            raise
    
    def search_embeddings(self, query_embedding: np.ndarray, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            limit: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if self.collection is None:
            raise Exception("Collection not initialized")
        
        # Convert embedding to list if needed
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()
        
        # Load collection (required for search)
        self.collection.load()
        
        # Search
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["text_chunk", "document_name", "page_number", "chunk_index", "token_count"]
        )
        
        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "score": hit.score,
                    "text_chunk": hit.entity.get("text_chunk"),
                    "document_name": hit.entity.get("document_name"),
                    "page_number": hit.entity.get("page_number"),
                    "chunk_index": hit.entity.get("chunk_index"),
                    "token_count": hit.entity.get("token_count"),
                })
        
        return formatted_results
    
    def delete_by_document_name(self, document_name: str) -> int:
        """
        Delete all embeddings for a specific document
        
        Args:
            document_name: Name of the document to delete embeddings for
            
        Returns:
            Number of embeddings deleted
        """
        try:
            logger.info(f"Deleting embeddings for document: {document_name}")
            
            # Load collection if not already loaded
            if self.collection is None:
                if utility.has_collection(self.collection_name):
                    self.collection = Collection(name=self.collection_name)
                    logger.info(f"✓ Collection '{self.collection_name}' loaded for deletion")
                else:
                    logger.warning(f"Collection '{self.collection_name}' does not exist")
                    return 0
            
            # Load collection to perform delete operation
            self.collection.load()
            logger.info(f"Collection loaded and ready for deletion")
            
            # Delete entities where document_name matches
            expr = f'document_name == "{document_name}"'
            logger.info(f"Delete expression: {expr}")
            
            # Get count before deletion
            query_result = self.collection.query(expr=expr, output_fields=["id"], limit=10000)
            count_before = len(query_result)
            logger.info(f"Found {count_before} embeddings to delete for document '{document_name}'")
            
            if count_before == 0:
                logger.warning(f"No embeddings found for document '{document_name}'")
                return 0
            
            # Perform deletion
            self.collection.delete(expr=expr)
            logger.info(f"Delete operation executed for document '{document_name}'")
            
            # Flush to ensure deletion is persisted
            self.collection.flush()
            logger.info(f"✅ Successfully deleted {count_before} embeddings for document '{document_name}'")
            
            return count_before
            
        except Exception as e:
            logger.error(f"❌ Error deleting embeddings for document '{document_name}': {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        if self.collection is None:
            return {}
        
        return {
            "collection_name": self.collection_name,
            "num_entities": self.collection.num_entities,
        }
