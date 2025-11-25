# Phase 3: Architecture & Code Quality Improvements (P2)

**Execution Mode:** PARALLEL (files are independent)
**Duration:** 2-4 weeks
**Total Tasks:** 8 major refactoring tasks

---

## Parallel Execution Guide

These tasks modify independent files and can run in **multiple Claude Code instances simultaneously**.

### Recommended Parallel Groups

```
Claude Code 1: Tasks 3.1, 3.2 (Python backend decomposition)
Claude Code 2: Tasks 3.3, 3.4 (Frontend refactoring)
Claude Code 3: Tasks 3.5, 3.6 (Database & API improvements)
Claude Code 4: Tasks 3.7, 3.8 (Agent & utility improvements)
```

### Coordination Rules
- Each task works on different files - no conflicts
- Commit frequently to avoid large merges
- If tasks overlap, coordinate via comments in PROGRESS-LOG.md

---

## Task Overview

| Task | Focus | Files | Effort | Parallelizable |
|------|-------|-------|--------|----------------|
| 3.1 | Decompose AI Assistant | `personal_ai_assistant_enhanced.py` | 16h | Yes |
| 3.2 | Decompose Image Views | `views_image.py` | 12h | Yes |
| 3.3 | Frontend Modularization | `ai_image_studio.html` | 20h | Yes |
| 3.4 | Extract Frontend JavaScript | Template JS → files | 16h | Yes |
| 3.5 | Database Model Improvements | `content/models.py` | 8h | Yes |
| 3.6 | API Provider Standardization | `*_provider.py` | 8h | Yes |
| 3.7 | Agent System Cleanup | `agents/`, `intelligence/` | 8h | Yes |
| 3.8 | Utility Consolidation | Various utils | 6h | Yes |

---

## Task 3.1: Decompose AI Assistant (personal_ai_assistant_enhanced.py)

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
7,000+ line monolithic file is difficult to maintain, test, and understand.

### Claude Code Prompt
```
# REMEDIATION TASK 3.1: Decompose AI Assistant

## Context
The personal_ai_assistant_enhanced.py file is 7,000+ lines and needs to be decomposed into focused modules.

## Your Task
1. Analyze the file structure and identify logical groupings
2. Create a new package structure: core/assistant/
3. Extract components into separate modules
4. Maintain all existing functionality
5. Update imports throughout codebase

## Target Structure
```
core/assistant/
├── __init__.py              # Public API exports
├── base.py                  # PersonalAIAssistant base class
├── message_processor.py     # Message handling logic
├── tool_executor.py         # Tool execution logic
├── prompt_builder.py        # System prompt construction
├── context_manager.py       # Conversation context handling
├── response_formatter.py    # Response formatting
├── utils.py                 # Helper functions
└── constants.py             # Constants and configurations
```

## Extraction Guidelines

### base.py (~500 lines)
- Main class definition
- Initialization
- Public interface methods

### message_processor.py (~1,500 lines)
- process_message()
- _parse_user_intent()
- _handle_tool_request()
- Message routing logic

### tool_executor.py (~2,000 lines)
- execute_tool()
- All tool-specific execution methods
- Tool result formatting

### prompt_builder.py (~800 lines)
- _build_system_prompt()
- _get_tool_definitions()
- Context injection

### context_manager.py (~500 lines)
- Conversation history management
- Context window handling
- Memory/learning integration

### response_formatter.py (~400 lines)
- Format AI responses
- Error message formatting
- Progress message formatting

## Important
- Keep the same public API (PersonalAIAssistant class)
- All existing code should work without changes
- Add __all__ exports in __init__.py
- Write docstrings for each module

## Verification Steps
After refactoring:
1. python -c "from core.assistant import PersonalAIAssistant"
2. python manage.py check
3. Test AI assistant functionality

Begin by reading core/personal_ai_assistant_enhanced.py to understand the structure.
```

### Verification
```bash
python -c "from core.assistant import PersonalAIAssistant"
python manage.py check
make start
# Test assistant chat functionality
```

### Completion Sign-off
- [ ] Package structure created
- [ ] All components extracted
- [ ] Imports updated
- [ ] Tests pass
- [ ] Assistant functionality works

---

## Task 3.2: Decompose Image Views (views_image.py)

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
7,500+ line views file is difficult to maintain and navigate.

### Claude Code Prompt
```
# REMEDIATION TASK 3.2: Decompose Image Views

## Context
The views_image.py file is 7,500+ lines. Decompose into focused view modules.

## Your Task
1. Analyze views_image.py and identify logical groupings
2. Create core/views/images/ package
3. Extract views by operation type
4. Update URL routing

## Target Structure
```
core/views/images/
├── __init__.py              # Router/exports
├── generation.py            # Image generation views
├── editing.py               # Image editing views (upscale, crop, etc.)
├── manipulation.py          # Background removal, recolor, etc.
├── gallery.py               # Gallery listing and detail views
├── batch.py                 # Batch operation views
└── utils.py                 # Shared view utilities
```

## Extraction by Functionality

### generation.py (~1,200 lines)
- generate_image()
- generate_with_style()
- Text-to-image endpoints

### editing.py (~1,500 lines)
- upscale_image()
- crop_image()
- Structure control
- Creative upscale

### manipulation.py (~1,500 lines)
- remove_background()
- recolor_image()
- search_and_replace()
- inpaint/outpaint

### gallery.py (~800 lines)
- list_images()
- image_detail()
- delete_image()
- Pagination helpers

### batch.py (~500 lines)
- batch_operation()
- Batch upscale
- Batch background removal

## URL Routing Update
Update core/urls.py to import from new locations:
```python
from core.views.images import generation, editing, manipulation, gallery, batch

urlpatterns = [
    path('images/generate/', generation.generate_image),
    path('images/upscale/', editing.upscale_image),
    # etc.
]
```

Begin by reading core/views_image.py to understand the view organization.
```

### Verification
```bash
python manage.py check
python manage.py test  # If tests exist
make start
# Test each image operation type
```

### Completion Sign-off
- [ ] Package structure created
- [ ] Views extracted by type
- [ ] URL routing updated
- [ ] All image operations work

---

## Task 3.3: Frontend Modularization (HTML Template)

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
31,000+ line template with 387 functions is unmaintainable.

### Claude Code Prompt
```
# REMEDIATION TASK 3.3: Frontend Template Modularization

## Context
ai_image_studio.html is 31,000+ lines with embedded JavaScript. Begin modularization.

## Your Task
1. Identify the major sections of the template
2. Extract reusable template components using Django includes
3. Create component templates for repeated UI patterns
4. Keep JavaScript embedded for now (Task 3.4 handles JS extraction)

## Target Structure
```
ai_core/templates/
├── ai_image_studio.html          # Main template (reduced size)
├── components/
│   ├── image_card.html           # Image gallery card
│   ├── video_card.html           # Video gallery card
│   ├── model_card.html           # 3D model card
│   ├── chat_message.html         # Chat message component
│   ├── progress_indicator.html   # Progress/loading UI
│   ├── project_sidebar.html      # Project sidebar
│   ├── gallery_section.html      # Gallery section wrapper
│   └── modal_base.html           # Modal dialog base
├── partials/
│   ├── header.html               # Page header
│   ├── footer.html               # Page footer
│   └── navigation.html           # Navigation menu
└── includes/
    ├── scripts.html              # JavaScript includes
    └── styles.html               # CSS includes
```

## Django Include Pattern
```html
<!-- In main template -->
{% include "components/image_card.html" with image=image_obj %}

<!-- In image_card.html -->
<div class="image-card" data-id="{{ image.id }}">
    <img src="{{ image.url }}" alt="{{ image.prompt|truncatewords:10 }}">
    <div class="image-info">
        <span class="image-number">#{{ image.sequential_number }}</span>
    </div>
</div>
```

## Priority Extractions
1. Asset cards (image, video, 3D model) - heavily duplicated
2. Chat message rendering
3. Progress indicators
4. Modal dialogs
5. Sidebar sections

Begin by analyzing ai_core/templates/ai_image_studio.html structure.
```

### Verification
```bash
make start
# Test all UI components render correctly
# Test chat functionality
# Test gallery displays
```

### Completion Sign-off
- [ ] Component templates created
- [ ] Main template uses includes
- [ ] Template size reduced
- [ ] All UI functionality works

---

## Task 3.4: Extract Frontend JavaScript

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
JavaScript embedded in HTML template prevents proper testing and caching.

### Claude Code Prompt
```
# REMEDIATION TASK 3.4: Extract Frontend JavaScript

## Context
The 387 JavaScript functions in ai_image_studio.html should be extracted to separate files.

## Your Task
1. Identify JavaScript sections in the template
2. Create organized JS module structure
3. Extract functions by domain
4. Set up proper script loading

## Target Structure
```
core/static/js/ai_studio/
├── main.js                    # Entry point, initialization
├── api.js                     # API communication layer
├── chat.js                    # Chat functionality
├── gallery.js                 # Gallery management
├── images.js                  # Image operations
├── videos.js                  # Video operations
├── models3d.js               # 3D model operations
├── projects.js                # Project management
├── websocket.js               # WebSocket handling
├── ui/
│   ├── modals.js             # Modal dialogs
│   ├── notifications.js      # Toast/notifications
│   ├── progress.js           # Progress indicators
│   └── forms.js              # Form handling
└── utils/
    ├── helpers.js            # Utility functions
    ├── validation.js         # Input validation
    └── formatting.js         # Data formatting
```

## Module Pattern
```javascript
// api.js
const AIStudioAPI = (function() {
    'use strict';

    const BASE_URL = '/api/';

    async function authenticatedFetch(url, options = {}) {
        const csrfToken = getCookie('csrftoken');
        return fetch(url, {
            ...options,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
    }

    async function generateImage(prompt, options = {}) {
        return authenticatedFetch(`${BASE_URL}images/generate/`, {
            method: 'POST',
            body: JSON.stringify({ prompt, ...options })
        });
    }

    // Public API
    return {
        generateImage,
        // other exports
    };
})();
```

## Script Loading
```html
<!-- In template -->
<script src="{% static 'js/ai_studio/utils/helpers.js' %}"></script>
<script src="{% static 'js/ai_studio/api.js' %}"></script>
<script src="{% static 'js/ai_studio/chat.js' %}"></script>
<!-- ... -->
<script src="{% static 'js/ai_studio/main.js' %}"></script>
```

Begin by analyzing the JavaScript in ai_image_studio.html.
```

### Verification
```bash
make start
# Open browser dev tools - no JS errors
# Test all interactive features
```

### Completion Sign-off
- [ ] JS files created
- [ ] Functions extracted by domain
- [ ] Scripts load correctly
- [ ] All functionality works
- [ ] No console errors

---

## Task 3.5: Database Model Improvements

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
Various database model issues: JSONField without schema, inconsistent patterns.

### Claude Code Prompt
```
# REMEDIATION TASK 3.5: Database Model Improvements

## Context
Database models need improvements for consistency and data integrity.

## Your Task
1. Add JSONField schema validation where needed
2. Ensure all models inherit from UnifiedBaseModel where appropriate
3. Add missing indexes
4. Improve model docstrings

## Files to Modify
- `content/models.py`
- `core/models.py`

## Improvements

### JSONField Validation
```python
from django.core.validators import ValidationError
import jsonschema

# Define schemas for JSON fields
PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "width": {"type": "integer", "minimum": 64, "maximum": 4096},
        "height": {"type": "integer", "minimum": 64, "maximum": 4096},
        "style": {"type": "string"},
        # etc.
    }
}

def validate_parameters(value):
    try:
        jsonschema.validate(value, PARAMETERS_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValidationError(f"Invalid parameters: {e.message}")

class ImageHistory(UnifiedBaseModel):
    parameters = models.JSONField(
        default=dict,
        validators=[validate_parameters],
        help_text="Generation parameters"
    )
```

### Ensure UnifiedBaseModel inheritance
Check all models inherit from UnifiedBaseModel for consistency.

### Index Improvements
```python
class Meta:
    indexes = [
        models.Index(fields=['user', 'created_at']),
        models.Index(fields=['project', 'sequential_number']),
        models.Index(fields=['status', 'created_at']),
    ]
```

Begin by reading content/models.py and identifying improvements.
```

### Verification
```bash
python manage.py makemigrations --dry-run
python manage.py check
```

### Completion Sign-off
- [ ] JSONField validation added
- [ ] All models use UnifiedBaseModel
- [ ] Indexes optimized
- [ ] Migrations created (if needed)

---

## Task 3.6: API Provider Standardization

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
API providers have inconsistent patterns for error handling, retries, timeouts.

### Claude Code Prompt
```
# REMEDIATION TASK 3.6: API Provider Standardization

## Context
The various *_provider.py files have inconsistent patterns. Standardize them.

## Your Task
1. Create a base provider class with common functionality
2. Standardize error handling, retries, timeouts
3. Refactor existing providers to inherit from base

## Files to Create/Modify
- Create: `content/providers/base.py`
- Modify: All `*_provider.py` files

## Base Provider Implementation
```python
"""Base provider for external API integrations."""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for external API providers."""

    def __init__(self):
        self.timeout = getattr(settings, 'API_TIMEOUT', 60)
        self.max_retries = getattr(settings, 'API_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'API_RETRY_DELAY', 1)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider for logging."""
        pass

    @property
    @abstractmethod
    def api_key(self) -> str:
        """API key for authentication."""
        pass

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('headers', {})

        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, **kwargs)

                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"{self.provider_name}: Rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                logger.warning(f"{self.provider_name}: Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"{self.provider_name}: Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    def _handle_error(self, response: requests.Response) -> Dict[str, Any]:
        """Standardized error response handling."""
        return {
            'success': False,
            'error': f"{self.provider_name} API error",
            'status_code': response.status_code,
            'details': response.text[:500]  # Truncate for safety
        }
```

Begin by creating the base provider and analyzing existing providers.
```

### Verification
```bash
python manage.py check
# Test each provider works
```

### Completion Sign-off
- [ ] Base provider created
- [ ] All providers inherit from base
- [ ] Consistent error handling
- [ ] Retry logic standardized

---

## Task 3.7: Agent System Cleanup

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
Agent system has inconsistencies and incomplete implementations.

### Claude Code Prompt
```
# REMEDIATION TASK 3.7: Agent System Cleanup

## Context
The agent system has inconsistent patterns and incomplete operations.

## Your Task
1. Review all agents for consistency
2. Complete partial implementations
3. Standardize agent interface
4. Fix datetime inconsistencies

## Files to Modify
- `agents/video_agent.py`
- `agents/audio_agent.py`
- `agents/three_d_generation_agent.py`
- `intelligence/agent_orchestrator.py`
- `intelligence/agent_executor.py`

## Agent Interface Standardization
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """Base class for all agents."""

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of agent capabilities."""
        pass

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return result."""
        pass

    @abstractmethod
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if agent can handle the task."""
        pass
```

## DateTime Fixes
```python
from django.utils import timezone

# Use timezone-aware datetimes
now = timezone.now()  # NOT datetime.now()

# Consistent formatting
timestamp = now.isoformat()
```

Begin by reviewing the agent files.
```

### Verification
```bash
python manage.py check
# Test agent operations
```

### Completion Sign-off
- [ ] Agents follow standard interface
- [ ] Incomplete operations fixed
- [ ] DateTime handling consistent
- [ ] All agent operations work

---

## Task 3.8: Utility Consolidation

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
Utility functions scattered and duplicated across codebase.

### Claude Code Prompt
```
# REMEDIATION TASK 3.8: Utility Consolidation

## Context
Various utility functions are duplicated or scattered. Consolidate them.

## Your Task
1. Identify duplicate utility functions
2. Create organized utility package
3. Update imports throughout codebase

## Target Structure
```
core/utils/
├── __init__.py
├── id_resolver.py      # From Task 2.13
├── url_validator.py    # From Task 1.9
├── temp_files.py       # From Task 2.10
├── file_handling.py    # File operations
├── formatting.py       # String/data formatting
├── validation.py       # Input validation
└── datetime_utils.py   # Datetime utilities
```

## Common Utilities to Consolidate

### formatting.py
```python
def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def slugify(text: str) -> str:
    # Convert to lowercase, replace spaces with hyphens
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
```

### datetime_utils.py
```python
from django.utils import timezone
from datetime import timedelta

def time_ago(dt) -> str:
    """Return human-readable time ago string."""
    now = timezone.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
```

Begin by searching for duplicate utility patterns.
```

### Verification
```bash
python manage.py check
# Test utilities work correctly
```

### Completion Sign-off
- [ ] Utilities consolidated
- [ ] Duplicates removed
- [ ] Imports updated
- [ ] All functionality works

---

## Phase 3 Completion Checklist

### All Tasks Complete
- [ ] 3.1 AI Assistant decomposed
- [ ] 3.2 Image views decomposed
- [ ] 3.3 Frontend templates modularized
- [ ] 3.4 JavaScript extracted
- [ ] 3.5 Database models improved
- [ ] 3.6 API providers standardized
- [ ] 3.7 Agent system cleaned up
- [ ] 3.8 Utilities consolidated

### Quality Verification
- [ ] `python manage.py check` passes
- [ ] `make start` succeeds
- [ ] All features work correctly
- [ ] No JavaScript errors in browser
- [ ] Code is more maintainable

### Documentation
- [ ] Module docstrings added
- [ ] Import changes documented
- [ ] Architecture docs updated

---

## Next Steps

After completing Phase 3:

1. Update progress in `00-REMEDIATION-ORCHESTRATOR.md`
2. Create git tag: `git tag -a v1.2-architecture -m "Phase 3 architecture improvements complete"`
3. Proceed to `04-PHASE4-TESTING.md`
