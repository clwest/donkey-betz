import os
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('OPENAI_API_KEY', '')
print('API Key configured:', bool(key and 'your-key' not in key))