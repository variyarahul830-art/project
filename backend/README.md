# Chatbot Backend - Python FastAPI + SQLAlchemy + PostgreSQL

Production-ready REST API backend for the chatbot application using FastAPI and SQLAlchemy ORM.

## Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chatbot_db
DB_USER=postgres
DB_PASSWORD=your_password_here
PORT=3001
FRONTEND_URL=http://localhost:3000
```

### 3. Create PostgreSQL Database

```sql
CREATE DATABASE chatbot_db;
```

The tables will be created automatically when the server starts.

### 4. Start the Server

```bash
# Development (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

Server runs on `http://localhost:3001`

## Project Structure

```
backend/
├── main.py              # FastAPI app initialization
├── config.py            # Settings & environment configuration
├── database.py          # SQLAlchemy setup & session management
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response models
├── crud.py              # Database CRUD operations
├── routes/
│   ├── qa.py           # Q&A endpoints
│   └── chat.py         # Chat endpoints
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - Python ORM for database operations
- **Psycopg2** - PostgreSQL adapter for Python
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation using Python type annotations

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "OK",
  "message": "Backend is running"
}
```

### Add Q&A
```
POST /api/qa
Content-Type: application/json

{
  "question": "What is FastAPI?",
  "answer": "FastAPI is a modern, fast web framework for building APIs."
}
```

Response:
```json
{
  "success": true,
  "message": "Q&A added successfully",
  "data": {
    "id": 1,
    "question": "What is FastAPI?",
    "answer": "FastAPI is a modern, fast web framework for building APIs.",
    "created_at": "2026-01-16T10:00:00",
    "updated_at": "2026-01-16T10:00:00"
  }
}
```

### Chat
```
POST /api/chat
Content-Type: application/json

{
  "question": "What is FastAPI?"
}
```

Response:
```json
{
  "question": "What is FastAPI?",
  "answer": "FastAPI is a modern, fast web framework for building APIs.",
  "success": true
}
```

### Get All Q&As
```
GET /api/qa
```

Response:
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "id": 1,
      "question": "What is FastAPI?",
      "answer": "FastAPI is a modern, fast web framework for building APIs.",
      "created_at": "2026-01-16T10:00:00",
      "updated_at": "2026-01-16T10:00:00"
    }
  ]
}
```

## Database Schema

The `qa_pairs` table is automatically created on startup:

```sql
CREATE TABLE qa_pairs (
  id SERIAL PRIMARY KEY,
  question VARCHAR(500) NOT NULL UNIQUE,
  answer TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Features

✅ **FastAPI Framework**
- Type hints with Pydantic validation
- Automatic API documentation (Swagger UI at `/docs`)
- Built-in request/response validation

✅ **SQLAlchemy ORM**
- Database-agnostic queries
- Automatic schema management
- Connection pooling

✅ **PostgreSQL**
- Reliable, scalable database
- ACID compliance
- Full-text search capabilities

✅ **CORS Support**
- Configured for frontend communication
- Customizable origin list

✅ **Error Handling**
- Proper HTTP status codes
- Descriptive error messages
- Database constraint violations

✅ **Input Validation**
- Pydantic schemas for type safety
- Min/max length constraints
- Automatic serialization

## Frontend Integration

The frontend communicates via Fetch API using the base URL:

```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

Ensure your frontend `.env.local` has:
```
NEXT_PUBLIC_API_URL=http://localhost:3001
```

## Troubleshooting

### Import Error: No module named 'fastapi'
```
pip install -r requirements.txt
```

### PostgreSQL Connection Error
```
Error: could not connect to server: Connection refused
```
→ Ensure PostgreSQL is running
→ Check `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` in `.env`

### Database Does Not Exist
→ Run: `CREATE DATABASE chatbot_db;` in PostgreSQL

### CORS Errors
→ Check `FRONTEND_URL` in `.env`
→ Default is `http://localhost:3000`

### Port Already in Use
→ Change `PORT` in `.env` to another value
→ Or kill the process using the port

## Development

### Auto-reload on Changes
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

### View API Documentation
Visit: `http://localhost:3001/docs` (Swagger UI)

### Reset Database
```sql
DROP TABLE qa_pairs;
-- Server will recreate table on restart
```

## Production Deployment

For production, consider:
- Using a process manager (Gunicorn, PM2)
- Adding authentication (JWT)
- Using environment secrets management
- Adding request logging
- Database connection pooling configuration
- Rate limiting middleware
- Input sanitization
- SQL query monitoring

Example production run:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
