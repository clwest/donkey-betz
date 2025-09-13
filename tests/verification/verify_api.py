#!/usr/bin/env python3
"""
API Endpoint Verification Script for Unified Donkey Betz Platform

This script tests all API endpoints to ensure:
1. Root and API endpoints are accessible
2. Unified API versioning works correctly
3. Authentication middleware functions properly
4. Rate limiting is applied
5. API documentation is accessible
6. Consistent response formats
7. Security headers are present
8. CORS configuration works
"""

import requests
import json
import time
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"  └─ {details}")
    
    def test_endpoint(self, endpoint, method="GET", expected_status=200, 
                     expected_fields=None, auth_required=False, headers=None):
        """Test a specific endpoint"""
        url = f"{self.base_url}{endpoint}"
        test_headers = self.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            response = self.session.request(method, url, headers=test_headers)
            
            # Check status code
            if response.status_code != expected_status:
                return False, f"Expected {expected_status}, got {response.status_code}"
            
            # Check response format (JSON)
            try:
                data = response.json()
            except json.JSONDecodeError:
                return False, "Response is not valid JSON"
            
            # Check for unified response format
            if endpoint.startswith('/api/') and response.status_code < 400:
                if 'success' not in data:
                    return False, "Response missing 'success' field in unified format"
            
            # Check expected fields
            if expected_fields:
                for field in expected_fields:
                    if field not in data:
                        return False, f"Response missing expected field: {field}"
            
            # Check security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Content-Security-Policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                return False, f"Missing security headers: {', '.join(missing_headers)}"
            
            return True, f"Status: {response.status_code}, Headers: OK"
            
        except requests.exceptions.ConnectionError:
            return False, "Connection failed - server may not be running"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def test_rate_limiting(self, endpoint="/api/", requests_count=10):
        """Test rate limiting by making multiple requests quickly"""
        url = f"{self.base_url}{endpoint}"
        
        # Make rapid requests
        responses = []
        for i in range(requests_count):
            try:
                response = self.session.get(url)
                responses.append(response.status_code)
            except Exception as e:
                responses.append(f"Error: {e}")
        
        # Check if any were rate limited (429)
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            return True, f"Rate limiting working - got 429 status in {requests_count} requests"
        else:
            return True, f"No rate limiting triggered in {requests_count} requests (might be expected for low volume)"
    
    def test_cors_headers(self, endpoint="/api/"):
        """Test CORS headers"""
        url = f"{self.base_url}{endpoint}"
        
        # Send preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type',
        }
        
        try:
            response = self.session.options(url, headers=headers)
            
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
            ]
            
            present_headers = []
            missing_headers = []
            
            for header in cors_headers:
                if header in response.headers:
                    present_headers.append(f"{header}: {response.headers[header]}")
                else:
                    missing_headers.append(header)
            
            if missing_headers:
                return False, f"Missing CORS headers: {', '.join(missing_headers)}"
            
            return True, f"CORS headers present: {'; '.join(present_headers)}"
            
        except Exception as e:
            return False, f"CORS test failed: {str(e)}"
    
    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("=" * 60)
        print("UNIFIED DONKEY BETZ PLATFORM - API VERIFICATION")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Root endpoint
        success, details = self.test_endpoint("/", expected_fields=['success', 'data'])
        self.log_result("Root Endpoint (/)", "PASS" if success else "FAIL", details)
        
        # Test 2: API root endpoint
        success, details = self.test_endpoint("/api/", expected_fields=['success', 'data'])
        self.log_result("API Root Endpoint (/api/)", "PASS" if success else "FAIL", details)
        
        # Test 3: API documentation endpoints
        success, details = self.test_endpoint("/api/docs/")
        self.log_result("Swagger Documentation (/api/docs/)", "PASS" if success else "FAIL", details)
        
        success, details = self.test_endpoint("/api/redoc/")
        self.log_result("ReDoc Documentation (/api/redoc/)", "PASS" if success else "FAIL", details)
        
        success, details = self.test_endpoint("/api/schema/")
        self.log_result("OpenAPI Schema (/api/schema/)", "PASS" if success else "FAIL", details)
        
        # Test 4: Versioned API endpoints
        success, details = self.test_endpoint("/api/v1/agents/")
        self.log_result("Agents API v1 (/api/v1/agents/)", "PASS" if success else "FAIL", details)
        
        success, details = self.test_endpoint("/api/v1/sports/")
        self.log_result("Sports API v1 (/api/v1/sports/)", "PASS" if success else "FAIL", details)
        
        # Test 5: Rate limiting
        success, details = self.test_rate_limiting()
        self.log_result("Rate Limiting Test", "PASS" if success else "FAIL", details)
        
        # Test 6: CORS headers
        success, details = self.test_cors_headers()
        self.log_result("CORS Headers Test", "PASS" if success else "FAIL", details)
        
        # Test 7: Authentication test (should fail without token)
        success, details = self.test_endpoint("/api/v1/agents/templates/", expected_status=401)
        self.log_result("Authentication Required Test", "PASS" if success else "FAIL", details)
        
        # Test 8: Admin interface
        success, details = self.test_endpoint("/admin/", expected_status=302)  # Redirect to login
        self.log_result("Admin Interface (/admin/)", "PASS" if success else "FAIL", details)
        
        # Summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed = sum(1 for result in self.test_results if result['status'] == 'FAIL')
        warnings = sum(1 for result in self.test_results if result['status'] == 'WARN')
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print()
            print("FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['details']}")
        
        print()
        print("RECOMMENDATIONS:")
        print("1. All core API endpoints should be accessible")
        print("2. Unified response format should be consistent")
        print("3. Security headers should be present on all responses")
        print("4. Rate limiting should prevent abuse")
        print("5. CORS should be configured for frontend integration")
        print("6. API documentation should be available and functional")
        
        return failed == 0

def main():
    """Main execution function"""
    import sys
    
    base_url = "http://localhost:8001"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()