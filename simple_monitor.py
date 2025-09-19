#!/usr/bin/env python3
"""
ULTRA SIMPLE MONITOR - This one WILL work
"""
import os
import time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from django.db import connection

while True:
    os.system('clear')  # Clear screen
    
    print("=" * 60)
    print("UNIFIED DONKEY BETZ - SIMPLE MONITOR")
    print("=" * 60)
    
    # Direct queries - no fancy stuff
    agents_count = UnifiedAgentTemplate.objects.count()
    active_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
    executions = AgentExecution.objects.count()
    
    print(f"\n🤖 AGENTS:")
    print(f"  Total: {agents_count}")
    print(f"  Active: {active_agents}")
    
    print(f"\n⚡ EXECUTIONS:")
    print(f"  Total: {executions}")
    
    # Get database size
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_database_size(current_database()) / 1024 / 1024")
        db_size = cursor.fetchone()[0]
    
    print(f"\n💾 DATABASE:")
    print(f"  Size: {db_size:.2f} MB")
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to exit | Updates every 2 seconds")
    
    time.sleep(2)
