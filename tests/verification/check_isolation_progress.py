#!/usr/bin/env python
"""
Quick check of isolation progress
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import Document

def check_progress():
    total = Document.objects.count()
    
    namespaces = ['personal', 'system', 'agent_memory', 'public']
    
    print("🔍 Current Isolation Status:")
    print("=" * 50)
    
    for namespace in namespaces:
        count = Document.objects.filter(metadata__namespace=namespace).count()
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{namespace:15} : {count:6} ({percentage:5.1f}%)")
    
    untagged = Document.objects.exclude(metadata__has_key='namespace').count()
    untagged_pct = (untagged / total * 100) if total > 0 else 0
    print(f"{'Untagged':15} : {untagged:6} ({untagged_pct:5.1f}%)")
    print(f"{'TOTAL':15} : {total:6}")
    
    tagged = total - untagged
    progress = (tagged / total * 100) if total > 0 else 0
    
    print(f"\n📊 Progress: {progress:.1f}% complete ({tagged}/{total})")
    
    if untagged == 0:
        print("🎉 ALL DOCUMENTS ISOLATED!")
    else:
        print(f"🔄 {untagged} documents remaining")

if __name__ == '__main__':
    check_progress()