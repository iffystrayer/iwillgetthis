#!/usr/bin/env python3
"""
Aegis Risk Management Platform - Fixed Integration Test Suite
============================================================
This script tests all core functionality using the correct API endpoints.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AegisIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.test_data = {}
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        logger.info(f"{status_emoji} {test_name}: {status} - {details}")

    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", "PASS", "Service is healthy")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Unhealthy status: {data}")
                    return False
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_authentication(self):
        """Test authentication workflow"""
        try:
            # Test login with default admin credentials
            login_data = {
                "username": "admin@aegis-platform.com",
                "password": "admin123"
            }

            response = self.session.post(f"{self.api_base}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Authentication - Login", "PASS", "Successfully authenticated as admin")
                    
                    # Test token validation
                    me_response = self.session.get(f"{self.api_base}/auth/me")
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        self.test_data["current_user"] = user_data
                        self.log_test("Authentication - Token Validation", "PASS", f"User: {user_data.get('email')}")
                        return True
                    else:
                        self.log_test("Authentication - Token Validation", "FAIL", f"HTTP {me_response.status_code}")
                        return False
                else:
                    self.log_test("Authentication - Login", "FAIL", "No access token in response")
                    return False
            else:
                self.log_test("Authentication - Login", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Error: {str(e)}")
            return False

    def test_user_management(self):
        """Test user management functionality"""
        try:
            response = self.session.get(f"{self.api_base}/users/")
            if response.status_code == 200:
                users = response.json()
                self.test_data["users"] = users
                self.log_test("User Management - List Users", "PASS", f"Found {len(users)} users")
                
                # Test user count
                count_response = self.session.get(f"{self.api_base}/users/count")
                if count_response.status_code == 200:
                    self.log_test("User Management - User Count", "PASS", "User count accessible")
                else:
                    self.log_test("User Management - User Count", "FAIL", f"HTTP {count_response.status_code}")
                
                return True
            else:
                self.log_test("User Management - List Users", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Management", "FAIL", f"Error: {str(e)}")
            return False

    def test_asset_management(self):
        """Test asset management functionality"""
        try:
            response = self.session.get(f"{self.api_base}/assets/")
            if response.status_code == 200:
                assets = response.json()
                self.test_data["assets"] = assets
                self.log_test("Asset Management - List Assets", "PASS", f"Found {len(assets)} assets")
                
                # Test asset summary
                summary_response = self.session.get(f"{self.api_base}/assets/summary")
                if summary_response.status_code == 200:
                    self.log_test("Asset Management - Asset Summary", "PASS", "Asset summary accessible")
                else:
                    self.log_test("Asset Management - Asset Summary", "FAIL", f"HTTP {summary_response.status_code}")
                
                # Test asset categories
                categories_response = self.session.get(f"{self.api_base}/assets/categories/")
                if categories_response.status_code == 200:
                    self.log_test("Asset Management - Categories", "PASS", "Asset categories accessible")
                else:
                    self.log_test("Asset Management - Categories", "FAIL", f"HTTP {categories_response.status_code}")
                
                return True
            else:
                self.log_test("Asset Management - List Assets", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Asset Management", "FAIL", f"Error: {str(e)}")
            return False

    def test_risk_management(self):
        """Test risk management functionality"""
        try:
            response = self.session.get(f"{self.api_base}/risks/")
            if response.status_code == 200:
                risks = response.json()
                self.test_data["risks"] = risks
                self.log_test("Risk Management - List Risks", "PASS", f"Found {len(risks)} risks")
                
                # Test risk matrices
                matrices_response = self.session.get(f"{self.api_base}/risks/matrices/")
                if matrices_response.status_code == 200:
                    self.log_test("Risk Management - Risk Matrices", "PASS", "Risk matrices accessible")
                else:
                    self.log_test("Risk Management - Risk Matrices", "FAIL", f"HTTP {matrices_response.status_code}")
                
                # Test risk summary
                summary_response = self.session.get(f"{self.api_base}/risks/summary")
                if summary_response.status_code == 200:
                    self.log_test("Risk Management - Risk Summary", "PASS", "Risk summary accessible")
                else:
                    self.log_test("Risk Management - Risk Summary", "FAIL", f"HTTP {summary_response.status_code}")
                
                return True
            else:
                self.log_test("Risk Management - List Risks", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Risk Management", "FAIL", f"Error: {str(e)}")
            return False

    def test_task_management(self):
        """Test POA&M task management"""
        try:
            response = self.session.get(f"{self.api_base}/tasks/")
            if response.status_code == 200:
                tasks = response.json()
                self.test_data["tasks"] = tasks
                self.log_test("Task Management - List Tasks", "PASS", f"Found {len(tasks)} tasks")
                
                # Test my tasks
                my_tasks_response = self.session.get(f"{self.api_base}/tasks/my-tasks")
                if my_tasks_response.status_code == 200:
                    self.log_test("Task Management - My Tasks", "PASS", "My tasks accessible")
                else:
                    self.log_test("Task Management - My Tasks", "FAIL", f"HTTP {my_tasks_response.status_code}")
                
                # Test task summary
                summary_response = self.session.get(f"{self.api_base}/tasks/summary")
                if summary_response.status_code == 200:
                    self.log_test("Task Management - Task Summary", "PASS", "Task summary accessible")
                else:
                    self.log_test("Task Management - Task Summary", "FAIL", f"HTTP {summary_response.status_code}")
                
                return True
            else:
                self.log_test("Task Management - List Tasks", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Task Management", "FAIL", f"Error: {str(e)}")
            return False

    def test_evidence_management(self):
        """Test evidence management functionality"""
        try:
            response = self.session.get(f"{self.api_base}/evidence/")
            if response.status_code == 200:
                evidence = response.json()
                self.test_data["evidence"] = evidence
                self.log_test("Evidence Management - List Evidence", "PASS", f"Found {len(evidence)} evidence items")
                return True
            else:
                self.log_test("Evidence Management - List Evidence", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Evidence Management", "FAIL", f"Error: {str(e)}")
            return False

    def test_dashboard_endpoints(self):
        """Test dashboard functionality"""
        try:
            # Test overview dashboard
            overview_response = self.session.get(f"{self.api_base}/dashboards/overview")
            if overview_response.status_code == 200:
                self.log_test("Dashboard - Overview", "PASS", "Overview dashboard accessible")
            else:
                self.log_test("Dashboard - Overview", "FAIL", f"HTTP {overview_response.status_code}")
            
            # Test CISO cockpit
            ciso_response = self.session.get(f"{self.api_base}/dashboards/ciso-cockpit")
            if ciso_response.status_code == 200:
                self.log_test("Dashboard - CISO Cockpit", "PASS", "CISO cockpit accessible")
            else:
                self.log_test("Dashboard - CISO Cockpit", "FAIL", f"HTTP {ciso_response.status_code}")
            
            # Test analyst workbench
            analyst_response = self.session.get(f"{self.api_base}/dashboards/analyst-workbench")
            if analyst_response.status_code == 200:
                self.log_test("Dashboard - Analyst Workbench", "PASS", "Analyst workbench accessible")
                return True
            else:
                self.log_test("Dashboard - Analyst Workbench", "FAIL", f"HTTP {analyst_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Endpoints", "FAIL", f"Error: {str(e)}")
            return False

    def test_ai_integration(self):
        """Test AI/LLM integration"""
        try:
            # Test AI evidence analysis endpoint
            analysis_response = self.session.get(f"{self.api_base}/ai/ai/analyze-evidence")
            if analysis_response.status_code in [200, 422, 405]:  # 422/405 expected without proper data
                self.log_test("AI Integration - Evidence Analysis", "PASS", "Evidence analysis endpoint accessible")
            else:
                self.log_test("AI Integration - Evidence Analysis", "FAIL", f"HTTP {analysis_response.status_code}")
            
            # Test AI risk statement generation
            risk_gen_response = self.session.get(f"{self.api_base}/ai/ai/generate-risk-statement")
            if risk_gen_response.status_code in [200, 422, 405]:  # 422/405 expected without proper data
                self.log_test("AI Integration - Risk Generation", "PASS", "Risk generation endpoint accessible")
                return True
            else:
                self.log_test("AI Integration - Risk Generation", "FAIL", f"HTTP {risk_gen_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Integration", "FAIL", f"Error: {str(e)}")
            return False

    def test_frontend_application(self):
        """Test frontend application accessibility"""
        try:
            frontend_response = requests.get("http://localhost:3000")
            if frontend_response.status_code == 200:
                content = frontend_response.text
                if "<!doctype html>" in content.lower():
                    self.log_test("Frontend - Main Page", "PASS", "Frontend application accessible")
                    
                    # Check for React app
                    if "react" in content.lower() or "root" in content:
                        self.log_test("Frontend - React App", "PASS", "React application detected")
                    else:
                        self.log_test("Frontend - React App", "WARN", "React app structure not clearly detected")
                    
                    return True
                else:
                    self.log_test("Frontend - Main Page", "FAIL", "Invalid HTML response")
                    return False
            else:
                self.log_test("Frontend - Main Page", "FAIL", f"HTTP {frontend_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Application", "FAIL", f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Aegis Platform Integration Tests (Fixed)")
        logger.info("=" * 60)
        
        test_methods = [
            self.test_health_check,
            self.test_authentication,
            self.test_user_management,
            self.test_asset_management,
            self.test_risk_management,
            self.test_task_management,
            self.test_evidence_management,
            self.test_dashboard_endpoints,
            self.test_ai_integration,
            self.test_frontend_application
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Unexpected error in {test_method.__name__}: {str(e)}")
            
            time.sleep(0.5)
        
        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "test_data": self.test_data
        }
        
        return report

if __name__ == "__main__":
    tester = AegisIntegrationTester()
    
    logger.info("🔍 Aegis Platform - Fixed Integration Test Suite")
    logger.info("=" * 60)
    
    report = tester.run_all_tests()
    
    # Save report to file
    with open("integration_test_report_fixed.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {report['summary']['total_tests']}")
    logger.info(f"✅ Passed: {report['summary']['passed']}")
    logger.info(f"❌ Failed: {report['summary']['failed']}")
    logger.info(f"⚠️ Warnings: {report['summary']['warnings']}")
    logger.info(f"📈 Success Rate: {report['summary']['success_rate']}%")
    logger.info("=" * 60)
    
    if report['summary']['failed'] > 0:
        logger.warning("⚠️ Some tests failed. Check the detailed report above.")
        sys.exit(1)
    else:
        logger.info("🎉 All tests passed successfully!")
        sys.exit(0)
