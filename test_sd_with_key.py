#!/usr/bin/env python
"""
Test Stable Diffusion with the configured API key
"""

import os
import sys
import django

# Ensure the key is loaded from .env
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.image_generation import ImageGenerationService
import json

# Create a fresh instance to pick up the new keys
service = ImageGenerationService()

print("\n" + "🎨"*20)
print("STABLE DIFFUSION TEST WITH API KEY")
print("🎨"*20)

# Check which providers are available
print("\n✅ Provider Status:")
print(f"  Stability AI: {'✅ Ready' if service.stability_key else '❌ Not configured'}")
print(f"  Replicate: {'✅ Ready' if service.replicate_key else '❌ Not configured'}")
print(f"  OpenAI: {'✅ Ready' if service.openai_key else '❌ Not configured'}")

if service.stability_key:
    print(f"\n  Stability key detected: {service.stability_key[:10]}...")

# Test image generation with auto provider (should use Stable Diffusion)
print("\n🖼️ Testing Image Generation (auto-select provider)...")

test_cases = [
    {
        'prompt': "A majestic dragon flying over a fantasy castle at sunset",
        'style': 'fantasy',
        'negative_prompt': 'low quality, blurry, distorted'
    },
    {
        'prompt': "A cyberpunk street scene with neon lights",
        'style': 'cyberpunk',
        'negative_prompt': 'boring, plain, low detail'
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n📝 Test {i}: {test['prompt'][:50]}...")
    print(f"   Style: {test['style']}")

    result = service.generate_image(
        prompt=test['prompt'],
        style=test['style'],
        negative_prompt=test['negative_prompt'],
        size='1024x1024',
        provider='auto',  # Will auto-select Stable Diffusion first
        cfg_scale=7.5,
        steps=30,
        num_images=1
    )

    if result.success:
        print(f"   ✅ Success!")
        print(f"   Provider used: {result.provider_used}")
        print(f"   Model: {result.model_used}")
        print(f"   Generation time: {result.generation_time_ms}ms")

        if result.images:
            if result.images[0].startswith('data:image'):
                print(f"   Image type: Base64 encoded")
                # Save the image
                import base64
                from PIL import Image
                from io import BytesIO

                try:
                    base64_str = result.images[0].split(',')[1]
                    img_data = base64.b64decode(base64_str)

                    output_path = f"/tmp/stable_diffusion_test_{i}.png"
                    with open(output_path, 'wb') as f:
                        f.write(img_data)

                    img = Image.open(BytesIO(img_data))
                    print(f"   Saved to: {output_path}")
                    print(f"   Dimensions: {img.size}")
                except Exception as e:
                    print(f"   Could not save: {e}")
            else:
                print(f"   Image URL: {result.images[0][:100]}...")
    else:
        print(f"   ❌ Failed: {result.error_message}")

    # Only test one for speed
    break

print("\n" + "="*60)

if service.stability_key and result.provider_used == 'stability':
    print("🎉 SUCCESS! Stable Diffusion is now your primary image generator!")
    print("All image generation will use Stable Diffusion instead of DALL-E.")
elif service.stability_key:
    print("⚠️ Stability key is configured but there might be an issue.")
    print("Check the error message above for details.")
else:
    print("❌ Stability API key not detected.")
    print("Make sure your .env file is loaded correctly.")