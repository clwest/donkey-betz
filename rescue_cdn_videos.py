#!/usr/bin/env python
"""
Session 119: Rescue videos with CDN URLs by downloading them to local storage
This fixes videos that have expired Runway ML CloudFront URLs
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from content.models import VideoHistory
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def rescue_cdn_videos():
    """Download all videos with CDN URLs to local storage"""

    # Find all videos with CDN URLs
    cdn_videos = VideoHistory.objects.filter(
        video_url__icontains='cloudfront.net'
    ) | VideoHistory.objects.filter(
        video_url__icontains='storage.googleapis.com'
    )

    total = cdn_videos.count()
    logger.info(f"🔍 Found {total} videos with CDN URLs")

    if total == 0:
        logger.info("✅ No videos to rescue!")
        return

    success_count = 0
    fail_count = 0

    for i, video in enumerate(cdn_videos, 1):
        logger.info(f"\n[{i}/{total}] Processing Video #{video.get_sequential_number()} (ID: {video.id})")
        logger.info(f"   Current URL: {video.video_url[:100]}...")

        try:
            # Try to download the video
            logger.info(f"   📥 Downloading...")
            response = requests.get(video.video_url, timeout=120, stream=True)
            response.raise_for_status()

            # Read video content
            video_content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    video_content += chunk

            # Generate filename
            filename = f"rescued_videos/{video.id}.mp4"

            # Save to local storage
            file_path = default_storage.save(filename, ContentFile(video_content))
            local_url = default_storage.url(file_path)

            # Update video URL
            video.video_url = local_url
            video.save(update_fields=['video_url'])

            logger.info(f"   ✅ Saved to: {file_path}")
            success_count += 1

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning(f"   ❌ EXPIRED (401 Unauthorized) - Cannot rescue")
            else:
                logger.warning(f"   ❌ HTTP Error {e.response.status_code}: {e}")
            fail_count += 1

        except Exception as e:
            logger.error(f"   ❌ Download failed: {str(e)}")
            fail_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Rescue Summary:")
    logger.info(f"   Total videos: {total}")
    logger.info(f"   ✅ Successfully rescued: {success_count}")
    logger.info(f"   ❌ Failed (likely expired): {fail_count}")
    logger.info(f"{'='*60}")

if __name__ == '__main__':
    rescue_cdn_videos()
