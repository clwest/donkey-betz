"""
Utility functions for Render Node

Session 103 - Resolve Render Node Service
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import config


def setup_logging(log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_file: Optional path to log file
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("RenderNode")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    if not file_path.exists():
        return 0.0
    return file_path.stat().st_size / (1024 * 1024)


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


# Error response templates
ERROR_TEMPLATES = {
    "invalid_token": {
        "error": "Invalid or missing authentication token",
        "code": "AUTH_001",
        "message": "Please provide a valid X-Render-Token header"
    },
    "job_not_found": {
        "error": "Job not found",
        "code": "JOB_001",
        "message": "The requested job ID does not exist"
    },
    "render_failed": {
        "error": "Render failed",
        "code": "RENDER_001",
        "message": "The render job failed to complete"
    },
    "resolve_not_available": {
        "error": "DaVinci Resolve not available",
        "code": "RESOLVE_001",
        "message": "Cannot connect to DaVinci Resolve. Ensure it is running."
    },
    "upload_failed": {
        "error": "Upload failed",
        "code": "UPLOAD_001",
        "message": "Failed to upload results to backend"
    },
    "invalid_request": {
        "error": "Invalid request",
        "code": "REQ_001",
        "message": "The request payload is invalid or incomplete"
    }
}


def get_error_response(error_type: str, details: Optional[str] = None) -> dict:
    """
    Get formatted error response

    Args:
        error_type: Error type key from ERROR_TEMPLATES
        details: Optional additional details

    Returns:
        Error response dictionary
    """
    error = ERROR_TEMPLATES.get(error_type, {
        "error": "Unknown error",
        "code": "UNKNOWN",
        "message": str(details) if details else "An unknown error occurred"
    })

    if details:
        error["details"] = details

    return error


# Initialize logger
logger = setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
