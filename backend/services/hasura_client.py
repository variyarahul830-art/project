"""
Hasura GraphQL Client Service
Provides utility functions to query Hasura GraphQL API
"""

import httpx
import logging
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
