"""
API routes for BlusWipe application.
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List

import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from io import BytesIO
from pathlib import Path

# Get directories
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create router
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for monitoring."""
    background_remover = getattr(request.app.state, 'background_remover', None)
    return {
        "status": "healthy",
        "model_loaded": background_remover is not None,
        "version": "1.0.0",
        "available_models": background_remover.get_available_models() if background_remover else []
    }


@router.post("/api/remove-background")
async def remove_background_api(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form("u2net"),
    enhancement: float = Form(1.0)
):
    """
    Remove background from uploaded image.
    
    Args:
        file: Uploaded image file (max 10MB)
        model: AI model to use
        enhancement: Edge enhancement strength (0.5-2.0)
        
    Returns:
        Processed image with background removed
    """
    background_remover = getattr(request.app.state, 'background_remover', None)
    if not background_remover:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    try:
        # Read and validate image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
            
        input_image = Image.open(BytesIO(image_data))
        
        # Validate dimensions
        if input_image.size[0] > 4096 or input_image.size[1] > 4096:
            raise HTTPException(status_code=400, detail="Image too large (max 4096x4096)")
        
        # Switch model if needed
        if model != background_remover.model_name:
            background_remover.switch_model(model)
        
        # Process image
        result = background_remover.remove_background(input_image)
        
        # Apply enhancement
        if enhancement != 1.0:
            enhancement = max(0.5, min(2.0, enhancement))
            result = background_remover.enhance_edges(result, enhancement)
        
        # Convert to bytes
        output_buffer = BytesIO()
        result.save(output_buffer, format="PNG", optimize=True)
        output_buffer.seek(0)
        
        return StreamingResponse(
            BytesIO(output_buffer.read()),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/api/batch")
async def batch_process(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """Process multiple images in batch."""
    background_remover = getattr(request.app.state, 'background_remover', None)
    if not background_remover:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed")
    
    results = []
    
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            results.append({
                "original_filename": file.filename,
                "status": "error",
                "error": "Not an image file"
            })
            continue
        
        try:
            image_data = await file.read()
            input_image = Image.open(BytesIO(image_data))
            result = background_remover.remove_background(input_image)
            
            # Save result
            file_id = str(uuid.uuid4())
            output_filename = f"batch_{file_id}.png"
            output_path = OUTPUT_DIR / output_filename
            result.save(output_path, format="PNG", optimize=True)
            
            results.append({
                "original_filename": file.filename,
                "output_filename": output_filename,
                "download_url": f"/api/download/{output_filename}",
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "original_filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results}


@router.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a processed file."""
    # Security check
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="image/png"
    )


@router.get("/api/models")
async def get_available_models(request: Request):
    """Get list of available AI models."""
    background_remover = getattr(request.app.state, 'background_remover', None)
    if not background_remover:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {
        "models": background_remover.get_available_models(),
        "current_model": background_remover.model_name,
        "descriptions": {
            "u2net": "General purpose - Good for most images",
            "u2netp": "Lightweight version - Faster processing", 
            "u2net_human_seg": "Optimized for people",
            "silueta": "High accuracy for objects",
            "isnet-general-use": "Latest model - Best quality"
        }
    }


# Background task for cleanup
async def cleanup_old_files():
    """Remove files older than 1 hour."""
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            for directory in [UPLOAD_DIR, OUTPUT_DIR]:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            file_path.unlink()
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception:
            await asyncio.sleep(3600)
