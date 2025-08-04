# Aegis Platform - API Reference

## 🔌 Complete API Documentation

This document provides comprehensive information about the Aegis Risk Management Platform REST API, including authentication, endpoints, request/response formats, and integration examples.

## 📋 Table of Contents

- [Authentication](#authentication)
- [API Overview](#api-overview)
- [Core Endpoints](#core-endpoints)
- [Advanced Endpoints](#advanced-endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [SDKs and Examples](#sdks-and-examples)

## 🔐 Authentication

### JWT Authentication

The Aegis Platform uses JWT (JSON Web Token) based authentication for secure API access.

#### Login Endpoint
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

#### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Using Access Tokens
Include the access token in the Authorization header for all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### API Key Authentication

For service-to-service integration, API keys can be used:

```http
X-API-Key: your-api-key-here
```

## 📊 API Overview

### Base URL
```
Production: https://api.yourcompany.com
Development: http://localhost:8000
```

### API Versioning
All endpoints are versioned with `/api/v1/` prefix.

### Response Format
All responses follow a consistent JSON format:

```json
{
  "data": { ... },           // Response data
  "message": "Success",      // Human-readable message
  "status": "success",       // Status indicator
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Pagination
List endpoints support pagination:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🏢 Core Endpoints

### Users Management

#### Get All Users
```http
GET /api/v1/users
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50, max: 100)
- `role` (string): Filter by user role
- `is_active` (boolean): Filter by active status
- `search` (string): Search in username, email, full_name

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "username": "john.doe",
      "email": "john.doe@company.com",
      "full_name": "John Doe",
      "role": "analyst",
      "department": "IT Security",
      "is_active": true,
      "last_login": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### Create User
```http
POST /api/v1/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "jane.smith",
  "email": "jane.smith@company.com",
  "full_name": "Jane Smith",
  "password": "SecurePassword123!",
  "role": "manager",
  "department": "Risk Management",
  "is_active": true
}
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
Authorization: Bearer {token}
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Jane Smith-Johnson",
  "department": "Cybersecurity",
  "is_active": true
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer {token}
```

### Asset Management

#### Get All Assets
```http
GET /api/v1/assets
Authorization: Bearer {token}
```

**Query Parameters:**
- `asset_type` (string): Filter by asset type
- `criticality` (string): Filter by criticality level
- `owner` (string): Filter by asset owner
- `is_active` (boolean): Filter by active status
- `search` (string): Search in asset name and description

#### Create Asset
```http
POST /api/v1/assets
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Customer Database Server",
  "asset_type": "server",
  "description": "Primary customer data database server",
  "owner": "john.doe",
  "location": "Data Center A",
  "criticality": "critical",
  "ip_address": "192.168.1.100",
  "operating_system": "Ubuntu 20.04 LTS",
  "business_service": "Customer Management",
  "compliance_requirements": ["SOX", "GDPR"],
  "is_active": true
}
```

#### Get Asset by ID
```http
GET /api/v1/assets/{asset_id}
Authorization: Bearer {token}
```

#### Asset Relationships
```http
GET /api/v1/assets/{asset_id}/relationships
Authorization: Bearer {token}
```

### Risk Management

#### Get All Risks
```http
GET /api/v1/risks
Authorization: Bearer {token}
```

**Query Parameters:**
- `category` (string): Risk category filter
- `risk_level` (string): Risk level filter (low, medium, high, critical)
- `status` (string): Risk status filter
- `owner` (string): Risk owner filter
- `created_after` (datetime): Filter risks created after date
- `created_before` (datetime): Filter risks created before date

#### Create Risk
```http
POST /api/v1/risks
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Unauthorized Database Access",
  "description": "Risk of unauthorized access to customer database due to weak authentication controls",
  "category": "cybersecurity",
  "affected_assets": [1, 2, 3],
  "likelihood": 4,
  "impact": 5,
  "risk_level": "high",
  "owner": "security.team",
  "status": "identified",
  "identified_date": "2024-01-15T00:00:00Z",
  "tags": ["database", "authentication", "access control"]
}
```

#### Risk Assessment
```http
POST /api/v1/risks/{risk_id}/assess
Authorization: Bearer {token}
Content-Type: application/json

{
  "likelihood": 3,
  "impact": 4,
  "risk_score": 12,
  "justification": "Updated based on recent security improvements",
  "assessed_by": "jane.smith",
  "assessment_date": "2024-01-15T10:00:00Z"
}
```

#### Risk Treatment
```http
POST /api/v1/risks/{risk_id}/treatment
Authorization: Bearer {token}
Content-Type: application/json

{
  "treatment_type": "mitigate",
  "treatment_plan": "Implement multi-factor authentication for database access",
  "target_risk_level": "low",
  "estimated_cost": 15000,
  "timeline_months": 3,
  "assigned_to": "it.security.team"
}
```

### Assessment Management

#### Get All Assessments
```http
GET /api/v1/assessments
Authorization: Bearer {token}
```

#### Create Assessment
```http
POST /api/v1/assessments
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Q1 2024 NIST CSF Assessment",
  "framework_id": 1,
  "scope": "Enterprise-wide cybersecurity assessment",
  "assessor": "jane.smith",
  "start_date": "2024-01-01T00:00:00Z",
  "target_completion_date": "2024-03-31T23:59:59Z",
  "assessment_type": "internal",
  "status": "planning"
}
```

#### Assessment Controls
```http
GET /api/v1/assessments/{assessment_id}/controls
Authorization: Bearer {token}
```

```http
PUT /api/v1/assessments/{assessment_id}/controls/{control_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "implementation_status": "implemented",
  "effectiveness": "effective",
  "testing_date": "2024-01-15T00:00:00Z",
  "testing_method": "automated_scan",
  "findings": "Control is properly implemented and functioning as expected",
  "evidence_references": ["DOC-001-2024", "SCAN-001-2024"]
}
```

### Task Management

#### Get All Tasks
```http
GET /api/v1/tasks
Authorization: Bearer {token}
```

**Query Parameters:**
- `assignee` (string): Filter by assigned user
- `status` (string): Filter by task status
- `priority` (string): Filter by priority level
- `due_after` (datetime): Tasks due after date
- `due_before` (datetime): Tasks due before date
- `category` (string): Filter by task category

#### Create Task
```http
POST /api/v1/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Implement Database Encryption",
  "description": "Encrypt customer database to meet GDPR requirements",
  "assignee": "john.doe",
  "priority": "high",
  "due_date": "2024-02-15T23:59:59Z",
  "category": "security_improvement",
  "related_risk_id": 5,
  "related_assessment_id": 2,
  "estimated_hours": 40,
  "status": "open"
}
```

#### Update Task Status
```http
PATCH /api/v1/tasks/{task_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "in_progress",
  "progress_percentage": 25,
  "status_comment": "Started implementation phase",
  "updated_by": "john.doe"
}
```

### Evidence Management

#### Upload Evidence
```http
POST /api/v1/evidence
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary file data]
title: "Database Security Policy"
document_type: "policy"
tags: ["database", "security", "policy"]
related_asset_id: 1
related_risk_id: 5
access_level: "internal"
```

#### Get Evidence
```http
GET /api/v1/evidence
Authorization: Bearer {token}
```

#### Download Evidence
```http
GET /api/v1/evidence/{evidence_id}/download
Authorization: Bearer {token}
```

## 🚀 Advanced Endpoints

### Analytics API

#### Get Metrics
```http
GET /api/v1/analytics/metrics
Authorization: Bearer {token}
```

#### Create Custom Metric
```http
POST /api/v1/analytics/metrics
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Critical Vulnerabilities",
  "description": "Number of critical security vulnerabilities",
  "metric_type": "vulnerability_count",
  "category": "security",
  "aggregation_type": "count",
  "target_value": 0,
  "threshold_warning": 5,
  "threshold_critical": 10,
  "unit_of_measure": "count",
  "refresh_frequency": "daily"
}
```

#### Get Dashboard Data
```http
GET /api/v1/analytics/dashboards/{dashboard_id}/data
Authorization: Bearer {token}
```

#### Generate Risk Forecast
```http
GET /api/v1/analytics/forecasts/risk
Authorization: Bearer {token}
```

**Query Parameters:**
- `metrics` (array): Specific metrics to forecast
- `horizon_days` (int): Forecast horizon in days (default: 90)

### Reporting API

#### Get Report Templates
```http
GET /api/v1/analytics/reports/templates
Authorization: Bearer {token}
```

#### Generate Report
```http
POST /api/v1/analytics/reports/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "template_id": 1,
  "title": "Q1 2024 Risk Assessment Report",
  "parameters_used": {
    "date_range": "2024-01-01 to 2024-03-31",
    "scope": "enterprise",
    "include_charts": true
  },
  "format": "PDF"
}
```

#### Get Generated Reports
```http
GET /api/v1/analytics/reports
Authorization: Bearer {token}
```

### AI Services API

#### Get AI Insights
```http
GET /api/v1/ai/insights
Authorization: Bearer {token}
```

**Query Parameters:**
- `context` (string): Context for insights (risks, compliance, security)
- `time_range` (string): Time range for analysis

#### Risk Analysis
```http
POST /api/v1/ai/analyze-risk
Authorization: Bearer {token}
Content-Type: application/json

{
  "risk_description": "Potential data breach due to weak authentication",
  "context": {
    "asset_types": ["database", "web_application"],
    "current_controls": ["password_policy", "network_firewall"],
    "industry": "financial_services"
  }
}
```

### Integration API

#### Configure Integration
```http
POST /api/v1/integrations
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "OpenVAS Scanner",
  "integration_type": "vulnerability_scanner",
  "config": {
    "host": "scanner.company.com",
    "port": 9392,
    "username": "aegis_user",
    "password": "secure_password",
    "scan_frequency": "weekly"
  },
  "is_active": true
}
```

#### Trigger Integration Sync
```http
POST /api/v1/integrations/{integration_id}/sync
Authorization: Bearer {token}
```

## 📝 Request/Response Formats

### Common Data Types

#### DateTime Format
All datetime fields use ISO 8601 format:
```json
"2024-01-15T10:30:00Z"
```

#### Risk Levels
```json
["low", "medium", "high", "critical"]
```

#### User Roles
```json
["viewer", "analyst", "manager", "admin", "super_admin"]
```

#### Asset Types
```json
["server", "workstation", "network_device", "application", "database", "cloud_service"]
```

### Validation Rules

#### Username
- Length: 3-50 characters
- Characters: alphanumeric, underscore, hyphen
- Must be unique

#### Email
- Valid email format
- Must be unique
- Maximum 255 characters

#### Password
- Minimum 12 characters
- Must contain uppercase, lowercase, number, special character
- Cannot be in password history (last 12 passwords)

## ❌ Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": [
      {
        "field": "email",
        "message": "Email address is already in use"
      }
    ]
  },
  "status": "error",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes
- `AUTHENTICATION_FAILED` - Invalid credentials
- `AUTHORIZATION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Request validation failed
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded
- `INTERNAL_ERROR` - Server internal error

## 🚦 Rate Limiting

### Rate Limits
- **Standard users**: 100 requests per minute
- **Service accounts**: 1000 requests per minute
- **Bulk operations**: 10 requests per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

### Rate Limit Exceeded Response
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 60
  },
  "status": "error"
}
```

## 💻 SDKs and Examples

### Python SDK Example
```python
import requests
from datetime import datetime

class AegisAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.login(username, password)
    
    def login(self, username, password):
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        self.session.headers.update({
            "Authorization": f"Bearer {data['access_token']}"
        })
    
    def get_risks(self, **filters):
        response = self.session.get(
            f"{self.base_url}/api/v1/risks",
            params=filters
        )
        return response.json()
    
    def create_risk(self, risk_data):
        response = self.session.post(
            f"{self.base_url}/api/v1/risks",
            json=risk_data
        )
        return response.json()

# Usage
api = AegisAPI("http://localhost:8000", "admin", "password")
risks = api.get_risks(risk_level="high")
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

class AegisAPI {
    constructor(baseURL) {
        this.client = axios.create({
            baseURL: baseURL,
            timeout: 10000
        });
    }
    
    async login(username, password) {
        const response = await this.client.post('/api/v1/auth/login', {
            username,
            password
        });
        
        this.client.defaults.headers.common['Authorization'] = 
            `Bearer ${response.data.access_token}`;
        
        return response.data;
    }
    
    async getRisks(filters = {}) {
        const response = await this.client.get('/api/v1/risks', {
            params: filters
        });
        return response.data;
    }
    
    async createAsset(assetData) {
        const response = await this.client.post('/api/v1/assets', assetData);
        return response.data;
    }
}

// Usage
const api = new AegisAPI('http://localhost:8000');
await api.login('admin', 'password');
const risks = await api.getRisks({ risk_level: 'high' });
```

### cURL Examples

#### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Risk Management
```bash
# Get all risks
curl -X GET "http://localhost:8000/api/v1/risks" \
  -H "Authorization: Bearer $TOKEN"

# Create risk
curl -X POST "http://localhost:8000/api/v1/risks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Vulnerability",
    "category": "cybersecurity",
    "likelihood": 4,
    "impact": 5,
    "status": "identified"
  }'
```

#### File Upload
```bash
# Upload evidence
curl -X POST "http://localhost:8000/api/v1/evidence" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@security_policy.pdf" \
  -F "title=Security Policy Document" \
  -F "document_type=policy"
```

### OpenAPI/Swagger

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Webhooks (Future Enhancement)

Webhook support for real-time notifications:

```json
{
  "url": "https://your-app.com/webhooks/aegis",
  "events": [
    "risk.created",
    "risk.updated", 
    "assessment.completed",
    "task.overdue"
  ],
  "secret": "webhook_secret_key"
}
```

---

This API reference provides comprehensive documentation for integrating with the Aegis Risk Management Platform. For additional examples and support, refer to the interactive documentation at `/docs` or contact the development team.