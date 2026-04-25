# VoxDocs Backend - AI-Powered Voice Document Assistant

A clean, modular FastAPI backend for processing PDF documents with RAG (Retrieval-Augmented Generation), speech-to-text, and text-to-speech capabilities.

## 🎯 Features

- **📄 PDF Processing**: Upload and automatically process PDF documents
- **🧠 RAG Pipeline**: Vector embeddings with FAISS for intelligent document retrieval
- **💬 Question Answering**: Ask questions about uploaded documents with LLM-powered answers
- **🎙️ Speech-to-Text**: Convert audio to text using OpenAI Whisper
- **🔊 Text-to-Speech**: Convert responses to audio using ElevenLabs
- **🏗️ Clean Architecture**: Modular design with dependency injection
- **🔒 Type-Safe**: Full Pydantic validation and FastAPI documentation

## 📋 Tech Stack

- **Framework**: FastAPI
- **Python**: 3.10+
- **LLM**: OpenAI API
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: FAISS (local)
- **Speech-to-Text**: OpenAI Whisper
- **Text-to-Speech**: ElevenLabs
- **Document Processing**: pdfplumber, PyPDF2

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration & environment variables
│   ├── models/
│   │   ├── request_models.py   # Request validation schemas
│   │   └── response_models.py  # Response formatting schemas
│   ├── routes/
│   │   ├── upload.py           # Document upload endpoints
│   │   ├── query.py            # Question answering endpoints
│   │   └── voice.py            # Speech-to-text & text-to-speech
│   ├── services/
│   │   ├── rag_service.py      # RAG orchestration
│   │   └── voice_service.py    # Voice processing
│   └── utils/
│       ├── file_loader.py      # PDF extraction & chunking
│       └── embeddings.py       # Embedding generation & FAISS
├── uploads/                    # Temporary uploads directory
├── vectors/                    # FAISS index storage
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenAI API key
- ElevenLabs API key (optional, for TTS)

### 2. Installation

```bash
# Clone the repository
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-...
# ELEVENLABS_API_KEY=...
```

### 4. Run the Application

```bash
# Using uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py script
python app/main.py
```

The API will be available at `http://localhost:8000`

### 5. Access API Documentation

- **Interactive Docs** (Swagger UI): http://localhost:8000/docs
- **Alternative Docs** (ReDoc): http://localhost:8000/redoc

## 📚 API Endpoints

### Document Upload
```
POST /api/v1/upload
```
Upload a PDF document and process it into embeddings.

**Request**: Multipart file upload
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/v1/upload
```

**Response**:
```json
{
  "success": true,
  "filename": "document.pdf",
  "message": "Document processed successfully",
  "chunks_created": 15,
  "timestamp": "2026-04-25T10:30:00"
}
```

### Ask Question
```
POST /api/v1/ask
```
Ask a question about the uploaded documents.

**Request**:
```json
{
  "question": "What is the main topic of this document?",
  "include_audio": false
}
```

**Response**:
```json
{
  "answer": "The document primarily discusses...",
  "sources": ["document.pdf"],
  "audio_url": null,
  "confidence": 0.92
}
```

### Speech-to-Text
```
POST /api/v1/voice/speech-to-text
```
Convert audio file to text.

**Request**: Multipart audio file upload
```bash
curl -X POST -F "file=@audio.mp3" http://localhost:8000/api/v1/voice/speech-to-text
```

**Response**:
```json
{
  "text": "What is the main topic of this document?",
  "language": "english",
  "duration": 2.5
}
```

### Text-to-Speech
```
POST /api/v1/voice/text-to-speech
```
Convert text to audio.

**Request**:
```json
{
  "text": "Here is the answer to your question..."
}
```

**Response**:
```json
{
  "audio_url": "/api/v1/voice/audio/12345.mp3",
  "text": "Here is the answer to your question...",
  "duration": 5.2
}
```

### Download Audio
```
GET /api/v1/voice/audio/{filename}
```
Download previously generated audio file.

### Health Check
```
GET /health
```
Check API server status.

## 🔧 Configuration

Edit `app/config.py` or `.env` file to customize:

- **Chunk Size**: How documents are split (default: 1000 chars)
- **Overlap**: Context preservation between chunks (default: 100 chars)
- **Top K**: Retrieved documents per query (default: 3)
- **API Keys**: OpenAI and ElevenLabs credentials
- **Storage**: Directories for uploads and vector indices

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_rag_service.py -v
```

## 🏗️ Architecture Highlights

### Dependency Injection
Services are injected into routes for testability:

```python
def get_rag_service() -> RAGService:
    return RAGService(...)

@router.post("/")
async def query(service: RAGService = Depends(get_rag_service)):
    ...
```

### Service Layer
Business logic isolated from HTTP layer:
- `RAGService`: Document processing and LLM queries
- `SpeechToTextService`: Audio transcription
- `TextToSpeechService`: Speech synthesis

### Utilities
Reusable, single-responsibility functions:
- `PDFLoader`: PDF extraction
- `TextChunker`: Text splitting
- `EmbeddingGenerator`: Vector creation
- `FAISSVectorStore`: Vector search

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| FastAPI | API framework |
| pdfplumber | PDF text extraction |
| openai | LLM & embeddings |
| faiss-cpu | Vector similarity search |
| librosa | Audio processing |
| requests | HTTP client |

## 🔐 Security Considerations

1. **API Keys**: Use environment variables, never commit `.env`
2. **File Uploads**: Validate file types and sizes
3. **CORS**: Configure for your frontend origin
4. **Rate Limiting**: Add in production
5. **Authentication**: Implement JWT or API keys for protected endpoints

## 🐛 Troubleshooting

### "OPENAI_API_KEY not set"
```bash
# Make sure .env file exists and has your key
export OPENAI_API_KEY=your_key_here
```

### "pdfplumber not installed"
```bash
pip install pdfplumber
```

### "FAISS index not found"
The index is created automatically on first document upload.

### "No relevant documents found"
Upload documents first using the `/api/v1/upload` endpoint.

## 📊 Performance Tips

1. **Batch Processing**: Process multiple files at once
2. **Caching**: Cache embeddings for repeated queries
3. **Index Optimization**: Periodically rebuild FAISS index
4. **Compression**: Enable gzip compression (already configured)

## 🚢 Deployment

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Environment Variables (Production)
```bash
export OPENAI_API_KEY=sk-...
export ELEVENLABS_API_KEY=...
export APP_ENV=production
```

## 📝 Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

1. Create a feature branch
2. Make changes following the existing code style
3. Add tests for new functionality
4. Run linters and tests
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs for error messages
4. Open an issue on the repository

---

**Built with ❤️ for AI-powered document processing**
