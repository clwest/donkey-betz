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

Cost per 10-second base video: ~$0.60-1.00 (longer with loop mode)
- TTS: ~$0.05
- Image-to-Video: ~$0.15 (10 Runway credits)
- Lip Sync: ~$0.50+ (scales with final duration in loop mode)

Modes:
- loop: Single Runway clip looped to match audio length (fast, cheap, visible seams)
- multi_clip: N unique Runway clips with varied motion, concatenated via ffmpeg (3-6x cost, no loop seams)
"""

import logging
import math
import os
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.utils import timezone

logger = logging.getLogger(__name__)

# Varied motion suffixes for multi_clip mode — cycled if more clips than variations
MOTION_VARIATIONS = [
    "",
    ", with a gentle head tilt to the left",
    ", with a subtle nod",
    ", with a slight smile forming",
    ", looking slightly to the right",
    ", with a soft blink and slight eyebrow raise",
]


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
        duration: int = 10,
        sync_mode: str = "loop",
        temperature: float = 0.5,
        lipsync_model: str = "auto",
        project_id: str = None,
        mode: str = "loop",
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
            sync_mode: Lip sync mode (loop, cut_off, bounce)
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

        # multi_clip mode requires synchronous polling + ffmpeg; warn and fall back in async
        if mode == "multi_clip":
            logger.warning(
                "[PIPELINE] multi_clip mode not supported in async — "
                "falling back to loop mode (use generate_talking_video_sync for multi_clip)"
            )
            mode = "loop"

        logger.info(f"🎬 [PIPELINE] Starting talking character generation (mode={mode})")
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

            # Log estimated audio duration for debugging/cost estimation
            estimated_audio_secs = len(text) / 15  # ~15 chars/sec
            logger.info(f"📏 [PIPELINE] Estimated audio: {estimated_audio_secs:.0f}s, video base: {duration}s, sync_mode: {sync_mode}")

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
        sync_mode: str = "loop",
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
            # LatentSync (bytedance/latentsync) removed from Replicate — default to sync_labs
            if lipsync_model == "auto":
                lipsync_model = "sync_labs"
                logger.info(f"🎨 [PIPELINE] Auto-selected Sync Labs Lipsync-2")

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

    def _generate_multi_clip_base_video(
        self,
        image_url: str,
        text: str,
        motion_prompt: str,
        duration: int,
        timeout: int,
        start_time: float,
    ) -> Tuple[Optional[str], str]:
        """
        Generate N unique Runway clips with varied motion prompts, concatenate via ffmpeg.

        Returns:
            (video_url, error) — video_url is None on failure
        """
        import requests as req
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        estimated_audio_secs = len(text) / 15  # ~15 chars/sec
        num_clips = min(math.ceil(estimated_audio_secs / duration), 6)
        num_clips = max(num_clips, 2)  # at least 2 clips for multi_clip to make sense

        logger.info(
            f"🎬 [MULTI_CLIP] Generating {num_clips} clips "
            f"(~{estimated_audio_secs:.0f}s audio, {duration}s each)"
        )

        # Build varied prompts
        prompts = []
        for i in range(num_clips):
            variation = MOTION_VARIATIONS[i % len(MOTION_VARIATIONS)]
            prompts.append(f"{motion_prompt}{variation}")

        # Submit all Runway i2v calls in parallel
        def _submit_clip(prompt: str) -> str:
            """Submit a single Runway i2v call, return task_id."""
            result = self.video_provider.image_to_video(
                image_url=image_url,
                motion_prompt=prompt,
                duration=duration,
            )
            if not result.success:
                raise RuntimeError(f"Runway submission failed: {result.error_message}")
            return result.task_id

        task_ids = []
        with ThreadPoolExecutor(max_workers=num_clips) as executor:
            futures = {executor.submit(_submit_clip, p): i for i, p in enumerate(prompts)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    task_id = future.result()
                    task_ids.append((idx, task_id))
                    logger.info(f"🎬 [MULTI_CLIP] Clip {idx} submitted: {task_id[:20]}...")
                except Exception as e:
                    return None, f"Failed to submit clip {idx}: {e}"

        task_ids.sort(key=lambda x: x[0])  # maintain order

        # Poll all tasks until complete or timeout
        clip_urls = [None] * num_clips
        pending = {task_id: idx for idx, task_id in task_ids}

        while pending and (time.time() - start_time) < timeout:
            for task_id, idx in list(pending.items()):
                status = self.video_provider.check_status(task_id)
                vs = status.status if hasattr(status, 'status') else ''
                if vs in ('SUCCEEDED', 'completed'):
                    url = status.video_url if hasattr(status, 'video_url') else ''
                    clip_urls[idx] = url
                    del pending[task_id]
                    logger.info(f"✅ [MULTI_CLIP] Clip {idx} ready")
                elif vs in ('FAILED', 'failed'):
                    err = status.error_message if hasattr(status, 'error_message') else 'unknown'
                    return None, f"Clip {idx} failed: {err}"
            if pending:
                time.sleep(5)

        if pending:
            return None, f"Timed out waiting for {len(pending)} clips"

        # Download clips to temp dir
        tmp_dir = tempfile.mkdtemp(prefix="multi_clip_")
        try:
            clip_paths = []
            for i, url in enumerate(clip_urls):
                clip_path = os.path.join(tmp_dir, f"clip_{i:02d}.mp4")
                resp = req.get(url, timeout=60)
                resp.raise_for_status()
                with open(clip_path, 'wb') as f:
                    f.write(resp.content)
                clip_paths.append(clip_path)
                logger.info(f"📥 [MULTI_CLIP] Downloaded clip {i}: {len(resp.content)} bytes")

            # ffmpeg concat
            output_path = os.path.join(tmp_dir, "concatenated.mp4")
            concat_list = os.path.join(tmp_dir, "concat.txt")
            with open(concat_list, 'w') as f:
                for path in clip_paths:
                    f.write(f"file '{path}'\n")

            # Try fast concat demuxer first (no re-encode)
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_list,
                '-c', 'copy', '-y', output_path,
            ]
            logger.info(f"🔧 [MULTI_CLIP] ffmpeg concat: {num_clips} clips")
            proc = subprocess.run(cmd, capture_output=True, timeout=120)

            if proc.returncode != 0:
                # Fallback: re-encode with filter_complex (video-only, Runway clips have no audio)
                logger.warning("[MULTI_CLIP] Concat demuxer failed, trying filter_complex re-encode")
                input_args = []
                filter_parts = []
                for i, path in enumerate(clip_paths):
                    input_args.extend(['-i', path])
                    filter_parts.append(f'[{i}:v:0]')

                filter_complex = f"{''.join(filter_parts)}concat=n={len(clip_paths)}:v=1:a=0[v]"
                cmd = ['ffmpeg'] + input_args + [
                    '-filter_complex', filter_complex,
                    '-map', '[v]', '-y', output_path,
                ]
                proc = subprocess.run(cmd, capture_output=True, timeout=120)

                if proc.returncode != 0:
                    stderr = proc.stderr.decode(errors='replace')[:500]
                    return None, f"ffmpeg concat failed: {stderr}"

            # Upload concatenated video via Cloudinary video upload
            # (default_storage is MediaCloudinaryStorage which rejects non-image files)
            try:
                import cloudinary.uploader
                upload_result = cloudinary.uploader.upload(
                    output_path,
                    resource_type="video",
                    folder="videos/multi_clip",
                    public_id=f"multi_clip_{int(time.time())}",
                )
                video_url = upload_result.get('secure_url', upload_result.get('url', ''))
            except Exception:
                # Fallback: try default_storage (works if local or non-Cloudinary)
                with open(output_path, 'rb') as f:
                    content = f.read()
                filename = f"videos/multi_clip/multi_clip_{int(time.time())}.mp4"
                saved_path = default_storage.save(filename, ContentFile(content))
                video_url = default_storage.url(saved_path)

            logger.info(
                f"✅ [MULTI_CLIP] Concatenated {num_clips} clips → {video_url[:60]}..."
            )
            return video_url, ""

        except Exception as e:
            return None, f"Multi-clip post-processing failed: {e}"
        finally:
            # Clean up temp dir
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _mark_video_history_failed(self, video_task_id: str, error_message: str):
        """Mark the VideoHistory record as failed so media library stays clean."""
        if not video_task_id:
            return
        try:
            from content.models import VideoHistory
            vh = VideoHistory.objects.filter(video_id=video_task_id).first()
            if vh:
                vh.status = 'failed'
                vh.parameters['pipeline_stage'] = 'failed'
                vh.parameters['error'] = error_message[:500]
                vh.save()
                logger.info(f"[PIPELINE] Marked VideoHistory {vh.id} as failed")
        except Exception as e:
            logger.warning(f"Failed to mark VideoHistory as failed: {e}")

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
        duration: int = 10,
        sync_mode: str = "loop",
        temperature: float = 0.5,
        lipsync_model: str = "auto",
        project_id: str = None,
        timeout: int = 600,
        color_grade: Optional[str] = None,
        mode: str = "loop",
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

        if mode == "multi_clip":
            # ── Multi-clip path ──────────────────────────────────────
            # TTS first, then N parallel Runway clips → ffmpeg concat → lip sync
            result = PipelineResult(
                success=False,
                status=PipelineStatus.PENDING,
                created_at=timezone.now().isoformat(),
            )
            cost_estimate = self.estimate_cost(text, duration)
            num_clips = min(math.ceil(len(text) / 15 / duration), 6)
            result.estimated_cost = cost_estimate['total_cost'] * max(num_clips, 2)

            logger.info(f"🎬 [MULTI_CLIP] Starting multi-clip pipeline (~{num_clips} clips)")

            # Stage 1: TTS
            try:
                result.status = PipelineStatus.GENERATING_AUDIO
                audio_result = self.audio_provider.text_to_speech(text=text, voice=voice)
                if not audio_result.get('success'):
                    result.status = PipelineStatus.FAILED
                    result.failed_stage = "tts"
                    result.error_message = audio_result.get('error', 'TTS generation failed')
                    return result
                result.audio_url = audio_result.get('audio_url', '')
                logger.info(f"✅ [MULTI_CLIP] TTS complete: {result.audio_url[:60]}...")
            except Exception as e:
                result.status = PipelineStatus.FAILED
                result.failed_stage = "tts"
                result.error_message = str(e)
                return result

            # Stage 2: Multi-clip generation + ffmpeg concat
            result.status = PipelineStatus.ANIMATING_IMAGE
            video_url, error = self._generate_multi_clip_base_video(
                image_url=image_url,
                text=text,
                motion_prompt=motion_prompt,
                duration=duration,
                timeout=timeout,
                start_time=start_time,
            )
            if not video_url:
                logger.warning(
                    f"[PIPELINE] multi_clip failed ({error}), falling back to loop mode"
                )
                mode = "loop"
                # Fall through to loop path below
            else:
                result.base_video_url = video_url
                # Force cut_off — concatenated video already matches audio length
                sync_mode = "cut_off"

        if mode != "multi_clip":
            # ── Single-clip (loop) path ──────────────────────────────
            # Start async pipeline (TTS + Video task creation)
            result = self.generate_talking_video_async(
                image_url=image_url,
                text=text,
                voice=voice,
                motion_prompt=motion_prompt,
                duration=duration,
                sync_mode=sync_mode,
                temperature=temperature,
                project_id=project_id,
            )

            if not result.success:
                return result

            # Wait for video generation
            logger.info(f"⏳ [PIPELINE] Waiting for video generation...")
            video_url = None

            while time.time() - start_time < timeout:
                video_status = self.check_video_status(result.video_task_id)

                vs = video_status.get('status', '')
                if vs in ('SUCCEEDED', 'completed'):
                    video_url = video_status.get('video_url')
                    logger.info(f"✅ [PIPELINE] Video ready: {video_url[:60]}...")
                    break
                elif vs in ('FAILED', 'failed'):
                    result.success = False
                    result.status = PipelineStatus.FAILED
                    result.failed_stage = "image_to_video"
                    result.error_message = video_status.get('error_message', 'Video generation failed')
                    self._mark_video_history_failed(result.video_task_id, result.error_message)
                    return result

                time.sleep(5)

            if not video_url:
                result.success = False
                result.status = PipelineStatus.FAILED
                result.failed_stage = "image_to_video"
                result.error_message = "Video generation timed out"
                self._mark_video_history_failed(result.video_task_id, "Video generation timed out")
                return result

            result.base_video_url = video_url

        # ── Lip sync (shared by both paths) ──────────────────────────
        # Session 1075: Try primary model, fallback to alternate if it fails
        _FALLBACK_MODEL = {'latentsync': 'sync_labs', 'sync_labs': 'latentsync'}
        models_to_try = [lipsync_model]
        fallback = _FALLBACK_MODEL.get(lipsync_model)
        if fallback:
            models_to_try.append(fallback)

        lipsync_succeeded = False
        last_lipsync_error = ""

        for attempt_model in models_to_try:
            # Start lip sync with model selection
            lipsync_result = self.continue_pipeline_after_video(
                audio_url=result.audio_url,
                video_url=result.base_video_url,
                sync_mode=sync_mode,
                temperature=temperature,
                lipsync_model=attempt_model,
            )

            if not lipsync_result.success:
                last_lipsync_error = lipsync_result.error_message
                if attempt_model != models_to_try[-1]:
                    logger.warning(
                        f"[PIPELINE] {attempt_model} submission failed, trying fallback: "
                        f"{last_lipsync_error[:100]}"
                    )
                    continue
                # No more fallbacks
                return lipsync_result

            # Wait for lip sync
            logger.info(f"⏳ [PIPELINE] Waiting for lip sync ({attempt_model})...")

            while time.time() - start_time < timeout:
                lipsync_status = self.check_lipsync_status(lipsync_result.lipsync_task_id)

                if lipsync_status.get('status') == 'succeeded':
                    lipsync_succeeded = True
                    break
                elif lipsync_status.get('status') == 'failed':
                    last_lipsync_error = lipsync_status.get('error', 'Lip sync failed')
                    logger.warning(
                        f"[PIPELINE] {attempt_model} failed: {last_lipsync_error[:100]}"
                    )
                    break

                time.sleep(5)  # Poll every 5 seconds
            else:
                # Timed out waiting for this model
                last_lipsync_error = f"{attempt_model} lip sync timed out"
                logger.warning(f"[PIPELINE] {last_lipsync_error}")

            if lipsync_succeeded:
                break

            # Try fallback model if available
            if attempt_model != models_to_try[-1]:
                logger.info(f"[PIPELINE] Retrying lip sync with fallback model...")

        if not lipsync_succeeded:
            result.success = False
            result.status = PipelineStatus.FAILED
            result.failed_stage = "lip_sync"
            result.error_message = f"Lip sync failed (tried {', '.join(models_to_try)}): {last_lipsync_error}"
            self._mark_video_history_failed(result.video_task_id, result.error_message)
            return result

        # Lip sync succeeded
        result.final_video_url = lipsync_status.get('video_url', '')
        result.success = True
        result.status = PipelineStatus.COMPLETED
        result.progress_percent = 100
        result.progress_message = "✅ Talking character video complete!"
        result.duration_seconds = duration

        # Persist final video to Cloudinary (ephemeral URLs expire)
        persistent_url = result.final_video_url
        try:
            import urllib.request
            import cloudinary.uploader
            with urllib.request.urlopen(result.final_video_url, timeout=60) as resp:
                video_bytes = resp.read()
            if len(video_bytes) > 1000:  # sanity check
                upload_result = cloudinary.uploader.upload(
                    video_bytes,
                    resource_type="video",
                    folder="videos/talking_character",
                    public_id=f"talk_{int(time.time())}",
                )
                persistent_url = upload_result.get('secure_url', upload_result.get('url', ''))
                result.final_video_url = persistent_url
                logger.info(f"✅ [PIPELINE] Persisted video to Cloudinary: {persistent_url[:80]}")
            else:
                logger.warning(f"[PIPELINE] Downloaded video too small ({len(video_bytes)}b), keeping ephemeral URL")
        except Exception as e:
            logger.warning(f"⚠️ [PIPELINE] Could not persist video to Cloudinary: {e} — keeping ephemeral URL")

        # Update VideoHistory with final lip-synced video URL
        if self.user and result.video_task_id:
            try:
                from content.models import VideoHistory
                vh = VideoHistory.objects.filter(
                    video_id=result.video_task_id
                ).first()
                if vh:
                    vh.video_url = persistent_url
                    vh.status = 'completed'
                    vh.duration = duration
                    vh.parameters['final_video_url'] = persistent_url
                    vh.parameters['base_video_url'] = result.base_video_url
                    vh.parameters['audio_url'] = result.audio_url
                    vh.parameters['pipeline_stage'] = 'completed'
                    vh.parameters['actual_cost'] = result.actual_cost
                    vh.save()
                    logger.info(f"✅ [PIPELINE] Updated VideoHistory {vh.id} with final video")
            except Exception as e:
                logger.warning(f"⚠️ Failed to update VideoHistory: {e}")

        # Optional DaVinci Resolve color grade post-processing
        if color_grade:
            try:
                from core.agents.resolve_agent import ResolveNodeClient
                client = ResolveNodeClient()
                health = client.health_check()
                if health.get('status') == 'ok':
                    logger.info(f"🎨 [PIPELINE] Sending to DaVinci for color grade: {color_grade}")
                    render = client.start_render(
                        clip_paths=[result.final_video_url],
                        template='default_mp4',
                    )
                    if render.get('job_id'):
                        job_id = render['job_id']
                        while time.time() - start_time < timeout:
                            status = client.get_status(job_id)
                            if status.get('status') == 'done':
                                result_url = client.get_result_url(job_id)
                                if result_url:
                                    result.final_video_url = result_url
                                    logger.info(f"✅ [PIPELINE] DaVinci render complete: {result_url[:60]}...")
                                break
                            elif status.get('status') == 'error':
                                logger.warning("DaVinci render failed, using lip-synced video")
                                break
                            time.sleep(5)
                else:
                    logger.warning("DaVinci Resolve not available, skipping color grade")
            except Exception as e:
                logger.warning(f"DaVinci post-processing failed: {e}")

        logger.info(f"🎉 [PIPELINE] COMPLETE! Final video: {result.final_video_url[:60]}...")
        return result


# Singleton instance
_pipeline = None

def get_talking_character_pipeline(user=None) -> TalkingCharacterPipeline:
    """Get singleton instance of the talking character pipeline"""
    global _pipeline
    if _pipeline is None or user is not None:
        _pipeline = TalkingCharacterPipeline(user=user)
    return _pipeline
