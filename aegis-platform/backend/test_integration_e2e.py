#!/usr/bin/env python3
"""
Comprehensive End-to-End Integration Tests for Aegis Risk Management Platform
Tests core workflows and functionality across all modules
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
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    def test_server_health(self):
        """Test 1: Verify server is running and healthy"""
        try:
            response = self.make_request("GET", "/health")
            if response["success"] and response["data"].get("status") == "healthy":
                self.log_test("Server Health Check", "PASS", f"Server responding - {response['data']}")
                return True
            else:
                self.log_test("Server Health Check", "FAIL", f"Server unhealthy - {response}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", "FAIL", f"Connection failed: {str(e)}")
            return False
    
    def test_risk_management_workflow(self):
        """Test 2: Complete Risk Management Workflow"""
        # Get risks
        response = self.make_request("GET", "/api/v1/risks")
        if response["success"]:
            risks = response["data"].get("items", [])
            if len(risks) > 0:
                self.log_test("Risk Management - List Risks", "PASS", f"Retrieved {len(risks)} risks")
            else:
                self.log_test("Risk Management - List Risks", "FAIL", "No risks found")
                return False
        else:
            self.log_test("Risk Management - List Risks", "FAIL", f"Failed to get risks: {response}")
            return False
        
        # Get specific risk
        risk_id = risks[0]["id"]
        response = self.make_request("GET", f"/api/v1/risks/{risk_id}")
        if response["success"]:
            risk_detail = response["data"]
            self.log_test("Risk Management - Get Risk Detail", "PASS", f"Retrieved risk: {risk_detail.get('risk_name', 'Unknown')}")
        else:
            self.log_test("Risk Management - Get Risk Detail", "FAIL", f"Failed to get risk detail: {response}")
            return False
        
        # Test risk assessment
        assessment_data = {
            "risk_id": risk_id,
            "assessment_name": "E2E Test Assessment",
            "assessor_id": 1,
            "methodology": "quantitative"
        }
        response = self.make_request("POST", "/api/v1/risk-assessments", assessment_data)
        if response["success"]:
            self.log_test("Risk Management - Create Assessment", "PASS", "Assessment created successfully")
        else:
            self.log_test("Risk Management - Create Assessment", "FAIL", f"Failed to create assessment: {response}")
        
        # Test dashboard
        response = self.make_request("GET", "/api/v1/dashboards/risk-summary")
        if response["success"]:
            dashboard = response["data"]
            total_risks = dashboard.get("summary", {}).get("total_risks", 0)
            self.log_test("Risk Management - Dashboard", "PASS", f"Dashboard loaded with {total_risks} total risks")
        else:
            self.log_test("Risk Management - Dashboard", "FAIL", f"Dashboard failed: {response}")
        
        return True
    
    def test_vulnerability_management_workflow(self):
        """Test 3: Vulnerability Management Workflow"""
        # Get vulnerabilities
        response = self.make_request("GET", "/api/v1/vulnerabilities")
        if response["success"]:
            vulns = response["data"].get("items", [])
            self.log_test("Vulnerability Management - List Vulnerabilities", "PASS", f"Retrieved {len(vulns)} vulnerabilities")
        else:
            self.log_test("Vulnerability Management - List Vulnerabilities", "FAIL", f"Failed: {response}")
            return False
        
        # Test vulnerability scanning
        scan_data = {
            "scan_name": "E2E Test Scan",
            "target_assets": ["192.168.1.100", "web-server-01"],
            "scan_type": "comprehensive"
        }
        response = self.make_request("POST", "/api/v1/vulnerability-scans", scan_data)
        if response["success"]:
            self.log_test("Vulnerability Management - Create Scan", "PASS", "Vulnerability scan initiated")
        else:
            self.log_test("Vulnerability Management - Create Scan", "FAIL", f"Scan failed: {response}")
        
        # Test vulnerability dashboard
        response = self.make_request("GET", "/api/v1/dashboards/vulnerability-summary")
        if response["success"]:
            dashboard = response["data"]
            total_vulns = dashboard.get("summary", {}).get("total_vulnerabilities", 0)
            self.log_test("Vulnerability Management - Dashboard", "PASS", f"Dashboard shows {total_vulns} vulnerabilities")
        else:
            self.log_test("Vulnerability Management - Dashboard", "FAIL", f"Dashboard failed: {response}")
        
        return True
    
    def test_compliance_management_workflow(self):
        """Test 4: Compliance Management Workflow"""
        # Get compliance frameworks
        response = self.make_request("GET", "/api/v1/compliance/frameworks")
        if response["success"]:
            frameworks = response["data"].get("items", [])
            self.log_test("Compliance Management - List Frameworks", "PASS", f"Retrieved {len(frameworks)} frameworks")
        else:
            self.log_test("Compliance Management - List Frameworks", "FAIL", f"Failed: {response}")
            return False
        
        # Get compliance assessments
        response = self.make_request("GET", "/api/v1/compliance/assessments")
        if response["success"]:
            assessments = response["data"].get("items", [])
            self.log_test("Compliance Management - List Assessments", "PASS", f"Retrieved {len(assessments)} assessments")
        else:
            self.log_test("Compliance Management - List Assessments", "FAIL", f"Failed: {response}")
        
        # Test compliance dashboard
        response = self.make_request("GET", "/api/v1/dashboards/compliance-summary")
        if response["success"]:
            dashboard = response["data"]
            total_frameworks = dashboard.get("summary", {}).get("total_frameworks", 0)
            self.log_test("Compliance Management - Dashboard", "PASS", f"Dashboard shows {total_frameworks} frameworks")
        else:
            self.log_test("Compliance Management - Dashboard", "FAIL", f"Dashboard failed: {response}")
        
        return True
    
    def test_incident_response_workflow(self):
        """Test 5: Incident Response Workflow"""
        # Get incidents
        response = self.make_request("GET", "/api/v1/incidents")
        if response["success"]:
            incidents = response["data"].get("items", [])
            self.log_test("Incident Response - List Incidents", "PASS", f"Retrieved {len(incidents)} incidents")
        else:
            self.log_test("Incident Response - List Incidents", "FAIL", f"Failed: {response}")
            return False
        
        # Create new incident
        incident_data = {
            "title": "E2E Test Security Incident",
            "description": "Test incident created during end-to-end testing",
            "category": "security_breach",
            "severity": "medium",
            "reported_by": 1,
            "affected_systems": ["test-system"],
            "business_impact": "Test impact"
        }
        response = self.make_request("POST", "/api/v1/incidents", incident_data)
        if response["success"]:
            new_incident_id = response["data"].get("id")
            self.log_test("Incident Response - Create Incident", "PASS", f"Created incident ID: {new_incident_id}")
        else:
            self.log_test("Incident Response - Create Incident", "FAIL", f"Failed: {response}")
            return False
        
        # Test incident classification
        classification_data = {
            "title": "Suspicious network activity detected",
            "description": "Unusual data transfer patterns observed on network",
            "affected_systems": ["network-core"],
            "affected_users_count": 100
        }
        response = self.make_request("POST", "/api/v1/incidents/classify", classification_data)
        if response["success"]:
            classification = response["data"]
            self.log_test("Incident Response - Classification", "PASS", 
                         f"Classified as {classification.get('category', 'unknown')} with {classification.get('severity', 'unknown')} severity")
        else:
            self.log_test("Incident Response - Classification", "FAIL", f"Classification failed: {response}")
        
        return True
    
    def test_post_incident_analysis_workflow(self):
        """Test 6: Post-Incident Analysis and Lessons Learned"""
        # Get post-incident review
        response = self.make_request("GET", "/api/v1/incidents/1/post-incident-review")
        if response["success"]:
            review = response["data"]
            self.log_test("Post-Incident Analysis - Get Review", "PASS", 
                         f"Retrieved review: {review.get('review_name', 'Unknown')}")
        else:
            self.log_test("Post-Incident Analysis - Get Review", "FAIL", f"Failed: {response}")
            return False
        
        # Get action items
        response = self.make_request("GET", "/api/v1/post-incident-reviews/1/action-items")
        if response["success"]:
            action_items = response["data"].get("action_items", [])
            self.log_test("Post-Incident Analysis - Action Items", "PASS", 
                         f"Retrieved {len(action_items)} action items")
        else:
            self.log_test("Post-Incident Analysis - Action Items", "FAIL", f"Failed: {response}")
        
        # Get lessons learned
        response = self.make_request("GET", "/api/v1/lessons-learned")
        if response["success"]:
            lessons = response["data"].get("items", [])
            self.log_test("Post-Incident Analysis - Lessons Learned", "PASS", 
                         f"Retrieved {len(lessons)} lessons learned")
        else:
            self.log_test("Post-Incident Analysis - Lessons Learned", "FAIL", f"Failed: {response}")
        
        # Test lessons learned knowledge base
        response = self.make_request("GET", "/api/v1/lessons-learned/knowledge-base")
        if response["success"]:
            knowledge_base = response["data"].get("items", [])
            self.log_test("Post-Incident Analysis - Knowledge Base", "PASS", 
                         f"Knowledge base contains {len(knowledge_base)} items")
        else:
            self.log_test("Post-Incident Analysis - Knowledge Base", "FAIL", f"Failed: {response}")
        
        return True
    
    def test_asset_management_workflow(self):
        """Test 7: Asset Management Workflow"""
        # Get assets
        response = self.make_request("GET", "/api/v1/assets")
        if response["success"]:
            assets = response["data"].get("items", [])
            self.log_test("Asset Management - List Assets", "PASS", f"Retrieved {len(assets)} assets")
        else:
            self.log_test("Asset Management - List Assets", "FAIL", f"Failed: {response}")
            return False
        
        # Test asset relationships
        response = self.make_request("GET", "/api/v1/asset-relationships/network-graph")
        if response["success"]:
            network = response["data"]
            nodes = network.get("nodes", [])
            self.log_test("Asset Management - Network Graph", "PASS", f"Network graph has {len(nodes)} nodes")
        else:
            self.log_test("Asset Management - Network Graph", "FAIL", f"Failed: {response}")
        
        # Test asset scoring
        response = self.make_request("GET", "/api/v1/assets/1/risk-score")
        if response["success"]:
            score_data = response["data"]
            risk_score = score_data.get("overall_risk_score", 0)
            self.log_test("Asset Management - Risk Scoring", "PASS", f"Asset risk score: {risk_score}")
        else:
            self.log_test("Asset Management - Risk Scoring", "FAIL", f"Failed: {response}")
        
        return True
    
    def test_dashboard_integration(self):
        """Test 8: Dashboard Integration"""
        dashboards = [
            ("/api/v1/dashboards/risk-summary", "Risk Summary"),
            ("/api/v1/dashboards/vulnerability-summary", "Vulnerability Summary"),
            ("/api/v1/dashboards/compliance-summary", "Compliance Summary"),
            ("/api/v1/dashboards/incident-analytics", "Incident Analytics")
        ]
        
        all_passed = True
        for endpoint, name in dashboards:
            response = self.make_request("GET", endpoint)
            if response["success"]:
                self.log_test(f"Dashboard Integration - {name}", "PASS", "Dashboard loaded successfully")
            else:
                self.log_test(f"Dashboard Integration - {name}", "FAIL", f"Failed: {response}")
                all_passed = False
        
        return all_passed
    
    def test_api_performance(self):
        """Test 9: API Performance"""
        test_endpoints = [
            "/api/v1/risks",
            "/api/v1/vulnerabilities", 
            "/api/v1/incidents",
            "/api/v1/assets",
            "/api/v1/dashboards/risk-summary"
        ]
        
        performance_results = []
        for endpoint in test_endpoints:
            start_time = time.time()
            response = self.make_request("GET", endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            performance_results.append({
                "endpoint": endpoint,
                "response_time_ms": response_time,
                "success": response["success"]
            })
            
            if response_time < 1000:  # Less than 1 second
                self.log_test(f"Performance - {endpoint}", "PASS", f"Response time: {response_time:.2f}ms")
            else:
                self.log_test(f"Performance - {endpoint}", "FAIL", f"Slow response time: {response_time:.2f}ms")
        
        return performance_results
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 80)
        print("AEGIS RISK MANAGEMENT PLATFORM - END-TO-END INTEGRATION TESTS")
        print("=" * 80)
        print(f"Test started at: {datetime.now().isoformat()}")
        print(f"Target server: {self.base_url}")
        print("-" * 80)
        
        # Test 1: Server Health
        if not self.test_server_health():
            print("CRITICAL: Server health check failed. Aborting tests.")
            return self.generate_report()
        
        # Test 2-8: Core Functionality
        self.test_risk_management_workflow()
        self.test_vulnerability_management_workflow()
        self.test_compliance_management_workflow()
        self.test_incident_response_workflow()
        self.test_post_incident_analysis_workflow()
        self.test_asset_management_workflow()
        self.test_dashboard_integration()
        
        # Test 9: Performance
        performance_results = self.test_api_performance()
        
        # Generate comprehensive report
        return self.generate_report(performance_results)
    
    def generate_report(self, performance_results=None):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("END-TO-END INTEGRATION TEST REPORT")
        print("=" * 80)
        
        # Summary
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        # Failed tests
        if self.failed_tests > 0:
            print(f"\nFAILED TESTS ({self.failed_tests}):")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test_name']}: {result['details']}")
        
        # Performance summary
        if performance_results:
            print(f"\nPERFORMANCE SUMMARY:")
            avg_response_time = sum(r["response_time_ms"] for r in performance_results) / len(performance_results)
            print(f"  Average Response Time: {avg_response_time:.2f}ms")
            slowest = max(performance_results, key=lambda x: x["response_time_ms"])
            print(f"  Slowest Endpoint: {slowest['endpoint']} ({slowest['response_time_ms']:.2f}ms)")
        
        # Core functionality status
        print(f"\nCORE FUNCTIONALITY STATUS:")
        modules = {
            "Risk Management": any("Risk Management" in t["test_name"] and t["status"] == "PASS" for t in self.test_results),
            "Vulnerability Management": any("Vulnerability Management" in t["test_name"] and t["status"] == "PASS" for t in self.test_results),
            "Compliance Management": any("Compliance Management" in t["test_name"] and t["status"] == "PASS" for t in self.test_results),
            "Incident Response": any("Incident Response" in t["test_name"] and t["status"] == "PASS" for t in self.test_results),
            "Post-Incident Analysis": any("Post-Incident Analysis" in t["test_name"] and t["status"] == "PASS" for t in self.test_results),
            "Asset Management": any("Asset Management" in t["test_name"] and t["status"] == "PASS" for t in self.test_results)
        }
        
        for module, status in modules.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {module}")
        
        # Overall assessment
        overall_health = "HEALTHY" if self.failed_tests == 0 else "ISSUES DETECTED" if self.passed_tests > self.failed_tests else "CRITICAL"
        print(f"\nOVERALL SYSTEM HEALTH: {overall_health}")
        
        # Recommendations
        if self.failed_tests > 0:
            print(f"\nRECOMMENDATIONS:")
            print("  1. Review failed test details above")
            print("  2. Check server logs for error details")
            print("  3. Verify all dependencies are properly installed")
            print("  4. Ensure database connections are working")
        
        print("\n" + "=" * 80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        
        return {
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
                "overall_health": overall_health
            },
            "modules": modules,
            "performance": performance_results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aegis Platform E2E Integration Tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the server")
    parser.add_argument("--output", help="Output file for detailed JSON report")
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = AegisE2ETestSuite(args.url)
    report = test_suite.run_all_tests()
    
    # Save detailed report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed_tests"] == 0 else 1)

if __name__ == "__main__":
    main()