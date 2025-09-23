#!/usr/bin/env python
"""
Verify Cost Optimization with gpt-4o-mini
==========================================
Shows cost savings by using gpt-4o-mini vs other models
"""

from config.api_settings import OPENAI_CONFIG, COST_COMPARISON, estimate_cost

def show_cost_savings():
    """
    Demonstrate cost savings with gpt-4o-mini
    """
    print("=" * 70)
    print("💰 COST OPTIMIZATION WITH gpt-4o-mini")
    print("=" * 70)

    # Current configuration
    print(f"\n📋 Current Configuration:")
    print(f"   Model: {OPENAI_CONFIG['model']}")
    print(f"   Max Tokens: {OPENAI_CONFIG['max_tokens']}")
    print(f"   Temperature: {OPENAI_CONFIG['temperature']}")

    # Cost comparison for typical usage
    print(f"\n📊 Cost Comparison (per 1M tokens):")
    print("-" * 50)
    for model, costs in COST_COMPARISON.items():
        print(f"{model:15} Input: ${costs['input']:6.2f}  Output: ${costs['output']:6.2f}")

    # Example usage scenario
    print(f"\n💡 Example: 1000 API calls per day")
    print("   Average: 500 input tokens, 500 output tokens per call")
    print("-" * 50)

    daily_input_tokens = 1000 * 500
    daily_output_tokens = 1000 * 500

    for model in COST_COMPARISON.keys():
        cost = estimate_cost(daily_input_tokens, daily_output_tokens, model)
        print(f"{model:15} Daily cost: {cost['total_cost']:>10}")

    # Monthly projection
    print(f"\n📈 Monthly Projection (30 days):")
    print("-" * 50)

    for model in COST_COMPARISON.keys():
        daily_cost = estimate_cost(daily_input_tokens, daily_output_tokens, model)
        # Extract numeric value from string
        numeric_cost = float(daily_cost['total_cost'].replace('$', ''))
        monthly_cost = numeric_cost * 30
        print(f"{model:15} Monthly: ${monthly_cost:10.2f}")

    # Savings calculation
    print(f"\n✨ SAVINGS with gpt-4o-mini:")
    print("-" * 50)

    mini_daily = estimate_cost(daily_input_tokens, daily_output_tokens, 'gpt-4o-mini')
    mini_cost = float(mini_daily['total_cost'].replace('$', ''))

    for model in ['gpt-3.5-turbo', 'gpt-4']:
        other_daily = estimate_cost(daily_input_tokens, daily_output_tokens, model)
        other_cost = float(other_daily['total_cost'].replace('$', ''))

        savings_daily = other_cost - mini_cost
        savings_monthly = savings_daily * 30
        savings_percent = (savings_daily / other_cost) * 100

        print(f"vs {model:12}")
        print(f"   Daily savings:   ${savings_daily:.2f} ({savings_percent:.0f}% less)")
        print(f"   Monthly savings: ${savings_monthly:.2f}")

    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATION: gpt-4o-mini is optimal for cost")
    print("   - 3x cheaper than gpt-3.5-turbo")
    print("   - 200x cheaper than gpt-4")
    print("   - Perfect for high-volume agent operations")
    print("=" * 70)

if __name__ == "__main__":
    show_cost_savings()