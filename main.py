"""
BlusWipe - Production Web Application
AI-powered background removal service optimized for cloud deployment.

Developed by Eleblu Nunana
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.background_remover import BackgroundRemover
from app.utils.config import Config
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
background_remover: Optional[BackgroundRemover] = None
config = Config()

# Define directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, MODELS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global background_remover
    try:
        logger.info("🚀 Starting BlusWipe Production Server...")
        background_remover = BackgroundRemover(
            model_name="u2net"
        )
        logger.info("✅ Background remover initialized successfully")
        
        # Make background_remover available to routes
        app.state.background_remover = background_remover
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize background remover: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down BlusWipe server...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="BlusWipe - AI Background Remover",
    description="Production-ready AI-powered background removal service. Developed by Eleblu Nunana.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routes
app.include_router(router)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="BlusWipe Production Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Starting BlusWipe on {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
