#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Now import Django models
from agents.models import UnifiedAgentTemplate

def check_agents():
    total = UnifiedAgentTemplate.objects.count()
    active = UnifiedAgentTemplate.objects.filter(is_active=True).count()

    print(f"Total agents in database: {total}")
    print(f"Active agents: {active}")
    print(f"Inactive agents: {total - active}")

    print("\nFirst 10 agents:")
    for i, agent in enumerate(UnifiedAgentTemplate.objects.all()[:10], 1):
        print(f"  {i}. {agent.name} ({agent.specialization}) - {'Active' if agent.is_active else 'Inactive'}")

    print("\nSpecializations:")
    from django.db.models import Count
    specializations = UnifiedAgentTemplate.objects.values('specialization').annotate(count=Count('id')).order_by('-count')
    for spec in specializations:
        print(f"  - {spec['specialization']}: {spec['count']} agents")

if __name__ == "__main__":
    check_agents()