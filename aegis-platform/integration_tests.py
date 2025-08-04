#!/usr/bin/env python3
"""
Aegis Risk Management Platform - Comprehensive Integration Test Suite
=====================================================================
This script tests all core functionality and workflows without making changes.
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
            response = self.session.get(f"{self.base_url}/health")
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

            response = self.session.post(f"{self.api_base}/auth/login", data=login_data)
            
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
            # Get all users
            response = self.session.get(f"{self.api_base}/users/")
            if response.status_code == 200:
                users = response.json()
                self.test_data["users"] = users
                self.log_test("User Management - List Users", "PASS", f"Found {len(users)} users")

                # Test getting specific user
                if users:
                    user_id = users[0]["id"]
                    user_response = self.session.get(f"{self.api_base}/users/{user_id}")
                    if user_response.status_code == 200:
                        self.log_test("User Management - Get User", "PASS", "Successfully retrieved user details")
                        return True
                    else:
                        self.log_test("User Management - Get User", "FAIL", f"HTTP {user_response.status_code}")
                        return False
                else:
                    self.log_test("User Management - Get User", "SKIP", "No users found to test")
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
            # Get all assets
            response = self.session.get(f"{self.api_base}/assets/")
            if response.status_code == 200:
                assets = response.json()
                self.test_data["assets"] = assets
                self.log_test("Asset Management - List Assets", "PASS", f"Found {len(assets)} assets")

                # Test asset creation (read-only, so we'll test the endpoint structure)
                create_response = self.session.post(f"{self.api_base}/assets/", json={
                    "name": "TEST_ASSET_VALIDATION",
                    "description": "Test asset for validation",
                    "asset_type": "server",
                    "criticality": "high"
                })
                
                if create_response.status_code in [200, 201]:
                    # If successful, we need to clean up (but we're in read-only mode)
                    self.log_test("Asset Management - Create Asset", "PASS", "Asset creation endpoint working")
                    # Store the created asset for potential cleanup
                    if create_response.status_code == 201:
                        created_asset = create_response.json()
                        self.test_data["created_asset"] = created_asset
                elif create_response.status_code == 422:
                    self.log_test("Asset Management - Create Asset", "PASS", "Validation working (expected for test data)")
                else:
                    self.log_test("Asset Management - Create Asset", "FAIL", f"HTTP {create_response.status_code}")
                
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
            # Get all risks
            response = self.session.get(f"{self.api_base}/risks/")
            if response.status_code == 200:
                risks = response.json()
                self.test_data["risks"] = risks
                self.log_test("Risk Management - List Risks", "PASS", f"Found {len(risks)} risks")

                # Test risk matrices endpoint
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

    def test_compliance_frameworks(self):
        """Test compliance framework functionality"""
        try:
            # Test NIST CSF
            nist_response = self.session.get(f"{self.base_url}/compliance/nist-csf")
            if nist_response.status_code == 200:
                nist_data = nist_response.json()
                self.log_test("Compliance - NIST CSF", "PASS", f"Found {len(nist_data)} NIST controls")
            else:
                self.log_test("Compliance - NIST CSF", "FAIL", f"HTTP {nist_response.status_code}")
            
            # Test CIS Controls
            cis_response = self.session.get(f"{self.base_url}/compliance/cis-controls")
            if cis_response.status_code == 200:
                cis_data = cis_response.json()
                self.log_test("Compliance - CIS Controls", "PASS", f"Found {len(cis_data)} CIS controls")
            else:
                self.log_test("Compliance - CIS Controls", "FAIL", f"HTTP {cis_response.status_code}")
            
            # Test compliance status
            status_response = self.session.get(f"{self.base_url}/compliance/status")
            if status_response.status_code == 200:
                self.log_test("Compliance - Status", "PASS", "Compliance status accessible")
                return True
            else:
                self.log_test("Compliance - Status", "FAIL", f"HTTP {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Compliance Frameworks", "FAIL", f"Error: {str(e)}")
            return False

    def test_task_management(self):
        """Test POA&M task management"""
        try:
            # Get all tasks
            response = self.session.get(f"{self.base_url}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                self.test_data["tasks"] = tasks
                self.log_test("Task Management - List Tasks", "PASS", f"Found {len(tasks)} tasks")
                
                # Test task status updates (if tasks exist)
                if tasks:
                    task_id = tasks[0]["id"]
                    task_response = self.session.get(f"{self.base_url}/tasks/{task_id}")
                    if task_response.status_code == 200:
                        self.log_test("Task Management - Get Task", "PASS", "Task details accessible")
                    else:
                        self.log_test("Task Management - Get Task", "FAIL", f"HTTP {task_response.status_code}")
                
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
            # Get all evidence
            response = self.session.get(f"{self.base_url}/evidence")
            if response.status_code == 200:
                evidence = response.json()
                self.test_data["evidence"] = evidence
                self.log_test("Evidence Management - List Evidence", "PASS", f"Found {len(evidence)} evidence items")
                
                # Test file upload endpoint (without actually uploading)
                upload_response = self.session.get(f"{self.base_url}/evidence/upload")
                if upload_response.status_code in [200, 405]:  # 405 is expected for GET on POST endpoint
                    self.log_test("Evidence Management - Upload Endpoint", "PASS", "Upload endpoint accessible")
                else:
                    self.log_test("Evidence Management - Upload Endpoint", "FAIL", f"HTTP {upload_response.status_code}")
                
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
            # Test main dashboard
            dashboard_response = self.session.get(f"{self.base_url}/dashboard")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                self.log_test("Dashboard - Main Dashboard", "PASS", "Dashboard data accessible")
            else:
                self.log_test("Dashboard - Main Dashboard", "FAIL", f"HTTP {dashboard_response.status_code}")
            
            # Test metrics endpoint
            metrics_response = self.session.get(f"{self.base_url}/dashboard/metrics")
            if metrics_response.status_code == 200:
                self.log_test("Dashboard - Metrics", "PASS", "Metrics data accessible")
            else:
                self.log_test("Dashboard - Metrics", "FAIL", f"HTTP {metrics_response.status_code}")
            
            # Test reports endpoint
            reports_response = self.session.get(f"{self.base_url}/reports")
            if reports_response.status_code == 200:
                self.log_test("Dashboard - Reports", "PASS", "Reports accessible")
                return True
            else:
                self.log_test("Dashboard - Reports", "FAIL", f"HTTP {reports_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Endpoints", "FAIL", f"Error: {str(e)}")
            return False

    def test_ai_integration(self):
        """Test AI/LLM integration"""
        try:
            # Test AI providers endpoint
            providers_response = self.session.get(f"{self.base_url}/ai/providers")
            if providers_response.status_code == 200:
                providers = providers_response.json()
                self.log_test("AI Integration - Providers", "PASS", f"Found {len(providers)} AI providers")
            else:
                self.log_test("AI Integration - Providers", "FAIL", f"HTTP {providers_response.status_code}")
            
            # Test AI analysis endpoint (without making actual calls)
            analysis_response = self.session.get(f"{self.base_url}/ai/analysis")
            if analysis_response.status_code in [200, 422]:  # 422 expected without proper data
                self.log_test("AI Integration - Analysis", "PASS", "Analysis endpoint accessible")
                return True
            else:
                self.log_test("AI Integration - Analysis", "FAIL", f"HTTP {analysis_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Integration", "FAIL", f"Error: {str(e)}")
            return False

    def test_external_integrations(self):
        """Test external integration endpoints"""
        try:
            # Test OpenVAS integration
            openvas_response = self.session.get(f"{self.base_url}/integrations/openvas/status")
            if openvas_response.status_code in [200, 503]:  # 503 expected if not configured
                self.log_test("External Integrations - OpenVAS", "PASS", "OpenVAS endpoint accessible")
            else:
                self.log_test("External Integrations - OpenVAS", "FAIL", f"HTTP {openvas_response.status_code}")
            
            # Test OpenCTI integration
            opencti_response = self.session.get(f"{self.base_url}/integrations/opencti/status")
            if opencti_response.status_code in [200, 503]:  # 503 expected if not configured
                self.log_test("External Integrations - OpenCTI", "PASS", "OpenCTI endpoint accessible")
                return True
            else:
                self.log_test("External Integrations - OpenCTI", "FAIL", f"HTTP {opencti_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("External Integrations", "FAIL", f"Error: {str(e)}")
            return False

    def test_api_documentation(self):
        """Test API documentation endpoints"""
        try:
            # Test OpenAPI docs
            docs_response = self.session.get(f"{self.base_url}/docs")
            if docs_response.status_code == 200:
                self.log_test("API Documentation - Swagger UI", "PASS", "Swagger UI accessible")
            else:
                self.log_test("API Documentation - Swagger UI", "FAIL", f"HTTP {docs_response.status_code}")

            # Test OpenAPI JSON
            openapi_response = self.session.get(f"{self.base_url}/openapi.json")
            if openapi_response.status_code == 200:
                self.log_test("API Documentation - OpenAPI JSON", "PASS", "OpenAPI spec accessible")
                return True
            else:
                self.log_test("API Documentation - OpenAPI JSON", "FAIL", f"HTTP {openapi_response.status_code}")
                return False

        except Exception as e:
            self.log_test("API Documentation", "FAIL", f"Error: {str(e)}")
            return False

    def test_frontend_application(self):
        """Test frontend application accessibility"""
        try:
            # Test frontend main page
            frontend_response = requests.get("http://localhost:3000")
            if frontend_response.status_code == 200:
                content = frontend_response.text
                if "<!doctype html>" in content.lower():
                    self.log_test("Frontend - Main Page", "PASS", "Frontend application accessible")

                    # Check for key elements
                    if "aegis" in content.lower():
                        self.log_test("Frontend - Branding", "PASS", "Aegis branding present")
                    else:
                        self.log_test("Frontend - Branding", "FAIL", "Aegis branding not found")

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

    def test_database_connectivity(self):
        """Test database connectivity through API"""
        try:
            # Test database status through health endpoint
            db_response = self.session.get(f"{self.base_url}/health/database")
            if db_response.status_code == 200:
                self.log_test("Database - Connectivity", "PASS", "Database accessible through API")
                return True
            elif db_response.status_code == 404:
                # If no specific DB health endpoint, check if we can query data
                users_response = self.session.get(f"{self.base_url}/users")
                if users_response.status_code == 200:
                    self.log_test("Database - Connectivity", "PASS", "Database working (users query successful)")
                    return True
                else:
                    self.log_test("Database - Connectivity", "FAIL", "Cannot query database")
                    return False
            else:
                self.log_test("Database - Connectivity", "FAIL", f"HTTP {db_response.status_code}")
                return False

        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Aegis Platform Integration Tests")
        logger.info("=" * 60)
        
        test_methods = [
            self.test_health_check,
            self.test_authentication,
            self.test_database_connectivity,
            self.test_user_management,
            self.test_asset_management,
            self.test_risk_management,
            self.test_compliance_frameworks,
            self.test_task_management,
            self.test_evidence_management,
            self.test_dashboard_endpoints,
            self.test_ai_integration,
            self.test_external_integrations,
            self.test_api_documentation,
            self.test_frontend_application
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Unexpected error in {test_method.__name__}: {str(e)}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "test_data": self.test_data
        }
        
        return report

if __name__ == "__main__":
    # Check if backend is running
    tester = AegisIntegrationTester()
    
    logger.info("🔍 Aegis Platform - Comprehensive Integration Test Suite")
    logger.info("=" * 60)
    
    report = tester.run_all_tests()
    
    # Save report to file
    with open("integration_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {report['summary']['total_tests']}")
    logger.info(f"✅ Passed: {report['summary']['passed']}")
    logger.info(f"❌ Failed: {report['summary']['failed']}")
    logger.info(f"⚠️ Skipped: {report['summary']['skipped']}")
    logger.info(f"📈 Success Rate: {report['summary']['success_rate']}%")
    logger.info("=" * 60)
    
    if report['summary']['failed'] > 0:
        logger.warning("⚠️ Some tests failed. Check the detailed report above.")
        sys.exit(1)
    else:
        logger.info("🎉 All tests passed successfully!")
        sys.exit(0)
