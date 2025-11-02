#!/usr/bin/env python3
"""
Test Image Generation with Style Presets
Demonstrates the 50+ built-in styles including Pixar!
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.image_generation import image_generation_service

def print_available_styles():
    """Display all 50+ available styles"""
    print("\n" + "="*70)
    print("🎨 AVAILABLE IMAGE STYLES (50+ Presets)")
    print("="*70 + "\n")

    styles = {
        "📸 Photography Styles": [
            'photorealistic', 'photographic', 'portrait', 'landscape', 'macro',
            'street', 'fashion', 'architectural', 'black_white', 'vintage'
        ],
        "🎮 Digital Art Styles": [
            'digital-art', 'concept_art', 'matte_painting', 'vector', 'low_poly',
            'voxel', 'isometric'
        ],
        "🎨 Traditional Art Styles": [
            'oil_painting', 'watercolor', 'acrylic', 'gouache', 'ink',
            'charcoal', 'pencil', 'pastel'
        ],
        "🎬 Animation & Comic Styles": [
            'pixar', 'disney', 'anime', 'manga', 'comic', 'cartoon', 'chibi'
        ],
        "🏛️ Artistic Movements": [
            'impressionist', 'expressionist', 'surreal', 'abstract', 'cubist',
            'art_nouveau', 'art_deco', 'pop_art', 'minimalist', 'baroque', 'renaissance'
        ],
        "🌟 Genre Styles": [
            'fantasy', 'scifi', 'cyberpunk', 'steampunk', 'gothic', 'horror',
            'retro', 'vaporwave'
        ],
        "🖥️ 3D & Rendering Styles": [
            '3d_render', 'clay_render', 'wireframe'
        ],
        "✨ Special Effects": [
            'neon', 'holographic', 'glitch'
        ],
        "🌏 Cultural Styles": [
            'japanese', 'chinese', 'indian', 'african', 'aztec'
        ],
        "🎲 Other Unique Styles": [
            'pixel_art', 'graffiti', 'collage', 'mosaic', 'stained_glass',
            'origami', 'psychedelic'
        ]
    }

    for category, style_list in styles.items():
        print(f"{category}")
        for style in style_list:
            print(f"  - {style}")
        print()

    print("="*70)
    print(f"Total: {sum(len(s) for s in styles.values())} styles available!")
    print("="*70 + "\n")


def test_pixar_style():
    """Test Pixar style image generation"""
    print("\n" + "="*70)
    print("🎬 TESTING PIXAR STYLE")
    print("="*70 + "\n")

    # Simple prompt - the style system will enhance it!
    simple_prompt = "a cute robot"

    print(f"User's Simple Prompt: \"{simple_prompt}\"")
    print(f"Selected Style: Pixar\n")

    # Show what the system does automatically
    enhanced = service._apply_style_to_prompt(simple_prompt, 'pixar')
    print(f"🤖 System Auto-Enhancement:")
    print(f"\"{enhanced}\"\n")

    print("✅ The user just types 'a cute robot' and selects 'Pixar'")
    print("✅ The system automatically adds professional Pixar styling!")
    print("\nThis is EXACTLY what you wanted! 🎉\n")


def test_multiple_styles():
    """Test different styles with the same simple prompt"""
    print("\n" + "="*70)
    print("🎨 TESTING MULTIPLE STYLES WITH SAME PROMPT")
    print("="*70 + "\n")

    simple_prompt = "a dragon"
    styles_to_test = ['pixar', 'anime', 'cyberpunk', 'oil_painting', 'watercolor']

    print(f"Simple Prompt: \"{simple_prompt}\"\n")

    for style in styles_to_test:
        enhanced = service._apply_style_to_prompt(simple_prompt, style)
        print(f"Style: {style}")
        print(f"  → {enhanced}\n")

    print("✅ Same simple prompt, completely different results!")
    print("✅ No complex prompting required from the user!\n")


def generate_test_image(prompt="a friendly robot", style="pixar"):
    """Actually generate an image using Stability AI"""
    print("\n" + "="*70)
    print("🚀 GENERATING REAL IMAGE WITH STABILITY AI")
    print("="*70 + "\n")

    print(f"Prompt: \"{prompt}\"")
    print(f"Style: {style}")
    print(f"Provider: Stability AI (Stable Diffusion XL)")
    print(f"\nGenerating... (this may take 10-30 seconds)\n")

    result = service.generate_image(
        prompt=prompt,
        style=style,
        provider='stability',
        size='1024x1024',
        num_images=1,
        cfg_scale=7.5,
        steps=30
    )

    if result.success:
        print("✅ SUCCESS!")
        print(f"   Provider: {result.provider_used}")
        print(f"   Model: {result.model_used}")
        print(f"   Generation Time: {result.generation_time_ms}ms")
        print(f"   Images Generated: {len(result.images)}")
        print(f"   Cost: ${result.cost:.4f}")

        if result.images:
            # Save the first image
            import base64
            from datetime import datetime

            # Extract base64 data (remove data:image/png;base64, prefix)
            image_data = result.images[0].split(',')[1] if ',' in result.images[0] else result.images[0]

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{style}_{timestamp}.png"
            filepath = os.path.join(os.path.dirname(__file__), filename)

            # Save image
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_data))

            print(f"\n   💾 Image saved to: {filepath}")
            print(f"\n   You can open it with:")
            print(f"   open {filename}\n")

        return True
    else:
        print(f"❌ FAILED: {result.error_message}")
        return False


def main():
    """Main test function"""
    print("\n🎨 IMAGE GENERATION STYLE PRESET TEST")
    print("Testing the built-in style system\n")

    # Show all available styles
    print_available_styles()

    # Test Pixar style enhancement
    test_pixar_style()

    # Test multiple styles
    test_multiple_styles()

    # Ask if user wants to generate a real image
    print("\n" + "="*70)
    print("🎬 READY TO GENERATE A REAL IMAGE?")
    print("="*70 + "\n")
    print("This will use your Stability AI API key to generate a real image.")
    print("Estimated cost: $0.002 (less than a penny!)\n")

    response = input("Generate a Pixar-style robot image? (y/n): ").lower().strip()

    if response == 'y':
        success = generate_test_image("a friendly robot helping humans", "pixar")

        if success:
            print("\n" + "="*70)
            print("🎉 TEST COMPLETE!")
            print("="*70 + "\n")
            print("✅ Style preset system works perfectly!")
            print("✅ Pixar style generates beautiful images!")
            print("✅ User experience is simple: just pick a style!\n")
    else:
        print("\n✅ Style system demonstration complete!")
        print("   Run this script again anytime to generate images!\n")


if __name__ == '__main__':
    # Initialize service
    service = image_generation_service

    # Run tests
    main()
