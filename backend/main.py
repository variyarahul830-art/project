from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from models import Node, Edge, PDFDocument, Workflow, FAQ

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Graph Chatbot Backend",
    description="REST API for knowledge graph-based chatbot with PostgreSQL",
    version="2.0.0"
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
from routes import graph, chat, pdf, workflows, faq

# Include routers
app.include_router(workflows.router)

app.include_router(graph.router)

app.include_router(chat.router)

app.include_router(pdf
                   .router)

app.include_router(faq.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "message": "Backend is running"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chatbot Backend API",
         "version": "2.0.0",
        "endpoints": {
             "POST /api/graph/nodes": "Create node",
             "GET /api/graph/nodes": "Get all nodes",
             "POST /api/graph/edges": "Create edge",
             "GET /api/graph/edges": "Get all edges",
             "GET /api/graph": "Get complete graph",
             "POST /api/chat": "Query graph",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
    )
