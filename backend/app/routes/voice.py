"""
Voice processing routes.
Handles speech-to-text and text-to-speech conversions.
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from app.models.request_models import TextToSpeechRequest
from app.models.response_models import TranscriptionResponse, SpeechResponse
from app.services.voice_service import SpeechToTextService, TextToSpeechService
from app import config
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


def get_stt_service() -> SpeechToTextService:
    """Dependency injection for speech-to-text service."""
    return SpeechToTextService(
        openai_api_key=config.OPENAI_API_KEY,
        model=config.WHISPER_MODEL
    )


def get_tts_service() -> TextToSpeechService:
    """Dependency injection for text-to-speech service."""
    return TextToSpeechService(
        api_key=config.ELEVENLABS_API_KEY,
        voice_id=config.ELEVENLABS_VOICE_ID
    )


@router.post("/speech-to-text", response_model=TranscriptionResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    stt_service: SpeechToTextService = Depends(get_stt_service)
) -> TranscriptionResponse:
    """
    Convert speech (audio) to text using Whisper.
    
    - **file**: Audio file to transcribe (required)
    
    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    
    Returns:
    - **text**: Transcribed text
    - **language**: Detected language
    - **duration**: Audio duration in seconds
    
    Raises:
    - 400: Invalid file type
    - 413: File too large
    - 500: Processing error
    """
    try:
        # Validate file type
        valid_types = {"audio/mpeg", "audio/wav", "audio/webm", "audio/mp4"}
        if file.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio file type. Supported: {valid_types}"
            )

        # Read file
        content = await file.read()

        # Validate file size (Whisper API: max 25MB)
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Audio file too large. Maximum size: 25MB"
            )

        # Save temporarily
        file_path = config.UPLOADS_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        # Transcribe
        logger.info(f"Transcribing audio: {file.filename}")
        text, language, duration = await stt_service.transcribe_audio(file_path)

        # Clean up temp file
        file_path.unlink()

        return TranscriptionResponse(
            text=text,
            language=language,
            duration=duration
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing audio: {str(e)}"
        )


@router.post("/text-to-speech", response_model=SpeechResponse)
async def text_to_speech(
    request: TextToSpeechRequest,
    tts_service: TextToSpeechService = Depends(get_tts_service)
) -> SpeechResponse:
    """
    Convert text to speech using ElevenLabs API.
    
    Request body:
    - **text**: Text to convert to speech (required)
    
    Returns:
    - **audio_url**: URL/path to the generated audio file
    - **text**: The input text
    - **duration**: Duration of generated audio in seconds
    
    Raises:
    - 400: Invalid text
    - 500: Processing error
    """
    try:
        # Validate text
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )

        if len(request.text) > 2000:
            raise HTTPException(
                status_code=400,
                detail="Text too long. Maximum 2000 characters"
            )

        # Generate speech
        logger.info(f"Generating speech for text: {len(request.text)} characters")
        output_path = config.UPLOADS_DIR / f"speech_{hash(request.text) % 10000}.mp3"
        audio_path, duration = await tts_service.synthesize_speech(request.text, output_path)

        return SpeechResponse(
            audio_url=f"/api/v1/audio/{audio_path.name}",
            text=request.text,
            duration=duration
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating speech: {str(e)}"
        )


@router.get("/audio/{filename}")
async def download_audio(filename: str):
    """
    Download generated audio file.
    
    - **filename**: Name of the audio file
    
    Returns:
    - Audio file with appropriate MIME type
    
    Raises:
    - 404: File not found
    """
    try:
        file_path = config.UPLOADS_DIR / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Audio file not found"
            )

        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error downloading audio"
        )
