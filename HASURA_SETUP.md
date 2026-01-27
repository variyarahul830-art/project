# Hasura GraphQL Integration Guide

## Overview

This project has been updated to use **Hasura GraphQL Engine** instead of REST APIs for workflows, nodes, edges, and FAQs. This provides:

- **Auto-generated GraphQL API** from PostgreSQL
- **Real-time subscriptions** support
- **Fine-grained permissions** and access control
- **Simplified CRUD operations** from frontend
- **Separation of concerns**: REST API handles complex operations (PDF, Chat), GraphQL handles data CRUD

## Architecture

```
Frontend (Next.js)
    ├── GraphQL Queries → Hasura (Workflows, Nodes, Edges, FAQs)
    └── REST API Calls → FastAPI (PDF Upload, Chat)
    
Hasura GraphQL Engine
    └── PostgreSQL Database (Docker Container)
    
Backend (FastAPI)
    ├── PDF Processing → MinIO (S3)
    ├── Embeddings → Milvus (Vector DB)
    └── Chat Logic
```

## Docker Setup

### 1. Start Docker Containers

```bash
# Navigate to project root
cd c:\project

# Start all containers (PostgreSQL, Hasura, MinIO, Milvus, etcd)
docker-compose up -d
```

### Verify Containers are Running

```bash
docker ps
```

Expected containers:
- `hasuradb` - PostgreSQL 15
- `hasura` - Hasura GraphQL Engine
- `minio` - Object Storage (S3)
- `milvus` - Vector Database
- `etcd` - etcd metadata service

### 2. Create Database Tables

**Option A: Using SQL Script (Recommended)**

1. Connect to PostgreSQL in Docker:
   ```bash
   docker exec -it hasuradb psql -U postgres -d hasuradb
   ```

2. Execute the schema:
   ```bash
   \i /path/to/schema.sql
   ```
   Or copy-paste the contents from [schema.sql](./backend/schema.sql)

**Option B: Using pgAdmin (UI)**

1. Open pgAdmin: http://localhost:5050
2. Create connection to `hasuradb:5432`
3. Execute SQL from schema.sql in query tool

### 3. Access Hasura Console

Open your browser and navigate to:

```
http://localhost:8081
```

**Features in Hasura Console:**
- **Data Tab**: View/edit database tables and relationships
- **GraphQL Tab**: Test GraphQL queries interactively
- **Permissions Tab**: Set row-level security
- **Events Tab**: Set up webhooks for database changes

## Configuration Files

### Backend Configuration

**`.env` file** - Backend environment variables:
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

# MinIO, Milvus, etc...
```

**`config.py`** - Python configuration:
```python
HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8081/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "myadminsecret")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

### Frontend Configuration

**`.env.local` file** - Frontend environment variables:
```env
NEXT_PUBLIC_HASURA_URL=http://localhost:8081/v1/graphql
NEXT_PUBLIC_HASURA_ADMIN_SECRET=myadminsecret
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Backend Usage

### Python HasuraClient Service

**Location**: `backend/services/hasura_client.py`

```python
from services.hasura_client import HasuraClient

client = HasuraClient()

# Get all workflows
workflows = await client.get_workflows()

# Create a workflow
workflow = await client.create_workflow(
    name="My Workflow",
    description="Test workflow"
)

# Get workflow by ID
workflow = await client.get_workflow(workflow_id=1)

# Create node
node = await client.create_node(workflow_id=1, text="Node text")

# Create edge
edge = await client.create_edge(
    workflow_id=1,
    source_node_id=1,
    target_node_id=2
)

# FAQs
faqs = await client.get_faqs()
faq = await client.create_faq(
    question="Q1",
    answer="A1",
    category="General"
)
```

## Frontend Usage

### JavaScript Hasura Service

**Location**: `frontend/app/services/hasura.js`

```javascript
import {
  getWorkflows,
  createWorkflow,
  getNodes,
  createNode,
  getEdges,
  createEdge,
  getFAQs,
  createFAQ,
  updateFAQ,
  deleteFAQ,
} from '@/app/services/hasura';

// Example in a React component
export default function WorkflowManager() {
  const [workflows, setWorkflows] = useState([]);

  useEffect(() => {
    const loadWorkflows = async () => {
      try {
        const data = await getWorkflows();
        setWorkflows(data.workflows);
      } catch (error) {
        console.error('Failed to load workflows:', error);
      }
    };
    loadWorkflows();
  }, []);

  const handleCreateWorkflow = async (name) => {
    const result = await createWorkflow(name, "New workflow");
    setWorkflows([...workflows, result.insert_workflows_one]);
  };

  return (
    <div>
      {workflows.map(wf => (
        <div key={wf.id}>{wf.name}</div>
      ))}
    </div>
  );
}
```

## GraphQL Query Examples

### Get All Workflows with Nodes and Edges

```graphql
query {
  workflows(order_by: {created_at: desc}) {
    id
    name
    description
    created_at
    nodes {
      id
      text
    }
    edges {
      id
      source_node_id
      target_node_id
    }
  }
}
```

### Create a Workflow

```graphql
mutation {
  insert_workflows_one(
    object: {
      name: "New Workflow"
      description: "Test workflow"
    }
  ) {
    id
    name
    created_at
  }
}
```

### Get FAQs by Category

```graphql
query {
  faqs(
    where: {category: {_eq: "General"}}
    order_by: {created_at: desc}
  ) {
    id
    question
    answer
    category
  }
}
```

### Update FAQ

```graphql
mutation {
  update_faqs_by_pk(
    pk_columns: {id: 1}
    _set: {
      question: "Updated Q"
      answer: "Updated A"
    }
  ) {
    id
    question
    answer
  }
}
```

## Key Tables

### workflows
- `id` (PK): Auto-increment primary key
- `name`: Workflow name
- `description`: Optional description
- `created_at`: Timestamp
- `updated_at`: Timestamp

### nodes
- `id` (PK): Auto-increment primary key
- `workflow_id` (FK): Foreign key to workflows
- `text`: Node text content
- `created_at`: Timestamp
- `updated_at`: Timestamp
- **Constraint**: UNIQUE(workflow_id, text)

### edges
- `id` (PK): Auto-increment primary key
- `workflow_id` (FK): Foreign key to workflows
- `source_node_id` (FK): Source node reference
- `target_node_id` (FK): Target node reference
- `created_at`: Timestamp
- **Constraint**: UNIQUE(workflow_id, source_node_id, target_node_id)

### faqs
- `id` (PK): Auto-increment primary key
- `question`: FAQ question
- `answer`: FAQ answer
- `category`: Optional category
- `created_at`: Timestamp
- `updated_at`: Timestamp

### pdf_documents
- `id` (PK): Auto-increment primary key
- `filename`: PDF filename
- `minio_path`: Path in MinIO storage
- `file_size`: File size in bytes
- `upload_date`: Upload timestamp
- `description`: Optional description
- `is_processed`: 0=pending, 1=processing, 2=completed, -1=failed
- `processing_status`: Status message
- `chunk_count`: Number of text chunks
- `embedding_count`: Number of embeddings
- `processed_at`: Processing completion timestamp

## Dependencies

### Python (Backend)
```
httpx==0.25.2          # Async HTTP client for Hasura queries
aiohttp==3.9.1         # Alternative async HTTP client
transformers==4.35.2   # AI model transformations
torch==2.1.2           # PyTorch tensor operations
sentence-transformers==3.0.1  # Embeddings
pymilvus==2.3.7        # Milvus vector DB client
```

### JavaScript (Frontend)
- Hasura queries use native `fetch` API (no additional dependencies)
- Works with Next.js 14+ and React 18+

## Troubleshooting

### 1. Connection Refused to Hasura

**Error**: `Connection refused to http://localhost:8081/v1/graphql`

**Solution**:
```bash
# Check if containers are running
docker ps

# Restart Hasura
docker restart hasura

# Check logs
docker logs hasura
```

### 2. PostgreSQL Permission Denied

**Error**: `FATAL: Ident authentication failed`

**Solution**:
```bash
# Verify PostgreSQL is running
docker ps | grep hasuradb

# Check environment variables in .env file
cat backend/.env | grep DB_
```

### 3. Hasura Tables Not Visible

**Error**: Tables don't appear in Hasura console

**Solution**:
1. Ensure schema.sql was executed
2. Refresh Hasura console (F5)
3. Go to Data tab → Schema → Reload

### 4. GraphQL Query Errors

**Check**:
1. Hasura admin secret in requests: `x-hasura-admin-secret: myadminsecret`
2. GraphQL syntax in queries
3. Hasura console GraphQL tab for validation

## Next Steps

1. **Install Backend Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Test Hasura Connection**:
   ```bash
   python -c "from services.hasura_client import HasuraClient; import asyncio; asyncio.run(HasuraClient().get_workflows())"
   ```

3. **Update Frontend Components** to use `hasura.js` service

4. **Deploy to Production** (update URLs from localhost)

## Production Deployment

For production:

1. Update `.env` files with production Hasura URL
2. Use environment-specific admin secrets
3. Enable Hasura permissions and row-level security
4. Use PostgreSQL backups
5. Enable HTTPS for Hasura endpoint
6. Use Docker secrets instead of plaintext credentials

## Support

- **Hasura Docs**: https://hasura.io/docs
- **GraphQL Docs**: https://graphql.org/learn
- **PostgreSQL Docs**: https://www.postgresql.org/docs

## Version Info

- **Hasura**: 2.38.0
- **PostgreSQL**: 15
- **Backend**: FastAPI 0.104.1
- **Frontend**: Next.js 14+
- **Project**: AI PDF Chatbot v3.0.0
