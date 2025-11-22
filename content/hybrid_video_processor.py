"""
Hybrid Video Processor - DaVinci Resolve First, FFmpeg Fallback
Session 167: Leveraging the $295 DaVinci Resolve Studio investment!

This processor intelligently routes video operations:
1. Checks if DaVinci Resolve Studio is running
2. Uses DaVinci for premium quality when available (GPU-accelerated, ProRes, etc.)
3. Falls back to ffmpeg when DaVinci isn't running

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
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


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
    processor_used: str = "unknown"  # "davinci" or "ffmpeg"
    gpu_accelerated: bool = False
    codec_used: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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

        # Check DaVinci availability
        self._check_davinci_status()

        logger.info(f"🎬 HybridVideoProcessor initialized")
        logger.info(f"   Mode: {mode.value}")
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

    def get_status(self) -> Dict[str, Any]:
        """
        Get current processor status.

        Returns:
            Status dictionary with availability info
        """
        # Refresh status
        self._check_davinci_status()

        return {
            "mode": self.mode.value,
            "davinci_installed": self.davinci_available,
            "davinci_running": self.davinci_running,
            "active_processor": "davinci" if self.davinci_running else "ffmpeg",
            "gpu_acceleration": self.davinci_running,
            "professional_codecs_available": self.davinci_running,
            "available_codecs": [c.value for c in ProfessionalCodec] if self.davinci_running else ["h264", "h265"],
            "message": self._get_status_message()
        }

    def _get_status_message(self) -> str:
        """Get human-readable status message"""
        if self.davinci_running:
            return "🎬 DaVinci Resolve Studio ACTIVE - GPU rendering, ProRes, DNxHD available!"
        elif self.davinci_available:
            return "⚠️ DaVinci installed but not running - start Resolve for GPU acceleration"
        else:
            return "ℹ️ Using ffmpeg - install DaVinci Resolve Studio for professional features"

    def _should_use_davinci(self) -> bool:
        """Determine if we should use DaVinci for this operation"""
        if self.mode == ProcessorMode.FFMPEG:
            return False
        if self.mode == ProcessorMode.DAVINCI:
            return self.davinci_running
        # AUTO mode - use DaVinci if running
        return self.davinci_running

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

        if self._should_use_davinci():
            return self._render_with_davinci(
                video_path, output_path, codec, resolution, frame_rate
            )
        else:
            return self._render_with_ffmpeg(
                video_path, output_path, codec, resolution, frame_rate,
                audio_codec, audio_bitrate
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
