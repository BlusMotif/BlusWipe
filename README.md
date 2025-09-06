# BlusWipe Production - AI Background Remover

🚀 **Production-ready web application for AI-powered background removal.**

## 📁 Project Structure

```
BlusWipe-Production/
├── 📄 main.py                   # FastAPI application entry point
├── 📄 requirements.txt          # Python dependencies (pinned versions)
├── 📄 Dockerfile               # Container configuration
├── 📄 Procfile                 # Heroku/Railway deployment
├── 📄 railway.json            # Railway configuration
├── 📄 .gitignore               # Git ignore rules
│
├── 📁 app/                     # Application modules
│   ├── 📄 __init__.py
│   ├── 📁 api/                 # API routes
│   │   ├── 📄 __init__.py
│   │   └── 📄 routes.py        # REST API endpoints
│   ├── 📁 core/                # Core business logic
│   │   ├── 📄 __init__.py
│   │   └── 📄 background_remover.py  # AI processing engine
│   └── 📁 utils/               # Utilities
│       ├── 📄 __init__.py
│       └── 📄 config.py        # Configuration management
│
├── 📁 templates/               # Jinja2 templates
│   └── 📄 index.html          # Web interface
├── 📁 static/                 # Static assets (CSS, JS, images)
├── 📁 uploads/                # Temporary file uploads
├── 📁 outputs/                # Processed images
└── 📁 models/                 # AI model cache
```

## ✨ Features

### 🧠 AI-Powered Processing
- **Multiple Models**: U²-Net, ISNet, Silueta for different use cases
- **GPU Acceleration**: Automatic CUDA detection and usage
- **Edge Enhancement**: Post-processing for cleaner results
- **Batch Processing**: Handle multiple images simultaneously

### 🌐 Production Web Stack
- **FastAPI**: High-performance async web framework
- **Modern Architecture**: Clean separation of concerns
- **RESTful API**: Complete API with OpenAPI documentation
- **Responsive UI**: Bootstrap 5 web interface

### 🔒 Security & Performance
- **File Validation**: Strict image type and size checking
- **Path Security**: Protection against directory traversal
- **Rate Limiting**: Built-in request throttling
- **Auto Cleanup**: Automatic temporary file management
- **Health Checks**: Monitoring endpoints for uptime

## 🚀 Quick Deploy

### Option 1: Railway (Recommended)
1. **Connect GitHub**: Fork this repo and connect to Railway
2. **Auto Deploy**: Railway detects Python and deploys automatically
3. **Environment**: Set any environment variables if needed
4. **Access**: Your app will be live at `https://your-app.railway.app`

### Option 2: Heroku
```bash
# Install Heroku CLI
heroku create your-bluswipe-app
git push heroku main
```

### Option 3: DigitalOcean App Platform
1. **Connect Repo**: Link your GitHub repository
2. **Configure**: Select Python app type
3. **Deploy**: Automatic deployment from main branch

### Option 4: Google Cloud Run
```bash
gcloud run deploy bluswipe \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 5: Docker
```bash
# Build and run locally
docker build -t bluswipe-prod .
docker run -p 8000:8000 bluswipe-prod

# Or use Docker Compose
docker-compose up
```

## 🛠 Local Development

### Prerequisites
- Python 3.11+
- 4GB+ RAM (for AI models)
- 1GB+ disk space

### Setup
```bash
# Clone and enter directory
git clone <your-repo>
cd BlusWipe-Production

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py --host 127.0.0.1 --port 8000
```

### Access
- **Web Interface**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 API Reference

### Core Endpoints

#### Remove Background
```http
POST /api/remove-background
Content-Type: multipart/form-data

Parameters:
- file: Image file (max 10MB)
- model: AI model (u2net, u2netp, u2net_human_seg, silueta, isnet-general-use)
- enhancement: Edge enhancement strength (0.5-2.0)

Response: PNG image with background removed
```

#### Batch Processing
```http
POST /api/batch
Content-Type: multipart/form-data

Parameters:
- files: Multiple image files (max 5)

Response: JSON with download URLs for processed images
```

#### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "available_models": ["u2net", "u2netp", ...]
}
```

#### Available Models
```http
GET /api/models

Response:
{
  "models": ["u2net", "u2netp", "u2net_human_seg", "silueta", "isnet-general-use"],
  "current_model": "u2net",
  "descriptions": {...}
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Server configuration
PORT=8000
HOST=0.0.0.0

# File limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_BATCH_FILES=5

# AI model settings
DEFAULT_MODEL=u2net
USE_GPU=true

# Logging
LOG_LEVEL=INFO
```

### Production Settings
- **Memory**: Minimum 2GB RAM, 4GB recommended
- **Storage**: ~1GB for model cache
- **CPU**: 2+ cores recommended
- **GPU**: Optional but significantly improves performance

## 📈 Performance & Scaling

### Processing Times
- **Small images** (< 1MB): 2-5 seconds
- **Medium images** (1-5MB): 5-10 seconds  
- **Large images** (5-10MB): 10-20 seconds

### Scaling Options
- **Horizontal**: Multiple app instances behind load balancer
- **Vertical**: Increase CPU/RAM for single instance
- **GPU**: Add GPU support for 3-5x speed improvement

### Monitoring
- Health endpoint: `/health`
- Metrics: Prometheus-compatible (optional)
- Logs: Structured JSON logging
- Alerts: Configure based on health checks

## 🛡 Security

### Built-in Protection
- ✅ File type validation
- ✅ File size limits
- ✅ Path traversal protection
- ✅ CORS configuration
- ✅ Request rate limiting
- ✅ Input sanitization

### Production Checklist
- [ ] Configure allowed origins in CORS
- [ ] Set up proper logging
- [ ] Enable HTTPS/SSL
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerts
- [ ] Regular security updates

## 🎯 Use Cases

### Business Applications
- **E-commerce**: Product photography automation
- **Marketing**: Campaign asset creation
- **Real Estate**: Property photo enhancement
- **Fashion**: Model and product shots

### Integration Examples
- **SaaS Platforms**: Integrate via REST API
- **Mobile Apps**: Process user photos
- **Batch Processing**: Automated workflows
- **White-label**: Rebrand and deploy

## 📞 Support & Deployment

### Pre-deployment Checklist
- ✅ Dependencies installed
- ✅ Environment variables set
- ✅ Health check working
- ✅ Static files accessible
- ✅ Database/storage configured (if needed)

### Troubleshooting
1. **Memory Issues**: Increase instance RAM
2. **Slow Processing**: Enable GPU acceleration  
3. **File Upload Errors**: Check file size limits
4. **Model Loading**: Verify internet for first download

### Support Channels
- **Documentation**: `/docs` endpoint
- **Health Status**: `/health` endpoint
- **Logs**: Check application logs for errors

---

## 🎉 Ready for Production!

Your BlusWipe application is now optimized and ready for production deployment on any major cloud platform. Choose your preferred hosting option and start serving AI-powered background removal at scale! 

**Happy deploying! 🚀**
