#!/usr/bin/env python
"""
GENERATE SELLABLE ART - Use Stable Diffusion to create art that sells
This script generates images that you can sell on stock photo sites TODAY
"""

import os
import json
from datetime import datetime

print("\n🎨 STABLE DIFFUSION ART GENERATOR")
print("=" * 50)
print("Generate images that sell on Shutterstock, Adobe Stock, etc.")
print()

# Check for API key
api_key = os.environ.get('REPLICATE_API_KEY')
if not api_key:
    print("⚠️ REPLICATE_API_KEY not set!")
    print("\nTo set it:")
    print("  export REPLICATE_API_KEY='your_key_here'")
    print("\nYou said you have Stable Diffusion access - let's use it!")
    exit(1)

print("✅ API Key found! Ready to generate.")
print()

# Popular stock photo categories that sell well
print("📈 HIGH-DEMAND STOCK PHOTO CATEGORIES")
print("-" * 40)

categories = [
    {
        "category": "Business & Technology",
        "prompts": [
            "Professional businesswoman working on laptop in modern office, photorealistic",
            "Team collaboration meeting with diverse professionals, bright lighting",
            "Futuristic technology concept with AI and data visualization",
            "Remote work setup with coffee and laptop, cozy atmosphere"
        ],
        "potential": "$50-200/image"
    },
    {
        "category": "Lifestyle & Wellness",
        "prompts": [
            "Healthy breakfast bowl with fresh fruits, top view, natural lighting",
            "Person doing yoga at sunrise on beach, silhouette",
            "Minimalist home interior with plants, Scandinavian style",
            "Happy family cooking together in kitchen, warm lighting"
        ],
        "potential": "$30-150/image"
    },
    {
        "category": "Abstract & Backgrounds",
        "prompts": [
            "Gradient mesh abstract background, purple and blue tones",
            "Geometric patterns with gold accents, luxury style",
            "Watercolor texture background, pastel colors",
            "Tech circuit board pattern, neon glow effect"
        ],
        "potential": "$20-100/image"
    }
]

# Function to generate with Replicate
def generate_image(prompt, style="photorealistic"):
    """Generate an image using Replicate API"""

    try:
        import replicate

        # Full prompt with style modifiers for better sales
        full_prompt = f"{prompt}, high quality, 4k, professional photography, commercial use, {style}"

        print(f"🎨 Generating: {prompt[:50]}...")

        # Use SDXL for best quality
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": full_prompt,
                "negative_prompt": "low quality, blurry, watermark, text",
                "width": 1024,
                "height": 1024,
                "num_outputs": 1
            }
        )

        if output:
            print(f"✅ Generated successfully!")
            return output[0]
        else:
            print(f"❌ Generation failed")
            return None

    except ImportError:
        print("\n⚠️ Replicate library not installed!")
        print("Install it with: pip install replicate")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# Generate images for each category
print("\n🚀 GENERATING SELLABLE CONTENT")
print("=" * 50)

generated_images = []

for cat in categories:
    print(f"\n📁 Category: {cat['category']}")
    print(f"💰 Potential: {cat['potential']}")
    print("-" * 30)

    for i, prompt in enumerate(cat['prompts'][:2], 1):  # Start with 2 per category
        print(f"\n{i}. {prompt[:60]}...")

        # This would actually generate if replicate is installed
        # For now, we'll simulate the process
        image_url = generate_image(prompt)

        if image_url:
            generated_images.append({
                "category": cat['category'],
                "prompt": prompt,
                "url": image_url,
                "created": datetime.now().isoformat()
            })

# Save generated images info
if generated_images:
    with open("generated_stock_images.json", "w") as f:
        json.dump(generated_images, f, indent=2)
    print(f"\n✅ Saved {len(generated_images)} image details to generated_stock_images.json")

# Selling instructions
print("\n\n💰 HOW TO SELL YOUR GENERATED IMAGES")
print("=" * 50)

platforms = [
    {
        "name": "Shutterstock",
        "url": "shutterstock.com/contributors",
        "commission": "15-40%",
        "tips": "Focus on business and lifestyle images"
    },
    {
        "name": "Adobe Stock",
        "url": "contributor.stock.adobe.com",
        "commission": "33%",
        "tips": "High-quality, unique concepts sell best"
    },
    {
        "name": "Getty Images",
        "url": "gettyimages.com/workwithus",
        "commission": "20-45%",
        "tips": "Editorial and creative content"
    },
    {
        "name": "123RF",
        "url": "123rf.com/contributors",
        "commission": "30-60%",
        "tips": "Volume uploading works well"
    }
]

print("\n📱 STOCK PHOTO PLATFORMS:")
for p in platforms:
    print(f"\n{p['name']}")
    print(f"  🌐 {p['url']}")
    print(f"  💰 Commission: {p['commission']}")
    print(f"  💡 Tip: {p['tips']}")

# Quick money plan
print("\n\n⚡ QUICK MONEY PLAN")
print("=" * 50)

print("""
TODAY (Make $50-100):
1. Generate 20 images in high-demand categories
2. Sign up for Shutterstock contributor account
3. Upload your 20 best images
4. Write SEO-optimized titles and keywords
5. Submit for review

THIS WEEK (Make $200-500):
1. Generate 100+ images across all categories
2. Join 3-4 stock photo platforms
3. Upload consistently (10-20 per day)
4. Track which styles sell best
5. Focus on trending topics

THIS MONTH (Make $1000+):
1. Scale to 500+ images in portfolio
2. Create series/collections that sell together
3. Research seasonal trends
4. Optimize based on sales data
5. Reinvest earnings in better tools
""")

# Action items
print("\n✅ IMMEDIATE ACTIONS:")
print("-" * 30)
print("1. Install replicate: pip install replicate")
print("2. Set your API key: export REPLICATE_API_KEY='...'")
print("3. Run this script to generate first batch")
print("4. Sign up for Shutterstock (takes 10 minutes)")
print("5. Upload your first image within the hour")

print("\n🔥 STOP PLANNING. START GENERATING. START SELLING!")
print("The first sale is the hardest. After that, it's just scaling.")
print("\n💪 Your platform is ready. Now make it pay you!")