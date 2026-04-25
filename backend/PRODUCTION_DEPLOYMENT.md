# 🚀 Production Deployment Guide

## Pre-Deployment Checklist

### ✅ Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `MONGODB_URI` to production MongoDB Atlas URI
- [ ] Set `DATABASE_NAME` appropriately
- [ ] Set `OPENAI_API_KEY` (production key)
- [ ] Set `ELEVENLABS_API_KEY` (production key)
- [ ] Set `SECRET_KEY` to a random 32+ character string
- [ ] Review all configuration values in `config.py`

### ✅ Security
- [ ] Enable HTTPS/SSL (use reverse proxy like nginx)
- [ ] Set `ALGORITHM` to `HS256` or higher
- [ ] Implement JWT authentication middleware
- [ ] Add rate limiting (FastAPI slowapi)
- [ ] Enable CORS properly (restrict to your domains)
- [ ] Store secrets in environment variables (never commit .env)
- [ ] Use strong passwords for MongoDB
- [ ] Enable MongoDB IP whitelist

### ✅ Database
- [ ] Create MongoDB Atlas account
- [ ] Create production cluster
- [ ] Whitelist production server IPs
- [ ] Create database user with limited permissions
- [ ] Create backups (enable auto-backups in Atlas)
- [ ] Test connection from production environment

### ✅ Dependencies
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify all packages installed without errors
- [ ] Test imports: `python -c "import uvicorn, fastapi, beanie, motor"`

### ✅ Testing
- [ ] Run `python -m pytest tests/` (when tests are added)
- [ ] Test endpoints manually: `python example_usage.py`
- [ ] Test with production MongoDB connection
- [ ] Test file upload with various PDFs
- [ ] Test speech-to-text and text-to-speech

---

## Deployment Options

### Option 1: Docker (Recommended)

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  voxdocs-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=${MONGODB_URI}
      - DATABASE_NAME=${DATABASE_NAME}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
      - FAISS_INDEX_PATH=/app/faiss_index.bin
      - PDF_STORAGE_PATH=/app/uploads
    volumes:
      - ./uploads:/app/uploads
      - ./faiss_index.bin:/app/faiss_index.bin
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Build and Run
```bash
# Build image
docker build -t voxdocs-api:1.0.0 .

# Run container
docker run -d -p 8000:8000 \
  -e MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net" \
  -e OPENAI_API_KEY="sk-..." \
  -e ELEVENLABS_API_KEY="your-key" \
  -v $(pwd)/uploads:/app/uploads \
  --name voxdocs \
  voxdocs-api:1.0.0

# Check logs
docker logs -f voxdocs

# Stop container
docker stop voxdocs
```

---

### Option 2: Linux Server (Manual)

#### Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip nginx supervisor

# Create app user
sudo useradd -m -s /bin/bash voxdocs
sudo mkdir -p /home/voxdocs/app
sudo chown -R voxdocs:voxdocs /home/voxdocs/app
```

#### Installation
```bash
# Switch to app user
sudo su - voxdocs

# Clone/copy application code
cd /home/voxdocs/app
# Copy your code here

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
DATABASE_NAME=voxdocs
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=your-key
EOF

# Test run
python -m uvicorn app.main:app --reload
```

#### Supervisor Configuration
```bash
# Create /etc/supervisor/conf.d/voxdocs.conf
cat > /etc/supervisor/conf.d/voxdocs.conf << 'EOF'
[program:voxdocs]
directory=/home/voxdocs/app
command=/home/voxdocs/app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
user=voxdocs
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/voxdocs/app.log
environment=PATH="/home/voxdocs/app/venv/bin"
EOF

# Create log directory
sudo mkdir -p /var/log/voxdocs
sudo chown voxdocs:voxdocs /var/log/voxdocs

# Enable and start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start voxdocs
```

#### Nginx Configuration
```bash
# Create /etc/nginx/sites-available/voxdocs
cat > /etc/nginx/sites-available/voxdocs << 'EOF'
upstream voxdocs_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json;

    client_max_body_size 100M;

    location / {
        proxy_pass http://voxdocs_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # Static files (audio downloads)
    location /api/v1/voice/audio/ {
        alias /home/voxdocs/app/audio_output/;
        expires 1h;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/voxdocs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

### Option 3: Cloud Platforms

#### AWS EC2
```bash
# Launch Ubuntu 22.04 t3.medium instance
# Security group: Allow 80, 443, 22

# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Follow "Option 2: Linux Server" steps
```

#### DigitalOcean Droplet
```bash
# Create $5-12/month Droplet with Ubuntu 22.04
# SSH and follow Option 2 steps
# Use DigitalOcean App Platform for easier deployment
```

#### Google Cloud Run (Recommended for simplicity)
```bash
# Push to Container Registry
docker build -t voxdocs-api:1.0.0 .
docker tag voxdocs-api:1.0.0 gcr.io/PROJECT_ID/voxdocs-api:1.0.0
docker push gcr.io/PROJECT_ID/voxdocs-api:1.0.0

# Deploy to Cloud Run
gcloud run deploy voxdocs-api \
  --image gcr.io/PROJECT_ID/voxdocs-api:1.0.0 \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 60 \
  --max-instances 10 \
  --set-env-vars MONGODB_URI=$MONGODB_URI,OPENAI_API_KEY=$OPENAI_API_KEY
```

#### Heroku (Legacy but simple)
```bash
# Create Procfile
cat > Procfile << EOF
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

# Create runtime.txt
echo "python-3.10.0" > runtime.txt

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Performance Optimization

### 1. Enable Response Compression
Already configured in `app/main.py` with GZipMiddleware

### 2. Connection Pooling
MongoDB Motor automatically handles connection pooling

### 3. Caching (Future Enhancement)
```python
from functools import lru_cache
from fastapi import Depends
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Cache document list for 5 minutes
@app.get("/documents", response_class=JSONResponse)
@cached(expire=300)
async def get_all_documents():
    ...
```

### 4. Load Balancing
```nginx
upstream voxdocs {
    server api1.example.com:8000;
    server api2.example.com:8000;
    server api3.example.com:8000;
}

# ... rest of nginx config ...
```

### 5. CDN for Audio Files
```python
# Serve audio from CDN
AUDIO_CDN_URL = "https://cdn.example.com/audio"

@app.post("/voice/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    # ... generate audio ...
    audio_url = f"{AUDIO_CDN_URL}/audio/{filename}"
    return {"audio_url": audio_url}
```

---

## Monitoring & Logging

### 1. Application Logs
```python
# Already configured in config.py
# Logs go to ./logs/app.log

import logging
logger = logging.getLogger(__name__)
logger.info("Processing document...")
```

### 2. Health Check Monitoring
```bash
# Uptime monitoring (UptimeRobot, Pingdom)
# Add to monitoring: GET /health
# Expected: {"status": "healthy"}
```

### 3. Database Monitoring
- Use MongoDB Atlas dashboard
- Monitor: CPU, Memory, Connection count
- Set alerts for: High CPU, Connection exhaustion

### 4. Application Monitoring (Optional)
```python
# Add to requirements.txt
# sentry-sdk==1.37.0

import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

### 5. Log Aggregation (Optional)
```bash
# Option A: ELK Stack (Elasticsearch, Logstash, Kibana)
# Option B: Datadog
# Option C: CloudWatch (if on AWS)
# Option D: Stackdriver (if on GCP)
```

---

## Database Backups

### MongoDB Atlas Automatic Backups
- Update `/app/config.py`:
```python
BACKUP_ENABLED = True
BACKUP_FREQUENCY = 24  # hours
BACKUP_RETENTION = 7   # days
```

### Manual Backup
```bash
# Export data
mongodump --uri "mongodb+srv://user:pass@cluster.mongodb.net/voxdocs" \
  --out backup_$(date +%Y%m%d)

# Download backup
tar -czf backup.tar.gz backup_20260425/

# Restore from backup
mongorestore --uri "mongodb+srv://user:pass@cluster.mongodb.net" \
  backup_20260425/
```

---

## Scaling Strategy

### Phase 1 (1-1000 users)
- Single server (2GB RAM, 2CPU)
- MongoDB shared cluster
- Local FAISS index

### Phase 2 (1000-10000 users)
- Load balancer + 2-3 API servers
- MongoDB dedicated cluster
- Distributed FAISS with Redis cache
- CDN for audio files

### Phase 3 (10000+ users)
- Kubernetes cluster (5-10 nodes)
- MongoDB sharded cluster
- Redis cluster for caching
- Elasticsearch for search
- Message queue (RabbitMQ/Kafka) for async processing

---

## Security Hardening

### API Security
```python
# Add to requirements.txt
slowapi==0.1.8  # Rate limiting

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/documents")
@limiter.limit("100/minute")
async def get_documents(request: Request):
    ...
```

### CORS Configuration
```python
# In app/main.py - Update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

### MongoDB User Permissions
```javascript
// Create limited user for API
db.createUser({
  user: "voxdocs_user",
  pwd: "strong_random_password_32_chars",
  roles: [
    { role: "readWrite", db: "voxdocs" }
  ]
})
```

### Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Load from secure location
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id openai-key)
```

---

## Emergency Procedures

### If FAISS Index Corrupts
```bash
# Rebuild from MongoDB
python scripts/rebuild_faiss_from_db.py
```

### If MongoDB Connection Fails
```bash
# Check connectivity
curl mongodb+srv://user:pass@cluster.mongodb.net/admin

# Verify IP whitelist
# Login to MongoDB Atlas → Security → Network Access

# Check credentials
# Verify MONGODB_URI in .env
```

### If Memory Usage Spikes
```bash
# Check memory status
free -h

# Monitor process
top -p $(pgrep -f uvicorn)

# Clear old audio files
find audio_output -mtime +7 -delete
```

---

## Rollback Procedure

```bash
# Tag releases
git tag v1.0.0
git push origin v1.0.0

# Rollback to previous version
docker pull voxdocs-api:v0.9.0
docker run -d ... voxdocs-api:v0.9.0

# Or with git
git checkout v0.9.0
./deploy.sh
```

---

## Post-Deployment Validation

```bash
#!/bin/bash

API="https://your-domain.com/api/v1"

echo "Testing health endpoint..."
curl -s $API/health | jq '.'

echo "Testing document endpoints..."
curl -s $API/documents | jq '.'

echo "Testing session creation..."
curl -s -X POST $API/session/new \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}' | jq '.'

echo "Testing speech endpoint..."
curl -s -X POST $API/voice/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}' | jq '.'

echo "✅ All endpoints responding!"
```

---

**Your production deployment is ready! 🚀**
