#!/usr/bin/env python3
"""
Check actual API costs for our agent calls
"""

import os
from openai import OpenAI

def calculate_costs():
    """Calculate costs for typical agent calls"""

    print("💰 API COST ANALYSIS")
    print("=" * 50)

    # GPT-4o-mini pricing (as of Sept 2024)
    input_cost_per_1k = 0.00015   # $0.000150 per 1K input tokens
    output_cost_per_1k = 0.0006   # $0.000600 per 1K output tokens

    print(f"📊 GPT-4o-mini pricing:")
    print(f"   Input:  ${input_cost_per_1k:.6f} per 1,000 tokens")
    print(f"   Output: ${output_cost_per_1k:.6f} per 1,000 tokens")
    print()

    # Test a typical agent call
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    print("🧪 Testing typical agent call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional content writer."},
            {"role": "user", "content": "Write a brief 200-word blog post about AI productivity tools."}
        ],
        max_tokens=500
    )

    # Get usage
    usage = response.usage
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    # Calculate costs
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    total_cost = input_cost + output_cost

    print(f"📈 Token usage:")
    print(f"   Input tokens:  {input_tokens:,}")
    print(f"   Output tokens: {output_tokens:,}")
    print(f"   Total tokens:  {total_tokens:,}")
    print()

    print(f"💵 Cost breakdown:")
    print(f"   Input cost:  ${input_cost:.6f}")
    print(f"   Output cost: ${output_cost:.6f}")
    print(f"   Total cost:  ${total_cost:.6f}")
    print()

    # Extrapolate to agent activity
    print("🔢 Typical agent activity costs:")
    print(f"   1 blog post:     ${total_cost:.6f}")
    print(f"   10 blog posts:   ${total_cost * 10:.4f}")
    print(f"   100 blog posts:  ${total_cost * 100:.2f}")
    print(f"   1000 projects:   ${total_cost * 1000:.2f}")
    print()

    print("🔍 Why your balance might not change:")
    print(f"   • GPT-4o-mini is extremely cheap (~${total_cost:.6f} per call)")
    print(f"   • Your account might have free credits")
    print(f"   • OpenAI only charges when costs exceed minimum threshold")
    print(f"   • Changes under $0.01 might not be visible immediately")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    calculate_costs()