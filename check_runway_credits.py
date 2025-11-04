#!/usr/bin/env python3
"""
Check Runway ML credit balance and usage
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import RunwayMLProvider
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_credits():
    print("\n💰 Runway ML Credit Report\n")
    print("=" * 60)

    provider = RunwayMLProvider()

    # Get organization info (includes credit balance)
    org_info = provider.get_organization()

    if org_info.get('success'):
        print(f"✅ Organization: Connected")
        print(f"   Credits Remaining: {org_info.get('credits', 'Unknown')}")
    else:
        print(f"❌ Error: {org_info.get('error_message', 'Unknown')}")
        return

    print("\n" + "=" * 60)
    print("📊 Credit Usage (Last 30 Days)\n")

    # Get credit usage for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    usage = provider.get_credit_usage(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    if usage.get('success'):
        daily_usage = usage.get('data', {}).get('dailyUsage', [])

        total_used = 0
        usage_by_model = {}

        for day in daily_usage:
            for model_usage in day.get('modelUsage', []):
                model = model_usage.get('model', 'unknown')
                credits = model_usage.get('creditsUsed', 0)
                total_used += credits

                if model not in usage_by_model:
                    usage_by_model[model] = 0
                usage_by_model[model] += credits

        print(f"Total Credits Used (30 days): {total_used}")
        print(f"\nBreakdown by Model:")

        for model, credits in sorted(usage_by_model.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {model}: {credits} credits")
    else:
        print(f"❌ Could not retrieve usage: {usage.get('error_message', 'Unknown')}")

    print("\n" + "=" * 60)
    print("💡 Credit Costs Reference\n")
    print("Video Generation:")
    print("  - Text-to-Video (veo3.1_fast): 20 credits/second")
    print("  - Text-to-Video (veo3.1): 40 credits/second")
    print("  - Image-to-Video (gen4_turbo): 5 credits/second")
    print("  - Video-to-Video (gen4_aleph): 15 credits/second")
    print("  - Video Upscaling: 10 credits/second")
    print("  - Character Performance: ~15-20 credits/second")
    print("\nAudio Generation:")
    print("  - Text-to-Speech: ~10 credits per generation")
    print("  - Text-to-Sound: ~10 credits per generation")
    print("  - Voice Dubbing: ~20 credits per audio")
    print("  - Speech-to-Speech: ~15 credits per audio")
    print("  - Voice Isolation: ~15 credits per audio")
    print("\nImage Generation:")
    print("  - Text-to-Image: 1 credit per image")

    print("\n" + "=" * 60)
    print("📈 Starting Balance vs Current\n")

    current = org_info.get('credits', 900)
    started_with = 4070  # From CLAUDE.md
    used = started_with - current

    print(f"Started With: {started_with} credits")
    print(f"Current Balance: {current} credits")
    print(f"Total Used: {used} credits ({(used/started_with*100):.1f}%)")
    print(f"Remaining: {(current/started_with*100):.1f}%")

    # Estimate what you can still do
    print("\n" + "=" * 60)
    print("🎯 What You Can Still Do With 900 Credits\n")
    print(f"Text-to-Video (4s, veo3.1_fast): ~{900//80} videos")
    print(f"Image-to-Video (5s, gen4_turbo): ~{900//25} videos")
    print(f"Character Performance (6s): ~{900//120} animations")
    print(f"Video Upscaling (4s): ~{900//40} upscales")
    print(f"Text-to-Speech: ~{900//10} audio generations")
    print(f"Text-to-Image: {900} images!")

    print("\n💡 Tip: Use shorter durations to conserve credits!")
    print("   - 4 seconds instead of 8 = 50% savings")
    print("   - Text-to-image is cheapest (1 credit each)")
    print("   - Image-to-video cheaper than text-to-video")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_credits()
