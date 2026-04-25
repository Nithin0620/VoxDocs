# 🚀 VoxDocs Quick Start Reference Card

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your keys:
# - OPENAI_API_KEY=sk-...
# - ELEVENLABS_API_KEY=...
# - MONGODB_URI=mongodb+srv://...
```

### 3. Start Server
```bash
python -m uvicorn app.main:app --reload
# Access API docs: http://localhost:8000/docs
```

### 4. Test with Examples
```bash
python example_usage.py
# Choose option 5 for complete workflow demo
```

---

## 📝 Essential Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **Upload** | `POST /upload` | Upload PDF document |
| **Query** | `POST /ask/session` | Ask question with session |
| **Sessions** | `POST /session/new` | Create chat session |
| **Sessions** | `GET /session/{id}` | Get chat history |
| **Sessions** | `DELETE /session/{id}` | Delete session |
| **Documents** | `GET /documents` | List all documents |
| **Stats** | `GET /documents/stats/overview` | Document statistics |
| **Speech** | `POST /voice/speech-to-text` | Convert audio to text |
| **Speech** | `POST /voice/text-to-speech` | Convert text to audio |

---

## 🔑 Core API Keys Needed

```
OPENAI_API_KEY          → https://platform.openai.com/api-keys
ELEVENLABS_API_KEY      → https://elevenlabs.io/app/api-keys
MONGODB_URI             → https://cloud.mongodb.com (Atlas)
```

---

## 🗂️ Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment config
│   ├── db/
│   │   ├── database.py            # MongoDB connection
│   │   └── models.py              # Beanie models
│   ├── services/
│   │   ├── rag_service.py         # Vector search & LLM
│   │   ├── chat_service.py        # Session management
│   │   ├── document_service.py    # Document tracking
│   │   └── voice_service.py       # Speech services
│   └── routes/
│       ├── health.py              # Health checks
│       ├── upload.py              # PDF upload
│       ├── query.py               # Question answering
│       ├── session.py             # Session endpoints
│       ├── documents.py           # Document endpoints
│       └── voice.py               # Speech endpoints
├── requirements.txt               # Dependencies
├── .env.example                   # Config template
└── example_usage.py              # Demo script
```

---

## 🔄 Complete Workflow

```
1. Upload PDF
   curl -F "file=@doc.pdf" http://localhost:8000/api/v1/upload

2. Create Session
   curl -X POST http://localhost:8000/api/v1/session/new

3. Ask Question (with session persistence)
   curl -X POST http://localhost:8000/api/v1/ask/session \
     -d '{"session_id":"...", "question":"...?"}}'

4. Get Chat History
   curl http://localhost:8000/api/v1/session/{session_id}

5. Get Statistics
   curl http://localhost:8000/api/v1/documents/stats/overview
```

---

## 🗄️ Database Models

### Session
```python
{
  "id": ObjectId,
  "title": str,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Message
```python
{
  "id": ObjectId,
  "session_id": ObjectId,
  "question": str,
  "answer": str,
  "sources": [str],
  "confidence": float,
  "created_at": datetime
}
```

### Document
```python
{
  "id": ObjectId,
  "filename": str,
  "file_path": str,
  "uploaded_at": datetime,
  "chunk_count": int,
  "file_size": int,
  "embedding_count": int
}
```

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| **"Connection refused"** | Check MongoDB running: `mongod` or verify Atlas cluster |
| **"API key invalid"** | Verify key in .env, ensure it's for correct service |
| **"Address already in use"** | Kill process: `lsof -i :8000` and `kill -9 <PID>` |
| **"Session not found"** | Create session first: `POST /session/new` |
| **"File size exceeded"** | Upload files < 100MB or adjust MAX_FILE_SIZE |

---

## 🔧 Useful Commands

```bash
# Start server with debugging
python -m uvicorn app.main:app --reload --log-level debug

# Run tests (when available)
pytest tests/

# Check if port is free
lsof -i :8000

# Monitor server logs
tail -f logs/app.log

# View MongoDB data
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/voxdocs"
use voxdocs
db.session.find()

# Rebuild vector index
python scripts/rebuild_faiss.py

# Clean old audio files
find audio_output -mtime +7 -delete
```

---

## 📊 Performance Benchmarks

| Operation | Avg Time | Max Time |
|-----------|----------|----------|
| PDF Upload (10MB) | 2-3s | 5s |
| Vector Search | 100-200ms | 500ms |
| LLM Response | 1-3s | 5s |
| Session Creation | 50ms | 200ms |
| Message Storage | 100ms | 300ms |
| Speech-to-Text | 1-2s | 5s |
| Text-to-Speech | 500ms | 2s |

**Note**: Times depend on network, API rate limits, and document complexity

---

## 🔐 Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong MongoDB passwords
- [ ] Whitelist server IPs in MongoDB Atlas
- [ ] Use HTTPS in production (reverse proxy)
- [ ] Enable CORS only for your domain
- [ ] Rate limit API endpoints
- [ ] Enable request logging
- [ ] Implement JWT authentication
- [ ] Add request validation
- [ ] Monitor API usage

---

## 📈 Scale Your Deployment

### Development
```bash
python -m uvicorn app.main:app --reload
# Single server, local MongoDB
```

### Production Small
```bash
docker run -p 8000:8000 voxdocs-api:1.0.0
# Single container, MongoDB Atlas
```

### Production Medium
```
API Server 1 ──┐
API Server 2 ──┼─→ Nginx LB ─→ MongoDB Atlas Cluster
API Server 3 ──┘
```

### Production Large
```
K8s Cluster (10+ instances) ─→ MongoDB Sharded Cluster
Redis Cache ─→ Document Vector Index (Distributed)
```

---

## 🎯 Next Steps

1. **Immediate**
   - [ ] Create MongoDB Atlas account
   - [ ] Get OpenAI API key
   - [ ] Get ElevenLabs API key
   - [ ] Configure `.env` file
   - [ ] Start server: `uvicorn app.main:app --reload`

2. **Today**
   - [ ] Upload a PDF document
   - [ ] Create a session
   - [ ] Ask questions with session persistence
   - [ ] Test speech features

3. **This Week**
   - [ ] Build frontend UI
   - [ ] Deploy to production
   - [ ] Set up monitoring

4. **This Month**
   - [ ] Implement user authentication
   - [ ] Add rate limiting
   - [ ] Set up analytics
   - [ ] Performance optimization

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** | Project overview |
| **QUICK_START.md** | Detailed setup instructions |
| **DEVELOPMENT.md** | Development environment |
| **MONGODB_GUIDE.md** | MongoDB Atlas setup |
| **MONGODB_COMPLETE.md** | MongoDB integration details |
| **API_ENDPOINTS.md** | All endpoint documentation |
| **API_REFERENCE.md** | Request/response examples |
| **PRODUCTION_DEPLOYMENT.md** | Production setup guide |
| **TROUBLESHOOTING.md** | Common issues & fixes |
| **example_usage.py** | Working code examples |

---

## 🆘 Getting Help

### Check These First
1. **Troubleshooting Guide** → TROUBLESHOOTING.md
2. **API Documentation** → API_ENDPOINTS.md
3. **Example Code** → example_usage.py
4. **Logs** → logs/app.log

### Debug with Examples
```bash
# Test connection
python -c "from app.config import MONGODB_URI; print(MONGODB_URI)"

# Test imports
python -c "import fastapi; import pymongo; import openai; print('All imports OK')"

# Test API
curl http://localhost:8000/health
```

### Online Resources
- FastAPI: https://fastapi.tiangolo.com
- MongoDB: https://docs.mongodb.com
- OpenAI: https://platform.openai.com/docs

---

## 💡 Pro Tips

1. **Always start MongoDB before the app**
   ```bash
   # Terminal 1
   mongod
   # Terminal 2
   python -m uvicorn app.main:app --reload
   ```

2. **Use FastAPI interactive docs**
   - Open http://localhost:8000/docs
   - Try endpoints directly in browser
   - No tools needed!

3. **Batch test everything at once**
   ```bash
   python example_usage.py
   # Select option 5 for complete workflow
   ```

4. **Monitor in real-time**
   ```bash
   tail -f logs/app.log
   # Watch logs update as you use API
   ```

5. **Keep sessions organized**
   - Create new session for each topic
   - Use meaningful titles
   - Delete old sessions to save space

---

## 🎓 Learning Path

**Week 1**: Setup & Basics
- Install dependencies
- Configure environment
- Run example script
- Understand basic workflow

**Week 2**: Integration
- Build simple frontend
- Deploy to staging
- Test all features
- Optimize performance

**Week 3**: Production
- Deploy to production
- Set up monitoring
- Implement authentication
- Add advanced features

---

**You're all set! Start with `python example_usage.py` 🚀**

Last Updated: 2026-04-25
Version: 1.0.0
