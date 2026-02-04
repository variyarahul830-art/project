"""
Chat Sessions Routes (Backend Proxy to Hasura)
All routes require JWT authentication
"""

from fastapi import APIRouter, HTTPException, status, Depends
from middleware.auth import get_current_user
from services.hasura_client import (
    get_user_chat_sessions,
    get_chat_session,
    create_chat_session,
    get_chat_messages,
    update_chat_session,
    delete_chat_session
)
from pydantic import BaseModel
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"
    category: str = "General"


class UpdateSessionRequest(BaseModel):
    title: str
    category: Optional[str] = None


@router.get("/")
async def get_sessions(current_user_id: int = Depends(get_current_user)):
    """Get all sessions for authenticated user"""
    try:
        logger.info(f"📋 Fetching sessions for user: {current_user_id}")
        result = await get_user_chat_sessions(str(current_user_id))
        # result is already a list from hasura_client
        return {"sessions": result if isinstance(result, list) else []}
    except Exception as e:
        logger.error(f"❌ Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")


@router.get("/{session_id}")
async def get_session(session_id: str, current_user_id: int = Depends(get_current_user)):
    """Get specific session - verifies ownership"""
    try:
        logger.info(f"📋 Fetching session: {session_id} for user: {current_user_id}")
        
        # Try to query by session_id first (UUID format)
        session = await get_chat_session(session_id)
        
        # If not found and session_id looks numeric, it might be the 'id' field
        # Query by id instead by getting all sessions and filtering
        if not session:
            sessions = await get_user_chat_sessions(str(current_user_id))
            session = next((s for s in sessions if str(s.get("id")) == session_id), None)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify ownership
        if session.get("user_id") != str(current_user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"session": session}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch session")


@router.post("/")
async def create_session(
    request: CreateSessionRequest,
    current_user_id: int = Depends(get_current_user)
):
    """Create new chat session"""
    try:
        logger.info(f"➕ Creating session for user: {current_user_id}")
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        result = await create_chat_session(
            session_id=session_id,
            user_id=str(current_user_id),
            title=request.title,
            category=request.category
        )
        return {"session": result}
    except Exception as e:
        logger.error(f"❌ Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.put("/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user_id: int = Depends(get_current_user)
):
    """Update session title/category - verifies ownership"""
    try:
        # First verify ownership
        session = await get_chat_session(session_id)
        
        # If not found and session_id looks numeric, it might be the 'id' field
        actual_session_id = session_id
        if not session:
            sessions = await get_user_chat_sessions(str(current_user_id))
            session = next((s for s in sessions if str(s.get("id")) == session_id), None)
            if session:
                actual_session_id = session.get("session_id")
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.get("user_id") != str(current_user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"✏️ Updating session: {actual_session_id}")
        result = await update_chat_session(
            session_id=actual_session_id,
            title=request.title,
            category=request.category or "General"
        )
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user_id: int = Depends(get_current_user)
):
    """Delete session - verifies ownership"""
    try:
        # First verify ownership
        session = await get_chat_session(session_id)
        
        # If not found and session_id looks numeric, it might be the 'id' field
        actual_session_id = session_id
        if not session:
            sessions = await get_user_chat_sessions(str(current_user_id))
            session = next((s for s in sessions if str(s.get("id")) == session_id), None)
            if session:
                actual_session_id = session.get("session_id")
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.get("user_id") != str(current_user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"🗑️ Deleting session: {actual_session_id}")
        result = await delete_chat_session(actual_session_id)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get("/{session_id}/messages")
async def get_messages(
    session_id: str,
    current_user_id: int = Depends(get_current_user)
):
    """Get all messages in a session - verifies ownership"""
    try:
        # Verify session ownership first
        session = await get_chat_session(session_id)
        
        # If not found and session_id looks numeric, it might be the 'id' field
        if not session:
            sessions = await get_user_chat_sessions(str(current_user_id))
            session = next((s for s in sessions if str(s.get("id")) == session_id), None)
            if session:
                session_id = session.get("session_id")  # Use the actual session_id for querying messages
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.get("user_id") != str(current_user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"💬 Fetching messages for session: {session_id}")
        messages = await get_chat_messages(session_id)
        # messages is already a list from hasura_client
        return {"messages": messages if isinstance(messages, list) else []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")
