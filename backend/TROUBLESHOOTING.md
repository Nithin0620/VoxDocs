# 🔧 Troubleshooting Guide

## Common Issues & Solutions

---

## 🔴 MongoDB Connection Issues

### Error: "Connection refused"
```
Error: connect ECONNREFUSED 127.0.0.1:27017
```

**Solutions:**
1. **Check if MongoDB is running**
   ```bash
   # Local MongoDB
   sudo systemctl status mongod
   sudo systemctl start mongod
   
   # Or check if mongod process exists
   pgrep mongod
   ```

2. **For MongoDB Atlas (Cloud):**
   - Verify MONGODB_URI in `.env` is correct
   - Check MongoDB Atlas → Network Access → IP Whitelist
   - Add your server IP to whitelist
   - Verify username and password in connection string
   ```bash
   # Test connection string
   mongosh "mongodb+srv://username:password@cluster.mongodb.net/admin"
   ```

3. **Check firewall**
   ```bash
   # Linux
   sudo ufw allow 27017
   
   # Or check if port is accessible
   nc -zv localhost 27017
   ```

---

### Error: "Authentication failed"
```
MongoAuthenticationError: auth failed
```

**Solutions:**
1. **Verify credentials in .env**
   ```bash
   # Format: mongodb+srv://username:password@cluster.mongodb.net/dbname
   # Check for special characters - must be URL-encoded
   # Example: password "p@ss123" → "p%40ss123"
   ```

2. **Reset MongoDB user password**
   ```bash
   # In MongoDB Shell
   use admin
   db.changeUserPassword("username", "newpassword")
   ```

3. **Check database name**
   ```bash
   # In .env, set DATABASE_NAME to correct name
   DATABASE_NAME=voxdocs  # Not admin or other
   ```

---

### Error: "Network timeout"
```
MongoError: connection timed out after 10000ms
```

**Solutions:**
1. **Check network connectivity**
   ```bash
   # Ping MongoDB host
   ping cluster.mongodb.net
   
   # Check DNS resolution
   nslookup cluster.mongodb.net
   ```

2. **Increase timeout in config.py**
   ```python
   # Add to database.py
   client = AsyncClient(
       MONGODB_URI,
       serverSelectionTimeoutMS=5000,
       connectTimeoutMS=10000,
       socketTimeoutMS=30000
   )
   ```

3. **Check if MongoDB is overloaded**
   - Login to MongoDB Atlas
   - Check Metrics → Network I/O, CPU, Memory
   - Consider upgrading cluster tier

---

## 🔴 API & FastAPI Issues

### Error: "Address already in use"
```
ERROR:     Address already in use
Uvicorn can't start because port 8000 is already in use
```

**Solutions:**
1. **Find and kill process using port 8000**
   ```bash
   # Find process
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Use different port**
   ```bash
   python -m uvicorn app.main:app --port 8001
   ```

3. **Check what's using the port**
   ```bash
   sudo netstat -tlnp | grep :8000
   ```

---

### Error: "ModuleNotFoundError: No module named..."
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
1. **Install missing dependencies**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   
   # Or specific package
   pip install fastapi
   ```

2. **Check Python version**
   ```bash
   python --version  # Should be 3.9+
   ```

3. **Activate virtual environment**
   ```bash
   # Create if not exists
   python -m venv venv
   
   # Activate
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate.bat  # Windows
   ```

4. **Reinstall all packages**
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

---

### Error: "JSON decode error"
```
JSONDecodeError: Expecting value: line 1 column 1
```

**Solutions:**
1. **Check request format**
   ```bash
   # Must be valid JSON
   curl -X POST http://localhost:8000/api/v1/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "test"}'  # Valid JSON
   ```

2. **Check Content-Type header**
   ```bash
   # Always include this
   -H "Content-Type: application/json"
   ```

3. **Validate JSON**
   ```bash
   # Use online validator: jsonlint.com
   # Or check locally:
   python -m json.tool << 'EOF'
   {"question": "test"}
   EOF
   ```

---

## 🔴 File Upload Issues

### Error: "File size limit exceeded"
```
HTTPException: Uploaded file is too large
```

**Solutions:**
1. **Check file size limit in config.py**
   ```python
   MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
   ```

2. **Increase limit if needed**
   ```python
   # In app/routes/upload.py
   MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
   ```

3. **Check nginx/server limits**
   ```nginx
   # In nginx config
   client_max_body_size 100M;
   ```

---

### Error: "Invalid file type"
```
ValueError: Only PDF files are accepted
```

**Solutions:**
1. **Ensure file is PDF**
   ```bash
   # Check file type
   file document.pdf
   # Should output: PDF document, version 1.4
   ```

2. **Verify file extension**
   ```bash
   # Must end with .pdf (case-insensitive)
   document.pdf  # ✓ Valid
   document.PDF  # ✓ Valid
   document.txt  # ✗ Invalid
   ```

3. **Check MIME type**
   ```bash
   # Verify MIME type
   mimetype document.pdf
   # Should output: application/pdf
   ```

---

### Error: "PDF parsing error"
```
PDFException: Error extracting text from PDF
```

**Solutions:**
1. **Check PDF is valid**
   ```bash
   # Try opening locally
   pdftotext document.pdf  # If ImageMagick installed
   ```

2. **Try pdfplumber directly**
   ```python
   import pdfplumber
   with pdfplumber.open("document.pdf") as pdf:
       for page in pdf.pages:
           print(page.extract_text())
   ```

3. **Supported PDF versions**
   - PDF 1.4 and higher
   - Text-based PDFs (not image scans)
   - If PDF is scanned, try OCR first

---

## 🔴 Vector Search (FAISS) Issues

### Error: "FAISS index not found"
```
FileNotFoundError: [Errno 2] No such file or directory: 'faiss_index.bin'
```

**Solutions:**
1. **Initialize empty index**
   ```python
   # This happens automatically on first document upload
   # Just upload a document first
   curl -F "file=@test.pdf" http://localhost:8000/api/v1/upload
   ```

2. **Rebuild index from database**
   ```bash
   # Create script to rebuild
   python scripts/rebuild_faiss_index.py
   ```

3. **Check index path**
   ```python
   # In config.py, verify:
   FAISS_INDEX_PATH = "faiss_index.bin"
   
   # Should exist in current working directory or absolute path needed:
   FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
   ```

---

### Error: "Vector dimension mismatch"
```
RuntimeError: Vector dimension mismatch
```

**Solutions:**
1. **Check embedding model**
   ```python
   # In config.py
   EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
   # Don't mix with other models (they have different dimensions)
   ```

2. **Rebuild with consistent model**
   ```python
   # When rebuilding index, use same model
   from app.services.rag_service import RAGService
   rag = RAGService()
   rag.initialize_faiss_index()  # Recreates with current model
   ```

---

## 🔴 Speech Service Issues

### Error: "OpenAI API key invalid"
```
AuthenticationError: Invalid API key
```

**Solutions:**
1. **Verify API key**
   ```bash
   # In .env
   OPENAI_API_KEY=sk-proj-xxxxx
   
   # Should start with "sk-proj-" or "sk-"
   ```

2. **Check key has permissions**
   - Login to OpenAI
   - Go to Account → API Keys
   - Ensure key has access to: GPT-3.5, Embeddings, Whisper, TTS

3. **Test key directly**
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="sk-xxxxx")
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "test"}]
   )
   print(response)
   ```

---

### Error: "Speech-to-text failed"
```
Error transcribing audio with Whisper
```

**Solutions:**
1. **Check audio file format**
   ```bash
   # Supported: MP3, MP4, MPEG, MPGA, M4A, OGG, FLAC, WAV, WEBM
   file audio.mp3
   ```

2. **Check file size (max 25MB)**
   ```bash
   ls -lh audio.mp3  # Should be < 25MB
   ```

3. **Test Whisper API**
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="sk-xxxxx")
   
   with open("audio.mp3", "rb") as f:
       transcript = client.audio.transcriptions.create(
           model="whisper-1",
           file=f
       )
   print(transcript)
   ```

---

### Error: "Text-to-speech failed"
```
Error generating speech with ElevenLabs
```

**Solutions:**
1. **Verify ElevenLabs API key**
   ```bash
   # In .env
   ELEVENLABS_API_KEY=your-api-key-here
   
   # Get from: elevenlabs.io/app/api-keys
   ```

2. **Check text length**
   ```python
   # Text must be between 1-2000 characters
   text = "..." # 1-2000 chars
   ```

3. **Verify voice ID**
   ```python
   # Available voices: 21m00Tcm4TlvDq8ikWAM, EXAVITQu4vr4xnSDxMaL, etc.
   # List voices at: elevenlabs.io/app/voice-library
   ```

4. **Test API directly**
   ```python
   import requests
   
   headers = {"xi-api-key": "your-api-key"}
   url = "https://api.elevenlabs.io/v1/voices"
   response = requests.get(url, headers=headers)
   print(response.json())
   ```

---

## 🔴 Session Management Issues

### Error: "Session not found"
```
HTTPException: Session not found
```

**Solutions:**
1. **Verify session ID exists**
   ```bash
   # Get all sessions
   curl http://localhost:8000/api/v1/session
   
   # Check returned IDs
   ```

2. **Session ID format**
   ```bash
   # Must be valid MongoDB ObjectId
   # Format: 24 hex characters
   # Example: 507f1f77bcf86cd799439011
   
   # Check in Python
   from bson import ObjectId
   ObjectId("507f1f77bcf86cd799439011")  # Valid
   ```

3. **Check MongoDB**
   ```bash
   # Connect to MongoDB
   mongosh "mongodb+srv://user:pass@cluster.mongodb.net/voxdocs"
   
   # List sessions
   db.session.find()
   ```

---

### Error: "Message creation failed"
```
Error adding message to session
```

**Solutions:**
1. **Verify session exists first**
   ```bash
   curl http://localhost:8000/api/v1/session/{session_id}
   ```

2. **Check question is not empty**
   ```bash
   # Question must be 1-500 characters
   
   curl -X POST http://localhost:8000/api/v1/ask/session \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "60d5ec49c1234567890abcde",
       "question": "Valid question?"
     }'
   ```

3. **Check database permissions**
   ```bash
   # Verify user has readWrite on voxdocs database
   mongosh
   use voxdocs
   db.auth("username", "password")
   ```

---

## 🔴 Performance Issues

### Problem: "Slow response times"
```
Average response time > 5 seconds
```

**Solutions:**
1. **Check database performance**
   ```bash
   # In MongoDB Atlas
   - Check Metrics → Network I/O, CPU
   - Check Databases → Collections → Indexes
   - Ensure indexes exist on: session_id, created_at
   ```

2. **Monitor server resources**
   ```bash
   # CPU usage
   top -b -n 1 | head -20
   
   # Memory usage
   free -h
   
   # Disk I/O
   iostat -x 1 5
   ```

3. **Enable query caching** (future enhancement)
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   async def get_documents():
       ...
   ```

4. **Batch operations**
   ```python
   # Instead of individual inserts, batch them
   # Instead of N queries, use aggregation pipeline
   ```

---

### Problem: "High memory usage"
```
Memory exceeds 80% of available
```

**Solutions:**
1. **Check FAISS index size**
   ```bash
   ls -lh faiss_index.bin
   # Each embedding = 1536 * 4 bytes ≈ 6KB
   # 10,000 embeddings ≈ 60MB
   ```

2. **Clear audio files**
   ```bash
   # Remove old audio files
   find audio_output -mtime +7 -delete  # Older than 7 days
   ```

3. **Monitor process**
   ```bash
   # Check specific process memory
   ps aux | grep uvicorn
   
   # Monitor over time
   watch -n 1 'ps aux | grep uvicorn'
   ```

4. **Increase server resources**
   - Upgrade to larger instance
   - Enable swap memory (Linux)

---

## 🔴 Authentication & Security Issues

### Error: "CORS error"
```
Cross-Origin Request Blocked
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solutions:**
1. **Check CORS configuration**
   ```python
   # In app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Update for your frontend domain**
   ```python
   allow_origins=[
       "http://localhost:3000",  # Development
       "http://localhost:5173",  # Vite
       "https://yourdomain.com", # Production
   ]
   ```

3. **Test CORS**
   ```bash
   curl -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS http://localhost:8000/api/v1/ask
   ```

---

## 📊 Diagnostic Commands

### Check System Health
```bash
#!/bin/bash

echo "=== System Health Check ==="
echo ""

echo "1. Python Version:"
python --version

echo ""
echo "2. FastAPI Running:"
curl -s http://localhost:8000/health | jq '.'

echo ""
echo "3. MongoDB Connection:"
python -c "
from app.config import MONGODB_URI
from motor.motor_asyncio import AsyncClient
import asyncio

async def check():
    client = AsyncClient(MONGODB_URI)
    try:
        await client.admin.command('ping')
        print('✓ MongoDB connected')
    except Exception as e:
        print(f'✗ MongoDB error: {e}')
    finally:
        client.close()

asyncio.run(check())
"

echo ""
echo "4. OpenAI API:"
python -c "
from openai import OpenAI
try:
    client = OpenAI()
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'test'}]
    )
    print('✓ OpenAI API working')
except Exception as e:
    print(f'✗ OpenAI error: {e}')
" 2>/dev/null || echo "✗ OpenAI API key not configured"

echo ""
echo "5. FAISS Index:"
if [ -f "faiss_index.bin" ]; then
    echo "✓ FAISS index exists"
    ls -lh faiss_index.bin
else
    echo "⚠ FAISS index not found (will be created on first upload)"
fi

echo ""
echo "6. Disk Space:"
df -h | grep -E "^/dev|Filesystem|mounted"

echo ""
echo "7. Memory Usage:"
free -h

echo ""
echo "=== Health check complete ==="
```

---

## 📞 Getting Help

### Debugging Steps
1. **Reproduce the issue** consistently
2. **Check logs** - enable debug logging
3. **Isolate the component** - test each independently
4. **Simplify the request** - remove optional parameters
5. **Check latest docs** - ensure configuration is current

### Enable Debug Logging
```python
# In config.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment
export LOG_LEVEL=DEBUG
python -m uvicorn app.main:app --reload
```

### Useful Resources
- FastAPI Docs: https://fastapi.tiangolo.com
- MongoDB Documentation: https://docs.mongodb.com
- OpenAI API Docs: https://platform.openai.com/docs
- FAISS Documentation: https://github.com/facebookresearch/faiss/wiki
- ElevenLabs API: https://elevenlabs.io/docs

---

**Still having issues? Check the logs! 🔍**
