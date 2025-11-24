"""
Talking Character Pipeline - Session 175
Complete workflow: Image + Text → Talking Video

This pipeline combines multiple AI services to create talking character videos:
1. Text-to-Speech (ElevenLabs) - Generate audio from script
2. Image-to-Video (Runway) - Animate the character image
3. Lip Sync (Sync Labs via Replicate) - Sync mouth movements to audio

Use Cases:
- Promo videos with AI spokesperson
- YouTube explainer videos
- Marketing content with brand characters
- Social media content

Cost per 10-second video: ~$0.60-1.00
- TTS: ~$0.05
- Image-to-Video: ~$0.15 (10 Runway credits)
- Lip Sync: ~$0.50 (10 seconds × $0.05)
"""

import logging
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Status of the talking character pipeline"""
    PENDING = "pending"
    GENERATING_AUDIO = "generating_audio"
    ANIMATING_IMAGE = "animating_image"
    SYNCING_LIPS = "syncing_lips"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineResult:
    """Result from the talking character pipeline"""
    success: bool
    status: PipelineStatus = PipelineStatus.PENDING

    # Stage outputs
    audio_url: str = ""
    base_video_url: str = ""
    final_video_url: str = ""

    # Tracking IDs for async polling
    tts_task_id: str = ""
    video_task_id: str = ""
    lipsync_task_id: str = ""

    # Progress info
    current_stage: str = ""
    progress_percent: int = 0
    progress_message: str = ""

    # Error handling
    error_message: str = ""
    failed_stage: str = ""

    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0

    # Metadata
    duration_seconds: float = 0.0
    created_at: str = ""


class TalkingCharacterPipeline:
    """
    Complete pipeline for creating talking character videos.

    Workflow:
    1. Generate audio from text (ElevenLabs TTS)
    2. Create base video from character image (Runway Image-to-Video)
    3. Apply lip sync to match audio (Sync Labs Lipsync-2)

    Supports both sync (wait for completion) and async (return task IDs) modes.
    """

    def __init__(self, user=None):
        self.user = user
        self._init_providers()

    def _init_providers(self):
        """Initialize API providers"""
        # ElevenLabs for TTS
        from content.elevenlabs_provider import ElevenLabsProvider
        self.audio_provider = ElevenLabsProvider()

        # Runway for Image-to-Video
        from content.video_provider import RunwayMLProvider
        self.video_provider = RunwayMLProvider()

        # Replicate for Lip Sync
        from content.replicate_provider import get_replicate_provider
        self.replicate_provider = get_replicate_provider()

    def estimate_cost(self, text: str, duration_seconds: int = 10) -> Dict[str, float]:
        """
        Estimate cost for generating a talking character video.

        Args:
            text: Script text for TTS
            duration_seconds: Target video duration

        Returns:
            Dict with cost breakdown
        """
        # TTS cost: ~$0.01 per 100 characters (ElevenLabs)
        tts_cost = len(text) * 0.0001

        # Image-to-Video: ~10-15 Runway credits per 5-10s video
        # 1 credit = ~$0.01
        video_cost = 0.15  # Rough estimate

        # Lip Sync: $0.05 per second
        lipsync_cost = duration_seconds * 0.05

        total = tts_cost + video_cost + lipsync_cost

        return {
            'tts_cost': round(tts_cost, 3),
            'video_cost': round(video_cost, 3),
            'lipsync_cost': round(lipsync_cost, 3),
            'total_cost': round(total, 3),
            'duration_seconds': duration_seconds
        }

    def generate_talking_video_async(
        self,
        image_url: str,
        text: str,
        voice: str = "Rachel",
        motion_prompt: str = "subtle talking motion, slight head movements",
        duration: int = 5,
        sync_mode: str = "cut_off",
        temperature: float = 0.5,
        lipsync_model: str = "auto",
        project_id: str = None
    ) -> PipelineResult:
        """
        Start async generation of a talking character video.

        This method starts each stage and returns task IDs for polling.
        Call check_pipeline_status() to monitor progress.

        Args:
            image_url: URL or path to character image
            text: Script text to speak
            voice: ElevenLabs voice name (default: Rachel)
            motion_prompt: Motion description for video generation
            duration: Target duration in seconds (5 or 10)
            sync_mode: Lip sync mode (cut_off, loop, bounce)
            temperature: Lip sync expression intensity (0-1)
            lipsync_model: Which model to use (auto/latentsync/sync_labs)
            project_id: Optional project association

        Returns:
            PipelineResult with task IDs for polling (note: lipsync_model is stored for later use)
        """
        result = PipelineResult(
            success=False,
            status=PipelineStatus.PENDING,
            created_at=timezone.now().isoformat()
        )

        # Estimate cost
        cost_estimate = self.estimate_cost(text, duration)
        result.estimated_cost = cost_estimate['total_cost']

        logger.info(f"🎬 [PIPELINE] Starting talking character generation")
        logger.info(f"   Image: {image_url[:60]}...")
        logger.info(f"   Text: {text[:50]}...")
        logger.info(f"   Voice: {voice}, Duration: {duration}s")
        logger.info(f"   Estimated cost: ${cost_estimate['total_cost']:.3f}")

        # Stage 1: Generate Audio (TTS)
        try:
            result.status = PipelineStatus.GENERATING_AUDIO
            result.current_stage = "Generating speech audio"
            result.progress_percent = 10
            result.progress_message = "🎤 Generating speech with ElevenLabs..."

            logger.info(f"🎤 [PIPELINE] Stage 1: Generating TTS audio")

            # Call ElevenLabs TTS
            audio_result = self.audio_provider.text_to_speech(
                text=text,
                voice=voice
            )

            if not audio_result.get('success'):
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "tts"
                result.error_message = audio_result.get('error', 'TTS generation failed')
                return result

            result.audio_url = audio_result.get('audio_url', '')
            result.tts_task_id = "completed"  # TTS is synchronous
            result.progress_percent = 30

            logger.info(f"✅ [PIPELINE] TTS complete: {result.audio_url[:60]}...")

        except Exception as e:
            logger.error(f"❌ [PIPELINE] TTS error: {e}")
            result.success = False
            result.status = PipelineStatus.FAILED
            result.failed_stage = "tts"
            result.error_message = str(e)
            return result

        # Stage 2: Animate Image to Video
        try:
            result.status = PipelineStatus.ANIMATING_IMAGE
            result.current_stage = "Animating character"
            result.progress_percent = 40
            result.progress_message = "🎬 Animating character with Runway..."

            logger.info(f"🎬 [PIPELINE] Stage 2: Image-to-Video")

            # Call Runway Image-to-Video
            video_result = self.video_provider.image_to_video(
                image_url=image_url,
                motion_prompt=motion_prompt,
                duration=duration
            )

            if not video_result.success:
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "image_to_video"
                result.error_message = video_result.error_message
                return result

            result.video_task_id = video_result.task_id
            result.progress_percent = 50
            result.progress_message = f"🎬 Video generating... (Task: {video_result.task_id[:20]}...)"

            logger.info(f"✅ [PIPELINE] Video task started: {video_result.task_id}")

            # Session 176: Create VideoHistory record for status polling
            # This allows check_video_status endpoint to find and update the record
            if self.user:
                from content.models import VideoHistory
                try:
                    video_history = VideoHistory.objects.create(
                        user=self.user,
                        video_id=video_result.task_id,  # Use Runway task_id
                        prompt=motion_prompt,
                        model_used='runway_gen4_turbo',
                        video_type='talking_character',
                        status='pending',
                        parameters={
                            'text': text,
                            'voice': voice,
                            'image_url': image_url,
                            'duration': duration,
                            'sync_mode': sync_mode,
                            'temperature': temperature,
                            'lipsync_model': lipsync_model,  # Session 177: Store for later use
                            'pipeline_stage': 'image_to_video'
                        }
                    )
                    if project_id:
                        # Associate with project
                        from content.models import CreativeProject
                        try:
                            project = CreativeProject.objects.get(id=project_id)
                            video_history.project = project
                            video_history.save()
                            logger.info(f"✅ VideoHistory created with project: {project_id}")
                        except CreativeProject.DoesNotExist:
                            logger.warning(f"⚠️ Project {project_id} not found")
                    logger.info(f"✅ [PIPELINE] Created VideoHistory: {video_history.id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create VideoHistory: {e}")

            # Return here for async mode - caller will poll for completion
            result.success = True
            result.current_stage = "Waiting for video generation"

            return result

        except Exception as e:
            logger.error(f"❌ [PIPELINE] Video generation error: {e}")
            result.success = False
            result.status = PipelineStatus.FAILED
            result.failed_stage = "image_to_video"
            result.error_message = str(e)
            return result

    def continue_pipeline_after_video(
        self,
        audio_url: str,
        video_url: str,
        sync_mode: str = "cut_off",
        temperature: float = 0.5,
        lipsync_model: str = "auto"
    ) -> PipelineResult:
        """
        Continue pipeline after video generation completes.

        Called when Image-to-Video task completes to start lip sync.

        Args:
            audio_url: URL to generated audio
            video_url: URL to generated video
            sync_mode: Lip sync mode
            temperature: Expression intensity
            lipsync_model: Which model to use:
                          - "auto": Auto-detect (photorealistic → sync_labs, stylized → latentsync)
                          - "sync_labs": Sync Labs Lipsync-2 (photorealistic humans)
                          - "latentsync": ByteDance LatentSync (cartoon/stylized)

        Returns:
            PipelineResult with lip sync task ID
        """
        result = PipelineResult(
            success=False,
            status=PipelineStatus.SYNCING_LIPS,
            audio_url=audio_url,
            base_video_url=video_url,
            created_at=timezone.now().isoformat()
        )

        try:
            # Session 177: Model selection logic
            # Default to latentsync for better cartoon/stylized character support
            if lipsync_model == "auto":
                lipsync_model = "latentsync"  # Default to cartoon-optimized model
                logger.info(f"🎨 [PIPELINE] Auto-selected LatentSync (cartoon-optimized)")

            result.current_stage = "Syncing lip movements"
            result.progress_percent = 70

            if lipsync_model == "latentsync":
                result.progress_message = "👄 Syncing lips with ByteDance LatentSync (cartoon-optimized)..."
                logger.info(f"👄 [PIPELINE] Stage 3: Lip Sync (LatentSync - Cartoon Optimized)")
            else:
                result.progress_message = "👄 Syncing lips with Sync Labs (photorealistic)..."
                logger.info(f"👄 [PIPELINE] Stage 3: Lip Sync (Sync Labs - Photorealistic)")

            logger.info(f"   Video: {video_url[:60]}...")
            logger.info(f"   Audio: {audio_url[:60]}...")
            logger.info(f"   Model: {lipsync_model}")

            # Call appropriate lip sync model
            if lipsync_model == "latentsync":
                # ByteDance LatentSync - optimized for cartoon/stylized characters
                lipsync_result = self.replicate_provider.lip_sync_latent(
                    video_url=video_url,
                    audio_url=audio_url,
                    bbox_shift=0
                )
            else:
                # Sync Labs Lipsync-2 - optimized for photorealistic humans
                lipsync_result = self.replicate_provider.lip_sync(
                    video_url=video_url,
                    audio_url=audio_url,
                    sync_mode=sync_mode,
                    temperature=temperature
                )

            if not lipsync_result.success:
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "lip_sync"
                result.error_message = lipsync_result.error_message
                return result

            result.lipsync_task_id = lipsync_result.prediction_id
            result.progress_percent = 80
            result.progress_message = f"👄 Lip sync processing... (ID: {lipsync_result.prediction_id[:20]}...)"
            result.success = True

            logger.info(f"✅ [PIPELINE] Lip sync started: {lipsync_result.prediction_id}")

            return result

        except Exception as e:
            logger.error(f"❌ [PIPELINE] Lip sync error: {e}")
            result.success = False
            result.status = PipelineStatus.FAILED
            result.failed_stage = "lip_sync"
            result.error_message = str(e)
            return result

    def check_video_status(self, task_id: str) -> Dict[str, Any]:
        """Check status of Runway video generation task"""
        return self.video_provider.check_status(task_id).__dict__

    def check_lipsync_status(self, prediction_id: str) -> Dict[str, Any]:
        """Check status of Sync Labs lip sync task"""
        return self.replicate_provider.check_lip_sync_status(prediction_id)

    def generate_talking_video_sync(
        self,
        image_url: str,
        text: str,
        voice: str = "Rachel",
        motion_prompt: str = "subtle talking motion, slight head movements",
        duration: int = 5,
        sync_mode: str = "cut_off",
        temperature: float = 0.5,
        lipsync_model: str = "auto",
        project_id: str = None,
        timeout: int = 300
    ) -> PipelineResult:
        """
        Generate a talking character video synchronously (blocking).

        Waits for each stage to complete before proceeding.
        Use for testing or when you need the final result immediately.

        Args:
            image_url: URL or path to character image
            text: Script text to speak
            voice: ElevenLabs voice name
            motion_prompt: Motion description for video
            duration: Target duration in seconds
            sync_mode: Lip sync mode
            temperature: Expression intensity
            project_id: Optional project association
            timeout: Max time to wait in seconds

        Returns:
            PipelineResult with final video URL
        """
        start_time = time.time()

        # Start async pipeline (TTS + Video task creation)
        result = self.generate_talking_video_async(
            image_url=image_url,
            text=text,
            voice=voice,
            motion_prompt=motion_prompt,
            duration=duration,
            sync_mode=sync_mode,
            temperature=temperature,
            project_id=project_id
        )

        if not result.success:
            return result

        # Wait for video generation
        logger.info(f"⏳ [PIPELINE] Waiting for video generation...")
        video_url = None

        while time.time() - start_time < timeout:
            video_status = self.check_video_status(result.video_task_id)

            if video_status.get('status') == 'SUCCEEDED':
                video_url = video_status.get('video_url')
                logger.info(f"✅ [PIPELINE] Video ready: {video_url[:60]}...")
                break
            elif video_status.get('status') == 'FAILED':
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "image_to_video"
                result.error_message = video_status.get('error_message', 'Video generation failed')
                return result

            time.sleep(5)  # Poll every 5 seconds

        if not video_url:
            result.success = False
            result.status = PipelineStatus.FAILED
            result.failed_stage = "image_to_video"
            result.error_message = "Video generation timed out"
            return result

        result.base_video_url = video_url

        # Start lip sync with model selection
        lipsync_result = self.continue_pipeline_after_video(
            audio_url=result.audio_url,
            video_url=video_url,
            sync_mode=sync_mode,
            temperature=temperature,
            lipsync_model=lipsync_model
        )

        if not lipsync_result.success:
            return lipsync_result

        # Wait for lip sync
        logger.info(f"⏳ [PIPELINE] Waiting for lip sync...")

        while time.time() - start_time < timeout:
            lipsync_status = self.check_lipsync_status(lipsync_result.lipsync_task_id)

            if lipsync_status.get('status') == 'succeeded':
                result.final_video_url = lipsync_status.get('video_url', '')
                result.success = True
                result.status = PipelineStatus.COMPLETED
                result.progress_percent = 100
                result.progress_message = "✅ Talking character video complete!"
                result.duration_seconds = duration

                logger.info(f"🎉 [PIPELINE] COMPLETE! Final video: {result.final_video_url[:60]}...")
                return result

            elif lipsync_status.get('status') == 'failed':
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "lip_sync"
                result.error_message = lipsync_status.get('error', 'Lip sync failed')
                return result

            time.sleep(5)  # Poll every 5 seconds

        # Timeout
        result.success = False
        result.status = PipelineStatus.FAILED
        result.failed_stage = "lip_sync"
        result.error_message = "Lip sync timed out"
        return result


# Singleton instance
_pipeline = None

def get_talking_character_pipeline(user=None) -> TalkingCharacterPipeline:
    """Get singleton instance of the talking character pipeline"""
    global _pipeline
    if _pipeline is None or user is not None:
        _pipeline = TalkingCharacterPipeline(user=user)
    return _pipeline
