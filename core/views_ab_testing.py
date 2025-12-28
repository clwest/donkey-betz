"""
Session 235: A/B Testing Framework API Views
Phase 6 - Proactive System (Creative Intelligence Empire)

Provides complete CRUD operations for A/B tests, variants, events, and goals.
"""

import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models_unified_system import ABTest, ABTestVariant, ABTestEvent, UserGoal
from .api_helpers import api_success, api_error


# ==============================================================================
# A/B Test Dashboard
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def ab_testing_dashboard(request):
    """Get A/B testing dashboard with overview statistics."""
    try:
        user = request.user if request.user.is_authenticated else None

        # Get test counts by status
        tests = ABTest.objects.filter(user=user) if user else ABTest.objects.all()

        status_counts = {
            'draft': tests.filter(status='draft').count(),
            'running': tests.filter(status='running').count(),
            'paused': tests.filter(status='paused').count(),
            'completed': tests.filter(status='completed').count(),
        }

        # Get recent tests
        recent_tests = tests.order_by('-created_at')[:5]
        recent_data = []
        for test in recent_tests:
            recent_data.append({
                'id': str(test.id),
                'name': test.name,
                'test_type': test.test_type,
                'status': test.status,
                'created_at': test.created_at.isoformat(),
                'variant_count': test.variants.count(),
            })

        # Get running tests with progress
        running_tests = tests.filter(status='running')
        running_data = []
        for test in running_tests:
            results = test.get_results()
            running_data.append({
                'id': str(test.id),
                'name': test.name,
                'test_type': test.test_type,
                'started': test.start_date.isoformat() if test.start_date else None,
                'variants': results['variants'],
                'has_winner': results['winner'] is not None,
            })

        # Get goals summary
        goals = UserGoal.objects.filter(user=user, is_active=True) if user else UserGoal.objects.filter(is_active=True)
        active_goals = goals.count()
        achieved_goals = goals.filter(is_achieved=True).count()

        return api_success({
            'status_counts': status_counts,
            'total_tests': sum(status_counts.values()),
            'recent_tests': recent_data,
            'running_tests': running_data,
            'goals': {
                'active': active_goals,
                'achieved': achieved_goals,
            }
        })

    except Exception as e:
        return api_error(str(e), status=500)


# ==============================================================================
# A/B Test CRUD
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_tests(request):
    """List all A/B tests."""
    try:
        user = request.user if request.user.is_authenticated else None
        status_filter = request.GET.get('status')
        test_type_filter = request.GET.get('test_type')

        tests = ABTest.objects.filter(user=user) if user else ABTest.objects.all()

        if status_filter:
            tests = tests.filter(status=status_filter)
        if test_type_filter:
            tests = tests.filter(test_type=test_type_filter)

        tests = tests.order_by('-created_at')[:50]

        tests_data = []
        for test in tests:
            tests_data.append({
                'id': str(test.id),
                'name': test.name,
                'description': test.description,
                'test_type': test.test_type,
                'status': test.status,
                'hypothesis': test.hypothesis,
                'primary_metric': test.primary_metric,
                'created_at': test.created_at.isoformat(),
                'start_date': test.start_date.isoformat() if test.start_date else None,
                'variant_count': test.variants.count(),
            })

        return api_success({'tests': tests_data})

    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_test(request):
    """Create a new A/B test."""
    try:
        data = json.loads(request.body) if request.body else {}

        required_fields = ['name', 'test_type']
        for field in required_fields:
            if not data.get(field):
                return api_error(f"Missing required field: {field}")

        user = request.user if request.user.is_authenticated else None

        test = ABTest.objects.create(
            user=user,
            name=data['name'],
            description=data.get('description', ''),
            test_type=data['test_type'],
            hypothesis=data.get('hypothesis', ''),
            primary_metric=data.get('primary_metric', 'conversion_rate'),
            secondary_metrics=data.get('secondary_metrics', []),
            confidence_level=data.get('confidence_level', 0.95),
            minimum_sample_size=data.get('minimum_sample_size', 100),
            content_filter=data.get('content_filter', {}),
            platform_filter=data.get('platform_filter', []),
            max_duration_days=data.get('max_duration_days', 30),
        )

        # Create variants if provided
        variants = data.get('variants', [])
        if not variants:
            # Create default control and test variants
            ABTestVariant.objects.create(
                test=test,
                name='Control',
                is_control=True,
                traffic_percentage=50,
            )
            ABTestVariant.objects.create(
                test=test,
                name='Variant A',
                is_control=False,
                traffic_percentage=50,
            )
        else:
            for idx, variant_data in enumerate(variants):
                ABTestVariant.objects.create(
                    test=test,
                    name=variant_data.get('name', f'Variant {idx}'),
                    description=variant_data.get('description', ''),
                    is_control=variant_data.get('is_control', idx == 0),
                    config=variant_data.get('config', {}),
                    traffic_percentage=variant_data.get('traffic_percentage', 50),
                )

        return api_success({
            'test': {
                'id': str(test.id),
                'name': test.name,
                'test_type': test.test_type,
                'status': test.status,
                'variant_count': test.variants.count(),
            }
        }, message='A/B test created successfully')

    except json.JSONDecodeError:
        return api_error("Invalid JSON data")
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def test_detail(request, test_id):
    """Get, update, or delete a specific A/B test."""
    try:
        test = ABTest.objects.get(id=test_id)

        if request.method == "GET":
            variants_data = []
            for variant in test.variants.all():
                stats = variant.get_statistics()
                variants_data.append({
                    'id': str(variant.id),
                    'name': variant.name,
                    'description': variant.description,
                    'is_control': variant.is_control,
                    'config': variant.config,
                    'traffic_percentage': variant.traffic_percentage,
                    'statistics': stats,
                })

            return api_success({
                'test': {
                    'id': str(test.id),
                    'name': test.name,
                    'description': test.description,
                    'test_type': test.test_type,
                    'status': test.status,
                    'hypothesis': test.hypothesis,
                    'primary_metric': test.primary_metric,
                    'secondary_metrics': test.secondary_metrics,
                    'confidence_level': test.confidence_level,
                    'minimum_sample_size': test.minimum_sample_size,
                    'content_filter': test.content_filter,
                    'platform_filter': test.platform_filter,
                    'max_duration_days': test.max_duration_days,
                    'start_date': test.start_date.isoformat() if test.start_date else None,
                    'end_date': test.end_date.isoformat() if test.end_date else None,
                    'created_at': test.created_at.isoformat(),
                    'winner_variant_id': str(test.winner_variant_id) if test.winner_variant_id else None,
                    'conclusion': test.conclusion,
                    'variants': variants_data,
                }
            })

        elif request.method == "PUT":
            data = json.loads(request.body) if request.body else {}

            if 'name' in data:
                test.name = data['name']
            if 'description' in data:
                test.description = data['description']
            if 'hypothesis' in data:
                test.hypothesis = data['hypothesis']
            if 'primary_metric' in data:
                test.primary_metric = data['primary_metric']
            if 'confidence_level' in data:
                test.confidence_level = data['confidence_level']
            if 'minimum_sample_size' in data:
                test.minimum_sample_size = data['minimum_sample_size']

            test.save()

            return api_success({
                'test': {
                    'id': str(test.id),
                    'name': test.name,
                    'status': test.status,
                }
            }, message='Test updated successfully')

        elif request.method == "DELETE":
            test_name = test.name
            test.delete()
            return api_success(message=f'Test "{test_name}" deleted successfully')

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def start_test(request, test_id):
    """Start an A/B test."""
    try:
        test = ABTest.objects.get(id=test_id)

        if test.variants.count() < 2:
            return api_error("Test must have at least 2 variants")

        if test.start_test():
            return api_success({
                'test': {
                    'id': str(test.id),
                    'status': test.status,
                    'start_date': test.start_date.isoformat(),
                }
            }, message='Test started successfully')
        else:
            return api_error(f"Cannot start test in {test.status} status")

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def pause_test(request, test_id):
    """Pause a running A/B test."""
    try:
        test = ABTest.objects.get(id=test_id)

        if test.pause_test():
            return api_success({
                'test': {
                    'id': str(test.id),
                    'status': test.status,
                }
            }, message='Test paused successfully')
        else:
            return api_error(f"Cannot pause test in {test.status} status")

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complete_test(request, test_id):
    """Complete an A/B test with results."""
    try:
        test = ABTest.objects.get(id=test_id)
        data = json.loads(request.body) if request.body else {}

        winner_id = data.get('winner_variant_id')
        conclusion = data.get('conclusion', '')

        if test.complete_test(winner_id=winner_id, conclusion=conclusion):
            return api_success({
                'test': {
                    'id': str(test.id),
                    'status': test.status,
                    'winner_variant_id': str(test.winner_variant_id) if test.winner_variant_id else None,
                    'conclusion': test.conclusion,
                }
            }, message='Test completed successfully')
        else:
            return api_error("Failed to complete test")

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["GET"])
def test_results(request, test_id):
    """Get detailed results for an A/B test."""
    try:
        test = ABTest.objects.get(id=test_id)
        results = test.get_results()

        # Add additional analysis
        results['test_info'] = {
            'name': test.name,
            'test_type': test.test_type,
            'status': test.status,
            'primary_metric': test.primary_metric,
            'start_date': test.start_date.isoformat() if test.start_date else None,
            'days_running': (timezone.now() - test.start_date).days if test.start_date else 0,
        }

        return api_success(results)

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


# ==============================================================================
# A/B Test Variant Operations
# ==============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def add_variant(request, test_id):
    """Add a variant to an A/B test."""
    try:
        test = ABTest.objects.get(id=test_id)

        if test.status != 'draft':
            return api_error("Cannot add variants to a non-draft test")

        data = json.loads(request.body) if request.body else {}

        variant = ABTestVariant.objects.create(
            test=test,
            name=data.get('name', f'Variant {test.variants.count()}'),
            description=data.get('description', ''),
            is_control=data.get('is_control', False),
            config=data.get('config', {}),
            traffic_percentage=data.get('traffic_percentage', 50),
        )

        return api_success({
            'variant': {
                'id': str(variant.id),
                'name': variant.name,
                'is_control': variant.is_control,
            }
        }, message='Variant added successfully')

    except ABTest.DoesNotExist:
        return api_error("Test not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def variant_detail(request, variant_id):
    """Update or delete a variant."""
    try:
        variant = ABTestVariant.objects.get(id=variant_id)

        if request.method == "PUT":
            data = json.loads(request.body) if request.body else {}

            if 'name' in data:
                variant.name = data['name']
            if 'description' in data:
                variant.description = data['description']
            if 'config' in data:
                variant.config = data['config']
            if 'traffic_percentage' in data:
                variant.traffic_percentage = data['traffic_percentage']

            variant.save()

            return api_success({
                'variant': {
                    'id': str(variant.id),
                    'name': variant.name,
                }
            }, message='Variant updated successfully')

        elif request.method == "DELETE":
            if variant.is_control and variant.test.variants.count() <= 2:
                return api_error("Cannot delete control variant with only 2 variants")

            variant.delete()
            return api_success(message='Variant deleted successfully')

    except ABTestVariant.DoesNotExist:
        return api_error("Variant not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


# ==============================================================================
# A/B Test Events
# ==============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def record_event(request, variant_id):
    """Record an event for a variant (impression, click, conversion)."""
    try:
        variant = ABTestVariant.objects.get(id=variant_id)
        data = json.loads(request.body) if request.body else {}

        event_type = data.get('event_type', 'impression')

        event = ABTestEvent.objects.create(
            variant=variant,
            event_type=event_type,
            content_id=data.get('content_id', ''),
            platform=data.get('platform', ''),
            session_id=data.get('session_id', ''),
            revenue=data.get('revenue', 0),
            metadata=data.get('metadata', {}),
        )

        return api_success({
            'event': {
                'id': str(event.id),
                'event_type': event.event_type,
            }
        }, message='Event recorded successfully')

    except ABTestVariant.DoesNotExist:
        return api_error("Variant not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


# ==============================================================================
# User Goals CRUD
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_goals(request):
    """List all user goals."""
    try:
        user = request.user if request.user.is_authenticated else None
        is_active = request.GET.get('is_active')

        goals = UserGoal.objects.filter(user=user) if user else UserGoal.objects.all()

        if is_active is not None:
            goals = goals.filter(is_active=is_active.lower() == 'true')

        goals = goals.order_by('-created_at')[:50]

        goals_data = []
        for goal in goals:
            goals_data.append({
                'id': str(goal.id),
                'name': goal.name,
                'description': goal.description,
                'goal_type': goal.goal_type,
                'period': goal.period,
                'target_value': float(goal.target_value),
                'current_value': float(goal.current_value),
                'progress_percentage': goal.progress_percentage,
                'is_achieved': goal.is_achieved,
                'is_active': goal.is_active,
                'start_date': goal.start_date.isoformat(),
                'end_date': goal.end_date.isoformat() if goal.end_date else None,
            })

        return api_success({'goals': goals_data})

    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_goal(request):
    """Create a new goal."""
    try:
        data = json.loads(request.body) if request.body else {}

        required_fields = ['name', 'goal_type', 'target_value', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return api_error(f"Missing required field: {field}")

        user = request.user if request.user.is_authenticated else None

        goal = UserGoal.objects.create(
            user=user,
            name=data['name'],
            description=data.get('description', ''),
            goal_type=data['goal_type'],
            period=data.get('period', 'monthly'),
            target_value=data['target_value'],
            custom_metric=data.get('custom_metric', ''),
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            notify_at_milestones=data.get('notify_at_milestones', True),
            milestone_percentages=data.get('milestone_percentages', [25, 50, 75, 100]),
        )

        return api_success({
            'goal': {
                'id': str(goal.id),
                'name': goal.name,
                'goal_type': goal.goal_type,
                'target_value': float(goal.target_value),
            }
        }, message='Goal created successfully')

    except json.JSONDecodeError:
        return api_error("Invalid JSON data")
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def goal_detail(request, goal_id):
    """Get, update, or delete a specific goal."""
    try:
        goal = UserGoal.objects.get(id=goal_id)

        if request.method == "GET":
            return api_success({
                'goal': {
                    'id': str(goal.id),
                    'name': goal.name,
                    'description': goal.description,
                    'goal_type': goal.goal_type,
                    'period': goal.period,
                    'target_value': float(goal.target_value),
                    'current_value': float(goal.current_value),
                    'progress_percentage': goal.progress_percentage,
                    'custom_metric': goal.custom_metric,
                    'is_achieved': goal.is_achieved,
                    'achieved_at': goal.achieved_at.isoformat() if goal.achieved_at else None,
                    'start_date': goal.start_date.isoformat(),
                    'end_date': goal.end_date.isoformat() if goal.end_date else None,
                    'is_active': goal.is_active,
                    'notify_at_milestones': goal.notify_at_milestones,
                    'milestone_percentages': goal.milestone_percentages,
                    'created_at': goal.created_at.isoformat(),
                }
            })

        elif request.method == "PUT":
            data = json.loads(request.body) if request.body else {}

            if 'name' in data:
                goal.name = data['name']
            if 'description' in data:
                goal.description = data['description']
            if 'target_value' in data:
                goal.target_value = data['target_value']
            if 'is_active' in data:
                goal.is_active = data['is_active']

            goal.save()

            return api_success({
                'goal': {
                    'id': str(goal.id),
                    'name': goal.name,
                    'progress_percentage': goal.progress_percentage,
                }
            }, message='Goal updated successfully')

        elif request.method == "DELETE":
            goal_name = goal.name
            goal.delete()
            return api_success(message=f'Goal "{goal_name}" deleted successfully')

    except UserGoal.DoesNotExist:
        return api_error("Goal not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_goal_progress(request, goal_id):
    """Update the current value of a goal."""
    try:
        goal = UserGoal.objects.get(id=goal_id)
        data = json.loads(request.body) if request.body else {}

        new_value = data.get('current_value')
        if new_value is None:
            return api_error("Missing current_value")

        result = goal.update_progress(new_value)

        return api_success({
            'goal': {
                'id': str(goal.id),
                'name': goal.name,
                'current_value': float(goal.current_value),
                'progress_percentage': result['progress'],
                'is_achieved': result['is_achieved'],
            }
        }, message='Goal progress updated')

    except UserGoal.DoesNotExist:
        return api_error("Goal not found", status=404)
    except Exception as e:
        return api_error(str(e), status=500)
