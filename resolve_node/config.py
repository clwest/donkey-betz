"""
Configuration for DaVinci Resolve Render Node

Session 103 - Resolve Render Node Service
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
JOBS_DIR = BASE_DIR / "jobs"
RESULTS_DIR = BASE_DIR / "results"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
JOBS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Server configuration
HOST = os.getenv("RENDER_NODE_HOST", "0.0.0.0")
PORT = int(os.getenv("RENDER_NODE_PORT", "5001"))

# Security
RENDER_NODE_TOKEN = os.getenv("RENDER_NODE_TOKEN", "dev-token-change-in-production")

# Django backend configuration
DJANGO_BACKEND_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")
DJANGO_COMPLETE_ENDPOINT = f"{DJANGO_BACKEND_URL}/api/v1/render/complete/"

# DaVinci Resolve settings
RESOLVE_PROJECT_NAME = os.getenv("RESOLVE_PROJECT_NAME", "RenderNode")
RESOLVE_TIMELINE_NAME = os.getenv("RESOLVE_TIMELINE_NAME", "Timeline 1")

# Render settings
DEFAULT_RENDER_SETTINGS = {
    "SelectAllFrames": True,
    "TargetDir": str(RESULTS_DIR),
    "CustomName": "render",
    "ExportVideo": True,
    "ExportAudio": True,
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": 24.0,
    "VideoQuality": 0,  # 0 = Automatic, 1-5 = Quality levels
    "AudioCodec": "aac",
    "AudioSampleRate": 48000,
    "VideoCodec": "h264",
    "EncodingProfile": "Main",
    "MultiPassEncode": False,
    "AlphaMode": 0,  # 0 = None
}

# Job queue settings
MAX_CONCURRENT_JOBS = 1  # Single render at a time for MVP
JOB_CHECK_INTERVAL = 2  # seconds
RENDER_TIMEOUT = 3600  # 1 hour max per job

# Upload retry settings
UPLOAD_MAX_RETRIES = 3
UPLOAD_RETRY_DELAY = 5  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "render_node.log"
