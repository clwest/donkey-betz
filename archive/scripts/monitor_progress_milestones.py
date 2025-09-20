#!/usr/bin/env python
"""
Monitor embedding generation progress and report at 10% milestones
"""

import os
import sys
import time
import django
from datetime import datetime

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def get_progress():
    """Get current embedding progress"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(embedding) as has_embedding
            FROM unified_embeddings
        """)
        total, has_embedding = cursor.fetchone()
        percentage = (has_embedding / total * 100) if total > 0 else 0
        return total, has_embedding, percentage

def main():
    print("=" * 60)
    print("EMBEDDING GENERATION PROGRESS MONITOR")
    print("Starting monitoring at 10% intervals...")
    print("=" * 60)
    
    # Track milestones
    last_milestone = 30  # Start from 30% (we're already past that)
    start_time = datetime.now()
    initial_total, initial_count, initial_pct = get_progress()
    
    print(f"\nStarting point: {initial_count:,}/{initial_total:,} ({initial_pct:.1f}%)")
    
    while True:
        time.sleep(30)  # Check every 30 seconds
        
        total, has_embedding, percentage = get_progress()
        
        # Check if we've reached a new 10% milestone
        current_milestone = int(percentage / 10) * 10
        
        if current_milestone > last_milestone:
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            rate = (has_embedding - initial_count) / elapsed if elapsed > 0 else 0
            remaining = total - has_embedding
            eta_minutes = remaining / rate if rate > 0 else 0
            
            print(f"\n{'=' * 60}")
            print(f"🎯 {current_milestone}% MILESTONE REACHED!")
            print(f"{'=' * 60}")
            print(f"Progress: {has_embedding:,}/{total:,} embeddings")
            print(f"Completed: {has_embedding - initial_count:,} in {elapsed:.1f} minutes")
            print(f"Rate: {rate:.0f} embeddings/minute")
            print(f"Remaining: {remaining:,} embeddings")
            print(f"ETA: ~{eta_minutes:.0f} minutes")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            
            last_milestone = current_milestone
            
            # Check if complete
            if percentage >= 99.9:
                print(f"\n✅ EMBEDDING GENERATION COMPLETE!")
                print(f"Total embeddings: {has_embedding:,}")
                print(f"Total time: {elapsed:.1f} minutes")
                break
        
        # Also print if process appears to have stopped
        if percentage < 99.9:
            # Check if the generation script is still running
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'generate_all_embeddings.py' not in result.stdout:
                print(f"\n⚠️  Generation process stopped at {percentage:.1f}%")
                print(f"Current count: {has_embedding:,}/{total:,}")
                print("Run 'python generate_all_embeddings.py' to continue")
                break

if __name__ == "__main__":
    main()