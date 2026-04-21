"""
DaVinci Resolve Bridge Server

A FastAPI microservice that bridges web applications with DaVinci Resolve Studio.

Usage:
    python server.py
    # or
    uvicorn server:app --reload --host 0.0.0.0 --port 9090
"""

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config import settings
from resolve_wrapper import (
    get_resolve_wrapper,
    DaVinciResolveWrapper,
    ResolveConnectionError,
    ResolveOperationError,
    RenderResult
)

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class StatusResponse(BaseModel):
    """DaVinci connection status response"""
    connected: bool
    product_name: Optional[str] = None
    version: Optional[str] = None
    current_page: Optional[str] = None
    current_project: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class CreateProjectRequest(BaseModel):
    """Request to create a new project"""
    name: str = Field(..., description="Project name")


class ProjectResponse(BaseModel):
    """Project information response"""
    success: bool
    name: str
    message: Optional[str] = None


class AddClipRequest(BaseModel):
    """Request to add a clip to timeline"""
    file_path: Optional[str] = None
    url: Optional[str] = None
    position_seconds: float = 0


class AddTransitionRequest(BaseModel):
    """Request to add a transition"""
    transition_type: str = "Cross Dissolve"
    at_second: float = 0
    duration: float = 1.0


class AddTextRequest(BaseModel):
    """Request to add text overlay"""
    text: str
    position: str = "center"
    start_second: float = 0
    duration_seconds: float = 3
    font_size: int = 72
    color: str = "#FFFFFF"


class AddAudioRequest(BaseModel):
    """Request to add audio"""
    file_path: Optional[str] = None
    url: Optional[str] = None
    volume: float = 0.5
    start_second: float = 0


class RenderRequest(BaseModel):
    """Request to render project"""
    output_path: Optional[str] = None
    format: str = "mp4"
    codec: str = "H264"
    resolution: str = "1920x1080"


class RenderResponse(BaseModel):
    """Render result response"""
    success: bool
    job_id: Optional[str] = None
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChainVideosRequest(BaseModel):
    """Request to chain multiple videos"""
    video_urls: List[str]
    project_name: Optional[str] = None
    add_transitions: bool = True
    transition_duration: float = 1.0


class OperationResponse(BaseModel):
    """Generic operation response"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting DaVinci Bridge Server...")
    logger.info(f"Server will listen on {settings.bridge_host}:{settings.bridge_port}")

    # Create render directory
    os.makedirs(settings.default_render_path, exist_ok=True)

    # Try to connect to DaVinci Resolve
    wrapper = get_resolve_wrapper()
    try:
        wrapper.connect()
        logger.info("Connected to DaVinci Resolve on startup")
    except ResolveConnectionError as e:
        logger.warning(f"Could not connect to DaVinci Resolve on startup: {e}")
        logger.warning("Server will continue - connection will be attempted when needed")

    yield

    # Shutdown
    logger.info("Shutting down DaVinci Bridge Server...")
    wrapper.disconnect()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="DaVinci Resolve Bridge",
    description="REST API bridge for DaVinci Resolve Studio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Dependencies
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key for authentication"""
    if settings.api_key == "dev-key-change-in-production":
        # Dev mode - no auth required
        return True

    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return True


def get_wrapper() -> DaVinciResolveWrapper:
    """Get DaVinci Resolve wrapper with connection check"""
    wrapper = get_resolve_wrapper()

    if not wrapper.is_connected:
        try:
            wrapper.connect()
        except ResolveConnectionError as e:
            raise HTTPException(
                status_code=503,
                detail=f"DaVinci Resolve not available: {e}"
            )

    return wrapper


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/status", response_model=StatusResponse)
async def get_status(auth: bool = Depends(verify_api_key)):
    """Get DaVinci Resolve connection status"""
    wrapper = get_resolve_wrapper()

    if not wrapper.is_connected:
        try:
            wrapper.connect()
        except ResolveConnectionError as e:
            return StatusResponse(
                connected=False,
                message=f"Not connected: {e}"
            )

    status = wrapper.get_status()
    return StatusResponse(**status)


@app.post("/api/connect")
async def connect_to_resolve(auth: bool = Depends(verify_api_key)):
    """Attempt to connect to DaVinci Resolve"""
    wrapper = get_resolve_wrapper()

    if wrapper.is_connected:
        return {"success": True, "message": "Already connected"}

    try:
        wrapper.connect()
        return {"success": True, "message": "Connected to DaVinci Resolve"}
    except ResolveConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Project Endpoints
# ============================================================================

@app.get("/api/projects")
async def list_projects(
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """List all projects"""
    projects = wrapper.list_projects()
    return {"projects": projects}


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Create a new project"""
    try:
        success = wrapper.create_project(request.name)
        return ProjectResponse(
            success=success,
            name=request.name,
            message=f"Project '{request.name}' created"
        )
    except ResolveOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/projects/{name}/load", response_model=ProjectResponse)
async def load_project(
    name: str,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Load an existing project"""
    try:
        success = wrapper.load_project(name)
        return ProjectResponse(
            success=success,
            name=name,
            message=f"Project '{name}' loaded"
        )
    except ResolveOperationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/projects/close")
async def close_project(
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Close current project"""
    success = wrapper.close_project()
    return {"success": success}


@app.post("/api/projects/save")
async def save_project(
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Save current project"""
    success = wrapper.save_project()
    return {"success": success}


@app.delete("/api/projects/{name}")
async def delete_project(
    name: str,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Delete a project"""
    success = wrapper.delete_project(name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Could not delete project: {name}")
    return {"success": True, "message": f"Project '{name}' deleted"}


# ============================================================================
# Timeline Endpoints
# ============================================================================

@app.post("/api/timeline/add-clip", response_model=OperationResponse)
async def add_clip(
    request: AddClipRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Add a clip to timeline"""
    try:
        # Handle URL download if provided
        file_path = request.file_path
        if request.url and not file_path:
            file_path = await wrapper.download_media(request.url, "video")
            if not file_path:
                raise HTTPException(status_code=400, detail="Failed to download video")

        if not file_path:
            raise HTTPException(status_code=400, detail="Either file_path or url required")

        success = wrapper.add_clip_to_timeline(file_path, request.position_seconds)
        return OperationResponse(
            success=success,
            message=f"Clip added at {request.position_seconds}s"
        )

    except ResolveOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/timeline/add-transition", response_model=OperationResponse)
async def add_transition(
    request: AddTransitionRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Add a transition between clips"""
    success = wrapper.add_transition(
        request.transition_type,
        request.at_second,
        request.duration
    )
    return OperationResponse(
        success=success,
        message=f"Transition '{request.transition_type}' added at {request.at_second}s"
    )


@app.post("/api/timeline/add-text", response_model=OperationResponse)
async def add_text(
    request: AddTextRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Add text overlay to timeline"""
    success = wrapper.add_text_overlay(
        request.text,
        request.position,
        request.start_second,
        request.duration_seconds,
        request.font_size,
        request.color
    )
    return OperationResponse(
        success=success,
        message=f"Text '{request.text}' added"
    )


@app.post("/api/timeline/add-audio", response_model=OperationResponse)
async def add_audio(
    request: AddAudioRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Add audio to timeline"""
    try:
        # Handle URL download if provided
        file_path = request.file_path
        if request.url and not file_path:
            file_path = await wrapper.download_media(request.url, "audio")
            if not file_path:
                raise HTTPException(status_code=400, detail="Failed to download audio")

        if not file_path:
            raise HTTPException(status_code=400, detail="Either file_path or url required")

        success = wrapper.add_audio(file_path, request.volume, request.start_second)
        return OperationResponse(
            success=success,
            message=f"Audio added with volume {request.volume}"
        )

    except ResolveOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Render Endpoints
# ============================================================================

@app.post("/api/render/start", response_model=RenderResponse)
async def start_render(
    request: RenderRequest,
    background_tasks: BackgroundTasks,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Start rendering the current project"""
    try:
        result = wrapper.render(
            request.output_path,
            request.format,
            request.codec,
            request.resolution
        )

        return RenderResponse(
            success=result.success,
            job_id=result.job_id,
            video_path=result.video_path,
            duration=result.duration,
            error_message=result.error_message,
            metadata=result.metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/render/status/{job_id}")
async def get_render_status(
    job_id: str,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Get status of a render job"""
    status = wrapper.get_render_status(job_id)
    return status


@app.post("/api/render/cancel")
async def cancel_render(
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """Cancel current render"""
    success = wrapper.cancel_render()
    return {"success": success}


# ============================================================================
# High-Level Video Operations
# ============================================================================

@app.post("/api/video/chain", response_model=RenderResponse)
async def chain_videos(
    request: ChainVideosRequest,
    auth: bool = Depends(verify_api_key),
    wrapper: DaVinciResolveWrapper = Depends(get_wrapper)
):
    """
    Chain multiple videos together

    This is a high-level operation that:
    1. Creates a new project
    2. Downloads and imports all videos
    3. Adds them to timeline with optional transitions
    4. Renders the final video
    """
    try:
        project_name = request.project_name or f"Chained_{int(datetime.now().timestamp())}"

        # Create project
        wrapper.create_project(project_name)

        # Download and add each video
        position = 0
        for i, url in enumerate(request.video_urls):
            logger.info(f"Processing video {i+1}/{len(request.video_urls)}: {url[:50]}...")

            # Download
            file_path = await wrapper.download_media(url, "video")
            if not file_path:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to download video {i+1}"
                )

            # Add to timeline
            wrapper.add_clip_to_timeline(file_path, position)
            position += 8  # Assume 8 seconds per clip

            # Add transition (except for first clip)
            if request.add_transitions and i > 0:
                wrapper.add_transition(
                    "Cross Dissolve",
                    position - request.transition_duration,
                    request.transition_duration
                )

        # Render
        result = wrapper.render()

        return RenderResponse(
            success=result.success,
            job_id=result.job_id,
            video_path=result.video_path,
            duration=result.duration,
            error_message=result.error_message,
            metadata={
                **(result.metadata or {}),
                "video_count": len(request.video_urls),
                "project_name": project_name
            }
        )

    except Exception as e:
        logger.error(f"Chain videos error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# File Serving
# ============================================================================

@app.get("/api/files/{filename}")
async def serve_file(
    filename: str,
    auth: bool = Depends(verify_api_key)
):
    """Serve rendered video files"""
    file_path = os.path.join(settings.default_render_path, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           DaVinci Resolve Bridge Server                      ║
║                                                              ║
║  Starting on http://{settings.bridge_host}:{settings.bridge_port}                          ║
║                                                              ║
║  Make sure DaVinci Resolve Studio is running!                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "server:app",
        host=settings.bridge_host,
        port=settings.bridge_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
