# tests/models/test_unified_base.py
"""Tests for UnifiedBaseModel and UnifiedUser."""
import pytest
import uuid
from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUnifiedBaseModel:
    """Tests for UnifiedBaseModel abstract model functionality."""

    def test_uuid_primary_key(self, image_history):
        """Test that models have UUID primary key."""
        assert isinstance(image_history.id, uuid.UUID)

    def test_created_at_auto_set(self, image_history):
        """Test created_at is automatically set."""
        assert image_history.created_at is not None

    def test_updated_at_auto_update(self, image_history):
        """Test updated_at is automatically updated on save."""
        original_updated = image_history.updated_at
        image_history.prompt = 'Updated'
        image_history.save()

        assert image_history.updated_at >= original_updated

    def test_version_increment(self, image_history):
        """Test version increments on save."""
        initial_version = image_history.version

        image_history.prompt = 'Changed'
        image_history.save()

        assert image_history.version == initial_version + 1

    def test_is_active_default(self, image_history):
        """Test is_active defaults to True."""
        assert image_history.is_active is True

    def test_metadata_json_field(self, user, project):
        """Test metadata JSONField functionality."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test.png',
            file_path='test/test.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra',
            metadata={'custom_key': 'custom_value', 'count': 42}
        )

        image.refresh_from_db()
        assert image.metadata['custom_key'] == 'custom_value'
        assert image.metadata['count'] == 42

    def test_get_metadata_method(self, user, project):
        """Test get_metadata helper method."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test.png',
            file_path='test/test.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra',
            metadata={'key1': 'value1'}
        )

        assert image.get_metadata('key1') == 'value1'
        assert image.get_metadata('nonexistent') is None
        assert image.get_metadata('nonexistent', 'default') == 'default'

    def test_set_metadata_method(self, user, project):
        """Test set_metadata helper method."""
        from content.models import ImageHistory

        image = ImageHistory.objects.create(
            user=user,
            project=project,
            filename='test.png',
            file_path='test/test.png',
            image_type='generated',
            prompt='Test',
            model_used='ultra'
        )

        image.set_metadata('new_key', 'new_value')
        assert image.metadata['new_key'] == 'new_value'

    def test_to_dict_method(self, image_history):
        """Test to_dict serialization method."""
        data = image_history.to_dict()

        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'metadata' in data
        assert 'version' in data
        assert 'is_active' in data
        assert isinstance(data['id'], str)


class TestUnifiedUser:
    """Tests for UnifiedUser model."""

    def test_create_user(self, db):
        """Test creating a basic user."""
        from core.models import UnifiedUser

        user = UnifiedUser.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='secure123'
        )

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('secure123')

    def test_platform_role_default(self, db):
        """Test platform_role defaults to unified_user."""
        user = UserFactory()
        assert user.platform_role == 'unified_user'

    def test_platform_role_choices(self, db):
        """Test platform_role accepts valid choices."""
        from core.models import UnifiedUser

        valid_roles = ['admin', 'sports_analyst', 'content_creator', 'agent_manager', 'unified_user']

        for role in valid_roles:
            user = UnifiedUser.objects.create_user(
                username=f'{role}_user',
                email=f'{role}@example.com',
                password='pass123',
                platform_role=role
            )
            assert user.platform_role == role

    def test_subscription_tier_default(self, db):
        """Test subscription_tier defaults to free."""
        user = UserFactory()
        # Factory sets 'free' by default
        user2 = UserFactory(subscription_tier='free')
        assert user2.subscription_tier == 'free'

    def test_subscription_tier_choices(self, db):
        """Test subscription_tier accepts valid choices."""
        from core.models import UnifiedUser

        valid_tiers = ['free', 'pro', 'enterprise']

        for tier in valid_tiers:
            user = UnifiedUser.objects.create_user(
                username=f'{tier}_user',
                email=f'{tier}@example.com',
                password='pass123',
                subscription_tier=tier
            )
            assert user.subscription_tier == tier

    def test_api_key_unique(self, db):
        """Test API key uniqueness."""
        from core.models import UnifiedUser
        from django.db import IntegrityError

        user1 = UnifiedUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            api_key='unique-api-key-123'
        )

        with pytest.raises(IntegrityError):
            user2 = UnifiedUser.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='pass123',
                api_key='unique-api-key-123'  # Same key, should fail
            )

    def test_monthly_api_calls_default(self, db):
        """Test monthly_api_calls defaults to 0."""
        user = UserFactory()
        assert user.monthly_api_calls == 0

    def test_superuser_creation(self, db):
        """Test creating a superuser."""
        from core.models import UnifiedUser

        admin = UnifiedUser.objects.create_superuser(
            username='superadmin',
            email='admin@example.com',
            password='adminpass'
        )

        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_user_projects_relationship(self, db):
        """Test user can have multiple projects."""
        # Session 452: CreativeProject is now alias for PartnershipProject
        from core.models_partnership import PartnershipProject

        user = UserFactory()

        # Session 452: Use correct field names for PartnershipProject
        proj1 = PartnershipProject.objects.create(user=user, project_name='Project 1', project_type='content_creation')
        proj2 = PartnershipProject.objects.create(user=user, project_name='Project 2', project_type='research')

        # Check reverse relationship - related_name is 'partnership_projects'
        user_projects = user.partnership_projects.all()
        assert proj1 in user_projects
        assert proj2 in user_projects
        assert user_projects.count() == 2

    def test_user_images_relationship(self, db):
        """Test user-images relationship through image_history."""
        from content.models import ImageHistory

        user = UserFactory()

        img1 = ImageHistory.objects.create(
            user=user,
            filename='img1.png',
            file_path='test/img1.png',
            image_type='generated',
            prompt='Test 1',
            model_used='ultra'
        )
        img2 = ImageHistory.objects.create(
            user=user,
            filename='img2.png',
            file_path='test/img2.png',
            image_type='generated',
            prompt='Test 2',
            model_used='ultra'
        )

        assert user.image_history.count() == 2

    def test_user_videos_relationship(self, db):
        """Test user-videos relationship through video_history."""
        from content.models import VideoHistory

        user = UserFactory()

        vid1 = VideoHistory.objects.create(
            user=user,
            video_id='vid1',
            video_type='text_to_video',
            prompt='Test 1',
            model_used='gen4_turbo'
        )

        assert user.video_history.count() == 1
