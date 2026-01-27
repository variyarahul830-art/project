# ✅ Hasura Integration Checklist

## Phase 1: Pre-Deployment Setup

### Docker & Environment
- [ ] Docker is installed (`docker --version`)
- [ ] Docker Compose is installed (`docker-compose --version`)
- [ ] Windows 10/11 or Linux/macOS system
- [ ] Administrator access for Docker commands
- [ ] Ports 5432, 8081, 9000, 9001, 19530 are available
- [ ] c:\project directory exists and has all files

### Python Environment
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Virtual environment can be created
- [ ] pip is functional (`pip --version`)
- [ ] No conflicting Python installations

---

## Phase 2: Docker Deployment

### Start Containers
- [ ] Run `docker-compose up -d` successfully
- [ ] All 6 containers start without errors:
  - [ ] hasura-postgres (PostgreSQL)
  - [ ] hasura (Hasura GraphQL Engine)
  - [ ] milvus-minio (MinIO)
  - [ ] milvus-standalone (Milvus)
  - [ ] milvus-etcd (etcd)
  - [ ] milvus-attu (Attu UI)

### Verify Containers
- [ ] `docker ps` shows all containers running
- [ ] PostgreSQL responding: `docker logs hasura-postgres`
- [ ] Hasura responding: `docker logs hasura`
- [ ] No port conflicts detected

### Network Connectivity
- [ ] PostgreSQL accessible at localhost:5432
- [ ] Hasura console accessible at http://localhost:8081
- [ ] MinIO console accessible at http://localhost:9001
- [ ] Milvus accessible at localhost:19530

---

## Phase 3: Database Setup

### Create Tables

**Using SQL Script:**
- [ ] schema.sql file exists at `backend/schema.sql`
- [ ] Execute: `docker exec -i hasura-postgres psql -U postgres -d hasuradb < backend/schema.sql`
- [ ] Command completes without errors

**Verify Tables Created:**
- [ ] Open Hasura console: http://localhost:8081
- [ ] Go to Data tab
- [ ] See tables:
  - [ ] workflows
  - [ ] nodes
  - [ ] edges
  - [ ] faqs
  - [ ] pdf_documents

### Table Properties
- [ ] workflows: has id, name, description, created_at, updated_at
- [ ] nodes: has id, workflow_id, text, created_at, updated_at
- [ ] edges: has id, workflow_id, source_node_id, target_node_id, created_at
- [ ] faqs: has id, question, answer, category, created_at, updated_at
- [ ] pdf_documents: has id, filename, minio_path, file_size, upload_date

### Relationships
- [ ] Foreign keys are set up correctly
- [ ] Cascade delete enabled on workflow deletions
- [ ] Unique constraints in place

---

## Phase 4: Backend Setup

### Environment Configuration
- [ ] `.env` file exists at `backend/.env`
- [ ] DB_HOST=localhost
- [ ] DB_PORT=5432
- [ ] DB_NAME=hasuradb
- [ ] HASURA_URL=http://localhost:8081/v1/graphql
- [ ] HASURA_ADMIN_SECRET=myadminsecret
- [ ] MINIO_ENDPOINT, MILVUS_HOST configured

### Python Virtual Environment
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Activated: `venv\Scripts\activate` (Windows)
- [ ] `(venv)` appears in terminal prompt

### Dependencies Installation
- [ ] `pip install -r requirements.txt` completes
- [ ] All 23 packages installed successfully
- [ ] `pip check` shows "No broken distributions found"

### Dependency Verification
- [ ] httpx 0.25.2 installed
- [ ] transformers 4.35.2 installed
- [ ] torch 2.1.2 installed
- [ ] sentence-transformers 3.0.1 installed
- [ ] pymilvus 2.3.7 installed
- [ ] huggingface-hub >=0.19.3,<1.0 installed

### File Verification
- [ ] config.py has HASURA_URL and HASURA_ADMIN_SECRET
- [ ] main.py imports only pdf and chat routes
- [ ] models.py only contains PDFDocument
- [ ] hasura_client.py exists with HasuraClient class
- [ ] services/hasura_client.py has all CRUD methods

### Backend Startup
- [ ] Backend can start: `python -m uvicorn main:app --reload`
- [ ] No startup errors in console
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Swagger UI shows only pdf and chat routes

---

## Phase 5: Frontend Setup

### Environment Configuration
- [ ] `.env.local` file exists at `frontend/.env.local`
- [ ] NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
- [ ] NEXT_PUBLIC_HASURA_ADMIN_SECRET=myadminsecret
- [ ] NEXT_PUBLIC_API_URL=http://localhost:8000

### Node.js Setup
- [ ] Node.js v14+ installed (`node --version`)
- [ ] npm installed (`npm --version`)

### Dependencies Installation
- [ ] `npm install` completes successfully
- [ ] node_modules directory created
- [ ] package-lock.json updated

### Frontend Startup
- [ ] Frontend can start: `npm run dev`
- [ ] No startup errors
- [ ] Accessible at http://localhost:3000
- [ ] React components load without errors

### File Verification
- [ ] hasura.js exists at `frontend/app/services/hasura.js`
- [ ] Contains executeGraphQL function
- [ ] Has workflow CRUD functions
- [ ] Has node CRUD functions
- [ ] Has edge CRUD functions
- [ ] Has FAQ CRUD functions

---

## Phase 6: Functionality Testing

### Backend API Tests

**Health Check:**
```bash
curl http://localhost:8000/health
```
- [ ] Returns 200 status
- [ ] Shows "healthy" status
- [ ] Includes Hasura URL

**API Documentation:**
- [ ] http://localhost:8000/docs loads
- [ ] Shows pdf routes
- [ ] Shows chat routes
- [ ] No graph/workflow/faq REST routes

### Hasura GraphQL Tests

**Console Access:**
- [ ] http://localhost:8081 loads
- [ ] Data tab shows all tables
- [ ] GraphQL playground available

**Query Test:**
```graphql
query {
  workflows {
    id
    name
  }
}
```
- [ ] Executes without errors
- [ ] Returns empty array (no data yet)

**Mutation Test - Create Workflow:**
```graphql
mutation {
  insert_workflows_one(object: {name: "Test", description: "Test workflow"}) {
    id
    name
    created_at
  }
}
```
- [ ] Executes without errors
- [ ] Returns created workflow with id

**Mutation Test - Create Node:**
```graphql
mutation {
  insert_nodes_one(object: {workflow_id: 1, text: "Sample node"}) {
    id
    text
    workflow_id
  }
}
```
- [ ] Executes without errors
- [ ] Returns created node

### Frontend Integration Tests

**Page Load:**
- [ ] http://localhost:3000 loads
- [ ] No console errors
- [ ] Components render

**API Connection:**
- [ ] Frontend can connect to backend
- [ ] Frontend can connect to Hasura
- [ ] No CORS errors

### PDF Upload Test
- [ ] Upload endpoint works
- [ ] File stored in MinIO
- [ ] Metadata in PostgreSQL

### Chat Test
- [ ] Chat endpoint works
- [ ] Can send message
- [ ] Gets response

---

## Phase 7: Documentation Review

### Documentation Files
- [ ] QUICK_START.md exists and is readable
- [ ] HASURA_SETUP.md exists and is comprehensive
- [ ] README.md updated with Hasura content
- [ ] IMPLEMENTATION_SUMMARY.md explains changes

### Documentation Content
- [ ] Quick Start covers setup steps
- [ ] Hasura Setup explains architecture
- [ ] README includes API examples
- [ ] Summary lists all changes

### Code Comments
- [ ] HasuraClient has proper docstrings
- [ ] hasura.js has function descriptions
- [ ] config.py explains settings
- [ ] schema.sql has table comments

---

## Phase 8: Final Validation

### Performance Checks
- [ ] Backend responds within 1 second
- [ ] Frontend loads within 3 seconds
- [ ] GraphQL queries execute <500ms
- [ ] No memory leaks after 5 minutes

### Dependency Confirmation
- [ ] No version conflicts: `pip check`
- [ ] All packages functional
- [ ] No circular imports
- [ ] No missing dependencies

### Data Integrity
- [ ] Can create workflows
- [ ] Can create nodes
- [ ] Can create edges
- [ ] Can create FAQs
- [ ] Relationships maintained
- [ ] Foreign keys working

### Error Handling
- [ ] Invalid queries return proper errors
- [ ] Missing admin secret returns 401
- [ ] Database errors handled gracefully
- [ ] File upload errors handled

---

## Phase 9: Production Readiness

### Security
- [ ] HASURA_ADMIN_SECRET is strong (not "myadminsecret")
- [ ] Permissions configured in Hasura
- [ ] CORS properly configured
- [ ] API authentication enabled
- [ ] Database password is strong

### Scalability
- [ ] Database indexes created
- [ ] Query performance optimized
- [ ] Caching implemented
- [ ] Load testing considered

### Monitoring
- [ ] Logging configured
- [ ] Error tracking enabled
- [ ] Performance monitoring ready
- [ ] Database backups scheduled

### Deployment
- [ ] All configuration files reviewed
- [ ] Environment-specific settings prepared
- [ ] Deployment script created
- [ ] Rollback plan exists

---

## Phase 10: Issues Resolution

### If Docker Issues Occur
- [ ] Check if ports available: `netstat -ano`
- [ ] Verify Docker daemon running: `docker ps`
- [ ] Check disk space: `docker system df`
- [ ] Review container logs: `docker logs [container-name]`
- [ ] Solution: See HASURA_SETUP.md Troubleshooting

### If Database Issues Occur
- [ ] Verify PostgreSQL running: `docker exec hasura-postgres psql -U postgres -c "SELECT 1"`
- [ ] Check table creation: `docker exec hasura-postgres psql -U postgres -d hasuradb -c "\dt"`
- [ ] Review migration logs: `docker logs hasura-postgres`
- [ ] Solution: Re-execute schema.sql

### If Backend Issues Occur
- [ ] Check Python version: `python --version`
- [ ] Verify venv activated: Check `(venv)` in prompt
- [ ] Check dependencies: `pip list`
- [ ] Run verification: `python backend/verify_requirements.py`
- [ ] Solution: Reinstall requirements

### If Frontend Issues Occur
- [ ] Check Node version: `node --version`
- [ ] Clear cache: `npm cache clean --force`
- [ ] Delete node_modules: `rm -r node_modules`
- [ ] Reinstall: `npm install`
- [ ] Solution: Check .env.local configuration

### If Hasura Issues Occur
- [ ] Check console: http://localhost:8081
- [ ] Verify admin secret in requests
- [ ] Check table visibility in Data tab
- [ ] Review GraphQL query syntax
- [ ] Solution: See HASURA_SETUP.md GraphQL Examples

---

## ✅ Sign-Off

### Before Going Live

- [ ] All Phase checks complete
- [ ] No critical errors remaining
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] Team trained
- [ ] Backup plan ready

### Post-Deployment Checklist

- [ ] Monitor logs for errors
- [ ] Test all user workflows
- [ ] Collect feedback
- [ ] Document any issues
- [ ] Plan improvements

---

## 📊 Completion Matrix

| Phase | Status | Completed By | Date |
|-------|--------|-------------|------|
| 1. Pre-Deployment | ⬜ | | |
| 2. Docker | ⬜ | | |
| 3. Database | ⬜ | | |
| 4. Backend | ⬜ | | |
| 5. Frontend | ⬜ | | |
| 6. Testing | ⬜ | | |
| 7. Documentation | ⬜ | | |
| 8. Validation | ⬜ | | |
| 9. Production Ready | ⬜ | | |
| 10. Issues Resolved | ⬜ | | |

**Overall Status:** 🔲 Not Started | 🟨 In Progress | ✅ Complete

---

## 📞 Support & Escalation

If you encounter issues:

1. Check QUICK_START.md
2. Review HASURA_SETUP.md Troubleshooting
3. Check container logs: `docker logs [container-name]`
4. Run verification: `python backend/verify_requirements.py`
5. Review error messages in console
6. Check resource usage: `docker system stats`

---

**Version**: 3.0.0
**Last Updated**: 2024
**Status**: Ready for Implementation
