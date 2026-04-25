"""
Voice processing service.
Handles speech-to-text and text-to-speech conversions.
"""
import logging
import io
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Converts audio files to text using OpenAI Whisper API.
    """

    def __init__(self, openai_api_key: str, model: str = "whisper-1"):
        """
        Initialize speech-to-text service.
        
        Args:
            openai_api_key: OpenAI API key
            model: Whisper model name
        """
        self.openai_api_key = openai_api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._client

    async def transcribe_audio(self, file_path: Path) -> Tuple[str, str, float]:
        """
        Transcribe audio file to text.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (text, language, duration)
        """
        try:
            logger.info(f"Transcribing audio: {file_path}")

            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language="en"  # English only for simplicity
                )

            text = response.text

            # Try to get duration (if available in metadata)
            duration = self._get_audio_duration(file_path)

            logger.info(f"Successfully transcribed audio: {len(text)} characters")
            return text, "english", duration

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    @staticmethod
    def _get_audio_duration(file_path: Path) -> float:
        """
        Get duration of audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            import librosa
            y, sr = librosa.load(file_path)
            duration = librosa.get_duration(y=y, sr=sr)
            return float(duration)
        except Exception:
            logger.warning("Could not determine audio duration")
            return 0.0

    @staticmethod
    def validate_audio_file(file_path: Path, max_size: int = 25 * 1024 * 1024) -> bool:
        """
        Validate audio file.
        Whisper API supports files up to 25MB.
        
        Args:
            file_path: Path to audio file
            max_size: Maximum file size in bytes
            
        Returns:
            True if valid, False otherwise
        """
        if not file_path.exists():
            return False

        file_size = file_path.stat().st_size
        if file_size > max_size:
            logger.warning(f"Audio file too large: {file_size} bytes")
            return False

        return True


class TextToSpeechService:
    """
    Converts text to speech using ElevenLabs API.
    Alternatively, can use other TTS services.
    """

    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Initialize text-to-speech service.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use (default: Rachel)
        """
        self.api_key = api_key
        self.voice_id = voice_id

    async def synthesize_speech(self, text: str, output_path: Path) -> Tuple[Path, float]:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            
        Returns:
            Tuple of (file_path, duration)
        """
        try:
            logger.info(f"Synthesizing speech: {len(text)} characters")

            import requests

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"ElevenLabs API error: {response.status_code}")
                raise ValueError(f"TTS API error: {response.text}")

            # Save audio file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            duration = self._get_audio_duration(output_path)

            logger.info(f"Successfully synthesized speech: {output_path}")
            return output_path, duration

        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            raise

    @staticmethod
    def _get_audio_duration(file_path: Path) -> float:
        """
        Get duration of audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            import librosa
            y, sr = librosa.load(file_path)
            duration = librosa.get_duration(y=y, sr=sr)
            return float(duration)
        except Exception:
            logger.warning("Could not determine audio duration")
            return 0.0

    @staticmethod
    def validate_text(text: str, max_length: int = 2000) -> bool:
        """
        Validate text for TTS.
        
        Args:
            text: Text to validate
            max_length: Maximum text length
            
        Returns:
            True if valid, False otherwise
        """
        if not text or len(text.strip()) == 0:
            return False

        if len(text) > max_length:
            logger.warning(f"Text too long: {len(text)} characters")
            return False

        return True
