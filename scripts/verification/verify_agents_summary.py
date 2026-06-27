# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Summary of agent executions with real-time data
"""

import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.models.agents_registry import AgentTaskExecution
from django.utils import timezone

print(f"\n{'='*80}")
print(f"🎯 AGENT EXECUTION SUMMARY - Real-Time Data Verification")
print(f"{'='*80}\n")

# Get recent executions for Alabama game
recent = AgentTaskExecution.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=2),
    input_data__home_team='Alabama Crimson Tide'
).order_by('-completed_at')

# Categorize
using_realtime = []
generic = []
pending = []
failed = []

for ex in recent:
    if ex.status == 'pending':
        pending.append(ex)
    elif ex.status == 'failed':
        failed.append(ex)
    elif ex.status == 'completed' and ex.result and 'output' in ex.result:
        output = ex.result['output']
        # Check for real odds
        if any(x in output for x in ['-16.5', '+475', '-650', '54.5']):
            using_realtime.append(ex)
        else:
            generic.append(ex)

print(f"📊 EXECUTION STATUS")
print(f"-" * 40)
print(f"✅ Using Real-Time Data: {len(using_realtime)}")
print(f"⚠️ Generic Analysis: {len(generic)}")
print(f"⏳ Pending: {len(pending)}")
print(f"❌ Failed: {len(failed)}")
print(f"📈 Total: {recent.count()}")

if using_realtime:
    print(f"\n✅ AGENTS WITH REAL-TIME ANALYSIS ({len(using_realtime)})")
    print(f"-" * 40)
    
    for ex in using_realtime[:10]:
        agent_name = ex.template.name if ex.template else 'Unknown'
        print(f"\n• {agent_name}")
        
        # Show specific betting recommendations
        output = ex.result['output']
        lines = output.split('\n')
        
        # Find recommendation lines
        for line in lines:
            lower_line = line.lower()
            if any(word in lower_line for word in ['recommend', 'bet:', 'kelly:', 'value:', 'ev:', 'edge:']):
                print(f"  → {line.strip()[:100]}")
                break
        
        # Show odds references
        for line in lines[:20]:
            if 'Alabama -16.5' in line or '-650' in line or '+475' in line:
                print(f"  📊 {line.strip()[:100]}")
                break

print(f"\n{'='*80}")
print(f"💡 KEY INSIGHTS")
print(f"{'='*80}")

if using_realtime:
    # Sample a successful execution for key data
    sample = using_realtime[0]
    if sample.input_data and 'markets' in sample.input_data:
        markets = sample.input_data['markets']
        print(f"\n📌 Real-Time Odds Being Used:")
        print(f"  • Spread: Alabama {markets['spread']['home_spread']} ({markets['spread']['home_odds']})")
        print(f"  • Total: {markets['total']['line']} O/U ({markets['total']['over_odds']}/{markets['total']['under_odds']})")
        print(f"  • ML: Alabama {markets['moneyline']['home_odds']}, Wisconsin +{markets['moneyline']['away_odds']}")

print(f"\n✨ RECOMMENDATION:")
if len(using_realtime) >= 5:
    print(f"✅ SUCCESS! {len(using_realtime)} agents are providing real-time betting analysis.")
    print(f"   Check the betting page for Wisconsin @ Alabama to see specific recommendations!")
elif pending:
    print(f"⏳ {len(pending)} executions are pending. Run: python execute_pending_agents.py")
else:
    print(f"⚠️ Need to run more agents with real data. Use: python run_agents_with_realtime.py")

print(f"\n{'='*80}\n")