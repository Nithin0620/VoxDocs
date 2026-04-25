# 📚 VoxDocs API Reference - Complete Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently no authentication required (add as needed for production)

---

## 📁 1. Document Management

### Upload PDF Document
```
POST /upload
Content-Type: multipart/form-data

Request:
- file: PDF file (required)

Response: 200 OK
{
  "success": true,
  "filename": "document.pdf",
  "message": "Document processed successfully",
  "chunks_created": 15,
  "timestamp": "2026-04-25T10:30:00"
}

Errors:
- 400: Invalid file type (only PDF supported)
- 413: File too large (>50MB)
- 500: Processing error
```

### Get Upload Status
```
GET /upload/status

Response: 200 OK
{
  "status": "ready",
  "statistics": {
    "rag": {
      "vector_store": {
        "total_vectors": 45,
        "embedding_dim": 1536,
        "metadata_count": 45
      },
      "embedding_model": "text-embedding-3-small",
      "llm_model": "gpt-3.5-turbo"
    },
    "documents": {
      "total_documents": 3,
      "total_size_bytes": 512000,
      "total_chunks": 45,
      "total_embeddings": 45,
      "average_file_size": 170666.67,
      "average_chunks_per_doc": 15
    }
  }
}

Errors:
- 500: Error retrieving status
```

---

## 📄 2. Document Information (NEW)

### Get All Documents
```
GET /documents

Response: 200 OK
[
  {
    "id": "507f1f77bcf86cd799439013",
    "filename": "guide.pdf",
    "file_path": "uploads/guide.pdf",
    "uploaded_at": "2026-04-25T10:00:00+00:00",
    "chunk_count": 25,
    "file_size": 102400,
    "embedding_count": 25
  },
  ...
]

Errors:
- 500: Database error
```

### Get Document Details
```
GET /documents/{doc_id}

Parameters:
- doc_id: Document MongoDB ObjectId

Response: 200 OK
{
  "id": "507f1f77bcf86cd799439013",
  "filename": "guide.pdf",
  "file_path": "uploads/guide.pdf",
  "uploaded_at": "2026-04-25T10:00:00+00:00",
  "chunk_count": 25,
  "file_size": 102400,
  "embedding_count": 25
}

Errors:
- 404: Document not found
- 500: Database error
```

### Get Document Statistics
```
GET /documents/stats/overview

Response: 200 OK
{
  "total_documents": 5,
  "total_size_bytes": 512000,
  "total_chunks": 125,
  "total_embeddings": 125,
  "average_file_size": 102400,
  "average_chunks_per_doc": 25
}

Errors:
- 500: Database error
```

---

## 💬 3. Question Answering

### Ask Question (Without Session)
```
POST /ask

Request:
{
  "question": "What is FastAPI?",
  "include_audio": false
}

Response: 200 OK
{
  "answer": "FastAPI is a modern, fast web framework...",
  "sources": ["guide.pdf"],
  "audio_url": null,
  "confidence": 0.92
}

Errors:
- 400: Empty question
- 500: Processing error
```

### Ask Question with Session (NEW)
```
POST /ask/session

Request:
{
  "session_id": "507f1f77bcf86cd799439011",
  "question": "How to get started?",
  "include_audio": false
}

Response: 200 OK
{
  "answer": "To get started, first install FastAPI...",
  "sources": ["guide.pdf"],
  "audio_url": null,
  "confidence": 0.88
}

Notes:
- Message is automatically saved to MongoDB
- Session title auto-generated from first message
- Maintains conversation history

Errors:
- 400: Missing session_id or empty question
- 404: Session not found
- 500: Processing error
```

---

## 🗂️ 4. Session Management (NEW)

### Create New Session
```
POST /session/new

Request:
{
  "title": "AI Discussion"  # optional, auto-generated if empty
}

Response: 201 Created
{
  "id": "507f1f77bcf86cd799439011",
  "title": "AI Discussion",
  "created_at": "2026-04-25T10:00:00+00:00",
  "updated_at": "2026-04-25T10:00:00+00:00"
}

Errors:
- 500: Database error
```

### Get All Sessions
```
GET /session

Response: 200 OK
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "AI Discussion",
    "created_at": "2026-04-25T10:00:00+00:00",
    "updated_at": "2026-04-25T10:00:00+00:00"
  },
  {
    "id": "507f1f77bcf86cd799439012",
    "title": "FastAPI Tutorial",
    "created_at": "2026-04-25T09:00:00+00:00",
    "updated_at": "2026-04-25T09:30:00+00:00"
  }
]

Notes:
- Sorted by creation time (newest first)

Errors:
- 500: Database error
```

### Get Session with Chat History
```
GET /session/{session_id}

Parameters:
- session_id: Session MongoDB ObjectId

Response: 200 OK
{
  "session": {
    "id": "507f1f77bcf86cd799439011",
    "title": "AI Discussion",
    "created_at": "2026-04-25T10:00:00+00:00",
    "updated_at": "2026-04-25T10:30:00+00:00"
  },
  "messages": [
    {
      "id": "507f1f77bcf86cd799439012",
      "question": "What is AI?",
      "answer": "AI stands for Artificial Intelligence...",
      "sources": ["ai_guide.pdf"],
      "confidence": 0.89,
      "created_at": "2026-04-25T10:00:00+00:00"
    },
    {
      "id": "507f1f77bcf86cd799439013",
      "question": "How to apply AI?",
      "answer": "AI can be applied in many ways...",
      "sources": ["ai_guide.pdf", "applications.pdf"],
      "confidence": 0.85,
      "created_at": "2026-04-25T10:15:00+00:00"
    }
  ]
}

Notes:
- Messages sorted by creation time (ascending)
- Perfect for displaying conversation UI

Errors:
- 404: Session not found
- 500: Database error
```

### Delete Session
```
DELETE /session/{session_id}

Parameters:
- session_id: Session MongoDB ObjectId

Response: 200 OK
{
  "success": true,
  "message": "Session 507f1f77bcf86cd799439011 and all messages deleted"
}

Notes:
- Deletes session and ALL associated messages

Errors:
- 404: Session not found
- 500: Database error
```

---

## 🎙️ 5. Speech-to-Text

### Convert Speech to Text
```
POST /voice/speech-to-text
Content-Type: multipart/form-data

Request:
- file: Audio file (MP3, WAV, WebM, M4A)

Response: 200 OK
{
  "text": "What is FastAPI?",
  "language": "english",
  "duration": 2.5
}

Supported Formats:
- MP3, WAV, WebM, M4A, MPEG, MPGA
- Max size: 25MB (Whisper API limit)

Errors:
- 400: Invalid audio file type
- 413: File too large (>25MB)
- 500: Transcription error
```

---

## 🔊 6. Text-to-Speech

### Convert Text to Speech
```
POST /voice/text-to-speech

Request:
{
  "text": "Here is the answer to your question..."
}

Response: 200 OK
{
  "audio_url": "/api/v1/voice/audio/answer_12345.mp3",
  "text": "Here is the answer to your question...",
  "duration": 5.2
}

Constraints:
- Text max length: 2000 characters
- Requires ElevenLabs API key

Errors:
- 400: Empty or too long text
- 500: TTS generation error
```

### Download Generated Audio
```
GET /voice/audio/{filename}

Parameters:
- filename: Audio filename from TTS response

Response: 200 OK
- Returns audio file (audio/mpeg)

Example:
GET /voice/audio/answer_12345.mp3

Returns:
- Binary audio data with audio/mpeg MIME type

Errors:
- 404: Audio file not found
- 500: Error downloading
```

---

## ❤️ 7. Health & Status

### Health Check
```
GET /health

Response: 200 OK
{
  "status": "healthy",
  "version": "1.0.0",
  "name": "VoxDocs API"
}

Always returns 200 if API is running
```

### API Info
```
GET /

Response: 200 OK
{
  "name": "VoxDocs API",
  "version": "1.0.0",
  "description": "AI-powered Voice Document Assistant",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 📊 Complete Workflow Example

### 1. Upload and Process Documents
```bash
# Upload PDF
curl -X POST -F "file=@guide.pdf" \
  http://localhost:8000/api/v1/upload

# Response: Document saved to vector store + MongoDB
```

### 2. Create Conversation Session
```bash
curl -X POST http://localhost:8000/api/v1/session/new \
  -H "Content-Type: application/json" \
  -d '{"title": "FastAPI Questions"}'

# Response: session_id = "507f1f77bcf86cd799439011"
```

### 3. Ask Multiple Questions
```bash
# Question 1
curl -X POST http://localhost:8000/api/v1/ask/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "507f1f77bcf86cd799439011",
    "question": "What is FastAPI?",
    "include_audio": false
  }'

# Question 2
curl -X POST http://localhost:8000/api/v1/ask/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "507f1f77bcf86cd799439011",
    "question": "How to create routes?",
    "include_audio": true
  }'

# Response includes audio_url for second question
```

### 4. Review Chat History
```bash
curl -X GET \
  http://localhost:8000/api/v1/session/507f1f77bcf86cd799439011

# Response: Session + all messages
```

### 5. Check Documents
```bash
curl -X GET http://localhost:8000/api/v1/documents

# Response: All uploaded documents + metadata
```

### 6. Cleanup
```bash
curl -X DELETE \
  http://localhost:8000/api/v1/session/507f1f77bcf86cd799439011

# Response: Session deleted
```

---

## 🔐 Response Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request (invalid input) |
| 404  | Not Found |
| 413  | Payload Too Large |
| 500  | Server Error |

---

## 📝 Common Request Patterns

### Python Requests Library
```python
import requests

# Upload document
files = {"file": open("guide.pdf", "rb")}
resp = requests.post("http://localhost:8000/api/v1/upload", files=files)

# Create session
resp = requests.post("http://localhost:8000/api/v1/session/new",
  json={"title": "Discussion"})
session_id = resp.json()["id"]

# Ask question
resp = requests.post("http://localhost:8000/api/v1/ask/session",
  json={
    "session_id": session_id,
    "question": "What is this?",
    "include_audio": False
  })
answer = resp.json()["answer"]
```

### Curl Examples
```bash
# Get all sessions
curl http://localhost:8000/api/v1/session

# Get session history
curl http://localhost:8000/api/v1/session/{session_id}

# Get documents
curl http://localhost:8000/api/v1/documents

# Get stats
curl http://localhost:8000/api/v1/documents/stats/overview
```

---

## ⚡ Performance Tips

1. **Batch Questions**: Ask multiple questions in one session
2. **Cache Sessions**: Keep session ID for conversation continuity
3. **Limit History**: Get only recent messages if needed
4. **Compress Responses**: Gzip enabled automatically
5. **Async Operations**: All endpoints use async/await

---

## 🎓 Key Features

✅ **RAG Pipeline**: Intelligent document retrieval
✅ **Session Tracking**: Persistent conversation history
✅ **Multi-Document**: Query across multiple PDFs
✅ **Audio Support**: Speech-to-text & text-to-speech
✅ **Confidence Scores**: Assess answer quality
✅ **Document Tracking**: Monitor uploaded files
✅ **Async Operations**: Non-blocking requests
✅ **MongoDB Integration**: Cloud database storage

---

**All endpoints are documented in the interactive API at `/docs`** 📖
