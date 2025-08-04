#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script for Aegis Platform
Tests all endpoints, authentication workflows, and API functionality
"""

import sys
import os
from fastapi.testclient import TestClient
import json
import traceback
from datetime import datetime

# Add current directory to path
sys.path.append('.')

try:
    from main import app
    print("✅ Successfully imported main FastAPI application")
except ImportError as e:
    print(f"❌ Failed to import main application: {e}")
    sys.exit(1)

# Initialize test client
client = TestClient(app)

class EndpointTester:
    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "detailed_results": []
        }
        self.access_token = None
        
    def log_result(self, test_name, success, status_code=None, response_data=None, error=None):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name} - Status: {status_code}")
        else:
            self.test_results["failed"] += 1
            print(f"❌ {test_name} - Status: {status_code} - Error: {error}")
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(error),
                "status_code": status_code
            })
        
        self.test_results["detailed_results"].append({
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "response_data": response_data,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })

    def test_basic_endpoints(self):
        """Test basic application endpoints"""
        print("\n🔄 Testing Basic Endpoints...")
        
        # Test health endpoint
        try:
            response = client.get("/health")
            self.log_result("Health Endpoint", 
                          response.status_code == 200, 
                          response.status_code, 
                          response.json())
        except Exception as e:
            self.log_result("Health Endpoint", False, None, None, e)
        
        # Test root endpoint
        try:
            response = client.get("/")
            self.log_result("Root Endpoint", 
                          response.status_code == 200, 
                          response.status_code, 
                          response.json())
        except Exception as e:
            self.log_result("Root Endpoint", False, None, None, e)

    def test_authentication_endpoints(self):
        """Test authentication workflows"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test login endpoint - should fail with no credentials
        try:
            response = client.post("/api/v1/auth/login", json={})
            self.log_result("Login Endpoint (No Credentials)", 
                          response.status_code in [400, 422], 
                          response.status_code, 
                          response.json())
        except Exception as e:
            self.log_result("Login Endpoint (No Credentials)", False, None, None, e)
        
        # Test login with invalid credentials
        try:
            response = client.post("/api/v1/auth/login", json={
                "username": "invalid_user",
                "password": "invalid_password"
            })
            self.log_result("Login Endpoint (Invalid Credentials)", 
                          response.status_code in [401, 400], 
                          response.status_code, 
                          response.json())
        except Exception as e:
            self.log_result("Login Endpoint (Invalid Credentials)", False, None, None, e)

    def test_protected_endpoints(self):
        """Test protected endpoints without authentication"""
        print("\n🔒 Testing Protected Endpoints (Unauthorized Access)...")
        
        protected_endpoints = [
            ("GET", "/api/v1/users"),
            ("GET", "/api/v1/assets"),
            ("GET", "/api/v1/risks"),
            ("GET", "/api/v1/assessments"),
            ("GET", "/api/v1/tasks"),
            ("GET", "/api/v1/evidence"),
            ("GET", "/api/v1/analytics/metrics"),
            ("GET", "/api/v1/analytics/dashboards"),
        ]
        
        for method, endpoint in protected_endpoints:
            try:
                if method == "GET":
                    response = client.get(endpoint)
                elif method == "POST":
                    response = client.post(endpoint, json={})
                
                # Should return 401 Unauthorized
                self.log_result(f"Protected {method} {endpoint}", 
                              response.status_code == 401, 
                              response.status_code, 
                              response.json())
            except Exception as e:
                self.log_result(f"Protected {method} {endpoint}", False, None, None, e)

    def test_openapi_documentation(self):
        """Test OpenAPI documentation endpoints"""
        print("\n📚 Testing API Documentation Endpoints...")
        
        doc_endpoints = [
            "/docs",
            "/redoc", 
            "/openapi.json"
        ]
        
        for endpoint in doc_endpoints:
            try:
                response = client.get(endpoint)
                self.log_result(f"Documentation {endpoint}", 
                              response.status_code == 200, 
                              response.status_code)
            except Exception as e:
                self.log_result(f"Documentation {endpoint}", False, None, None, e)

    def test_data_validation(self):
        """Test input validation on various endpoints"""
        print("\n✅ Testing Data Validation...")
        
        # Test POST endpoints with invalid data
        validation_tests = [
            ("POST", "/api/v1/auth/login", {"username": ""}),  # Empty username
            ("POST", "/api/v1/auth/login", {"password": ""}),   # Empty password
        ]
        
        for method, endpoint, data in validation_tests:
            try:
                response = client.post(endpoint, json=data)
                # Should return 422 for validation errors
                self.log_result(f"Validation {method} {endpoint}", 
                              response.status_code in [400, 422], 
                              response.status_code, 
                              response.json())
            except Exception as e:
                self.log_result(f"Validation {method} {endpoint}", False, None, None, e)

    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n🌐 Testing CORS Configuration...")
        
        try:
            response = client.options("/")
            # Check for CORS headers
            has_cors_headers = (
                "access-control-allow-origin" in response.headers or
                "Access-Control-Allow-Origin" in response.headers
            )
            self.log_result("CORS Headers", 
                          has_cors_headers or response.status_code == 200, 
                          response.status_code)
        except Exception as e:
            self.log_result("CORS Headers", False, None, None, e)

    def test_error_handling(self):
        """Test error handling for non-existent endpoints"""
        print("\n🚫 Testing Error Handling...")
        
        # Test 404 for non-existent endpoint
        try:
            response = client.get("/api/v1/nonexistent")
            self.log_result("404 Error Handling", 
                          response.status_code == 404, 
                          response.status_code, 
                          response.json())
        except Exception as e:
            self.log_result("404 Error Handling", False, None, None, e)

    def test_analytics_endpoints(self):
        """Test analytics endpoints structure"""
        print("\n📊 Testing Analytics Endpoints...")
        
        analytics_endpoints = [
            "/api/v1/analytics/metrics",
            "/api/v1/analytics/dashboards",
            "/api/v1/analytics/reports",
            "/api/v1/analytics/forecasts/risk"
        ]
        
        for endpoint in analytics_endpoints:
            try:
                response = client.get(endpoint)
                # Should be unauthorized (401) since we're not authenticated
                self.log_result(f"Analytics {endpoint}", 
                              response.status_code == 401, 
                              response.status_code)
            except Exception as e:
                self.log_result(f"Analytics {endpoint}", False, None, None, e)

    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Comprehensive Aegis Platform Endpoint Testing")
        print("=" * 60)
        
        # Run all test suites
        self.test_basic_endpoints()
        self.test_authentication_endpoints()
        self.test_protected_endpoints()
        self.test_openapi_documentation()
        self.test_data_validation()
        self.test_cors_headers()
        self.test_error_handling()
        self.test_analytics_endpoints()
        
        # Print summary
        self.print_summary()
        
        # Save results to file
        self.save_results()
        
        return self.test_results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\n❌ Failed Tests:")
            for error in self.test_results['errors']:
                print(f"  - {error['test']}: {error['error']} (Status: {error['status_code']})")

    def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"endpoint_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main function to run tests"""
    try:
        tester = EndpointTester()
        results = tester.run_all_tests()
        
        # Exit with error code if any tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            print("\n🎉 All tests passed successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()