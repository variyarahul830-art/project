from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base, ensure_pdf_schema
from models import PDFDocument
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure schema drift is corrected before creating tables (handles missing minio_path column)
ensure_pdf_schema()
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI PDF Chatbot API",
    description="REST API for PDF processing and Chat (Workflows/Nodes/Edges/FAQs use Hasura GraphQL)",
    version="3.0.0"
)  

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes after app initialization to avoid circular imports
from routes import chat, pdf, chat_sessions

# Include routers (only PDF and Chat - Workflows/FAQs handled by Hasura)
app.include_router(chat.router)
app.include_router(pdf.router)
app.include_router(chat_sessions.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI PDF Chatbot API is running",
        "hasura_url": settings.HASURA_URL
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI PDF Chatbot API",
        "version": "3.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "PDF": {
                "POST /api/pdf/upload": "Upload PDF",
                "GET /api/pdf/documents": "List PDFs",
                "GET /api/pdf/documents/{id}": "Get PDF",
            },
            "Chat": {
                "POST /api/chat": "Send chat message",
            },
            "GraphQL": {
                "Hasura GraphQL": settings.HASURA_URL,
                "Console": "http://localhost:8081"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
    )
