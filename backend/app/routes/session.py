"""
Session management routes.
Handles chat session lifecycle and history.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app import config
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["session"])


# === Pydantic models for requests/responses ===

class SessionRequest(BaseModel):
    """Request to create a new session"""
    title: Optional[str] = Field(None, description="Session title (auto-generated if not provided)")


class SessionResponse(BaseModel):
    """Session response model"""
    id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    created_at: str = Field(..., description="Creation time")
    updated_at: str = Field(..., description="Last update time")


class MessageResponse(BaseModel):
    """Message response model"""
    id: str = Field(..., description="Message ID")
    question: str = Field(..., description="User's question")
    answer: str = Field(..., description="LLM answer")
    sources: List[str] = Field(default=[], description="Document sources")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    created_at: str = Field(..., description="Message timestamp")


# === Dependency injection ===

def get_chat_service(rag_service: RAGService = Depends(lambda: RAGService(
    openai_api_key=config.OPENAI_API_KEY,
    faiss_index_path=config.FAISS_INDEX_PATH,
    faiss_metadata_path=config.FAISS_METADATA_PATH,
    embedding_model=config.OPENAI_EMBEDDING_MODEL,
    llm_model=config.OPENAI_MODEL,
    chunk_size=config.MAX_CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    top_k=config.TOP_K_RESULTS
))) -> ChatService:
    """Dependency injection for chat service."""
    return ChatService(rag_service)


# === Routes ===

@router.post("/new", response_model=SessionResponse)
async def create_session(
    request: SessionRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> SessionResponse:
    """
    Create a new chat session.
    
    Request body:
    - **title**: Optional session title (auto-generated if not provided)
    
    Returns:
    - **id**: Session ID
    - **title**: Session title
    - **created_at**: Creation timestamp
    - **updated_at**: Last update timestamp
    
    Raises:
    - 500: Database error
    """
    try:
        title = request.title or "New Conversation"
        
        logger.info(f"Creating new session: {title}")
        session = await chat_service.create_session(title)
        
        return SessionResponse(
            id=str(session.id),
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating session: {str(e)}"
        )


@router.get("", response_model=List[SessionResponse])
async def get_all_sessions(
    chat_service: ChatService = Depends(get_chat_service)
) -> List[SessionResponse]:
    """
    Retrieve all chat sessions.
    Sorted by creation time (newest first).
    
    Returns:
    - List of sessions with metadata
    
    Raises:
    - 500: Database error
    """
    try:
        logger.info("Retrieving all sessions")
        sessions = await chat_service.get_all_sessions()
        
        return [
            SessionResponse(
                id=str(session.id),
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat()
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving sessions"
        )


@router.get("/{session_id}", response_model=dict)
async def get_session_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> dict:
    """
    Get chat history for a specific session.
    
    Path parameters:
    - **session_id**: Session ID
    
    Returns:
    - **session**: Session metadata
    - **messages**: List of messages in the session
    
    Raises:
    - 404: Session not found
    - 500: Database error
    """
    try:
        logger.info(f"Retrieving history for session: {session_id}")
        
        # Get session
        session = await chat_service.get_session(session_id)
        
        # Get messages
        messages = await chat_service.get_session_messages(session_id)
        
        return {
            "session": SessionResponse(
                id=str(session.id),
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat()
            ),
            "messages": [
                MessageResponse(
                    id=str(msg.id),
                    question=msg.question,
                    answer=msg.answer,
                    sources=msg.sources,
                    confidence=msg.confidence,
                    created_at=msg.created_at.isoformat()
                )
                for msg in messages
            ]
        }
        
    except ValueError as e:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving session history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving session history"
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> dict:
    """
    Delete a session and all its messages.
    
    Path parameters:
    - **session_id**: Session ID to delete
    
    Returns:
    - **success**: Confirmation message
    
    Raises:
    - 404: Session not found
    - 500: Database error
    """
    try:
        logger.info(f"Deleting session: {session_id}")
        
        # Verify session exists first
        await chat_service.get_session(session_id)
        
        # Delete session
        await chat_service.delete_session(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} and all messages deleted"
        }
        
    except ValueError as e:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting session"
        )
