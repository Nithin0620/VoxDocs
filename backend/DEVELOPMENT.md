# VoxDocs Backend Development Guide

## 🎯 Quick Reference

### Start the Server
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Testing

#### 1. Upload Document
```bash
curl -X POST -F "file=@sample.pdf" http://localhost:8000/api/v1/upload
```

#### 2. Ask Question
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "include_audio": false
  }'
```

#### 3. Speech-to-Text
```bash
curl -X POST -F "file=@audio.mp3" http://localhost:8000/api/v1/voice/speech-to-text
```

#### 4. Text-to-Speech
```bash
curl -X POST http://localhost:8000/api/v1/voice/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

## 📚 Code Organization

### Models (`app/models/`)
- **request_models.py**: API request validation (Pydantic)
- **response_models.py**: API response schemas

**Why separate?** Keeps validation logic separate from HTTP response formatting.

### Routes (`app/routes/`)
- **upload.py**: Document upload & processing
- **query.py**: Question answering
- **voice.py**: Speech-to-text & text-to-speech

**Responsibility**: HTTP handling, validation, dependency injection

### Services (`app/services/`)
- **rag_service.py**: Core RAG orchestration
- **voice_service.py**: Audio processing

**Responsibility**: Business logic, no HTTP awareness

### Utils (`app/utils/`)
- **file_loader.py**: PDF extraction & chunking
- **embeddings.py**: Embeddings & FAISS vector store

**Responsibility**: Reusable functions, single purpose each

## 🔄 Data Flow

```
PDF Upload
    ↓
[routes/upload.py] → validate file
    ↓
[rag_service.process_document()]
    ↓
[file_loader.extract_text_from_pdf()] → text
    ↓
[file_loader.chunk_text()] → chunks
    ↓
[embeddings.EmbeddingGenerator.generate_embeddings_batch()] → vectors
    ↓
[embeddings.FAISSVectorStore.add_embeddings()] → saved
```

```
Query Processing
    ↓
[routes/query.py] → validate question
    ↓
[rag_service.query()]
    ↓
[embeddings.EmbeddingGenerator.generate_embedding()] → query vector
    ↓
[embeddings.FAISSVectorStore.search()] → similar docs
    ↓
[rag_service._generate_answer_with_llm()] → answer
    ↓
(Optional) [voice_service.TextToSpeechService.synthesize_speech()] → audio
```

## 🧪 Testing

### Create Test File
```python
# test_upload.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_pdf():
    with open("sample.pdf", "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("sample.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### Run Tests
```bash
pytest
pytest -v  # Verbose
pytest --cov=app  # With coverage
```

## 🔧 Common Customizations

### Change Chunk Size
Edit `app/config.py`:
```python
MAX_CHUNK_SIZE = 500  # Smaller = more granular
CHUNK_OVERLAP = 50
```

### Change LLM Model
```python
OPENAI_MODEL = "gpt-4"  # Requires API access
```

### Add Custom TTS Service
Replace ElevenLabs in `voice_service.py`:
```python
async def synthesize_speech(self, text: str, output_path: Path):
    # Your custom implementation
    pass
```

### Add Authentication
In `routes/upload.py`:
```python
@router.post("/")
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user)  # Add this
):
    ...
```

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
tail -f logs/app.log

# Search logs
grep "ERROR" logs/app.log
```

### Check Vector Store Stats
```bash
curl http://localhost:8000/api/v1/upload/status
```

## 🚀 Deployment Checklist

- [ ] Update `OPENAI_API_KEY` in production environment
- [ ] Update `ELEVENLABS_API_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure CORS for your frontend domain
- [ ] Set up SSL/TLS certificates
- [ ] Enable rate limiting
- [ ] Add request logging
- [ ] Configure persistent vector storage
- [ ] Set up database for metadata
- [ ] Monitor API usage and costs

## 🐛 Debugging Tips

### Enable Debug Logging
In `app/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Requests
Use FastAPI docs at http://localhost:8000/docs

### Check FAISS Index
```python
from app.config import FAISS_INDEX_PATH
from app.utils.embeddings import FAISSVectorStore

store = FAISSVectorStore(FAISS_INDEX_PATH, "metadata.json")
print(store.get_stats())
```

### Test LLM Connection
```python
from app.config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "test"}]
)
print(response.choices[0].message.content)
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [FAISS Documentation](https://faiss.ai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## ❓ Frequently Asked Issues

### "No module named 'app'"
```bash
# Make sure you're in the backend directory
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### "FAISS IndexFlatL2 error"
```bash
# Reinstall FAISS
pip install --force-reinstall faiss-cpu
```

### "OpenAI API rate limit"
Implement exponential backoff in `rag_service.py`

### PDF text extraction returns empty
Check if PDF is text-based (not scanned image PDF - requires OCR)

---

**Happy coding! 🎉**
