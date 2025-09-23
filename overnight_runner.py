#!/usr/bin/env python
"""
Overnight Learning Runner - Simulates data collection every 15 minutes
Run this to have continuous learning overnight
"""

import os
import sys
import time
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models_unified_system import SpiderData, AgentSolution, AgentLearning
from intelligence.spider_agent_connector import SpiderAgentConnector
from django.core.management import call_command
from django.utils import timezone

def run_collection_cycle():
    """Run one collection cycle"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting collection cycle...")
    print(f"{'='*60}")

    try:
        # 1. Activate spiders to collect data
        print("1. Collecting spider data...")
        call_command('activate_spiders', '--simulate')

        # 2. Process spider data through agents
        print("\n2. Processing spider data...")
        call_command('process_spider_data')

        # 3. Connect agents for learning
        print("\n3. Connecting agents for learning...")
        call_command('connect_all_agents')

        # Show stats
        spider_count = SpiderData.objects.count()
        solution_count = AgentSolution.objects.count()
        learning_count = AgentLearning.objects.count()

        print(f"\n📊 Current Totals:")
        print(f"  • Spider Data:     {spider_count}")
        print(f"  • Solutions:       {solution_count}")
        print(f"  • Learning Events: {learning_count}")

        return True

    except Exception as e:
        print(f"❌ Error in collection cycle: {e}")
        return False

def main():
    """Main overnight runner"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🌙 OVERNIGHT LEARNING RUNNER - AUTONOMOUS MODE 🌙          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("\nThis will run data collection every 15 minutes.")
    print("Press Ctrl+C to stop.\n")

    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 CYCLE #{cycle_count}")

            # Run collection
            success = run_collection_cycle()

            if success:
                print(f"\n✅ Cycle #{cycle_count} completed successfully!")
            else:
                print(f"\n⚠️  Cycle #{cycle_count} had some issues but continuing...")

            # Wait 15 minutes (900 seconds)
            print(f"\n💤 Waiting 15 minutes until next cycle...")
            print(f"   Next run at: {(datetime.now().timestamp() + 900)}")

            for i in range(15):
                time.sleep(60)  # Sleep 1 minute at a time
                remaining = 15 - i - 1
                if remaining > 0:
                    print(f"   {remaining} minutes remaining...")

    except KeyboardInterrupt:
        print("\n\n🛑 Overnight runner stopped by user.")
        print(f"Completed {cycle_count} cycles.")

        # Show final stats
        spider_count = SpiderData.objects.count()
        solution_count = AgentSolution.objects.count()
        learning_count = AgentLearning.objects.count()

        print(f"\n📊 Final Statistics:")
        print(f"  • Total Spider Data:     {spider_count}")
        print(f"  • Total Solutions:       {solution_count}")
        print(f"  • Total Learning Events: {learning_count}")

if __name__ == "__main__":
    main()