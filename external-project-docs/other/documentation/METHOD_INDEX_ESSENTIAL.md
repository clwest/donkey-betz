# METHOD_INDEX_ESSENTIAL.md - Top 20% Most-Used Methods

> Quick reference for the most frequently used imports and methods in Donkey Betz
> Last Updated: June 26, 2025

## 🚀 Quick Jump
- [Authentication](#authentication)
- [AI Chat & Agents](#ai-chat--agents)
- [Universal Business Builder](#universal-business-builder-new)
- [API Services](#api-services)
- [Models & Database](#models--database)
- [Flutter Essentials](#flutter-essentials)
- [Common Patterns](#common-patterns)
- [Error Fixes](#quick-error-fixes)

---

## Asset Gallery (AI Images)

### Essential Models
```python
from content.models import GeneratedImage, ImageCategory, ImageTag

# Create image record
image = GeneratedImage.objects.create(
    user=user,
    prompt="A modern office",
    style="professional",
    image_url=url,
    category=category,  # Optional
    project_name="Q4 Campaign"  # Optional
)

# Add tags
image.tags.add(tag1, tag2)
```

### API Endpoints
```python
# Generate image
POST /api/content/images/unified/generate/
{
    "prompt": "A beautiful sunset",
    "style": "photorealistic",
    "backend": "dalle3"  # or "stable-diffusion" or "auto"
}

# Delete image
DELETE /api/content/images/{id}/delete/

# Batch operations
POST /api/content/images/batch/
{
    "operation": "delete",  # or "add_category", "add_tags", "toggle_favorite"
    "image_ids": [1, 2, 3],
    "category_id": 5,  # for add_category
    "tags": ["marketing", "social"]  # for add_tags
}

# Search images
GET /api/content/images/search/?q=sunset&category=1&tags=nature,landscape
```

### React/TypeScript Usage
```typescript
import { contentService } from './services/api/content.service';

// Generate image
const result = await contentService.generateImage({
    prompt: "A futuristic city",
    style: "cyberpunk",
    backend: "dalle3"
});

// Delete image
await contentService.deleteImage(imageId);

// Get all images
const images = await contentService.getGeneratedImages();
```

---

## Authentication

### Django Quick Start
```python
# User model
from accounts.models import User

# Auth decorators
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# JWT tokens
from rest_framework_simplejwt.tokens import RefreshToken
```

### Flutter Auth
```dart
import 'package:momentum_flutter/services/auth_service.dart';

// Login
await AuthService.login(email, password);

// Get token
String? token = await AuthService.getAccessToken();

// Logout
await AuthService.logout();
```

---

## AI Chat & Agents

### Deploy an Agent (Most Common Task)
```python
from agent_orchestra.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(user)
result = await orchestrator.deploy_single_agent(
    "Market Intelligence Agent",  # Agent name
    "research AI fitness apps",   # Task
    wait_for_completion=False
)
```

### Personal AI Chat
```python
from ai_partner.services.personal_ai_service import PersonalAIService

service = PersonalAIService()
response = await service.chat(
    message="Deploy the Business Agent to create a plan",
    user=user,
    conversation_id=conversation_id  # Optional
)
```

### Agent Models
```python
from agent_orchestra.models import (
    TaskOrchestration,  # Main orchestration
    AgentInstance,      # Individual agent
    AgentTemplate,      # Agent types
)

# Get active agents
active = AgentInstance.objects.filter(
    orchestration__user=user,
    current_status='working'
)
```

### Agent Management Commands
```bash
# Monitor and restart stuck agents
python manage.py monitor_stuck_agents  # Run continuously
python manage.py monitor_stuck_agents --once  # Run once
python manage.py monitor_stuck_agents --interval 30 --max-retries 3

# Fix stuck agents manually
python fix_stuck_agents.py  # Stops simulations & restarts stuck agents

# Monitor agent progress in real-time
./monitor_agent_progress.sh
```

---

## API Services

### Make API Calls (Django)
```python
from django.http import JsonResponse
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def my_endpoint(request):
    try:
        # Your logic
        return Response({'success': True, 'data': result})
    except Exception as e:
        return Response({'error': str(e)}, status=400)
```

### Make API Calls (Flutter)
```dart
import 'package:momentum_flutter/services/api_service.dart';

// GET request
final response = await ApiService.get('/api/endpoint/');

// POST request
final response = await ApiService.post('/api/endpoint/', {
  'key': 'value'
});
```

---

## Universal Business Builder (NEW!)

### 🚀 Frontend Service (Latest Integration)
```typescript
// Import the service
import { universalBuilderService } from '../../../services/universalBuilder.service';

// Generate business
const response = await universalBuilderService.generateBusiness({
    businessIdea: "AI-powered fitness coaching platform",
    businessName: "FitGenius",
    businessType: "saas"
});

// Poll for completion
const result = await universalBuilderService.waitForCompletion(
    response.taskId,
    (progress) => console.log(`Progress: ${progress.progress}%`)
);

// List previous builds
const businesses = await universalBuilderService.listBusinesses();
```

### Quick Start - Generate a Complete Business
```python
# Generate a business from idea
from universal_builder.views import generate_business

POST /api/universal-builder/generate/
{
    "business_idea": "Online tutoring platform for K-12 students",
    "business_name": "TutorConnect",
    "business_type": "saas"
}
```

### Essential Imports
```python
# Models
from universal_builder.models import GeneratedBusiness, GeneratedFile, StackPattern

# Business Orchestrator
from universal_builder.business_orchestrator import BusinessOrchestrator, BusinessPlan

# Stack Decision
from universal_builder.stack_decision_engine import StackDecisionEngine, BusinessRequirements

# Builder Agents  
from universal_builder.builder_agents import (
    DjangoBuilderAgent, ExpressBuilderAgent, NextJSBuilderAgent,
    AuthenticationAgent, PaymentAgent
)
```

### API Endpoints
```python
# Generate business
POST /api/universal-builder/generate/

# Check status
GET /api/universal-builder/businesses/{id}/

# List all businesses
GET /api/universal-builder/businesses/

# Get generated files
GET /api/universal-builder/businesses/{id}/files/

# Download as ZIP
POST /api/universal-builder/businesses/{id}/download/

# Get stack recommendations
GET /api/universal-builder/recommendations/?business_type=saas&budget=medium
```

### Common Usage Patterns
```python
# Initialize orchestrator
orchestrator = BusinessOrchestrator()

# Build business (async)
result = await orchestrator.build_business(
    business_idea="AI-powered CRM",
    user_context={'user_id': user.id}
)

# Check generated business
business = GeneratedBusiness.objects.get(id=business_id)
print(f"Status: {business.status}")
print(f"Progress: {business.progress}%")
print(f"Files: {business.total_files_generated}")
```

---

## Models & Database

### Essential Models
```python
# User
from accounts.models import User
user = User.objects.get(email="user@example.com")

# Memory
from ai_partner.models import ConversationMemory
memories = ConversationMemory.objects.filter(user=user)

# Agents
from agent_orchestra.models import AgentInstance
agents = AgentInstance.objects.filter(orchestration__user=user)
```

### Common ORM Patterns
```python
# Create
obj = Model.objects.create(field1=value1, field2=value2)

# Get or 404
from django.shortcuts import get_object_or_404
obj = get_object_or_404(Model, pk=id)

# Filter with multiple conditions
results = Model.objects.filter(
    user=user,
    status__in=['active', 'pending'],
    created_at__gte=datetime.now() - timedelta(days=7)
)
```

---

## Flutter Essentials

### Navigation
```dart
// Navigate to page
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => NewPage()),
);

// Navigate with replacement
Navigator.pushReplacement(
  context,
  MaterialPageRoute(builder: (context) => HomePage()),
);

// Pop back
Navigator.pop(context);
```

### State Management
```dart
// Set state in StatefulWidget
setState(() {
  _isLoading = false;
  _data = newData;
});

// IMPORTANT: Check mounted first!
if (mounted) {
  setState(() {
    _isLoading = false;
  });
}
```

### Common Widgets
```dart
// Loading indicator
if (_isLoading) {
  return Center(child: CircularProgressIndicator());
}

// Error display
if (_error != null) {
  return Center(
    child: Text('Error: $_error', 
      style: TextStyle(color: Colors.red)
    ),
  );
}

// List builder
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(title: Text(items[index]));
  },
)
```

---

## Common Patterns

### Async/Sync in Django
```python
# PROBLEM: "You cannot call this from an async context"
# SOLUTION: Use sync_to_async
from asgiref.sync import sync_to_async

# Wrap ORM calls
user = await sync_to_async(User.objects.get)(id=user_id)

# For querysets
agents = await sync_to_async(
    lambda: list(AgentInstance.objects.filter(user=user))
)()
```

### API Response Pattern
```python
# Success response
return Response({
    'success': True,
    'data': {
        'id': obj.id,
        'message': 'Operation successful'
    }
})

# Error response
return Response({
    'success': False,
    'error': 'Detailed error message'
}, status=400)
```

### Flutter Try-Catch Pattern
```dart
try {
  setState(() => _isLoading = true);
  
  final response = await ApiService.post('/api/endpoint/', data);
  
  if (mounted) {
    setState(() {
      _isLoading = false;
      _result = response['data'];
    });
  }
} catch (e) {
  if (mounted) {
    setState(() {
      _isLoading = false;
      _error = e.toString();
    });
  }
}
```

---

## Quick Error Fixes

### JWT Token Expired (Normal)
```dart
// This is EXPECTED behavior - tokens expire after 15 minutes
// Flutter automatically refreshes on 401 responses
// No action needed - it's handled!
```

### Flutter Type Mismatch
```dart
// Handle both List and Map responses
if (response is List) {
  return response;
} else if (response is Map && response['results'] != null) {
  return response['results'];
}
return [];
```

### Null Safety in Flutter
```dart
// Always check for null
final data = agent.outputData;
if (data != null && data['results'] != null) {
  // Safe to use data['results']
}

// Use null-aware operators
String? name = user?.profile?.displayName ?? 'Anonymous';
```

### Text Cleaning (UTF-8 Issues)
```python
from core.services.text_cleaning_service import text_cleaner

# Clean any text
cleaned = text_cleaner.clean_text(dirty_text)

# Clean API response
cleaned_response = text_cleaner.clean_dict(response_data)
```

---

## Management Commands

### Essential Commands
```bash
# Create initial data
python manage.py create_agent_templates
python manage.py create_personalities

# Run agent progress simulation
python manage.py simulate_agent_progress --continuous --interval 30

# Clean text in database
python manage.py clean_all_text

# Test features
python test_minimal_auth.py
python scripts/test_asset_generation.py
```

---

## React Command Center Quick Start

### Setup
```bash
cd moveyourazz-command-center
npm install
npm run dev  # http://localhost:5173
```

### Essential Imports
```typescript
// API
import api from './services/api';

// State
import { useStore } from './store';

// Auth
import { authService } from './services/auth.service';

// Components
import { GlowCard } from './components/magical/GlowCard';
import { MagicButton } from './components/magical/MagicButton';
```

---

## 🔥 Most Common Tasks

### 1. Deploy an Agent
```python
# Backend
orchestrator = AgentOrchestrator(user)
await orchestrator.deploy_single_agent("Business Agent", "create business plan")
```

### 2. Send AI Chat Message
```python
# Backend
service = PersonalAIService()
response = await service.chat("Hello", user)
```

### 3. Generate AI Image
```python
# Backend - Asset Gallery
from content.views_unified import UnifiedGenerateView
# Or in code:
from content.models import GeneratedImage
image = GeneratedImage.objects.create(
    user=user,
    prompt="A futuristic office",
    style="cyberpunk",
    image_url=generated_url
)
```

### 4. Check Agent Status
```python
# Get active agents
agents = AgentInstance.objects.filter(
    orchestration__user=user,
    current_status__in=['working', 'initializing']
)
```

### 5. Make Authenticated API Call
```dart
// Flutter
final headers = await ApiService.getAuthHeaders();
final response = await http.get(uri, headers: headers);
```

### 6. Handle Async Django ORM
```python
# Always wrap in sync_to_async
from asgiref.sync import sync_to_async
result = await sync_to_async(Model.objects.get)(id=1)
```

---

💡 **Pro Tip**: Keep this file open in a split screen while coding!