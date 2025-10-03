# AI-First Asset Library API Documentation

## Overview

The AI-First Asset Library API provides endpoints for generating, managing, and organizing AI-created assets including logos, brand colors, marketing materials, and more. All assets are generated through AI rather than uploaded by users.

## Authentication

All endpoints require authentication using Django REST Framework's token authentication.

**Header Format:**
```
Authorization: Token YOUR_AUTH_TOKEN
```

## Base URL

```
http://localhost:8000/api/content/
```

## API Endpoints

### 1. Asset Generation

#### Generate Assets
Start AI generation of assets with variations.

**Endpoint:** `POST /api/content/assets/generation/generate/`

**Request Body:**
```json
{
  "asset_type": "logo",  // Required: logo, brand_colors, typography, marketing, product_visual, social_media
  "style": "modern",     // Optional: modern, bold, elegant, playful, professional
  "custom_prompt": "Tech startup logo with abstract geometric shapes", // Optional
  "variations": 3,       // Optional: 1, 3, 5, or 10 (default: 3)
  "brand_identity_id": 1 // Optional: Use specific brand identity
}
```

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "asset_type": "logo",
  "status": "pending",
  "progress": 0,
  "variations": 3,
  "prompt_used": "modern style tech startup logo with abstract geometric shapes",
  "created_at": "2025-08-02T10:00:00Z",
  "completed_at": null,
  "error_message": null
}
```

#### Check Generation Status
Monitor the progress of asset generation.

**Endpoint:** `GET /api/content/assets/generation/{id}/status/`

**Response:**
```json
{
  "id": 1,
  "status": "completed",  // pending, queued, generating, completed, failed
  "progress": 100,
  "generated_assets": [
    {
      "id": 1,
      "asset_url": "https://example.com/asset1.png",
      "thumbnail_url": "https://example.com/asset1_thumb.png",
      "quality_score": 0.92,
      "brand_compliance_score": 0.85,
      "is_selected": false
    }
  ]
}
```

#### Select Variation
Choose one variation from the generated options.

**Endpoint:** `POST /api/content/assets/generation/{id}/select-variation/`

**Request Body:**
```json
{
  "asset_id": 1,
  "create_upload": true  // Optional: Create UserUpload entry (default: true)
}
```

### 2. Brand Identity Management

#### List Brand Identities
Get all brand identities for the authenticated user.

**Endpoint:** `GET /api/content/brand-identity/`

#### Create Brand Identity
Define brand guidelines for AI generation.

**Endpoint:** `POST /api/content/brand-identity/`

**Request Body:**
```json
{
  "name": "Tech Startup Brand",
  "colors": {
    "primary": "#1E40AF",
    "secondary": "#EAB308",
    "accent": "#DC2626",
    "usage": {
      "primary": "Main brand color for logos and headers",
      "secondary": "Call-to-action buttons and highlights"
    }
  },
  "typography": {
    "heading": "Helvetica",
    "body": "Arial",
    "sizes": {
      "h1": "48px",
      "h2": "36px",
      "body": "16px"
    }
  },
  "tone_of_voice": {
    "style": "Professional yet friendly",
    "keywords": ["innovative", "reliable", "modern", "approachable"],
    "avoid": ["corporate jargon", "overly casual"]
  },
  "visual_style": "modern",  // modern, classic, playful, minimal, bold
  "generation_preferences": {
    "include_text": false,
    "prefer_abstract": true,
    "color_scheme": "vibrant"
  },
  "is_active": true  // Set as the active brand identity
}
```

#### Get Active Brand Identity
Retrieve the currently active brand identity.

**Endpoint:** `GET /api/content/brand-identity/active/`

#### Refine Brand Identity
Update specific aspects of brand guidelines.

**Endpoint:** `PUT /api/content/brand-identity/{id}/refine/`

**Request Body:**
```json
{
  "refinements": {
    "colors": {
      "primary": "#2563EB"  // Update primary color
    },
    "visual_style": "minimal",
    "tone": {
      "keywords": ["cutting-edge", "sustainable"]
    }
  }
}
```

### 3. Asset Gallery

#### List Assets
Get all assets with filtering and search capabilities.

**Endpoint:** `GET /api/content/assets/`

**Query Parameters:**
- `ai_only=true` - Show only AI-generated assets
- `category=logo` - Filter by category (logo, brand_colors, typography, marketing, product_visual, social_media)
- `min_compliance=70` - Minimum brand compliance score (0-100)
- `search=startup` - Search in title, description, and generation prompt
- `order_by=-created_at` - Sort order (prefix with - for descending)

**Response:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/content/assets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern Tech Logo",
      "file_url": "https://example.com/logo.png",
      "file_type": "png",
      "category": "logo",
      "is_ai_generated": true,
      "generation_prompt": "modern tech startup logo",
      "brand_compliance_score": 85.5,
      "quality_score": 92.0,
      "created_at": "2025-08-02T10:00:00Z",
      "ai_asset": {
        "id": 1,
        "generation_model": "dall-e-3",
        "generation_parameters": {...}
      }
    }
  ]
}
```

#### Get AI-Generated Assets Only
List only AI-generated assets with additional filtering.

**Endpoint:** `GET /api/content/assets/ai-generated/`

**Query Parameters:**
- `selected_only=true` - Show only selected variations
- `days=7` - Assets created in the last N days

#### Approve Asset
Approve an asset for shared use across the organization.

**Endpoint:** `POST /api/content/assets/{id}/approve/`

**Response:**
```json
{
  "message": "Asset approved for shared use",
  "shared_asset_id": 1
}
```

#### Delete Asset
Remove an asset and its associated AI generation data.

**Endpoint:** `DELETE /api/content/assets/{id}/`

### 4. Quota Management

#### Get Quota Status
Check current generation limits and availability.

**Endpoint:** `GET /api/content/quota/status/`

**Response:**
```json
{
  "quota": {
    "id": 1,
    "tier": "pro",
    "credits_remaining": 450,
    "daily_limit": 50,
    "daily_used": 5,
    "monthly_limit": 1000,
    "monthly_used": 150,
    "reset_date": "2025-09-01T00:00:00Z"
  },
  "availability": {
    "logo": {
      "can_generate": true,
      "credits_needed": 5,
      "remaining_today": 45,
      "remaining_monthly": 850
    },
    "marketing": {
      "can_generate": true,
      "credits_needed": 3,
      "remaining_today": 45,
      "remaining_monthly": 850
    }
  },
  "tier_limits": {
    "daily_limit": 50,
    "monthly_limit": 1000,
    "credits_per_asset": {
      "logo": 5,
      "brand_colors": 2,
      "marketing": 3
    }
  }
}
```

#### Get Usage Statistics
View detailed usage analytics.

**Endpoint:** `GET /api/content/quota/usage/`

**Response:**
```json
{
  "daily_usage": 5,
  "weekly_usage": 25,
  "monthly_usage": 150,
  "usage_by_type": [
    {
      "asset_type": "logo",
      "count": 50,
      "avg_variations": 3.5
    }
  ],
  "success_rate": 94.5,
  "total_generations": 250
}
```

#### Add Credits
Add credits to user's quota (admin use).

**Endpoint:** `POST /api/content/quota/add-credits/`

**Request Body:**
```json
{
  "credits": 100,
  "description": "Monthly bonus credits"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error type",
  "details": "Detailed error message",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid data)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (quota exceeded)
- `500` - Internal Server Error

## Integration Examples

### JavaScript/TypeScript

```typescript
// Generate logo with variations
const generateLogo = async (authToken: string) => {
  const response = await fetch('http://localhost:8000/api/content/assets/generation/generate/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${authToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      asset_type: 'logo',
      style: 'modern',
      variations: 3,
      custom_prompt: 'Minimalist tech startup logo'
    })
  });
  
  const data = await response.json();
  return data;
};

// Poll for generation status
const checkStatus = async (authToken: string, requestId: number) => {
  const response = await fetch(
    `http://localhost:8000/api/content/assets/generation/${requestId}/status/`,
    {
      headers: {
        'Authorization': `Token ${authToken}`
      }
    }
  );
  
  const data = await response.json();
  return data;
};
```

### Python

```python
import requests

# Setup headers
headers = {
    'Authorization': f'Token {auth_token}',
    'Content-Type': 'application/json'
}

# Create brand identity
brand_data = {
    'name': 'My Brand',
    'colors': {
        'primary': '#1E40AF',
        'secondary': '#EAB308'
    },
    'visual_style': 'modern',
    'is_active': True
}

response = requests.post(
    'http://localhost:8000/api/content/brand-identity/',
    headers=headers,
    json=brand_data
)

brand_id = response.json()['id']
```

## Rate Limits

- Asset generation is limited by user quota/tier
- API calls are limited to 1000 requests per hour per user
- Concurrent generation requests are limited to 3 per user

## Best Practices

1. **Always check quota before generation** - Use `/quota/status/` to verify availability
2. **Poll status endpoint** - Check every 2-5 seconds for generation completion
3. **Cache brand identity** - Retrieve active brand once and cache locally
4. **Handle errors gracefully** - Implement retry logic for transient failures
5. **Use appropriate variations** - More variations consume more credits

## Migration from Upload-Based System

For existing users migrating from the upload-based system:

1. Existing uploads remain accessible through the same endpoints
2. Set `ai_only=false` to see both uploaded and AI-generated assets
3. Use the `category` field to organize existing uploads
4. Brand compliance scores are calculated for existing assets

## Support

For API issues or questions:
- Check error responses for detailed messages
- Review quota limits if generation fails
- Ensure brand identity is set for consistent results