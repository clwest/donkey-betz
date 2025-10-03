#!/usr/bin/env python
"""Monitor active spider deployment progress"""

import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import SpiderData
from django.db.models import Count

# Get current stats
total_count = SpiderData.objects.count()
print(f"\n{'='*80}")
print(f"SPIDER DEPLOYMENT MONITORING - {datetime.now().strftime('%H:%M:%S')}")
print(f"{'='*80}")
print(f"\n📊 Total SpiderData Entries: {total_count}")
print(f"   (Started at: 872)")
print(f"   New entries: {total_count - 872}")

# Breakdown by spider type
print(f"\n📋 Data by Spider Type:")
breakdown = SpiderData.objects.values('spider_name').annotate(
    count=Count('spider_name')
).order_by('-count')[:15]

for item in breakdown:
    print(f"   • {item['spider_name']}: {item['count']} entries")

# Recent data
recent = SpiderData.objects.order_by('-created_at')[:5]
print(f"\n🕐 Most Recent Data:")
for entry in recent:
    print(f"   • {entry.spider_name} | {entry.data_type} | Quality: {entry.quality_score:.2f} | {entry.created_at.strftime('%H:%M:%S')}")

print(f"\n{'='*80}\n")
