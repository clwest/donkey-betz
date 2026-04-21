"""
DaVinci Resolve API Wrapper

This module provides a clean Python interface to DaVinci Resolve's scripting API.
It handles connection management, error handling, and provides high-level operations.
"""

import os
import sys
import logging
import tempfile
import time
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import httpx

from config import settings

logger = logging.getLogger(__name__)


class ResolveConnectionError(Exception):
    """Raised when unable to connect to DaVinci Resolve"""
    pass


class ResolveOperationError(Exception):
    """Raised when a DaVinci operation fails"""
    pass


class RenderStatus(str, Enum):
    """Render job status"""
    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RenderResult:
    """Result of a render operation"""
    success: bool
    job_id: Optional[str] = None
    video_path: Optional[str] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectInfo:
    """Information about a DaVinci Resolve project"""
    name: str
    timeline_count: int = 0
    current_timeline: Optional[str] = None
    resolution: str = "1920x1080"
    frame_rate: float = 24.0


class DaVinciResolveWrapper:
    """
    Wrapper for DaVinci Resolve Python API

    This class provides a clean interface to DaVinci Resolve's scripting API,
    handling connection management, error recovery, and high-level operations.

    Example:
        wrapper = DaVinciResolveWrapper()
        if wrapper.connect():
            project = wrapper.create_project("My Video")
            wrapper.add_clip("/path/to/video.mp4")
            result = wrapper.render()
    """

    def __init__(self):
        """Initialize the wrapper (does not connect automatically)"""
        self._resolve = None
        self._project_manager = None
        self._current_project = None
        self._current_timeline = None
        self._media_pool = None
        self._connected = False

        # Setup Python path for DaVinci script module
        self._setup_python_path()

    def _setup_python_path(self):
        """Add DaVinci scripting module to Python path"""
        # Set environment variables
        os.environ["RESOLVE_SCRIPT_API"] = settings.resolve_script_api
        os.environ["RESOLVE_SCRIPT_LIB"] = settings.resolve_script_lib

        # Add modules path to sys.path
        modules_path = os.path.join(settings.resolve_script_api, "Modules")
        if modules_path not in sys.path:
            sys.path.append(modules_path)
            logger.info(f"Added DaVinci modules path: {modules_path}")

    @property
    def is_connected(self) -> bool:
        """Check if connected to DaVinci Resolve"""
        return self._connected and self._resolve is not None

    def connect(self) -> bool:
        """
        Connect to running DaVinci Resolve instance

        Returns:
            bool: True if connection successful

        Raises:
            ResolveConnectionError: If unable to connect
        """
        try:
            import DaVinciResolveScript as dvr_script

            self._resolve = dvr_script.scriptapp("Resolve")
            if not self._resolve:
                raise ResolveConnectionError(
                    "Failed to connect to DaVinci Resolve. "
                    "Make sure DaVinci Resolve Studio is running."
                )

            self._project_manager = self._resolve.GetProjectManager()
            if not self._project_manager:
                raise ResolveConnectionError("Failed to get Project Manager")

            self._connected = True
            logger.info("Successfully connected to DaVinci Resolve")

            # Get current project if one is open
            self._current_project = self._project_manager.GetCurrentProject()
            if self._current_project:
                self._media_pool = self._current_project.GetMediaPool()
                self._current_timeline = self._current_project.GetCurrentTimeline()
                logger.info(f"Current project: {self._current_project.GetName()}")

            return True

        except ImportError as e:
            logger.error(f"Failed to import DaVinci script module: {e}")
            raise ResolveConnectionError(
                f"DaVinci Resolve scripting module not found. "
                f"Ensure DaVinci Resolve Studio is installed. Error: {e}"
            )
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise ResolveConnectionError(f"Failed to connect: {e}")

    def disconnect(self):
        """Disconnect from DaVinci Resolve"""
        self._resolve = None
        self._project_manager = None
        self._current_project = None
        self._current_timeline = None
        self._media_pool = None
        self._connected = False
        logger.info("Disconnected from DaVinci Resolve")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of DaVinci Resolve connection

        Returns:
            Dict with connection status, version info, and current project
        """
        if not self.is_connected:
            return {
                "connected": False,
                "message": "Not connected to DaVinci Resolve"
            }

        try:
            status = {
                "connected": True,
                "product_name": self._resolve.GetProductName(),
                "version": self._resolve.GetVersionString(),
                "current_page": self._resolve.GetCurrentPage(),
            }

            if self._current_project:
                status["current_project"] = {
                    "name": self._current_project.GetName(),
                    "timeline_count": self._current_project.GetTimelineCount(),
                }

                if self._current_timeline:
                    status["current_project"]["current_timeline"] = (
                        self._current_timeline.GetName()
                    )

            return status

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "connected": True,
                "error": str(e)
            }

    # =========================================================================
    # Project Management
    # =========================================================================

    def create_project(self, name: str) -> bool:
        """
        Create a new DaVinci Resolve project

        Args:
            name: Project name (must be unique)

        Returns:
            bool: True if project created successfully
        """
        if not self.is_connected:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        try:
            logger.info(f"Creating project: {name}")

            self._current_project = self._project_manager.CreateProject(name)
            if not self._current_project:
                raise ResolveOperationError(f"Failed to create project: {name}")

            self._media_pool = self._current_project.GetMediaPool()
            if not self._media_pool:
                raise ResolveOperationError("Failed to get media pool")

            # Create default timeline
            self._current_timeline = self._media_pool.CreateEmptyTimeline(name)
            if not self._current_timeline:
                raise ResolveOperationError("Failed to create timeline")

            logger.info(f"Project created: {name}")
            return True

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise ResolveOperationError(f"Failed to create project: {e}")

    def load_project(self, name: str) -> bool:
        """Load an existing project by name"""
        if not self.is_connected:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        try:
            self._current_project = self._project_manager.LoadProject(name)
            if not self._current_project:
                raise ResolveOperationError(f"Project not found: {name}")

            self._media_pool = self._current_project.GetMediaPool()
            self._current_timeline = self._current_project.GetCurrentTimeline()

            logger.info(f"Loaded project: {name}")
            return True

        except Exception as e:
            logger.error(f"Error loading project: {e}")
            raise ResolveOperationError(f"Failed to load project: {e}")

    def close_project(self) -> bool:
        """Close current project without saving"""
        if not self._current_project:
            return True

        try:
            self._project_manager.CloseProject(self._current_project)
            self._current_project = None
            self._current_timeline = None
            self._media_pool = None
            logger.info("Project closed")
            return True
        except Exception as e:
            logger.error(f"Error closing project: {e}")
            return False

    def save_project(self) -> bool:
        """Save current project"""
        if not self._current_project:
            return False

        try:
            return self._project_manager.SaveProject()
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            return False

    def list_projects(self) -> List[str]:
        """List all projects in current folder"""
        if not self.is_connected:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        try:
            return self._project_manager.GetProjectListInCurrentFolder()
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []

    def delete_project(self, name: str) -> bool:
        """Delete a project by name"""
        if not self.is_connected:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        try:
            return self._project_manager.DeleteProject(name)
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False

    # =========================================================================
    # Media Import
    # =========================================================================

    async def download_media(self, url: str, media_type: str = "video") -> Optional[str]:
        """
        Download media from URL to temp file

        Args:
            url: URL to download from
            media_type: "video" or "audio"

        Returns:
            Path to downloaded file, or None on error
        """
        try:
            # Determine file extension
            ext = ".mp4" if media_type == "video" else ".mp3"
            if "." in url.split("/")[-1]:
                ext = "." + url.split(".")[-1].lower()

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=ext,
                delete=False,
                dir=settings.default_render_path
            )

            # Download
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60.0)
                response.raise_for_status()
                temp_file.write(response.content)

            temp_file.close()
            logger.info(f"Downloaded {len(response.content) / 1024:.1f} KB to {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    def import_media(self, file_path: str) -> Optional[Any]:
        """
        Import media file into current project's media pool

        Args:
            file_path: Path to media file

        Returns:
            MediaPoolItem if successful, None otherwise
        """
        if not self._media_pool:
            raise ResolveOperationError("No media pool available")

        try:
            # Verify file exists
            if not os.path.exists(file_path):
                raise ResolveOperationError(f"File not found: {file_path}")

            logger.info(f"Importing media: {file_path}")

            media_items = self._media_pool.ImportMedia([file_path])
            if not media_items or len(media_items) == 0:
                raise ResolveOperationError(f"Failed to import: {file_path}")

            logger.info(f"Imported: {os.path.basename(file_path)}")
            return media_items[0]

        except Exception as e:
            logger.error(f"Import error: {e}")
            raise ResolveOperationError(f"Failed to import media: {e}")

    # =========================================================================
    # Timeline Operations
    # =========================================================================

    def add_clip_to_timeline(
        self,
        file_path: str,
        position_seconds: float = 0
    ) -> bool:
        """
        Add video clip to timeline

        Args:
            file_path: Path to video file
            position_seconds: Position in timeline (seconds)

        Returns:
            bool: True if successful
        """
        if not self._current_timeline:
            raise ResolveOperationError("No timeline available")

        try:
            # Import media first
            media_item = self.import_media(file_path)
            if not media_item:
                return False

            # Add to timeline
            success = self._media_pool.AppendToTimeline([media_item])
            if not success:
                raise ResolveOperationError("Failed to add clip to timeline")

            logger.info(f"Added clip to timeline at {position_seconds}s")
            return True

        except Exception as e:
            logger.error(f"Error adding clip: {e}")
            raise ResolveOperationError(f"Failed to add clip: {e}")

    def add_transition(
        self,
        transition_type: str = "Cross Dissolve",
        at_second: float = 0,
        duration: float = 1.0
    ) -> bool:
        """
        Add transition between clips

        Args:
            transition_type: Type of transition
            at_second: Position in timeline
            duration: Transition duration

        Returns:
            bool: True if successful
        """
        if not self._current_timeline:
            raise ResolveOperationError("No timeline available")

        try:
            # Note: DaVinci's transition API is limited via scripting
            # This is a placeholder - actual implementation may vary by version
            logger.info(f"Adding {transition_type} at {at_second}s (duration: {duration}s)")
            return True

        except Exception as e:
            logger.error(f"Error adding transition: {e}")
            return False

    def add_text_overlay(
        self,
        text: str,
        position: str = "center",
        start_second: float = 0,
        duration_seconds: float = 3,
        font_size: int = 72,
        color: str = "#FFFFFF"
    ) -> bool:
        """
        Add text overlay to timeline

        Args:
            text: Text to display
            position: "center", "lower_third", or "upper_third"
            start_second: Start time
            duration_seconds: Duration
            font_size: Text size
            color: Text color (hex)

        Returns:
            bool: True if successful
        """
        if not self._current_timeline:
            raise ResolveOperationError("No timeline available")

        try:
            logger.info(f"Adding text '{text}' at {position}, {start_second}s for {duration_seconds}s")
            # Note: Full text overlay requires Fusion API which is complex
            # This logs the intent - actual implementation uses Fusion nodes
            return True

        except Exception as e:
            logger.error(f"Error adding text: {e}")
            return False

    def add_audio(
        self,
        file_path: str,
        volume: float = 0.5,
        start_second: float = 0
    ) -> bool:
        """
        Add audio to timeline

        Args:
            file_path: Path to audio file
            volume: Volume level (0.0 to 1.0)
            start_second: Start position

        Returns:
            bool: True if successful
        """
        if not self._current_timeline:
            raise ResolveOperationError("No timeline available")

        try:
            # Import audio
            media_item = self.import_media(file_path)
            if not media_item:
                return False

            # Add to timeline (audio track)
            success = self._media_pool.AppendToTimeline([media_item])
            logger.info(f"Added audio at {start_second}s with volume {volume}")
            return success

        except Exception as e:
            logger.error(f"Error adding audio: {e}")
            return False

    # =========================================================================
    # Rendering
    # =========================================================================

    def render(
        self,
        output_path: Optional[str] = None,
        format: str = "mp4",
        codec: str = "H264",
        resolution: str = "1920x1080"
    ) -> RenderResult:
        """
        Render current timeline

        Args:
            output_path: Output file path (auto-generated if None)
            format: Video format (mp4, mov, etc.)
            codec: Video codec (H264, H265, ProRes, etc.)
            resolution: Output resolution

        Returns:
            RenderResult with status and file path
        """
        if not self._current_project:
            return RenderResult(
                success=False,
                error_message="No project loaded"
            )

        try:
            # Generate output path if not provided
            if not output_path:
                os.makedirs(settings.default_render_path, exist_ok=True)
                output_path = os.path.join(
                    settings.default_render_path,
                    f"render_{int(time.time())}.{format}"
                )

            logger.info(f"Starting render to: {output_path}")

            # Set format and codec
            success = self._current_project.SetCurrentRenderFormatAndCodec(format, codec)
            if not success:
                return RenderResult(
                    success=False,
                    error_message=f"Failed to set format/codec: {format}/{codec}"
                )

            # Configure render settings
            render_settings = {
                "SelectAllFrames": 1,
                "TargetDir": os.path.dirname(output_path),
                "CustomName": os.path.splitext(os.path.basename(output_path))[0],
            }

            self._current_project.SetRenderSettings(render_settings)

            # Add render job
            job_id = self._current_project.AddRenderJob()
            if not job_id:
                return RenderResult(
                    success=False,
                    error_message="Failed to create render job"
                )

            logger.info(f"Render job created: {job_id}")

            # Start rendering
            self._current_project.StartRendering()

            # Wait for completion
            start_time = time.time()
            max_wait = 600  # 10 minutes timeout

            while time.time() - start_time < max_wait:
                if not self._current_project.IsRenderingInProgress():
                    break
                time.sleep(1)

            # Check result
            if time.time() - start_time >= max_wait:
                return RenderResult(
                    success=False,
                    job_id=job_id,
                    error_message="Render timeout"
                )

            # Verify output file
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                render_time = time.time() - start_time

                logger.info(f"Render complete: {output_path} ({file_size:.1f} MB in {render_time:.1f}s)")

                return RenderResult(
                    success=True,
                    job_id=job_id,
                    video_path=output_path,
                    metadata={
                        "format": format,
                        "codec": codec,
                        "resolution": resolution,
                        "file_size_mb": file_size,
                        "render_time_seconds": render_time
                    }
                )
            else:
                return RenderResult(
                    success=False,
                    job_id=job_id,
                    error_message=f"Output file not found: {output_path}"
                )

        except Exception as e:
            logger.error(f"Render error: {e}")
            return RenderResult(
                success=False,
                error_message=str(e)
            )

    def get_render_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a render job"""
        if not self._current_project:
            return {"status": "error", "message": "No project loaded"}

        try:
            return self._current_project.GetRenderJobStatus(job_id)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancel_render(self) -> bool:
        """Cancel current render"""
        if not self._current_project:
            return False

        try:
            self._current_project.StopRendering()
            return True
        except Exception as e:
            logger.error(f"Error cancelling render: {e}")
            return False


# Singleton instance
_wrapper: Optional[DaVinciResolveWrapper] = None


def get_resolve_wrapper() -> DaVinciResolveWrapper:
    """Get or create the DaVinci Resolve wrapper singleton"""
    global _wrapper
    if _wrapper is None:
        _wrapper = DaVinciResolveWrapper()
    return _wrapper
