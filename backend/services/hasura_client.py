"""
Hasura GraphQL Client Service
Provides utility functions to query Hasura GraphQL API
"""

import httpx
import logging
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)


class HasuraClient:
    """Client for interacting with Hasura GraphQL API"""

    def __init__(self):
        self.url = settings.HASURA_URL
        self.headers = {
            "Content-Type": "application/json",
            "x-hasura-admin-secret": settings.HASURA_ADMIN_SECRET
        }

    async def execute(self, query: str, variables: dict = None):
        """Execute GraphQL query against Hasura"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {"query": query}
                if variables:
                    payload["variables"] = variables

                response = await client.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )

                result = response.json()

                if "errors" in result:
                    logger.error(f"Hasura GraphQL Error: {result['errors']}")
                    raise Exception(f"GraphQL Error: {result['errors']}")

                return result.get("data")

        except Exception as e:
            logger.error(f"Hasura Client Error: {str(e)}")
            raise


# Initialize client
hasura = HasuraClient()


# ==================== WORKFLOWS ====================

async def get_workflows():
    """Fetch all workflows"""
    query = """
    query GetWorkflows {
        workflows(order_by: {created_at: desc}) {
            id
            name
            description
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query)
    return result["workflows"]


async def get_workflow(workflow_id: int):
    """Fetch single workflow"""
    query = """
    query GetWorkflow($id: Int!) {
        workflows_by_pk(id: $id) {
            id
            name
            description
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"id": workflow_id})
    return result["workflows_by_pk"]


async def create_workflow(name: str, description: str = None):
    """Create new workflow"""
    query = """
    mutation CreateWorkflow($name: String!, $description: String) {
        insert_workflows_one(object: {name: $name, description: $description}) {
            id
            name
            description
            created_at
        }
    }
    """
    result = await hasura.execute(query, {"name": name, "description": description})
    return result["insert_workflows_one"]


async def delete_workflow(workflow_id: int):
    """Delete workflow"""
    query = """
    mutation DeleteWorkflow($id: Int!) {
        delete_workflows_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": workflow_id})
    return result["delete_workflows_by_pk"]


# ==================== NODES ====================

async def get_nodes(workflow_id: int):
    """Fetch nodes for workflow"""
    query = """
    query GetNodes($workflowId: Int!) {
        nodes(where: {workflow_id: {_eq: $workflowId}}, order_by: {created_at: desc}) {
            id
            text
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query, {"workflowId": workflow_id})
    return result["nodes"]


async def create_node(workflow_id: int, text: str):
    """Create new node"""
    query = """
    mutation CreateNode($workflowId: Int!, $text: String!) {
        insert_nodes_one(object: {workflow_id: $workflowId, text: $text}) {
            id
            text
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query, {"workflowId": workflow_id, "text": text})
    return result["insert_nodes_one"]


async def delete_node(node_id: int):
    """Delete node"""
    query = """
    mutation DeleteNode($id: Int!) {
        delete_nodes_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": node_id})
    return result["delete_nodes_by_pk"]


# ==================== EDGES ====================

async def get_edges(workflow_id: int):
    """Fetch edges for workflow"""
    query = """
    query GetEdges($workflowId: Int!) {
        edges(where: {workflow_id: {_eq: $workflowId}}, order_by: {created_at: desc}) {
            id
            source_node_id
            target_node_id
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query, {"workflowId": workflow_id})
    return result["edges"]


async def create_edge(workflow_id: int, source_node_id: int, target_node_id: int):
    """Create new edge"""
    query = """
    mutation CreateEdge($workflowId: Int!, $sourceId: Int!, $targetId: Int!) {
        insert_edges_one(object: {
            workflow_id: $workflowId
            source_node_id: $sourceId
            target_node_id: $targetId
        }) {
            id
            source_node_id
            target_node_id
            created_at
        }
    }
    """
    result = await hasura.execute(query, {
        "workflowId": workflow_id,
        "sourceId": source_node_id,
        "targetId": target_node_id
    })
    return result["insert_edges_one"]


async def delete_edge(edge_id: int):
    """Delete edge"""
    query = """
    mutation DeleteEdge($id: Int!) {
        delete_edges_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": edge_id})
    return result["delete_edges_by_pk"]


# ==================== FAQS ====================

async def get_faqs():
    """Fetch all FAQs"""
    query = """
    query GetFAQs {
        faqs(order_by: {created_at: desc}) {
            id
            question
            answer
            category
            created_at
        }
    }
    """
    result = await hasura.execute(query)
    return result["faqs"]


async def create_faq(question: str, answer: str, category: str = None):
    """Create new FAQ"""
    query = """
    mutation CreateFAQ($question: String!, $answer: String!, $category: String) {
        insert_faqs_one(object: {question: $question, answer: $answer, category: $category}) {
            id
            question
            answer
            category
            created_at
        }
    }
    """
    result = await hasura.execute(query, {
        "question": question,
        "answer": answer,
        "category": category
    })
    return result["insert_faqs_one"]


async def update_faq(faq_id: int, question: str, answer: str, category: str = None):
    """Update FAQ"""
    query = """
    mutation UpdateFAQ($id: Int!, $question: String!, $answer: String!, $category: String) {
        update_faqs_by_pk(
            pk_columns: {id: $id}
            _set: {question: $question, answer: $answer, category: $category}
        ) {
            id
            question
            answer
            category
        }
    }
    """
    result = await hasura.execute(query, {
        "id": faq_id,
        "question": question,
        "answer": answer,
        "category": category
    })
    return result["update_faqs_by_pk"]


async def delete_faq(faq_id: int):
    """Delete FAQ"""
    query = """
    mutation DeleteFAQ($id: Int!) {
        delete_faqs_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": faq_id})
    return result["delete_faqs_by_pk"]


# ==================== PDF DOCUMENTS ====================


async def pdf_exists_by_path(minio_path: str) -> bool:
    """Check if a PDF document exists by its MinIO path"""
    query = """
    query PdfExists($minio_path: String!) {
        pdf_documents(where: {minio_path: {_eq: $minio_path}}, limit: 1) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"minio_path": minio_path})
    return bool(result.get("pdf_documents"))


async def create_pdf_document(
    filename: str,
    minio_path: str,
    file_size: int,
    description: str | None = None,
    processing_status: str | None = None,
    is_processed: int | None = None,
):
    """Create a new PDF document record"""
    mutation = """
    mutation CreatePdf($object: pdf_documents_insert_input!) {
        insert_pdf_documents_one(object: $object) {
            id
            filename
            minio_path
            file_size
            upload_date
            description
            is_processed
            processing_status
            chunk_count
            embedding_count
            processed_at
        }
    }
    """

    payload = {
        "filename": filename,
        "minio_path": minio_path,
        "file_size": file_size,
    }

    if description is not None:
        payload["description"] = description
    if processing_status is not None:
        payload["processing_status"] = processing_status
    if is_processed is not None:
        payload["is_processed"] = is_processed

    result = await hasura.execute(mutation, {"object": payload})
    return result["insert_pdf_documents_one"]


async def get_pdf_by_id(pdf_id: int):
    """Fetch a single PDF document by ID"""
    query = """
    query GetPdf($id: Int!) {
        pdf_documents_by_pk(id: $id) {
            id
            filename
            minio_path
            file_size
            upload_date
            description
            is_processed
            processing_status
            chunk_count
            embedding_count
            processed_at
        }
    }
    """
    result = await hasura.execute(query, {"id": pdf_id})
    return result.get("pdf_documents_by_pk")


async def get_all_pdfs():
    """Fetch all PDF documents ordered by upload date"""
    query = """
    query GetPdfs {
        pdf_documents(order_by: {upload_date: desc}) {
            id
            filename
            minio_path
            file_size
            upload_date
            description
            is_processed
            processing_status
            chunk_count
            embedding_count
            processed_at
        }
    }
    """
    result = await hasura.execute(query)
    return result.get("pdf_documents", [])


async def delete_pdf(pdf_id: int):
    """Delete a PDF document record"""
    mutation = """
    mutation DeletePdf($id: Int!) {
        delete_pdf_documents_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(mutation, {"id": pdf_id})
    return result.get("delete_pdf_documents_by_pk")


async def update_pdf_processing_status(
    pdf_id: int,
    status: int,
    status_message: str | None = None,
    chunk_count: int | None = None,
    embedding_count: int | None = None,
):
    """Update PDF processing status and optional counters"""
    update_fields: dict[str, object] = {"is_processed": status}

    if status_message is not None:
        update_fields["processing_status"] = status_message
    if chunk_count is not None:
        update_fields["chunk_count"] = chunk_count
    if embedding_count is not None:
        update_fields["embedding_count"] = embedding_count
    if status == 2:
        update_fields["processed_at"] = datetime.utcnow().isoformat()

    mutation = """
    mutation UpdatePdfStatus($id: Int!, $set: pdf_documents_set_input!) {
        update_pdf_documents_by_pk(pk_columns: {id: $id}, _set: $set) {
            id
            is_processed
            processing_status
            chunk_count
            embedding_count
            processed_at
        }
    }
    """

    result = await hasura.execute(mutation, {"id": pdf_id, "set": update_fields})
    return result.get("update_pdf_documents_by_pk")
