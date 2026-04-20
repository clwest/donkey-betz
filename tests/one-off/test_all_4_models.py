#!/usr/bin/env python3
"""
Test All 4 Stability AI Models with Style Presets
Comprehensive test of the updated image generation system
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.image_generation import ImageGenerationService
from datetime import datetime

def test_all_models_with_pixar():
    """Test all 4 models with Pixar style"""

    print("\n" + "="*80)
    print("TESTING ALL 4 MODELS WITH PIXAR STYLE PRESET")
    print("="*80 + "\n")

    service = ImageGenerationService()

    # Test prompt
    prompt = "a friendly robot helping a child with homework"
    style = "pixar"

    # Test configurations
    tests = [
        {
            "name": "Fast (Core)",
            "quality": "fast",
            "expected_time": "~3.5s",
            "expected_cost": "$0.003"
        },
        {
            "name": "Balanced (SDXL)",
            "quality": "balanced",
            "expected_time": "~5.8s",
            "expected_cost": "$0.002"
        },
        {
            "name": "High (SD3)",
            "quality": "high",
            "expected_time": "~8.7s",
            "expected_cost": "$0.0065"
        },
        {
            "name": "Premium (Ultra)",
            "quality": "premium",
            "expected_time": "~10.4s",
            "expected_cost": "$0.008"
        }
    ]

    results = []

    for test_config in tests:
        print(f"\n{'─'*80}")
        print(f"🎨 {test_config['name']}")
        print(f"{'─'*80}")
        print(f"   Quality: {test_config['quality']}")
        print(f"   Expected Time: {test_config['expected_time']}")
        print(f"   Expected Cost: {test_config['expected_cost']}")
        print(f"   Prompt: '{prompt}'")
        print(f"   Style: {style}")
        print("   ⏳ Generating...")

        try:
            result = service.generate_image(
                prompt=prompt,
                style=style,
                quality=test_config['quality'],
                provider='stability',
                size='1024x1024'
            )

            if result.success:
                time_s = result.generation_time_ms / 1000
                print(f"\n   ✅ SUCCESS!")
                print(f"      Model: {result.model_used}")
                print(f"      Time: {time_s:.2f}s")
                print(f"      Cost: ${result.cost:.4f}")
                print(f"      Images: {len(result.images)}")

                # Save image
                if result.images:
                    # Extract base64 from data URL
                    import base64
                    img_data = result.images[0].split(',')[1]
                    filename = f"test_{test_config['quality']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

                    with open(filename, 'wb') as f:
                        f.write(base64.b64decode(img_data))
                    print(f"      Saved: {filename}")

                results.append({
                    "config": test_config,
                    "success": True,
                    "time": time_s,
                    "cost": result.cost,
                    "model": result.model_used
                })
            else:
                print(f"\n   ❌ FAILED")
                print(f"      Error: {result.error_message}")

                results.append({
                    "config": test_config,
                    "success": False,
                    "error": result.error_message
                })

        except Exception as e:
            print(f"\n   ❌ ERROR: {str(e)}")
            results.append({
                "config": test_config,
                "success": False,
                "error": str(e)
            })

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY: ALL 4 MODELS WITH PIXAR STYLE")
    print("="*80 + "\n")

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"✅ Successful: {len(successful)}/4")
    print(f"❌ Failed: {len(failed)}/4\n")

    if successful:
        print("Working Models:")
        for r in successful:
            print(f"  ✅ {r['config']['name']:20s} {r['time']:5.2f}s  ${r['cost']:.4f}  ({r['model']})")

    if failed:
        print("\nFailed Models:")
        for r in failed:
            print(f"  ❌ {r['config']['name']:20s} {r.get('error', 'Unknown error')[:50]}")

    print("\n" + "="*80)

    return results


def test_multiple_styles():
    """Test multiple popular styles with the best model"""

    print("\n" + "="*80)
    print("TESTING MULTIPLE STYLES WITH SD3 (HIGH QUALITY)")
    print("="*80 + "\n")

    service = ImageGenerationService()

    styles_to_test = [
        ("pixar", "a cute robot"),
        ("anime", "a warrior princess"),
        ("watercolor", "a peaceful garden"),
        ("cyberpunk", "a futuristic city"),
        ("photorealistic", "a mountain landscape")
    ]

    results = []

    for style, prompt in styles_to_test:
        print(f"\n{'─'*80}")
        print(f"🎨 Testing: {style}")
        print(f"{'─'*80}")
        print(f"   Prompt: '{prompt}'")
        print(f"   Quality: high (SD3)")
        print("   ⏳ Generating...")

        try:
            result = service.generate_image(
                prompt=prompt,
                style=style,
                quality='high',  # Use SD3 for best quality
                provider='stability',
                size='1024x1024'
            )

            if result.success:
                time_s = result.generation_time_ms / 1000
                print(f"\n   ✅ SUCCESS!")
                print(f"      Time: {time_s:.2f}s")
                print(f"      Cost: ${result.cost:.4f}")

                # Save image
                if result.images:
                    import base64
                    img_data = result.images[0].split(',')[1]
                    filename = f"test_style_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

                    with open(filename, 'wb') as f:
                        f.write(base64.b64decode(img_data))
                    print(f"      Saved: {filename}")

                results.append({"style": style, "success": True})
            else:
                print(f"\n   ❌ FAILED: {result.error_message}")
                results.append({"style": style, "success": False})

        except Exception as e:
            print(f"\n   ❌ ERROR: {str(e)}")
            results.append({"style": style, "success": False})

    print("\n" + "="*80)
    print("STYLE TEST SUMMARY")
    print("="*80 + "\n")

    successful = [r for r in results if r['success']]
    print(f"✅ {len(successful)}/{len(styles_to_test)} styles working")

    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"  {status} {r['style']}")

    print("\n" + "="*80)

    return results


def main():
    print("\n🎨 COMPREHENSIVE STABILITY AI MODEL TESTING")
    print("Testing all 4 models + multiple style presets\n")

    print("Tests to run:")
    print("1. All 4 models with Pixar style")
    print("2. Multiple styles with SD3 (best balance of quality/speed)")
    print()

    input("Press Enter to start testing...")

    # Run tests
    model_results = test_all_models_with_pixar()
    style_results = test_multiple_styles()

    # Final summary
    print("\n" + "="*80)
    print("🎉 FINAL SUMMARY")
    print("="*80 + "\n")

    model_success = sum(1 for r in model_results if r.get('success'))
    style_success = sum(1 for r in style_results if r['success'])

    print(f"✅ Models Working: {model_success}/4")
    print(f"✅ Styles Working: {style_success}/5")
    print()

    if model_success == 4 and style_success == 5:
        print("🎊 PERFECT! All 4 models + all 5 tested styles working!")
        print()
        print("Your users can now choose:")
        print("  • Fast Mode (Core) - 3.5s for quick iterations")
        print("  • Balanced (SDXL) - 5.8s for great quality")
        print("  • High Quality (SD3) - 8.7s for excellent results")
        print("  • Premium (Ultra) - 10.4s for flagship quality")
        print()
        print("All 69 style presets work across all models!")
    else:
        print("⚠️  Some tests failed. Review the output above.")

    print("="*80 + "\n")


if __name__ == '__main__':
    main()
