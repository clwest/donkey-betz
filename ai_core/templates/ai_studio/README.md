# AI Studio Template Structure

Session 186: Created as part of Phase 3 Architecture Improvements

## Overview

This directory contains the modular template structure for AI Image Studio, extracted from the monolithic `ai_image_studio.html` file (~31,000 lines).

## Directory Structure

```
ai_studio/
├── base.html              # Base template with blocks
├── README.md              # This file
└── partials/
    ├── _head.html         # <head> section (meta, CSS)
    ├── _header.html       # Studio header with branding
    ├── _navigation.html   # Tab navigation
    └── _scripts.html      # JavaScript includes
```

## Current Status

The original `ai_image_studio.html` remains the working template. This modular structure provides:

1. **Foundation for migration** - Partials can be gradually adopted
2. **Extracted CSS** - Available at `static/css/ai_studio.css` (~1,077 lines)
3. **Extracted JS** - Available at `static/js/ai_studio/` modules

## Usage

### Using Partials in Existing Template

```django
{% include 'ai_studio/partials/_header.html' %}
```

### Creating New Pages with Base Template

```django
{% extends 'ai_studio/base.html' %}

{% block title %}My Custom Page{% endblock %}

{% block content %}
<div class="tab-pane fade show active" id="custom" role="tabpanel">
    <h3>Custom Content</h3>
</div>
{% endblock %}
```

## Migration Path

To fully migrate from `ai_image_studio.html`:

1. **Phase 1** (Done): Extract CSS and core JS utilities
2. **Phase 2** (Future): Extract tab content into separate partials
3. **Phase 3** (Future): Extract remaining inline JavaScript
4. **Phase 4** (Future): Switch to base.html template inheritance

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `base.html` | ~60 | Base template structure |
| `partials/_head.html` | ~25 | Head section with CSS |
| `partials/_header.html` | ~100 | Branding and feature cards |
| `partials/_navigation.html` | ~60 | Tab navigation |
| `partials/_scripts.html` | ~20 | JS includes |

## JavaScript Modules

See `static/js/ai_studio/README.md` for JavaScript module documentation.

## Related Files

- **Original template**: `ai_image_studio.html` (~31,000 lines)
- **Extracted CSS**: `static/css/ai_studio.css` (~1,077 lines)
- **JS modules**: `static/js/ai_studio/` directory
