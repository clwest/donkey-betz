"""
Hybrid Video Processor - DaVinci Resolve First, FFmpeg Fallback
Session 167: Leveraging the $295 DaVinci Resolve Studio investment!
Session 168: Connected to Render Node for proper DaVinci integration!

This processor intelligently routes video operations:
1. Checks if Render Node (port 5001) is available for DaVinci operations
2. Falls back to direct DaVinci API if render node unavailable but Resolve running
3. Falls back to ffmpeg when neither is available

Architecture (Session 168):
- Render Node (localhost:5001) handles DaVinci scripting properly
- Hybrid processor calls render node API for professional operations
- FFmpeg provides reliable fallback for all operations

Benefits of DaVinci-First:
- GPU-accelerated rendering (5-10x faster)
- Professional codecs (ProRes, DNxHD)
- Industry-leading color science
- LUT support
- Fusion effects

One person + AI Assistant + AI Agents = UNSTOPPABLE! 🚀
"""

import os
import logging
import subprocess
import tempfile
import time
import requests
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Render Node Configuration (Session 168)
RENDER_NODE_URL = os.getenv("RENDER_NODE_URL", "http://localhost:5001")
RENDER_NODE_TOKEN = os.getenv("RENDER_NODE_TOKEN", "dev-token-change-in-production")
RENDER_NODE_TIMEOUT = 5  # seconds for health check
RENDER_JOB_POLL_INTERVAL = 2  # seconds between status checks
RENDER_JOB_MAX_WAIT = 3600  # 1 hour max wait for render


class ProcessorMode(Enum):
    """Video processing mode"""
    DAVINCI = "davinci"      # Full DaVinci Resolve Studio
    FFMPEG = "ffmpeg"        # FFmpeg fallback
    AUTO = "auto"            # Auto-detect (DaVinci first, ffmpeg fallback)


class ProfessionalCodec(Enum):
    """Professional video codecs available via DaVinci"""
    PRORES_422 = "prores_422"           # Apple ProRes 422 (~150 Mbps)
    PRORES_422_HQ = "prores_422_hq"     # Apple ProRes 422 HQ (~220 Mbps)
    PRORES_4444 = "prores_4444"         # Apple ProRes 4444 (with alpha)
    DNXHD = "dnxhd"                      # Avid DNxHD
    DNXHR_HQ = "dnxhr_hq"               # Avid DNxHR HQ
    H264 = "h264"                        # Standard H.264
    H265 = "h265"                        # HEVC/H.265


@dataclass
class ProcessingResult:
    """Result from video processing operation"""
    success: bool
    output_path: Optional[str] = None
    processor_used: str = "unknown"  # "davinci" or "ffmpeg" or "render_node"
    gpu_accelerated: bool = False
    codec_used: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# SESSION 168: Render Node Client
# =============================================================================

class RenderNodeClient:
    """
    Client for communicating with the DaVinci Resolve Render Node (Session 103).

    The render node properly manages DaVinci projects, timelines, and rendering
    via the DaVinciResolveScript API. This client provides a clean interface
    for the hybrid processor to submit render jobs.
    """

    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize render node client.

        Args:
            base_url: Render node URL (default: localhost:5001)
            token: Authentication token
        """
        self.base_url = base_url or RENDER_NODE_URL
        self.token = token or RENDER_NODE_TOKEN
        self.headers = {"X-Render-Token": self.token}
        self._available = None

    def is_available(self) -> bool:
        """
        Check if render node is running and healthy.

        Returns:
            True if render node is available
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=RENDER_NODE_TIMEOUT
            )
            if response.status_code == 200:
                self._available = True
                logger.info("✅ Render Node is available at %s", self.base_url)
                return True
        except requests.exceptions.RequestException as e:
            logger.debug("Render Node not available: %s", e)

        self._available = False
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get render node status including queue info."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=RENDER_NODE_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass

        return {"status": "unavailable", "queue_size": 0, "active_jobs": 0}

    def start_render(
        self,
        clip_paths: list,
        template: str = "default_mp4",
        timeline_name: str = None,
        webhook_url: str = None
    ) -> Optional[str]:
        """
        Submit a render job to the render node.

        Args:
            clip_paths: List of video file paths to render
            template: Render template name
            timeline_name: Custom timeline name
            webhook_url: URL to notify when complete

        Returns:
            Job ID if successful, None otherwise
        """
        try:
            payload = {
                "clip_paths": clip_paths,
                "template": template
            }
            if timeline_name:
                payload["timeline_name"] = timeline_name
            if webhook_url:
                payload["webhook_url"] = webhook_url

            response = requests.post(
                f"{self.base_url}/render/start",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("🎬 Render job started: %s", data.get("job_id"))
                return data.get("job_id")
            else:
                logger.error("Failed to start render: %s", response.text)

        except requests.exceptions.RequestException as e:
            logger.error("Render node request failed: %s", e)

        return None

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a render job.

        Args:
            job_id: Job ID from start_render

        Returns:
            Job status dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/render/status/{job_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

        except requests.exceptions.RequestException as e:
            logger.error("Failed to get job status: %s", e)

        return {"status": "unknown", "error_message": "Failed to get status"}

    def wait_for_completion(
        self,
        job_id: str,
        max_wait: int = None,
        poll_interval: int = None
    ) -> Dict[str, Any]:
        """
        Wait for a render job to complete.

        Args:
            job_id: Job ID to wait for
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final job status
        """
        max_wait = max_wait or RENDER_JOB_MAX_WAIT
        poll_interval = poll_interval or RENDER_JOB_POLL_INTERVAL

        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = self.get_job_status(job_id)
            job_status = status.get("status", "unknown")

            if job_status in ("completed", "done", "failed", "cancelled"):
                return status

            logger.debug("Job %s status: %s (%.0f%% progress)",
                        job_id, job_status, status.get("progress", 0) * 100)
            time.sleep(poll_interval)

        return {"status": "timeout", "error_message": "Job timed out"}

    def download_result(self, job_id: str, output_path: str) -> bool:
        """
        Download the rendered result file.

        Args:
            job_id: Job ID
            output_path: Local path to save file

        Returns:
            True if download successful
        """
        try:
            response = requests.get(
                f"{self.base_url}/render/result/{job_id}",
                headers=self.headers,
                stream=True,
                timeout=300  # 5 minutes for large files
            )

            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info("✅ Downloaded render result to %s", output_path)
                return True
            else:
                logger.error("Failed to download result: %s", response.status_code)

        except requests.exceptions.RequestException as e:
            logger.error("Download failed: %s", e)

        return False


# Global render node client instance
_render_node_client: Optional[RenderNodeClient] = None

def get_render_node_client() -> RenderNodeClient:
    """Get or create the global render node client."""
    global _render_node_client
    if _render_node_client is None:
        _render_node_client = RenderNodeClient()
    return _render_node_client


class HybridVideoProcessor:
    """
    Intelligent video processor that uses DaVinci Resolve when available,
    falls back to ffmpeg otherwise.

    Session 167: Making the $295 investment COUNT!

    Usage:
        processor = HybridVideoProcessor()

        # Auto-detect best processor
        result = processor.render_professional(
            video_path="/path/to/video.mp4",
            codec=ProfessionalCodec.PRORES_422_HQ,
            output_path="/path/to/output.mov"
        )

        # Check what was used
        print(f"Rendered with: {result.processor_used}")
        print(f"GPU accelerated: {result.gpu_accelerated}")
    """

    def __init__(self, mode: ProcessorMode = ProcessorMode.AUTO):
        """
        Initialize the hybrid processor.

        Args:
            mode: Processing mode (AUTO recommended)
        """
        self.mode = mode
        self.davinci_available = False
        self.davinci_running = False
        self.davinci_provider = None

        # Session 168: Track render node availability
        self.render_node_available = False
        self.render_node_client = get_render_node_client()

        # Check DaVinci and render node availability
        self._check_davinci_status()
        self._check_render_node_status()

        logger.info(f"🎬 HybridVideoProcessor initialized")
        logger.info(f"   Mode: {mode.value}")
        logger.info(f"   Render Node: {'✅ AVAILABLE' if self.render_node_available else '❌ Not running'}")
        logger.info(f"   DaVinci installed: {self.davinci_available}")
        logger.info(f"   DaVinci running: {self.davinci_running}")

    def _check_davinci_status(self) -> Tuple[bool, bool]:
        """
        Check if DaVinci Resolve Studio is installed and running.

        Returns:
            Tuple of (installed, running)
        """
        # Check if DaVinci Resolve Script API is available
        try:
            import DaVinciResolveScript as dvr_script
            self.davinci_available = True

            # Try to connect to running instance
            resolve = dvr_script.scriptapp("Resolve")
            if resolve:
                self.davinci_running = True
                logger.info("✅ DaVinci Resolve Studio is RUNNING - GPU power available!")
            else:
                self.davinci_running = False
                logger.info("⚠️ DaVinci Resolve installed but not running")

        except ImportError:
            self.davinci_available = False
            self.davinci_running = False
            logger.info("ℹ️ DaVinci Resolve Studio not installed - using ffmpeg")
        except Exception as e:
            logger.warning(f"⚠️ DaVinci check error: {e}")
            self.davinci_running = False

        return self.davinci_available, self.davinci_running

    def _check_render_node_status(self) -> bool:
        """
        Check if the Render Node service is available.

        Session 168: The render node (Session 103) properly handles DaVinci
        scripting with project management, timelines, and job queues.

        Returns:
            True if render node is available
        """
        self.render_node_available = self.render_node_client.is_available()
        return self.render_node_available

    def get_status(self) -> Dict[str, Any]:
        """
        Get current processor status.

        Returns:
            Status dictionary with availability info
        """
        # Refresh status
        self._check_davinci_status()
        self._check_render_node_status()

        # Session 168: Determine active processor priority
        # 1. Render Node (best - proper DaVinci management)
        # 2. Direct DaVinci (fallback - may have issues)
        # 3. FFmpeg (always works)
        if self.render_node_available:
            active = "render_node"
            gpu = True
            pro_codecs = True
        elif self.davinci_running:
            active = "davinci"
            gpu = True
            pro_codecs = True
        else:
            active = "ffmpeg"
            gpu = False
            pro_codecs = False

        return {
            "mode": self.mode.value,
            "render_node_available": self.render_node_available,
            "davinci_installed": self.davinci_available,
            "davinci_running": self.davinci_running,
            "active_processor": active,
            "gpu_acceleration": gpu,
            "professional_codecs_available": pro_codecs,
            "available_codecs": [c.value for c in ProfessionalCodec] if pro_codecs else ["h264", "h265"],
            "message": self._get_status_message()
        }

    def _get_status_message(self) -> str:
        """Get human-readable status message"""
        if self.render_node_available:
            return "🎬 Render Node ACTIVE - Professional DaVinci rendering via API!"
        elif self.davinci_running:
            return "🎬 DaVinci Resolve Studio ACTIVE - GPU rendering, ProRes, DNxHD available!"
        elif self.davinci_available:
            return "⚠️ DaVinci installed but not running - start Resolve for GPU acceleration"
        else:
            return "ℹ️ Using ffmpeg - install DaVinci Resolve Studio for professional features"

    def _should_use_davinci(self) -> bool:
        """
        Determine if we should use DaVinci for this operation.

        Session 168: Priority order:
        1. Render Node (if available) - proper project/timeline management
        2. Direct DaVinci API (if running) - may have queue issues
        3. FFmpeg (fallback) - always works
        """
        if self.mode == ProcessorMode.FFMPEG:
            return False
        if self.mode == ProcessorMode.DAVINCI:
            return self.render_node_available or self.davinci_running
        # AUTO mode - prefer render node, then direct DaVinci
        return self.render_node_available or self.davinci_running

    def _should_use_render_node(self) -> bool:
        """Check if render node should be used (Session 168)"""
        if self.mode == ProcessorMode.FFMPEG:
            return False
        return self.render_node_available

    def _get_davinci_provider(self):
        """Get or create DaVinci provider instance"""
        if not self.davinci_provider:
            from content.davinci_provider import get_davinci_provider
            self.davinci_provider = get_davinci_provider()
        return self.davinci_provider

    # =========================================================================
    # PROFESSIONAL RENDERING
    # =========================================================================

    def render_professional(
        self,
        video_path: str,
        output_path: str,
        codec: ProfessionalCodec = ProfessionalCodec.PRORES_422_HQ,
        resolution: str = "1920x1080",
        frame_rate: int = 30,
        audio_codec: str = "aac",
        audio_bitrate: str = "320k"
    ) -> ProcessingResult:
        """
        Render video with professional codec.

        Uses DaVinci Resolve for true ProRes/DNxHD encoding when available,
        falls back to ffmpeg with best-effort encoding otherwise.

        Args:
            video_path: Input video file
            output_path: Output file path
            codec: Professional codec to use
            resolution: Output resolution (e.g., "1920x1080", "3840x2160")
            frame_rate: Output frame rate
            audio_codec: Audio codec
            audio_bitrate: Audio bitrate

        Returns:
            ProcessingResult with render details
        """
        logger.info(f"🎬 Professional render requested: {codec.value}")

        # Session 168: Priority order for rendering
        # 1. Render Node (best - proper DaVinci project management)
        if self._should_use_render_node():
            result = self._render_with_render_node(
                video_path, output_path, codec, resolution, frame_rate
            )
            if result.success:
                return result
            logger.warning("⚠️ Render node failed, trying direct DaVinci...")

        # 2. Direct DaVinci API (fallback - may have queue issues)
        if self._should_use_davinci() and not self._should_use_render_node():
            result = self._render_with_davinci(
                video_path, output_path, codec, resolution, frame_rate
            )
            if result.success:
                return result
            logger.warning("⚠️ Direct DaVinci failed, falling back to ffmpeg...")

        # 3. FFmpeg (always works)
        return self._render_with_ffmpeg(
            video_path, output_path, codec, resolution, frame_rate,
            audio_codec, audio_bitrate
        )

    def _render_with_render_node(
        self,
        video_path: str,
        output_path: str,
        codec: ProfessionalCodec,
        resolution: str,
        frame_rate: int
    ) -> ProcessingResult:
        """
        Render using the Render Node service (Session 168).

        The render node properly handles DaVinci project creation,
        timeline management, and job queuing.
        """
        logger.info("🎬 Using Render Node for professional DaVinci rendering")

        try:
            # Map codec to template name
            template_map = {
                ProfessionalCodec.PRORES_422: "prores_422",
                ProfessionalCodec.PRORES_422_HQ: "prores_422_hq",
                ProfessionalCodec.PRORES_4444: "prores_4444",
                ProfessionalCodec.DNXHD: "dnxhd",
                ProfessionalCodec.DNXHR_HQ: "dnxhr_hq",
                ProfessionalCodec.H264: "default_mp4",
                ProfessionalCodec.H265: "h265",
            }
            template = template_map.get(codec, "default_mp4")

            # Submit render job
            job_id = self.render_node_client.start_render(
                clip_paths=[video_path],
                template=template,
                timeline_name=f"render_{os.path.basename(video_path)}"
            )

            if not job_id:
                return ProcessingResult(
                    success=False,
                    processor_used="render_node",
                    error_message="Failed to start render job"
                )

            # Wait for completion
            logger.info(f"⏳ Waiting for render job {job_id}...")
            result = self.render_node_client.wait_for_completion(job_id)

            if result.get("status") in ("completed", "done"):
                # Download the result
                if self.render_node_client.download_result(job_id, output_path):
                    return ProcessingResult(
                        success=True,
                        output_path=output_path,
                        processor_used="render_node",
                        gpu_accelerated=True,
                        codec_used=codec.value,
                        metadata={
                            "job_id": job_id,
                            "render_node": RENDER_NODE_URL
                        }
                    )
                else:
                    return ProcessingResult(
                        success=False,
                        processor_used="render_node",
                        error_message="Failed to download render result"
                    )
            else:
                error_msg = result.get("error_message", "Unknown error")
                return ProcessingResult(
                    success=False,
                    processor_used="render_node",
                    error_message=f"Render job failed: {error_msg}"
                )

        except Exception as e:
            logger.error(f"❌ Render node error: {e}")
            return ProcessingResult(
                success=False,
                processor_used="render_node",
                error_message=str(e)
            )

    def _render_with_davinci(
        self,
        video_path: str,
        output_path: str,
        codec: ProfessionalCodec,
        resolution: str,
        frame_rate: int
    ) -> ProcessingResult:
        """Render using DaVinci Resolve Studio (GPU-accelerated)"""
        logger.info("🎬 Using DaVinci Resolve Studio for GPU-accelerated render")

        try:
            provider = self._get_davinci_provider()

            # Map codec to DaVinci format
            format_map = {
                ProfessionalCodec.PRORES_422: ("mov", "Apple ProRes 422"),
                ProfessionalCodec.PRORES_422_HQ: ("mov", "Apple ProRes 422 HQ"),
                ProfessionalCodec.PRORES_4444: ("mov", "Apple ProRes 4444"),
                ProfessionalCodec.DNXHD: ("mxf", "DNxHD"),
                ProfessionalCodec.DNXHR_HQ: ("mxf", "DNxHR HQ"),
                ProfessionalCodec.H264: ("mp4", "H264"),
                ProfessionalCodec.H265: ("mp4", "H265"),
            }

            fmt, codec_name = format_map.get(codec, ("mp4", "H264"))

            # Create project, import video, render
            project_name = f"render_{os.path.basename(video_path)}"
            provider.create_project(project_name)
            provider.import_video(video_path)

            result = provider.render_project(
                output_path=output_path,
                format=fmt,
                quality="high",
                resolution=resolution
            )

            if result.success:
                return ProcessingResult(
                    success=True,
                    output_path=result.video_path or output_path,
                    processor_used="davinci",
                    gpu_accelerated=True,
                    codec_used=codec_name,
                    duration_seconds=result.duration,
                    metadata={"davinci_project": project_name}
                )
            else:
                logger.warning(f"⚠️ DaVinci render failed: {result.error_message}")
                # Fall back to ffmpeg
                return self._render_with_ffmpeg(
                    video_path, output_path, codec, resolution, frame_rate,
                    "aac", "320k"
                )

        except Exception as e:
            logger.error(f"❌ DaVinci render error: {e}")
            # Fall back to ffmpeg
            return self._render_with_ffmpeg(
                video_path, output_path, codec, resolution, frame_rate,
                "aac", "320k"
            )

    def _render_with_ffmpeg(
        self,
        video_path: str,
        output_path: str,
        codec: ProfessionalCodec,
        resolution: str,
        frame_rate: int,
        audio_codec: str,
        audio_bitrate: str
    ) -> ProcessingResult:
        """Render using ffmpeg (CPU-based fallback)"""
        logger.info("🎬 Using ffmpeg for render (DaVinci not available)")

        try:
            # Map professional codecs to ffmpeg equivalents
            ffmpeg_codec_map = {
                ProfessionalCodec.PRORES_422: ("prores_ks", "-profile:v 2"),
                ProfessionalCodec.PRORES_422_HQ: ("prores_ks", "-profile:v 3"),
                ProfessionalCodec.PRORES_4444: ("prores_ks", "-profile:v 4"),
                ProfessionalCodec.DNXHD: ("dnxhd", "-b:v 185M"),
                ProfessionalCodec.DNXHR_HQ: ("dnxhd", "-profile:v dnxhr_hq"),
                ProfessionalCodec.H264: ("libx264", "-crf 18 -preset slow"),
                ProfessionalCodec.H265: ("libx265", "-crf 20 -preset slow"),
            }

            vcodec, vcodec_opts = ffmpeg_codec_map.get(
                codec, ("libx264", "-crf 18 -preset slow")
            )

            width, height = resolution.split("x")

            # Build ffmpeg command
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-c:v", vcodec,
            ]

            # Add codec-specific options
            cmd.extend(vcodec_opts.split())

            # Add resolution and frame rate
            cmd.extend([
                "-vf", f"scale={width}:{height}",
                "-r", str(frame_rate),
                "-c:a", audio_codec,
                "-b:a", audio_bitrate,
                output_path
            ])

            logger.info(f"🔧 FFmpeg command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                return ProcessingResult(
                    success=True,
                    output_path=output_path,
                    processor_used="ffmpeg",
                    gpu_accelerated=False,
                    codec_used=vcodec,
                    metadata={"ffmpeg_stderr": result.stderr[-500:] if result.stderr else None}
                )
            else:
                return ProcessingResult(
                    success=False,
                    processor_used="ffmpeg",
                    error_message=result.stderr[-500:] if result.stderr else "FFmpeg failed"
                )

        except subprocess.TimeoutExpired:
            return ProcessingResult(
                success=False,
                processor_used="ffmpeg",
                error_message="Render timed out (10 minutes)"
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                processor_used="ffmpeg",
                error_message=str(e)
            )

    # =========================================================================
    # LUT APPLICATION (DaVinci's Color Science!)
    # =========================================================================

    def apply_lut(
        self,
        video_path: str,
        lut_path: str,
        output_path: str,
        intensity: float = 1.0
    ) -> ProcessingResult:
        """
        Apply a LUT (Look-Up Table) to video.

        DaVinci Resolve has industry-leading color science for LUT application.
        Falls back to ffmpeg lut3d filter when DaVinci isn't available.

        Args:
            video_path: Input video
            lut_path: Path to .cube or .3dl LUT file
            output_path: Output video path
            intensity: LUT intensity (0.0-1.0, DaVinci only)

        Returns:
            ProcessingResult
        """
        logger.info(f"🎨 Applying LUT: {os.path.basename(lut_path)}")

        if self._should_use_davinci():
            return self._apply_lut_davinci(video_path, lut_path, output_path, intensity)
        else:
            return self._apply_lut_ffmpeg(video_path, lut_path, output_path)

    def _apply_lut_davinci(
        self,
        video_path: str,
        lut_path: str,
        output_path: str,
        intensity: float
    ) -> ProcessingResult:
        """Apply LUT using DaVinci Resolve's color science"""
        logger.info("🎨 Using DaVinci Resolve for professional LUT application")

        try:
            provider = self._get_davinci_provider()

            # Create project
            project_name = f"lut_{os.path.basename(video_path)}"
            provider.create_project(project_name)

            # Import video
            clip = provider.import_video(video_path)

            if clip and provider.current_project:
                # Get the color page
                resolve = provider.resolve
                if resolve:
                    # Apply LUT via scripting
                    # Note: Full LUT application requires timeline clip access
                    current_timeline = provider.current_project.GetCurrentTimeline()
                    if current_timeline:
                        # Get clips in timeline
                        clips = current_timeline.GetItemListInTrack("video", 1)
                        if clips and len(clips) > 0:
                            timeline_clip = clips[0]
                            # Apply LUT to clip
                            timeline_clip.SetLUT(1, lut_path)  # Node 1
                            logger.info(f"✅ LUT applied via DaVinci")

                # Render with LUT
                result = provider.render_project(output_path=output_path)

                if result.success:
                    return ProcessingResult(
                        success=True,
                        output_path=result.video_path or output_path,
                        processor_used="davinci",
                        gpu_accelerated=True,
                        metadata={"lut": os.path.basename(lut_path), "intensity": intensity}
                    )

            # Fall back to ffmpeg
            logger.warning("⚠️ DaVinci LUT application failed, using ffmpeg")
            return self._apply_lut_ffmpeg(video_path, lut_path, output_path)

        except Exception as e:
            logger.error(f"❌ DaVinci LUT error: {e}")
            return self._apply_lut_ffmpeg(video_path, lut_path, output_path)

    def _apply_lut_ffmpeg(
        self,
        video_path: str,
        lut_path: str,
        output_path: str
    ) -> ProcessingResult:
        """Apply LUT using ffmpeg lut3d filter"""
        logger.info("🎨 Using ffmpeg for LUT application")

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", f"lut3d={lut_path}",
                "-c:v", "libx264",
                "-crf", "18",
                "-c:a", "copy",
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                return ProcessingResult(
                    success=True,
                    output_path=output_path,
                    processor_used="ffmpeg",
                    gpu_accelerated=False,
                    metadata={"lut": os.path.basename(lut_path)}
                )
            else:
                return ProcessingResult(
                    success=False,
                    processor_used="ffmpeg",
                    error_message=result.stderr[-500:] if result.stderr else "LUT application failed"
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                processor_used="ffmpeg",
                error_message=str(e)
            )

    # =========================================================================
    # COLOR GRADING (DaVinci's Crown Jewel!)
    # =========================================================================

    def color_grade_professional(
        self,
        video_path: str,
        output_path: str,
        grade_type: str = "cinematic",
        lift: Tuple[float, float, float] = None,  # Shadows RGB
        gamma: Tuple[float, float, float] = None,  # Midtones RGB
        gain: Tuple[float, float, float] = None,   # Highlights RGB
        saturation: float = 1.0,
        contrast: float = 1.0
    ) -> ProcessingResult:
        """
        Professional color grading using DaVinci's color wheels.

        DaVinci Resolve is THE industry standard for color grading.
        Falls back to ffmpeg colorbalance when DaVinci isn't available.

        Args:
            video_path: Input video
            output_path: Output path
            grade_type: Preset type ("cinematic", "warm", "cool", "vintage", "custom")
            lift: Shadow color adjustment (R, G, B) - DaVinci only
            gamma: Midtone color adjustment (R, G, B) - DaVinci only
            gain: Highlight color adjustment (R, G, B) - DaVinci only
            saturation: Color saturation (0.0-2.0)
            contrast: Contrast adjustment (0.5-2.0)

        Returns:
            ProcessingResult
        """
        logger.info(f"🎨 Professional color grade: {grade_type}")

        if self._should_use_davinci():
            return self._color_grade_davinci(
                video_path, output_path, grade_type,
                lift, gamma, gain, saturation, contrast
            )
        else:
            return self._color_grade_ffmpeg(
                video_path, output_path, grade_type, saturation, contrast
            )

    def _color_grade_davinci(
        self,
        video_path: str,
        output_path: str,
        grade_type: str,
        lift: Tuple[float, float, float],
        gamma: Tuple[float, float, float],
        gain: Tuple[float, float, float],
        saturation: float,
        contrast: float
    ) -> ProcessingResult:
        """Color grade using DaVinci Resolve's color wheels"""
        logger.info("🎨 Using DaVinci Resolve for professional color grading")

        try:
            provider = self._get_davinci_provider()

            # Use existing color grading method
            project_name = f"grade_{os.path.basename(video_path)}"
            provider.create_project(project_name)
            provider.import_video(video_path)

            # Apply color grading
            provider.apply_color_grading(grade_type)

            # Render
            result = provider.render_project(output_path=output_path)

            if result.success:
                return ProcessingResult(
                    success=True,
                    output_path=result.video_path or output_path,
                    processor_used="davinci",
                    gpu_accelerated=True,
                    metadata={
                        "grade_type": grade_type,
                        "saturation": saturation,
                        "contrast": contrast
                    }
                )

            return self._color_grade_ffmpeg(
                video_path, output_path, grade_type, saturation, contrast
            )

        except Exception as e:
            logger.error(f"❌ DaVinci color grade error: {e}")
            return self._color_grade_ffmpeg(
                video_path, output_path, grade_type, saturation, contrast
            )

    def _color_grade_ffmpeg(
        self,
        video_path: str,
        output_path: str,
        grade_type: str,
        saturation: float,
        contrast: float
    ) -> ProcessingResult:
        """Color grade using ffmpeg filters"""
        logger.info("🎨 Using ffmpeg for color grading")

        # Grade presets
        grade_presets = {
            "cinematic": "eq=saturation=0.9:contrast=1.1,curves=preset=cross_process",
            "warm": "colorbalance=rs=0.1:gs=0.05:bs=-0.1,eq=saturation=1.1",
            "cool": "colorbalance=rs=-0.1:gs=0:bs=0.15,eq=saturation=0.95",
            "vintage": "eq=saturation=0.7:contrast=1.15,curves=preset=vintage",
            "vibrant": "eq=saturation=1.4:contrast=1.05",
            "noir": "eq=saturation=0:contrast=1.3",
        }

        filter_chain = grade_presets.get(grade_type, f"eq=saturation={saturation}:contrast={contrast}")

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", filter_chain,
                "-c:v", "libx264",
                "-crf", "18",
                "-c:a", "copy",
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                return ProcessingResult(
                    success=True,
                    output_path=output_path,
                    processor_used="ffmpeg",
                    gpu_accelerated=False,
                    metadata={"grade_type": grade_type}
                )
            else:
                return ProcessingResult(
                    success=False,
                    processor_used="ffmpeg",
                    error_message=result.stderr[-500:] if result.stderr else "Grading failed"
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                processor_used="ffmpeg",
                error_message=str(e)
            )


# Singleton instance
_hybrid_processor = None

def get_hybrid_processor() -> HybridVideoProcessor:
    """Get or create the hybrid video processor singleton"""
    global _hybrid_processor
    if _hybrid_processor is None:
        _hybrid_processor = HybridVideoProcessor()
    return _hybrid_processor
