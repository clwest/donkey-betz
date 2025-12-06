# Session 378: Cyberpunk Style Bias Fix

## Summary
Fixed the Image Agent's tendency to default to "cyberpunk" style for AI/tech-related projects. The system now selects styles based on project context rather than a biased default.

## Problem
User reported: "We have over 70 styles for images, but for some reason regardless of what the branding strategy or even what the actual project is, if it involves AI it always has a Cyber Punk style selected from the Image Agent."

## Root Cause Found

### Issue: Biased Examples in Docstrings
**Location:** `core/agents/image_agent.py`

The module and class docstrings all used "cyberpunk" as the example style:
- Line 37: `task="create a cyberpunk logo for a tech startup"`
- Line 38: `context={'count': 3, 'style': 'cyberpunk', ...}`
- Line 58: `1. Takes a task like "create a cyberpunk logo"`
- Line 153: `task: User's image request (e.g., "create a cyberpunk logo")`

While GPT doesn't directly read Python docstrings, these examples were:
1. Setting a pattern for developers
2. Influencing tests and documentation
3. Creating cognitive bias in the codebase

### Missing: Style Selection Guidance
The system prompt listed available styles but didn't provide guidance on WHEN to use each style or how to select based on project context.

## Fixes Applied

### 1. Updated Docstring Examples
Changed biased cyberpunk examples to neutral alternatives:

**Module docstring (line 37-38):**
```python
# Before
task="create a cyberpunk logo for a tech startup",
context={'count': 3, 'style': 'cyberpunk', ...}

# After
task="create a modern logo for a bakery",
context={'count': 3, 'style': 'minimalist', ...}
```

**Class docstring (line 58):**
```python
# Before
1. Takes a task like "create a cyberpunk logo"

# After
1. Takes a task like "create a professional logo"
```

### 2. Enhanced System Prompt with Style Selection Guidelines
Added explicit guidance on style selection based on context:

```python
IMPORTANT - Style Selection Guidelines:
- Match style to the PROJECT/BRAND context, not to a default preference
- For AI/tech companies: Consider clean, modern, minimalist, or professional styles first
- For creative agencies: Consider artistic, colorful, or unique brand-appropriate styles
- For corporate: Consider professional, clean, or photorealistic styles
- ONLY use cyberpunk/neon styles when the brand explicitly calls for it
- When in doubt, prefer: minimalist, modern, professional, or clean styles

SPECIAL STYLES (use only when explicitly requested or matching brand):
- cyberpunk: For explicitly futuristic/dystopian/neon-focused brands
- fantasy: For gaming, entertainment, or magical themes
- steampunk: For Victorian/mechanical aesthetics
```

### 3. Updated Router Example
Changed `agents/router.py` docstring example from cyberpunk to neutral:

```python
# Before
question='Find trending cyberpunk art styles',
context={'style_focus': 'neon', 'era': 'modern'}

# After
question='Find trending logo design styles',
context={'style_focus': 'modern', 'era': '2024'}
```

## Files Modified
- `core/agents/image_agent.py:37-38` - Module docstring example
- `core/agents/image_agent.py:58` - Class docstring example
- `core/agents/image_agent.py:74-110` - Enhanced system prompt with style guidelines
- `core/agents/image_agent.py:152` - Execute method docstring example
- `agents/router.py:1036-1037` - Router docstring example

## Expected Behavior After Fix

### Before:
- AI/tech project → cyberpunk style (biased default)
- Corporate project → cyberpunk style (biased default)
- Any tech-adjacent request → cyberpunk style

### After:
- AI/tech project → modern, minimalist, or professional styles
- Corporate project → professional, clean, or photorealistic styles
- Cyberpunk → Only when explicitly requested or brand demands it

## Key Learnings

### Docstrings Matter for AI-Assisted Code
Even though GPT doesn't read Python docstrings directly, they:
1. Set patterns that developers follow
2. Influence tests and documentation
3. Create subtle biases in the codebase
4. Affect how features are used and documented

### Explicit Guidance Beats Implicit Defaults
The system prompt now explicitly tells GPT:
- WHEN to use each style category
- What to prefer when uncertain
- What "special" styles require explicit context

## Related Sessions
- Session 377: Dream Implementation Image Fix
- Session 268: Image Agent isolation (created the file)
- Session 334: Project Context Support (added brand_style support)
