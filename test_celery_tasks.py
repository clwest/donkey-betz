#!/usr/bin/env python
"""
Test Celery tasks for prediction evaluation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sports.tasks import evaluate_completed_predictions, generate_accuracy_report

print("=" * 80)
print("TESTING CELERY TASKS")
print("=" * 80)

print("\n1. Testing evaluate_completed_predictions task...")
print("-" * 80)
result = evaluate_completed_predictions()
print(f"Result: {result}")

print("\n2. Testing generate_accuracy_report task...")
print("-" * 80)
result = generate_accuracy_report()
print(f"\nReport generated successfully!")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETE")
print("=" * 80)