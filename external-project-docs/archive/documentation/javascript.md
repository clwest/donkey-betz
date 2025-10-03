# JavaScript API Examples

This guide provides JavaScript/TypeScript examples for interacting with the Donkey Betz API.

## Complete Client Class

```javascript
class DonkeyBetzClient {
  constructor(baseUrl = 'https://api.donkeybetz.com') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
  }

  async makeRequest(method, endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Add auth header if token exists
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    // Check if token needs refresh (5 minutes before expiry)
    if (this.tokenExpiry && new Date() >= new Date(this.tokenExpiry - 5 * 60 * 1000)) {
      await this.refreshAccessToken();
    }

    try {
      const response = await fetch(url, {
        method,
        headers,
        ...options,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });

      // Handle 401 by refreshing token
      if (response.status === 401 && this.refreshToken) {
        await this.refreshAccessToken();
        // Retry with new token
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        const retryResponse = await fetch(url, {
          method,
          headers,
          ...options,
          body: options.body ? JSON.stringify(options.body) : undefined,
        });
        return this.handleResponse(retryResponse);
      }

      return this.handleResponse(response);
    } catch (error) {
      console.error('Request failed:', error);
      throw error;
    }
  }

  async handleResponse(response) {
    const data = await response.json();
    
    if (!response.ok) {
      throw {
        status: response.status,
        message: data.detail || data.message || 'Request failed',
        data
      };
    }
    
    return data;
  }

  storeTokens(tokenData) {
    this.accessToken = tokenData.access;
    this.refreshToken = tokenData.refresh;
    // Access tokens are valid for 8 hours
    this.tokenExpiry = new Date(Date.now() + 8 * 60 * 60 * 1000);
    
    // Store in localStorage for persistence (consider security implications)
    if (typeof window !== 'undefined') {
      localStorage.setItem('donkeybetz_access_token', this.accessToken);
      localStorage.setItem('donkeybetz_refresh_token', this.refreshToken);
    }
  }

  loadStoredTokens() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('donkeybetz_access_token');
      this.refreshToken = localStorage.getItem('donkeybetz_refresh_token');
    }
  }

  // Authentication Methods
  async register(email, password, username) {
    const data = await this.makeRequest('POST', '/api/auth/registration/', {
      body: {
        email,
        password1: password,
        password2: password,
        username
      }
    });
    this.storeTokens(data);
    return data;
  }

  async login(email, password, twoFactorToken = null) {
    const body = { email, password };
    if (twoFactorToken) {
      body.two_factor_token = twoFactorToken;
    }
    
    const data = await this.makeRequest('POST', '/api/auth/login/', { body });
    this.storeTokens(data);
    return data;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const data = await this.makeRequest('POST', '/api/auth/token/refresh/', {
        body: { refresh: this.refreshToken }
      });
      this.accessToken = data.access;
      this.tokenExpiry = new Date(Date.now() + 8 * 60 * 60 * 1000);
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('donkeybetz_access_token', this.accessToken);
      }
      
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout();
      return false;
    }
  }

  async logout() {
    try {
      await this.makeRequest('POST', '/api/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.accessToken = null;
      this.refreshToken = null;
      this.tokenExpiry = null;
      
      if (typeof window !== 'undefined') {
        localStorage.removeItem('donkeybetz_access_token');
        localStorage.removeItem('donkeybetz_refresh_token');
      }
    }
  }

  // Profile Management
  async getProfile() {
    return this.makeRequest('GET', '/api/user/profile/');
  }

  async updateProfile(updates) {
    return this.makeRequest('PUT', '/api/user/profile/', { body: updates });
  }

  // AI Agent Methods
  async executeTask(taskDescription, taskType = 'general') {
    return this.makeRequest('POST', '/api/agent-orchestra/execute/', {
      body: { task_description: taskDescription, task_type: taskType }
    });
  }

  async getOrchestrationStatus(orchestrationId) {
    return this.makeRequest('GET', `/api/agent-orchestra/orchestrations/${orchestrationId}/`);
  }

  async deployRedditScout(subreddits = null, keywords = null) {
    const body = {};
    if (subreddits) body.subreddits = subreddits;
    if (keywords) body.keywords = keywords;
    
    return this.makeRequest('POST', '/api/agent-orchestra/reddit/scout/', { body });
  }

  // Stock Intelligence
  async analyzeStock(ticker, analysisType = 'comprehensive') {
    return this.makeRequest('POST', '/api/agent-orchestra/stocks/analyze/', {
      body: {
        ticker,
        analysis_type: analysisType,
        include_technical: true,
        include_fundamental: true,
        include_sentiment: true
      }
    });
  }

  async getStockQuote(ticker) {
    return this.makeRequest('GET', `/api/agent-orchestra/stocks/quote/${ticker}/`);
  }

  // Memory Palace
  async chatWithAI(message, conversationId = null) {
    const body = { message };
    if (conversationId) body.conversation_id = conversationId;
    
    return this.makeRequest('POST', '/api/ai-partner/chat/', { body });
  }

  async searchMemories(query, limit = 10) {
    return this.makeRequest('POST', '/api/ai-partner/memory/search/', {
      body: { query, limit, threshold: 0.7 }
    });
  }

  // Content Generation
  async generateImage(prompt, style = 'realistic', model = 'dall-e-3') {
    return this.makeRequest('POST', '/api/content/images/generate/', {
      body: { prompt, style, model, size: '1024x1024' }
    });
  }

  async getImageStatus(taskId) {
    return this.makeRequest('GET', `/api/content/images/status/${taskId}/`);
  }

  // WebSocket connection
  connectWebSocket(endpoint, handlers) {
    const wsUrl = `wss://${this.baseUrl.replace('https://', '').replace('http://', '')}/ws/${endpoint}/`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      if (handlers.onOpen) handlers.onOpen();
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (handlers.onMessage) handlers.onMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (handlers.onError) handlers.onError(error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      if (handlers.onClose) handlers.onClose();
    };
    
    return ws;
  }
}

// Example usage
async function main() {
  const client = new DonkeyBetzClient('http://localhost:8000');
  
  try {
    // Login
    const loginResult = await client.login('user@example.com', 'SecurePassword123!');
    console.log('Logged in as:', loginResult.user.email);
    
    // Get profile
    const profile = await client.getProfile();
    console.log('Username:', profile.username);
    
    // Execute a task
    const task = await client.executeTask(
      'Analyze the current AI startup landscape',
      'research'
    );
    console.log('Task created:', task.orchestration_id);
    
    // Monitor task progress with WebSocket
    const ws = client.connectWebSocket(`agent-activity/${task.orchestration_id}`, {
      onMessage: (data) => {
        console.log('Progress:', data.progress + '%', data.message);
        if (data.type === 'orchestration_completed') {
          ws.close();
        }
      }
    });
    
    // Chat with AI
    const chatResponse = await client.chatWithAI('What are my recent projects?');
    console.log('AI:', chatResponse.response);
    
    // Generate an image
    const image = await client.generateImage(
      'A futuristic donkey coding on multiple screens',
      'cyberpunk'
    );
    console.log('Image task:', image.task_id);
    
    // Poll for image completion
    let imageStatus;
    do {
      await new Promise(resolve => setTimeout(resolve, 2000));
      imageStatus = await client.getImageStatus(image.task_id);
      console.log('Image status:', imageStatus.status);
    } while (imageStatus.status === 'processing');
    
    if (imageStatus.status === 'completed') {
      console.log('Image URL:', imageStatus.image_url);
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the example
main();
```

## React Hook Example

```jsx
import { useState, useEffect, useCallback } from 'react';

// Custom hook for Donkey Betz API
function useDonkeyBetz() {
  const [client, setClient] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiClient = new DonkeyBetzClient();
    apiClient.loadStoredTokens();
    
    // Check if stored tokens are valid
    if (apiClient.accessToken) {
      apiClient.getProfile()
        .then(() => setIsAuthenticated(true))
        .catch(() => setIsAuthenticated(false))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
    
    setClient(apiClient);
  }, []);

  const login = useCallback(async (email, password) => {
    if (!client) return;
    
    try {
      await client.login(email, password);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, [client]);

  const logout = useCallback(async () => {
    if (!client) return;
    
    await client.logout();
    setIsAuthenticated(false);
  }, [client]);

  return {
    client,
    isAuthenticated,
    loading,
    login,
    logout
  };
}

// React component example
function AgentOrchestra() {
  const { client, isAuthenticated } = useDonkeyBetz();
  const [orchestrations, setOrchestrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [taskInput, setTaskInput] = useState('');

  const executeTask = async () => {
    if (!client || !taskInput) return;
    
    setLoading(true);
    try {
      const result = await client.executeTask(taskInput);
      
      // Start WebSocket monitoring
      const ws = client.connectWebSocket(`agent-activity/${result.orchestration_id}`, {
        onMessage: (data) => {
          // Update orchestration in state
          setOrchestrations(prev => 
            prev.map(o => 
              o.id === result.orchestration_id 
                ? { ...o, progress: data.progress, status: data.type }
                : o
            )
          );
        }
      });
      
      // Add to orchestrations list
      setOrchestrations(prev => [...prev, {
        id: result.orchestration_id,
        task: taskInput,
        progress: 0,
        status: 'started',
        ws
      }]);
      
      setTaskInput('');
    } catch (error) {
      console.error('Task execution failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Cleanup WebSocket connections on unmount
  useEffect(() => {
    return () => {
      orchestrations.forEach(o => o.ws?.close());
    };
  }, [orchestrations]);

  if (!isAuthenticated) {
    return <div>Please login to use Agent Orchestra</div>;
  }

  return (
    <div>
      <h2>Agent Orchestra</h2>
      
      <div>
        <input
          type="text"
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          placeholder="Describe your task..."
          disabled={loading}
        />
        <button onClick={executeTask} disabled={loading || !taskInput}>
          Execute Task
        </button>
      </div>
      
      <div>
        <h3>Active Orchestrations</h3>
        {orchestrations.map(o => (
          <div key={o.id}>
            <h4>{o.task}</h4>
            <progress value={o.progress} max="100" />
            <span>{o.progress}% - {o.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## TypeScript Types

```typescript
// types.ts
export interface User {
  id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface Orchestration {
  orchestration_id: string;
  task_description: string;
  task_type: string;
  overall_status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface AgentResult {
  agent_id: string;
  agent_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

export interface MemorySearchResult {
  id: string;
  content: string;
  similarity_score: number;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface GeneratedImage {
  id: string;
  prompt: string;
  image_url: string;
  style: string;
  model: string;
  created_at: string;
}

// client.ts - TypeScript version
export class DonkeyBetzClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiry: Date | null = null;

  constructor(baseUrl: string = 'https://api.donkeybetz.com') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    // Implementation
  }

  async executeTask(
    taskDescription: string, 
    taskType: string = 'general'
  ): Promise<Orchestration> {
    // Implementation
  }

  async searchMemories(
    query: string, 
    limit: number = 10
  ): Promise<{ results: MemorySearchResult[] }> {
    // Implementation
  }
}
```

## Next.js API Route Example

```javascript
// pages/api/donkeybetz/[...path].js
// Proxy API route for server-side requests

export default async function handler(req, res) {
  const { path } = req.query;
  const apiPath = Array.isArray(path) ? path.join('/') : path;
  
  // Get token from secure HTTP-only cookie
  const token = req.cookies.donkeybetz_token;
  
  if (!token) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  
  try {
    const response = await fetch(
      `${process.env.DONKEYBETZ_API_URL}/api/${apiPath}`,
      {
        method: req.method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
      }
    );
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ error: 'API request failed' });
  }
}
```

## File Upload Example

```javascript
async function uploadDocument(file) {
  const client = new DonkeyBetzClient();
  
  // Create FormData
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', file.name);
  
  // Make upload request
  const response = await fetch(`${client.baseUrl}/api/ai-partner/document-ingestion/upload-file/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${client.accessToken}`
      // Don't set Content-Type, let browser set it with boundary
    },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Upload failed');
  }
  
  return response.json();
}

// React component for file upload
function DocumentUploader() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setUploading(true);
    
    try {
      const result = await uploadDocument(file);
      console.log('Document uploaded:', result);
      
      // Poll for processing status
      const checkStatus = setInterval(async () => {
        const status = await client.makeRequest('GET', `/api/ai-partner/documents/${result.id}/status/`);
        setProgress(status.progress);
        
        if (status.status === 'completed') {
          clearInterval(checkStatus);
          setUploading(false);
          alert('Document processed successfully!');
        }
      }, 1000);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploading(false);
    }
  };
  
  return (
    <div>
      <input
        type="file"
        onChange={handleFileSelect}
        disabled={uploading}
        accept=".pdf,.doc,.docx,.txt,.md"
      />
      {uploading && (
        <div>
          <progress value={progress} max="100" />
          <span>{progress}%</span>
        </div>
      )}
    </div>
  );
}
```

## Error Handling and Retry Logic

```javascript
class ResilientDonkeyBetzClient extends DonkeyBetzClient {
  async makeRequestWithRetry(method, endpoint, options = {}, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await this.makeRequest(method, endpoint, options);
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx)
        if (error.status >= 400 && error.status < 500) {
          throw error;
        }
        
        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
        console.log(`Retry attempt ${attempt + 1} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError;
  }
  
  // Override methods to use retry logic
  async executeTask(taskDescription, taskType = 'general') {
    return this.makeRequestWithRetry('POST', '/api/agent-orchestra/execute/', {
      body: { task_description: taskDescription, task_type: taskType }
    });
  }
}
```