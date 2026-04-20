#!/usr/bin/env python3
"""
Session 83: Complete Audio Workflow Test
Tests each component in isolation to find the break in the chain.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.elevenlabs_provider import elevenlabs_provider
from core.agents import get_audio_agent
from core.agents import VideoAgent
from content.models import VideoHistory

User = get_user_model()

def print_header(text):
    """Print a nice header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}\n")

def test_1_elevenlabs_direct():
    """Test 1: ElevenLabs Provider Direct Call"""
    print_header("TEST 1: ElevenLabs Provider Direct Call")

    try:
        print("📞 Calling ElevenLabs API directly...")
        print("   Text: 'Hello world, this is a test'")
        print("   Voice: Rachel")

        result = elevenlabs_provider.text_to_speech(
            text="Hello world, this is a test",
            voice="Rachel"
        )

        print(f"\n📋 Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Audio URL: {result.get('audio_url', 'None')}")

        if result.get('success') and result.get('audio_url'):
            # Check if file exists
            audio_url = result['audio_url']
            if audio_url.startswith('/media/'):
                file_path = f"/Users/donkeyking/development/unified-donkey-betz{audio_url}"
                exists = os.path.exists(file_path)
                size = os.path.getsize(file_path) if exists else 0

                print(f"   File exists: {exists}")
                print(f"   File size: {size:,} bytes")

                if exists and size > 0:
                    print_result(True, "ElevenLabs works! Audio file created successfully!")
                    return True, audio_url
                else:
                    print_result(False, "ElevenLabs returned URL but file doesn't exist")
                    return False, None
            else:
                print_result(True, "ElevenLabs returned external URL (not local file)")
                return True, audio_url
        else:
            print_result(False, f"ElevenLabs failed: {result.get('error', 'Unknown error')}")
            return False, None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_2_audio_agent():
    """Test 2: AudioAgent Direct Call"""
    print_header("TEST 2: AudioAgent Direct Call")

    try:
        print("📞 Getting AudioAgent instance...")
        user = User.objects.get(username='admin')
        audio_agent = get_audio_agent(user=user)

        print(f"✅ AudioAgent created: {audio_agent}")
        print(f"   User: {user.username}")
        print(f"   Template: {audio_agent.template.name if audio_agent.template else 'None'}")

        print("\n📞 Calling AudioAgent.generate_speech()...")
        print("   Text: 'Testing audio agent integration'")
        print("   Voice: Rachel")

        result = audio_agent.generate_speech(
            text="Testing audio agent integration",
            voice="Rachel"
        )

        print(f"\n📋 Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Audio URL: {result.get('audio_url', 'None')}")

        if result.get('success'):
            print_result(True, "AudioAgent works! Generated speech successfully!")
            return True, result.get('audio_url')
        else:
            print_result(False, f"AudioAgent failed: {result.get('error', 'Unknown error')}")
            return False, None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_3_audio_agent_memory():
    """Test 3: AudioAgent Memory Storage"""
    print_header("TEST 3: AudioAgent Memory Storage")

    try:
        print("📞 Generating speech and checking memory...")
        user = User.objects.get(username='admin')
        audio_agent = get_audio_agent(user=user)

        result = audio_agent.generate_speech(
            text="Memory test audio",
            voice="Drew"
        )

        if result.get('success'):
            print("✅ Speech generated successfully")

            # Check if stored in memory
            print("\n📋 Checking shared memory...")
            from intelligence.shared_memory import shared_memory

            memory_data = shared_memory.retrieve_memory(
                entity_type='agent',
                entity_id='audio_agent',
                memory_type='most_recent_audio'
            )

            if memory_data and memory_data.get('content'):
                print(f"✅ Memory found!")
                print(f"   Audio URL: {memory_data['content'].get('audio_url')}")
                print_result(True, "AudioAgent memory storage works!")
                return True
            else:
                print_result(False, "Memory not found - storage failed")
                return False
        else:
            print_result(False, "Speech generation failed, can't test memory")
            return False

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_4_video_agent_query():
    """Test 4: VideoAgent Queries AudioAgent"""
    print_header("TEST 4: VideoAgent Queries AudioAgent")

    try:
        print("📞 Getting agents...")
        user = User.objects.get(username='admin')

        # First generate audio with AudioAgent
        print("\n1️⃣ Generating audio with AudioAgent...")
        audio_agent = get_audio_agent(user=user)
        audio_result = audio_agent.generate_speech(
            text="Video agent query test",
            voice="Paul"
        )

        if not audio_result.get('success'):
            print_result(False, "Audio generation failed, can't test query")
            return False

        print(f"✅ Audio generated: {audio_result.get('audio_url')}")

        # Now test if VideoAgent can query for it
        print("\n2️⃣ Getting most recent video...")
        video = VideoHistory.objects.filter(user=user).order_by('-created_at').first()

        if not video:
            print_result(False, "No videos found for user, can't test")
            return False

        print(f"✅ Video found: {video.id}")
        print(f"   URL: {video.video_url[:50]}...")

        print("\n3️⃣ Creating VideoAgent and calling add_music_to_video WITHOUT audio_url...")
        print("   (This should trigger auto-query to AudioAgent)")

        video_agent = VideoAgent(user=user)

        # Call WITHOUT audio_url - should query AudioAgent
        result = video_agent.add_music_to_video(
            video_selection='last',
            audio_url=None,  # Force query
            audio_volume=0.5
        )

        print(f"\n📋 Result:")
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            print(f"   Video URL: {result.get('video_url', 'None')}")
            print(f"   Message: {result.get('message', 'None')}")
            print_result(True, "VideoAgent successfully queried AudioAgent!")
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
            print_result(False, "VideoAgent query failed")
            return False

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_5_complete_workflow():
    """Test 5: Complete Workflow with Real Audio URL"""
    print_header("TEST 5: Complete Workflow - Video + Audio Mixing")

    try:
        print("📞 Running complete workflow...")
        user = User.objects.get(username='admin')

        # Generate fresh audio
        print("\n1️⃣ Generating audio with AudioAgent...")
        audio_agent = get_audio_agent(user=user)
        audio_result = audio_agent.generate_speech(
            text="Welcome to the complete workflow test",
            voice="Aria"
        )

        if not audio_result.get('success'):
            print_result(False, f"Audio generation failed: {audio_result.get('error')}")
            return False

        audio_url = audio_result.get('audio_url')
        print(f"✅ Audio generated: {audio_url}")

        # Mix with video
        print("\n2️⃣ Mixing audio with most recent video...")
        video_agent = VideoAgent(user=user)

        result = video_agent.add_music_to_video(
            video_selection='last',
            audio_url=audio_url,
            audio_volume=0.7
        )

        print(f"\n📋 Result:")
        print(f"   Success: {result.get('success')}")

        if result.get('success'):
            mixed_video_url = result.get('video_url')
            print(f"   Mixed Video URL: {mixed_video_url}")

            # Check if it's a local file
            if mixed_video_url and mixed_video_url.startswith('/media/'):
                file_path = f"/Users/donkeyking/development/unified-donkey-betz{mixed_video_url}"
                exists = os.path.exists(file_path)
                size = os.path.getsize(file_path) if exists else 0

                print(f"   File exists: {exists}")
                print(f"   File size: {size:,} bytes")

                if exists and size > 0:
                    # Check if VideoHistory record was created
                    print("\n3️⃣ Checking if VideoHistory record was created...")
                    video_record = VideoHistory.objects.filter(
                        video_url=mixed_video_url
                    ).first()

                    if video_record:
                        print(f"✅ VideoHistory record found!")
                        print(f"   ID: {video_record.id}")
                        print(f"   Type: {video_record.video_type}")
                        print(f"   Model: {video_record.model_used}")
                        print_result(True, "COMPLETE WORKFLOW WORKS! 🎉")
                        return True
                    else:
                        print_result(False, "File created but no VideoHistory record")
                        return False
                else:
                    print_result(False, "URL returned but file doesn't exist")
                    return False
            else:
                print_result(True, "Mixing completed (external URL or temp file)")
                return True
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
            print_result(False, "Video mixing failed")
            return False

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("  SESSION 83: COMPLETE AUDIO WORKFLOW TEST")
    print("🧪" * 40)

    results = {}

    # Test 1: ElevenLabs Direct
    success, audio_url = test_1_elevenlabs_direct()
    results['elevenlabs'] = success

    # Test 2: AudioAgent
    success, audio_url = test_2_audio_agent()
    results['audio_agent'] = success

    # Test 3: Memory Storage
    success = test_3_audio_agent_memory()
    results['memory'] = success

    # Test 4: VideoAgent Query
    success = test_4_video_agent_query()
    results['video_query'] = success

    # Test 5: Complete Workflow
    success = test_5_complete_workflow()
    results['complete'] = success

    # Summary
    print_header("TEST SUMMARY")

    for test_name, success in results.items():
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {'PASS' if success else 'FAIL'}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)

    print(f"\n{'='*80}")
    print(f"  TOTAL: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    print(f"{'='*80}\n")

    if passed == total:
        print("🎉 ALL TESTS PASSED! The audio workflow is fully functional!")
        print("\n💡 Next step: Figure out why AI Assistant isn't calling the tools")
    else:
        print("⚠️  Some tests failed. Review the output above to see what needs fixing.")

if __name__ == '__main__':
    main()
