"""
Chat Sessions Routes
Handles chat session creation, retrieval, and message management
Uses Hasura GraphQL for data persistence
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging
from services import hasura_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat-sessions", tags=["Chat Sessions"])


# ==================== Request Models ====================

class CreateSessionRequest(BaseModel):
    user_id: str
    title: str = "New Chat Session"


class AddMessageRequest(BaseModel):
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str


class UpdateSessionRequest(BaseModel):
    title: str


# ==================== API Endpoints ====================

@router.post("/create", response_model=dict)
async def create_chat_session(request: CreateSessionRequest):
    """
    Create a new chat session for a user
    
    - **user_id**: The ID of the user (required)
    - **title**: Session title (optional, defaults to "New Chat Session")
    """
    try:
        session_id = f"session_{datetime.utcnow().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating chat session for user {request.user_id}")
        
        session = await hasura_client.create_chat_session(
            session_id=session_id,
            user_id=request.user_id,
            title=request.title
        )
        
        if not session:
            raise Exception("Failed to create chat session")
        
        logger.info(f"Chat session created successfully: {session_id}")
        
        return {
            "success": True,
            "message": "Chat session created successfully",
            "data": session
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=dict)
async def get_user_sessions(user_id: str):
    """
    Get all active chat sessions for a user
    
    - **user_id**: The ID of the user (required)
    """
    try:
        logger.info(f"Fetching chat sessions for user {user_id}")
        
        sessions = await hasura_client.get_user_chat_sessions(user_id)
        
        logger.info(f"Found {len(sessions)} chat sessions for user {user_id}")
        
        return {
            "success": True,
            "data": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error fetching user sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chat sessions: {str(e)}"
        )


@router.get("/{session_id}", response_model=dict)
async def get_session_details(session_id: str):
    """
    Get details of a specific chat session
    
    - **session_id**: The ID of the session (required)
    """
    try:
        logger.info(f"Fetching details for session {session_id}")
        
        session = await hasura_client.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return {
            "success": True,
            "data": session
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch session details: {str(e)}"
        )


@router.get("/{session_id}/messages", response_model=dict)
async def get_session_messages(session_id: str):
    """
    Get all messages in a chat session
    
    - **session_id**: The ID of the session (required)
    """
    try:
        logger.info(f"Fetching messages for session {session_id}")
        
        # Verify session exists
        session = await hasura_client.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        messages = await hasura_client.get_chat_messages(session_id)
        
        logger.info(f"Found {len(messages)} messages in session {session_id}")
        
        return {
            "success": True,
            "data": messages,
            "count": len(messages),
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch session messages: {str(e)}"
        )


@router.post("/{session_id}/messages", response_model=dict)
async def add_message_to_session(session_id: str, request: AddMessageRequest):
    """
    Add a message to a chat session
    
    - **session_id**: The ID of the session (required)
    - **user_id**: The ID of the user (required)
    - **role**: Message role - 'user' or 'assistant' (required)
    - **content**: The message content (required)
    """
    try:
        logger.info(f"Adding message to session {session_id} from user {request.user_id}")
        
        # Validate role
        if request.role not in ['user', 'assistant']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'user' or 'assistant'"
            )
        
        # Verify session exists
        session = await hasura_client.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Create message with unique ID
        message_id = f"msg_{datetime.utcnow().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        message = await hasura_client.add_chat_message(
            message_id=message_id,
            session_id=session_id,
            user_id=request.user_id,
            role=request.role,
            content=request.content
        )
        
        if not message:
            raise Exception("Failed to add message to session")
        
        logger.info(f"Message added successfully to session {session_id}")
        
        return {
            "success": True,
            "message": "Message added successfully",
            "data": message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message to session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message: {str(e)}"
        )


@router.put("/{session_id}", response_model=dict)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    Update a chat session's title
    
    - **session_id**: The ID of the session (required)
    - **title**: New session title (required)
    """
    try:
        logger.info(f"Updating session {session_id}")
        
        # Verify session exists
        session = await hasura_client.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        result = await hasura_client.update_chat_session(
            session_id=session_id,
            title=request.title
        )
        
        if not result:
            raise Exception("Failed to update chat session")
        
        logger.info(f"Session {session_id} updated successfully")
        
        return {
            "success": True,
            "message": "Session updated successfully",
            "data": result[0] if result else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )


@router.delete("/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    """
    Delete a chat session (soft delete - marks as inactive)
    
    - **session_id**: The ID of the session to delete (required)
    """
    try:
        logger.info(f"Deleting session {session_id}")
        
        # Verify session exists
        session = await hasura_client.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        success = await hasura_client.delete_chat_session(session_id)
        
        if not success:
            raise Exception("Failed to delete chat session")
        
        logger.info(f"Session {session_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Session deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.delete("/{session_id}/messages", response_model=dict)
async def clear_session_messages(session_id: str):
    """
    Clear all messages from a chat session
    
    - **session_id**: The ID of the session (required)
    """
    try:
        logger.info(f"Clearing messages for session {session_id}")
        
        # Verify session exists
        session = await hasura_client.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        affected_rows = await hasura_client.clear_chat_messages(session_id)
        
        logger.info(f"Cleared {affected_rows} messages from session {session_id}")
        
        return {
            "success": True,
            "message": "Messages cleared successfully",
            "messages_cleared": affected_rows
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear messages: {str(e)}"
        )
