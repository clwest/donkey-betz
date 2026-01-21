# tests/models/test_project.py
"""Tests for CreativeProject model."""
import pytest
from tests.factories import CreativeProjectFactory, UserFactory, ImageHistoryFactory, VideoHistoryFactory

pytestmark = pytest.mark.django_db


class TestCreativeProjectModel:
    """Tests for CreativeProject model."""

    def test_create_project(self, user):
        """Test creating a basic project."""
        from content.models import CreativeProject

        project = CreativeProject.objects.create(
            user=user,
            name='My Project',
            description='A test project',
            project_type='logo'
        )

        assert project.id is not None
        assert project.name == 'My Project'
        assert project.user == user

    def test_project_type_choices(self, user):
        """Test project_type field accepts valid choices."""
        from content.models import CreativeProject

        # Valid project types
        valid_types = ['logo', 'character', 'product', 'marketing', 'other']

        for proj_type in valid_types:
            project = CreativeProject.objects.create(
                user=user,
                name=f'{proj_type} Project',
                project_type=proj_type
            )
            assert project.project_type == proj_type

    def test_project_images_relationship(self, user):
        """Test project-images relationship."""
        project = CreativeProjectFactory(user=user)

        img1 = ImageHistoryFactory(user=user, project=project)
        img2 = ImageHistoryFactory(user=user, project=project)

        assert project.project_images.count() == 2
        assert img1 in project.project_images.all()
        assert img2 in project.project_images.all()

    def test_project_videos_relationship(self, user):
        """Test project-videos relationship."""
        project = CreativeProjectFactory(user=user)

        vid1 = VideoHistoryFactory(user=user, project=project)
        vid2 = VideoHistoryFactory(user=user, project=project)

        assert project.project_videos.count() == 2
        assert vid1 in project.project_videos.all()
        assert vid2 in project.project_videos.all()

    def test_user_projects_ordering(self, user):
        """Test that user's projects are ordered by creation."""
        import time

        proj1 = CreativeProjectFactory(user=user)
        time.sleep(0.01)
        proj2 = CreativeProjectFactory(user=user)
        time.sleep(0.01)
        proj3 = CreativeProjectFactory(user=user)

        from content.models import CreativeProject
        projects = list(CreativeProject.objects.filter(user=user))

        # Most recent first
        assert projects[0] == proj3
        assert projects[1] == proj2
        assert projects[2] == proj1

    def test_project_metadata_json_field(self, user):
        """Test metadata JSONField stores custom data."""
        from content.models import CreativeProject

        metadata = {
            'client_name': 'Test Client',
            'deadline': '2025-12-31',
            'budget': 5000
        }

        project = CreativeProject.objects.create(
            user=user,
            name='Client Project',
            metadata=metadata
        )

        project.refresh_from_db()
        assert project.metadata['client_name'] == 'Test Client'
        assert project.metadata['budget'] == 5000

    def test_project_string_representation(self, user):
        """Test __str__ method."""
        project = CreativeProjectFactory(user=user, name='My Special Project')
        string_repr = str(project)

        assert 'My Special Project' in string_repr

    def test_project_is_active_default(self, user):
        """Test is_active defaults to True."""
        project = CreativeProjectFactory(user=user)
        assert project.is_active is True

    def test_project_soft_deactivation(self, user):
        """Test soft deactivation of projects."""
        project = CreativeProjectFactory(user=user, is_active=True)
        project.is_active = False
        project.save()

        project.refresh_from_db()
        assert project.is_active is False

    def test_project_description_optional(self, user):
        """Test description field is optional."""
        from content.models import CreativeProject

        project = CreativeProject.objects.create(
            user=user,
            name='No Description Project'
        )

        assert project.description == '' or project.description is None

    def test_version_increment_on_save(self, user):
        """Test version auto-increments on updates."""
        project = CreativeProjectFactory(user=user)
        initial_version = project.version

        project.name = 'Updated Name'
        project.save()

        assert project.version == initial_version + 1

    def test_created_at_and_updated_at(self, user):
        """Test timestamp fields."""
        project = CreativeProjectFactory(user=user)

        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.created_at <= project.updated_at

    def test_multiple_users_separate_projects(self, db):
        """Test projects are correctly separated by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        proj1 = CreativeProjectFactory(user=user1)
        proj2 = CreativeProjectFactory(user=user2)

        from content.models import CreativeProject

        user1_projects = CreativeProject.objects.filter(user=user1)
        user2_projects = CreativeProject.objects.filter(user=user2)

        assert proj1 in user1_projects
        assert proj1 not in user2_projects
        assert proj2 in user2_projects
        assert proj2 not in user1_projects

    def test_cascade_delete_behavior(self, user):
        """Test that deleting a project doesn't delete images/videos."""
        from content.models import CreativeProject, ImageHistory, VideoHistory

        project = CreativeProjectFactory(user=user)
        image = ImageHistoryFactory(user=user, project=project)
        video = VideoHistoryFactory(user=user, project=project)

        image_id = image.id
        video_id = video.id
        project.delete()

        # Images and videos should still exist (SET_NULL relationship)
        image.refresh_from_db()
        video.refresh_from_db()

        assert ImageHistory.objects.filter(id=image_id).exists()
        assert VideoHistory.objects.filter(id=video_id).exists()
        assert image.project is None
        assert video.project is None


class TestAISessionModel:
    """Tests for AISession model."""

    def test_create_ai_session(self, user, project):
        """Test creating an AI session."""
        from content.models import AISession

        # Session 452: Use conversation_transcript instead of transcript
        session = AISession.objects.create(
            user=user,
            project=project,
            title='Test Session',
            conversation_transcript=[{'role': 'user', 'content': 'Hello'}]
        )

        assert session.id is not None
        assert session.title == 'Test Session'
        assert len(session.conversation_transcript) == 1

    def test_session_transcript_json(self, user, project):
        """Test transcript JSONField stores conversation correctly."""
        from content.models import AISession

        transcript = [
            {'role': 'user', 'content': 'Generate an image'},
            {'role': 'assistant', 'content': 'I\'ll create that for you.'},
            {'role': 'user', 'content': 'Make it more colorful'}
        ]

        # Session 452: Use conversation_transcript instead of transcript
        session = AISession.objects.create(
            user=user,
            project=project,
            title='Test',
            conversation_transcript=transcript
        )

        session.refresh_from_db()
        assert len(session.conversation_transcript) == 3
        assert session.conversation_transcript[0]['role'] == 'user'
        assert session.conversation_transcript[1]['role'] == 'assistant'

    def test_session_images_relationship(self, user, project):
        """Test session-images relationship."""
        from content.models import AISession

        session = AISession.objects.create(
            user=user,
            project=project,
            title='Test'
        )

        image = ImageHistoryFactory(user=user, project=project, session=session)

        assert session.session_images.count() == 1
        assert image in session.session_images.all()

    def test_session_videos_relationship(self, user, project):
        """Test session-videos relationship."""
        from content.models import AISession

        session = AISession.objects.create(
            user=user,
            project=project,
            title='Test'
        )

        video = VideoHistoryFactory(user=user, project=project, session=session)

        assert session.session_videos.count() == 1
        assert video in session.session_videos.all()

    def test_session_counters(self, user, project):
        """Test session counters for images and videos."""
        from content.models import AISession

        # Session 452: Use total_images/total_videos instead of image_count/video_count
        session = AISession.objects.create(
            user=user,
            project=project,
            title='Test',
            total_images=5,
            total_videos=2
        )

        assert session.total_images == 5
        assert session.total_videos == 2
