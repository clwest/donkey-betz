"""
FastAPI Server for DaVinci Resolve Render Node

Session 103 - Resolve Render Node Service
Exposes REST API for render job management
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

import config
from models import RenderJob, JobStatus
from job_queue import JobQueue
from utils import logger, get_error_response


# Pydantic models for API
class RenderStartRequest(BaseModel):
    """Request model for starting a render"""
    timeline_name: Optional[str] = None
    clip_paths: List[str] = []
    template: str = "default_mp4"
    webhook_url: Optional[str] = None


class RenderStartResponse(BaseModel):
    """Response model for starting a render"""
    job_id: str
    status: str


class RenderStatusResponse(BaseModel):
    """Response model for render status"""
    job_id: str
    status: str
    progress: float
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = {}


# Create FastAPI app
app = FastAPI(
    title="DaVinci Resolve Render Node",
    description="REST API for managing DaVinci Resolve render jobs",
    version="1.0.0"
)

# Global job queue instance
job_queue: Optional[JobQueue] = None


@app.on_event("startup")
async def startup_event():
    """Initialize job queue on startup"""
    global job_queue

    logger.info("Starting Render Node API server")
    logger.info(f"Server: {config.HOST}:{config.PORT}")
    logger.info(f"Mock mode: {os.getenv('MOCK_MODE', 'false').lower() == 'true'}")

    # Check if running in mock mode
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"

    # Initialize job queue
    try:
        job_queue = JobQueue(mock_mode=mock_mode)
        job_queue.start()
        logger.info("Job queue initialized and started")
    except Exception as e:
        logger.error(f"Failed to initialize job queue: {e}")
        if not mock_mode:
            logger.error("Cannot continue without Resolve connection. Set MOCK_MODE=true for testing.")
            sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Stop job queue on shutdown"""
    global job_queue

    logger.info("Shutting down Render Node API server")

    if job_queue:
        job_queue.stop()


def verify_token(x_render_token: Optional[str] = Header(None)):
    """
    Verify authentication token

    Args:
        x_render_token: Token from X-Render-Token header

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not x_render_token or x_render_token != config.RENDER_NODE_TOKEN:
        raise HTTPException(
            status_code=401,
            detail=get_error_response("invalid_token")
        )


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "DaVinci Resolve Render Node",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "queue_size": job_queue.queue.qsize() if job_queue else 0,
        "active_jobs": len(job_queue.jobs) if job_queue else 0,
        "demo_mode": config.DEMO_MODE,
    }


def _enforce_demo_mode(clip_paths: List[str]):
    """Block clip paths that aren't inside demo_assets/ when RESOLVE_DEMO_MODE=true."""
    if not config.DEMO_MODE:
        return

    demo_dir = str(config.DEMO_ASSETS_DIR.resolve())
    allowed_prefixes = config.DEMO_ALLOWED_URL_PREFIXES

    for path in clip_paths:
        # Remote URL check
        if path.startswith(("http://", "https://")):
            if not any(path.startswith(prefix) for prefix in allowed_prefixes):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Demo mode: remote URL blocked",
                        "code": "DEMO_001",
                        "message": (
                            f"RESOLVE_DEMO_MODE is active. Remote URL '{path}' is not in the "
                            f"allowed prefixes: {allowed_prefixes or '(none)'}. "
                            f"Only local files in {demo_dir}/ are permitted."
                        ),
                    },
                )
            continue

        # Local path check — must resolve inside demo_assets/
        resolved = str(Path(path).resolve())
        if not resolved.startswith(demo_dir):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Demo mode: path outside demo_assets",
                    "code": "DEMO_002",
                    "message": (
                        f"RESOLVE_DEMO_MODE is active. Path '{path}' resolves to '{resolved}' "
                        f"which is outside the allowed directory: {demo_dir}/. "
                        f"Move your clip into demo_assets/ or disable demo mode."
                    ),
                },
            )


@app.post("/render/start", response_model=RenderStartResponse)
async def start_render(
    request: RenderStartRequest,
    x_render_token: Optional[str] = Header(None)
):
    """
    Start a new render job

    Args:
        request: Render job request
        x_render_token: Authentication token

    Returns:
        RenderStartResponse with job ID and status

    Raises:
        HTTPException: If authentication fails or request is invalid
    """
    # Verify token
    verify_token(x_render_token)

    # Session 1065: Demo mode guardrail
    _enforce_demo_mode(request.clip_paths)

    try:
        # Create render job
        job = RenderJob(
            timeline_name=request.timeline_name,
            clip_paths=request.clip_paths,
            template=request.template,
            webhook_url=request.webhook_url
        )

        # Add to queue
        job_queue.add_job(job)

        logger.info(f"Created render job {job.job_id}")

        return RenderStartResponse(
            job_id=job.job_id,
            status=job.status.value
        )

    except Exception as e:
        logger.error(f"Failed to start render: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_error_response("render_failed", str(e))
        )


@app.get("/render/status/{job_id}", response_model=RenderStatusResponse)
async def get_render_status(
    job_id: str,
    x_render_token: Optional[str] = Header(None)
):
    """
    Get render job status

    Args:
        job_id: Job ID
        x_render_token: Authentication token

    Returns:
        RenderStatusResponse with job status

    Raises:
        HTTPException: If authentication fails or job not found
    """
    # Verify token
    verify_token(x_render_token)

    # Get job
    job = job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=get_error_response("job_not_found")
        )

    return RenderStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        created_at=job.created_at.isoformat() if job.created_at else None,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        output_file=job.output_file,
        error_message=job.error_message,
        metadata=job.metadata
    )


@app.get("/render/result/{job_id}")
async def get_render_result(
    job_id: str,
    x_render_token: Optional[str] = Header(None)
):
    """
    Download render result file

    Args:
        job_id: Job ID
        x_render_token: Authentication token

    Returns:
        FileResponse with rendered video file

    Raises:
        HTTPException: If authentication fails, job not found, or render not complete
    """
    # Verify token
    verify_token(x_render_token)

    # Get job
    job = job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=get_error_response("job_not_found")
        )

    # Check if job is complete
    if job.status != JobStatus.DONE and job.status != JobStatus.UPLOADED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Render not complete",
                "code": "RENDER_002",
                "message": f"Job status is {job.status.value}, cannot download result"
            }
        )

    # Check if output file exists
    if not job.output_file or not Path(job.output_file).exists():
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Output file not found",
                "code": "FILE_001",
                "message": "The rendered output file does not exist"
            }
        )

    # Return file
    return FileResponse(
        path=job.output_file,
        media_type="video/mp4",
        filename=Path(job.output_file).name
    )


@app.get("/jobs")
async def list_jobs(x_render_token: Optional[str] = Header(None)):
    """
    List all jobs

    Args:
        x_render_token: Authentication token

    Returns:
        List of all jobs with their status

    Raises:
        HTTPException: If authentication fails
    """
    # Verify token
    verify_token(x_render_token)

    jobs_list = [
        {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "timeline_name": job.timeline_name
        }
        for job in job_queue.jobs.values()
    ]

    return {
        "total": len(jobs_list),
        "jobs": jobs_list
    }


def main():
    """Main entry point"""
    logger.info("="* 60)
    logger.info("DaVinci Resolve Render Node")
    logger.info("Session 103 - Resolve Render Node Service")
    logger.info("="* 60)
    logger.info(f"Host: {config.HOST}")
    logger.info(f"Port: {config.PORT}")
    logger.info(f"Results directory: {config.RESULTS_DIR}")
    logger.info(f"Logs directory: {config.LOGS_DIR}")
    logger.info("="* 60)

    # Start FastAPI server
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()
