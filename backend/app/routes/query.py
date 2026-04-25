"""
Document query routes.
Handles question answering based on uploaded documents.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import QuestionRequest
from app.models.response_models import AnswerResponse
from app.services.rag_service import RAGService
from app.services.voice_service import TextToSpeechService
from app import config
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ask", tags=["query"])


def get_rag_service() -> RAGService:
    """Dependency injection for RAG service."""
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


def get_tts_service() -> TextToSpeechService:
    """Dependency injection for TTS service."""
    return TextToSpeechService(
        api_key=config.ELEVENLABS_API_KEY,
        voice_id=config.ELEVENLABS_VOICE_ID
    )


@router.post("/", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),
    tts_service: TextToSpeechService = Depends(get_tts_service)
) -> AnswerResponse:
    """
    Ask a question about the uploaded documents and get an answer.
    
    Request body:
    - **question**: The question to ask (required)
    - **include_audio**: Whether to return an audio response (optional)
    
    Returns:
    - **answer**: The generated answer based on documents
    - **sources**: List of document sources used
    - **audio_url**: URL to audio response (if requested)
    - **confidence**: Confidence score of the answer (0-1)
    
    Raises:
    - 400: Invalid request
    - 404: No documents uploaded yet
    - 500: Processing error
    """
    try:
        # Validate request
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # Query documents
        logger.info(f"Processing question: {request.question}")
        answer, sources, confidence = await rag_service.query(request.question)

        # Check if documents were found
        if not sources:
            logger.warning("No relevant documents found")
            return AnswerResponse(
                answer="No relevant documents found. Please upload documents first.",
                sources=[],
                audio_url=None,
                confidence=0.0
            )

        audio_url = None

        # Generate audio response if requested
        if request.include_audio:
            try:
                logger.info("Generating audio response")
                audio_path = config.UPLOADS_DIR / f"answer_{hash(answer) % 10000}.mp3"
                audio_path, duration = await tts_service.synthesize_speech(answer, audio_path)
                audio_url = f"/api/v1/audio/{audio_path.name}"
                logger.info(f"Generated audio response: {audio_url}")
            except Exception as e:
                logger.error(f"Error generating audio: {str(e)}")
                # Continue without audio if TTS fails
                audio_url = None

        return AnswerResponse(
            answer=answer,
            sources=sources,
            audio_url=audio_url,
            confidence=min(confidence, 1.0)  # Ensure confidence is between 0-1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )
