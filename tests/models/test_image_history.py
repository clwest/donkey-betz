# tests/models/test_image_history.py
"""Tests for ImageHistory model."""
import pytest
from django.db.models import F
from tests.factories import ImageHistoryFactory, UserFactory, CreativeProjectFactory

pytestmark = pytest.mark.django_db


class TestImageHistoryModel:
    """Tests for ImageHistory model."""

    def test_create_image_history(self, user, project):
        """Test creating a basic image history record."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test_image.png',
            file_path='generated_images/test/test_image.png',
            image_type='generated',
            prompt='A beautiful sunset',
            parameters={'width': 1024, 'height': 1024},
            model_used='ultra'
        )

        assert image.id is not None
        assert image.prompt == 'A beautiful sunset'
        assert image.user == user
        assert image.project == project

    def test_sequential_number_auto_assignment(self, user, project):
        """Test that sequential numbers are auto-assigned on creation."""
        img1 = ImageHistoryFactory(user=user, project=project)
        img2 = ImageHistoryFactory(user=user, project=project)

        assert img1.sequential_number is not None
        assert img2.sequential_number is not None
        assert img2.sequential_number == img1.sequential_number + 1

    def test_sequential_number_per_user(self, db):
        """Test that sequential numbers are independent per user."""
        user1 = UserFactory()
        user2 = UserFactory()

        img1_user1 = ImageHistoryFactory(user=user1)
        img2_user1 = ImageHistoryFactory(user=user1)
        img1_user2 = ImageHistoryFactory(user=user2)

        # User 1's images should be sequential
        assert img2_user1.sequential_number == img1_user1.sequential_number + 1

        # User 2's first image should start fresh
        assert img1_user2.sequential_number == 1

    def test_get_sequential_number_method(self, user, project):
        """Test get_sequential_number returns the stored value."""
        image = ImageHistoryFactory(user=user, project=project)

        assert image.get_sequential_number() == image.sequential_number

    def test_get_sequential_number_legacy_fallback(self, user, project):
        """Test get_sequential_number falls back to calculation for legacy images."""
        from content.models import ImageHistory

        # Create an image without sequential_number (simulating legacy data)
        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='legacy_image.png',
            file_path='generated_images/test/legacy.png',
            image_type='generated',
            prompt='Legacy image',
            model_used='ultra'
        )

        # Manually set sequential_number to None to simulate legacy
        ImageHistory.objects.filter(pk=image.pk).update(sequential_number=None)
        image.refresh_from_db()

        # Should calculate based on position
        assert image.get_sequential_number() >= 1

    def test_parameters_json_field(self, user, project):
        """Test parameters JSONField stores and retrieves correctly."""
        from content.models import ImageHistory

        params = {
            'width': 1024,
            'height': 768,
            'style': 'cinematic',
            'negative_prompt': 'blurry',
            'cfg_scale': 7.5
        }

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test.png',
            file_path='test/test.png',
            image_type='generated',
            prompt='Test',
            parameters=params,
            model_used='ultra'
        )

        image.refresh_from_db()
        assert image.parameters == params
        assert image.parameters['cfg_scale'] == 7.5

    def test_string_representation(self, user, project):
        """Test __str__ method."""
        image = ImageHistoryFactory(
            user=user,
            project=project,
            image_type='generated',
            filename='my_image.png'
        )

        string_repr = str(image)
        assert user.username in string_repr
        assert 'generated' in string_repr

    def test_increment_view_count(self, user, project):
        """Test atomic view count increment."""
        image = ImageHistoryFactory(user=user, project=project)
        initial_count = image.view_count

        image.increment_view_count()

        assert image.view_count == initial_count + 1

    def test_increment_download_count(self, user, project):
        """Test atomic download count increment."""
        image = ImageHistoryFactory(user=user, project=project)
        initial_count = image.download_count

        image.increment_download_count()

        assert image.download_count == initial_count + 1

    def test_parent_child_lineage(self, user, project):
        """Test parent-child image relationships."""
        parent = ImageHistoryFactory(user=user, project=project, image_type='generated')
        child = ImageHistoryFactory(
            user=user,
            project=project,
            image_type='upscaled_fast',
            parent_image=parent
        )

        assert child.parent_image == parent
        assert parent.child_images.first() == child

    def test_tags_json_field(self, user, project):
        """Test tags JSONField for list storage."""
        from content.models import ImageHistory

        tags = ['sunset', 'ocean', 'beautiful', 'ai-generated']

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test.png',
            file_path='test/test.png',
            image_type='generated',
            prompt='Test',
            tags=tags,
            model_used='ultra'
        )

        image.refresh_from_db()
        assert image.tags == tags
        assert 'sunset' in image.tags

    def test_is_favorite_toggle(self, user, project):
        """Test favorite boolean field."""
        image = ImageHistoryFactory(user=user, project=project, is_favorite=False)
        assert not image.is_favorite

        image.is_favorite = True
        image.save()
        image.refresh_from_db()

        assert image.is_favorite

    def test_get_full_url_data_uri(self, user, project):
        """Test get_full_url returns data URI directly."""
        from content.models import ImageHistory

        data_uri = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=='

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='data_uri_image.png',
            file_path=data_uri,
            image_type='generated',
            prompt='Test',
            model_used='ultra'
        )

        assert image.get_full_url() == data_uri

    def test_batch_selection_fields(self, user, project):
        """Test batch generation fields for CreativeDirectorAgent."""
        import uuid
        from content.models import ImageHistory

        batch_id = uuid.uuid4()

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='batch_image.png',
            file_path='test/batch.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra',
            seed=12345678901234,  # Big integer seed
            generation_batch_id=batch_id,
            option_number=1,
            was_selected=True
        )

        image.refresh_from_db()
        assert image.seed == 12345678901234
        assert image.generation_batch_id == batch_id
        assert image.option_number == 1
        assert image.was_selected is True

    def test_model_used_choices(self, user, project):
        """Test model_used field accepts valid choices."""
        from content.models import ImageHistory

        valid_models = ['core', 'sdxl', 'sd3', 'ultra']

        for model in valid_models:
            image = ImageHistory.objects.create(
                user=user,
                project=project,
                filename=f'{model}_image.png',
                file_path=f'test/{model}.png',
                image_type='generated',
                prompt='Test',
                model_used=model
            )
            assert image.model_used == model

    def test_image_type_choices(self, user, project):
        """Test image_type field accepts valid choices."""
        from content.models import ImageHistory

        valid_types = [
            'generated', 'erased', 'inpainted', 'outpainted',
            'upscaled_fast', 'upscaled_conservative', 'upscaled_creative',
            'recolored', 'background_removed', 'sketch_control', 'structure_control'
        ]

        for img_type in valid_types:
            image = ImageHistory.objects.create(
                user=user,
                project=project,
                filename=f'{img_type}_image.png',
                file_path=f'test/{img_type}.png',
                image_type=img_type,
                prompt='Test',
                model_used='ultra'
            )
            assert image.image_type == img_type

    def test_image_metadata_fields(self, user, project):
        """Test image metadata fields."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='metadata_test.png',
            file_path='test/metadata.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra',
            image_width=1920,
            image_height=1080,
            file_size_bytes=1024000,
            style='cinematic'
        )

        assert image.image_width == 1920
        assert image.image_height == 1080
        assert image.file_size_bytes == 1024000
        assert image.style == 'cinematic'

    def test_project_relationship_optional(self, user):
        """Test that project can be null."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=None,  # No project
            filename='no_project.png',
            file_path='test/no_project.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra'
        )

        assert image.project is None

    def test_session_relationship_optional(self, user, project):
        """Test that session can be null."""
        image = ImageHistoryFactory(user=user, project=project)
        assert image.session is None  # Should be None by default

    def test_ordering(self, user, project):
        """Test default ordering is by -created_at."""
        from content.models import ImageHistory
        import time

        img1 = ImageHistoryFactory(user=user, project=project)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        img2 = ImageHistoryFactory(user=user, project=project)
        time.sleep(0.01)
        img3 = ImageHistoryFactory(user=user, project=project)

        images = list(ImageHistory.objects.filter(user=user))

        # Most recent first
        assert images[0] == img3
        assert images[1] == img2
        assert images[2] == img1

    def test_version_increment_on_save(self, user, project):
        """Test version auto-increments on updates."""
        image = ImageHistoryFactory(user=user, project=project)
        initial_version = image.version

        image.prompt = 'Updated prompt'
        image.save()

        assert image.version == initial_version + 1
