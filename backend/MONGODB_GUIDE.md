# 🗄️ MongoDB Atlas Integration Guide

## Introduction

The VoxDocs backend now integrates **MongoDB Atlas** (cloud database) for:
- **Session Management**: Create and manage chat sessions
- **Chat History**: Store questions and answers with metadata
- **Document Tracking**: Track uploaded documents and their processing
- **Persistent Storage**: Keep data across server restarts

---

## 🚀 MongoDB Atlas Setup

### 1. Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new project

### 2. Create a Cluster

1. Click **Create** on the Clusters page
2. Choose **M0 (Free)** tier
3. Select your region (closest to your location)
4. Click **Create Cluster**
5. Wait 2-3 minutes for cluster creation

### 3. Create Database User

1. In the left sidebar, click **Database Access**
2. Click **Add New Database User**
3. Choose **Password** authentication
4. Enter username and password (save these!)
5. Click **Add User**

### 4. Allow Network Access

1. In the left sidebar, click **Network Access**
2. Click **Add IP Address**
3. Select **Allow access from anywhere** (0.0.0.0/0) for development
   - For production, restrict to your app's IP
4. Click **Confirm**

### 5. Get Connection String

1. Click **Databases** in the left sidebar
2. Click **Connect** on your cluster
3. Select **Drivers** → **Python** → **3.12 or later**
4. Copy the connection string

Your connection string looks like:
```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/voxdocs
```

Replace:
- `<username>`: Your database user
- `<password>`: Your password (URL-encode special characters)
- `cluster0.xxxxx`: Your cluster name

---

## 🔌 Environment Configuration

### 1. Update .env File

```bash
# Edit your .env file
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/voxdocs
DATABASE_NAME=voxdocs
```

### 2. Test Connection (Optional)

```python
from motor.motor_asyncio import AsyncClient

async def test_connection():
    client = AsyncClient("your_connection_string")
    await client.admin.command("ping")
    print("✓ Connected to MongoDB!")
    client.close()

# Run in Python
import asyncio
asyncio.run(test_connection())
```

---

## 📊 Database Models

### Session Document
```python
{
  "_id": ObjectId,
  "title": "What is FastAPI?",
  "created_at": "2026-04-25T10:00:00",
  "updated_at": "2026-04-25T10:15:00"
}
```

### Message Document
```python
{
  "_id": ObjectId,
  "session_id": "session_id_string",
  "question": "How to create an API?",
  "answer": "With FastAPI, you can...",
  "sources": ["document1.pdf"],
  "confidence": 0.92,
  "created_at": "2026-04-25T10:00:00"
}
```

### Document Document
```python
{
  "_id": ObjectId,
  "filename": "guide.pdf",
  "file_path": "uploads/guide.pdf",
  "uploaded_at": "2026-04-25T10:00:00",
  "chunk_count": 25,
  "file_size": 102400,
  "embedding_count": 25,
  "status": "success"
}
```

---

## 🔌 API Endpoints

### Session Management

#### Create New Session
```bash
POST /api/v1/session/new

Request:
{
  "title": "Software Design Discussion"
}

Response:
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Software Design Discussion",
  "created_at": "2026-04-25T10:00:00+00:00",
  "updated_at": "2026-04-25T10:00:00+00:00"
}
```

#### Get All Sessions
```bash
GET /api/v1/session

Response:
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "Software Design Discussion",
    "created_at": "2026-04-25T10:00:00+00:00",
    "updated_at": "2026-04-25T10:00:00+00:00"
  },
  ...
]
```

#### Get Session History
```bash
GET /api/v1/session/{session_id}

Response:
{
  "session": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Software Design Discussion",
    "created_at": "2026-04-25T10:00:00+00:00",
    "updated_at": "2026-04-25T10:00:00+00:00"
  },
  "messages": [
    {
      "id": "507f1f77bcf86cd799439012",
      "question": "What is design patterns?",
      "answer": "Design patterns are...",
      "sources": ["guide.pdf"],
      "confidence": 0.85,
      "created_at": "2026-04-25T10:00:00+00:00"
    },
    ...
  ]
}
```

#### Delete Session
```bash
DELETE /api/v1/session/{session_id}

Response:
{
  "success": true,
  "message": "Session ... and all messages deleted"
}
```

---

### Chat with Session Context

#### Ask Question (with session tracking)
```bash
POST /api/v1/ask/session

Request:
{
  "session_id": "507f1f77bcf86cd799439011",
  "question": "What are the best practices?",
  "include_audio": false
}

Response:
{
  "answer": "Based on the documents, best practices include...",
  "sources": ["guide.pdf", "best_practices.pdf"],
  "audio_url": null,
  "confidence": 0.88
}
```

The message is automatically saved to MongoDB!

---

### Document Management

#### Get All Documents
```bash
GET /api/v1/documents

Response:
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
```

#### Get Document Details
```bash
GET /api/v1/documents/{doc_id}

Response:
{
  "id": "507f1f77bcf86cd799439013",
  "filename": "guide.pdf",
  "file_path": "uploads/guide.pdf",
  "uploaded_at": "2026-04-25T10:00:00+00:00",
  "chunk_count": 25,
  "file_size": 102400,
  "embedding_count": 25
}
```

#### Get Document Statistics
```bash
GET /api/v1/documents/stats/overview

Response:
{
  "total_documents": 5,
  "total_size_bytes": 512000,
  "total_chunks": 125,
  "total_embeddings": 125,
  "average_file_size": 102400,
  "average_chunks_per_doc": 25
}
```

---

## 💻 Usage Examples

### Python Client Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# 1. Create a session
session_resp = requests.post(
    f"{API_BASE}/session/new",
    json={"title": "FastAPI Discussion"}
)
session_id = session_resp.json()["id"]

# 2. Ask a question (with session)
query_resp = requests.post(
    f"{API_BASE}/ask/session",
    json={
        "session_id": session_id,
        "question": "How to create an API?",
        "include_audio": False
    }
)
print("Answer:", query_resp.json()["answer"])

# 3. Get session history
history_resp = requests.get(f"{API_BASE}/session/{session_id}")
messages = history_resp.json()["messages"]
print(f"Chat history ({len(messages)} messages)")

# 4. Get all documents
docs_resp = requests.get(f"{API_BASE}/documents")
documents = docs_resp.json()
print(f"Total documents: {len(documents)}")

# 5. Get statistics
stats_resp = requests.get(f"{API_BASE}/documents/stats/overview")
stats = stats_resp.json()
print(f"Total chunks: {stats['total_chunks']}")
```

---

## 🔄 Workflow Example

### Complete Conversation Flow

```
1. Upload Document
   POST /api/v1/upload → Document saved to vector store + MongoDB

2. Create Session
   POST /api/v1/session/new → New conversation created

3. Ask Questions (multiple)
   POST /api/v1/ask/session → Each Q&A pair saved to MongoDB

4. Review History
   GET /api/v1/session/{session_id} → Get all messages

5. Check Documents
   GET /api/v1/documents → See all uploaded documents

6. Delete Session
   DELETE /api/v1/session/{session_id} → Clean up conversation
```

---

## 🔍 Monitoring in MongoDB Atlas

### 1. View Data in MongoDB Atlas

1. Go to **Collections** in MongoDB Atlas
2. You'll see three collections:
   - `sessions` - Chat sessions
   - `messages` - Q&A pairs
   - `documents` - Uploaded documents

### 2. Query Data

```javascript
// Find all sessions
db.sessions.find({})

// Get messages from a session
db.messages.find({"session_id": "507f1f77bcf86cd799439011"})

// Count documents
db.documents.countDocuments({})
```

### 3. View Usage Statistics

In MongoDB Atlas dashboard:
- **Metrics** tab → View storage, operation counts
- **Logs** → Check for errors
- **Alerts** → Set up notifications

---

## ⚙️ Configuration Options

### Beanie Model Indexes

Indexes are automatically created on:
- `sessions.created_at`, `sessions.updated_at`
- `messages.session_id`, `messages.created_at`
- `documents.uploaded_at`, `documents.filename`

This ensures fast queries even with large datasets.

---

## 🚀 Production Checklist

### Database
- [ ] Use dedicated MongoDB Atlas cluster (not M0)
- [ ] Enable encryption in rest
- [ ] Configure IP whitelist (not 0.0.0.0/0)
- [ ] Set up automated backups
- [ ] Monitor storage usage

### Application
- [ ] Set `MONGODB_URI` in production environment
- [ ] Use strong database password
- [ ] Enable connection pooling
- [ ] Add error logging for DB operations
- [ ] Test failover scenarios

### Security
- [ ] Don't commit `.env` file
- [ ] Rotate database credentials regularly
- [ ] Use separate DB user for each environment
- [ ] Implement authentication in API
- [ ] Log all database access

---

## 🐛 Troubleshooting

### Connection Issues

```
Error: ServerSelectionTimeoutError
→ Check MONGODB_URI in .env
→ Verify IP whitelist in MongoDB Atlas
→ Ensure network connectivity
```

### Authentication Failed

```
Error: Authentication failed
→ Verify username/password in connection string
→ Check URL encoding of special characters
→ Ensure user exists in MongoDB Atlas
```

### No Collections Found

```
Issue: Collections not created
→ Upload a document first (creates documents collection)
→ Create a session first (creates sessions collection)
→ Ask a question (creates messages collection)
```

### Slow Queries

```
Solution:
→ Check indexes on MongoDB Atlas Metrics
→ Ensure created_at fields are indexed
→ Verify session_id index on messages
→ Monitor query performance in Atlas
```

---

## 📚 Additional Resources

- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Beanie ODM Documentation](https://beanie-odm.readthedocs.io/)
- [Motor (Async MongoDB Driver)](https://motor.readthedocs.io/)
- [MongoDB Connection Tutorial](https://www.mongodb.com/docs/guides/server/drivers/)

---

## 🎯 Key Benefits

✅ **Cloud Database** - MongoDB Atlas is fully managed
✅ **Auto-scaling** - Handles growth automatically
✅ **Backup & Recovery** - Automatic backups included
✅ **Global Access** - Access from anywhere
✅ **Monitoring** - Built-in metrics and alerts
✅ **Async Support** - Motor driver for async operations
✅ **Type Safe** - Beanie provides type-safe ORM
✅ **Flexible Schema** - JSON-like documents

---

**Your VoxDocs backend now supports persistent session management and document tracking! 🎉**
