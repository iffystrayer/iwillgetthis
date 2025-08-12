# User Acceptance Testing (UAT) Setup Guide

**Platform:** Aegis Risk Management Platform v1.0.0  
**UAT Environment:** Production-like staging environment  
**Testing Phase:** Pre-production validation  

---

## 🎯 UAT Overview

### Objectives
- Validate business requirements with actual users
- Confirm system meets operational needs
- Identify usability improvements before production
- Verify workflows match business processes
- Test performance under realistic usage

### Success Criteria
- ✅ All critical business workflows completed successfully
- ✅ User satisfaction score ≥ 8/10
- ✅ Zero critical defects identified
- ✅ Performance meets business requirements
- ✅ Security and compliance requirements validated

---

## 🏗️ UAT Environment Setup

### Infrastructure Configuration

```bash
# Create UAT environment (similar to production but isolated)
cd /opt/aegis-platform

# Copy UAT configuration
cp .env.production .env.uat

# Edit UAT-specific settings
nano .env.uat
```

### UAT Environment Variables (.env.uat)
```bash
# UAT-specific configuration
APP_NAME=Aegis Risk Management Platform (UAT)
ENVIRONMENT=uat
DEBUG=false

# UAT Domain
VITE_API_URL=https://uat-api.yourdomain.com/api/v1
CORS_ORIGINS='["https://uat.yourdomain.com"]'

# UAT Database (separate from production)
DATABASE_URL=postgresql://aegis_user:password@uat-db-host:5432/aegis_uat

# UAT Redis
REDIS_URL=redis://uat-redis-host:6379/0

# Reduced token expiry for testing
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480

# UAT-specific logging
LOG_LEVEL=DEBUG
ENABLE_AUDIT_LOGGING=true

# Test data indicators
UAT_ENVIRONMENT=true
SAMPLE_DATA_ENABLED=true
```

### UAT Docker Compose
```yaml
# docker/docker-compose.uat.yml
version: '3.8'

services:
  backend:
    environment:
      - ENVIRONMENT=uat
      - UAT_MODE=true
    labels:
      - "traefik.http.routers.backend-uat.rule=Host(`uat-api.yourdomain.com`)"
    
  frontend:
    environment:
      - VITE_ENVIRONMENT=uat
      - VITE_UAT_MODE=true
    labels:
      - "traefik.http.routers.frontend-uat.rule=Host(`uat.yourdomain.com`)"
```

---

## 👥 UAT Team & Roles

### UAT Participants

#### Business Users (Primary Testers)
- **Risk Managers** - Test risk assessment workflows
- **Security Analysts** - Test evidence collection and analysis
- **Compliance Officers** - Test framework adherence
- **IT Administrators** - Test user management and system admin
- **Executive Users** - Test dashboards and reporting

#### Support Team
- **UAT Coordinator** - Test planning and execution oversight
- **Technical Support** - Environment and technical issue resolution
- **Business Analyst** - Requirements validation and documentation
- **Training Coordinator** - User training and documentation

### Responsibilities Matrix

| Role | Responsibilities |
|------|-----------------|
| **Risk Manager** | Test risk registration, assessment, mitigation workflows |
| **Security Analyst** | Test evidence upload, analysis, vulnerability tracking |
| **Compliance Officer** | Test framework mapping, control evaluation, audit trails |
| **IT Administrator** | Test user management, system configuration, integrations |
| **Executive User** | Test dashboard views, executive reporting, KPI tracking |
| **UAT Coordinator** | Overall test coordination, issue tracking, sign-off |

---

## 📋 UAT Test Plan

### Phase 1: Core Functionality Testing (Week 1)

#### User Management Testing
```
Test Case ID: UAT-001
Description: User Registration and Role Assignment
Priority: Critical

Steps:
1. Admin creates new user account
2. Assign appropriate role (Admin/Analyst/ReadOnly)
3. User receives invitation email
4. User completes profile setup
5. Verify role-based access permissions

Expected Result: User can access system with correct permissions
Acceptance Criteria: All role permissions work as designed
```

#### Asset Management Testing  
```
Test Case ID: UAT-002
Description: Asset Registration and Management
Priority: Critical

Steps:
1. Register new IT assets in system
2. Categorize assets by type and criticality
3. Update asset information
4. Generate asset inventory report
5. Test asset relationship mapping

Expected Result: Complete asset lifecycle management
Acceptance Criteria: Asset data accurate and accessible
```

#### Risk Assessment Testing
```
Test Case ID: UAT-003
Description: Risk Assessment Workflow
Priority: Critical

Steps:
1. Identify and register new risk
2. Conduct risk assessment scoring
3. Document mitigation strategies
4. Assign risk owner and due dates
5. Track risk status through lifecycle

Expected Result: Complete risk management workflow
Acceptance Criteria: Risk data tracked from identification to closure
```

### Phase 2: Advanced Features Testing (Week 2)

#### Evidence Management Testing
```
Test Case ID: UAT-004
Description: Evidence Collection and Analysis
Priority: High

Steps:
1. Upload various evidence types (docs, images, logs)
2. Tag and categorize evidence
3. Link evidence to specific risks/controls
4. Generate evidence reports
5. Test AI-powered evidence analysis (if configured)

Expected Result: Efficient evidence management
Acceptance Criteria: Evidence properly organized and retrievable
```

#### Compliance Framework Testing
```
Test Case ID: UAT-005
Description: Framework Adherence and Mapping
Priority: High

Steps:
1. Select compliance framework (NIST, ISO27001)
2. Map controls to organizational processes
3. Conduct control assessments
4. Generate compliance reports
5. Track compliance status over time

Expected Result: Framework compliance tracking
Acceptance Criteria: Accurate compliance reporting
```

### Phase 3: Integration & Performance Testing (Week 3)

#### Dashboard and Reporting
```
Test Case ID: UAT-006
Description: Executive Dashboard and Reporting
Priority: High

Steps:
1. Access executive dashboard
2. Review risk KPIs and metrics
3. Generate various reports (executive, detailed, compliance)
4. Export reports in multiple formats
5. Schedule automated report delivery

Expected Result: Comprehensive business intelligence
Acceptance Criteria: Reports accurate and actionable
```

#### System Integration Testing
```
Test Case ID: UAT-007
Description: External System Integration
Priority: Medium

Steps:
1. Test API endpoints for external access
2. Validate data import/export functionality
3. Test SIEM integration (if configured)
4. Verify backup and recovery procedures
5. Test notification systems

Expected Result: Seamless system integration
Acceptance Criteria: All integrations functional
```

---

## 📊 UAT Test Data Setup

### Sample Data Creation Script
```python
# uat_test_data.py
import requests
import json

UAT_API_BASE = "https://uat-api.yourdomain.com/api/v1"

def setup_uat_data():
    """Create realistic test data for UAT"""
    
    # Sample Assets
    assets = [
        {"name": "Web Server Cluster", "type": "server", "criticality": "high"},
        {"name": "Customer Database", "type": "database", "criticality": "critical"},
        {"name": "Employee Laptops", "type": "endpoint", "criticality": "medium"},
        {"name": "Firewall Infrastructure", "type": "network", "criticality": "high"},
        {"name": "Cloud Storage", "type": "storage", "criticality": "medium"}
    ]
    
    # Sample Risks
    risks = [
        {
            "title": "Unencrypted Data Transmission",
            "category": "technical",
            "likelihood": 4,
            "impact": 5,
            "status": "identified"
        },
        {
            "title": "Insufficient Access Controls",
            "category": "administrative", 
            "likelihood": 3,
            "impact": 4,
            "status": "mitigating"
        },
        {
            "title": "Outdated Security Patches",
            "category": "technical",
            "likelihood": 5,
            "impact": 3,
            "status": "open"
        }
    ]
    
    # Sample Users
    users = [
        {"email": "risk.manager@company.com", "role": "analyst", "name": "Risk Manager"},
        {"email": "security.analyst@company.com", "role": "analyst", "name": "Security Analyst"},
        {"email": "compliance.officer@company.com", "role": "analyst", "name": "Compliance Officer"},
        {"email": "executive@company.com", "role": "readonly", "name": "Executive User"}
    ]
    
    return {"assets": assets, "risks": risks, "users": users}

if __name__ == "__main__":
    data = setup_uat_data()
    print("UAT test data generated successfully")
```

---

## 📝 UAT Test Scripts

### User Registration Test
```python
# tests/uat_user_registration.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserRegistration:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        
    def test_admin_creates_user(self):
        # Login as admin
        self.driver.get("https://uat.yourdomain.com/login")
        self.driver.find_element(By.NAME, "email").send_keys("admin@company.com")
        self.driver.find_element(By.NAME, "password").send_keys("admin123")
        self.driver.find_element(By.TYPE, "submit").click()
        
        # Navigate to users page
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Users")))
        self.driver.find_element(By.LINK_TEXT, "Users").click()
        
        # Add new user
        self.driver.find_element(By.TEXT, "Add User").click()
        self.driver.find_element(By.NAME, "fullName").send_keys("Test User")
        self.driver.find_element(By.NAME, "email").send_keys("test.user@company.com")
        
        # Submit form
        self.driver.find_element(By.TEXT, "Create User").click()
        
        # Verify success
        success_msg = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success")))
        assert "User created successfully" in success_msg.text
        
    def teardown_method(self):
        self.driver.quit()
```

---

## 📋 UAT Execution Checklist

### Pre-UAT Checklist
- [ ] UAT environment deployed and stable
- [ ] Test data loaded and verified
- [ ] UAT participants identified and trained
- [ ] Test cases reviewed and approved
- [ ] Issue tracking system configured
- [ ] Communication channels established

### Daily UAT Activities
- [ ] Morning standup with UAT team
- [ ] Execute planned test cases
- [ ] Document issues and feedback
- [ ] Triage and prioritize defects
- [ ] Update test execution status
- [ ] End-of-day status report

### UAT Completion Criteria
- [ ] All critical test cases passed
- [ ] No critical or high-priority defects remain
- [ ] User satisfaction surveys completed
- [ ] Performance benchmarks met
- [ ] Security validation completed
- [ ] Business stakeholder sign-off obtained

---

## 📊 UAT Metrics & Reporting

### Key Metrics to Track
- **Test Coverage**: Percentage of requirements tested
- **Defect Rate**: Number of defects per test case
- **User Satisfaction**: Average user rating (1-10 scale)
- **Performance**: Response times for key workflows
- **Completion Rate**: Percentage of test cases completed

### Daily UAT Report Template
```
UAT Daily Status Report - [Date]

Test Execution Summary:
- Test Cases Planned: [X]
- Test Cases Executed: [X]
- Test Cases Passed: [X]
- Test Cases Failed: [X]
- Test Cases Blocked: [X]

Defects Summary:
- Critical: [X]
- High: [X]
- Medium: [X]
- Low: [X]

Key Accomplishments:
- [List key achievements]

Issues & Blockers:
- [List current issues]

Next Day Plan:
- [List planned activities]
```

---

## ✅ UAT Sign-off Process

### Final UAT Report
Upon completion of UAT, generate a comprehensive report including:

1. **Executive Summary**
   - Overall UAT outcome
   - Key findings and recommendations
   - Go/No-go decision for production

2. **Test Results Summary**
   - Test case execution statistics
   - Defect summary and resolution
   - Performance test results

3. **User Feedback Analysis**
   - User satisfaction scores
   - Usability feedback
   - Recommended improvements

4. **Production Readiness Assessment**
   - Technical readiness verification
   - Business process validation
   - Risk assessment for production deployment

### Sign-off Requirements
- [ ] Business sponsor approval
- [ ] Technical lead approval  
- [ ] Security team approval
- [ ] Compliance team approval (if applicable)
- [ ] UAT coordinator approval

**UAT Completion**: Ready to proceed to Production Deployment

---

**Next Phase**: OAuth2/OIDC Integration (can be done in parallel with UAT)