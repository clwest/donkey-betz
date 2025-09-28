#!/usr/bin/env python3
"""
Debug why the monitor isn't showing data
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.db import connection
from agents.models import UnifiedAgentTemplate, AgentExecution

print("=" * 60)
print("DEBUGGING MONITOR DATA ISSUES")
print("=" * 60)

# Step 1: Check UnifiedAgentTemplate fields
print("\n1. CHECKING AGENT MODEL FIELDS:")
print("-" * 40)
agent = UnifiedAgentTemplate.objects.first()
if agent:
    print(f"Sample agent: {agent.name}")
    print(f"Agent fields: {[f.name for f in agent._meta.fields]}")
    print(f"Looking for 'is_active' field...")
    
    # Check if is_active field exists
    has_is_active = hasattr(agent, 'is_active')
    print(f"Has 'is_active' field: {has_is_active}")
    
    if has_is_active:
        print(f"Agent is_active value: {agent.is_active}")
        active_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        print(f"Active agents count: {active_count}")
    else:
        print("⚠️  No 'is_active' field - this is why monitor shows 0!")
        print("All agents count:", UnifiedAgentTemplate.objects.count())

# Step 2: Check AgentExecution timestamps
print("\n2. CHECKING AGENT EXECUTIONS:")
print("-" * 40)
exec_count = AgentExecution.objects.count()
print(f"Total executions: {exec_count}")

if exec_count > 0:
    # Get first and last execution
    first_exec = AgentExecution.objects.order_by('created_at').first()
    last_exec = AgentExecution.objects.order_by('-created_at').first()
    
    print(f"First execution: {first_exec.created_at if first_exec else 'None'}")
    print(f"Last execution: {last_exec.created_at if last_exec else 'None'}")
    
    # Check recent executions
    recent_time = datetime.now() - timedelta(minutes=10)
    recent_execs = AgentExecution.objects.filter(created_at__gte=recent_time).count()
    print(f"Executions in last 10 minutes: {recent_execs}")
    
    # Check if timezone is issue
    from django.utils import timezone
    recent_time_tz = timezone.now() - timedelta(minutes=10)
    recent_execs_tz = AgentExecution.objects.filter(created_at__gte=recent_time_tz).count()
    print(f"Executions in last 10 min (with timezone): {recent_execs_tz}")

# Step 3: Check actual query being used
print("\n3. TESTING EXACT MONITOR QUERIES:")
print("-" * 40)

# Test the exact query from the monitor
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COALESCE(metadata->>'group', 'ungrouped') as group_name,
                COUNT(*) as agent_count
            FROM agents_unifiedagenttemplate
            WHERE is_active = true
            GROUP BY metadata->>'group'
        """)
        groups = cursor.fetchall()
        print(f"Agent groups query result: {groups}")
except Exception as e:
    print(f"Agent groups query failed: {e}")
    
    # Try without is_active filter
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(metadata->>'group', 'ungrouped') as group_name,
                    COUNT(*) as agent_count
                FROM agents_unifiedagenttemplate
                GROUP BY metadata->>'group'
            """)
            groups = cursor.fetchall()
            print(f"Agent groups (no filter) result: {groups}")
    except Exception as e2:
        print(f"Even simpler query failed: {e2}")

# Step 4: Check what fields are actually available
print("\n4. ACTUAL DATABASE SCHEMA:")
print("-" * 40)
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'agents_unifiedagenttemplate'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("UnifiedAgentTemplate columns:")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
