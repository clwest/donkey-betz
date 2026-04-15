"""
DaVinci Bridge Client

This client connects to the DaVinci Bridge Server to perform video editing operations.
It replaces direct DaVinci Resolve API calls with HTTP requests to the bridge.

The bridge server can run on:
1. The same machine (localhost:9090) - for local development
2. A dedicated rendering machine - for production
3. Cloud instances - for scalability

Usage:
    from content.davinci_bridge_client import get_davinci_client

    client = get_davinci_client()
    if client.is_available():
        result = client.chain_videos([url1, url2, url3])
"""

import os
import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import httpx
from django.conf import settings as django_settings

logger = logging.getLogger(__name__)


# Default bridge URL - can be overridden in Django settings
DAVINCI_BRIDGE_URL = getattr(
    django_settings,
    'DAVINCI_BRIDGE_URL',
    os.environ.get('DAVINCI_BRIDGE_URL', 'http://localhost:9090')
)

DAVINCI_BRIDGE_API_KEY = getattr(
    django_settings,
    'DAVINCI_BRIDGE_API_KEY',
    os.environ.get('DAVINCI_BRIDGE_API_KEY', 'dev-key-change-in-production')
)


@dataclass
class DaVinciResult:
    """Result from a DaVinci operation"""
    success: bool
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    job_id: Optional[str] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DaVinciBridgeClient:
    """
    Client for the DaVinci Bridge Server

    This client provides the same interface as the old DaVinciResolveProvider
    but communicates via HTTP to the bridge server instead of directly
    calling the DaVinci Resolve API.

    Example:
        client = DaVinciBridgeClient()

        # Check if bridge is available
        if client.is_available():
            # Chain videos
            result = client.chain_videos([
                "http://example.com/video1.mp4",
                "http://example.com/video2.mp4"
            ])

            if result.success:
                print(f"Video created: {result.video_path}")
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the bridge client

        Args:
            base_url: Bridge server URL (default: from settings)
            api_key: API key for authentication (default: from settings)
        """
        self.base_url = (base_url or DAVINCI_BRIDGE_URL).rstrip('/')
        self.api_key = api_key or DAVINCI_BRIDGE_API_KEY
        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _get_client(self) -> httpx.Client:
        """Get or create sync HTTP client"""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self.headers,
                timeout=300.0  # 5 minute timeout for render operations
            )
        return self._client

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=300.0
            )
        return self._async_client

    def close(self):
        """Close HTTP clients"""
        if self._client:
            self._client.close()
            self._client = None

    async def aclose(self):
        """Close async HTTP client"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    # =========================================================================
    # Status & Health
    # =========================================================================

    def is_available(self) -> bool:
        """
        Check if DaVinci Bridge is available and connected to Resolve

        Returns:
            bool: True if bridge is available and Resolve is connected
        """
        try:
            response = self._get_client().get("/api/status")
            if response.status_code == 200:
                data = response.json()
                return data.get("connected", False)
            return False
        except Exception as e:
            logger.warning(f"Bridge not available: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed status of the bridge and DaVinci Resolve

        Returns:
            Dict with connection status, version info, etc.
        """
        try:
            response = self._get_client().get("/api/status")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get status: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

    def health_check(self) -> bool:
        """Check if bridge server is running (even if Resolve isn't connected)"""
        try:
            response = self._get_client().get("/api/health")
            return response.status_code == 200
        except Exception as _e:
            logger.warning(
                "davinci_bridge_client.health_check: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    # =========================================================================
    # Project Operations
    # =========================================================================

    def create_project(self, name: str) -> bool:
        """
        Create a new DaVinci Resolve project

        Args:
            name: Project name

        Returns:
            bool: True if successful
        """
        try:
            response = self._get_client().post(
                "/api/projects",
                json={"name": name}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to create project: {e}")
            return False

    def list_projects(self) -> List[str]:
        """List all projects"""
        try:
            response = self._get_client().get("/api/projects")
            response.raise_for_status()
            data = response.json()
            return data.get("projects", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    def load_project(self, name: str) -> bool:
        """Load an existing project"""
        try:
            response = self._get_client().post(f"/api/projects/{name}/load")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to load project: {e}")
            return False

    def close_project(self) -> bool:
        """Close current project"""
        try:
            response = self._get_client().post("/api/projects/close")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to close project: {e}")
            return False

    def save_project(self) -> bool:
        """Save current project"""
        try:
            response = self._get_client().post("/api/projects/save")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to save project: {e}")
            return False

    # =========================================================================
    # Timeline Operations
    # =========================================================================

    def add_clip_to_timeline(
        self,
        video_path: Optional[str] = None,
        video_url: Optional[str] = None,
        position_seconds: float = 0
    ) -> bool:
        """
        Add a video clip to the timeline

        Args:
            video_path: Local path to video file
            video_url: URL to download video from
            position_seconds: Position in timeline

        Returns:
            bool: True if successful
        """
        try:
            response = self._get_client().post(
                "/api/timeline/add-clip",
                json={
                    "file_path": video_path,
                    "url": video_url,
                    "position_seconds": position_seconds
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to add clip: {e}")
            return False

    def add_transition(
        self,
        transition_type: str = "Cross Dissolve",
        at_second: float = 0,
        duration: float = 1.0
    ) -> bool:
        """Add a transition between clips"""
        try:
            response = self._get_client().post(
                "/api/timeline/add-transition",
                json={
                    "transition_type": transition_type,
                    "at_second": at_second,
                    "duration": duration
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to add transition: {e}")
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
        """Add text overlay to timeline"""
        try:
            response = self._get_client().post(
                "/api/timeline/add-text",
                json={
                    "text": text,
                    "position": position,
                    "start_second": start_second,
                    "duration_seconds": duration_seconds,
                    "font_size": font_size,
                    "color": color
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to add text: {e}")
            return False

    def add_audio(
        self,
        audio_path: Optional[str] = None,
        audio_url: Optional[str] = None,
        volume: float = 0.5,
        start_second: float = 0
    ) -> bool:
        """Add audio to timeline"""
        try:
            response = self._get_client().post(
                "/api/timeline/add-audio",
                json={
                    "file_path": audio_path,
                    "url": audio_url,
                    "volume": volume,
                    "start_second": start_second
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to add audio: {e}")
            return False

    # =========================================================================
    # Rendering
    # =========================================================================

    def render_project(
        self,
        output_path: Optional[str] = None,
        format: str = "mp4",
        codec: str = "H264",
        resolution: str = "1920x1080"
    ) -> DaVinciResult:
        """
        Render the current project

        Args:
            output_path: Output file path (auto-generated if None)
            format: Video format (mp4, mov, etc.)
            codec: Video codec
            resolution: Output resolution

        Returns:
            DaVinciResult with render status and file path
        """
        try:
            response = self._get_client().post(
                "/api/render/start",
                json={
                    "output_path": output_path,
                    "format": format,
                    "codec": codec,
                    "resolution": resolution
                }
            )
            response.raise_for_status()
            data = response.json()

            return DaVinciResult(
                success=data.get("success", False),
                video_path=data.get("video_path"),
                video_url=data.get("video_url"),
                job_id=data.get("job_id"),
                duration=data.get("duration"),
                error_message=data.get("error_message"),
                metadata=data.get("metadata", {})
            )

        except httpx.HTTPError as e:
            logger.error(f"Render failed: {e}")
            return DaVinciResult(
                success=False,
                error_message=str(e)
            )

    def get_render_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a render job"""
        try:
            response = self._get_client().get(f"/api/render/status/{job_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get render status: {e}")
            return {"error": str(e)}

    def cancel_render(self) -> bool:
        """Cancel current render"""
        try:
            response = self._get_client().post("/api/render/cancel")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            logger.error(f"Failed to cancel render: {e}")
            return False

    # =========================================================================
    # High-Level Operations
    # =========================================================================

    def chain_videos(
        self,
        video_urls: List[str],
        project_name: Optional[str] = None,
        add_transitions: bool = True,
        transition_duration: float = 1.0
    ) -> DaVinciResult:
        """
        Chain multiple videos together with transitions

        This is a high-level operation that handles:
        1. Creating a project
        2. Downloading videos
        3. Adding to timeline with transitions
        4. Rendering the result

        Args:
            video_urls: List of video URLs to chain
            project_name: Optional project name
            add_transitions: Whether to add transitions between clips
            transition_duration: Duration of transitions

        Returns:
            DaVinciResult with the chained video
        """
        try:
            logger.info(f"Chaining {len(video_urls)} videos via bridge")

            response = self._get_client().post(
                "/api/video/chain",
                json={
                    "video_urls": video_urls,
                    "project_name": project_name,
                    "add_transitions": add_transitions,
                    "transition_duration": transition_duration
                },
                timeout=600.0  # 10 minute timeout for multi-video operations
            )
            response.raise_for_status()
            data = response.json()

            return DaVinciResult(
                success=data.get("success", False),
                video_path=data.get("video_path"),
                video_url=data.get("video_url"),
                job_id=data.get("job_id"),
                duration=data.get("duration"),
                error_message=data.get("error_message"),
                metadata=data.get("metadata", {})
            )

        except httpx.HTTPError as e:
            logger.error(f"Chain videos failed: {e}")
            return DaVinciResult(
                success=False,
                error_message=str(e)
            )

    def add_music_to_video(
        self,
        video_url: str,
        audio_url: str,
        audio_volume: float = 0.3,
        output_format: str = 'mp4'
    ) -> DaVinciResult:
        """
        Add audio/music to a video

        Args:
            video_url: URL or path to source video
            audio_url: URL or path to audio file
            audio_volume: Volume level (0.0 to 1.0)
            output_format: Output format

        Returns:
            DaVinciResult with the video+audio
        """
        try:
            logger.info(f"Adding audio to video via bridge")

            # For now, this uses the step-by-step approach
            # Could add a dedicated endpoint later

            # Create project
            project_name = f"audio_mix_{int(time.time())}"
            if not self.create_project(project_name):
                return DaVinciResult(
                    success=False,
                    error_message="Failed to create project"
                )

            # Add video
            if not self.add_clip_to_timeline(video_url=video_url):
                return DaVinciResult(
                    success=False,
                    error_message="Failed to add video"
                )

            # Add audio
            if not self.add_audio(audio_url=audio_url, volume=audio_volume):
                return DaVinciResult(
                    success=False,
                    error_message="Failed to add audio"
                )

            # Render
            return self.render_project(format=output_format)

        except Exception as e:
            logger.error(f"Add music failed: {e}")
            return DaVinciResult(
                success=False,
                error_message=str(e)
            )


# ============================================================================
# Singleton Instance
# ============================================================================

_davinci_client: Optional[DaVinciBridgeClient] = None


def get_davinci_client() -> DaVinciBridgeClient:
    """
    Get the singleton DaVinci Bridge Client

    Usage:
        from content.davinci_bridge_client import get_davinci_client

        client = get_davinci_client()
        if client.is_available():
            result = client.chain_videos([...])
    """
    global _davinci_client
    if _davinci_client is None:
        _davinci_client = DaVinciBridgeClient()
    return _davinci_client


# ============================================================================
# Backwards Compatibility
# ============================================================================

# These classes/functions provide backwards compatibility with the old
# davinci_provider.py interface

class DaVinciRenderResult:
    """Backwards-compatible render result class"""

    def __init__(
        self,
        success: bool,
        video_path: Optional[str] = None,
        project_name: Optional[str] = None,
        duration: Optional[float] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.video_path = video_path
        self.project_name = project_name
        self.duration = duration
        self.error_message = error_message
        self.metadata = metadata or {}


class DaVinciResolveProvider:
    """
    Backwards-compatible wrapper that uses the bridge client

    This class provides the same interface as the original DaVinciResolveProvider
    but routes all calls through the bridge server.
    """

    def __init__(self):
        self._client = get_davinci_client()

    @property
    def studio_available(self) -> bool:
        """Check if DaVinci Resolve Studio is available via bridge"""
        return self._client.is_available()

    def create_project(self, project_name: str) -> bool:
        return self._client.create_project(project_name)

    def add_clip_to_timeline(
        self,
        video_path: str,
        position_seconds: float = 0
    ) -> bool:
        # Determine if it's a URL or file path
        if video_path.startswith(('http://', 'https://')):
            return self._client.add_clip_to_timeline(
                video_url=video_path,
                position_seconds=position_seconds
            )
        else:
            return self._client.add_clip_to_timeline(
                video_path=video_path,
                position_seconds=position_seconds
            )

    def add_transition(
        self,
        transition_type: str = "Cross Dissolve",
        at_second: float = 0,
        duration: float = 1.0
    ) -> bool:
        return self._client.add_transition(transition_type, at_second, duration)

    def add_text_overlay(
        self,
        text: str,
        position: str = "center",
        start_second: float = 0,
        duration_seconds: float = 3,
        font: str = "Arial",
        font_size: int = 72,
        color: str = "#FFFFFF"
    ) -> bool:
        return self._client.add_text_overlay(
            text, position, start_second, duration_seconds, font_size, color
        )

    def add_audio(
        self,
        audio_path: str,
        volume: float = 0.5,
        start_second: float = 0,
        fade_in: float = 0.5,
        fade_out: float = 0.5
    ) -> bool:
        if audio_path.startswith(('http://', 'https://')):
            return self._client.add_audio(audio_url=audio_path, volume=volume)
        else:
            return self._client.add_audio(audio_path=audio_path, volume=volume)

    def add_music_to_video(
        self,
        video_url: str,
        audio_url: str,
        audio_volume: float = 0.3,
        output_format: str = 'mp4'
    ) -> Dict[str, Any]:
        result = self._client.add_music_to_video(
            video_url, audio_url, audio_volume, output_format
        )
        return {
            'success': result.success,
            'video_url': result.video_path or result.video_url,
            'error': result.error_message,
            'metadata': result.metadata
        }

    def chain_videos_ffmpeg(
        self,
        video_urls: List[str],
        transition: str = 'fade',
        transition_duration: float = 1.0,
        output_format: str = 'mp4'
    ) -> Dict[str, Any]:
        result = self._client.chain_videos(
            video_urls,
            add_transitions=True,
            transition_duration=transition_duration
        )
        return {
            'success': result.success,
            'video_url': result.video_path or result.video_url,
            'error': result.error_message,
            'metadata': result.metadata
        }

    def render_project(
        self,
        output_path: str = None,
        format: str = "mp4",
        quality: str = "high",
        resolution: str = "1920x1080",
        export_audio: bool = False
    ) -> DaVinciRenderResult:
        result = self._client.render_project(output_path, format, "H264", resolution)
        return DaVinciRenderResult(
            success=result.success,
            video_path=result.video_path,
            duration=result.duration,
            error_message=result.error_message,
            metadata=result.metadata
        )

    def close_project(self):
        self._client.close_project()


def get_davinci_provider() -> DaVinciResolveProvider:
    """
    Get backwards-compatible DaVinci provider

    This function returns a provider that uses the bridge client internally,
    maintaining backwards compatibility with existing code.
    """
    return DaVinciResolveProvider()
