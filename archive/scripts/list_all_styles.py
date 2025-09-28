#!/usr/bin/env python
"""
List all available Stable Diffusion styles
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.image_generation import ImageGenerationService

service = ImageGenerationService()

# Get the style mappings by calling the method with a test prompt
test_prompt = "test"
styled_prompt = service._apply_style_to_prompt(test_prompt, "photorealistic")

# Extract styles from the method
import inspect
source = inspect.getsource(service._apply_style_to_prompt)

# Parse styles from the source
styles = []
categories = {}
current_category = None

for line in source.split('\n'):
    if '# ' in line and 'Styles' in line:
        # Found a category comment
        current_category = line.strip().replace('#', '').strip()
        categories[current_category] = []
    elif "'" in line and ':' in line and 'f"' in line:
        # Found a style definition
        style_name = line.split("'")[1]
        styles.append(style_name)
        if current_category:
            categories[current_category].append(style_name)

print("\n" + "🎨"*30)
print(f"STABLE DIFFUSION STYLE LIBRARY - {len(styles)} STYLES AVAILABLE!")
print("🎨"*30)

# Print by category
for category, style_list in categories.items():
    if style_list:  # Only show categories that have styles
        print(f"\n📁 {category} ({len(style_list)} styles)")
        print("─" * 50)
        for i, style in enumerate(style_list, 1):
            print(f"  {i:2}. {style}")

print("\n" + "="*60)
print(f"🎯 TOTAL STYLES AVAILABLE: {len(styles)}")
print("="*60)

print("\n💡 HOW TO USE:")
print("─" * 30)
print("In the frontend, select any style from the dropdown")
print("Or in code, specify the style parameter:")
print('  result = generate_image(prompt="...", style="cyberpunk")')

print("\n🚀 STYLE CATEGORIES:")
unique_categories = [cat for cat in categories.keys() if categories[cat]]
for i, cat in enumerate(unique_categories, 1):
    print(f"  {i}. {cat}")

print("\n✨ PRO TIP: Stable Diffusion works best with these styles!")
print("Each style is optimized with specific keywords for SD/SDXL.")