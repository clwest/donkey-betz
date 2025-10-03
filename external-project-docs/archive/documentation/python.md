# Python API Examples

This guide provides Python examples for interacting with the Donkey Betz API using the `requests` library.

## Installation

```bash
pip install requests
```

## Complete Example Client

```python
import requests
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class DonkeyBetzClient:
    """Python client for Donkey Betz API"""
    
    def __init__(self, base_url: str = "https://api.donkeybetz.com"):
        self.base_url = base_url.rstrip('/')
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with automatic token refresh"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers
            
        # Check if token needs refresh
        if self.token_expiry and datetime.now() >= self.token_expiry - timedelta(minutes=5):
            self.refresh_access_token()
            
        response = requests.request(method, url, **kwargs)
        
        # Handle 401 by refreshing token
        if response.status_code == 401 and self.refresh_token:
            self.refresh_access_token()
            # Retry request with new token
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers
            response = requests.request(method, url, **kwargs)
            
        response.raise_for_status()
        return response
    
    def register(self, email: str, password: str, username: str) -> Dict:
        """Register a new user"""
        data = {
            'email': email,
            'password1': password,
            'password2': password,
            'username': username
        }
        response = self._make_request('POST', '/api/auth/registration/', json=data)
        result = response.json()
        self._store_tokens(result)
        return result
    
    def login(self, email: str, password: str, two_factor_token: Optional[str] = None) -> Dict:
        """Login and store tokens"""
        data = {'email': email, 'password': password}
        if two_factor_token:
            data['two_factor_token'] = two_factor_token
            
        response = self._make_request('POST', '/api/auth/login/', json=data)
        result = response.json()
        self._store_tokens(result)
        return result
    
    def _store_tokens(self, token_data: Dict):
        """Store tokens from login/register response"""
        self.access_token = token_data.get('access')
        self.refresh_token = token_data.get('refresh')
        # Access tokens are valid for 8 hours
        self.token_expiry = datetime.now() + timedelta(hours=8)
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token"""
        if not self.refresh_token:
            return False
            
        try:
            response = self._make_request(
                'POST', 
                '/api/auth/token/refresh/', 
                json={'refresh': self.refresh_token}
            )
            result = response.json()
            self.access_token = result['access']
            self.token_expiry = datetime.now() + timedelta(hours=8)
            return True
        except:
            return False
    
    def logout(self):
        """Logout and clear tokens"""
        try:
            self._make_request('POST', '/api/auth/logout/')
        except:
            pass
        finally:
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
    
    # Profile Management
    def get_profile(self) -> Dict:
        """Get user profile"""
        response = self._make_request('GET', '/api/user/profile/')
        return response.json()
    
    def update_profile(self, **kwargs) -> Dict:
        """Update user profile"""
        response = self._make_request('PUT', '/api/user/profile/', json=kwargs)
        return response.json()
    
    # AI Agent Methods
    def execute_task(self, task_description: str, task_type: str = 'general') -> Dict:
        """Execute a task with AI agents"""
        data = {
            'task_description': task_description,
            'task_type': task_type
        }
        response = self._make_request('POST', '/api/agent-orchestra/execute/', json=data)
        return response.json()
    
    def get_orchestration_status(self, orchestration_id: str) -> Dict:
        """Check status of an orchestration"""
        response = self._make_request('GET', f'/api/agent-orchestra/orchestrations/{orchestration_id}/')
        return response.json()
    
    def deploy_reddit_scout(self, subreddits: Optional[list] = None, keywords: Optional[list] = None) -> Dict:
        """Deploy Reddit Scout agent"""
        data = {}
        if subreddits:
            data['subreddits'] = subreddits
        if keywords:
            data['keywords'] = keywords
            
        response = self._make_request('POST', '/api/agent-orchestra/reddit/scout/', json=data)
        return response.json()
    
    # Stock Intelligence
    def analyze_stock(self, ticker: str, analysis_type: str = 'comprehensive') -> Dict:
        """Analyze a stock"""
        data = {
            'ticker': ticker,
            'analysis_type': analysis_type,
            'include_technical': True,
            'include_fundamental': True,
            'include_sentiment': True
        }
        response = self._make_request('POST', '/api/agent-orchestra/stocks/analyze/', json=data)
        return response.json()
    
    def get_stock_quote(self, ticker: str) -> Dict:
        """Get real-time stock quote"""
        response = self._make_request('GET', f'/api/agent-orchestra/stocks/quote/{ticker}/')
        return response.json()
    
    # Memory Palace
    def chat_with_ai(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """Chat with personal AI"""
        data = {'message': message}
        if conversation_id:
            data['conversation_id'] = conversation_id
            
        response = self._make_request('POST', '/api/ai-partner/chat/', json=data)
        return response.json()
    
    def search_memories(self, query: str, limit: int = 10) -> Dict:
        """Search through memories"""
        data = {
            'query': query,
            'limit': limit,
            'threshold': 0.7
        }
        response = self._make_request('POST', '/api/ai-partner/memory/search/', json=data)
        return response.json()
    
    # Content Generation
    def generate_image(self, prompt: str, style: str = 'realistic', model: str = 'dall-e-3') -> Dict:
        """Generate an AI image"""
        data = {
            'prompt': prompt,
            'style': style,
            'model': model,
            'size': '1024x1024'
        }
        response = self._make_request('POST', '/api/content/images/generate/', json=data)
        return response.json()
    
    def get_image_status(self, task_id: str) -> Dict:
        """Check image generation status"""
        response = self._make_request('GET', f'/api/content/images/status/{task_id}/')
        return response.json()
    
    # Business Builder
    def generate_business(self, idea: str, name: str, target_audience: str) -> Dict:
        """Generate a complete business"""
        data = {
            'business_idea': idea,
            'business_name': name,
            'target_audience': target_audience,
            'features': ['landing_page', 'backend_api', 'database', 'documentation']
        }
        response = self._make_request('POST', '/api/universal-builder/generate/', json=data)
        return response.json()


# Example Usage
if __name__ == "__main__":
    # Initialize client
    client = DonkeyBetzClient(base_url="http://localhost:8000")
    
    # Login
    try:
        login_result = client.login("user@example.com", "SecurePassword123!")
        print(f"Logged in as: {login_result['user']['email']}")
    except requests.HTTPError as e:
        print(f"Login failed: {e}")
        exit(1)
    
    # Get profile
    profile = client.get_profile()
    print(f"Username: {profile['username']}")
    
    # Execute a task
    task = client.execute_task(
        "Analyze the current AI startup landscape and identify emerging opportunities",
        task_type="research"
    )
    print(f"Task created: {task['orchestration_id']}")
    
    # Check task status
    import time
    while True:
        status = client.get_orchestration_status(task['orchestration_id'])
        print(f"Status: {status['overall_status']} - Progress: {status['progress']}%")
        
        if status['overall_status'] in ['completed', 'failed']:
            break
            
        time.sleep(5)
    
    # Chat with AI
    chat_response = client.chat_with_ai("What startup ideas have I explored recently?")
    print(f"AI: {chat_response['response']}")
    
    # Search memories
    memories = client.search_memories("startup ideas")
    print(f"Found {len(memories['results'])} relevant memories")
    
    # Generate an image
    image = client.generate_image(
        prompt="A futuristic donkey wearing VR goggles, building a tech startup",
        style="digital-art"
    )
    print(f"Image generation started: {image['task_id']}")
    
    # Analyze a stock
    stock_analysis = client.analyze_stock("AAPL")
    print(f"Stock analysis: {stock_analysis['orchestration_id']}")
    
    # Logout
    client.logout()
    print("Logged out successfully")
```

## Async Example with aiohttp

```python
import aiohttp
import asyncio
from typing import Dict, Optional


class AsyncDonkeyBetzClient:
    """Async Python client for Donkey Betz API"""
    
    def __init__(self, base_url: str = "https://api.donkeybetz.com"):
        self.base_url = base_url.rstrip('/')
        self.access_token = None
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        
    async def login(self, email: str, password: str) -> Dict:
        """Async login"""
        async with self.session.post(
            f"{self.base_url}/api/auth/login/",
            json={'email': email, 'password': password}
        ) as response:
            data = await response.json()
            self.access_token = data['access']
            return data
            
    async def execute_multiple_tasks(self, tasks: list) -> list:
        """Execute multiple tasks concurrently"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        async def execute_one(task):
            async with self.session.post(
                f"{self.base_url}/api/agent-orchestra/execute/",
                json=task,
                headers=headers
            ) as response:
                return await response.json()
                
        results = await asyncio.gather(*[execute_one(task) for task in tasks])
        return results


# Async usage example
async def main():
    async with AsyncDonkeyBetzClient() as client:
        # Login
        await client.login("user@example.com", "SecurePassword123!")
        
        # Execute multiple tasks concurrently
        tasks = [
            {
                'task_description': 'Analyze AAPL stock',
                'task_type': 'stock_analysis'
            },
            {
                'task_description': 'Research AI trends in healthcare',
                'task_type': 'research'
            },
            {
                'task_description': 'Find trending startup ideas on Reddit',
                'task_type': 'reddit_scout'
            }
        ]
        
        results = await client.execute_multiple_tasks(tasks)
        for i, result in enumerate(results):
            print(f"Task {i+1}: {result['orchestration_id']}")


if __name__ == "__main__":
    asyncio.run(main())
```

## WebSocket Example

```python
import asyncio
import websockets
import json


async def monitor_agent_activity(orchestration_id: str, access_token: str):
    """Monitor agent activity via WebSocket"""
    uri = f"wss://api.donkeybetz.com/ws/agent-activity/{orchestration_id}/"
    
    async with websockets.connect(
        uri,
        extra_headers={"Authorization": f"Bearer {access_token}"}
    ) as websocket:
        print(f"Connected to WebSocket for orchestration {orchestration_id}")
        
        async for message in websocket:
            data = json.loads(message)
            event_type = data.get('type')
            
            if event_type == 'agent_started':
                print(f"Agent {data['agent_name']} started")
            elif event_type == 'agent_progress':
                print(f"Progress: {data['progress']}% - {data['message']}")
            elif event_type == 'agent_completed':
                print(f"Agent completed: {data['agent_name']}")
                print(f"Result: {json.dumps(data['result'], indent=2)}")
            elif event_type == 'orchestration_completed':
                print("Orchestration completed!")
                break
                
                
# Usage
asyncio.run(monitor_agent_activity("orchestration-id", "your-access-token"))
```

## Error Handling Example

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def create_session_with_retries():
    """Create a session with automatic retries"""
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def safe_api_call(func):
    """Decorator for safe API calls with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                retry_after = e.response.headers.get('Retry-After', '60')
                print(f"Rate limited. Retry after {retry_after} seconds")
            elif e.response.status_code == 401:
                print("Authentication failed. Please login again.")
            elif e.response.status_code == 403:
                print("Permission denied.")
            else:
                print(f"HTTP Error: {e}")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error. Please check your internet connection.")
            return None
        except requests.exceptions.Timeout:
            print("Request timed out.")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    return wrapper


@safe_api_call
def get_user_profile(access_token: str):
    """Safely get user profile"""
    session = create_session_with_retries()
    response = session.get(
        'https://api.donkeybetz.com/api/user/profile/',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10
    )
    response.raise_for_status()
    return response.json()
```

## Pagination Example

```python
def get_all_orchestrations(client: DonkeyBetzClient) -> list:
    """Get all orchestrations with pagination"""
    all_results = []
    page = 1
    
    while True:
        response = client._make_request(
            'GET',
            f'/api/agent-orchestra/orchestrations/?page={page}&page_size=50'
        )
        data = response.json()
        
        all_results.extend(data['results'])
        
        if not data['next']:
            break
            
        page += 1
        
    return all_results
```

## File Upload Example

```python
def upload_document(client: DonkeyBetzClient, file_path: str) -> Dict:
    """Upload a document to Memory Palace"""
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
        response = client._make_request(
            'POST',
            '/api/ai-partner/document-ingestion/upload-file/',
            files=files
        )
    return response.json()
```