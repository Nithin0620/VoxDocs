"""
Configuration module for VoxDocs backend.
Centralized environment variable and application settings.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === File Paths ===
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
VECTORS_DIR = BASE_DIR / "vectors"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
VECTORS_DIR.mkdir(exist_ok=True)

# === API Configuration ===
API_V1_PREFIX = "/api/v1"
APP_NAME = "VoxDocs API"
APP_VERSION = "1.0.0"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# === Authentication Configuration ===
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "voxdocs_access_token")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")
    if origin.strip()
]

# === Google OAuth Configuration ===
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/api/v1/auth/google/callback"
)
GOOGLE_OAUTH_STATE_COOKIE = os.getenv("GOOGLE_OAUTH_STATE_COOKIE", "voxdocs_google_state")
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

if GOOGLE_REDIRECT_URI.startswith("http://") and os.getenv("OAUTHLIB_INSECURE_TRANSPORT") != "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# === OpenAI Configuration ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# === FAISS Configuration ===
FAISS_INDEX_PATH = VECTORS_DIR / "documents.index"
FAISS_METADATA_PATH = VECTORS_DIR / "metadata.json"

# === MongoDB Atlas Configuration ===
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://user:password@cluster.mongodb.net/voxdocs"
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "voxdocs")

# === Speech Configuration ===
# Whisper is part of OpenAI API
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")

# ElevenLabs for Text-to-Speech
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice

# === Document Processing ===
MAX_CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# === RAG Configuration ===
TOP_K_RESULTS = 3  # Number of relevant documents to retrieve
CONFIDENCE_THRESHOLD = 0.7

# === Validation ===
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. OpenAI features will not work.")

if not ELEVENLABS_API_KEY:
    logger.warning("ELEVENLABS_API_KEY not set. Text-to-speech features will not work.")
