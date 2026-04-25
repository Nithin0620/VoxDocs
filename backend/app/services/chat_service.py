"""
Chat service for session and message management.
Orchestrates Q&A storage and retrieval with RAG pipeline.
"""
import logging
from typing import List
from datetime import datetime
from bson import ObjectId
from app.db.models import Session, Message
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Manages chat sessions and messages.
    Bridges RAG service with database persistence.
    """

    def __init__(self, rag_service: RAGService):
        """
        Initialize chat service.
        
        Args:
            rag_service: RAG service instance for query processing
        """
        self.rag_service = rag_service

    async def create_session(self, title: str) -> Session:
        """
        Create a new chat session.
        
        Args:
            title: Session title
            
        Returns:
            Created Session document
        """
        try:
            logger.info(f"Creating new session: {title}")
            
            session = Session(
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await session.save()
            logger.info(f"Session created: {session.id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise

    async def get_all_sessions(self) -> List[Session]:
        """
        Retrieve all chat sessions.
        
        Returns:
            List of Session documents, sorted by creation time (newest first)
        """
        try:
            sessions = await Session.find_all().sort(
                [("created_at", -1)]
            ).to_list()
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            raise

    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve a specific session by ID.
        
        Args:
            session_id: Session ID (as string or ObjectId)
            
        Returns:
            Session document
            
        Raises:
            ValueError: If session not found
        """
        try:
            # Convert string to ObjectId if needed
            obj_id = ObjectId(session_id) if isinstance(session_id, str) else session_id
            
            session = await Session.get(obj_id)
            
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            logger.info(f"Retrieved session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")
            raise

    async def get_session_messages(self, session_id: str, limit: int = None) -> List[Message]:
        """
        Retrieve all messages in a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of Message documents, sorted by creation time
        """
        try:
            logger.info(f"Retrieving messages for session: {session_id}")
            
            # Validate session exists
            await self.get_session(session_id)
            
            # Query messages
            query = Message.find(Message.session_id == str(session_id))
            
            if limit:
                query = query.limit(limit)
            
            messages = await query.sort(
                [("created_at", 1)]  # Ascending order
            ).to_list()
            
            logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            raise

    async def add_message(
        self,
        session_id: str,
        question: str,
        answer: str,
        sources: List[str],
        confidence: float
    ) -> Message:
        """
        Add a Q&A message to a session.
        
        Args:
            session_id: Session ID
            question: User's question
            answer: LLM generated answer
            sources: Retrieved document sources
            confidence: Confidence score (0-1)
            
        Returns:
            Created Message document
        """
        try:
            # Validate session exists
            await self.get_session(session_id)
            
            logger.info(f"Adding message to session: {session_id}")
            
            message = Message(
                session_id=str(session_id),
                question=question,
                answer=answer,
                sources=sources,
                confidence=confidence,
                created_at=datetime.utcnow()
            )
            
            await message.save()
            
            # Update session's updated_at timestamp
            session = await Session.get(ObjectId(session_id))
            if session:
                session.updated_at = datetime.utcnow()
                await session.save()
            
            logger.info(f"Message added: {message.id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            logger.info(f"Deleting session: {session_id}")
            
            obj_id = ObjectId(session_id) if isinstance(session_id, str) else session_id
            
            # Delete all messages in session
            await Message.find(Message.session_id == str(session_id)).delete_many()
            
            # Delete session
            session = await Session.get(obj_id)
            if session:
                await session.delete()
            
            logger.info(f"Session deleted: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            raise

    async def get_context_for_rag(self, session_id: str, limit: int = 5) -> str:
        """
        Get recent conversation context for RAG.
        Used to provide conversation history to the LLM.
        
        Args:
            session_id: Session ID
            limit: Number of previous messages to include
            
        Returns:
            Formatted context string
        """
        try:
            messages = await self.get_session_messages(session_id, limit=limit)
            
            if not messages:
                return ""
            
            context = "Recent conversation:\n"
            for msg in messages[-limit:]:
                context += f"Q: {msg.question}\nA: {msg.answer}\n\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {str(e)}")
            return ""

    async def auto_generate_session_title(self, session_id: str) -> None:
        """
        Auto-generate session title from first message.
        
        Args:
            session_id: Session ID
        """
        try:
            messages = await self.get_session_messages(session_id, limit=1)
            
            if not messages:
                return
            
            first_message = messages[0].question
            
            # Extract first 50 chars as title
            title = first_message[:50]
            if len(first_message) > 50:
                title += "..."
            
            session = await Session.get(ObjectId(session_id))
            session.title = title
            await session.save()
            
            logger.info(f"Auto-generated title for session {session_id}: {title}")
            
        except Exception as e:
            logger.error(f"Error auto-generating title: {str(e)}")
