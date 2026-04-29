"""
Beanie ODM models for MongoDB Atlas.
Defines document structures for Session, Message, and Document.
"""
from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import Field


class Session(Document):
    """
    Chat session document.
    Represents a conversation session with a user.
    """
    title: str = Field(..., description="Session title")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Settings:
        name = "sessions"
        indexes = ["created_at", "updated_at"]

    def __repr__(self) -> str:
        return f"<Session {self.id}: {self.title}>"


class Message(Document):
    """
    Chat message document.
    Stores individual Q&A pairs in a session.
    """
    session_id: str = Field(..., description="Reference to session ID")
    question: str = Field(..., min_length=1, description="User's question")
    answer: str = Field(..., description="LLM generated answer")
    sources: List[str] = Field(default_factory=list, description="Retrieved document sources")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Answer confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")

    class Settings:
        name = "messages"
        indexes = ["session_id", "created_at"]

    def __repr__(self) -> str:
        return f"<Message {self.id}: {self.question[:30]}...>"


class Document(Document):
    """
    Uploaded document metadata.
    Tracks which documents have been uploaded and processed.
    """
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Path to stored file")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    chunk_count: int = Field(default=0, description="Number of text chunks created")
    file_size: int = Field(default=0, description="File size in bytes")
    status: str = Field(default="success", description="Processing status")
    embedding_count: int = Field(default=0, description="Number of embeddings created")

    class Settings:
        name = "documents"
        indexes = ["uploaded_at", "filename"]

    def __repr__(self) -> str:
        return f"<Document {self.id}: {self.filename}>"
