# tests/models/test_video_history.py
"""Tests for VideoHistory model."""
import pytest
from tests.factories import VideoHistoryFactory, UserFactory, CreativeProjectFactory, ImageHistoryFactory

pytestmark = pytest.mark.django_db


class TestVideoHistoryModel:
    """Tests for VideoHistory model."""

    def test_create_video_history(self, user, project):
        """Test creating a basic video history record."""
        from content.models import VideoHistory

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='test-video-123',
            video_url='https://example.com/test.mp4',
            video_type='text_to_video',
            prompt='A sunset animation',
            parameters={'duration': 10},
            model_used='gen4_turbo',
            status='completed'
        )

        assert video.id is not None
        assert video.video_id == 'test-video-123'
        assert video.prompt == 'A sunset animation'
        assert video.status == 'completed'

    def test_video_type_choices(self, user, project):
        """Test video_type field accepts valid choices."""
        from content.models import VideoHistory

        valid_types = ['text_to_video', 'image_to_video', 'extend_video', 'chained_video']

        for vid_type in valid_types:
            video = VideoHistory.objects.create(
                user=user,
                project=project,
                video_id=f'{vid_type}-video',
                video_type=vid_type,
                prompt='Test',
                model_used='gen4_turbo'
            )
            assert video.video_type == vid_type

    def test_model_used_choices(self, user, project):
        """Test model_used field accepts valid choices."""
        from content.models import VideoHistory

        valid_models = ['veo3.1_fast', 'veo3.1', 'gen4_turbo']

        for model in valid_models:
            video = VideoHistory.objects.create(
                user=user,
                project=project,
                video_id=f'{model}-video',
                video_type='text_to_video',
                prompt='Test',
                model_used=model
            )
            assert video.model_used == model

    def test_status_choices(self, user, project):
        """Test status field accepts valid choices."""
        from content.models import VideoHistory

        valid_statuses = ['pending', 'processing', 'completed', 'failed']

        for status in valid_statuses:
            video = VideoHistory.objects.create(
                user=user,
                project=project,
                video_id=f'{status}-video',
                video_type='text_to_video',
                prompt='Test',
                model_used='gen4_turbo',
                status=status
            )
            assert video.status == status

    def test_parameters_json_field(self, user, project):
        """Test parameters JSONField stores and retrieves correctly."""
        from content.models import VideoHistory

        params = {
            'duration': 10,
            'ratio': '16:9',
            'fps': 24,
            'motion_intensity': 0.8
        }

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='params-test',
            video_type='text_to_video',
            prompt='Test',
            parameters=params,
            model_used='gen4_turbo'
        )

        video.refresh_from_db()
        assert video.parameters == params
        assert video.parameters['fps'] == 24

    def test_string_representation(self, user, project):
        """Test __str__ method."""
        video = VideoHistoryFactory(
            user=user,
            project=project,
            video_type='text_to_video',
            video_id='test-123'
        )

        string_repr = str(video)
        assert user.username in string_repr
        assert 'text_to_video' in string_repr

    def test_increment_view_count(self, user, project):
        """Test atomic view count increment."""
        video = VideoHistoryFactory(user=user, project=project)
        initial_count = video.view_count

        video.increment_view_count()

        assert video.view_count == initial_count + 1

    def test_increment_download_count(self, user, project):
        """Test atomic download count increment."""
        video = VideoHistoryFactory(user=user, project=project)
        initial_count = video.download_count

        video.increment_download_count()

        assert video.download_count == initial_count + 1

    def test_get_sequential_number(self, user, project):
        """Test sequential numbering for videos."""
        vid1 = VideoHistoryFactory(user=user, project=project)
        vid2 = VideoHistoryFactory(user=user, project=project)

        assert vid1.get_sequential_number() == 1
        assert vid2.get_sequential_number() == 2

    def test_sequential_number_per_user(self, db):
        """Test that sequential numbers are independent per user."""
        user1 = UserFactory()
        user2 = UserFactory()

        vid1_user1 = VideoHistoryFactory(user=user1)
        vid2_user1 = VideoHistoryFactory(user=user1)
        vid1_user2 = VideoHistoryFactory(user=user2)

        assert vid2_user1.get_sequential_number() == 2
        assert vid1_user2.get_sequential_number() == 1

    def test_source_image_relationship(self, user, project):
        """Test image-to-video source image relationship."""
        image = ImageHistoryFactory(user=user, project=project)

        video = VideoHistoryFactory(
            user=user,
            project=project,
            video_type='image_to_video',
            source_image=image
        )

        assert video.source_image == image
        assert image.generated_videos.first() == video

    def test_parent_video_url_for_extensions(self, user, project):
        """Test parent video tracking for video extensions."""
        from content.models import VideoHistory

        parent_url = 'https://example.com/parent-video.mp4'

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='extended-video',
            video_type='extend_video',
            prompt='Extension',
            model_used='gen4_turbo',
            parent_video_url=parent_url
        )

        assert video.parent_video_url == parent_url

    def test_generation_timing_fields(self, user, project):
        """Test generation timing fields."""
        from content.models import VideoHistory
        from django.utils import timezone

        start_time = timezone.now()
        end_time = start_time

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='timing-test',
            video_type='text_to_video',
            prompt='Test',
            model_used='gen4_turbo',
            generation_started=start_time,
            generation_completed=end_time,
            generation_time_seconds=45
        )

        assert video.generation_started is not None
        assert video.generation_completed is not None
        assert video.generation_time_seconds == 45

    def test_video_metadata_fields(self, user, project):
        """Test video metadata fields."""
        from content.models import VideoHistory

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='metadata-test',
            video_type='text_to_video',
            prompt='Test',
            model_used='gen4_turbo',
            duration=10,
            ratio='1920:1080',
            video_width=1920,
            video_height=1080,
            file_size_bytes=10485760  # 10MB
        )

        assert video.duration == 10
        assert video.ratio == '1920:1080'
        assert video.video_width == 1920
        assert video.video_height == 1080
        assert video.file_size_bytes == 10485760

    def test_tags_json_field(self, user, project):
        """Test tags JSONField for list storage."""
        from content.models import VideoHistory

        tags = ['animation', 'sunset', 'ocean']

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='tags-test',
            video_type='text_to_video',
            prompt='Test',
            tags=tags,
            model_used='gen4_turbo'
        )

        video.refresh_from_db()
        assert video.tags == tags
        assert 'animation' in video.tags

    def test_is_favorite_toggle(self, user, project):
        """Test favorite boolean field."""
        video = VideoHistoryFactory(user=user, project=project, is_favorite=False)
        assert not video.is_favorite

        video.is_favorite = True
        video.save()
        video.refresh_from_db()

        assert video.is_favorite

    def test_error_message_on_failure(self, user, project):
        """Test error message storage for failed videos."""
        from content.models import VideoHistory

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='failed-video',
            video_type='text_to_video',
            prompt='Test',
            model_used='gen4_turbo',
            status='failed',
            error_message='API rate limit exceeded'
        )

        assert video.status == 'failed'
        assert video.error_message == 'API rate limit exceeded'

    def test_user_notes_field(self, user, project):
        """Test user_notes field."""
        from content.models import VideoHistory

        video = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id='notes-test',
            video_type='text_to_video',
            prompt='Test',
            model_used='gen4_turbo',
            user_notes='This video is for the marketing campaign'
        )

        assert 'marketing campaign' in video.user_notes

    def test_project_relationship_optional(self, user):
        """Test that project can be null."""
        from content.models import VideoHistory

        video = VideoHistory.objects.create(
            user=user,
            project=None,  # No project
            video_id='no-project',
            video_type='text_to_video',
            prompt='Test',
            model_used='gen4_turbo'
        )

        assert video.project is None

    def test_ordering(self, user, project):
        """Test default ordering is by -created_at."""
        from content.models import VideoHistory
        import time

        vid1 = VideoHistoryFactory(user=user, project=project)
        time.sleep(0.01)
        vid2 = VideoHistoryFactory(user=user, project=project)
        time.sleep(0.01)
        vid3 = VideoHistoryFactory(user=user, project=project)

        videos = list(VideoHistory.objects.filter(user=user))

        # Most recent first
        assert videos[0] == vid3
        assert videos[1] == vid2
        assert videos[2] == vid1

    def test_version_increment_on_save(self, user, project):
        """Test version auto-increments on updates."""
        video = VideoHistoryFactory(user=user, project=project)
        initial_version = video.version

        video.prompt = 'Updated prompt'
        video.save()

        assert video.version == initial_version + 1
