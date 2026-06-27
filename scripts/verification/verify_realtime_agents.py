# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Verify that agents are using real-time data in their analysis
"""

import os
import django
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.models.agents_registry import AgentTaskExecution
from django.utils import timezone

# Check recent executions
recent = AgentTaskExecution.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
).order_by('-created_at')

print(f"\n{'='*70}")
print("🔍 AGENT EXECUTION VERIFICATION - Real-Time Data Usage")
print(f"{'='*70}\n")

# Categorize executions
using_realtime = []
generic_analysis = []
no_output = []

for ex in recent:
    if ex.result and 'output' in ex.result and ex.result['output']:
        output = ex.result['output'].lower()
        
        # Check for specific odds mentions
        has_specific_odds = any([
            '-110' in output,
            '+475' in output,
            '-650' in output,
            '16.5' in output,
            '54.5' in output,
            'spread: alabama' in output,
            'moneyline' in output and ('475' in output or '650' in output)
        ])
        
        # Check for generic phrases indicating no real data
        has_generic = any([
            'need more data' in output,
            'no specific odds' in output,
            'cannot provide' in output,
            'without the actual' in output,
            'need the current' in output
        ])
        
        if has_specific_odds and not has_generic:
            using_realtime.append(ex)
        else:
            generic_analysis.append(ex)
    else:
        no_output.append(ex)

# Display results
print(f"📊 Total Executions Analyzed: {recent.count()}")
print(f"✅ Using Real-Time Data: {len(using_realtime)}")
print(f"⚠️ Generic Analysis: {len(generic_analysis)}")
print(f"❌ No Output: {len(no_output)}")

if using_realtime:
    print(f"\n✅ AGENTS USING REAL-TIME DATA ({len(using_realtime)}):")
    print("-" * 40)
    for ex in using_realtime[:10]:
        agent_name = ex.template.name if ex.template else 'Unknown'
        print(f"• {agent_name}")
        if ex.result and 'output' in ex.result:
            # Find specific odds mentions
            output = ex.result['output']
            sample = ""
            if "Alabama -16.5" in output:
                idx = output.find("Alabama -16.5")
                sample = output[idx:idx+50]
            elif "-650" in output:
                idx = output.find("-650")
                sample = output[idx-20:idx+30]
            elif "+475" in output:
                idx = output.find("+475")
                sample = output[idx-20:idx+30]
            
            if sample:
                print(f"  Evidence: ...{sample}...")

if generic_analysis:
    print(f"\n⚠️ AGENTS WITH GENERIC ANALYSIS ({len(generic_analysis)}):")
    print("-" * 40)
    for ex in generic_analysis[:5]:
        agent_name = ex.template.name if ex.template else 'Unknown'
        print(f"• {agent_name}")
        if ex.execution_id.startswith('realtime_'):
            print(f"  ⚠️ This was supposed to have real-time data!")

# Check input data
print(f"\n📥 INPUT DATA VERIFICATION:")
print("-" * 40)
sample_recent = recent[:3]
for ex in sample_recent:
    agent_name = ex.template.name if ex.template else 'Unknown'
    print(f"\n• {agent_name}:")
    if ex.input_data and 'markets' in ex.input_data:
        markets = ex.input_data['markets']
        if markets:
            print(f"  ✓ Has market data: {list(markets.keys())}")
            if 'spread' in markets:
                spread = markets['spread']
                if isinstance(spread, dict):
                    print(f"    Spread: {spread.get('home_spread', 'N/A')}")
        else:
            print(f"  ✗ Markets field is empty!")
    else:
        print(f"  ✗ No market data in input!")

print(f"\n{'='*70}")
print("📌 RECOMMENDATION:")
if len(using_realtime) > len(generic_analysis):
    print("✅ Most agents are successfully using real-time data!")
    print("   The Agent Analysis Reports should show specific betting recommendations.")
else:
    print("⚠️ Many agents still showing generic analysis.")
    print("   Run: python run_agents_with_realtime.py")
    print("   This will replace mock data with real-time odds.")
print(f"{'='*70}\n")