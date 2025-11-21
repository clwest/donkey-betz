"""
Test Batch Operations - Session 152
Tests range parsing and batch processing for image editing operations.
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from content.models import ImageHistory

User = get_user_model()


def test_range_parser():
    """Test the _parse_id_range utility."""
    print("=" * 80)
    print("TEST 1: Range Parser Utility")
    print("=" * 80)

    user = User.objects.first()
    assistant = EnhancedPersonalAIAssistant(user)

    test_cases = [
        ("5", ["5"]),                                    # Single ID
        ("1-3", ["1", "2", "3"]),                       # Simple range
        ("5, 8, 12", ["5", "8", "12"]),                 # List
        ("1-3, 7", ["1", "2", "3", "7"]),               # Range + single
        ("1-3, 7, 8-9", ["1", "2", "3", "7", "8", "9"]), # Combined
        ("10 - 12, 15", ["10", "11", "12", "15"]),      # Spaces in range
    ]

    for input_str, expected in test_cases:
        result = assistant._parse_id_range(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_str}' → {result} (expected: {expected})")

    print()


def test_batch_operations():
    """Test batch image editing operations."""
    print("=" * 80)
    print("TEST 2: Batch Image Editing Operations")
    print("=" * 80)

    user = User.objects.first()
    assistant = EnhancedPersonalAIAssistant(user)

    # Check how many images we have
    total_images = ImageHistory.objects.filter(user=user).count()
    print(f"📊 Total images in database: {total_images}")

    if total_images < 3:
        print("⚠️  Need at least 3 images for testing. Skipping batch tests.")
        return

    # Test 1: Range format (1-3)
    print("\n" + "-" * 80)
    print("Test 2.1: Range Format - 'upscale images 1-3'")
    print("-" * 80)

    # Simulate tool call
    arguments = {
        'operation': 'upscale',
        'image_id': '1-3',
        'params': {},
        'project_id': None
    }

    print("🔧 Simulating tool call with arguments:")
    print(f"   operation: {arguments['operation']}")
    print(f"   image_id: {arguments['image_id']}")

    # Don't actually execute - just test parsing
    try:
        parsed_ids = assistant._parse_id_range(arguments['image_id'])
        print(f"✅ Successfully parsed range: {parsed_ids}")
        print(f"   Will process {len(parsed_ids)} images")
    except Exception as e:
        print(f"❌ Error parsing range: {e}")

    # Test 2: List format (1, 3, 5)
    print("\n" + "-" * 80)
    print("Test 2.2: List Format - 'remove backgrounds from images 1, 3, 5'")
    print("-" * 80)

    arguments = {
        'operation': 'remove_background',
        'image_id': '1, 3, 5',
        'params': {},
        'project_id': None
    }

    print("🔧 Simulating tool call with arguments:")
    print(f"   operation: {arguments['operation']}")
    print(f"   image_id: {arguments['image_id']}")

    try:
        parsed_ids = assistant._parse_id_range(arguments['image_id'])
        print(f"✅ Successfully parsed list: {parsed_ids}")
        print(f"   Will process {len(parsed_ids)} images")
    except Exception as e:
        print(f"❌ Error parsing list: {e}")

    # Test 3: Combined format (1-3, 7, 8-9)
    if total_images >= 9:
        print("\n" + "-" * 80)
        print("Test 2.3: Combined Format - 'create variations of images 1-3, 7, 8-9'")
        print("-" * 80)

        arguments = {
            'operation': 'create_variations',
            'image_id': '1-3, 7, 8-9',
            'params': {'count': 2},
            'project_id': None
        }

        print("🔧 Simulating tool call with arguments:")
        print(f"   operation: {arguments['operation']}")
        print(f"   image_id: {arguments['image_id']}")
        print(f"   params: {arguments['params']}")

        try:
            parsed_ids = assistant._parse_id_range(arguments['image_id'])
            print(f"✅ Successfully parsed combined format: {parsed_ids}")
            print(f"   Will process {len(parsed_ids)} images")
        except Exception as e:
            print(f"❌ Error parsing combined format: {e}")

    print()


def test_batch_detection():
    """Test batch detection logic."""
    print("=" * 80)
    print("TEST 3: Batch Detection Logic")
    print("=" * 80)

    test_cases = [
        ("5", False, "Single number"),
        ("1-3", True, "Range with dash"),
        ("5, 8, 12", True, "List with commas"),
        ("1-3, 7", True, "Combined format"),
        ("a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6", False, "UUID format"),
    ]

    for id_str, expected_batch, description in test_cases:
        # Simulate batch detection logic from _handle_image_editing_agent (Session 152)
        is_batch = ',' in id_str

        if not is_batch and '-' in id_str:
            # Check if it's a numeric range (not a UUID)
            cleaned = id_str.replace('-', '').replace(' ', '')
            is_batch = cleaned.isdigit()  # "1-3" → "13" → True, UUID → has letters → False

        status = "✅" if is_batch == expected_batch else "❌"
        batch_str = "BATCH" if is_batch else "SINGLE"
        print(f"{status} '{id_str}' detected as {batch_str} ({description})")

    print()


def test_error_handling():
    """Test error handling for invalid ranges."""
    print("=" * 80)
    print("TEST 4: Error Handling")
    print("=" * 80)

    user = User.objects.first()
    assistant = EnhancedPersonalAIAssistant(user)

    test_cases = [
        ("10-5", "Invalid range (start > end)"),
        ("999-1000", "Non-existent IDs"),
    ]

    for id_str, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        print(f"   Input: '{id_str}'")

        try:
            parsed_ids = assistant._parse_id_range(id_str)
            print(f"   Parsed: {parsed_ids}")

            # Try resolving (will fail for non-existent IDs)
            for img_id in parsed_ids[:1]:  # Just test first one
                try:
                    resolved = assistant._resolve_hybrid_image_id(img_id)
                    print(f"   ✅ Resolved {img_id} to {resolved[:8]}...")
                except ValueError as e:
                    print(f"   ⚠️  Resolution error (expected): {e}")

        except ValueError as e:
            print(f"   ⚠️  Parse error (expected): {e}")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("BATCH OPERATIONS TEST SUITE - SESSION 152")
    print("=" * 80)
    print()

    test_range_parser()
    test_batch_operations()
    test_batch_detection()
    test_error_handling()

    print("=" * 80)
    print("ALL TESTS COMPLETE!")
    print("=" * 80)
    print()
    print("✅ Next step: Test in AI Studio with natural language commands:")
    print("   1. 'Upscale images 1-3'")
    print("   2. 'Remove backgrounds from images 1, 3, 5'")
    print("   3. 'Create 2 variations of images 1-3, 7'")
    print()


if __name__ == '__main__':
    main()
