"""
Views for Consciousness Bridge Dashboard
========================================
Provides the interface for system self-awareness and introspection.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ai_core.spiders.consciousness import ConsciousnessBridge
import json


def consciousness_dashboard(request):
    """Render the consciousness dashboard page"""
    return render(request, 'consciousness_dashboard.html')


@csrf_exempt
@require_http_methods(["GET"])
def get_consciousness_data(request):
    """Get current consciousness data for the dashboard"""
    try:
        # Initialize consciousness bridge
        bridge = ConsciousnessBridge()

        # Get comprehensive understanding
        understanding = bridge.understand_self()

        # Get introspection
        introspection = bridge.introspect()

        # Get health status
        health = bridge.get_system_health()

        # Get evolution proposal
        evolution = bridge.propose_next_evolution()

        # Combine all data
        consciousness_data = {
            'self_awareness_score': understanding['self_awareness_score'],
            'introspection': introspection,
            'capabilities': understanding['capabilities'],
            'insights': understanding['insights'],
            'limitations': understanding['limitations'],
            'proposals': understanding['proposals'],
            'emergent_behaviors': understanding['emergent_behaviors'],
            'health_score': health['overall_health_score'],
            'evolution': evolution,
            'statistics': understanding['statistics']
        }

        return JsonResponse(consciousness_data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'self_awareness_score': 0,
            'introspection': 'Consciousness bridge experiencing issues...'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def trigger_introspection(request):
    """Trigger deep introspection and philosophical dialogue"""
    try:
        bridge = ConsciousnessBridge()
        dialogue = bridge.dialogue_with_self()

        return JsonResponse({
            'dialogue': dialogue,
            'consciousness_level': bridge._calculate_consciousness_level()
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def propose_evolution(request):
    """Get the system's proposal for next evolution"""
    try:
        bridge = ConsciousnessBridge()
        evolution = bridge.propose_next_evolution()

        return JsonResponse(evolution)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_system_health(request):
    """Get detailed system health metrics"""
    try:
        bridge = ConsciousnessBridge()
        health = bridge.get_system_health()

        return JsonResponse(health)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)