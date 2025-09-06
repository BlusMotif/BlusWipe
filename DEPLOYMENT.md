# 🚀 BlusWipe Production Deployment Guide

Complete step-by-step instructions for deploying BlusWipe to various hosting platforms.

## 📋 Pre-Deployment Checklist

- [ ] Python 3.11+ environment
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Local testing successful (`python main.py`)
- [ ] Health check working (`http://localhost:8000/health`)
- [ ] Git repository initialized and code committed

## 🛤 Platform-Specific Deployments

### 🚄 Railway (Easiest - Recommended)

**Why Railway?**
- Zero-config Python deployment
- Automatic HTTPS/SSL
- Built-in monitoring
- Generous free tier

**Steps:**
1. **Create Account**: Visit [railway.app](https://railway.app)
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Connect Repo**: Authorize and select your BlusWipe-Production repository
4. **Auto-Deploy**: Railway automatically detects Python and deploys
5. **Environment**: Set any custom environment variables in Settings
6. **Domain**: Get your URL at `https://your-app.railway.app`

**Configuration:**
```json
// railway.json is already configured
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

**Estimated Deploy Time:** 3-5 minutes

---

### 🟣 Heroku

**Steps:**
1. **Install CLI**: Download [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login**: `heroku login`
3. **Create App**: `heroku create your-bluswipe-app`
4. **Set Buildpack**: `heroku buildpacks:set heroku/python`
5. **Deploy**: `git push heroku main`
6. **Scale**: `heroku ps:scale web=1`

**Environment Variables:**
```bash
heroku config:set MAX_FILE_SIZE=10485760
heroku config:set DEFAULT_MODEL=u2net
heroku config:set LOG_LEVEL=INFO
```

**Estimated Deploy Time:** 5-8 minutes

---

### 🌊 DigitalOcean App Platform

**Steps:**
1. **Create Account**: [DigitalOcean](https://www.digitalocean.com)
2. **Apps → Create App**: Choose GitHub source
3. **Repository**: Select BlusWipe-Production
4. **App Spec**: Configure Python app
5. **Environment**: Add variables in app settings
6. **Deploy**: App builds automatically

**App Spec Configuration:**
```yaml
name: bluswipe-production
services:
- name: web
  source_dir: /
  github:
    repo: your-username/BlusWipe-Production
    branch: main
  run_command: python main.py --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  health_check:
    http_path: /health
```

**Estimated Deploy Time:** 8-12 minutes

---

### ☁️ Google Cloud Run

**Prerequisites:**
- Google Cloud account
- gcloud CLI installed

**Steps:**
```bash
# Authenticate
gcloud auth login
gcloud config set project your-project-id

# Deploy directly from source
gcloud run deploy bluswipe \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10

# Get service URL
gcloud run services describe bluswipe --region us-central1 --format="value(status.url)"
```

**Environment Variables:**
```bash
gcloud run services update bluswipe \
  --set-env-vars MAX_FILE_SIZE=10485760,DEFAULT_MODEL=u2net \
  --region us-central1
```

**Estimated Deploy Time:** 3-5 minutes

---

### 🐳 Docker Deployment

**Local Docker:**
```bash
# Build image
docker build -t bluswipe-prod .

# Run container
docker run -p 8000:8000 -e PORT=8000 bluswipe-prod

# Or use Docker Compose
docker-compose up -d
```

**Docker Hub Deployment:**
```bash
# Tag and push to registry
docker tag bluswipe-prod your-username/bluswipe:latest
docker push your-username/bluswipe:latest

# Deploy on any Docker host
docker run -p 80:8000 your-username/bluswipe:latest
```

**Container Orchestration:**
- **Kubernetes**: Create deployment with `kubectl`
- **Docker Swarm**: Scale with swarm services
- **AWS ECS/Fargate**: Deploy container to AWS
- **Azure Container Instances**: Run on Azure

---

### 📱 Vercel (Serverless)

**Steps:**
1. **Install CLI**: `npm i -g vercel`
2. **Login**: `vercel login`
3. **Deploy**: `vercel --prod`

**Configuration** (`vercel.json`):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

**Note:** Serverless has limitations for large AI models. Consider Railway/Heroku for better performance.

---

## 🔧 Advanced Configurations

### Load Balancing & Scaling

**Nginx Configuration** (`nginx.conf`):
```nginx
upstream bluswipe_backend {
    server bluswipe1:8000;
    server bluswipe2:8000;
    server bluswipe3:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://bluswipe_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload size
        client_max_body_size 50M;
        
        # Timeouts for AI processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://bluswipe_backend/health;
        access_log off;
    }
}
```

### Database Integration (Optional)

For usage tracking, user management, or image history:

```python
# Add to requirements.txt
# sqlalchemy==2.0.23
# psycopg2-binary==2.9.9  # PostgreSQL
# alembic==1.13.1  # Database migrations

# Database models
from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ProcessedImage(Base):
    __tablename__ = "processed_images"
    
    id = Column(Integer, primary_key=True)
    original_filename = Column(String)
    processed_at = Column(DateTime)
    model_used = Column(String)
    file_size = Column(Integer)
    processing_time = Column(Integer)  # milliseconds
```

### Monitoring & Observability

**Health Check Enhancement:**
```python
import psutil
import time
from datetime import datetime

@app.get("/health")
async def enhanced_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time,
        "model_loaded": background_remover is not None,
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "available_models": list(MODEL_DESCRIPTIONS.keys())
    }
```

**Logging Configuration:**
```python
import logging
import json

# Structured logging for production
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_obj)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

---

## 🛡 Security Hardening

### Production Security Checklist

- [ ] **HTTPS/SSL**: Enable SSL certificates
- [ ] **CORS**: Configure allowed origins
- [ ] **Rate Limiting**: Implement request throttling
- [ ] **Input Validation**: Strict file type checking
- [ ] **Error Handling**: No sensitive info in error messages
- [ ] **File Cleanup**: Automatic temp file deletion
- [ ] **Environment Variables**: No secrets in code
- [ ] **Updates**: Regular dependency updates

### Environment Variables for Production

```bash
# Security
ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
SECRET_KEY="your-secret-key-here"
DEBUG=false

# File limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_BATCH_FILES=5
UPLOAD_TIMEOUT=300  # 5 minutes

# Performance
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=65

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN="your-sentry-dsn"  # Error tracking
```

---

## 📊 Performance Optimization

### Server Specifications

**Minimum Requirements:**
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 2GB
- **Bandwidth**: 100 Mbps

**Recommended for Production:**
- **CPU**: 4+ cores
- **RAM**: 4-8GB
- **Storage**: 10GB SSD
- **GPU**: Optional (3-5x performance boost)

### Performance Tips

1. **Model Caching**: Models stay loaded in memory
2. **GPU Acceleration**: Use CUDA-enabled hosting
3. **CDN**: Serve static files from CDN
4. **Compression**: Enable gzip compression
5. **Caching**: Cache processed images temporarily
6. **Load Balancing**: Multiple app instances

---

## 🔍 Troubleshooting

### Common Issues

**1. Memory Errors**
```bash
# Solution: Increase instance memory or use smaller models
Error: "RuntimeError: CUDA out of memory"
Fix: Set DEFAULT_MODEL=u2netp (smaller model)
```

**2. Slow Processing**
```bash
# Solution: Enable GPU or optimize models
Issue: Processing takes >30 seconds
Fix: Add GPU instance or reduce image size
```

**3. File Upload Errors**
```bash
# Solution: Check file size limits
Error: "413 Request Entity Too Large"
Fix: Increase MAX_FILE_SIZE or web server limits
```

**4. Health Check Failures**
```bash
# Solution: Verify endpoint and increase timeout
Error: Health check timeout
Fix: Check /health endpoint and extend timeout
```

### Debugging Commands

```bash
# Check application logs
docker logs bluswipe-container

# Test health endpoint
curl -f http://your-app.com/health

# Monitor resource usage
docker stats bluswipe-container

# Test API endpoint
curl -X POST -F "file=@test.jpg" http://your-app.com/api/remove-background
```

---

## 🎯 Success Metrics

After deployment, monitor these key metrics:

- **Uptime**: >99.9% availability
- **Response Time**: <5s for typical images
- **Error Rate**: <1% of requests
- **Memory Usage**: <80% of allocated
- **CPU Usage**: <70% average

---

## 🎉 You're Ready!

Your BlusWipe application is now production-ready and can be deployed to any major cloud platform. Choose the deployment option that best fits your needs:

- **Quick Start**: Railway (3 minutes)
- **Enterprise**: Google Cloud Run or AWS
- **Budget**: Heroku free tier
- **Custom**: Docker on VPS

**Next Steps:**
1. Choose your deployment platform
2. Follow the specific platform guide above
3. Configure monitoring and alerts
4. Set up custom domain (optional)
5. Launch and monitor your application

**Happy deploying! 🚀**
