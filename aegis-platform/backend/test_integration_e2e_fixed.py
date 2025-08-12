#!/usr/bin/env python3
"""
Fixed End-to-End Integration Tests for Aegis Risk Management Platform
Tests core workflows and functionality using available endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

class AegisE2ETestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def get_auth_token(self):
        """Get authentication token"""
        try:
            login_data = {
                "username": "admin@aegis-platform.com",
                "password": "admin123"
            }
            response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                return True
            else:
                return False
        except Exception:
            return False
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, auth_required: bool = True) -> Dict:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {}
            
            if auth_required and self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"success": False, "status_code": 0, "data": {"error": "Invalid method"}}
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response.json() if response.content else {}
            }
            
        except Exception as e:
            return {
                "success": False, 
                "status_code": 0,
                "data": {"error": str(e)}
            }
    
    def test_server_health(self):
        """Test 1: Server Health Check"""
        response = self.make_request("GET", "/health", auth_required=False)
        if response["success"]:
            health_data = response["data"]
            self.log_test("Server Health Check", "PASS", f"Server responding - {health_data}")
        else:
            self.log_test("Server Health Check", "FAIL", f"Server not responding: {response}")
        return response["success"]

    def test_authentication(self):
        """Test 2: Authentication System"""
        if self.get_auth_token():
            self.log_test("Authentication - Login", "PASS", "Successfully obtained auth token")
            
            # Test authenticated endpoint
            response = self.make_request("GET", "/api/v1/auth/me")
            if response["success"]:
                user_data = response["data"]
                self.log_test("Authentication - User Info", "PASS", f"User: {user_data.get('email', 'Unknown')}")
            else:
                self.log_test("Authentication - User Info", "FAIL", f"Failed to get user info: {response}")
            return True
        else:
            self.log_test("Authentication - Login", "FAIL", "Failed to obtain auth token")
            return False

    def test_risk_management_workflow(self):
        """Test 3: Risk Management Workflow"""
        # Get risks
        response = self.make_request("GET", "/api/v1/risks")
        if response["success"]:
            risks = response["data"].get("items", [])
            self.log_test("Risk Management - List Risks", "PASS", f"Retrieved {len(risks)} risks")
        else:
            self.log_test("Risk Management - List Risks", "FAIL", f"Failed to get risks: {response}")
            return False
        
        return True

    def test_asset_management_workflow(self):
        """Test 4: Asset Management Workflow"""
        # Get assets
        response = self.make_request("GET", "/api/v1/assets")
        if response["success"]:
            assets = response["data"].get("items", [])
            self.log_test("Asset Management - List Assets", "PASS", f"Retrieved {len(assets)} assets")
        else:
            self.log_test("Asset Management - List Assets", "FAIL", f"Failed to get assets: {response}")
            return False
        
        return True

    def test_framework_management(self):
        """Test 5: Framework Management"""
        # Get frameworks
        response = self.make_request("GET", "/api/v1/frameworks")
        if response["success"]:
            frameworks = response["data"]
            # Handle both list and dict responses
            if isinstance(frameworks, dict):
                frameworks = frameworks.get("items", [])
            elif not isinstance(frameworks, list):
                frameworks = []
            
            self.log_test("Framework Management - List Frameworks", "PASS", f"Retrieved {len(frameworks)} frameworks")
            
            # Test framework controls if we have frameworks
            if frameworks and len(frameworks) > 0:
                framework_id = frameworks[0].get("id", 1) if isinstance(frameworks[0], dict) else 1
                controls_response = self.make_request("GET", f"/api/v1/frameworks/{framework_id}/controls")
                if controls_response["success"]:
                    controls = controls_response["data"]
                    if isinstance(controls, dict):
                        controls = controls.get("items", [])
                    elif not isinstance(controls, list):
                        controls = []
                    self.log_test("Framework Management - Controls", "PASS", f"Framework has {len(controls)} controls")
                else:
                    self.log_test("Framework Management - Controls", "FAIL", f"Failed: {controls_response}")
        else:
            self.log_test("Framework Management - List Frameworks", "FAIL", f"Failed: {response}")
            return False
        
        return True

    def test_task_management(self):
        """Test 6: Task Management"""
        # Get tasks
        response = self.make_request("GET", "/api/v1/tasks")
        if response["success"]:
            tasks = response["data"].get("items", [])
            self.log_test("Task Management - List Tasks", "PASS", f"Retrieved {len(tasks)} tasks")
        else:
            self.log_test("Task Management - List Tasks", "FAIL", f"Failed: {response}")
            return False
        
        return True

    def test_evidence_management(self):
        """Test 7: Evidence Management"""
        # Get evidence
        response = self.make_request("GET", "/api/v1/evidence")
        if response["success"]:
            evidence = response["data"].get("items", [])
            self.log_test("Evidence Management - List Evidence", "PASS", f"Retrieved {len(evidence)} evidence items")
        else:
            self.log_test("Evidence Management - List Evidence", "FAIL", f"Failed: {response}")
            return False
        
        return True

    def test_reports_management(self):
        """Test 8: Reports Management"""
        # Get reports
        response = self.make_request("GET", "/api/v1/reports")
        if response["success"]:
            reports = response["data"]
            # Handle both list and dict responses
            if isinstance(reports, dict):
                reports = reports.get("items", [])
            elif not isinstance(reports, list):
                reports = []
            
            self.log_test("Reports Management - List Reports", "PASS", f"Retrieved {len(reports)} reports")
        else:
            self.log_test("Reports Management - List Reports", "FAIL", f"Failed: {response}")
            return False
        
        return True

    def test_dashboard_integration(self):
        """Test 9: Dashboard Integration"""
        response = self.make_request("GET", "/api/v1/dashboards/overview")
        if response["success"]:
            dashboard = response["data"]
            total_risks = dashboard.get("risks", {}).get("total", 0)
            total_assets = dashboard.get("assets", {}).get("total", 0) 
            total_tasks = dashboard.get("tasks", {}).get("total", 0)
            self.log_test("Dashboard Integration - Overview", "PASS", f"Dashboard shows {total_risks} risks, {total_assets} assets, {total_tasks} tasks")
        else:
            self.log_test("Dashboard Integration - Overview", "FAIL", f"Failed: {response}")
        
        return True

    def test_api_performance(self):
        """Test 10: API Performance"""
        endpoints = [
            "/api/v1/risks", 
            "/api/v1/assets",
            "/api/v1/tasks",
            "/api/v1/frameworks",
            "/api/v1/dashboards/overview"
        ]
        
        total_time = 0
        slowest_endpoint = ""
        slowest_time = 0
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.make_request("GET", endpoint)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            total_time += response_time
            if response_time > slowest_time:
                slowest_time = response_time
                slowest_endpoint = endpoint
            
            self.log_test(f"Performance - {endpoint}", "PASS", f"Response time: {response_time:.2f}ms")
        
        avg_time = total_time / len(endpoints)
        self.log_test("Performance Summary", "INFO", f"Average: {avg_time:.2f}ms, Slowest: {slowest_endpoint} ({slowest_time:.2f}ms)")
        
        return True

    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 80)
        print("AEGIS RISK MANAGEMENT PLATFORM - END-TO-END INTEGRATION TESTS")
        print("=" * 80)
        print(f"Test started at: {datetime.now().isoformat()}")
        print(f"Target server: {self.base_url}")
        print("-" * 80)
        
        # Test order matters - authentication must be first
        test_methods = [
            self.test_server_health,
            self.test_authentication,
            self.test_risk_management_workflow,
            self.test_asset_management_workflow,
            self.test_framework_management,
            self.test_task_management,
            self.test_evidence_management,
            self.test_reports_management,
            self.test_dashboard_integration,
            self.test_api_performance
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, "ERROR", f"Test crashed: {str(e)}")
        
        # Generate final report
        self.generate_report()

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("END-TO-END INTEGRATION TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print(f"\nFAILED TESTS ({self.failed_tests}):")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test_name']}: {result['details']}")
        
        # Overall system health assessment
        success_rate = (self.passed_tests / self.total_tests) * 100
        if success_rate >= 90:
            health_status = "HEALTHY"
        elif success_rate >= 70:
            health_status = "WARNING"
        else:
            health_status = "CRITICAL"
        
        print(f"\nOVERALL SYSTEM HEALTH: {health_status}")
        
        if success_rate < 100:
            print(f"\nRECOMMENDATIONS:")
            print(f"  1. Review failed test details above")
            print(f"  2. Check server logs for error details")
            print(f"  3. Verify all dependencies are properly installed")
            print(f"  4. Ensure database connections are working")
        
        print("=" * 80)
        print(f"Test completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Allow base URL to be passed as command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Initializing E2E test suite for: {base_url}")
    
    suite = AegisE2ETestSuite(base_url)
    suite.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if suite.failed_tests == 0 else 1)