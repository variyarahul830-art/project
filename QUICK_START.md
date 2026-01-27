# Quick Start Guide - Hasura AI PDF Chatbot

## ⚡ 5-Minute Setup (Windows)

### 1. Start Docker Containers (1 minute)
```bash
cd c:\project
docker-compose up -d
```

**Verify containers are running:**
```bash
docker ps
```

### 2. Create Database Tables (1 minute)

**Option A - SQL Script (Recommended):**
```bash
docker exec -i hasura-postgres psql -U postgres -d hasuradb < backend/schema.sql
```

**Option B - Using Hasura Console:**
1. Open http://localhost:8081 in browser
2. Go to Data tab
3. Create tables manually (see schema.sql for table definitions)

### 3. Install Backend Dependencies (2 minutes)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip check
```

### 4. Start Services (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # Only first time
npm run dev
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Chat interface |
| **Backend API** | http://localhost:8000 | REST endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Hasura Console** | http://localhost:8081 | GraphQL management |
| **MinIO Console** | http://localhost:9001 | File storage UI |
| **Milvus Dashboard** | http://localhost:8080 | Vector DB UI |

---

## 🧪 Quick Tests

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "AI PDF Chatbot API is running",
  "hasura_url": "http://localhost:8081/v1/graphql"
}
```

### Test 2: Hasura Connection
```bash
curl -X POST http://localhost:8081/v1/graphql \
  -H "Content-Type: application/json" \
  -H "x-hasura-admin-secret: myadminsecret" \
  -d '{"query": "query { workflows { id name } }"}'
```

### Test 3: Create a Workflow via Hasura
```bash
curl -X POST http://localhost:8081/v1/graphql \
  -H "Content-Type: application/json" \
  -H "x-hasura-admin-secret: myadminsecret" \
  -d '{
    "query": "mutation { insert_workflows_one(object: { name: \"Test\", description: \"Test workflow\" }) { id name } }"
  }'
```

### Test 4: Upload PDF via Backend
```bash
curl -X POST http://localhost:8000/api/pdf/upload \
  -H "X-Token: secret-token" \
  -F "file=@sample.pdf"
```

---

## 📊 Workflow

```
1. Upload PDF
   ↓
2. Backend processes & extracts text
   ↓
3. Create embeddings & store in Milvus
   ↓
4. Store PDF metadata in PostgreSQL
   ↓
5. Frontend sends chat queries
   ↓
6. Backend searches Milvus for context
   ↓
7. Generate response with LLM
   ↓
8. Return to user
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/services/hasura_client.py` | GraphQL client |
| `frontend/app/services/hasura.js` | Frontend GraphQL functions |
| `backend/schema.sql` | Database schema |
| `docker-compose.yml` | Docker services |
| `.env` files | Configuration |

---

## 🔧 Common Commands

### Docker Management
```bash
# Start all containers
docker-compose up -d

# Stop all containers
docker-compose down

# View logs
docker logs hasura
docker logs hasuradb

# Execute SQL in PostgreSQL
docker exec -it hasura-postgres psql -U postgres -d hasuradb
```

### Python Environment
```bash
# Activate venv
cd backend && venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify no conflicts
pip check

# Run backend
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🚨 Troubleshooting

### Containers not starting?
```bash
# Check if ports are in use
netstat -ano | findstr :5432  # PostgreSQL
netstat -ano | findstr :8081  # Hasura

# Force restart
docker-compose down -v
docker-compose up -d
```

### Database connection error?
```bash
# Verify PostgreSQL is running
docker exec hasura-postgres psql -U postgres -d hasuradb -c "SELECT 1"

# Check connection string in .env
cat backend/.env | grep DB_
```

### "pip check" shows conflicts?
```bash
# Reinstall from scratch
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
pip check
```

### Can't query workflows from frontend?
1. Verify Hasura is running: `docker ps | grep hasura`
2. Check admin secret in requests: `x-hasura-admin-secret: myadminsecret`
3. Verify tables exist: Open http://localhost:8081 → Data tab
4. Check frontend .env: `cat frontend/.env.local`

---

## 📚 Additional Resources

- **HASURA_SETUP.md** - Complete integration guide
- **README.md** - Full project documentation
- **IMPLEMENTATION_SUMMARY.md** - What was changed
- **Hasura Docs** - https://hasura.io/docs
- **API Docs** - http://localhost:8000/docs

---

## ✅ Checklist Before Going Live

- [ ] Docker containers running (`docker ps`)
- [ ] Database tables created (Hasura console shows tables)
- [ ] Backend starts without errors (`python -m uvicorn main:app`)
- [ ] Frontend loads (`http://localhost:3000`)
- [ ] Can upload PDF
- [ ] Can create workflow via Hasura
- [ ] Can send chat message
- [ ] No dependency conflicts (`pip check`)

---

## 🎯 Next Steps

1. **Try uploading a PDF** to test backend
2. **Create a workflow** via Hasura console
3. **Add FAQ entries** using FAQManagement component
4. **Test chat interface** with PDF context
5. **Explore Hasura console** for data management

---

**Version**: 3.0.0  
**Last Updated**: 2024  
**Status**: Ready to Use
