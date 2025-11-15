"""
DaVinci Resolve Controller

Session 103 - Resolve Render Node Service
Handles all interactions with DaVinci Resolve Python API
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import config
from utils import logger


class ResolveController:
    """Controls DaVinci Resolve via Python API"""

    def __init__(self, mock_mode: bool = False):
        """
        Initialize Resolve controller

        Args:
            mock_mode: If True, run in mock mode without actual Resolve connection
        """
        self.mock_mode = mock_mode
        self.resolve = None
        self.project_manager = None
        self.project = None
        self.media_pool = None
        self.current_timeline = None

        if not mock_mode:
            self._load_resolve()

    def _load_resolve(self):
        """Load DaVinci Resolve API"""
        try:
            # Add Resolve's script lib to Python path
            # Typical locations on macOS
            resolve_script_paths = [
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
                "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/Modules",
            ]

            for path in resolve_script_paths:
                if os.path.exists(path) and path not in sys.path:
                    sys.path.append(path)

            # Import Resolve script module
            try:
                import DaVinciResolveScript as dvr_script
            except ImportError:
                logger.error("DaVinciResolveScript module not found")
                raise RuntimeError("DaVinci Resolve Python API not available")

            # Get Resolve instance
            self.resolve = dvr_script.scriptapp("Resolve")
            if not self.resolve:
                raise RuntimeError("Could not connect to DaVinci Resolve")

            logger.info("Successfully connected to DaVinci Resolve")

            # Get project manager
            self.project_manager = self.resolve.GetProjectManager()
            if not self.project_manager:
                raise RuntimeError("Could not get Project Manager")

            # Get or create project
            self._get_or_create_project(config.RESOLVE_PROJECT_NAME)

            # Get media pool
            self.media_pool = self.project.GetMediaPool()
            if not self.media_pool:
                raise RuntimeError("Could not get Media Pool")

            logger.info(f"Initialized Resolve with project: {config.RESOLVE_PROJECT_NAME}")

        except Exception as e:
            logger.error(f"Failed to initialize Resolve: {e}")
            raise

    def _get_or_create_project(self, project_name: str):
        """Get existing project or create new one"""
        # Try to load existing project
        self.project = self.project_manager.LoadProject(project_name)

        if not self.project:
            # Create new project
            logger.info(f"Creating new project: {project_name}")
            self.project = self.project_manager.CreateProject(project_name)

        if not self.project:
            raise RuntimeError(f"Could not create/load project: {project_name}")

        logger.info(f"Using project: {project_name}")

    def import_media(self, clip_paths: List[str]) -> bool:
        """
        Import media files into media pool

        Args:
            clip_paths: List of file paths to import

        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            logger.info(f"[MOCK] Would import {len(clip_paths)} clips")
            return True

        try:
            if not clip_paths:
                logger.warning("No clip paths provided for import")
                return True

            # Convert to absolute paths
            abs_paths = [str(Path(p).resolve()) for p in clip_paths if Path(p).exists()]

            if not abs_paths:
                logger.warning("No valid clip paths found")
                return False

            # Import to media pool
            imported_clips = self.media_pool.ImportMedia(abs_paths)

            if imported_clips:
                logger.info(f"Imported {len(imported_clips)} clips to media pool")
                return True
            else:
                logger.warning("Failed to import clips (returned None)")
                return False

        except Exception as e:
            logger.error(f"Failed to import media: {e}")
            return False

    def set_or_create_timeline(self, timeline_name: Optional[str] = None) -> bool:
        """
        Set current timeline or create new one

        Args:
            timeline_name: Name of timeline to use/create

        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            logger.info(f"[MOCK] Would set/create timeline: {timeline_name or 'default'}")
            self.current_timeline = {"name": timeline_name or "Timeline 1"}
            return True

        try:
            if not timeline_name:
                timeline_name = config.RESOLVE_TIMELINE_NAME

            # Try to get existing timeline
            self.current_timeline = self.project.GetTimelineByIndex(1)

            if not self.current_timeline:
                # Create new timeline
                logger.info(f"Creating new timeline: {timeline_name}")
                self.current_timeline = self.media_pool.CreateEmptyTimeline(timeline_name)

            if not self.current_timeline:
                raise RuntimeError(f"Could not create/get timeline: {timeline_name}")

            # Set as current timeline
            self.project.SetCurrentTimeline(self.current_timeline)

            logger.info(f"Using timeline: {self.current_timeline.GetName()}")
            return True

        except Exception as e:
            logger.error(f"Failed to set/create timeline: {e}")
            return False

    def configure_render_settings(self, job_id: str, template: str = "default_mp4") -> Dict[str, Any]:
        """
        Configure render settings for the job

        Args:
            job_id: Job ID for filename
            template: Render template name

        Returns:
            Render settings dictionary
        """
        # Start with default settings
        settings = config.DEFAULT_RENDER_SETTINGS.copy()

        # Customize filename with job ID
        settings["CustomName"] = f"render_{job_id}"

        # Template-specific settings (future expansion)
        if template == "high_quality":
            settings["VideoQuality"] = 5
            settings["MultiPassEncode"] = True

        return settings

    def start_render(self, job_id: str, template: str = "default_mp4") -> Optional[str]:
        """
        Start render job

        Args:
            job_id: Job ID
            template: Render template name

        Returns:
            Output file path if successful, None otherwise
        """
        if self.mock_mode:
            output_file = config.RESULTS_DIR / f"render_{job_id}.mp4"
            logger.info(f"[MOCK] Would render to: {output_file}")
            # Create a dummy file for testing
            output_file.touch()
            return str(output_file)

        try:
            if not self.current_timeline:
                raise RuntimeError("No timeline set for rendering")

            # Configure render settings
            settings = self.configure_render_settings(job_id, template)

            # Apply settings
            logger.info(f"Applying render settings for job {job_id}")
            success = self.project.SetRenderSettings(settings)

            if not success:
                raise RuntimeError("Failed to apply render settings")

            # Add timeline to render queue
            success = self.project.AddRenderJob()
            if not success:
                raise RuntimeError("Failed to add render job to queue")

            # Start rendering
            logger.info(f"Starting render for job {job_id}")
            success = self.project.StartRendering()

            if not success:
                raise RuntimeError("Failed to start rendering")

            # Construct expected output path
            output_file = config.RESULTS_DIR / f"{settings['CustomName']}.mp4"

            logger.info(f"Render started for job {job_id}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to start render: {e}")
            return None

    def get_render_status(self) -> Dict[str, Any]:
        """
        Get current render status

        Returns:
            Dictionary with status information
        """
        if self.mock_mode:
            return {
                "is_rendering": False,
                "progress": 100.0,
                "status": "done"
            }

        try:
            is_rendering = self.project.IsRenderingInProgress()

            if is_rendering:
                # Try to get progress (may not be available on all Resolve versions)
                # progress = self.project.GetRenderJobStatus(1).get("CompletionPercentage", 0)
                progress = 50.0  # Placeholder - actual progress tracking varies by Resolve version
                status = "rendering"
            else:
                progress = 100.0
                status = "done"

            return {
                "is_rendering": is_rendering,
                "progress": progress,
                "status": status
            }

        except Exception as e:
            logger.error(f"Failed to get render status: {e}")
            return {
                "is_rendering": False,
                "progress": 0.0,
                "status": "error",
                "error": str(e)
            }

    def wait_for_render_complete(self, timeout: int = 3600) -> bool:
        """
        Wait for render to complete

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if completed successfully, False if timeout/error
        """
        if self.mock_mode:
            logger.info("[MOCK] Render completed immediately")
            return True

        import time
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                status = self.get_render_status()

                if not status["is_rendering"]:
                    logger.info("Render completed")
                    return True

                # Wait before checking again
                time.sleep(config.JOB_CHECK_INTERVAL)

            logger.error(f"Render timeout after {timeout} seconds")
            return False

        except Exception as e:
            logger.error(f"Error waiting for render: {e}")
            return False
