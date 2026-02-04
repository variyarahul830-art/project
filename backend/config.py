import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # ==================== DATABASE ====================
    # Using Docker PostgreSQL Container (same as Hasura)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "hasuradb")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # ==================== HASURA ====================
    # Using Docker Hasura Container
    HASURA_URL: str = os.getenv("HASURA_URL", "http://localhost:8081/v1/graphql")
    HASURA_ADMIN_SECRET: str = os.getenv("HASURA_ADMIN_SECRET", "myadminsecret")
    
    # ==================== SERVER ====================
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # ==================== MINIO ====================
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_PUBLIC_ENDPOINT: str = os.getenv("MINIO_PUBLIC_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "pdf")
    MINIO_USE_SSL: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    
    # ==================== MILVUS ====================
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_COLLECTION_NAME: str = os.getenv("MILVUS_COLLECTION_NAME", "pdf_embeddings")
    
    # ==================== REDIS ====================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_FAQ_TTL_MINUTES: int = int(os.getenv("REDIS_FAQ_TTL_MINUTES", "20"))
    
    # ==================== EMBEDDING ====================
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # ==================== LLM ====================
    LLM_USE_API: bool = os.getenv("LLM_USE_API", "true").lower() == "true"
    LLM_API_PROVIDER: str = os.getenv("LLM_API_PROVIDER", "huggingface")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "not_needed")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/Llama-2-7b-chat-hf")
    LLM_MAX_LENGTH: int = int(os.getenv("LLM_MAX_LENGTH", "1000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Text Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))  # in tokens
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))  # in tokens
    
    # Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
