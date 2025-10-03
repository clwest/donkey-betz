# Crypto Detection False Positive Fix

## Problem
The system was incorrectly detecting "crypto" data requests in messages like:
"Tell me something that you know about me. Not something that's common knowledge dig a little deeper"

## Root Cause
The keyword 'eth' (for Ethereum) was matching the substring in "something".

## Solution
Update the crypto detection in `/backend/ai_partner/api_services/core.py` to use word boundaries:

```python
# Old problematic code:
'crypto': {
    'keywords': ['btc', 'bitcoin', 'eth', 'ethereum', 'crypto', 'cryptocurrency'],
    'must_have_context': [],  # Crypto keywords are specific enough
    'exclude_contexts': []
}

# Fixed code with word boundaries:
'crypto': {
    'keywords': ['bitcoin', 'ethereum', 'crypto', 'cryptocurrency'],
    'word_boundary_keywords': ['btc', 'eth'],  # These need word boundaries
    'must_have_context': [],
    'exclude_contexts': []
}
```

Then update the detection logic to handle word boundaries:

```python
# Add word boundary check for short keywords
import re

# In detect_data_requests method:
if 'word_boundary_keywords' in pattern_config:
    for wb_keyword in pattern_config['word_boundary_keywords']:
        if re.search(r'\b' + re.escape(wb_keyword) + r'\b', message_lower):
            keyword_found = True
            break
```

This ensures 'eth' only matches as a complete word, not as part of "something", "method", "whether", etc.