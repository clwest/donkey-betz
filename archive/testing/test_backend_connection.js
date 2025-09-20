
// Save this as: frontend/src/utils/testBackendConnection.ts

export async function testBackendConnection() {
  const API_BASE = 'http://localhost:8000';
  const TOKEN = localStorage.getItem('authToken') || '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';

  const endpoints = [
    '/api/v1/agents/templates/',
    '/api/v1/intelligence/opportunities/',
    '/api/v1/intelligence/revenue/',
  ];

  const results = {};

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Authorization': `Token ${TOKEN}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      results[endpoint] = {
        success: response.ok,
        status: response.status,
        hasData: !!data,
        dataKeys: Object.keys(data || {})
      };

      console.log(`✅ ${endpoint}:`, results[endpoint]);
    } catch (error) {
      results[endpoint] = { success: false, error: error.message };
      console.error(`❌ ${endpoint}:`, error);
    }
  }

  return results;
}

// Call this from browser console:
// await testBackendConnection()
