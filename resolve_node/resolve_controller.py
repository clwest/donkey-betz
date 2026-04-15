"""
import logging
logger = logging.getLogger(__name__)

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
        self.imported_clips = []  # Session 479: Store imported clips for timeline

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
        # Session 479: Close current project first if any
        current = self.project_manager.GetCurrentProject()
        if current:
            current_name = current.GetName()
            logger.info(f"Closing current project: {current_name}")
            # Save first to avoid blocking dialog
            try:
                self.project_manager.SaveProject()
            except:
                pass  # May fail if no changes
            self.project_manager.CloseProject(current)

        # Try to load existing project
        self.project = self.project_manager.LoadProject(project_name)

        if not self.project:
            # Create new project
            logger.info(f"Creating new project: {project_name}")
            self.project = self.project_manager.CreateProject(project_name)

        if not self.project:
            # Last resort: use any available project or create with random name
            logger.warning(f"Could not create '{project_name}', trying fallback...")
            import uuid
            fallback_name = f"RenderJob_{uuid.uuid4().hex[:8]}"
            self.project = self.project_manager.CreateProject(fallback_name)
            if self.project:
                project_name = fallback_name
                logger.info(f"Using fallback project name: {fallback_name}")

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
            self.imported_clips = ["mock_clip"]  # Mock clip for testing
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
                # Session 479: Store imported clips for adding to timeline
                self.imported_clips = imported_clips
                return True
            else:
                logger.warning("Failed to import clips (returned None)")
                return False

        except Exception as e:
            logger.error(f"Failed to import media: {e}")
            return False

    def set_or_create_timeline(self, timeline_name: Optional[str] = None) -> bool:
        """
        Set current timeline or create new one, adding imported clips if available

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

            # Session 479: If we have imported clips, add them to timeline
            if self.imported_clips:
                logger.info(f"Setting up timeline with {len(self.imported_clips)} clips")

                # Create or get timeline first
                self.current_timeline = self.project.GetTimelineByIndex(1)
                if not self.current_timeline:
                    logger.info(f"Creating new timeline: {timeline_name}")
                    self.current_timeline = self.media_pool.CreateEmptyTimeline(timeline_name)

                if self.current_timeline:
                    # Set as current timeline
                    self.project.SetCurrentTimeline(self.current_timeline)

                    # Session 479: AppendToTimeline can be finicky, try multiple approaches
                    logger.info(f"Appending {len(self.imported_clips)} clips to timeline...")

                    # Log clip info
                    for i, clip in enumerate(self.imported_clips):
                        try:
                            clip_name = clip.GetName() if hasattr(clip, 'GetName') else str(clip)
                            logger.info(f"  Clip {i}: {clip_name}")
                        except:
                            logger.info(f"  Clip {i}: (could not get name)")

                    # Try AppendToTimeline with list format
                    result = self.media_pool.AppendToTimeline(self.imported_clips)
                    logger.info(f"AppendToTimeline result: {result}")

                    # Check if clips were actually added
                    items_on_track = self.current_timeline.GetItemListInTrack("video", 1)
                    if items_on_track:
                        logger.info(f"Timeline now has {len(items_on_track)} items on video track 1")
                    else:
                        # Fallback: Try individual clips with different append method
                        logger.warning("AppendToTimeline didn't work, trying individual clips...")
                        for clip in self.imported_clips:
                            try:
                                # Try appending as a list of one
                                self.media_pool.AppendToTimeline([clip])
                            except Exception as e:
                                logger.warning(f"Individual append failed: {e}")

                        # Check again
                        items_on_track = self.current_timeline.GetItemListInTrack("video", 1)
                        if items_on_track:
                            logger.info(f"Individual append worked! {len(items_on_track)} items on timeline")
                        else:
                            # Last resort: Create a new timeline from clips with unique name
                            logger.warning("AppendToTimeline failed, trying CreateTimelineFromClips...")
                            import uuid
                            unique_id = uuid.uuid4().hex[:8]
                            new_timeline_name = f"Render_{unique_id}"
                            new_timeline = self.media_pool.CreateTimelineFromClips(
                                new_timeline_name,
                                self.imported_clips
                            )
                            if new_timeline:
                                self.current_timeline = new_timeline
                                self.project.SetCurrentTimeline(self.current_timeline)
                                logger.info(f"Created new timeline '{new_timeline_name}' with clips")
                            else:
                                logger.error("Could not add clips to any timeline!")
                else:
                    raise RuntimeError(f"Could not create timeline: {timeline_name}")
            else:
                # No clips - just get existing timeline or create empty one
                self.current_timeline = self.project.GetTimelineByIndex(1)
                if not self.current_timeline:
                    logger.info(f"Creating new empty timeline: {timeline_name}")
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
            custom_name = f"render_{job_id}"

            # Session 479: Must load a render preset or set format before AddRenderJob works
            logger.info(f"Configuring render settings for job {job_id}")

            # Try to load a common render preset first
            presets_to_try = [
                "H.264 Master",
                "YouTube - 1080p",
                "YouTube 1080p",
                "Vimeo 1080p",
                "ProRes 422",
                "H.264 High Quality",
            ]

            preset_loaded = False
            for preset_name in presets_to_try:
                try:
                    success = self.project.LoadRenderPreset(preset_name)
                    if success:
                        logger.info(f"Loaded render preset: {preset_name}")
                        preset_loaded = True
                        break
                except Exception as _e:
                    logger.warning(
                        "resolve_controller.start_render: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            if not preset_loaded:
                logger.warning("Could not load any preset, trying manual settings...")

            # Set output directory and filename
            try:
                render_settings = {
                    "TargetDir": str(config.RESULTS_DIR),
                    "CustomName": custom_name,
                    "SelectAllFrames": True,
                }
                success = self.project.SetRenderSettings(render_settings)
                if success:
                    logger.info("Applied render settings successfully")
                else:
                    logger.warning("SetRenderSettings returned False, continuing anyway...")
            except Exception as settings_error:
                logger.warning(f"Could not apply render settings: {settings_error}")

            # Add timeline to render queue
            logger.info("Adding timeline to render queue...")

            # Session 479: Check timeline state before adding job
            track_count = self.current_timeline.GetTrackCount("video")
            logger.info(f"Timeline video track count: {track_count}")

            # Check if timeline has any items
            timeline_item_count = self.current_timeline.GetItemListInTrack("video", 1)
            if timeline_item_count:
                logger.info(f"Timeline has {len(timeline_item_count)} items on video track 1")
            else:
                logger.warning("Timeline video track 1 appears empty!")

            # Try to add render job
            success = self.project.AddRenderJob()
            if not success:
                # Get more diagnostic info
                render_jobs = self.project.GetRenderJobs()
                logger.info(f"Current render jobs count: {len(render_jobs) if render_jobs else 0}")

                # Try to clear render queue and retry
                logger.warning("AddRenderJob failed, attempting to clear queue...")
                self.project.DeleteAllRenderJobs()

                # Try with in/out marks set to timeline bounds
                duration = self.current_timeline.GetEndFrame()
                logger.info(f"Timeline duration (frames): {duration}")

                success = self.project.AddRenderJob()
                if not success:
                    raise RuntimeError("Failed to add render job to queue")

            # Start rendering
            logger.info(f"Starting render for job {job_id}")
            success = self.project.StartRendering()

            if not success:
                raise RuntimeError("Failed to start rendering")

            # Session 479: Output format depends on preset, check for common extensions
            # H.264 Master uses .mov, others might use .mp4
            for ext in ['.mov', '.mp4', '.avi', '.mxf']:
                output_file = config.RESULTS_DIR / f"{custom_name}{ext}"
                if output_file.exists():
                    logger.info(f"Render started, output file: {output_file}")
                    return str(output_file)

            # If not found yet, return expected path (for polling)
            output_file = config.RESULTS_DIR / f"{custom_name}.mov"
            logger.info(f"Render started for job {job_id}, expected output: {output_file}")
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
