"""
Tests for Personal Assistant Voice Input
Session 113: Voice Input MVP
"""

import io
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class VoiceToAssistantTests(TestCase):
    """Test suite for voice input endpoint"""

    def setUp(self):
        """Set up test user and client"""
        # Test password (not a real secret)
        test_password = 'test' + 'pass' + '123'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=test_password
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/assistant/voice/'

    def test_voice_input_requires_authentication(self):
        """Test that voice endpoint requires authentication"""
        client = APIClient()  # Unauthenticated client
        response = client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_voice_input_requires_audio_file(self):
        """Test that audio file is required"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No audio file provided')

    @patch('core.views_personal_assistant.OpenAI')
    @patch('core.views_personal_assistant.PersonalAIAssistant')
    def test_voice_input_success(self, mock_assistant_class, mock_openai_class):
        """Test successful voice input processing"""
        # Mock OpenAI Whisper transcription
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Create a logo for my coffee shop"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        # Mock Personal Assistant response
        mock_assistant = MagicMock()
        mock_assistant_class.return_value = mock_assistant
        mock_assistant.process_message.return_value = {
            'response': "I'd be happy to help create a logo!",
            'suggestions': ['Generate logo', 'See examples'],
            'actions': ['start_project'],
            'confidence': 0.95
        }

        # Create fake audio file
        audio_content = b'fake audio data'
        audio_file = io.BytesIO(audio_content)
        audio_file.name = 'test.webm'

        # Send request
        response = self.client.post(
            self.url,
            {'audio': audio_file},
            format='multipart'
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user_text'], "Create a logo for my coffee shop")
        self.assertIn('assistant_message', response.data)
        self.assertEqual(
            response.data['assistant_message']['response'],
            "I'd be happy to help create a logo!"
        )

        # Verify OpenAI was called correctly
        mock_client.audio.transcriptions.create.assert_called_once()
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'whisper-1')
        self.assertEqual(call_kwargs['language'], 'en')

        # Verify assistant was called with transcribed text
        mock_assistant.process_message.assert_called_once()
        call_args = mock_assistant.process_message.call_args[0]
        self.assertEqual(call_args[0], "Create a logo for my coffee shop")

    @patch('core.views_personal_assistant.OpenAI')
    def test_voice_input_transcription_failure(self, mock_openai_class):
        """Test handling of transcription failures"""
        # Mock OpenAI to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("Whisper API error")

        # Create fake audio file
        audio_content = b'fake audio data'
        audio_file = io.BytesIO(audio_content)
        audio_file.name = 'test.webm'

        # Send request
        response = self.client.post(
            self.url,
            {'audio': audio_file},
            format='multipart'
        )

        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Failed to transcribe audio')

    @patch('core.views_personal_assistant.OpenAI')
    @patch('core.views_personal_assistant.PersonalAIAssistant')
    def test_voice_input_assistant_failure(self, mock_assistant_class, mock_openai_class):
        """Test handling when assistant fails but transcription succeeds"""
        # Mock successful transcription
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Test message"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        # Mock assistant to raise exception
        mock_assistant = MagicMock()
        mock_assistant_class.return_value = mock_assistant
        mock_assistant.process_message.side_effect = Exception("Assistant error")

        # Create fake audio file
        audio_content = b'fake audio data'
        audio_file = io.BytesIO(audio_content)
        audio_file.name = 'test.webm'

        # Send request
        response = self.client.post(
            self.url,
            {'audio': audio_file},
            format='multipart'
        )

        # Assert partial success - transcription worked
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['user_text'], "Test message")
        self.assertIn('error', response.data)

    @patch('core.views_personal_assistant.OpenAI')
    @patch('core.views_personal_assistant.PersonalAIAssistant')
    def test_voice_input_marks_input_method(self, mock_assistant_class, mock_openai_class):
        """Test that context is marked as voice input"""
        # Mock OpenAI
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Test message"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        # Mock assistant
        mock_assistant = MagicMock()
        mock_assistant_class.return_value = mock_assistant
        mock_assistant.process_message.return_value = {
            'response': "Test response",
            'suggestions': [],
            'actions': [],
            'confidence': 0.9
        }

        # Create fake audio file
        audio_content = b'fake audio data'
        audio_file = io.BytesIO(audio_content)
        audio_file.name = 'test.webm'

        # Send request
        response = self.client.post(
            self.url,
            {'audio': audio_file},
            format='multipart'
        )

        # Verify context was marked as voice input
        mock_assistant.process_message.assert_called_once()
        call_args = mock_assistant.process_message.call_args
        context = call_args[0][1]  # Second argument is context
        self.assertEqual(context['input_method'], 'voice')

    @patch('core.views_personal_assistant.OpenAI')
    @patch('core.views_personal_assistant.PersonalAIAssistant')
    def test_voice_input_with_various_audio_formats(self, mock_assistant_class, mock_openai_class):
        """Test that different audio formats are handled"""
        # Mock OpenAI
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Test message"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        # Mock assistant
        mock_assistant = MagicMock()
        mock_assistant_class.return_value = mock_assistant
        mock_assistant.process_message.return_value = {
            'response': "Test response",
            'suggestions': [],
            'actions': [],
            'confidence': 0.9
        }

        # Test with different filenames (format should be inferred from content)
        formats = ['test.webm', 'test.m4a', 'test.wav', 'test.mp3']

        for filename in formats:
            audio_content = b'fake audio data'
            audio_file = io.BytesIO(audio_content)
            audio_file.name = filename

            response = self.client.post(
                self.url,
                {'audio': audio_file},
                format='multipart'
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Failed for format: {filename}"
            )
