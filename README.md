# Chatbot Application

Full-stack chatbot with Next.js frontend and Python FastAPI backend using SQLAlchemy and PostgreSQL.

## 📁 Project Structure

```
project/
├── frontend/           # Next.js React Application
│   ├── app/
│   │   ├── page.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatBox.tsx
│   │   │   ├── AddQAForm.tsx
│   │   │   ├── Message.tsx
│   │   │   └── ModeSwitcher.tsx
│   │   └── services/
│   │       └── api.ts          # Fetch API service layer
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── .env.local
│
└── backend/            # Python FastAPI Backend
    ├── main.py
    ├── config.py
    ├── database.py     # SQLAlchemy setup
    ├── models.py       # SQLAlchemy ORM models
    ├── schemas.py
    ├── crud.py         # Database operations
    ├── routes/
    │   ├── qa.py
    │   ├── chat.py
    │   └── __init__.py
    ├── requirements.txt
    ├── .env.example
    └── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- PostgreSQL

### Backend Setup (Python)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Start server
python main.py
```

Backend runs on: **http://localhost:3001**

### Database Setup

```bash
# Create database using psql or pgAdmin
psql -U postgres
CREATE DATABASE chatbot_db;
\q
```

Tables are created automatically on backend startup.

### Frontend Setup (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:3000**

## 🔗 Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI component library  
- **TypeScript** - Type-safe JavaScript
- **Fetch API** - HTTP client
- **Styled JSX** - Component styling

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
