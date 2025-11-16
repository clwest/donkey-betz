"""
Rendering Tests - Session 105

Test suite for RenderJob model and API endpoints.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from content.models import CreativeProject, AISession
from .models import RenderJob

User = get_user_model()


class RenderJobModelTest(TestCase):
    """Test RenderJob model properties and behavior."""

    def setUp(self):
        """Set up test user and project."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = CreativeProject.objects.create(
            user=self.user,
            name='Test Project',
            description='Test project for renders'
        )

    def test_render_job_creation(self):
        """Test creating a RenderJob."""
        job = RenderJob.objects.create(
            user=self.user,
            project=self.project,
            status=RenderJob.STATUS_QUEUED
        )

        self.assertIsNotNone(job.id)
        self.assertEqual(job.user, self.user)
        self.assertEqual(job.project, self.project)
        self.assertEqual(job.status, RenderJob.STATUS_QUEUED)
        self.assertEqual(job.progress, 0.0)
        self.assertFalse(job.is_complete)
        self.assertFalse(job.is_active)

    def test_render_job_str(self):
        """Test RenderJob string representation."""
        job = RenderJob.objects.create(
            user=self.user,
            project=self.project,
            status=RenderJob.STATUS_RENDERING
        )

        str_repr = str(job)
        self.assertIn(str(job.id), str_repr)
        self.assertIn('Test Project', str_repr)
        self.assertIn('Rendering', str_repr)

    def test_is_active_property(self):
        """Test is_active property for different statuses."""
        # Queued - not active
        job = RenderJob.objects.create(user=self.user, status=RenderJob.STATUS_QUEUED)
        self.assertFalse(job.is_active)

        # Dispatching - active
        job.status = RenderJob.STATUS_DISPATCHING
        job.save()
        self.assertTrue(job.is_active)

        # Rendering - active
        job.status = RenderJob.STATUS_RENDERING
        job.save()
        self.assertTrue(job.is_active)

        # Done - not active
        job.status = RenderJob.STATUS_DONE
        job.save()
        self.assertFalse(job.is_active)

    def test_is_complete_property(self):
        """Test is_complete property for different statuses."""
        job = RenderJob.objects.create(user=self.user, status=RenderJob.STATUS_RENDERING)
        self.assertFalse(job.is_complete)

        job.status = RenderJob.STATUS_DONE
        job.save()
        self.assertTrue(job.is_complete)

        job.status = RenderJob.STATUS_ERROR
        job.save()
        self.assertTrue(job.is_complete)

    def test_progress_percentage(self):
        """Test progress_percentage property."""
        job = RenderJob.objects.create(user=self.user, progress=0.567)
        self.assertEqual(job.progress_percentage, 56.7)

        job.progress = 0.0
        self.assertEqual(job.progress_percentage, 0.0)

        job.progress = 1.0
        self.assertEqual(job.progress_percentage, 100.0)


class RenderJobAPITest(TestCase):
    """Test RenderJob API endpoints."""

    def setUp(self):
        """Set up test client, user, and auth."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.project = CreativeProject.objects.create(
            user=self.user,
            name='Test Project',
            description='Test project'
        )
        self.session = AISession.objects.create(
            user=self.user,
            title='Test Session'
        )

    @patch('rendering.views._call_resolve_node')
    def test_create_render_job_success(self, mock_resolve_call):
        """Test successfully creating a render job."""
        # Mock Resolve Node response
        mock_resolve_call.return_value = (
            True,
            {'job_id': '12345678-1234-1234-1234-123456789012', 'status': 'queued'},
            None
        )

        url = reverse('rendering:create_render_job')
        data = {
            'project_id': str(self.project.project_id),
            'session_id': str(self.session.session_id),
            'timeline_name': 'My Timeline',
            'template': 'default_mp4'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], RenderJob.STATUS_RENDERING)

        # Verify job was created in DB
        job = RenderJob.objects.get(id=response.data['id'])
        self.assertEqual(job.user, self.user)
        self.assertEqual(job.project, self.project)
        self.assertIsNotNone(job.node_job_id)

    @patch('rendering.views._call_resolve_node')
    def test_create_render_job_resolve_node_error(self, mock_resolve_call):
        """Test render job creation when Resolve Node fails."""
        # Mock Resolve Node error
        mock_resolve_call.return_value = (
            False,
            {},
            'Resolve Node timeout after 30s'
        )

        url = reverse('rendering:create_render_job')
        data = {
            'project_id': str(self.project.project_id),
            'template': 'default_mp4'
        }

        response = self.client.post(url, data, format='json')

        # Job is still created but with error status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], RenderJob.STATUS_ERROR)
        self.assertIn('Resolve Node timeout', response.data['error_message'])

    def test_create_render_job_invalid_project(self):
        """Test creating render job with non-existent project."""
        url = reverse('rendering:create_render_job')
        data = {
            'project_id': '12345678-1234-1234-1234-123456789012',  # Doesn't exist
            'template': 'default_mp4'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_create_render_job_other_user_project(self):
        """Test creating render job with another user's project."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_project = CreativeProject.objects.create(
            user=other_user,
            name='Other Project'
        )

        url = reverse('rendering:create_render_job')
        data = {
            'project_id': str(other_project.project_id),
            'template': 'default_mp4'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_render_job(self):
        """Test retrieving a render job."""
        job = RenderJob.objects.create(
            user=self.user,
            project=self.project,
            status=RenderJob.STATUS_DONE,
            progress=1.0,
            result_url='http://example.com/render.mp4'
        )

        url = reverse('rendering:get_render_job', args=[job.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(job.id))
        self.assertEqual(response.data['status'], RenderJob.STATUS_DONE)
        self.assertEqual(response.data['progress'], 1.0)
        self.assertEqual(response.data['result_url'], 'http://example.com/render.mp4')

    @patch('rendering.views._call_resolve_node')
    def test_get_render_job_with_polling(self, mock_resolve_call):
        """Test getting active render job polls Resolve Node."""
        job = RenderJob.objects.create(
            user=self.user,
            status=RenderJob.STATUS_RENDERING,
            node_job_id='12345678-1234-1234-1234-123456789012',
            progress=0.5
        )

        # Mock Resolve Node status response
        mock_resolve_call.return_value = (
            True,
            {
                'status': 'rendering',
                'progress': 0.75,
            },
            None
        )

        url = reverse('rendering:get_render_job', args=[job.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 0.75)  # Updated from poll

        # Verify Resolve Node was called
        mock_resolve_call.assert_called_once()

    def test_get_render_job_permission_denied(self):
        """Test getting another user's render job."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_job = RenderJob.objects.create(
            user=other_user,
            status=RenderJob.STATUS_DONE
        )

        url = reverse('rendering:get_render_job', args=[other_job.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_render_jobs(self):
        """Test listing user's render jobs."""
        # Create jobs for this user
        job1 = RenderJob.objects.create(user=self.user, status=RenderJob.STATUS_DONE)
        job2 = RenderJob.objects.create(user=self.user, status=RenderJob.STATUS_RENDERING)

        # Create job for another user (should not appear)
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pass')
        RenderJob.objects.create(user=other_user, status=RenderJob.STATUS_DONE)

        url = reverse('rendering:list_render_jobs')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 2)

        job_ids = [j['id'] for j in response.data['jobs']]
        self.assertIn(str(job1.id), job_ids)
        self.assertIn(str(job2.id), job_ids)

    def test_list_render_jobs_filtered_by_project(self):
        """Test listing render jobs filtered by project."""
        project2 = CreativeProject.objects.create(
            user=self.user,
            name='Project 2'
        )

        job1 = RenderJob.objects.create(user=self.user, project=self.project)
        job2 = RenderJob.objects.create(user=self.user, project=project2)

        url = reverse('rendering:list_render_jobs')
        response = self.client.get(url, {'project_id': str(self.project.project_id)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['jobs'][0]['id'], str(job1.id))

    def test_list_render_jobs_unauthenticated(self):
        """Test listing jobs without authentication."""
        self.client.force_authenticate(user=None)

        url = reverse('rendering:list_render_jobs')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
