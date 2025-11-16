"""
MiniFig Services Tests

Session 111 - Phase 7
Tests for MiniFig creation service layer and pipeline execution
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from content.models import ImageHistory, MiniFigAsset
from content import minifig_services

User = get_user_model()


class MiniFigServicesTests(TestCase):
    """Test MiniFig service layer functions"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test images
        self.image1 = ImageHistory.objects.create(
            user=self.user,
            filename='character_front.png',
            file_path='/media/test/character_front.png',
            prompt='character front view',
            model_used='test-model'
        )

        self.image2 = ImageHistory.objects.create(
            user=self.user,
            filename='character_back.png',
            file_path='/media/test/character_back.png',
            prompt='character back view',
            model_used='test-model'
        )

        self.image3 = ImageHistory.objects.create(
            user=self.user,
            filename='character_side.png',
            file_path='/media/test/character_side.png',
            prompt='character side view',
            model_used='test-model'
        )

        self.image4 = ImageHistory.objects.create(
            user=self.user,
            filename='character_detail.png',
            file_path='/media/test/character_detail.png',
            prompt='character detail',
            model_used='test-model'
        )

    def test_create_minifig_from_single_image(self):
        """Test creating mini-fig from a single image"""
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)],
            style='toy',
            scale='medium'
        )

        self.assertEqual(len(minifigs), 1)
        minifig = minifigs[0]

        # Verify basic fields
        self.assertEqual(minifig.user, self.user)
        self.assertEqual(minifig.provider, 'placeholder')
        self.assertEqual(minifig.status, 'completed')

        # Verify metadata
        self.assertEqual(minifig.metadata['style'], 'toy')
        self.assertEqual(minifig.metadata['scale'], 'medium')
        self.assertEqual(minifig.metadata['source_image_id'], str(self.image1.id))

        # Verify 3D file URL generated
        self.assertTrue(minifig.three_d_file)
        self.assertIn('placeholder', minifig.three_d_file)

    def test_create_minifig_from_multiple_images(self):
        """Test creating mini-figs from multiple images"""
        image_ids = [str(self.image1.id), str(self.image2.id), str(self.image3.id)]

        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=image_ids,
            style='realistic',
            scale='large'
        )

        self.assertEqual(len(minifigs), 3)

        # Verify all minifigs created
        for minifig in minifigs:
            self.assertEqual(minifig.user, self.user)
            self.assertEqual(minifig.status, 'completed')
            self.assertEqual(minifig.metadata['style'], 'realistic')
            self.assertEqual(minifig.metadata['scale'], 'large')

    def test_create_minifig_max_four_images(self):
        """Test that maximum 4 images are allowed"""
        # Create a 5th image
        image5 = ImageHistory.objects.create(
            user=self.user,
            filename='extra.png',
            file_path='/media/test/extra.png',
            prompt='extra image',
            model_used='test-model'
        )

        image_ids = [
            str(self.image1.id),
            str(self.image2.id),
            str(self.image3.id),
            str(self.image4.id),
            str(image5.id)
        ]

        with self.assertRaises(ValueError) as context:
            minifig_services.create_minifig_asset_from_images(
                user=self.user,
                image_asset_ids=image_ids
            )

        self.assertIn('Maximum 4 image assets allowed', str(context.exception))

    def test_create_minifig_requires_at_least_one_image(self):
        """Test that at least 1 image is required"""
        with self.assertRaises(ValueError) as context:
            minifig_services.create_minifig_asset_from_images(
                user=self.user,
                image_asset_ids=[]
            )

        self.assertIn('At least 1 image asset ID is required', str(context.exception))

    def test_create_minifig_validates_image_ownership(self):
        """Test that images must belong to the user"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Try to use image1 (belongs to self.user) as other_user
        with self.assertRaises(ValueError) as context:
            minifig_services.create_minifig_asset_from_images(
                user=other_user,
                image_asset_ids=[str(self.image1.id)]
            )

        self.assertIn("don't belong to user", str(context.exception))

    def test_create_minifig_validates_image_exists(self):
        """Test that images must exist in database"""
        fake_id = '00000000-0000-0000-0000-000000000000'

        with self.assertRaises(ValueError) as context:
            minifig_services.create_minifig_asset_from_images(
                user=self.user,
                image_asset_ids=[fake_id]
            )

        self.assertIn("not found or don't belong to user", str(context.exception))

    def test_create_minifig_generates_title(self):
        """Test that title is generated from image filename"""
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )

        minifig = minifigs[0]
        self.assertIn('character_front.png', minifig.title)

    def test_create_minifig_with_pipeline_run(self):
        """Test creating mini-fig with pipeline_run reference"""
        # This would require creating a CreativePipelineRun
        # For now, just test passing None works
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)],
            pipeline_run=None
        )

        self.assertEqual(len(minifigs), 1)
        self.assertIsNone(minifigs[0].source_pipeline_run)

    def test_update_minifig_status_to_processing(self):
        """Test updating minifig status to processing"""
        # Create a minifig
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )
        minifig = minifigs[0]

        # Update to processing
        updated = minifig_services.update_minifig_status(
            minifig_id=str(minifig.id),
            status='processing'
        )

        self.assertEqual(updated.status, 'processing')

    def test_update_minifig_status_to_failed(self):
        """Test updating minifig status to failed with error message"""
        # Create a minifig
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )
        minifig = minifigs[0]

        # Update to failed
        error_msg = 'Test error message'
        updated = minifig_services.update_minifig_status(
            minifig_id=str(minifig.id),
            status='failed',
            error_message=error_msg
        )

        self.assertEqual(updated.status, 'failed')
        self.assertEqual(updated.error_message, error_msg)

    def test_update_minifig_status_invalid_status(self):
        """Test that invalid status raises ValueError"""
        # Create a minifig
        minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )
        minifig = minifigs[0]

        with self.assertRaises(ValueError) as context:
            minifig_services.update_minifig_status(
                minifig_id=str(minifig.id),
                status='invalid_status'
            )

        self.assertIn('Invalid status', str(context.exception))

    def test_update_minifig_status_nonexistent_minifig(self):
        """Test updating non-existent minifig raises ValueError"""
        fake_id = '00000000-0000-0000-0000-000000000000'

        with self.assertRaises(ValueError) as context:
            minifig_services.update_minifig_status(
                minifig_id=fake_id,
                status='completed'
            )

        self.assertIn('not found', str(context.exception))

    def test_get_user_minifigs_all(self):
        """Test getting all minifigs for a user"""
        # Create multiple minifigs
        minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )
        minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image2.id)]
        )

        minifigs = minifig_services.get_user_minifigs(user=self.user)

        self.assertEqual(minifigs.count(), 2)

    def test_get_user_minifigs_filtered_by_status(self):
        """Test filtering minifigs by status"""
        # Create completed minifig
        completed = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )[0]

        # Create and update to failed
        failed_minifigs = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image2.id)]
        )
        minifig_services.update_minifig_status(
            str(failed_minifigs[0].id),
            'failed',
            'Test error'
        )

        # Get completed only
        completed_list = minifig_services.get_user_minifigs(
            user=self.user,
            status='completed'
        )
        self.assertEqual(completed_list.count(), 1)
        self.assertEqual(completed_list.first().status, 'completed')

        # Get failed only
        failed_list = minifig_services.get_user_minifigs(
            user=self.user,
            status='failed'
        )
        self.assertEqual(failed_list.count(), 1)
        self.assertEqual(failed_list.first().status, 'failed')

    def test_get_user_minifigs_ordered_by_created_desc(self):
        """Test that minifigs are ordered by created_at descending"""
        # Create minifigs in sequence
        minifig1 = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )[0]

        minifig2 = minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image2.id)]
        )[0]

        minifigs = minifig_services.get_user_minifigs(user=self.user)

        # Most recent first
        self.assertEqual(minifigs.first().id, minifig2.id)
        self.assertEqual(minifigs.last().id, minifig1.id)

    def test_get_user_minifigs_user_isolation(self):
        """Test that users only see their own minifigs"""
        # Create minifig for user1
        minifig_services.create_minifig_asset_from_images(
            user=self.user,
            image_asset_ids=[str(self.image1.id)]
        )

        # Create another user with minifig
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        other_image = ImageHistory.objects.create(
            user=other_user,
            filename='other.png',
            file_path='/media/test/other.png',
            prompt='other image',
            model_used='test-model'
        )

        minifig_services.create_minifig_asset_from_images(
            user=other_user,
            image_asset_ids=[str(other_image.id)]
        )

        # Verify isolation
        user1_minifigs = minifig_services.get_user_minifigs(user=self.user)
        user2_minifigs = minifig_services.get_user_minifigs(user=other_user)

        self.assertEqual(user1_minifigs.count(), 1)
        self.assertEqual(user2_minifigs.count(), 1)
        self.assertNotEqual(user1_minifigs.first().id, user2_minifigs.first().id)
