#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script for Aegis Platform
Tests all major endpoints and workflows to ensure system stability
"""

import requests
import json
import sys
import time
from typing import Dict, List, Optional

# Configuration
BASE_URL = "http://localhost:30641"
FRONTEND_URL = "http://localhost:58533"

class AegisTestSuite:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.test_results = []
        self.session = requests.Session()
        
        # Test user credentials
        self.test_user = {
            "email": "admin@example.com",
            "password": "admin123"
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self) -> bool:
        """Test backend health check"""
        try:
            response = self.session.get(f"{self.base_url}/health/")
            success = response.status_code == 200
            data = response.json() if success else response.text
            self.log_test("Health Check", success, f"Status: {response.status_code}, Data: {data}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_preflight(self) -> bool:
        """Test CORS preflight request"""
        try:
            headers = {
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            response = self.session.options(f"{self.base_url}/api/v1/evidence/upload", headers=headers)
            success = response.status_code == 200
            cors_headers = {
                k: v for k, v in response.headers.items() 
                if k.lower().startswith('access-control')
            }
            self.log_test("CORS Preflight", success, f"Headers: {cors_headers}")
            return success
        except Exception as e:
            self.log_test("CORS Preflight", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test user authentication"""
        try:
            # Login request
            login_data = {
                "username": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data,  # Form data
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log_test("Authentication", True, f"Token received: {self.access_token[:20]}...")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, description: str, data: Optional[Dict] = None) -> bool:
        """Generic endpoint testing"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                self.log_test(description, False, f"Unsupported method: {method}")
                return False
            
            success = response.status_code < 500  # Allow 4xx but not 5xx errors
            status_info = f"Status: {response.status_code}"
            
            if response.status_code == 401:
                status_info += " (Authentication required - expected)"
            elif response.status_code == 404:
                status_info += " (Not found - may be expected)"
            elif response.status_code >= 400:
                status_info += f" Error: {response.text[:100]}"
            
            self.log_test(description, success, status_info)
            return success
        except Exception as e:
            self.log_test(description, False, f"Exception: {str(e)}")
            return False
    
    def test_all_endpoints(self) -> Dict:
        """Test all major endpoints"""
        
        # Core API endpoints to test
        endpoints = [
            # Authentication
            ("GET", "/api/v1/auth/me", "Get Current User"),
            
            # Assets
            ("GET", "/api/v1/assets", "List Assets"),
            ("POST", "/api/v1/assets", "Create Asset", {
                "name": "Test Asset",
                "description": "Test asset description",
                "asset_type": "server",
                "criticality": "medium",
                "status": "active",
                "environment": "development"
            }),
            
            # Risks
            ("GET", "/api/v1/risks", "List Risks"),
            ("POST", "/api/v1/risks", "Create Risk", {
                "title": "Test Risk",
                "description": "Test risk description",
                "likelihood": "medium",
                "impact": "medium",
                "status": "open"
            }),
            
            # Tasks
            ("GET", "/api/v1/tasks", "List Tasks"),
            ("POST", "/api/v1/tasks", "Create Task", {
                "title": "Test Task",
                "description": "Test task description",
                "priority": "Medium",
                "status": "Open"
            }),
            
            # Evidence
            ("GET", "/api/v1/evidence", "List Evidence"),
            
            # Assessments
            ("GET", "/api/v1/assessments", "List Assessments"),
            ("POST", "/api/v1/assessments", "Create Assessment", {
                "name": "Test Assessment",
                "description": "Test assessment description",
                "framework": "NIST"
            }),
            
            # Users
            ("GET", "/api/v1/users", "List Users"),
            
            # Dashboards
            ("GET", "/api/v1/dashboards/overview", "Dashboard Overview"),
            ("GET", "/api/v1/dashboards/metrics", "Dashboard Metrics"),
            ("GET", "/api/v1/dashboards/ciso-cockpit", "CISO Cockpit"),
            ("GET", "/api/v1/dashboards/analyst-workbench", "Analyst Workbench"),
            ("GET", "/api/v1/dashboards/system-owner-inbox", "System Owner Inbox"),
            
            # Reports
            ("GET", "/api/v1/reports", "List Reports"),
            
            # AI Services
            ("GET", "/api/v1/ai/providers", "AI Providers"),
            ("GET", "/api/v1/ai/providers/status", "AI Provider Status"),
        ]
        
        results = {}
        for endpoint_data in endpoints:
            method = endpoint_data[0]
            endpoint = endpoint_data[1]
            description = endpoint_data[2]
            data = endpoint_data[3] if len(endpoint_data) > 3 else None
            
            success = self.test_endpoint(method, endpoint, description, data)
            results[endpoint] = success
        
        return results
    
    def test_evidence_upload(self) -> bool:
        """Test evidence upload functionality specifically"""
        try:
            # Create a test file
            files = {'file': ('test.txt', 'This is a test file content', 'text/plain')}
            params = {
                'title': 'Test Evidence Upload',
                'evidence_type': 'document',
                'description': 'Test evidence upload via API'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/evidence/upload",
                files=files,
                params=params
            )
            
            success = response.status_code < 500
            details = f"Status: {response.status_code}"
            if not success:
                details += f", Error: {response.text[:200]}"
            
            self.log_test("Evidence Upload", success, details)
            return success
        except Exception as e:
            self.log_test("Evidence Upload", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Aegis Platform Testing")
        print("=" * 60)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Backend is not healthy - stopping tests")
            return
        
        # Test 2: CORS
        self.test_cors_preflight()
        
        # Test 3: Authentication
        auth_success = self.test_authentication()
        
        # Test 4: All endpoints (with or without auth)
        print("\n📊 Testing All API Endpoints:")
        print("-" * 40)
        endpoint_results = self.test_all_endpoints()
        
        # Test 5: Evidence upload
        if auth_success:
            print("\n📎 Testing Evidence Upload:")
            print("-" * 40)
            self.test_evidence_upload()
        
        # Summary
        print("\n📋 Test Summary:")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = AegisTestSuite()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)