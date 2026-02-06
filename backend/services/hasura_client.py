"""
Hasura GraphQL Client Service
Provides utility functions to query Hasura GraphQL API
"""
from __future__ import annotations
import httpx
import logging
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

"""
Hasura GraphQL Client Service
Provides async utility functions to query Hasura GraphQL API.
"""



import logging
from datetime import datetime
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class HasuraClient:
    """Client for interacting with Hasura GraphQL API."""

    def __init__(self):
        self.url = settings.HASURA_URL
        self.headers = {
            "Content-Type": "application/json",
            "x-hasura-admin-secret": settings.HASURA_ADMIN_SECRET,
        }

    async def execute(self, query: str, variables: Optional[dict] = None) -> dict:
        """Execute GraphQL query against Hasura."""
        try:
            async with httpx.AsyncClient() as client:
                payload = {"query": query, "variables": variables or {}}
                response = await client.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )

                result = response.json()

                if "errors" in result:
                    logger.error("Hasura GraphQL Error: %s", result["errors"])
                    raise Exception(f"GraphQL Error: {result['errors']}")

                return result.get("data", {})

        except Exception as exc:  # pragma: no cover - network/remote errors
            logger.error("Hasura Client Error: %s", str(exc))
            raise


# Initialize singleton client
hasura = HasuraClient()


# ==================== WORKFLOWS ====================

async def get_workflows():
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
    return result.get("workflows", [])


async def get_workflow(workflow_id: int):
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
    return result.get("workflows_by_pk")


async def create_workflow(name: str, description: Optional[str] = None):
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
    return result.get("insert_workflows_one")


async def delete_workflow(workflow_id: int):
    query = """
    mutation DeleteWorkflow($id: Int!) {
        delete_workflows_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": workflow_id})
    return result.get("delete_workflows_by_pk")


# ==================== NODES ====================

async def get_nodes(workflow_id: int):
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
    return result.get("nodes", [])


async def get_all_nodes():
    query = """
    query GetAllNodes {
        nodes(order_by: {created_at: desc}) {
            id
            text
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query)
    return result.get("nodes", [])


async def get_node_by_id(node_id: int):
    query = """
    query GetNode($id: Int!) {
        nodes_by_pk(id: $id) {
            id
            text
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query, {"id": node_id})
    return result.get("nodes_by_pk")


async def node_exists(workflow_id: int, text: str) -> bool:
    query = """
    query NodeExists($workflowId: Int!, $text: String!) {
        nodes(where: {workflow_id: {_eq: $workflowId}, text: {_eq: $text}}, limit: 1) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"workflowId": workflow_id, "text": text})
    return bool(result.get("nodes"))


async def get_node_by_text(text: str, workflow_id: Optional[int] = None):
    """Fetch a single node by its text, optionally scoped to a workflow."""
    if workflow_id is not None:
        query = """
        query GetNodeByTextScoped($text: String!, $workflowId: Int!) {
            nodes(
                where: {text: {_eq: $text}, workflow_id: {_eq: $workflowId}},
                order_by: {created_at: desc},
                limit: 1
            ) {
                id
                text
                workflow_id
                created_at
            }
        }
        """
        variables = {"text": text, "workflowId": workflow_id}
    else:
        query = """
        query GetNodeByText($text: String!) {
            nodes(
                where: {text: {_eq: $text}},
                order_by: {created_at: desc},
                limit: 1
            ) {
                id
                text
                workflow_id
                created_at
            }
        }
        """
        variables = {"text": text}

    result = await hasura.execute(query, variables)
    nodes = result.get("nodes", [])
    return nodes[0] if nodes else None


async def search_nodes_by_text(text: str, workflow_id: Optional[int] = None):
    """Partial search for nodes by text (ILIKE)."""
    pattern = f"%{text}%"
    if workflow_id is not None:
        query = """
        query SearchNodesScoped($pattern: String!, $workflowId: Int!) {
            nodes(
                where: {text: {_ilike: $pattern}, workflow_id: {_eq: $workflowId}},
                order_by: {created_at: desc}
            ) {
                id
                text
                workflow_id
                created_at
            }
        }
        """
        variables = {"pattern": pattern, "workflowId": workflow_id}
    else:
        query = """
        query SearchNodes($pattern: String!) {
            nodes(
                where: {text: {_ilike: $pattern}},
                order_by: {created_at: desc}
            ) {
                id
                text
                workflow_id
                created_at
            }
        }
        """
        variables = {"pattern": pattern}

    result = await hasura.execute(query, variables)
    return result.get("nodes", [])


async def create_node(workflow_id: int, text: str):
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
    return result.get("insert_nodes_one")


async def delete_node(node_id: int):
    query = """
    mutation DeleteNode($id: Int!) {
        delete_nodes_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": node_id})
    return result.get("delete_nodes_by_pk")


# ==================== EDGES ====================

async def get_edges(workflow_id: int):
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
    return result.get("edges", [])


async def get_all_edges():
    query = """
    query GetAllEdges {
        edges(order_by: {created_at: desc}) {
            id
            source_node_id
            target_node_id
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query)
    return result.get("edges", [])


async def edge_exists(workflow_id: int, source_node_id: int, target_node_id: int) -> bool:
    query = """
    query EdgeExists($workflowId: Int!, $sourceId: Int!, $targetId: Int!) {
        edges(
            where: {
                workflow_id: {_eq: $workflowId},
                source_node_id: {_eq: $sourceId},
                target_node_id: {_eq: $targetId}
            },
            limit: 1
        ) {
            id
        }
    }
    """
    result = await hasura.execute(
        query,
        {"workflowId": workflow_id, "sourceId": source_node_id, "targetId": target_node_id},
    )
    return bool(result.get("edges"))


async def create_edge(workflow_id: int, source_node_id: int, target_node_id: int):
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
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(
        query,
        {"workflowId": workflow_id, "sourceId": source_node_id, "targetId": target_node_id},
    )
    return result.get("insert_edges_one")


async def delete_edge(edge_id: int):
    query = """
    mutation DeleteEdge($id: Int!) {
        delete_edges_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": edge_id})
    return result.get("delete_edges_by_pk")


# ==================== GRAPH HELPERS ====================

async def get_graph_data():
    """Return all nodes and edges."""
    query = """
    query GetGraph {
        nodes(order_by: {created_at: desc}) {
            id
            text
            workflow_id
            created_at
        }
        edges(order_by: {created_at: desc}) {
            id
            source_node_id
            target_node_id
            workflow_id
            created_at
        }
    }
    """
    result = await hasura.execute(query)
    return {
        "nodes": result.get("nodes", []),
        "edges": result.get("edges", []),
    }


async def get_target_nodes(source_node_id: int):
    """Fetch nodes targeted by edges starting from source_node_id."""
    query = """
    query GetTargetNodes($sourceId: Int!) {
        edges(where: {source_node_id: {_eq: $sourceId}}) {
            target_node_id
            target: target_node {
                id
                text
                workflow_id
                created_at
            }
        }
    }
    """
    result = await hasura.execute(query, {"sourceId": source_node_id})
    edges = result.get("edges", [])
    return [edge.get("target") for edge in edges if edge.get("target")]


async def get_further_options(node_id: int):
    """Alias to fetch downstream targets for a given node."""
    return await get_target_nodes(node_id)


# ==================== FAQS ====================

async def get_faq_by_id(faq_id: int):
    query = """
    query GetFaq($id: Int!) {
        faqs_by_pk(id: $id) {
            id
            question
            answer
            category
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"id": faq_id})
    return result.get("faqs_by_pk")


async def get_faqs(category: Optional[str] = None):
    if category:
        query = """
        query GetFaqsByCategory($category: String!) {
            faqs(where: {category: {_eq: $category}}, order_by: {created_at: desc}) {
                id
                question
                answer
                category
                created_at
                updated_at
            }
        }
        """
        variables = {"category": category}
    else:
        query = """
        query GetFaqs {
            faqs(order_by: {created_at: desc}) {
                id
                question
                answer
                category
                created_at
                updated_at
            }
        }
        """
        variables = None

    result = await hasura.execute(query, variables)
    return result.get("faqs", [])


async def get_faq_categories():
    query = """
    query GetFaqCategories {
        faqs(distinct_on: category, order_by: {category: asc}) {
            category
        }
    }
    """
    result = await hasura.execute(query)
    return [row.get("category") for row in result.get("faqs", []) if row.get("category")]


async def search_faq_exact(question: str):
    query = """
    query SearchFaqExact($question: String!) {
        faqs(where: {question: {_eq: $question}}, limit: 1) {
            id
            question
            answer
            category
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"question": question})
    faqs = result.get("faqs", [])
    return faqs[0] if faqs else None


async def search_faq_partial(question: str):
    query = """
    query SearchFaqPartial($pattern: String!) {
        faqs(where: {question: {_ilike: $pattern}}, order_by: {created_at: desc}) {
            id
            question
            answer
            category
            created_at
            updated_at
        }
    }
    """
    pattern = f"%{question}%"
    result = await hasura.execute(query, {"pattern": pattern})
    return result.get("faqs", [])


async def create_faq(question: str, answer: str, category: Optional[str] = None):
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
    result = await hasura.execute(
        query,
        {"question": question, "answer": answer, "category": category},
    )
    return result.get("insert_faqs_one")


async def update_faq(
    faq_id: int,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    category: Optional[str] = None,
):
    update_fields: dict[str, object] = {}
    if question is not None:
        update_fields["question"] = question
    if answer is not None:
        update_fields["answer"] = answer
    if category is not None:
        update_fields["category"] = category

    if not update_fields:
        return await get_faq_by_id(faq_id)

    query = """
    mutation UpdateFAQ($id: Int!, $set: faqs_set_input!) {
        update_faqs_by_pk(
            pk_columns: {id: $id}
            _set: $set
        ) {
            id
            question
            answer
            category
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"id": faq_id, "set": update_fields})
    return result.get("update_faqs_by_pk")


async def delete_faq(faq_id: int):
    query = """
    mutation DeleteFAQ($id: Int!) {
        delete_faqs_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": faq_id})
    return result.get("delete_faqs_by_pk")


# ==================== PDF DOCUMENTS ====================

async def pdf_exists_by_path(minio_path: str) -> bool:
    query = """
    query PdfExists($minio_path: String!) {
        pdf_documents(where: {minio_path: {_eq: $minio_path}}, limit: 1) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"minio_path": minio_path})
    return bool(result.get("pdf_documents"))


async def pdf_exists_by_filename(filename: str) -> bool:
    """Check if a PDF with the same filename already exists"""
    query = """
    query PdfExistsByFilename($filename: String!) {
        pdf_documents(where: {filename: {_eq: $filename}}, limit: 1) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"filename": filename})
    return bool(result.get("pdf_documents"))


async def create_pdf_document(
    filename: str,
    minio_path: str,
    file_size: int,
    description: Optional[str] = None,
    processing_status: Optional[str] = None,
    is_processed: Optional[int] = None,
    upload_date: Optional[str] = None,
):
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
        "chunk_count": 0,
        "embedding_count": 0,
    }

    if description is not None:
        payload["description"] = description
    if processing_status is not None:
        payload["processing_status"] = processing_status
    if is_processed is not None:
        payload["is_processed"] = is_processed
    if upload_date is not None:
        payload["upload_date"] = upload_date

    result = await hasura.execute(mutation, {"object": payload})
    return result.get("insert_pdf_documents_one")


async def get_pdf_by_id(pdf_id: int):
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


async def get_pdf_id_by_name(filename: str):
    """Get PDF ID by filename"""
    query = """
    query GetPdfByName($filename: String!) {
        pdf_documents(where: {filename: {_eq: $filename}}, limit: 1) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"filename": filename})
    pdfs = result.get("pdf_documents", [])
    return pdfs[0]["id"] if pdfs else None


async def get_all_pdfs():
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
    status_message: Optional[str] = None,
    chunk_count: Optional[int] = None,
    embedding_count: Optional[int] = None,
):
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


# ==================== CHAT SESSIONS ====================

async def create_chat_session(
    session_id: str,
    user_id: str,
    title: str = "New Chat Session"
):
    """Create a new chat session"""
    mutation = """
    mutation CreateChatSession(
        $sessionId: String!
        $userId: String!
        $title: String!
    ) {
        insert_chat_sessions_one(object: {
            session_id: $sessionId
            user_id: $userId
            title: $title
        }) {
            session_id
            user_id
            title
            total_messages
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(
        mutation,
        {
            "sessionId": session_id,
            "userId": user_id,
            "title": title
        }
    )
    return result.get("insert_chat_sessions_one")


async def get_user_chat_sessions(user_id: str):
    """Get all active chat sessions for a user"""
    query = """
    query GetUserChatSessions($userId: String!) {
        chat_sessions(
            where: {user_id: {_eq: $userId}, is_active: {_eq: true}}
            order_by: {updated_at: desc}
        ) {
            session_id
            user_id
            title
            total_messages
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"userId": user_id})
    return result.get("chat_sessions", [])


async def get_chat_session(session_id: str):
    """Get a specific chat session"""
    query = """
    query GetChatSession($sessionId: String!) {
        chat_sessions(where: {session_id: {_eq: $sessionId}}) {
            session_id
            user_id
            title
            total_messages
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"sessionId": session_id})
    sessions = result.get("chat_sessions", [])
    return sessions[0] if sessions else None


async def get_chat_messages(session_id: str):
    """Get all messages in a chat session"""
    query = """
    query GetChatMessages($sessionId: String!) {
        chat_messages(
            where: {session_id: {_eq: $sessionId}}
            order_by: {timestamp: asc}
        ) {
            id
            message_id
            session_id
            user_id
            question
            answer
            source
            timestamp
        }
    }
    """
    result = await hasura.execute(query, {"sessionId": session_id})
    return result.get("chat_messages", [])


async def add_chat_message(
    message_id: str,
    session_id: str,
    user_id: str,
    question: str,
    answer: str = None,
    source: str = None
):
    """Add a question-answer pair to a chat session"""
    logger.info(f"📝 add_chat_message called: session={session_id}, user={user_id}, msg_id={message_id}")
    mutation = """
    mutation AddChatMessage(
        $messageId: String!
        $sessionId: String!
        $userId: String!
        $question: String!
        $answer: String
        $source: String
    ) {
        insert_chat_messages_one(object: {
            message_id: $messageId
            session_id: $sessionId
            user_id: $userId
            question: $question
            answer: $answer
            source: $source
        }) {
            id
            message_id
            session_id
            user_id
            question
            answer
            source
            timestamp
        }
    }
    """
    variables = {
        "messageId": message_id,
        "sessionId": session_id,
        "userId": user_id,
        "question": question,
        "answer": answer,
        "source": source
    }
    logger.info(f"📤 Executing mutation with variables: {variables}")
    result = await hasura.execute(mutation, variables)
    logger.info(f"📥 Got result: {result}")
    message = result.get("insert_chat_messages_one")
    
    # Update session's total_messages count
    if message:
        logger.info(f"✅ Message saved successfully, updating session count...")
        await update_session_message_count(session_id)
    else:
        logger.warning(f"⚠️  No message returned from insert operation")
    
    return message
    
    return message


async def update_session_message_count(session_id: str):
    """Update the total_messages count for a session"""
    count_query = """
    query CountSessionMessages($sessionId: String!) {
        chat_messages_aggregate(where: {session_id: {_eq: $sessionId}}) {
            aggregate {
                count
            }
        }
    }
    """
    count_result = await hasura.execute(count_query, {"sessionId": session_id})
    total_messages = count_result.get("chat_messages_aggregate", {}).get("aggregate", {}).get("count", 0)
    
    update_mutation = """
    mutation UpdateSessionMessageCount($sessionId: String!, $totalMessages: Int!) {
        update_chat_sessions(
            where: {session_id: {_eq: $sessionId}}
            _set: {total_messages: $totalMessages}
        ) {
            affected_rows
        }
    }
    """
    await hasura.execute(
        update_mutation,
        {"sessionId": session_id, "totalMessages": total_messages}
    )


async def update_chat_session(session_id: str, title: str):
    """Update a chat session's title"""
    mutation = """
    mutation UpdateChatSession($sessionId: String!, $title: String!) {
        update_chat_sessions(
            where: {session_id: {_eq: $sessionId}}
            _set: {title: $title}
        ) {
            affected_rows
            returning {
                session_id
                title
                updated_at
            }
        }
    }
    """
    result = await hasura.execute(
        mutation,
        {"sessionId": session_id, "title": title}
    )
    return result.get("update_chat_sessions", {}).get("returning", [])


async def delete_chat_session(session_id: str):
    """Soft delete a chat session (mark as inactive)"""
    mutation = """
    mutation DeleteChatSession($sessionId: String!) {
        update_chat_sessions(
            where: {session_id: {_eq: $sessionId}}
            _set: {is_active: false}
        ) {
            affected_rows
        }
    }
    """
    result = await hasura.execute(mutation, {"sessionId": session_id})
    return result.get("update_chat_sessions", {}).get("affected_rows", 0) > 0


async def clear_chat_messages(session_id: str):
    """Clear all messages from a chat session"""
    delete_mutation = """
    mutation ClearChatMessages($sessionId: String!) {
        delete_chat_messages(where: {session_id: {_eq: $sessionId}}) {
            affected_rows
        }
    }
    """
    result = await hasura.execute(delete_mutation, {"sessionId": session_id})
    
    # Reset total_messages count
    if result.get("delete_chat_messages", {}).get("affected_rows", 0) > 0:
        await update_session_message_count(session_id)
    
    return result.get("delete_chat_messages", {}).get("affected_rows", 0)


# ==================== USER AUTHENTICATION ====================

async def get_user_by_username(username: str):
    """Get user by username"""
    query = """
    query GetUserByUsername($username: String!) {
        users(where: {username: {_eq: $username}}, limit: 1) {
            id
            username
            email
            password_hash
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"username": username})
    users = result.get("users", [])
    return users[0] if users else None


async def get_user_by_email(email: str):
    """Get user by email"""
    query = """
    query GetUserByEmail($email: String!) {
        users(where: {email: {_eq: $email}}, limit: 1) {
            id
            username
            email
            password_hash
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"email": email})
    users = result.get("users", [])
    return users[0] if users else None


async def get_user_by_id(user_id: int):
    """Get user by ID"""
    query = """
    query GetUserById($id: Int!) {
        users_by_pk(id: $id) {
            id
            username
            email
            password_hash
            is_active
            created_at
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"id": user_id})
    return result.get("users_by_pk")


async def create_user(username: str, email: str, password_hash: str):
    """Create new user"""
    query = """
    mutation CreateUser($username: String!, $email: String!, $password_hash: String!) {
        insert_users_one(object: {username: $username, email: $email, password_hash: $password_hash, is_active: 1}) {
            id
            username
            email
            is_active
            created_at
        }
    }
    """
    result = await hasura.execute(query, {
        "username": username,
        "email": email,
        "password_hash": password_hash
    })
    return result.get("insert_users_one")


async def update_user(user_id: int, username: Optional[str] = None, email: Optional[str] = None, is_active: Optional[int] = None):
    """Update user information"""
    update_fields = {}
    if username is not None:
        update_fields["username"] = username
    if email is not None:
        update_fields["email"] = email
    if is_active is not None:
        update_fields["is_active"] = is_active
    
    if not update_fields:
        return await get_user_by_id(user_id)
    
    query = """
    mutation UpdateUser($id: Int!, $set: users_set_input!) {
        update_users_by_pk(pk_columns: {id: $id}, _set: $set) {
            id
            username
            email
            is_active
            updated_at
        }
    }
    """
    result = await hasura.execute(query, {"id": user_id, "set": update_fields})
    return result.get("update_users_by_pk")


async def delete_user(user_id: int):
    """Delete user"""
    query = """
    mutation DeleteUser($id: Int!) {
        delete_users_by_pk(id: $id) {
            id
        }
    }
    """
    result = await hasura.execute(query, {"id": user_id})
    return result.get("delete_users_by_pk")

