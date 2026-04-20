#!/usr/bin/env python3
"""
Diagnose 3D Model Display Issue - Session 131
User sees only 3 3D models in UI but database has 21 (15 completed)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import models as django_models
from content.models import MiniFigAsset

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("3D MODEL DISPLAY INVESTIGATION")
print("=" * 80)

all_models = MiniFigAsset.objects.filter(user=admin).order_by('created_at')
print(f"\n📊 Total 3D models: {all_models.count()}")

# Status breakdown
completed = all_models.filter(status='completed')
processing = all_models.filter(status='processing')
pending = all_models.filter(status='pending')
failed = all_models.filter(status='failed')

print(f"\n📈 Status Breakdown:")
print(f"   ✅ Completed: {completed.count()}")
print(f"   ⏳ Processing: {processing.count()}")
print(f"   ⏸️  Pending: {pending.count()}")
print(f"   ❌ Failed: {failed.count()}")

# Project association
in_project = all_models.filter(project__isnull=False)
orphaned = all_models.filter(project__isnull=True)

print(f"\n🏢 Project Association:")
print(f"   📁 In project: {in_project.count()}")
print(f"   🚫 Orphaned: {orphaned.count()}")

# File availability
has_glb = all_models.exclude(glb_file='')
has_stl = all_models.exclude(stl_file='')
has_both = all_models.exclude(glb_file='').exclude(stl_file='')

print(f"\n📦 File Availability:")
print(f"   GLB files: {has_glb.count()}")
print(f"   STL files: {has_stl.count()}")
print(f"   Both files: {has_both.count()}")

# What SHOULD show in UI (completed + in project + has files)
should_show = completed.filter(project__isnull=False).exclude(glb_file='').exclude(stl_file='')

print(f"\n🎯 SHOULD SHOW IN UI:")
print(f"   Completed + In Project + Has Both Files: {should_show.count()}")

print("\n" + "=" * 80)
print("DETAILED ANALYSIS OF COMPLETED MODELS")
print("=" * 80)

for model in completed[:10]:  # First 10 completed
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    print(f"\n3D Model #{model_num}:")
    print(f"   UUID: {model.id}")
    print(f"   Title: {model.title}")
    print(f"   Status: {model.status}")
    print(f"   Provider: {model.provider}")
    print(f"   In Project: {'✅ Yes' if model.project else '❌ No (orphaned)'}")
    print(f"   Has GLB: {'✅ Yes' if model.glb_file else '❌ No'}")
    print(f"   Has STL: {'✅ Yes' if model.stl_file else '❌ No'}")
    print(f"   3D File URL: {model.three_d_file[:60] if model.three_d_file else '(empty)'}...")

    # Source tracking
    if model.source_image_asset:
        print(f"   Source Image: Image #{model.source_image_asset.get_sequential_number()}")
    else:
        print(f"   Source Image: (none)")

    # Determine if should show
    should_display = (
        model.status == 'completed' and
        model.project is not None and
        bool(model.glb_file) and
        bool(model.stl_file)
    )
    print(f"   Should Display: {'✅ YES' if should_display else '❌ NO'}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if orphaned.count() > 0:
    print(f"\n1. ORPHANED 3D MODELS:")
    print(f"   Found {orphaned.count()} 3D model(s) not in any project")
    print(f"   These won't show in Projects tab")
    print(f"   Options:")
    print(f"   - Add them to 'AI Content Generation Company' project")
    print(f"   - Or delete them if they're test data")

incomplete_files = completed.filter(project__isnull=False).filter(
    django_models.Q(glb_file='') | django_models.Q(stl_file='')
)
if incomplete_files.exists():
    print(f"\n2. COMPLETED MODELS WITH MISSING FILES:")
    print(f"   Found {incomplete_files.count()} completed model(s) missing GLB or STL files")
    for model in incomplete_files:
        model_num = list(all_models).index(model) + 1
        missing = []
        if not model.glb_file:
            missing.append("GLB")
        if not model.stl_file:
            missing.append("STL")
        print(f"   - 3D Model #{model_num}: Missing {', '.join(missing)}")

placeholder_models = completed.filter(provider='placeholder')
if placeholder_models.exists():
    print(f"\n3. PLACEHOLDER MODELS:")
    print(f"   Found {placeholder_models.count()} model(s) with provider='placeholder'")
    print(f"   These might be test/placeholder data from Session 111")
    print(f"   Consider cleaning up if not needed")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print(f"\n✅ Expected to show: {should_show.count()} (completed + in project + has both files)")
print(f"👀 User sees: 3")
print(f"🔍 Discrepancy: {should_show.count() - 3} models missing from UI")
