#!/usr/bin/env python
"""
Test the corrected cost calculations
"""

import sys
import os
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from api_unified_learning_dashboard import dashboard_api

def test_corrected_costs():
    print('💰 CORRECTED COST ANALYSIS:')
    print('=' * 50)

    cost_data = dashboard_api.get_cost_metrics()

    print(f'Total Cost: ${cost_data["totalCost"]:.3f}')
    print(f'Learning Cost: ${cost_data["learningCost"]:.3f}')
    print(f'Collaboration Cost: ${cost_data["collaborationCost"]:.3f}')
    print(f'Cost per Learning: ${cost_data["costPerLearning"]:.4f}')
    print()

    print('📉 Much more realistic! For 52 learnings:')
    old_cost = 4.05
    new_cost = cost_data["totalCost"]
    savings = old_cost - new_cost
    reduction_percent = (savings / old_cost) * 100

    print(f'   - Previous: ${old_cost:.2f} (${old_cost/52:.3f} per learning)')
    print(f'   - Current: ${new_cost:.3f} (${cost_data["costPerLearning"]:.4f} per learning)')
    print(f'   - Savings: ${savings:.2f} ({reduction_percent:.1f}% reduction)')

    print('\n📈 Updated Cost History:')
    for entry in cost_data['costHistory'][-4:]:  # Show last 4 entries
        print(f'   {entry["timestamp"]}: ${entry["cost"]:.3f}')

if __name__ == "__main__":
    test_corrected_costs()