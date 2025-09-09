/**
 * API Integration Test Suite
 * Tests shared API functionality across platforms
 */

import { apiClient } from '../api/client';
import { API_CONFIG, ENDPOINTS } from '../api/config';
import { 
  contentService,
  videoService,
  voiceService,
  stabilityService
} from '../services/content.service.refactored';

// Test configuration
const TEST_CONFIG = {
  timeout: 10000,
  authToken: '993f8273f70877e23b5c7d2f92ed30562a089fe3',
  testPrompt: 'A beautiful sunset over mountains',
  testTopic: 'Technology trends in 2025',
};

// Color codes for output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
};

// Test result tracking
interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  time?: number;
}

const results: TestResult[] = [];

// Helper functions
function log(message: string, color: keyof typeof colors = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTestStart(name: string) {
  log(`\n▶ Testing: ${name}`, 'blue');
}

function logTestResult(name: string, passed: boolean, error?: string, time?: number) {
  const status = passed ? '✅ PASS' : '❌ FAIL';
  const color = passed ? 'green' : 'red';
  log(`${status}: ${name}${time ? ` (${time}ms)` : ''}`, color);
  if (error) {
    log(`  Error: ${error}`, 'red');
  }
  results.push({ name, passed, error, time });
}

async function testWithTimeout<T>(
  name: string,
  testFn: () => Promise<T>,
  timeout: number = TEST_CONFIG.timeout
): Promise<T | null> {
  logTestStart(name);
  const start = Date.now();
  
  try {
    const result = await Promise.race([
      testFn(),
      new Promise<never>((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), timeout)
      ),
    ]);
    
    const time = Date.now() - start;
    logTestResult(name, true, undefined, time);
    return result;
  } catch (error: any) {
    const time = Date.now() - start;
    logTestResult(name, false, error.message || 'Unknown error', time);
    return null;
  }
}

// Test suites
async function testAPIConnection() {
  return testWithTimeout('API Connection', async () => {
    const response = await apiClient.get('/health/', {
      validateStatus: () => true,
    });
    
    if (!response) {
      throw new Error('No response from API');
    }
    
    return response.data;
  });
}

async function testAuthentication() {
  return testWithTimeout('Authentication', async () => {
    const response = await apiClient.get('/auth/profile/', {
      headers: {
        Authorization: `Token ${TEST_CONFIG.authToken}`,
      },
      validateStatus: () => true,
    });
    
    if (response.status === 401) {
      throw new Error('Authentication failed');
    }
    
    return response.data;
  });
}

async function testContentGeneration() {
  return testWithTimeout('Content Generation - Text', async () => {
    const result = await contentService.generateText({
      prompt: TEST_CONFIG.testPrompt,
      max_tokens: 100,
    });
    
    if (!result) {
      throw new Error('No content generated');
    }
    
    return result;
  });
}

async function testImageGeneration() {
  return testWithTimeout('Content Generation - Image', async () => {
    const result = await contentService.generateImage({
      prompt: TEST_CONFIG.testPrompt,
      style: 'photorealistic',
      width: 512,
      height: 512,
    });
    
    if (!result || !result.images) {
      throw new Error('No images generated');
    }
    
    return result;
  }, 30000); // 30 seconds for image generation
}

async function testBlogGeneration() {
  return testWithTimeout('Blog Generation', async () => {
    const result = await contentService.generateBlog({
      topic: TEST_CONFIG.testTopic,
      tone: 'professional',
      length: 'short',
    });
    
    if (!result || !result.content) {
      throw new Error('No blog content generated');
    }
    
    return result;
  }, 60000); // 60 seconds for blog generation
}

async function testGalleryFetch() {
  return testWithTimeout('Gallery Fetch', async () => {
    const result = await contentService.getGallery(1, 10);
    
    if (!result) {
      throw new Error('Failed to fetch gallery');
    }
    
    return result;
  });
}

async function testDashboardStats() {
  return testWithTimeout('Dashboard Statistics', async () => {
    const response = await apiClient.get(ENDPOINTS.ADMIN.DASHBOARD + 'stats/');
    
    if (!response.data) {
      throw new Error('No dashboard data');
    }
    
    return response.data;
  });
}

async function testVideoStatusCheck() {
  return testWithTimeout('Video Status Check', async () => {
    // Test with a dummy task ID
    const result = await videoService.checkStatus('test-task-id').catch(err => {
      // Expected to fail with 404, but should handle gracefully
      if (err.originalError?.response?.status === 404) {
        return { status: 'not_found' };
      }
      throw err;
    });
    
    return result;
  });
}

async function testErrorHandling() {
  return testWithTimeout('Error Handling - 404', async () => {
    try {
      await apiClient.get('/nonexistent-endpoint/');
      throw new Error('Should have thrown 404 error');
    } catch (error: any) {
      if (error.originalError?.response?.status === 404) {
        return { handled: true, status: 404 };
      }
      throw new Error('Error not properly handled');
    }
  });
}

async function testBatchRequest() {
  return testWithTimeout('Batch Image Generation', async () => {
    const result = await contentService.batchGenerate({
      prompt: TEST_CONFIG.testPrompt,
      batch_size: 2,
      style: 'artistic',
    });
    
    if (!result || !result.images) {
      throw new Error('Batch generation failed');
    }
    
    return result;
  }, 45000); // 45 seconds for batch
}

// Main test runner
export async function runAPITests() {
  log('\n' + '='.repeat(50), 'blue');
  log('🧪 API INTEGRATION TEST SUITE', 'blue');
  log('='.repeat(50), 'blue');
  log(`\nTarget: ${API_CONFIG.BASE_URL}`, 'yellow');
  log(`Platform: ${typeof window !== 'undefined' ? 'Web' : 'React Native'}`, 'yellow');
  
  // Run tests
  await testAPIConnection();
  await testAuthentication();
  await testContentGeneration();
  await testGalleryFetch();
  await testDashboardStats();
  await testBlogGeneration();
  await testVideoStatusCheck();
  await testErrorHandling();
  
  // Optional: Run slower tests
  const runSlowTests = false; // Set to true to run image generation tests
  if (runSlowTests) {
    await testImageGeneration();
    await testBatchRequest();
  }
  
  // Summary
  log('\n' + '='.repeat(50), 'blue');
  log('📊 TEST SUMMARY', 'blue');
  log('='.repeat(50), 'blue');
  
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const totalTime = results.reduce((sum, r) => sum + (r.time || 0), 0);
  
  log(`\nTotal Tests: ${results.length}`, 'yellow');
  log(`Passed: ${passed}`, 'green');
  log(`Failed: ${failed}`, failed > 0 ? 'red' : 'green');
  log(`Total Time: ${totalTime}ms`, 'yellow');
  
  if (failed > 0) {
    log('\n❌ FAILED TESTS:', 'red');
    results.filter(r => !r.passed).forEach(r => {
      log(`  - ${r.name}: ${r.error}`, 'red');
    });
  } else {
    log('\n✅ ALL TESTS PASSED!', 'green');
  }
  
  return {
    passed,
    failed,
    total: results.length,
    results,
  };
}

// Export for use in both platforms
export default runAPITests;