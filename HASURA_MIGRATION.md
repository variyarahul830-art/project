# Hasura GraphQL Integration Guide

## What Changed

Your project now uses **Hasura GraphQL** instead of REST APIs for:
- ✅ Workflows (create, read, delete)
- ✅ Nodes (create, read, delete)
- ✅ Edges (create, read, delete)
- ✅ FAQs (CRUD operations)

REST APIs are still used for:
- ✅ PDF Upload & Processing (`/api/pdf/*`)
- ✅ LLM Chat Service (`/api/chat`)

## Updated Backend Structure

### Removed Routes
- `routes/workflows.py` ❌ (use Hasura instead)
- `routes/graph.py` ❌ (use Hasura instead)
- `routes/faq.py` ❌ (use Hasura instead)

### Kept Routes
- `routes/pdf.py` ✅ (PDF upload/processing)
- `routes/chat.py` ✅ (LLM chat service)

### New Service
- `services/hasura_client.py` - Python utility functions for Hasura GraphQL queries

## Frontend Changes

### Old (REST API)
```javascript
import { createNode, deleteNode } from '@/services/api';

await createNode('My Node', workflowId);
await deleteNode(nodeId);
```

### New (Hasura GraphQL)
```javascript
import { createNode, deleteNode } from '@/services/hasura';

await createNode(workflowId, 'My Node');
await deleteNode(nodeId);
```

## Database Connection

**Backend** → Uses Hasura's PostgreSQL database directly via SQLAlchemy ORM

```
Backend (FastAPI)
    ↓
PostgreSQL (via Hasura)
```

No REST layer needed between backend and database for CRUD operations!

## Key Benefits

1. **Real-time Updates** - WebSocket support for live data
2. **No API Boilerplate** - Hasura generates GraphQL API automatically
3. **Better Performance** - Single query gets all related data
4. **Visual Admin** - Manage schema at `http://localhost:8081`
5. **Type Safety** - Frontend gets GraphQL types for better IDE support

## Environment Variables

Add to `backend/.env`:

```env
HASURA_URL=http://localhost:8081/v1/graphql
HASURA_ADMIN_SECRET=your_secret_here  # Optional, only if Hasura has auth enabled
```

Add to `frontend/.env.local`:

```env
NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
NEXT_PUBLIC_HASURA_ADMIN_SECRET=your_secret_here  # Optional
```

## How to Use

### Backend (Python)

```python
from services.hasura_client import get_workflows, create_node

# Get all workflows
workflows = await get_workflows()

# Create a node
node = await create_node(workflow_id=1, text="My Node")
```

### Frontend (React/Next.js)

```javascript
import { getWorkflows, createNode } from '@/services/hasura';

// Get all workflows
const workflows = await getWorkflows();

// Create a node
const node = await createNode(1, "My Node");
```

## Next Steps

1. Verify Hasura container is running: `http://localhost:8081`
2. Create tables in Hasura console if they don't exist (Workflow, Node, Edge, FAQ)
3. Update your component imports to use `hasura.js` instead of `api.js`
4. Remove REST API routes that are no longer needed
5. Test GraphQL queries in Hasura console

## Troubleshooting

**Hasura not found?**
```bash
docker ps  # Check if Hasura container is running
```

**Tables not appearing in Hasura?**
- Go to `http://localhost:8081/console`
- Click "Data" tab
- Click "Create Table" to add Workflow, Node, Edge, FAQ tables manually

**GraphQL errors?**
- Check browser console for error messages
- Verify `HASURA_URL` environment variable is correct
- Ensure tables exist in PostgreSQL
