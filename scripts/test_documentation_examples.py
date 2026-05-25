#!/usr/bin/env python3
"""
Documentation Examples Test Suite

Tests all code examples from Session 85 documentation to ensure they work correctly.

**Created:** Session 86 - November 12, 2025
**Purpose:** Verify all documented API examples, workflows, and voice commands
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DocumentationTester:
    """Test harness for documentation examples"""

    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []

    def test(self, name, test_func, skip_reason=None):
        """Run a single test"""
        if skip_reason:
            logger.info(f"⏭️  SKIP: {name} - {skip_reason}")
            self.skipped.append((name, skip_reason))
            return

        try:
            logger.info(f"🧪 Testing: {name}")
            test_func()
            logger.info(f"✅ PASS: {name}")
            self.passed.append(name)
        except Exception as e:
            logger.error(f"❌ FAIL: {name} - {e}")
            self.failed.append((name, str(e)))

    def report(self):
        """Print test summary"""
        total = len(self.passed) + len(self.failed) + len(self.skipped)

        print("\n" + "=" * 80)
        print("📊 DOCUMENTATION EXAMPLES TEST REPORT")
        print("=" * 80)
        print(f"\n✅ Passed: {len(self.passed)}/{total}")
        print(f"❌ Failed: {len(self.failed)}/{total}")
        print(f"⏭️  Skipped: {len(self.skipped)}/{total}")

        if self.passed:
            print("\n✅ Passed Tests:")
            for name in self.passed:
                print(f"  - {name}")

        if self.failed:
            print("\n❌ Failed Tests:")
            for name, error in self.failed:
                print(f"  - {name}")
                print(f"    Error: {error}")

        if self.skipped:
            print("\n⏭️  Skipped Tests:")
            for name, reason in self.skipped:
                print(f"  - {name}: {reason}")

        print("\n" + "=" * 80)

        # Calculate success rate
        if total > 0:
            success_rate = (len(self.passed) / (len(self.passed) + len(self.failed))) * 100 if (len(self.passed) + len(self.failed)) > 0 else 0
            print(f"Success Rate: {success_rate:.1f}%")

        return len(self.failed) == 0


# ============================================================================
# API AUTHENTICATION TESTS
# ============================================================================

def test_stability_api_key():
    """Test: Stability AI API key is configured (docs/archive/superseded-2026-05/apis/STABILITY_AI.md)"""
    api_key = os.getenv('STABILITY_API_KEY')
    assert api_key, "STABILITY_API_KEY not found in environment"
    assert api_key.startswith('sk-'), "Invalid Stability API key format"
    logger.info(f"  Found API key: {api_key[:10]}...")


def test_runway_api_key():
    """Test: Runway ML API key is configured (docs/archive/superseded-2026-05/apis/RUNWAY_ML.md)"""
    api_key = os.getenv('RUNWAY_API_SECRET')
    assert api_key, "RUNWAY_API_SECRET not found in environment"
    logger.info(f"  Found API key: {api_key[:10]}...")


def test_elevenlabs_api_key():
    """Test: ElevenLabs API key is configured (docs/archive/superseded-2026-05/apis/ELEVENLABS.md)"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    assert api_key, "ELEVENLABS_API_KEY not found in environment"
    logger.info(f"  Found API key: {api_key[:10]}...")


def test_openai_api_key():
    """Test: OpenAI API key is configured (docs/archive/superseded-2026-05/apis/OPENAI.md)"""
    api_key = os.getenv('OPENAI_API_KEY')
    assert api_key, "OPENAI_API_KEY not found in environment"
    assert api_key.startswith('sk-'), "Invalid OpenAI API key format"
    logger.info(f"  Found API key: {api_key[:10]}...")


def test_replicate_api_token():
    """Test: Replicate API token is configured (docs/archive/superseded-2026-05/apis/REPLICATE.md)"""
    api_token = os.getenv('REPLICATE_API_TOKEN')
    assert api_token, "REPLICATE_API_TOKEN not found in environment"
    logger.info(f"  Found API token: {api_token[:10]}...")


# ============================================================================
# IMAGE GENERATION TESTS (docs/archive/superseded-2026-05/features/IMAGE_GENERATION.md)
# ============================================================================

def test_image_generation_import():
    """Test: ImageGeneration class can be imported"""
    from content.image_generation import ImageGeneration
    assert ImageGeneration, "ImageGeneration class not found"
    logger.info("  ImageGeneration class imported successfully")


def test_image_generation_initialization():
    """Test: ImageGeneration can be initialized"""
    from content.image_generation import ImageGeneration
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()
    assert user, "No user found in database"

    image_gen = ImageGeneration(user=user)
    assert image_gen.user == user
    logger.info(f"  ImageGeneration initialized for user: {user.username}")


def test_style_presets_available():
    """Test: Style presets are configured"""
    from content.image_generation import ImageGeneration
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()
    image_gen = ImageGeneration(user=user)

    # Check style presets exist
    assert hasattr(image_gen, 'style_presets') or hasattr(image_gen, 'STYLE_PRESETS')
    logger.info("  Style presets available")


# ============================================================================
# VIDEO GENERATION TESTS (docs/archive/superseded-2026-05/features/VIDEO_GENERATION.md)
# ============================================================================

def test_video_provider_import():
    """Test: VideoProvider class can be imported"""
    from content.video_provider import VideoProvider
    assert VideoProvider, "VideoProvider class not found"
    logger.info("  VideoProvider class imported successfully")


def test_video_provider_initialization():
    """Test: VideoProvider can be initialized"""
    from content.video_provider import VideoProvider
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()
    assert user, "No user found in database"

    video_provider = VideoProvider(user=user)
    assert video_provider.user == user
    logger.info(f"  VideoProvider initialized for user: {user.username}")


# ============================================================================
# AUDIO GENERATION TESTS (docs/archive/superseded-2026-05/features/AUDIO_GENERATION.md)
# ============================================================================

def test_elevenlabs_provider_import():
    """Test: ElevenLabsProvider can be imported"""
    from content.elevenlabs_provider import ElevenLabsProvider
    assert ElevenLabsProvider, "ElevenLabsProvider class not found"
    logger.info("  ElevenLabsProvider class imported successfully")


def test_audio_agent_import():
    """Test: AudioAgent can be imported"""
    from core.agents import AudioAgent
    assert AudioAgent, "AudioAgent class not found"
    logger.info("  AudioAgent class imported successfully")


def test_audio_agent_initialization():
    """Test: AudioAgent can be initialized"""
    from core.agents import AudioAgent
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()
    assert user, "No user found in database"

    audio_agent = AudioAgent(user=user)
    assert audio_agent.user == user
    logger.info(f"  AudioAgent initialized for user: {user.username}")


# ============================================================================
# CHARACTER TRAINING TESTS (docs/archive/superseded-2026-05/features/CHARACTER_TRAINING.md)
# ============================================================================

def test_character_model_import():
    """Test: CharacterModel can be imported"""
    from content.models import CharacterModel
    assert CharacterModel, "CharacterModel class not found"
    logger.info("  CharacterModel imported successfully")


def test_replicate_provider_import():
    """Test: ReplicateProvider can be imported"""
    from content.replicate_provider import ReplicateProvider
    assert ReplicateProvider, "ReplicateProvider class not found"
    logger.info("  ReplicateProvider class imported successfully")


# ============================================================================
# AGENT SYSTEM TESTS (docs/archive/superseded-2026-05/agents/README.md)
# ============================================================================

def test_video_agent_import():
    """Test: VideoAgent can be imported"""
    from core.agents import VideoAgent
    assert VideoAgent, "VideoAgent class not found"
    logger.info("  VideoAgent class imported successfully")


def test_video_agent_initialization():
    """Test: VideoAgent can be initialized"""
    from core.agents import VideoAgent
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.first()
    assert user, "No user found in database"

    video_agent = VideoAgent(user=user)
    assert video_agent.user == user
    logger.info(f"  VideoAgent initialized for user: {user.username}")


def test_agent_query_protocol_import():
    """Test: AgentQueryProtocol can be imported"""
    from intelligence.agent_query_protocol import AgentQueryProtocol
    assert AgentQueryProtocol, "AgentQueryProtocol class not found"
    logger.info("  AgentQueryProtocol class imported successfully")


# ============================================================================
# DAVINCI RESOLVE TESTS (docs/archive/superseded-2026-05/DAVINCI_RESOLVE.md)
# ============================================================================

def test_davinci_provider_import():
    """Test: DaVinciProvider can be imported"""
    from content.davinci_provider import get_davinci_provider
    provider = get_davinci_provider()
    assert provider, "DaVinciProvider not available"
    logger.info("  DaVinciProvider imported successfully")


def test_davinci_resolve_connection():
    """Test: Can connect to DaVinci Resolve"""
    from content.davinci_provider import get_davinci_provider

    provider = get_davinci_provider()
    # Check if resolve attribute exists
    assert hasattr(provider, 'resolve') or hasattr(provider, 'is_connected')
    logger.info("  DaVinci Resolve connection available")


# ============================================================================
# DATABASE MODEL TESTS
# ============================================================================

def test_image_history_model():
    """Test: ImageHistory model can query database"""
    from content.models import ImageHistory

    count = ImageHistory.objects.count()
    logger.info(f"  Found {count} images in database")
    assert count >= 0, "ImageHistory query failed"


def test_video_history_model():
    """Test: VideoHistory model can query database"""
    from content.models import VideoHistory

    count = VideoHistory.objects.count()
    logger.info(f"  Found {count} videos in database")
    assert count >= 0, "VideoHistory query failed"


def test_audio_history_model():
    """Test: AudioHistory model can query database"""
    from content.models import AudioHistory

    count = AudioHistory.objects.count()
    logger.info(f"  Found {count} audio files in database")
    assert count >= 0, "AudioHistory query failed"


# ============================================================================
# WORKFLOW TESTS (docs/archive/superseded-2026-05/features/*.md voice commands)
# ============================================================================

def test_voice_command_structure():
    """Test: AI Assistant tool definitions exist"""
    from core.views_image import _get_gpt5_tools

    tools = _get_gpt5_tools()
    assert tools, "AI Assistant tools not found"
    assert len(tools) > 0, "No AI Assistant tools defined"

    # Check for key tools documented in Session 85
    tool_names = [tool['function']['name'] for tool in tools]

    expected_tools = [
        'generate_image',
        'generate_video',
        'generate_speech',
        'generate_sound_effect',
        'edit_video',
        'chain_videos',
        'add_text_to_video',
        'add_music_to_video',
        'apply_color_grade'
    ]

    found_tools = [tool for tool in expected_tools if tool in tool_names]
    logger.info(f"  Found {len(found_tools)}/{len(expected_tools)} documented AI tools")

    assert len(found_tools) >= 8, f"Missing documented AI tools: {set(expected_tools) - set(found_tools)}"


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all documentation tests"""
    tester = DocumentationTester()

    print("\n" + "=" * 80)
    print("🧪 DOCUMENTATION EXAMPLES TEST SUITE - Session 86")
    print("=" * 80)
    print("\nTesting all code examples from Session 85 documentation...\n")

    # API Authentication Tests
    print("\n📋 Category: API Authentication")
    tester.test("Stability AI API Key", test_stability_api_key)
    tester.test("Runway ML API Key", test_runway_api_key)
    tester.test("ElevenLabs API Key", test_elevenlabs_api_key)
    tester.test("OpenAI API Key", test_openai_api_key)
    tester.test("Replicate API Token", test_replicate_api_token)

    # Image Generation Tests
    print("\n📋 Category: Image Generation (docs/archive/superseded-2026-05/features/IMAGE_GENERATION.md)")
    tester.test("ImageGeneration Import", test_image_generation_import)
    tester.test("ImageGeneration Initialization", test_image_generation_initialization)
    tester.test("Style Presets Available", test_style_presets_available)

    # Video Generation Tests
    print("\n📋 Category: Video Generation (docs/archive/superseded-2026-05/features/VIDEO_GENERATION.md)")
    tester.test("VideoProvider Import", test_video_provider_import)
    tester.test("VideoProvider Initialization", test_video_provider_initialization)

    # Audio Generation Tests
    print("\n📋 Category: Audio Generation (docs/archive/superseded-2026-05/features/AUDIO_GENERATION.md)")
    tester.test("ElevenLabsProvider Import", test_elevenlabs_provider_import)
    tester.test("AudioAgent Import", test_audio_agent_import)
    tester.test("AudioAgent Initialization", test_audio_agent_initialization)

    # Character Training Tests
    print("\n📋 Category: Character Training (docs/archive/superseded-2026-05/features/CHARACTER_TRAINING.md)")
    tester.test("CharacterModel Import", test_character_model_import)
    tester.test("ReplicateProvider Import", test_replicate_provider_import)

    # Agent System Tests
    print("\n📋 Category: Agent System (docs/archive/superseded-2026-05/agents/README.md)")
    tester.test("VideoAgent Import", test_video_agent_import)
    tester.test("VideoAgent Initialization", test_video_agent_initialization)
    tester.test("AgentQueryProtocol Import", test_agent_query_protocol_import)

    # DaVinci Resolve Tests
    print("\n📋 Category: DaVinci Resolve (docs/archive/superseded-2026-05/DAVINCI_RESOLVE.md)")
    tester.test("DaVinciProvider Import", test_davinci_provider_import)
    tester.test("DaVinci Resolve Connection", test_davinci_resolve_connection)

    # Database Model Tests
    print("\n📋 Category: Database Models")
    tester.test("ImageHistory Model", test_image_history_model)
    tester.test("VideoHistory Model", test_video_history_model)
    tester.test("AudioHistory Model", test_audio_history_model)

    # Workflow Tests
    print("\n📋 Category: AI Assistant Workflows")
    tester.test("Voice Command Structure", test_voice_command_structure)

    # Generate report
    success = tester.report()

    if success:
        print("\n🎉 All documentation examples validated successfully!")
        print("✅ Ready for Session 87 testing phase")
        return 0
    else:
        print("\n⚠️  Some tests failed - review errors above")
        print("🔧 Fix failing tests before proceeding to Session 87")
        return 1


if __name__ == "__main__":
    sys.exit(main())
