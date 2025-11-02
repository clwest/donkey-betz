#!/usr/bin/env python
"""
Test Stable Diffusion Image Generation
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.image_generation import image_generation_service
import base64
from PIL import Image
from io import BytesIO


def test_provider_priority():
    """Test that Stable Diffusion is prioritized"""
    print("\n" + "="*60)
    print("TEST: Provider Priority Check")
    print("="*60)

    print(f"Stability API Key: {'✅ Configured' if image_generation_service.stability_key else '❌ Not configured'}")
    print(f"Replicate API Key: {'✅ Configured' if image_generation_service.replicate_key else '❌ Not configured'}")
    print(f"OpenAI API Key: {'✅ Configured' if image_generation_service.openai_key else '❌ Not configured'}")

    # Test auto-selection
    if image_generation_service.stability_key:
        print("\n✅ Stable Diffusion (Stability AI) will be used as primary provider")
    elif image_generation_service.replicate_key:
        print("\n⚠️ Replicate will be used (can run SDXL models)")
    elif image_generation_service.openai_key:
        print("\n⚠️ DALL-E will be used as fallback")
    else:
        print("\n❌ No image generation providers configured!")


def test_stable_diffusion_generation():
    """Test Stable Diffusion image generation"""
    print("\n" + "="*60)
    print("TEST: Stable Diffusion Generation")
    print("="*60)

    test_prompts = [
        {
            'prompt': "A majestic mountain landscape at sunset",
            'style': 'photorealistic',
            'negative_prompt': 'blurry, low quality, distorted'
        },
        {
            'prompt': "A futuristic cyberpunk city",
            'style': 'cyberpunk',
            'negative_prompt': 'boring, plain, low detail'
        },
        {
            'prompt': "A fantasy dragon",
            'style': 'fantasy',
            'negative_prompt': 'cartoon, childish, low quality'
        }
    ]

    for test_case in test_prompts[:1]:  # Test just one for speed
        print(f"\n🎨 Generating: {test_case['prompt']}")
        print(f"   Style: {test_case['style']}")

        result = image_generation_service.generate_image(
            prompt=test_case['prompt'],
            style=test_case['style'],
            negative_prompt=test_case['negative_prompt'],
            size='1024x1024',
            provider='auto',  # Will use Stable Diffusion if available
            cfg_scale=7.5,
            steps=30,
            num_images=1
        )

        if result.success:
            print(f"   ✅ Success!")
            print(f"   Provider: {result.provider_used}")
            print(f"   Model: {result.model_used}")
            print(f"   Time: {result.generation_time_ms}ms")
            print(f"   Images generated: {len(result.images)}")

            if result.images:
                # Check if it's a base64 image
                if result.images[0].startswith('data:image'):
                    print(f"   Image format: Base64 data URL")
                    # Extract and save the image
                    save_base64_image(result.images[0], f"test_{test_case['style']}.png")
                else:
                    print(f"   Image URL: {result.images[0][:100]}...")
        else:
            print(f"   ❌ Failed: {result.error_message}")

    return result.success if 'result' in locals() else False


def save_base64_image(data_url: str, filename: str):
    """Save base64 image to file"""
    try:
        # Remove the data URL prefix
        base64_str = data_url.split(',')[1] if ',' in data_url else data_url

        # Decode base64
        image_data = base64.b64decode(base64_str)

        # Save to file
        output_path = f"/tmp/{filename}"
        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"   📁 Image saved to: {output_path}")

        # Also get image dimensions
        img = Image.open(BytesIO(image_data))
        print(f"   📐 Dimensions: {img.size}")

    except Exception as e:
        print(f"   ⚠️ Could not save image: {e}")


def test_style_variations():
    """Test different artistic styles"""
    print("\n" + "="*60)
    print("TEST: Style Variations")
    print("="*60)

    base_prompt = "A serene Japanese garden"
    styles = ['photorealistic', 'anime', 'watercolor', 'minimalist']

    for style in styles:
        print(f"\n🎨 Style: {style}")

        # Apply style to prompt
        styled_prompt = image_generation_service._apply_style_to_prompt(base_prompt, style)
        print(f"   Styled prompt: {styled_prompt[:150]}...")

    return True


def main():
    """Run all tests"""
    print("\n" + "🖼️"*20)
    print("STABLE DIFFUSION INTEGRATION TEST")
    print("🖼️"*20)

    # Check environment
    print("\n📋 Checking environment variables...")
    if 'STABILITY_API_KEY' in os.environ:
        print("✅ STABILITY_API_KEY is set")
    else:
        print("❌ STABILITY_API_KEY not found in environment")
        print("   Set it with: export STABILITY_API_KEY='REDACTED'")

    # Run tests
    test_provider_priority()
    test_style_variations()

    # Only test generation if we have a provider configured
    if any([
        image_generation_service.stability_key,
        image_generation_service.replicate_key,
        image_generation_service.openai_key
    ]):
        success = test_stable_diffusion_generation()

        if success:
            print("\n🎉 Stable Diffusion integration working!")
        else:
            print("\n⚠️ Image generation had issues")
    else:
        print("\n⚠️ Skipping generation test - no providers configured")
        print("\nTo use Stable Diffusion, add to your .env file:")
        print("STABILITY_API_KEY=your-stability-ai-key")
        print("\nOr to use Replicate (SDXL):")
        print("REPLICATE_API_KEY=your-replicate-key")


if __name__ == "__main__":
    main()