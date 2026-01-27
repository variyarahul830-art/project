# AI PDF Chatbot with Hasura GraphQL

Full-stack AI-powered PDF chatbot with Next.js frontend, Python FastAPI backend, and **Hasura GraphQL Engine** for data management. Uses PostgreSQL, MinIO (S3), and Milvus (vector database) with Docker.

## 🎯 Project Overview

This project combines:
- **PDF Processing**: Upload and process PDFs with text extraction and chunking
- **Vector Embeddings**: Store embeddings in Milvus for semantic search
- **Knowledge Graphs**: Manage workflows, nodes, and edges via Hasura GraphQL
- **FAQ Management**: Store and query frequently asked questions
- **Chat Interface**: Interactive chat with PDF context and knowledge graph

## 📁 Project Structure

```
project/
├── docker-compose.yml          # Docker services (PostgreSQL, Hasura, Milvus, MinIO, etcd)
├── HASURA_SETUP.md             # Detailed Hasura integration guide
├── setup.sh / setup.bat        # Automated setup scripts
│
├── frontend/                   # Next.js React Application
│   ├── app/
│   │   ├── page.jsx           # Main page
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatBox.jsx
│   │   │   ├── FAQManagement.jsx
│   │   │   ├── PDFUpload.jsx
│   │   │   ├── GraphBuilder.jsx
│   │   │   └── Message.jsx
│   │   └── services/
│   │       ├── hasura.js      # Hasura GraphQL client
│   │       └── api.js         # REST API client
│   ├── package.json
│   ├── next.config.ts
│   ├── .env.local              # Frontend env vars
│   └── tsconfig.json
│
└── backend/                    # Python FastAPI Backend
    ├── main.py                 # FastAPI app
    ├── config.py               # Configuration
    ├── database.py             # SQLAlchemy setup
    ├── models.py               # Database models (PDFDocument only)
    ├── schemas.py              # Pydantic schemas
    ├── crud.py                 # Database operations
    ├── schema.sql              # PostgreSQL schema for Hasura
    ├── routes/
    │   ├── pdf.py              # PDF routes
    │   ├── chat.py             # Chat routes
    │   └── __init__.py
    ├── services/
    │   ├── hasura_client.py    # Hasura GraphQL client
    │   ├── llm_service.py
    │   ├── embeddings.py
    │   ├── pdf_processor.py
    │   ├── milvus_service.py
    │   └── text_chunker.py
    ├── requirements.txt        # Python dependencies
    ├── .env                    # Backend env vars
    ├── verify_requirements.py  # Dependency verification
    └── README.md
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** - For containerized services
- **Node.js** (v14+) - For frontend
- **Python** (v3.8+) - For backend
- **Git** - For version control

### 1. Clone and Setup (Windows)

```bash
# Navigate to project directory
cd c:\project

# Run automated setup
setup.bat

# Or manually:
docker-compose up -d  # Start all containers
```

### 2. Create Database Tables

```bash
# Option A: Using Hasura Console
# Open http://localhost:8081 and create tables manually

# Option B: Using SQL Script
docker exec -i hasura-postgres psql -U postgres -d hasuradb < backend/schema.sql

# Option C: Using psql directly
psql -h localhost -U postgres -d hasuradb -f backend/schema.sql
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Verify no conflicts
pip check

# Run server
python -m uvicorn main:app --reload
```

Backend API: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend: **http://localhost:3000**

## 🐳 Docker Services

All services are defined in `docker-compose.yml`:

```yaml
Services Running:
├── postgres (PostgreSQL 15)      - DB for Hasura tables
├── hasura (Hasura GraphQL 2.38)  - GraphQL API engine  
├── minio (S3-compatible)         - Object storage for PDFs
├── milvus (Vector DB)            - Embeddings storage
├── etcd (Metadata service)       - For Milvus coordination
└── attu (Milvus UI)              - Vector DB visualization
```

### Start/Stop Containers

```bash
# Start all containers
docker-compose up -d

# Stop all containers
docker-compose down

# View container logs
docker logs hasura
docker logs hasuradb

# Stop specific container
docker stop hasura
docker start hasura
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  Sidebar | ChatBox | FAQManagement | PDFUpload | GraphBuilder│
└────────────────┬──────────────────┬──────────────────────────┘
                 │                  │
        GraphQL Queries        REST API Calls
                 │                  │
                 ▼                  ▼
    ┌────────────────────────┐  ┌──────────────────┐
    │  Hasura GraphQL API    │  │ FastAPI Backend  │
    │  (Port 8081)           │  │ (Port 8000)      │
    └────────────┬───────────┘  └────────┬─────────┘
                 │                       │
                 │            ┌──────────┴──────────┐
                 │            │                     │
                 ▼            ▼                     ▼
            ┌─────────────────────────────────────────────────┐
            │     PostgreSQL Database (Docker)                 │
            │  ├─ workflows (Hasura manages)                   │
            │  ├─ nodes (Hasura manages)                       │
            │  ├─ edges (Hasura manages)                       │
            │  ├─ faqs (Hasura manages)                        │
            │  └─ pdf_documents (FastAPI manages)              │
            └────────────┬─────────────┬────────────────────────┘
                         │             │
                         ▼             ▼
            ┌──────────────────┐  ┌─────────────┐
            │  MinIO (S3)      │  │  Milvus     │
            │  PDF Files       │  │  Embeddings │
            └──────────────────┘  └─────────────┘
```

## 🔗 API Routes

### Hasura GraphQL Endpoint
```
POST http://localhost:8081/v1/graphql
```

Example queries available via GraphQL Console or `frontend/app/services/hasura.js`

### FastAPI REST Endpoints

**PDF Management:**
- `POST /api/pdf/upload` - Upload PDF file
- `GET /api/pdf/documents` - List uploaded PDFs
- `GET /api/pdf/documents/{id}` - Get PDF details

**Chat:**
- `POST /api/chat` - Send chat message

## 📊 Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI components
- **JavaScript/JSX** - Dynamic frontend
- **Hasura GraphQL Client** - GraphQL queries

### Backend
- **FastAPI 0.104.1** - Python web framework
- **Hasura GraphQL 2.38.0** - Auto-generated GraphQL API
- **PostgreSQL 15** - Relational database
- **SQLAlchemy** - ORM for PDFDocument
- **Pydantic** - Data validation

### Services
- **Milvus 2.6.9** - Vector database for embeddings
- **MinIO** - S3-compatible object storage
- **etcd 3.5.5** - Milvus metadata service

### ML/AI Libraries
- **sentence-transformers 3.0.1** - PDF embeddings
- **transformers 4.35.2** - Model transformations
- **torch 2.1.2** - Deep learning framework
- **pdf2image 1.16.3** - PDF processing

### HTTP Clients
- **httpx 0.25.2** - Async HTTP for Hasura queries
- **aiohttp 3.9.1** - Alternative async HTTP

## 🔑 Configuration

### Backend `.env` File
```env
# Database (Docker PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hasuradb
DB_USER=postgres
DB_PASSWORD=postgres

# Hasura
HASURA_URL=http://localhost:8081/v1/graphql
HASURA_ADMIN_SECRET=myadminsecret

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pdf

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### Frontend `.env.local` File
```env
NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
NEXT_PUBLIC_HASURA_ADMIN_SECRET=myadminsecret
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 Usage Examples

### Backend: Create Workflow via Hasura

```python
from services.hasura_client import HasuraClient

client = HasuraClient()
workflow = await client.create_workflow("My Workflow", "Description")
```

### Frontend: Fetch Workflows via GraphQL

```javascript
import { getWorkflows, createWorkflow } from '@/app/services/hasura';

// Get all workflows
const { workflows } = await getWorkflows();

// Create new workflow
const result = await createWorkflow("New Workflow", "Description");
```

### Backend: Upload PDF

```bash
curl -X POST "http://localhost:8000/api/pdf/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## 🔍 Monitoring & Debugging

### Hasura Console
```
http://localhost:8081
```
- View/manage database tables
- Test GraphQL queries
- Set permissions and relationships
- Monitor webhook events

### Milvus Dashboard (Attu)
```
http://localhost:8080
```
- View vector embeddings
- Monitor search operations
- Manage collections

### FastAPI Docs
```
http://localhost:8000/docs
```
- Interactive API documentation
- Test endpoints
- View request/response schemas

### MinIO Console
```
http://localhost:9001
```
- Manage S3 buckets
- Upload/download files
- View storage analytics

## 🐛 Troubleshooting

### Docker Containers Won't Start
```bash
# Check if ports are in use
netstat -ano | findstr :5432  # PostgreSQL
netstat -ano | findstr :8081  # Hasura
netstat -ano | findstr :9000  # MinIO
netstat -ano | findstr :19530 # Milvus

# Force remove containers
docker-compose down -v
docker-compose up -d
```

### Hasura Queries Fail
```bash
# Check Hasura logs
docker logs hasura

# Verify admin secret in requests
# x-hasura-admin-secret: myadminsecret

# Test connection
docker exec hasura psql -h postgres -U postgres -d hasuradb -c "SELECT version();"
```

### Python Dependencies Conflict
```bash
# Verify dependencies
python backend/verify_requirements.py

# Or use pip check
pip check

# Reinstall if needed
pip install --upgrade --force-reinstall -r requirements.txt
```

### PDFs Not Processing
```bash
# Check MinIO connection
docker logs minio

# Verify Milvus connection
docker logs milvus

# Check backend logs
python -m uvicorn backend/main:app --reload
```

## 📦 Dependency Management

All Python dependencies are carefully versioned to avoid conflicts:

```
✓ httpx 0.25.2          - Hasura async queries
✓ transformers 4.35.2   - Model transformations
✓ torch 2.1.2           - Deep learning
✓ sentence-transformers 3.0.1 - Embeddings
✓ pymilvus 2.3.7        - Vector database
✓ pdf2image 1.16.3      - PDF processing
```

Run `pip check` to verify no conflicts exist.

## 🚀 Production Deployment

1. **Update environment URLs** - Change `localhost` to production domain
2. **Use strong secrets** - Generate new `HASURA_ADMIN_SECRET`
3. **Enable HTTPS** - Use SSL certificates for Hasura endpoint
4. **Database backups** - Set up PostgreSQL backup strategy
5. **Docker registry** - Push images to private registry
6. **Environment secrets** - Use Docker secrets or vault

## 📖 Additional Resources

- **Hasura Docs**: https://hasura.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **GraphQL Docs**: https://graphql.org/learn

See **HASURA_SETUP.md** for detailed Hasura integration guide.

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/name`
4. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Authors

- AI PDF Chatbot Team
- Powered by Hasura, FastAPI, and Next.js

---

**Version**: 3.0.0  
**Last Updated**: 2024  
**Status**: Active Development


### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - Python ORM
- **Psycopg2** - PostgreSQL adapter
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Database
- **PostgreSQL** - Relational database

## 📡 API Communication

**Frontend uses Fetch API** to call Python backend endpoints:

```typescript
// frontend/app/services/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export async function addQA(question: string, answer: string) {
  const response = await fetch(`${API_BASE_URL}/api/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, answer }),
  });
  return response.json();
}

export async function chat(question: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  return response.json();
}
```

## 🗄️ Database (SQLAlchemy + PostgreSQL)

**Backend uses SQLAlchemy ORM** for database operations:

```python
# backend/models.py - SQLAlchemy ORM Model
class QAPair(Base):
    __tablename__ = "qa_pairs"
    id = Column(Integer, primary_key=True)
    question = Column(String(500), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# backend/crud.py - Database Operations
def create_qa(db: Session, qa: QACreate) -> QAPair:
    db_qa = QAPair(question=qa.question.strip(), answer=qa.answer.strip())
    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)
    return db_qa

def get_answer_by_question(db: Session, question: str) -> QAPair:
    result = db.query(QAPair).filter(
        func.lower(QAPair.question) == func.lower(question.strip())
    ).first()
    if not result:
        result = db.query(QAPair).filter(
            QAPair.question.ilike(f"%{question.strip()}%")
        ).first()
    return result
```

## 📊 Database Schema

Automatically created by SQLAlchemy on startup:

```sql
CREATE TABLE qa_pairs (
  id SERIAL PRIMARY KEY,
  question VARCHAR(500) NOT NULL UNIQUE,
  answer TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Features

✅ **Frontend (Next.js + React)**
- ChatGPT-style UI with sidebar navigation
- Two modes: Chat & Add Q&A
- Responsive design
- Client-side components with React hooks
- TypeScript for type safety
- Fetch API for HTTP requests

✅ **Backend (Python + FastAPI)**
- Async REST API with FastAPI
- SQLAlchemy ORM for database operations
- PostgreSQL integration
- CORS enabled for frontend communication
- Input validation with Pydantic
- Proper error handling and HTTP status codes
- Automatic API documentation at `/docs`

✅ **Database (PostgreSQL + SQLAlchemy)**
- Reliable relational database
- Automatic schema creation
- Connection pooling
- Support for exact and partial question matching

## 🧪 Testing

### Add Q&A via API
```bash
curl -X POST http://localhost:3001/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is FastAPI?",
    "answer": "FastAPI is a modern, fast web framework for building APIs with Python."
  }'
```

### Chat via API
```bash
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is FastAPI?"}'
```

### Get All Q&As
```bash
curl http://localhost:3001/api/qa
```

### View API Documentation
Visit: **http://localhost:3001/docs** (Swagger UI)

## 📚 Documentation

- [Backend README](backend/README.md) - Python/FastAPI setup and API details
- [Complete Setup Guide](SETUP.md) - Full installation and configuration

## 🚨 Troubleshooting

### Backend

**ModuleNotFoundError: No module named 'fastapi'**
```bash
pip install -r requirements.txt
```

**PostgreSQL Connection Error**
- Verify PostgreSQL is running
- Check credentials in `.env`

**Port 3001 Already in Use**
- Change `PORT` in `.env` or kill the process

### Frontend

**Cannot Reach Backend**
- Check backend is running on port 3001
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**CORS Errors**
- Ensure `FRONTEND_URL` in backend `.env` matches frontend URL

## 🔐 Security Notes (Production)

- Add JWT authentication
- Use HTTPS instead of HTTP
- Implement rate limiting
- Add input sanitization
- Enable database backups
- Use environment secrets
- Add request logging
- Implement API versioning

## 📞 Quick Commands

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py

# Frontend
cd frontend && npm install && npm run dev

# Database
psql -U postgres
CREATE DATABASE chatbot_db;
```

## 📄 License

MIT
