#!/usr/bin/env python
"""Populate Redis with real solutions for dashboard display"""
import redis
from intelligence.solution_storage import SolutionStorage
from datetime import datetime
import time

storage = SolutionStorage()

# Add varied real solutions
solutions = [
    {
        'problem': 'Parse command line arguments',
        'code': '''import argparse

def solution(args_list):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument('--input', type=str, help='Input file')
    parser.add_argument('--output', type=str, help='Output file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args(args_list)
    return vars(args)''',
        'agent': 'cli_expert_001',
        'execution_time': 0.002
    },
    {
        'problem': 'Find prime numbers up to N',
        'code': '''def solution(n):
    """Find all prime numbers up to n using Sieve of Eratosthenes"""
    if n < 2:
        return []

    primes = [True] * (n + 1)
    primes[0] = primes[1] = False

    for i in range(2, int(n**0.5) + 1):
        if primes[i]:
            for j in range(i*i, n + 1, i):
                primes[j] = False

    return [i for i, is_prime in enumerate(primes) if is_prime]''',
        'agent': 'math_solver_001',
        'execution_time': 0.005
    },
    {
        'problem': 'Merge two sorted arrays',
        'code': '''def solution(arr1, arr2):
    """Merge two sorted arrays into one sorted array"""
    merged = []
    i = j = 0

    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            merged.append(arr1[i])
            i += 1
        else:
            merged.append(arr2[j])
            j += 1

    # Add remaining elements
    merged.extend(arr1[i:])
    merged.extend(arr2[j:])

    return merged''',
        'agent': 'array_specialist',
        'execution_time': 0.001
    },
    {
        'problem': 'Convert temperature between units',
        'code': '''def solution(value, from_unit, to_unit):
    """Convert temperature between Celsius, Fahrenheit, and Kelvin"""
    # Convert to Celsius first
    if from_unit == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit == 'K':
        celsius = value - 273.15
    else:
        celsius = value

    # Convert from Celsius to target
    if to_unit == 'F':
        return celsius * 9/5 + 32
    elif to_unit == 'K':
        return celsius + 273.15
    else:
        return celsius''',
        'agent': 'conversion_expert',
        'execution_time': 0.0001
    },
    {
        'problem': 'Validate email addresses',
        'code': '''import re

def solution(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))''',
        'agent': 'validation_agent',
        'execution_time': 0.0003
    },
    {
        'problem': 'Calculate compound interest',
        'code': '''def solution(principal, rate, time, n=12):
    """Calculate compound interest
    principal: initial amount
    rate: annual interest rate (as decimal)
    time: time in years
    n: compounds per year
    """
    amount = principal * (1 + rate/n) ** (n * time)
    interest = amount - principal
    return {
        'total_amount': round(amount, 2),
        'interest_earned': round(interest, 2)
    }''',
        'agent': 'finance_calculator',
        'execution_time': 0.0002
    },
    {
        'problem': 'Parse JSON safely',
        'code': '''import json

def solution(json_string):
    """Parse JSON string safely with error handling"""
    try:
        data = json.loads(json_string)
        return {'success': True, 'data': data}
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': str(e),
            'position': e.pos if hasattr(e, 'pos') else None
        }''',
        'agent': 'json_handler',
        'execution_time': 0.0004
    },
    {
        'problem': 'Generate random password',
        'code': '''import random
import string

def solution(length=12, include_symbols=True):
    """Generate secure random password"""
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += string.punctuation

    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits)
    ]

    if include_symbols:
        password.append(random.choice(string.punctuation))

    # Fill the rest
    for _ in range(length - len(password)):
        password.append(random.choice(chars))

    # Shuffle and return
    random.shuffle(password)
    return ''.join(password)''',
        'agent': 'security_expert',
        'execution_time': 0.0006
    },
    {
        'problem': 'Count word frequency',
        'code': '''from collections import Counter

def solution(text):
    """Count word frequency in text"""
    # Convert to lowercase and split
    words = text.lower().split()

    # Remove punctuation
    import string
    translator = str.maketrans('', '', string.punctuation)
    words = [word.translate(translator) for word in words]

    # Count and return top 10
    word_count = Counter(words)
    return dict(word_count.most_common(10))''',
        'agent': 'text_analyzer',
        'execution_time': 0.0008
    },
    {
        'problem': 'Binary search implementation',
        'code': '''def solution(arr, target):
    """Implement binary search on sorted array"""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # Not found''',
        'agent': 'algorithm_master',
        'execution_time': 0.0001
    }
]

print("🚀 Populating Redis with real solutions...")

for i, sol in enumerate(solutions):
    key = storage.store_solution(
        problem=sol['problem'],
        solution_code=sol['code'],
        agent_id=sol['agent'],
        test_results={'execution_time': sol['execution_time'], 'success': True}
    )
    print(f"✅ Added solution {i+1}/{len(solutions)}: {sol['problem']}")
    time.sleep(0.1)  # Small delay to spread timestamps

print("\n📊 Storage Statistics:")
stats = storage.get_statistics()
print(f"  Total solutions: {stats['total_solutions']}")
print(f"  Total problems: {stats['total_problems']}")
print(f"  Agents with solutions: {stats['agents_with_solutions']}")

print("\n✨ Solutions populated successfully!")
print("🌐 Open http://localhost:8000/learning_details_dashboard.html to see them")