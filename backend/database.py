from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def ensure_pdf_schema():
    """Add missing pdf_documents.minio_path column/index if the table already exists."""
    inspector = inspect(engine)
    if "pdf_documents" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("pdf_documents")}
    if "minio_path" in columns:
        return

    # Add the column and a unique index so uploads using minio_path work without recreating the table.
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE pdf_documents ADD COLUMN IF NOT EXISTS minio_path VARCHAR(500)"))
        conn.execute(text("UPDATE pdf_documents SET minio_path = CONCAT('pdf/', id, '_', filename) WHERE minio_path IS NULL"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_pdf_documents_minio_path ON pdf_documents(minio_path)"))

def get_db():
    """Dependency injection for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
