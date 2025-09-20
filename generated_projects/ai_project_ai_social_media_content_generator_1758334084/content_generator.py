#!/usr/bin/env python3
"""
AI Content Generator
"""

import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title('🖋️ AI Content Generator')

topic = st.text_input('Enter your topic:')
content_type = st.selectbox('Content Type', ['Blog Post', 'Social Media', 'Email'])

if st.button('Generate Content'):
    if topic and openai.api_key:
        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a professional content writer."},
                    {"role": "user", "content": f"Create a {content_type.lower()} about {topic}"}
                ],
                max_completion_tokens=500
            )

            content = response.choices[0].message.content
            st.write(content)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning('Please enter a topic and configure OpenAI API key')

st.sidebar.write("💰 Revenue: $2,000-15,000/month")
