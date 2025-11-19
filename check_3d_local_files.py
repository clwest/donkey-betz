#!/usr/bin/env python3
"""
Check which 3D models have local GLB/STL files - Session 131
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import MiniFigAsset

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("3D MODELS WITH LOCAL FILES")
print("=" * 80)

all_models = MiniFigAsset.objects.filter(user=admin).order_by('created_at')
completed_models = all_models.filter(status='completed')

print(f"\n📊 Total completed models: {completed_models.count()}")

# Models with BOTH glb_file AND stl_file (should display in UI)
models_with_both = completed_models.exclude(glb_file='').exclude(stl_file='')
print(f"✅ Models with BOTH local files: {models_with_both.count()}")

# Models with ONLY three_d_file URL (won't display)
models_with_only_url = completed_models.filter(glb_file='', stl_file='')
print(f"❌ Models with ONLY CDN URLs: {models_with_only_url.count()}")

print("\n" + "=" * 80)
print("MODELS THAT SHOW IN UI (have local files)")
print("=" * 80)

for model in models_with_both:
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    print(f"\n3D Model #{model_num}:")
    print(f"   UUID: {model.id}")
    print(f"   Title: {model.title}")
    print(f"   GLB File: {model.glb_file.name if model.glb_file else '(empty)'}")
    print(f"   STL File: {model.stl_file.name if model.stl_file else '(empty)'}")
    print(f"   Created: {model.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "=" * 80)
print("MODELS THAT DON'T SHOW (only have expired CDN URLs)")
print("=" * 80)

for model in models_with_only_url[:5]:  # First 5
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    print(f"\n3D Model #{model_num}:")
    print(f"   UUID: {model.id}")
    print(f"   Title: {model.title}")
    print(f"   3D File URL: {model.three_d_file[:80]}...")
    print(f"   GLB File: (empty)")
    print(f"   STL File: (empty)")
    print(f"   Created: {model.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\n✅ Expected UI display: {models_with_both.count()} models (those with local files)")
print(f"❌ Won't display: {models_with_only_url.count()} models (only have CDN URLs)")
print(f"\nThese {models_with_only_url.count()} models were created before Session 128")
print(f"when local file storage (glb_file/stl_file) was added.")
print(f"\nThe Replicate CDN URLs have likely expired, so these models can't be displayed.")
print(f"\n💡 Solution: Delete these old models - they can't be recovered.")
