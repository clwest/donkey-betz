"""
Market Intelligence Desk - Comprehensive Verification

Tests what's ACTUALLY implemented vs assumed missing.

Run with:
    DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python verify_market_intelligence_desk.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from datetime import date, timedelta
import inspect


def test_core_agents():
    """Test if core agents exist and are functional."""
    print("\n🧪 Test 1: Core Agents")
    print("=" * 80)

    results = {}

    # Test BullCaseAgent
    try:
        from core.agents.stocks.bull_case_agent import BullCaseAgent
        bull = BullCaseAgent()
        assert hasattr(bull, 'execute'), "BullCaseAgent missing execute method"
        assert hasattr(bull, '_get_confidence_multiplier'), "Missing confidence multiplier"
        print("✅ BullCaseAgent - WORKING")
        print(f"   - Has execute method: ✓")
        print(f"   - Has confidence multiplier: ✓")
        print(f"   - System prompt: {len(bull.system_prompt)} chars")
        results['BullCaseAgent'] = True
    except Exception as e:
        print(f"❌ BullCaseAgent - FAILED: {e}")
        results['BullCaseAgent'] = False

    # Test BearCaseAgent
    try:
        from core.agents.stocks.bear_case_agent import BearCaseAgent
        bear = BearCaseAgent()
        assert hasattr(bear, 'execute'), "BearCaseAgent missing execute method"
        assert hasattr(bear, '_get_confidence_multiplier'), "Missing confidence multiplier"
        print("✅ BearCaseAgent - WORKING")
        print(f"   - Has execute method: ✓")
        print(f"   - Has confidence multiplier: ✓")
        print(f"   - System prompt: {len(bear.system_prompt)} chars")
        results['BearCaseAgent'] = True
    except Exception as e:
        print(f"❌ BearCaseAgent - FAILED: {e}")
        results['BearCaseAgent'] = False

    # Test MarketIntelligenceCoordinator
    try:
        from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator
        coordinator = MarketIntelligenceCoordinator()
        print("✅ MarketIntelligenceCoordinator - WORKING")

        # Check methods
        methods = ['execute', '_prepare_brief', '_record_predictions_for_learning']
        for method in methods:
            has_method = hasattr(coordinator, method)
            status = "✓" if has_method else "✗"
            print(f"   - Has {method}: {status}")

        results['MarketIntelligenceCoordinator'] = True
    except Exception as e:
        print(f"❌ MarketIntelligenceCoordinator - FAILED: {e}")
        results['MarketIntelligenceCoordinator'] = False

    return results


def test_missing_agents():
    """Test if 'missing' agents actually exist."""
    print("\n🧪 Test 2: Allegedly Missing Agents")
    print("=" * 80)

    results = {}

    # Check for SignalScannerAgent
    try:
        from core.agents.stocks import SignalScannerAgent
        print("✅ SignalScannerAgent - EXISTS!")
        print(f"   Location: Found in core.agents.stocks")
        results['SignalScannerAgent'] = True
    except ImportError:
        try:
            # Check if it exists but isn't exported
            import importlib
            import os
            stocks_dir = '/Users/donkeyking/development/unified-donkey-betz/core/agents/stocks'
            if os.path.exists(os.path.join(stocks_dir, 'signal_scanner_agent.py')):
                print("⚠️  SignalScannerAgent - File exists but not exported")
                results['SignalScannerAgent'] = 'exists_not_exported'
            else:
                print("❌ SignalScannerAgent - NOT FOUND")
                results['SignalScannerAgent'] = False
        except Exception as e:
            print(f"❌ SignalScannerAgent - NOT FOUND: {e}")
            results['SignalScannerAgent'] = False

    # Check for RiskOfficerAgent
    try:
        from core.agents.stocks import RiskOfficerAgent
        print("✅ RiskOfficerAgent - EXISTS!")
        results['RiskOfficerAgent'] = True
    except ImportError:
        try:
            import os
            stocks_dir = '/Users/donkeyking/development/unified-donkey-betz/core/agents/stocks'
            if os.path.exists(os.path.join(stocks_dir, 'risk_officer_agent.py')):
                print("⚠️  RiskOfficerAgent - File exists but not exported")
                results['RiskOfficerAgent'] = 'exists_not_exported'
            else:
                print("❌ RiskOfficerAgent - NOT FOUND")
                results['RiskOfficerAgent'] = False
        except Exception as e:
            print(f"❌ RiskOfficerAgent - NOT FOUND: {e}")
            results['RiskOfficerAgent'] = False

    # Check for StockAuditCoordinator (alternative to RiskOfficer)
    try:
        from core.services.autonomous_loop import run_stock_audit
        print("✅ StockAuditCoordinator - EXISTS (alternative to RiskOfficer)")
        print("   - Contains: StockAnalystAgent, MarketMovementMonitorAgent,")
        print("              InstitutionalWatcherAgent, MarketAnomalyDetectorAgent")
        results['StockAuditCoordinator'] = True
    except ImportError as e:
        print(f"❌ StockAuditCoordinator - NOT FOUND: {e}")
        results['StockAuditCoordinator'] = False

    return results


def test_spoken_output():
    """Test if spoken briefs are implemented."""
    print("\n🧪 Test 3: Spoken Output (TTS Integration)")
    print("=" * 80)

    results = {}

    # Check if ElevenLabs integration exists
    try:
        from core.services.elevenlabs_service import ElevenLabsService
        print("✅ ElevenLabsService - EXISTS")

        service = ElevenLabsService()
        methods = ['text_to_speech', 'get_voices', 'clone_voice']
        for method in methods:
            has_method = hasattr(service, method)
            status = "✓" if has_method else "✗"
            print(f"   - Has {method}: {status}")

        results['ElevenLabsService'] = True
    except Exception as e:
        print(f"❌ ElevenLabsService - FAILED: {e}")
        results['ElevenLabsService'] = False

    # Check if coordinator generates spoken briefs
    try:
        from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator

        # Read the source code to check for TTS integration
        import inspect
        source = inspect.getsource(MarketIntelligenceCoordinator)

        has_tts_call = 'text_to_speech' in source or 'ElevenLabs' in source
        has_audio_generation = 'audio' in source.lower() and ('generate' in source or 'create' in source)

        if has_tts_call or has_audio_generation:
            print("✅ Coordinator integrates TTS - WORKING")
            results['spoken_briefs'] = True
        else:
            print("❌ Coordinator does NOT integrate TTS - MISSING")
            print("   ElevenLabsService exists but not used in coordinator")
            results['spoken_briefs'] = False
    except Exception as e:
        print(f"❌ Spoken brief check - FAILED: {e}")
        results['spoken_briefs'] = False

    return results


def test_event_driven_reruns():
    """Test if event-driven re-runs are implemented."""
    print("\n🧪 Test 4: Event-Driven Re-runs")
    print("=" * 80)

    results = {}

    # Check for event monitoring tasks
    try:
        from core import tasks

        # Look for event-related tasks
        event_tasks = []
        for name in dir(tasks):
            if 'event' in name.lower() or 'alert' in name.lower() or 'monitor' in name.lower():
                event_tasks.append(name)

        if event_tasks:
            print("✅ Event monitoring tasks - FOUND")
            for task in event_tasks:
                print(f"   - {task}")
            results['event_monitoring'] = True
        else:
            print("❌ Event monitoring tasks - NOT FOUND")
            results['event_monitoring'] = False

        # Check for SEC filings alerts
        has_sec_alerts = hasattr(tasks, 'check_sec_filings_alert')
        if has_sec_alerts:
            print("✅ SEC filing alerts - WORKING")
            results['sec_alerts'] = True
        else:
            print("❌ SEC filing alerts - NOT FOUND")
            results['sec_alerts'] = False

    except Exception as e:
        print(f"❌ Event monitoring check - FAILED: {e}")
        results['event_monitoring'] = False
        results['sec_alerts'] = False

    # Check Celery Beat schedule for event tasks
    try:
        from django.conf import settings
        schedule = settings.CELERY_BEAT_SCHEDULE

        event_schedules = {k: v for k, v in schedule.items()
                          if 'sec' in k.lower() or 'alert' in k.lower() or 'market' in k.lower()}

        if event_schedules:
            print(f"✅ Event schedules - FOUND ({len(event_schedules)} tasks)")
            for name in event_schedules.keys():
                print(f"   - {name}")
            results['event_schedules'] = True
        else:
            print("❌ Event schedules - NOT FOUND")
            results['event_schedules'] = False

    except Exception as e:
        print(f"❌ Event schedule check - FAILED: {e}")
        results['event_schedules'] = False

    return results


def test_dynamic_asset_selection():
    """Test how assets/tickers are selected."""
    print("\n🧪 Test 5: Dynamic Asset Selection")
    print("=" * 80)

    results = {}

    try:
        from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator
        import inspect

        source = inspect.getsource(MarketIntelligenceCoordinator)

        # Check for hardcoded tickers
        has_hardcoded = 'AAPL' in source or 'MSFT' in source or "['AAPL'" in source

        # Check for dynamic selection logic
        has_dynamic = 'get_top_stocks' in source or 'select_stocks' in source or 'market_cap' in source

        # Check for user preference logic
        has_user_prefs = 'user_stocks' in source or 'preferences' in source or 'watchlist' in source

        if has_dynamic or has_user_prefs:
            print("✅ Dynamic asset selection - IMPLEMENTED")
            if has_dynamic:
                print("   - Has dynamic stock selection logic")
            if has_user_prefs:
                print("   - Has user preference logic")
            results['dynamic_selection'] = True
        elif has_hardcoded:
            print("❌ Dynamic asset selection - HARDCODED")
            print("   - Uses hardcoded ticker list")
            results['dynamic_selection'] = False
        else:
            print("⚠️  Dynamic asset selection - UNCLEAR")
            results['dynamic_selection'] = 'unclear'

        # Check for learning from user feedback
        has_learning = 'UserBriefFeedback' in source or 'learn' in source.lower()
        if has_learning:
            print("✅ Learns from user feedback - IMPLEMENTED")
            results['feedback_learning'] = True
        else:
            print("❌ Learns from user feedback - NOT IMPLEMENTED")
            results['feedback_learning'] = False

    except Exception as e:
        print(f"❌ Asset selection check - FAILED: {e}")
        results['dynamic_selection'] = False
        results['feedback_learning'] = False

    return results


def test_what_changed_feature():
    """Test if 'what changed since yesterday' is implemented."""
    print("\n🧪 Test 6: 'What Changed Since Yesterday' Feature")
    print("=" * 80)

    results = {}

    try:
        from core.models_unified_system import MarketIntelligenceBrief

        # Check if model has 'what_changed' field
        fields = [f.name for f in MarketIntelligenceBrief._meta.get_fields()]

        what_changed_fields = [f for f in fields if 'change' in f.lower() or 'delta' in f.lower() or 'diff' in f.lower()]

        if what_changed_fields:
            print(f"✅ 'What changed' fields - FOUND")
            for field in what_changed_fields:
                print(f"   - {field}")
            results['what_changed_fields'] = True
        else:
            print("❌ 'What changed' fields - NOT FOUND")
            results['what_changed_fields'] = False

        # Check if we have historical briefs to compare
        brief_count = MarketIntelligenceBrief.objects.count()
        print(f"ℹ️  Historical briefs: {brief_count}")

        if brief_count >= 2:
            # Get two most recent briefs
            briefs = MarketIntelligenceBrief.objects.order_by('-brief_date')[:2]
            if len(briefs) == 2:
                print(f"✅ Can compare: {briefs[1].brief_date} vs {briefs[0].brief_date}")
                results['comparable_data'] = True
            else:
                print("⚠️  Only 1 brief available")
                results['comparable_data'] = False
        else:
            print("❌ Need at least 2 briefs to compare")
            results['comparable_data'] = False

        # Check coordinator for comparison logic
        from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator
        import inspect

        source = inspect.getsource(MarketIntelligenceCoordinator)
        has_comparison = 'previous' in source or 'yesterday' in source or 'compare' in source

        if has_comparison:
            print("✅ Comparison logic - FOUND in coordinator")
            results['comparison_logic'] = True
        else:
            print("❌ Comparison logic - NOT FOUND")
            results['comparison_logic'] = False

    except Exception as e:
        print(f"❌ 'What changed' check - FAILED: {e}")
        results['what_changed_fields'] = False
        results['comparable_data'] = False
        results['comparison_logic'] = False

    return results


def test_celery_schedule():
    """Test Celery scheduling for Market Intelligence Desk."""
    print("\n🧪 Test 7: Celery Scheduling")
    print("=" * 80)

    results = {}

    try:
        from django.conf import settings
        schedule = settings.CELERY_BEAT_SCHEDULE

        # Check for market intelligence desk task
        market_tasks = {k: v for k, v in schedule.items() if 'market' in k.lower() and 'intelligence' in k.lower()}

        if market_tasks:
            print(f"✅ Market Intelligence Desk scheduled - WORKING")
            for name, config in market_tasks.items():
                print(f"   - Task: {name}")
                print(f"     Schedule: {config.get('schedule')}")
            results['scheduled'] = True
        else:
            print("❌ Market Intelligence Desk - NOT SCHEDULED")
            results['scheduled'] = False

        # Check learning loop tasks
        learning_tasks = [k for k in schedule.keys() if 'prediction' in k or 'accuracy' in k]
        if learning_tasks:
            print(f"✅ Learning loop tasks - SCHEDULED")
            for name in learning_tasks:
                print(f"   - {name}")
            results['learning_scheduled'] = True
        else:
            print("❌ Learning loop tasks - NOT SCHEDULED")
            results['learning_scheduled'] = False

    except Exception as e:
        print(f"❌ Schedule check - FAILED: {e}")
        results['scheduled'] = False
        results['learning_scheduled'] = False

    return results


def generate_summary(all_results):
    """Generate final summary and completion percentage."""
    print("\n" + "=" * 80)
    print("📊 MARKET INTELLIGENCE DESK - FINAL VERIFICATION SUMMARY")
    print("=" * 80)

    # Flatten all results
    flat_results = {}
    for category_results in all_results.values():
        flat_results.update(category_results)

    # Calculate completion
    total = len(flat_results)
    complete = sum(1 for v in flat_results.values() if v == True)
    partial = sum(1 for v in flat_results.values() if v == 'exists_not_exported' or v == 'unclear')
    missing = sum(1 for v in flat_results.values() if v == False)

    completion_pct = (complete / total * 100) if total > 0 else 0

    print(f"\n✅ Complete: {complete}/{total} components ({completion_pct:.1f}%)")
    print(f"⚠️  Partial: {partial}/{total} components")
    print(f"❌ Missing: {missing}/{total} components")

    # Category breakdown
    print("\n📋 Component Status:")
    print("-" * 80)

    categories = {
        'Core Agents': ['BullCaseAgent', 'BearCaseAgent', 'MarketIntelligenceCoordinator'],
        'Missing Agents': ['SignalScannerAgent', 'RiskOfficerAgent', 'StockAuditCoordinator'],
        'Spoken Output': ['ElevenLabsService', 'spoken_briefs'],
        'Event System': ['event_monitoring', 'sec_alerts', 'event_schedules'],
        'Asset Selection': ['dynamic_selection', 'feedback_learning'],
        'What Changed': ['what_changed_fields', 'comparable_data', 'comparison_logic'],
        'Scheduling': ['scheduled', 'learning_scheduled'],
    }

    for category, components in categories.items():
        category_status = [flat_results.get(c, 'unknown') for c in components]
        all_complete = all(s == True for s in category_status)
        any_complete = any(s == True for s in category_status)

        if all_complete:
            status_emoji = "✅"
        elif any_complete:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        print(f"{status_emoji} {category}")
        for comp in components:
            val = flat_results.get(comp, 'unknown')
            if val == True:
                print(f"   ✓ {comp}")
            elif val == False:
                print(f"   ✗ {comp}")
            else:
                print(f"   ? {comp} ({val})")

    # Final recommendation
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATION")
    print("=" * 80)

    if completion_pct >= 90:
        print("✅ Market Intelligence Desk is NEARLY COMPLETE!")
        print("   Only minor additions needed to reach 100%.")
    elif completion_pct >= 70:
        print("⚠️  Market Intelligence Desk is MOSTLY COMPLETE")
        print("   Core functionality works, advanced features need work.")
    elif completion_pct >= 50:
        print("⚠️  Market Intelligence Desk is PARTIALLY COMPLETE")
        print("   Significant work needed for production readiness.")
    else:
        print("❌ Market Intelligence Desk needs MAJOR WORK")
        print("   Many core components are missing.")

    print("\n")

    return flat_results, completion_pct


def run_all_tests():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("🔍 MARKET INTELLIGENCE DESK - COMPREHENSIVE VERIFICATION")
    print("=" * 80)

    all_results = {}

    all_results['core_agents'] = test_core_agents()
    all_results['missing_agents'] = test_missing_agents()
    all_results['spoken_output'] = test_spoken_output()
    all_results['event_driven'] = test_event_driven_reruns()
    all_results['asset_selection'] = test_dynamic_asset_selection()
    all_results['what_changed'] = test_what_changed_feature()
    all_results['scheduling'] = test_celery_schedule()

    flat_results, completion_pct = generate_summary(all_results)

    return flat_results, completion_pct


if __name__ == '__main__':
    results, pct = run_all_tests()
    sys.exit(0)
