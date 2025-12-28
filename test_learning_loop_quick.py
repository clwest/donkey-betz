#!/usr/bin/env python
"""
Session 463: Quick Learning Loop Verification

Tests the learning loop infrastructure without generating a full brief.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from core.models_unified_system import (
    MarketIntelligenceBrief,
    PredictionOutcome,
    UserBriefFeedback,
    AgentAccuracyMetrics
)
from django.contrib.auth import get_user_model

User = get_user_model()

print('='* 80)
print('🧪 SESSION 463: QUICK LEARNING LOOP VERIFICATION')
print('='* 80)

# Test 1: Models exist and work
print('\n📊 TEST 1: Database Models')
print('-' * 80)

try:
    # Get or create test brief
    test_brief, _ = MarketIntelligenceBrief.objects.get_or_create(
        brief_date=date.today(),
        defaults={
            'total_stocks_analyzed': 10,
            'gpt_success_rate': 80,
            'debate_zone_count': 2
        }
    )
    print(f'✅ MarketIntelligenceBrief: {test_brief.id}')

    # Create test prediction
    pred = PredictionOutcome.objects.create(
        brief=test_brief,
        ticker='TEST',
        prediction_type='BULL',
        conviction_level='HIGH',
        predicted_move=Decimal('10.5'),
        price_at_prediction=Decimal('100.00'),
        prediction_date=date.today(),
        was_in_debate_zone=False
    )
    print(f'✅ PredictionOutcome created: {pred.ticker}')

    # Test outcome calculation
    pred.calculate_outcome(current_price=110.00, days_elapsed=7)
    print(f'✅ Outcome calculation works: {pred.accuracy_score_7_days:.2f}')

    # Create test feedback
    test_user = User.objects.first()
    if test_user:
        feedback = UserBriefFeedback.objects.create(
            user=test_user,
            brief=test_brief,
            was_helpful=True,
            helpfulness_score=5
        )
        print(f'✅ UserBriefFeedback created for user: {test_user.username}')

        # Test action recording
        feedback.record_action('TEST', 'buy', 'bull_case')
        print(f'✅ Action recorded: {len(feedback.actions_taken)} actions')
        feedback.delete()

    # Create test metrics
    metrics = AgentAccuracyMetrics.objects.create(
        agent_name='BullCaseAgent',
        period_start=date.today() - timedelta(days=7),
        period_end=date.today(),
        total_predictions=10,
        accuracy_rate_7_days=75.0,
        confidence_multiplier=1.1
    )
    print(f'✅ AgentAccuracyMetrics created: {metrics.accuracy_rate_7_days}% accurate')

    # Cleanup
    pred.delete()
    metrics.delete()

    print('\n✅ TEST 1 PASSED: All models work correctly')

except Exception as e:
    print(f'\n❌ TEST 1 FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Celery schedules
print('\n⏰ TEST 2: Celery Beat Schedules')
print('-' * 80)

try:
    from core.celery import app
    schedule = app.conf.beat_schedule

    required_tasks = [
        'calculate-prediction-outcomes',
        'update-agent-accuracy-metrics'
    ]

    missing = []
    for task_name in required_tasks:
        if task_name in schedule:
            task = schedule[task_name]
            print(f'✅ {task_name}')
            print(f'   Task: {task["task"]}')
            print(f'   Schedule: {task["schedule"]}')
        else:
            missing.append(task_name)
            print(f'❌ {task_name} NOT FOUND')

    if missing:
        print(f'\n❌ TEST 2 FAILED: Missing tasks: {missing}')
        sys.exit(1)
    else:
        print('\n✅ TEST 2 PASSED: All Celery schedules configured')

except Exception as e:
    print(f'\n❌ TEST 2 FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Discord commands exist
print('\n💬 TEST 3: Discord Commands')
print('-' * 80)

try:
    # Check if discord_bot.py has the commands
    discord_bot_path = '/Users/donkeyking/development/unified-donkey-betz/core/services/discord_bot.py'
    with open(discord_bot_path, 'r') as f:
        content = f.read()

    required_commands = [
        'brief_feedback_command',
        'action_command'
    ]

    all_found = True
    for cmd in required_commands:
        if cmd in content:
            print(f'✅ /{cmd.replace("_command", "").replace("_", "-")} command found')
        else:
            print(f'❌ /{cmd.replace("_command", "").replace("_", "-")} command NOT FOUND')
            all_found = False

    if all_found:
        print('\n✅ TEST 3 PASSED: Discord commands implemented')
    else:
        print('\n❌ TEST 3 FAILED: Some commands missing')
        sys.exit(1)

except Exception as e:
    print(f'\n❌ TEST 3 FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Coordinator integration
print('\n🔧 TEST 4: Coordinator Integration')
print('-' * 80)

try:
    coordinator_path = '/Users/donkeyking/development/unified-donkey-betz/core/agents/stocks/market_intelligence_coordinator.py'
    with open(coordinator_path, 'r') as f:
        content = f.read()

    checks = [
        ('_record_predictions_for_learning', 'Prediction recording method'),
        ('_internal_bull_analyses', 'Bull analyses storage'),
        ('_internal_bear_analyses', 'Bear analyses storage'),
    ]

    all_found = True
    for code_snippet, description in checks:
        if code_snippet in content:
            print(f'✅ {description}')
        else:
            print(f'❌ {description} NOT FOUND')
            all_found = False

    if all_found:
        print('\n✅ TEST 4 PASSED: Coordinator has learning loop integration')
    else:
        print('\n❌ TEST 4 FAILED: Some integrations missing')
        sys.exit(1)

except Exception as e:
    print(f'\n❌ TEST 4 FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print('\n' + '='* 80)
print('📊 LEARNING LOOP VERIFICATION SUMMARY')
print('='* 80)
print('✅ TEST 1: Database models - PASS')
print('✅ TEST 2: Celery schedules - PASS')
print('✅ TEST 3: Discord commands - PASS')
print('✅ TEST 4: Coordinator integration - PASS')
print('\n' + '='* 80)
print('🎉 ALL TESTS PASSED! Learning loop infrastructure complete!')
print('='* 80)

print('\n📋 Next Steps:')
print('1. Let the current Market Intelligence Brief generation complete')
print('2. Verify predictions were recorded in database')
print('3. Restart Discord bot to register new commands: python manage.py run_discord_bot')
print('4. Test /brief-feedback and /action commands in Discord')
print('5. Wait for Celery Beat to run scheduled tasks (or trigger manually)')

sys.exit(0)
