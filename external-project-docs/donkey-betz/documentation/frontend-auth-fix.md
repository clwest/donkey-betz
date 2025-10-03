# Frontend Authentication Fix Guide for donkey-betz-frontend

## 1. API Path Updates

Run the provided script: `./fix_frontend_pipeline_paths.sh` from the donkey-betz-frontend directory.

## 2. Authentication Header Implementation

### Find your API service/utility file
Look for files like:
- `src/services/api.js` or `api.ts`
- `src/utils/api.js` or `api.ts`
- `src/lib/api.js` or `api.ts`
- `src/api/index.js` or `index.ts`

### Add Authentication Headers

#### If using Axios:
```javascript
// src/services/api.js (or similar)
import axios from 'axios';

// Create axios instance with auth
const api = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default api;
```

#### If using Fetch:
```javascript
// src/utils/api.js
export const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('authToken');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders.Authorization = `Token ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    }
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
};
```

### 3. Update Pipeline Service

Find your pipeline service file (might be named):
- `src/services/pipelineService.js`
- `src/api/pipeline.js`
- `src/stores/pipeline.js` (if using Pinia/Vuex)

Update it to use the authenticated API:

```javascript
// Example pipeline service
import api from '@/services/api'; // or your api utility

export const pipelineService = {
  // Get all pipelines
  async getPipelines() {
    const response = await api.get('/api/pipeline/pipelines/');
    return response.data;
  },

  // Get available AI content
  async getAvailableContent() {
    const response = await api.get('/api/content/ai-pipeline/available_content/');
    return response.data;
  },

  // Create pipeline
  async createPipeline(data) {
    const response = await api.post('/api/pipeline/pipelines/', data);
    return response.data;
  },

  // Link content to pipeline
  async linkContent(pipelineId, contentData) {
    const response = await api.post('/api/content/ai-pipeline/link_to_pipeline/', {
      pipeline_id: pipelineId,
      ...contentData
    });
    return response.data;
  }
};
```

### 4. Check Token Storage

Make sure your login flow saves the token:

```javascript
// In your login handler
async function login(credentials) {
  try {
    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials)
    });
    
    const data = await response.json();
    
    if (data.key || data.token) {
      // Django REST framework returns 'key'
      localStorage.setItem('authToken', data.key || data.token);
    }
    
    return data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}
```

### 5. Components to Update

Look for components that might be calling the pipeline API:
- ContentStudio component
- PipelineDashboard component
- Any component with "pipeline" in the name

### 6. Testing Checklist

1. Clear localStorage: `localStorage.clear()`
2. Log in fresh to get a new token
3. Check Network tab in DevTools
4. Verify Authorization header is present: `Authorization: Token xxxxx`
5. Check all API calls return 200/201 status

### 7. Common File Patterns to Check

```bash
# Run these from donkey-betz-frontend directory

# Find API configuration files
find src -name "*api*" -type f | grep -E "\.(js|ts)$"

# Find pipeline-related files
find src -name "*pipeline*" -type f | grep -E "\.(js|ts|vue|jsx|tsx)$"

# Find service files
find src -path "*/services/*" -type f | grep -E "\.(js|ts)$"

# Find store files (Vue/Pinia)
find src -path "*/store*/*" -type f | grep -E "\.(js|ts)$"

# Check for axios or fetch usage
grep -r "axios\|fetch(" src/ --include="*.js" --include="*.ts" --include="*.vue"
```