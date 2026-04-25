"""
Document upload routes.
Handles PDF file uploads and processing.
"""
import logging
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models.response_models import UploadResponse
from app.services.rag_service import RAGService
from app import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


def get_rag_service() -> RAGService:
    """
    Dependency injection for RAG service.
    Can be overridden in tests.
    """
    return RAGService(
        openai_api_key=config.OPENAI_API_KEY,
        faiss_index_path=config.FAISS_INDEX_PATH,
        faiss_metadata_path=config.FAISS_METADATA_PATH,
        embedding_model=config.OPENAI_EMBEDDING_MODEL,
        llm_model=config.OPENAI_MODEL,
        chunk_size=config.MAX_CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        top_k=config.TOP_K_RESULTS
    )


@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
) -> UploadResponse:
    """
    Upload and process a PDF document.
    
    - **file**: PDF file to upload (required)
    
    Returns:
    - **success**: Whether processing was successful
    - **filename**: Name of the uploaded file
    - **message**: Processing status message
    - **chunks_created**: Number of text chunks created
    - **timestamp**: When the document was processed
    
    Raises:
    - 400: Invalid file type or empty file
    - 413: File too large (>50MB)
    - 500: Processing error
    """
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )

        # Read file
        content = await file.read()

        # Validate file size
        if len(content) > config.MAX_UPLOAD_SIZE:
            logger.warning(f"File too large: {len(content)} bytes")
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {config.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Save file temporarily
        file_path = config.UPLOADS_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Saved uploaded file: {file_path}")

        # Process document
        result = await rag_service.process_document(file_path, file.filename)

        return UploadResponse(
            success=result["success"],
            filename=result["filename"],
            message="Document processed successfully",
            chunks_created=result["chunks_created"],
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/status")
async def upload_status(rag_service: RAGService = Depends(get_rag_service)) -> dict:
    """
    Get status of uploaded documents and vector store.
    
    Returns:
    - **vector_store**: Statistics about the vector store
    - **embedding_model**: Model used for embeddings
    - **llm_model**: Model used for LLM responses
    """
    try:
        stats = rag_service.get_statistics()
        return {
            "status": "ready",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving status"
        )
