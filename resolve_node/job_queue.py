"""
Job Queue for Render Node

Session 103 - Resolve Render Node Service
Simple single-job queue with worker thread
"""

import threading
import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from queue import Queue, Empty

import config
from models import RenderJob, JobStatus
from resolve_controller import ResolveController
from utils import logger, get_file_size_mb, format_duration


class JobQueue:
    """Simple job queue with single worker thread"""

    def __init__(self, mock_mode: bool = False):
        """
        Initialize job queue

        Args:
            mock_mode: If True, run in mock mode without actual Resolve
        """
        self.mock_mode = mock_mode
        self.jobs: Dict[str, RenderJob] = {}
        self.queue = Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self.resolve_controller: Optional[ResolveController] = None

    def start(self):
        """Start the job queue worker"""
        if self.running:
            logger.warning("Job queue is already running")
            return

        logger.info("Starting job queue worker")
        self.running = True

        # Initialize Resolve controller
        try:
            self.resolve_controller = ResolveController(mock_mode=self.mock_mode)
        except Exception as e:
            logger.error(f"Failed to initialize Resolve controller: {e}")
            if not self.mock_mode:
                raise

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        logger.info("Job queue worker started")

    def stop(self):
        """Stop the job queue worker"""
        logger.info("Stopping job queue worker")
        self.running = False

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=10)

        logger.info("Job queue worker stopped")

    def add_job(self, job: RenderJob):
        """
        Add job to queue

        Args:
            job: RenderJob instance
        """
        logger.info(f"Adding job {job.job_id} to queue")
        self.jobs[job.job_id] = job
        self.queue.put(job.job_id)

        # Save job to disk for persistence
        self._save_job(job)

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        """
        Get job by ID

        Args:
            job_id: Job ID

        Returns:
            RenderJob if found, None otherwise
        """
        return self.jobs.get(job_id)

    def _save_job(self, job: RenderJob):
        """Save job to disk"""
        job_file = config.JOBS_DIR / f"{job.job_id}.json"
        try:
            with open(job_file, 'w') as f:
                json.dump(job.to_dict(), f, indent=2)
            logger.debug(f"Saved job {job.job_id} to disk")
        except Exception as e:
            logger.error(f"Failed to save job {job.job_id}: {e}")

    def _worker(self):
        """Worker thread that processes jobs"""
        logger.info("Worker thread started")

        while self.running:
            try:
                # Get job from queue (with timeout to allow checking self.running)
                try:
                    job_id = self.queue.get(timeout=1)
                except Empty:
                    continue

                # Get job
                job = self.get_job(job_id)
                if not job:
                    logger.error(f"Job {job_id} not found in jobs dict")
                    continue

                # Process job
                self._process_job(job)

                # Mark task as done
                self.queue.task_done()

            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1)

        logger.info("Worker thread stopped")

    def _process_job(self, job: RenderJob):
        """
        Process a render job

        Args:
            job: RenderJob to process
        """
        logger.info(f"Processing job {job.job_id}")

        try:
            # Update status to rendering
            job.status = JobStatus.RENDERING
            job.started_at = datetime.now()
            self._save_job(job)

            # Import media if clip paths provided
            if job.clip_paths:
                logger.info(f"Importing {len(job.clip_paths)} clips for job {job.job_id}")
                success = self.resolve_controller.import_media(job.clip_paths)
                if not success:
                    raise RuntimeError("Failed to import media files")

            # Set or create timeline
            success = self.resolve_controller.set_or_create_timeline(job.timeline_name)
            if not success:
                raise RuntimeError("Failed to create/set timeline")

            # Start render
            output_file = self.resolve_controller.start_render(job.job_id, job.template)
            if not output_file:
                raise RuntimeError("Failed to start render")

            # Wait for render to complete
            logger.info(f"Waiting for render to complete for job {job.job_id}")
            success = self.resolve_controller.wait_for_render_complete(
                timeout=config.RENDER_TIMEOUT
            )

            if not success:
                raise RuntimeError("Render failed or timed out")

            # Session 479: Verify output file exists - check multiple extensions
            output_path = Path(output_file)
            if not output_path.exists():
                # Try different extensions (H.264 Master uses .mov)
                custom_name = f"render_{job.job_id}"
                for ext in ['.mov', '.mp4', '.avi', '.mxf']:
                    alt_path = config.RESULTS_DIR / f"{custom_name}{ext}"
                    if alt_path.exists():
                        output_file = str(alt_path)
                        output_path = alt_path
                        logger.info(f"Found output with extension {ext}: {output_file}")
                        break
                else:
                    raise RuntimeError(f"Output file not found: {output_file}")

            # Update job with results
            job.output_file = str(output_file)
            job.status = JobStatus.DONE
            job.progress = 1.0
            job.completed_at = datetime.now()

            # Add metadata
            duration = (job.completed_at - job.started_at).total_seconds()
            file_size_bytes = output_path.stat().st_size if output_path.exists() else 0
            job.metadata.update({
                "file_size_mb": get_file_size_mb(output_path),
                "file_size_bytes": file_size_bytes,
                "render_duration": format_duration(duration),
                "render_duration_ms": int(duration * 1000),
                "output_path": str(output_file)
            })

            logger.info(f"Job {job.job_id} completed successfully")
            logger.info(f"  Output: {output_file}")
            logger.info(f"  Size: {job.metadata['file_size_mb']:.2f} MB")
            logger.info(f"  Duration: {job.metadata['render_duration']}")

            self._save_job(job)

            # Upload results to backend
            if job.webhook_url:
                self._upload_results(job)

        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            job.status = JobStatus.ERROR
            job.error_message = str(e)
            job.completed_at = datetime.now()
            self._save_job(job)

    def _upload_results(self, job: RenderJob):
        """
        Upload results to Django backend

        Args:
            job: Completed RenderJob
        """
        logger.info(f"Uploading results for job {job.job_id}")

        try:
            job.status = JobStatus.UPLOADING
            self._save_job(job)

            # Prepare payload
            payload = {
                "job_id": job.job_id,
                "file_url": f"http://localhost:{config.PORT}/render/result/{job.job_id}",
                "metadata": job.metadata,
                "status": "completed",
                "output_file": job.output_file,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }

            # Send to backend
            headers = {"Content-Type": "application/json"}
            url = job.webhook_url or config.DJANGO_COMPLETE_ENDPOINT

            for attempt in range(config.UPLOAD_MAX_RETRIES):
                try:
                    logger.info(f"Upload attempt {attempt + 1}/{config.UPLOAD_MAX_RETRIES}")
                    response = requests.post(url, json=payload, headers=headers, timeout=30)

                    if response.status_code in [200, 201]:
                        logger.info(f"Successfully uploaded results for job {job.job_id}")
                        job.status = JobStatus.UPLOADED
                        self._save_job(job)
                        return

                    logger.warning(f"Upload failed with status {response.status_code}: {response.text}")

                except requests.RequestException as e:
                    logger.warning(f"Upload attempt {attempt + 1} failed: {e}")

                # Wait before retry
                if attempt < config.UPLOAD_MAX_RETRIES - 1:
                    time.sleep(config.UPLOAD_RETRY_DELAY)

            # All retries failed
            raise RuntimeError(f"Failed to upload after {config.UPLOAD_MAX_RETRIES} attempts")

        except Exception as e:
            logger.error(f"Failed to upload results for job {job.job_id}: {e}")
            job.status = JobStatus.DONE  # Keep as DONE even if upload failed
            job.metadata["upload_error"] = str(e)
            self._save_job(job)
