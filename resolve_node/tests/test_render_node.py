"""
Tests for Render Node components

Session 103 - Resolve Render Node Service
Tests cover models, controller, job queue, and API endpoints
"""

import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from models import RenderJob, JobStatus
from resolve_controller import ResolveController
from job_queue import JobQueue


# Fixtures
@pytest.fixture
def sample_job():
    """Create a sample render job"""
    return RenderJob(
        timeline_name="Test Timeline",
        clip_paths=["/path/to/clip1.mp4", "/path/to/clip2.mp4"],
        template="default_mp4",
        webhook_url="http://localhost:8000/api/v1/render/complete/"
    )


@pytest.fixture
def mock_resolve_controller():
    """Create a mock Resolve controller"""
    return ResolveController(mock_mode=True)


@pytest.fixture
def mock_job_queue():
    """Create a mock job queue"""
    queue = JobQueue(mock_mode=True)
    queue.start()
    yield queue
    queue.stop()


# Model Tests
class TestRenderJob:
    """Tests for RenderJob model"""

    def test_job_creation(self):
        """Test creating a render job"""
        job = RenderJob(
            timeline_name="Timeline 1",
            clip_paths=["/clip1.mp4"],
            template="high_quality"
        )

        assert job.job_id is not None
        assert job.timeline_name == "Timeline 1"
        assert len(job.clip_paths) == 1
        assert job.status == JobStatus.QUEUED
        assert job.progress == 0.0

    def test_job_to_dict(self, sample_job):
        """Test converting job to dictionary"""
        job_dict = sample_job.to_dict()

        assert isinstance(job_dict, dict)
        assert job_dict["job_id"] == sample_job.job_id
        assert job_dict["status"] == "queued"
        assert job_dict["timeline_name"] == "Test Timeline"

    def test_job_from_dict(self):
        """Test creating job from dictionary"""
        job_data = {
            "job_id": "test-123",
            "timeline_name": "Test",
            "clip_paths": [],
            "template": "default_mp4",
            "status": "queued",
            "progress": 0.0
        }

        job = RenderJob.from_dict(job_data)

        assert job.job_id == "test-123"
        assert job.timeline_name == "Test"
        assert job.status == JobStatus.QUEUED


# ResolveController Tests
class TestResolveController:
    """Tests for ResolveController (mock mode)"""

    def test_controller_initialization(self, mock_resolve_controller):
        """Test controller initializes in mock mode"""
        assert mock_resolve_controller.mock_mode is True
        assert mock_resolve_controller.resolve is None

    def test_import_media_mock(self, mock_resolve_controller):
        """Test importing media in mock mode"""
        result = mock_resolve_controller.import_media(["/clip1.mp4", "/clip2.mp4"])
        assert result is True

    def test_create_timeline_mock(self, mock_resolve_controller):
        """Test creating timeline in mock mode"""
        result = mock_resolve_controller.set_or_create_timeline("Test Timeline")
        assert result is True
        assert mock_resolve_controller.current_timeline is not None

    def test_start_render_mock(self, mock_resolve_controller):
        """Test starting render in mock mode"""
        mock_resolve_controller.set_or_create_timeline("Test")
        output_file = mock_resolve_controller.start_render("test-job-123")

        assert output_file is not None
        assert "test-job-123" in output_file
        assert Path(output_file).exists()

    def test_render_status_mock(self, mock_resolve_controller):
        """Test getting render status in mock mode"""
        status = mock_resolve_controller.get_render_status()

        assert isinstance(status, dict)
        assert "is_rendering" in status
        assert "progress" in status
        assert "status" in status


# JobQueue Tests
class TestJobQueue:
    """Tests for JobQueue (mock mode)"""

    def test_queue_initialization(self, mock_job_queue):
        """Test queue initializes"""
        assert mock_job_queue.running is True
        assert mock_job_queue.resolve_controller is not None

    def test_add_job(self, mock_job_queue, sample_job):
        """Test adding job to queue"""
        mock_job_queue.add_job(sample_job)

        assert sample_job.job_id in mock_job_queue.jobs
        retrieved_job = mock_job_queue.get_job(sample_job.job_id)
        assert retrieved_job == sample_job

    def test_process_job_mock(self, mock_job_queue, sample_job):
        """Test job processing in mock mode"""
        import time

        # Add job to queue
        mock_job_queue.add_job(sample_job)

        # Wait for processing
        time.sleep(3)

        # Check job was processed
        processed_job = mock_job_queue.get_job(sample_job.job_id)
        assert processed_job.status == JobStatus.DONE
        assert processed_job.output_file is not None


# API Endpoint Tests
class TestAPI:
    """Tests for FastAPI endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        # Set mock mode
        os.environ["MOCK_MODE"] = "true"

        # Import app after setting env var
        from app import app
        self.client = TestClient(app)
        self.headers = {"X-Render-Token": config.RENDER_NODE_TOKEN}

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "DaVinci Resolve Render Node"

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_start_render_unauthorized(self):
        """Test starting render without token"""
        payload = {
            "timeline_name": "Test",
            "clip_paths": [],
            "template": "default_mp4"
        }

        response = self.client.post("/render/start", json=payload)

        assert response.status_code == 401

    def test_start_render_authorized(self):
        """Test starting render with valid token"""
        payload = {
            "timeline_name": "Test Timeline",
            "clip_paths": ["/clip1.mp4"],
            "template": "default_mp4"
        }

        response = self.client.post(
            "/render/start",
            json=payload,
            headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_get_status(self):
        """Test getting job status"""
        # First create a job
        payload = {
            "timeline_name": "Test",
            "clip_paths": [],
            "template": "default_mp4"
        }

        create_response = self.client.post(
            "/render/start",
            json=payload,
            headers=self.headers
        )
        job_id = create_response.json()["job_id"]

        # Now get status
        response = self.client.get(
            f"/render/status/{job_id}",
            headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "progress" in data

    def test_list_jobs(self):
        """Test listing all jobs"""
        response = self.client.get("/jobs", headers=self.headers)

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "jobs" in data
        assert isinstance(data["jobs"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
