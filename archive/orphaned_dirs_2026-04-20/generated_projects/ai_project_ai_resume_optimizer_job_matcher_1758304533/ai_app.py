#!/usr/bin/env python3
"""
AI Resume Optimizer & Job Matcher
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def main():
    print("🤖 AI Resume Optimizer & Job Matcher")
    print("💰 Revenue Potential: $2,000-10,000/month")

    while True:
        user_input = input("\nEnter your input (or 'quit'): ")
        if user_input.lower() == 'quit':
            break

        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant."},
                    {"role": "user", "content": user_input}
                ],
                max_completion_tokens=300
            )

            print("\nAI:", response.choices[0].message.content)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
