"""
Document management routes.
Tracks and retrieves information about uploaded documents.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.services.document_service import DocumentService
from typing import List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


# === Pydantic models ===

class DocumentResponse(BaseModel):
    """Document response model"""
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Storage path")
    uploaded_at: str = Field(..., description="Upload timestamp")
    chunk_count: int = Field(..., description="Number of chunks")
    file_size: int = Field(..., description="File size in bytes")
    embedding_count: int = Field(..., description="Number of embeddings")


class DocumentStatistics(BaseModel):
    """Document statistics"""
    total_documents: int
    total_size_bytes: int
    total_chunks: int
    total_embeddings: int
    average_file_size: float
    average_chunks_per_doc: float


# === Dependency injection ===

def get_document_service() -> DocumentService:
    """Dependency injection for document service."""
    return DocumentService()


# === Routes ===

@router.get("", response_model=List[DocumentResponse])
async def get_all_documents(
    document_service: DocumentService = Depends(get_document_service)
) -> List[DocumentResponse]:
    """
    Retrieve all uploaded documents.
    Sorted by upload time (newest first).
    
    Returns:
    - List of documents with metadata
    
    Raises:
    - 500: Database error
    """
    try:
        logger.info("Retrieving all documents")
        documents = await document_service.get_all_documents()
        
        return [
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_path=doc.file_path,
                uploaded_at=doc.uploaded_at.isoformat(),
                chunk_count=doc.chunk_count,
                file_size=doc.file_size,
                embedding_count=doc.embedding_count
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving documents"
        )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """
    Get details of a specific document.
    
    Path parameters:
    - **doc_id**: Document ID
    
    Returns:
    - Document metadata
    
    Raises:
    - 404: Document not found
    - 500: Database error
    """
    try:
        logger.info(f"Retrieving document: {doc_id}")
        doc = await document_service.get_document(doc_id)
        
        return DocumentResponse(
            id=str(doc.id),
            filename=doc.filename,
            file_path=doc.file_path,
            uploaded_at=doc.uploaded_at.isoformat(),
            chunk_count=doc.chunk_count,
            file_size=doc.file_size,
            embedding_count=doc.embedding_count
        )
        
    except ValueError as e:
        logger.warning(f"Document not found: {doc_id}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving document"
        )


@router.get("/stats/overview", response_model=DocumentStatistics)
async def get_document_statistics(
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentStatistics:
    """
    Get overall statistics about uploaded documents.
    
    Returns:
    - Statistics including total documents, size, chunks, etc.
    
    Raises:
    - 500: Database error
    """
    try:
        logger.info("Retrieving document statistics")
        stats = await document_service.get_document_stats()
        
        return DocumentStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving statistics"
        )
