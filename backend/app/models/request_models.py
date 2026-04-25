"""
Pydantic models for request validation.
Ensures type safety and automatic API documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class QuestionRequest(BaseModel):
    """Request model for asking questions about documents."""
    question: str = Field(..., min_length=1, max_length=500, description="Question about the document")
    include_audio: Optional[bool] = Field(default=False, description="Whether to return audio response")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of this document?",
                "include_audio": False
            }
        }


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=2000, description="Text to convert to speech")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test message."
            }
        }


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents."""
    filename: str
    size: int
    chunk_count: int
    upload_timestamp: str
