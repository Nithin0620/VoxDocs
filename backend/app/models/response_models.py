"""
Pydantic models for response formatting.
Ensures consistent API responses and automatic documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool
    filename: str
    message: str
    chunks_created: int
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "filename": "document.pdf",
                "message": "Document processed successfully",
                "chunks_created": 15,
                "timestamp": "2026-04-25T10:30:00"
            }
        }


class AnswerResponse(BaseModel):
    """Response model for document queries."""
    answer: str
    sources: List[str] = Field(default=[], description="Relevant document chunks used for answer")
    audio_url: Optional[str] = Field(default=None, description="URL to audio response if requested")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the answer")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "According to the document, the main topic is...",
                "sources": ["Section 1.1, Page 2"],
                "audio_url": None,
                "confidence": 0.92
            }
        }


class TranscriptionResponse(BaseModel):
    """Response model for speech-to-text conversion."""
    text: str
    language: str = "english"
    duration: float = Field(..., ge=0, description="Audio duration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "What is the main topic of this document?",
                "language": "english",
                "duration": 2.5
            }
        }


class SpeechResponse(BaseModel):
    """Response model for text-to-speech conversion."""
    audio_url: str
    text: str
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "/api/v1/audio/12345.mp3",
                "text": "Here is the answer to your question...",
                "duration": 5.2
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Question cannot be empty",
                "status_code": 400
            }
        }
