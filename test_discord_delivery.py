#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.agents.stocks.market_intelligence_coordinator import run_market_intelligence_desk

print('🧪 Testing Market Intelligence Desk with Discord delivery...')
print('=' * 80)

result = run_market_intelligence_desk()

print('\n' + '=' * 80)
print('🎯 TEST RESULTS:')
print('=' * 80)

if result.get('success'):
    brief = result.get('data', {}).get('brief', {})
    delivery = result.get('data', {}).get('delivery_status', {})
    
    print(f"✅ Brief generated: {brief.get('total_stocks_analyzed', 0)} stocks analyzed")
    print(f"📊 GPT success rate: {brief.get('gpt_success_rate', 0)}%")
    print(f"⚔️ Debate zone: {brief.get('debate_zone_count', 0)} stocks")
    print(f"📈 Bullish opportunities: {len(brief.get('bullish_opportunities', []))}")
    print(f"📉 Bearish warnings: {len(brief.get('bearish_warnings', []))}")
    
    print('\n' + '-' * 80)
    print('📢 DISCORD DELIVERY:')
    print('-' * 80)
    if delivery.get('discord_sent'):
        print('✅ Discord notification sent successfully to #stock-agents!')
        print(f"   Channel ID: 1450589539562426418")
    else:
        print('❌ Discord notification FAILED')
        if delivery.get('discord_error'):
            print(f"   Error: {delivery['discord_error']}")
else:
    print(f"❌ Test failed: {result}")
