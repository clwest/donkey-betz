# tests/models/test_minifig_asset.py
"""Tests for MiniFigAsset model.

Session 452: Updated tests to use correct field names:
- source_image_asset (not source_image)
- title (not name)
- local_glb_path (not glb_file_path)
- three_d_file (URLField, required)
- No stl_file_path field exists
- No replicate_* fields exist
- No generation_* timing fields exist
"""
import pytest
from tests.factories import MiniFigAssetFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestMiniFigAssetModel:
    """Tests for MiniFigAsset model."""

    def test_create_minifig_asset(self, user, project, image_history):
        """Test creating a basic MiniFigAsset."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Test MiniFig',
            status='completed',
            three_d_file='https://example.com/model.glb'
        )

        assert asset.id is not None
        assert asset.title == 'Test MiniFig'
        assert asset.user == user
        assert asset.source_image_asset == image_history

    def test_status_choices(self, user, project, image_history):
        """Test status field accepts valid choices."""
        from content.models import MiniFigAsset

        valid_statuses = ['pending', 'processing', 'completed', 'failed']

        for status in valid_statuses:
            asset = MiniFigAsset.objects.create(
                user=user,
                project=project,
                source_image_asset=image_history,
                title=f'{status} MiniFig',
                status=status,
                three_d_file=f'https://example.com/{status}.glb'
            )
            assert asset.status == status

    def test_get_sequential_number(self, user, project, image_history):
        """Test get_sequential_number returns correct value."""
        asset1 = MiniFigAssetFactory(user=user)
        asset2 = MiniFigAssetFactory(user=user)

        # Check sequential numbering
        assert asset1.get_sequential_number() == 1
        assert asset2.get_sequential_number() == 2

    def test_sequential_number_per_user(self, db):
        """Test sequential numbers are independent per user."""
        user1 = UserFactory()
        user2 = UserFactory()

        asset1 = MiniFigAssetFactory(user=user1)
        asset2 = MiniFigAssetFactory(user=user1)
        asset3 = MiniFigAssetFactory(user=user2)

        assert asset2.get_sequential_number() == 2
        assert asset3.get_sequential_number() == 1  # New user, starts at 1

    def test_file_paths(self, user, project, image_history):
        """Test GLB file path storage."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Test MiniFig',
            status='completed',
            three_d_file='https://example.com/model.glb',
            local_glb_path='minifigs/test/model.glb'
        )

        assert asset.local_glb_path == 'minifigs/test/model.glb'
        assert 'model.glb' in asset.three_d_file

    def test_three_d_file_url(self, user, project, image_history):
        """Test 3D file URL storage."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Test MiniFig',
            status='processing',
            three_d_file='https://replicate.delivery/model.glb',
            preview_image_url='https://replicate.delivery/preview.png'
        )

        assert 'replicate.delivery' in asset.three_d_file
        assert 'replicate.delivery' in asset.preview_image_url

    def test_error_message_on_failure(self, user, project, image_history):
        """Test error message storage for failed conversions."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Failed MiniFig',
            status='failed',
            three_d_file='',
            error_message='API timeout after 300 seconds'
        )

        assert asset.status == 'failed'
        assert asset.error_message == 'API timeout after 300 seconds'

    def test_metadata_json_field(self, user, project, image_history):
        """Test metadata JSONField stores custom data."""
        from content.models import MiniFigAsset

        metadata = {
            'vertex_count': 12000,
            'face_count': 24000,
            'scale_factor': 1.5,
            'repair_applied': True
        }

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Test MiniFig',
            three_d_file='https://example.com/model.glb',
            metadata=metadata
        )

        asset.refresh_from_db()
        assert asset.metadata['vertex_count'] == 12000
        assert asset.metadata['repair_applied'] is True

    def test_source_image_relationship(self, user, project, image_history):
        """Test reverse relationship from image."""
        asset = MiniFigAssetFactory(
            user=user,
            source_image_asset=image_history
        )

        # Check reverse relationship (related_name='generated_minifigs')
        assert asset in image_history.generated_minifigs.all()

    def test_project_relationship_optional(self, user, image_history):
        """Test that project can be null."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=None,
            source_image_asset=image_history,
            title='No Project MiniFig',
            three_d_file='https://example.com/model.glb'
        )

        assert asset.project is None

    def test_source_image_optional(self, user, project):
        """Test that source_image_asset can be null."""
        from content.models import MiniFigAsset

        # source_image_asset is allowed to be null
        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=None,
            title='No Source MiniFig',
            three_d_file='https://example.com/model.glb'
        )
        assert asset.source_image_asset is None

    def test_string_representation(self, user, project, image_history):
        """Test __str__ method."""
        asset = MiniFigAssetFactory(
            user=user,
            title='My Custom MiniFig'
        )

        string_repr = str(asset)
        # __str__ returns f"{self.user.username} - {self.title}"
        assert user.username in string_repr
        assert 'My Custom MiniFig' in string_repr

    def test_ordering(self, user, project, image_history):
        """Test default ordering is by -created_at."""
        from content.models import MiniFigAsset
        import time

        asset1 = MiniFigAssetFactory(user=user)
        time.sleep(0.01)
        asset2 = MiniFigAssetFactory(user=user)
        time.sleep(0.01)
        asset3 = MiniFigAssetFactory(user=user)

        assets = list(MiniFigAsset.objects.filter(user=user))

        # Most recent first
        assert assets[0] == asset3
        assert assets[1] == asset2
        assert assets[2] == asset1

    def test_download_count_increment(self, user, project, image_history):
        """Test download count increment method."""
        asset = MiniFigAssetFactory(user=user)
        initial_count = asset.download_count

        asset.increment_download_count()

        assert asset.download_count == initial_count + 1

    def test_view_count_increment(self, user, project, image_history):
        """Test view count increment method."""
        asset = MiniFigAssetFactory(user=user)
        initial_count = asset.view_count

        asset.increment_view_count()

        assert asset.view_count == initial_count + 1

    def test_favorite_toggle(self, user, project, image_history):
        """Test is_favorite field."""
        from content.models import MiniFigAsset

        asset = MiniFigAsset.objects.create(
            user=user,
            project=project,
            source_image_asset=image_history,
            title='Test MiniFig',
            three_d_file='https://example.com/model.glb',
            is_favorite=False
        )

        assert asset.is_favorite is False

        asset.is_favorite = True
        asset.save()
        asset.refresh_from_db()

        assert asset.is_favorite is True
