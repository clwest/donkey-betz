"""
MiniFig API Tests

Session 111 - Phase 7
Tests for MiniFig asset REST API endpoints
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from content.models import MiniFigAsset, ImageHistory
import json
import uuid

User = get_user_model()


class MiniFigAPITests(TestCase):
    """Test MiniFig REST API endpoints"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test image (for source reference)
        self.test_image = ImageHistory.objects.create(
            user=self.user,
            filename='test_character.png',
            file_path='/media/test/test_character.png',
            prompt='test character',
            model_used='test-model'
        )

        # Create test minifigs
        self.minifig1 = MiniFigAsset.objects.create(
            user=self.user,
            title='Test MiniFig 1',
            provider='placeholder',
            status='completed',
            three_d_file='https://example.com/minifig1.stl',
            preview_image_url='https://example.com/preview1.png',
            metadata={'style': 'cartoon', 'scale': '28mm'},
            source_image_asset=self.test_image,
        )

        self.minifig2 = MiniFigAsset.objects.create(
            user=self.user,
            title='Test MiniFig 2',
            provider='placeholder',
            status='processing',
            three_d_file='https://example.com/minifig2.stl',
            metadata={'style': 'realistic', 'scale': '32mm'},
        )

        self.minifig3 = MiniFigAsset.objects.create(
            user=self.user,
            title='Test MiniFig 3',
            provider='placeholder',
            status='failed',
            three_d_file='',
            error_message='Test error',
            metadata={'style': 'pixel_art', 'scale': '28mm'},
        )

    def test_list_minifigs_requires_authentication(self):
        """Test that list endpoint requires authentication"""
        response = self.client.get('/api/v1/content/minifigs/')
        # Should require auth (redirect to login or 403/401)
        self.assertIn(response.status_code, [302, 401, 403])

    def test_list_minifigs_with_authentication(self):
        """Test authenticated user can list their minifigs"""
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/content/minifigs/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['success'])
        self.assertEqual(len(data['minifigs']), 3)
        self.assertEqual(data['total'], 3)

    def test_list_minifigs_returns_correct_structure(self):
        """Test list endpoint returns correct JSON structure"""
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/content/minifigs/')
        data = json.loads(response.content)

        # Check top-level keys
        self.assertIn('success', data)
        self.assertIn('minifigs', data)
        self.assertIn('count', data)
        self.assertIn('total', data)
        self.assertIn('limit', data)
        self.assertIn('offset', data)

        # Check minifig structure
        minifig = data['minifigs'][0]
        self.assertIn('id', minifig)
        self.assertIn('title', minifig)
        self.assertIn('provider', minifig)
        self.assertIn('status', minifig)
        self.assertIn('three_d_file', minifig)
        self.assertIn('preview_image_url', minifig)
        self.assertIn('is_favorite', minifig)
        self.assertIn('view_count', minifig)
        self.assertIn('download_count', minifig)
        self.assertIn('created_at', minifig)
        self.assertIn('updated_at', minifig)

    def test_list_minifigs_pagination(self):
        """Test pagination with limit and offset"""
        self.client.force_login(self.user)

        # Test limit
        response = self.client.get('/api/v1/content/minifigs/?limit=2')
        data = json.loads(response.content)
        self.assertEqual(len(data['minifigs']), 2)
        self.assertEqual(data['limit'], 2)

        # Test offset
        response = self.client.get('/api/v1/content/minifigs/?limit=2&offset=2')
        data = json.loads(response.content)
        self.assertEqual(len(data['minifigs']), 1)
        self.assertEqual(data['offset'], 2)

    def test_list_minifigs_status_filter(self):
        """Test filtering by status"""
        self.client.force_login(self.user)

        # Filter by completed
        response = self.client.get('/api/v1/content/minifigs/?status=completed')
        data = json.loads(response.content)
        self.assertEqual(len(data['minifigs']), 1)
        self.assertEqual(data['minifigs'][0]['status'], 'completed')

        # Filter by processing
        response = self.client.get('/api/v1/content/minifigs/?status=processing')
        data = json.loads(response.content)
        self.assertEqual(len(data['minifigs']), 1)
        self.assertEqual(data['minifigs'][0]['status'], 'processing')

        # Filter by failed
        response = self.client.get('/api/v1/content/minifigs/?status=failed')
        data = json.loads(response.content)
        self.assertEqual(len(data['minifigs']), 1)
        self.assertEqual(data['minifigs'][0]['status'], 'failed')

    def test_list_minifigs_max_limit(self):
        """Test that limit is capped at 100"""
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/content/minifigs/?limit=1000')
        data = json.loads(response.content)
        self.assertEqual(data['limit'], 100)

    def test_list_minifigs_ordered_by_created_desc(self):
        """Test that minifigs are ordered by created_at descending"""
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/content/minifigs/')
        data = json.loads(response.content)

        # First minifig should be the most recently created
        # (minifig3 was created last in setUp)
        self.assertEqual(data['minifigs'][0]['title'], 'Test MiniFig 3')

    def test_get_minifig_detail_requires_authentication(self):
        """Test that detail endpoint requires authentication"""
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig1.id}/')
        self.assertIn(response.status_code, [302, 401, 403])

    def test_get_minifig_detail_with_authentication(self):
        """Test authenticated user can get minifig details"""
        self.client.force_login(self.user)
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig1.id}/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['success'])
        self.assertIn('minifig', data)
        self.assertEqual(data['minifig']['id'], str(self.minifig1.id))

    def test_get_minifig_detail_returns_full_structure(self):
        """Test detail endpoint returns complete minifig data"""
        self.client.force_login(self.user)
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig1.id}/')
        data = json.loads(response.content)

        minifig = data['minifig']

        # Core fields
        self.assertEqual(minifig['id'], str(self.minifig1.id))
        self.assertEqual(minifig['title'], 'Test MiniFig 1')
        self.assertEqual(minifig['provider'], 'placeholder')
        self.assertEqual(minifig['status'], 'completed')

        # Metadata
        self.assertIn('metadata', minifig)
        self.assertEqual(minifig['metadata']['style'], 'cartoon')
        self.assertEqual(minifig['metadata']['scale'], '28mm')

        # User organization
        self.assertIn('user_notes', minifig)
        self.assertIn('tags', minifig)
        self.assertIn('is_favorite', minifig)

        # Analytics
        self.assertIn('view_count', minifig)
        self.assertIn('download_count', minifig)

        # Source references
        self.assertIn('source_image_asset', minifig)
        self.assertIsNotNone(minifig['source_image_asset'])

    def test_get_minifig_detail_increments_view_count(self):
        """Test that viewing detail increments view_count"""
        self.client.force_login(self.user)

        initial_count = self.minifig1.view_count

        # View the minifig
        self.client.get(f'/api/v1/content/minifigs/{self.minifig1.id}/')

        # Refresh from database
        self.minifig1.refresh_from_db()

        # View count should have incremented
        self.assertEqual(self.minifig1.view_count, initial_count + 1)

    def test_get_minifig_detail_not_found(self):
        """Test that non-existent minifig returns 404"""
        self.client.force_login(self.user)

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/content/minifigs/{fake_uuid}/')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_get_minifig_detail_user_isolation(self):
        """Test that users can only access their own minifigs"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Try to access minifig1 as other_user
        self.client.force_login(other_user)
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig1.id}/')

        # Should return 404 (not found, not unauthorized)
        self.assertEqual(response.status_code, 404)

    def test_list_minifigs_user_isolation(self):
        """Test that users only see their own minifigs"""
        # Create another user with minifigs
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        MiniFigAsset.objects.create(
            user=other_user,
            title='Other User MiniFig',
            provider='placeholder',
            status='completed',
            three_d_file='https://example.com/other.stl',
        )

        # Login as original user
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/content/minifigs/')
        data = json.loads(response.content)

        # Should only see own minifigs (3)
        self.assertEqual(len(data['minifigs']), 3)

        # Verify all returned minifigs belong to current user
        for minifig in data['minifigs']:
            self.assertNotEqual(minifig['title'], 'Other User MiniFig')

    def test_get_minifig_detail_with_no_source_references(self):
        """Test detail endpoint when source references are null"""
        self.client.force_login(self.user)
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig2.id}/')
        data = json.loads(response.content)

        # Should handle null source references gracefully
        self.assertIsNone(data['minifig']['source_pipeline_run'])
        self.assertIsNone(data['minifig']['source_image_asset'])

    def test_get_minifig_detail_with_error_message(self):
        """Test detail endpoint returns error_message for failed minifigs"""
        self.client.force_login(self.user)
        response = self.client.get(f'/api/v1/content/minifigs/{self.minifig3.id}/')
        data = json.loads(response.content)

        self.assertEqual(data['minifig']['status'], 'failed')
        self.assertEqual(data['minifig']['error_message'], 'Test error')
