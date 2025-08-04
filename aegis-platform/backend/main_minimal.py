from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

from config import settings
from database import engine, Base

# Pydantic models for login
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Aegis Risk Management Platform...")
    
    # Create database tables
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Continuing in development mode...")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Aegis Risk Management Platform...")


# Create FastAPI app
app = FastAPI(
    title="Aegis Risk Management Platform",
    version="1.0.0",
    description="Cybersecurity Risk Management Platform",
    lifespan=lifespan,
    debug=True
)

# CORS Configuration - Support dynamic ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Aegis Risk Management Platform",
        "version": "1.0.0",
        "environment": "development",
        "status": "operational"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "database": "connected",
        "environment": "development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}

@app.get("/api/v1/dashboards/overview")
async def get_dashboard_overview():
    """Get dashboard overview with mock data"""
    return {
        "assets": {
            "total": 45,
            "critical": 8
        },
        "risks": {
            "total": 23,
            "high_priority": 8,
            "open": 19
        },
        "tasks": {
            "total": 18,
            "open": 13,
            "overdue": 4
        },
        "assessments": {
            "total": 7,
            "active": 3,
            "completed": 4
        }
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user with mock data"""
    return {
        "id": 1,
        "email": "admin@aegis-platform.com",
        "username": "admin",
        "full_name": "System Administrator",
        "is_active": True,
        "is_superuser": True,
        "roles": [
            {
                "id": 1,
                "name": "admin",
                "description": "Administrator role",
                "permissions": {
                    "dashboard": ["read", "write"],
                    "assets": ["read", "write", "delete"],
                    "risks": ["read", "write", "delete"],
                    "assessments": ["read", "write", "delete"],
                    "tasks": ["read", "write", "delete"],
                    "evidence": ["read", "write", "delete"],
                    "reports": ["read", "write"],
                    "ai_services": ["read", "write"],
                    "users": ["read", "write", "delete"],
                    "integrations": ["read", "write"],
                    "settings": ["read", "write"]
                },
                "is_active": True
            }
        ]
    }

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Simple login endpoint for testing"""
    # Mock authentication - accept admin credentials
    if user_login.username == "admin@aegis-platform.com" and user_login.password == "admin123":
        mock_user = {
            "id": 1,
            "email": "admin@aegis-platform.com",
            "username": "admin",
            "full_name": "System Administrator",
            "is_active": True,
            "is_superuser": True,
            "roles": [
                {
                    "id": 1,
                    "name": "admin",
                    "description": "Administrator role",
                    "permissions": {
                        "dashboard": ["read", "write"],
                        "assets": ["read", "write", "delete"],
                        "risks": ["read", "write", "delete"],
                        "assessments": ["read", "write", "delete"],
                        "tasks": ["read", "write", "delete"],
                        "evidence": ["read", "write", "delete"],
                        "reports": ["read", "write"],
                        "ai_services": ["read", "write"],
                        "users": ["read", "write", "delete"],
                        "integrations": ["read", "write"],
                        "settings": ["read", "write"]
                    },
                    "is_active": True
                }
            ]
        }
        
        return Token(
            access_token="mock-access-token-123",
            refresh_token="mock-refresh-token-456",
            token_type="bearer",
            user=mock_user
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/api/v1/ai/providers/status")
async def get_ai_providers_status():
    """Get AI providers status"""
    return {
        "openai": {
            "enabled": True,
            "status": "healthy",
            "api_key_configured": False,
            "model": "gpt-3.5-turbo",
            "capabilities": {
                "text_generation": True,
                "function_calling": True,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "anthropic": {
            "enabled": False,
            "status": "disabled",
            "api_key_configured": False,
            "model": "claude-3-sonnet",
            "capabilities": {
                "text_generation": True,
                "function_calling": False,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "azure_openai": {
            "enabled": False,
            "status": "disabled",
            "api_key_configured": False,
            "model": "gpt-4-turbo",
            "capabilities": {
                "text_generation": True,
                "function_calling": True,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "total_providers": 14,
        "enabled_providers": 1,
        "ai_features_enabled": True
    }

@app.post("/api/v1/ai/test")
async def test_ai_generation():
    """Test AI text generation with mock response"""
    return {
        "success": True,
        "provider": "mock",
        "response": "This is a mock AI response for testing. The AI provider integration is working correctly.",
        "tokens_used": 25,
        "cost": 0.001,
        "response_time_ms": 1200
    }

# Asset Management Endpoints
from asset_scoring import calculate_asset_criticality, get_criticality_factors_info

@app.get("/api/v1/assets/categories")
async def get_asset_categories():
    """Get all asset categories"""
    return [
        {
            "id": 1,
            "name": "Servers",
            "description": "Physical and virtual servers",
            "color": "#ff6b6b",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Databases",
            "description": "Database systems and instances",
            "color": "#4ecdc4",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 3,
            "name": "Workstations",
            "description": "End-user workstations and laptops",
            "color": "#45b7d1",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 4,
            "name": "Network Devices",
            "description": "Routers, switches, and network infrastructure",
            "color": "#f9ca24",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 5,
            "name": "Applications",
            "description": "Software applications and services",
            "color": "#6c5ce7",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@app.get("/api/v1/assets")
async def get_assets(
    skip: int = 0,
    limit: int = 20,
    search: str = None,
    asset_type: str = None,
    criticality: str = None,
    category_id: int = None
):
    """Get assets with filtering and pagination"""
    # Mock asset data
    assets = [
        {
            "id": 1,
            "name": "Production Web Server",
            "description": "Main production web server hosting customer applications",
            "asset_type": "server",
            "criticality": "critical",
            "category_id": 1,
            "owner_id": 1,
            "ip_address": "192.168.1.100",
            "hostname": "web-prod-01",
            "operating_system": "Ubuntu 22.04 LTS",
            "version": "22.04.3",
            "location": "Data Center 1 - Rack A1",
            "environment": "production",
            "business_unit": "Engineering",
            "status": "active",
            "tags": ["web", "production", "critical", "ubuntu"],
            "is_active": True,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T14:22:00Z"
        },
        {
            "id": 2,
            "name": "Database Server",
            "description": "Primary PostgreSQL database server",
            "asset_type": "database",
            "criticality": "critical",
            "category_id": 2,
            "owner_id": 1,
            "ip_address": "192.168.1.101",
            "hostname": "db-prod-01",
            "operating_system": "CentOS 8",
            "version": "8.5",
            "location": "Data Center 1 - Rack A2",
            "environment": "production",
            "business_unit": "Engineering",
            "status": "active",
            "tags": ["database", "postgresql", "production", "critical"],
            "is_active": True,
            "created_at": "2024-01-10T09:15:00Z",
            "updated_at": "2024-01-18T11:45:00Z"
        },
        {
            "id": 3,
            "name": "Development Workstation",
            "description": "Developer workstation for application development",
            "asset_type": "workstation",
            "criticality": "medium",
            "category_id": 3,
            "owner_id": 2,
            "ip_address": "192.168.1.200",
            "hostname": "dev-ws-01",
            "operating_system": "Windows 11",
            "version": "22H2",
            "location": "Office Building A - Floor 2",
            "environment": "development",
            "business_unit": "Engineering",
            "status": "active",
            "tags": ["workstation", "development", "windows"],
            "is_active": True,
            "created_at": "2024-01-12T13:20:00Z",
            "updated_at": "2024-01-19T16:30:00Z"
        }
    ]
    
    # Apply filters
    filtered_assets = assets
    if search:
        filtered_assets = [a for a in filtered_assets if search.lower() in a["name"].lower() or search.lower() in a["description"].lower()]
    if asset_type:
        filtered_assets = [a for a in filtered_assets if a["asset_type"] == asset_type]
    if criticality:
        filtered_assets = [a for a in filtered_assets if a["criticality"] == criticality]
    if category_id:
        filtered_assets = [a for a in filtered_assets if a["category_id"] == category_id]
    
    # Apply pagination
    paginated_assets = filtered_assets[skip:skip + limit]
    
    return {
        "items": paginated_assets,
        "total": len(filtered_assets),
        "page": skip // limit + 1,
        "size": limit,
        "total_pages": (len(filtered_assets) + limit - 1) // limit
    }

@app.get("/api/v1/assets/{asset_id}")
async def get_asset(asset_id: int):
    """Get specific asset by ID"""
    if asset_id == 1:
        return {
            "id": 1,
            "name": "Production Web Server",
            "description": "Main production web server hosting customer applications",
            "asset_type": "server",
            "criticality": "critical",
            "category_id": 1,
            "category": {
                "id": 1,
                "name": "Servers",
                "description": "Physical and virtual servers",
                "color": "#ff6b6b"
            },
            "owner_id": 1,
            "owner": {
                "id": 1,
                "email": "admin@aegis-platform.com",
                "full_name": "System Administrator"
            },
            "ip_address": "192.168.1.100",
            "hostname": "web-prod-01",
            "operating_system": "Ubuntu 22.04 LTS",
            "version": "22.04.3",
            "location": "Data Center 1 - Rack A1",
            "environment": "production",
            "business_unit": "Engineering",
            "cost_center": "ENG-001",
            "compliance_scope": ["SOC2", "ISO27001"],
            "status": "active",
            "purchase_date": "2023-12-01T00:00:00Z",
            "warranty_expiry": "2026-12-01T00:00:00Z",
            "last_scan_date": "2024-01-20T02:30:00Z",
            "tags": ["web", "production", "critical", "ubuntu"],
            "custom_fields": {
                "backup_schedule": "daily",
                "monitoring_enabled": True,
                "security_patch_level": "up-to-date"
            },
            "is_active": True,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T14:22:00Z"
        }
    else:
        return {"error": "Asset not found", "detail": f"Asset with ID {asset_id} does not exist"}

@app.post("/api/v1/assets")
async def create_asset(asset_data: dict):
    """Create new asset"""
    # Simulate asset creation
    new_asset = {
        "id": 999,  # Mock ID
        "name": asset_data.get("name", "New Asset"),
        "description": asset_data.get("description", ""),
        "asset_type": asset_data.get("asset_type", "other"),
        "criticality": asset_data.get("criticality", "medium"),
        "category_id": asset_data.get("category_id"),
        "owner_id": asset_data.get("owner_id", 1),
        "ip_address": asset_data.get("ip_address"),
        "hostname": asset_data.get("hostname"),
        "operating_system": asset_data.get("operating_system"),
        "location": asset_data.get("location"),
        "environment": asset_data.get("environment", "development"),
        "business_unit": asset_data.get("business_unit"),
        "status": "active",
        "tags": asset_data.get("tags", []),
        "is_active": True,
        "created_at": "2024-01-21T10:00:00Z",
        "updated_at": "2024-01-21T10:00:00Z"
    }
    return new_asset

@app.put("/api/v1/assets/{asset_id}")
async def update_asset(asset_id: int, asset_data: dict):
    """Update existing asset"""
    # Simulate asset update
    updated_asset = {
        "id": asset_id,
        "name": asset_data.get("name", "Updated Asset"),
        "description": asset_data.get("description", "Updated description"),
        "asset_type": asset_data.get("asset_type", "server"),
        "criticality": asset_data.get("criticality", "high"),
        "status": asset_data.get("status", "active"),
        "updated_at": "2024-01-21T10:30:00Z"
    }
    return updated_asset

@app.delete("/api/v1/assets/{asset_id}")
async def delete_asset(asset_id: int):
    """Delete asset (soft delete)"""
    return {
        "success": True,
        "message": f"Asset {asset_id} has been deactivated",
        "asset_id": asset_id,
        "deleted_at": "2024-01-21T10:45:00Z"
    }

@app.post("/api/v1/assets/{asset_id}/calculate-criticality")
async def calculate_asset_criticality_score(asset_id: int):
    """Calculate criticality score for a specific asset"""
    # For demo purposes, get asset data from the mock asset
    if asset_id == 1:
        asset_data = {
            "asset_type": "server",
            "environment": "production",
            "business_unit": "Engineering",
            "compliance_scope": ["SOC2", "ISO27001"],
            "custom_fields": {
                "backup_schedule": "daily",
                "monitoring_enabled": True,
                "security_patch_level": "up-to-date",
                "sla_requirement": "99.9% uptime",
                "recovery_time_objective": "4 hours",
                "revenue_impact_per_hour": "50000",
                "dependent_systems": ["web-frontend", "mobile-app", "api-gateway"]
            }
        }
    else:
        asset_data = {
            "asset_type": "other",
            "environment": "development",
            "business_unit": "Other",
            "compliance_scope": [],
            "custom_fields": {}
        }
    
    try:
        criticality_result = calculate_asset_criticality(asset_data)
        return {
            "asset_id": asset_id,
            "criticality_assessment": criticality_result,
            "success": True
        }
    except Exception as e:
        return {
            "asset_id": asset_id,
            "error": str(e),
            "success": False
        }

@app.get("/api/v1/assets/criticality/factors")
async def get_criticality_factors():
    """Get information about criticality factors and scoring"""
    return get_criticality_factors_info()

@app.post("/api/v1/assets/batch-criticality")
async def calculate_batch_criticality():
    """Calculate criticality scores for all active assets"""
    # Mock implementation for batch processing
    mock_assets = [
        {
            "id": 1,
            "name": "Production Web Server",
            "asset_type": "server",
            "environment": "production",
            "business_unit": "Engineering",
            "compliance_scope": ["SOC2", "ISO27001"],
            "custom_fields": {
                "sla_requirement": "99.9% uptime",
                "recovery_time_objective": "4 hours",
                "revenue_impact_per_hour": "50000",
                "dependent_systems": ["web-frontend", "mobile-app", "api-gateway"]
            }
        },
        {
            "id": 2,
            "name": "Database Server",
            "asset_type": "database",
            "environment": "production",
            "business_unit": "Engineering",
            "compliance_scope": ["SOC2", "ISO27001", "PCI-DSS"],
            "custom_fields": {
                "data_classification": "confidential",
                "sla_requirement": "99.9% uptime",
                "recovery_time_objective": "1 hour",
                "revenue_impact_per_hour": "100000",
                "dependent_systems": ["web-server", "analytics", "reporting"]
            }
        },
        {
            "id": 3,
            "name": "Development Workstation",
            "asset_type": "workstation",
            "environment": "development",
            "business_unit": "Engineering",
            "compliance_scope": [],
            "custom_fields": {
                "data_classification": "internal",
                "recovery_time_objective": "24 hours",
                "revenue_impact_per_hour": "0"
            }
        }
    ]
    
    results = []
    for asset in mock_assets:
        try:
            criticality_result = calculate_asset_criticality(asset)
            results.append({
                "asset_id": asset["id"],
                "asset_name": asset["name"],
                "criticality_assessment": criticality_result,
                "success": True
            })
        except Exception as e:
            results.append({
                "asset_id": asset["id"],
                "asset_name": asset["name"],
                "error": str(e),
                "success": False
            })
    
    return {
        "processed_assets": len(results),
        "successful_assessments": sum(1 for r in results if r["success"]),
        "failed_assessments": sum(1 for r in results if not r["success"]),
        "results": results
    }

# Asset Relationships and Dependencies Endpoints
@app.get("/api/v1/assets/{asset_id}/relationships")
async def get_asset_relationships(asset_id: int):
    """Get relationships for a specific asset"""
    # Mock relationship data
    relationships = [
        {
            "id": 1,
            "source_asset_id": asset_id,
            "target_asset_id": 2,
            "relationship_type": "depends_on",
            "relationship_strength": "critical",
            "description": "Database dependency for data storage",
            "is_validated": True,
            "target_asset": {
                "id": 2,
                "name": "Database Server",
                "asset_type": "database",
                "criticality": "critical"
            }
        },
        {
            "id": 2,
            "source_asset_id": 3,
            "target_asset_id": asset_id,
            "relationship_type": "depends_on",
            "relationship_strength": "strong",
            "description": "Workstation connects to web server",
            "is_validated": True,
            "source_asset": {
                "id": 3,
                "name": "Development Workstation",
                "asset_type": "workstation",
                "criticality": "medium"
            }
        }
    ]
    
    return {
        "asset_id": asset_id,
        "outgoing_relationships": [r for r in relationships if r["source_asset_id"] == asset_id],
        "incoming_relationships": [r for r in relationships if r["target_asset_id"] == asset_id],
        "total_dependencies": 1,
        "total_dependents": 1
    }

@app.get("/api/v1/assets/{asset_id}/dependency-graph")
async def get_asset_dependency_graph(asset_id: int, max_depth: int = 3):
    """Get dependency graph for an asset"""
    if asset_id == 1:
        return {
            "root_asset_id": asset_id,
            "root_asset_name": "Production Web Server",
            "dependencies": [
                {
                    "asset_id": 2,
                    "asset_name": "Database Server",
                    "asset_type": "database",
                    "criticality": "critical",
                    "environment": "production",
                    "level": 1,
                    "relationship_type": "depends_on",
                    "relationship_strength": "critical",
                    "impact_percentage": 90.0
                }
            ],
            "dependents": [
                {
                    "asset_id": 3,
                    "asset_name": "Development Workstation",
                    "asset_type": "workstation",
                    "criticality": "medium",
                    "environment": "development",
                    "level": 1,
                    "relationship_type": "depends_on",
                    "relationship_strength": "strong",
                    "impact_percentage": 50.0
                }
            ],
            "max_depth": 2,
            "total_dependencies": 1,
            "total_dependents": 1,
            "critical_path_assets": [1, 2]
        }
    else:
        return {
            "root_asset_id": asset_id,
            "root_asset_name": "Unknown Asset",
            "dependencies": [],
            "dependents": [],
            "max_depth": 0,
            "total_dependencies": 0,
            "total_dependents": 0,
            "critical_path_assets": []
        }

@app.get("/api/v1/assets/{asset_id}/impact-analysis")
async def get_asset_impact_analysis(asset_id: int, scenario: str = "complete_failure"):
    """Get impact analysis for asset failure scenarios"""
    if asset_id == 1:
        return {
            "asset_id": asset_id,
            "asset_name": "Production Web Server",
            "scenario_name": scenario,
            "affected_assets": [
                {
                    "asset_id": 3,
                    "asset_name": "Development Workstation",
                    "impact_level": "moderate",
                    "estimated_downtime_minutes": 120,
                    "estimated_revenue_impact": 25000.0
                }
            ],
            "affected_services": [
                {
                    "service_name": "Web Application",
                    "impact_level": "high",
                    "affected_users": 1000
                }
            ],
            "estimated_downtime_minutes": 240,
            "estimated_revenue_impact": 50000.0,
            "business_functions_affected": [
                "Customer Services",
                "Revenue Generation",
                "IT Operations",
                "Web Services"
            ],
            "recovery_steps": [
                "1. Isolate failed asset: Production Web Server",
                "2. Assess root cause of failure",
                "3. Activate backup systems if available",
                "4. Notify stakeholders of dependent service impacts",
                "5. Implement temporary workarounds for critical dependents",
                "6. Begin primary recovery procedures",
                "7. Test functionality before bringing back online",
                "8. Gradually restore dependent services",
                "9. Conduct post-incident review"
            ],
            "estimated_recovery_time": 180,
            "scenario_probability": 0.04
        }
    else:
        return {
            "asset_id": asset_id,
            "asset_name": "Unknown Asset",
            "scenario_name": scenario,
            "affected_assets": [],
            "affected_services": [],
            "estimated_downtime_minutes": 0,
            "estimated_revenue_impact": 0.0,
            "business_functions_affected": [],
            "recovery_steps": [],
            "estimated_recovery_time": 0,
            "scenario_probability": 0.01
        }

@app.get("/api/v1/assets/{asset_id}/risk-metrics")
async def get_asset_risk_metrics(asset_id: int):
    """Get risk metrics for an asset"""
    if asset_id == 1:
        return {
            "asset_id": asset_id,
            "asset_name": "Production Web Server",
            "risk_metrics": {
                "single_point_of_failure_risk": 0.6,
                "cascade_failure_risk": 0.4,
                "overall_dependency_risk": 0.5
            },
            "calculated_at": "2024-01-21T15:30:00Z"
        }
    else:
        return {
            "asset_id": asset_id,
            "asset_name": "Unknown Asset",
            "risk_metrics": {
                "single_point_of_failure_risk": 0.1,
                "cascade_failure_risk": 0.1,
                "overall_dependency_risk": 0.1
            },
            "calculated_at": "2024-01-21T15:30:00Z"
        }

@app.post("/api/v1/assets/relationships")
async def create_asset_relationship(relationship_data: dict):
    """Create new asset relationship"""
    return {
        "id": 999,
        "source_asset_id": relationship_data.get("source_asset_id"),
        "target_asset_id": relationship_data.get("target_asset_id"),
        "relationship_type": relationship_data.get("relationship_type", "depends_on"),
        "relationship_strength": relationship_data.get("relationship_strength", "moderate"),
        "description": relationship_data.get("description", ""),
        "is_validated": False,
        "created_at": "2024-01-21T15:30:00Z",
        "success": True
    }

@app.post("/api/v1/assets/network-map")
async def get_network_map(request_data: dict):
    """Get network map for multiple assets"""
    asset_ids = request_data.get("asset_ids", [1, 2, 3])
    
    return {
        "nodes": [
            {
                "id": 1,
                "name": "Production Web Server",
                "type": "server",
                "criticality": "critical",
                "environment": "production",
                "group": "Engineering"
            },
            {
                "id": 2,
                "name": "Database Server",
                "type": "database",
                "criticality": "critical",
                "environment": "production",
                "group": "Engineering"
            },
            {
                "id": 3,
                "name": "Development Workstation",
                "type": "workstation",
                "criticality": "medium",
                "environment": "development",
                "group": "Engineering"
            }
        ],
        "edges": [
            {
                "source": 1,
                "target": 2,
                "type": "depends_on",
                "strength": "critical",
                "description": "Database dependency"
            },
            {
                "source": 3,
                "target": 1,
                "type": "depends_on",
                "strength": "strong",
                "description": "Development access"
            }
        ],
        "statistics": {
            "total_nodes": 3,
            "total_edges": 2,
            "network_density": 0.33
        }
    }

# Asset Import/Export Endpoints
@app.post("/api/v1/assets/export")
async def export_assets(request_data: dict):
    """Export assets to various formats"""
    format = request_data.get("format", "csv")
    asset_ids = request_data.get("asset_ids")
    include_relationships = request_data.get("include_relationships", False)
    include_metadata = request_data.get("include_metadata", True)
    
    # Mock export data
    if format == "csv":
        csv_content = """name,description,asset_type,criticality,category_name,ip_address,hostname,operating_system,environment,business_unit
Production Web Server,Main production web server,server,critical,Servers,192.168.1.100,web-prod-01,Ubuntu 22.04 LTS,production,Engineering
Database Server,Primary PostgreSQL database,database,critical,Databases,192.168.1.101,db-prod-01,CentOS 8,production,Engineering
Development Workstation,Developer workstation,workstation,medium,Workstations,192.168.1.200,dev-ws-01,Windows 11,development,Engineering"""
        
        return {
            "format": "csv",
            "assets_csv": csv_content,
            "asset_count": 3,
            "generated_at": "2024-01-21T16:00:00Z",
            "success": True
        }
    
    elif format == "json":
        return {
            "format": "json",
            "export_metadata": {
                "generated_at": "2024-01-21T16:00:00Z",
                "asset_count": 3,
                "includes_relationships": include_relationships
            },
            "assets": [
                {
                    "id": 1,
                    "name": "Production Web Server",
                    "description": "Main production web server",
                    "asset_type": "server",
                    "criticality": "critical",
                    "ip_address": "192.168.1.100",
                    "hostname": "web-prod-01",
                    "environment": "production",
                    "business_unit": "Engineering"
                },
                {
                    "id": 2,
                    "name": "Database Server", 
                    "description": "Primary PostgreSQL database",
                    "asset_type": "database",
                    "criticality": "critical",
                    "ip_address": "192.168.1.101",
                    "hostname": "db-prod-01",
                    "environment": "production",
                    "business_unit": "Engineering"
                }
            ],
            "success": True
        }
    
    else:
        return {
            "success": False,
            "error": f"Unsupported export format: {format}",
            "supported_formats": ["csv", "json", "xlsx", "xml"]
        }

@app.post("/api/v1/assets/import")
async def import_assets(request_data: dict):
    """Import assets from various formats"""
    format = request_data.get("format", "csv")
    file_content = request_data.get("file_content", "")
    validate_only = request_data.get("validate_only", False)
    update_existing = request_data.get("update_existing", False)
    create_categories = request_data.get("create_categories", True)
    
    # Mock import processing
    if validate_only:
        return {
            "is_valid": True,
            "total_rows": 3,
            "valid_rows": 3,
            "error_count": 0,
            "warning_count": 1,
            "errors": [],
            "warnings": ["Row 2: Asset with name 'Database Server' already exists (ID: 2)"],
            "validation_only": True
        }
    
    # Mock successful import
    return {
        "success": True,
        "total_processed": 3,
        "created_count": 2,
        "updated_count": 1,
        "error_count": 0,
        "errors": [],
        "imported_assets": [
            {
                "id": 4,
                "name": "New Server 1",
                "asset_type": "server",
                "criticality": "medium",
                "created_at": "2024-01-21T16:00:00Z"
            },
            {
                "id": 5,
                "name": "New Server 2", 
                "asset_type": "server",
                "criticality": "high",
                "created_at": "2024-01-21T16:00:00Z"
            }
        ]
    }

@app.get("/api/v1/assets/import/template")
async def get_import_template(format: str = "csv", include_relationships: bool = False):
    """Get import template for assets"""
    
    if format == "csv":
        template_content = """name,description,asset_type,criticality,category_name,ip_address,hostname,operating_system,version,location,environment,business_unit,cost_center,compliance_scope,status,tags,custom_fields
Example Web Server,Production web server hosting main application,server,high,Servers,192.168.1.100,web-prod-01,Ubuntu 22.04 LTS,22.04.3,Data Center 1 - Rack A1,production,Engineering,ENG-001,"[""SOC2"", ""ISO27001""]",active,"[""web"", ""production"", ""critical""]","{""backup_schedule"": ""daily"", ""monitoring_enabled"": true}"
Example Database Server,Primary PostgreSQL database server,database,critical,Databases,192.168.1.101,db-prod-01,CentOS 8,8.5,Data Center 1 - Rack A2,production,Engineering,ENG-001,"[""SOC2"", ""ISO27001"", ""PCI-DSS""]",active,"[""database"", ""postgresql"", ""production""]","{""backup_schedule"": ""hourly"", ""encryption_enabled"": true}\""""
        
        return {
            "format": "csv",
            "template_content": template_content,
            "description": "CSV template with sample asset data",
            "include_relationships": include_relationships
        }
    
    elif format == "json":
        template_data = {
            "assets": [
                {
                    "name": "Example Web Server",
                    "description": "Production web server hosting main application",
                    "asset_type": "server",
                    "criticality": "high",
                    "category_name": "Servers",
                    "ip_address": "192.168.1.100",
                    "hostname": "web-prod-01",
                    "operating_system": "Ubuntu 22.04 LTS",
                    "environment": "production",
                    "business_unit": "Engineering",
                    "tags": ["web", "production", "critical"],
                    "custom_fields": {
                        "backup_schedule": "daily",
                        "monitoring_enabled": True
                    }
                }
            ]
        }
        
        return {
            "format": "json",
            "template_data": template_data,
            "description": "JSON template with sample asset data",
            "include_relationships": include_relationships
        }
    
    else:
        return {
            "success": False,
            "error": f"Unsupported template format: {format}",
            "supported_formats": ["csv", "json", "xlsx", "xml"]
        }

@app.post("/api/v1/assets/bulk-operations")
async def bulk_asset_operations(request_data: dict):
    """Perform bulk operations on assets"""
    operation = request_data.get("operation")  # delete, update, tag, categorize
    asset_ids = request_data.get("asset_ids", [])
    operation_data = request_data.get("operation_data", {})
    
    if operation == "delete":
        return {
            "success": True,
            "operation": "bulk_delete",
            "processed_count": len(asset_ids),
            "deleted_assets": asset_ids,
            "message": f"Successfully deleted {len(asset_ids)} assets"
        }
    
    elif operation == "update":
        return {
            "success": True,
            "operation": "bulk_update",
            "processed_count": len(asset_ids),
            "updated_fields": list(operation_data.keys()),
            "updated_assets": asset_ids,
            "message": f"Successfully updated {len(asset_ids)} assets"
        }
    
    elif operation == "tag":
        tags_to_add = operation_data.get("tags", [])
        return {
            "success": True,
            "operation": "bulk_tag",
            "processed_count": len(asset_ids),
            "tags_added": tags_to_add,
            "tagged_assets": asset_ids,
            "message": f"Successfully tagged {len(asset_ids)} assets with {len(tags_to_add)} tags"
        }
    
    elif operation == "categorize":
        category_id = operation_data.get("category_id")
        return {
            "success": True,
            "operation": "bulk_categorize",
            "processed_count": len(asset_ids),
            "new_category_id": category_id,
            "categorized_assets": asset_ids,
            "message": f"Successfully moved {len(asset_ids)} assets to new category"
        }
    
    else:
        return {
            "success": False,
            "error": f"Unsupported bulk operation: {operation}",
            "supported_operations": ["delete", "update", "tag", "categorize"]
        }

# Risk Register Endpoints
@app.get("/api/v1/risks")
async def get_risks(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    status: str = None,
    priority: str = None,
    owner_id: int = None
):
    """Get risks with filtering and pagination"""
    # Mock risk data
    risks = [
        {
            "id": 1,
            "risk_id": "RISK-2024-001",
            "title": "Cybersecurity Data Breach",
            "description": "Risk of unauthorized access to customer data due to inadequate security controls",
            "category": "security",
            "status": "assessed",
            "inherent_likelihood": "medium",
            "inherent_impact": "major",
            "inherent_score": 7.0,
            "inherent_priority": "high",
            "residual_likelihood": "low",
            "residual_impact": "moderate",
            "residual_score": 5.0,
            "residual_priority": "medium",
            "business_unit": "IT Security",
            "potential_financial_impact_min": 500000,
            "potential_financial_impact_max": 2000000,
            "risk_owner": {
                "id": 1,
                "email": "security.manager@company.com",
                "full_name": "Security Manager"
            },
            "treatment_count": 3,
            "control_count": 5,
            "incident_count": 0,
            "first_identified_date": "2024-01-15T00:00:00Z",
            "last_review_date": "2024-01-20T00:00:00Z",
            "next_review_date": "2024-04-20T00:00:00Z",
            "created_at": "2024-01-15T00:00:00Z"
        },
        {
            "id": 2,
            "risk_id": "RISK-2024-002",
            "title": "Supply Chain Disruption",
            "description": "Risk of critical supplier failure affecting production capacity",
            "category": "operational",
            "status": "treating",
            "inherent_likelihood": "high",
            "inherent_impact": "severe",
            "inherent_score": 9.0,
            "inherent_priority": "critical",
            "residual_likelihood": "medium",
            "residual_impact": "major",
            "residual_score": 7.0,
            "residual_priority": "high",
            "business_unit": "Operations",
            "potential_financial_impact_min": 1000000,
            "potential_financial_impact_max": 5000000,
            "risk_owner": {
                "id": 2,
                "email": "ops.manager@company.com",
                "full_name": "Operations Manager"
            },
            "treatment_count": 2,
            "control_count": 3,
            "incident_count": 1,
            "first_identified_date": "2024-01-10T00:00:00Z",
            "last_review_date": "2024-01-18T00:00:00Z",
            "next_review_date": "2024-03-18T00:00:00Z",
            "created_at": "2024-01-10T00:00:00Z"
        },
        {
            "id": 3,
            "risk_id": "RISK-2024-003",
            "title": "Regulatory Compliance Violation",
            "description": "Risk of non-compliance with GDPR requirements leading to regulatory penalties",
            "category": "compliance",
            "status": "monitoring",
            "inherent_likelihood": "low",
            "inherent_impact": "major",
            "inherent_score": 6.0,
            "inherent_priority": "medium",
            "residual_likelihood": "very_low",
            "residual_impact": "moderate",
            "residual_score": 3.0,
            "residual_priority": "low",
            "business_unit": "Legal & Compliance",
            "potential_financial_impact_min": 100000,
            "potential_financial_impact_max": 1000000,
            "risk_owner": {
                "id": 3,
                "email": "compliance.officer@company.com",
                "full_name": "Compliance Officer"
            },
            "treatment_count": 1,
            "control_count": 4,
            "incident_count": 0,
            "first_identified_date": "2024-01-05T00:00:00Z",
            "last_review_date": "2024-01-25T00:00:00Z",
            "next_review_date": "2024-07-25T00:00:00Z",
            "created_at": "2024-01-05T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_risks = risks
    if category:
        filtered_risks = [r for r in filtered_risks if r["category"] == category]
    if status:
        filtered_risks = [r for r in filtered_risks if r["status"] == status]
    if priority:
        filtered_risks = [r for r in filtered_risks if r["inherent_priority"] == priority]
    if owner_id:
        filtered_risks = [r for r in filtered_risks if r["risk_owner"]["id"] == owner_id]
    
    # Apply pagination
    paginated_risks = filtered_risks[skip:skip + limit]
    
    return {
        "items": paginated_risks,
        "total": len(filtered_risks),
        "page": skip // limit + 1,
        "size": limit,
        "total_pages": (len(filtered_risks) + limit - 1) // limit
    }

@app.get("/api/v1/risks/{risk_id}")
async def get_risk(risk_id: int):
    """Get specific risk by ID"""
    if risk_id == 1:
        return {
            "id": 1,
            "risk_id": "RISK-2024-001",
            "title": "Cybersecurity Data Breach",
            "description": "Risk of unauthorized access to customer data due to inadequate security controls. This risk encompasses various attack vectors including phishing, malware, insider threats, and external attacks targeting our customer database and internal systems.",
            "category": "security",
            "subcategory": "Information Security",
            "tags": ["cybersecurity", "data-protection", "customer-data", "privacy"],
            "status": "assessed",
            "inherent_likelihood": "medium",
            "inherent_impact": "major",
            "inherent_score": 7.0,
            "inherent_priority": "high",
            "residual_likelihood": "low",
            "residual_impact": "moderate",
            "residual_score": 5.0,
            "residual_priority": "medium",
            "business_unit": "IT Security",
            "process_area": "Information Security Management",
            "geographic_scope": "Global",
            "potential_financial_impact_min": 500000,
            "potential_financial_impact_max": 2000000,
            "currency": "USD",
            "risk_horizon": "Short-term",
            "first_identified_date": "2024-01-15T00:00:00Z",
            "last_review_date": "2024-01-20T00:00:00Z",
            "next_review_date": "2024-04-20T00:00:00Z",
            "risk_owner": {
                "id": 1,
                "email": "security.manager@company.com",
                "full_name": "Security Manager"
            },
            "risk_manager": {
                "id": 4,
                "email": "risk.manager@company.com",
                "full_name": "Chief Risk Officer"
            },
            "regulatory_requirements": ["GDPR", "SOX", "ISO27001"],
            "compliance_impact": "Potential regulatory penalties and loss of certifications",
            "external_dependencies": ["Cloud service providers", "Third-party security vendors"],
            "market_conditions_impact": "Increasing cyber threats in current environment",
            "treatment_count": 3,
            "control_count": 5,
            "incident_count": 0,
            "is_active": True,
            "created_at": "2024-01-15T00:00:00Z",
            "updated_at": "2024-01-20T00:00:00Z"
        }
    else:
        return {"error": "Risk not found", "detail": f"Risk with ID {risk_id} does not exist"}

@app.post("/api/v1/risks/{risk_id}/assess")
async def assess_risk(risk_id: int, assessment_data: dict):
    """Perform risk assessment"""
    method = assessment_data.get("method", "simple_multiplication")
    
    return {
        "risk_id": risk_id,
        "assessment_result": {
            "likelihood_score": 6.5,
            "impact_score": 7.0,
            "overall_score": 6.75,
            "priority": "high",
            "confidence_level": 0.8,
            "methodology_used": method,
            "calculation_details": {
                "likelihood_value": "medium",
                "impact_value": "major",
                "context_applied": False,
                "adjustments": {
                    "historical_adjustment": 0.1,
                    "trend_adjustment": 0.0,
                    "business_context_adjustment": 0.15
                }
            }
        },
        "recommendations": [
            "Implement multi-factor authentication",
            "Conduct regular security awareness training",
            "Establish incident response procedures",
            "Review and update access controls"
        ],
        "assessment_id": "ASSESS-2024-001",
        "assessed_at": "2024-01-21T00:00:00Z",
        "success": True
    }

@app.get("/api/v1/risks/dashboard")
async def get_risk_dashboard():
    """Get risk dashboard data"""
    return {
        "summary": {
            "total_risks": 15,
            "critical_risks": 2,
            "high_risks": 5,
            "medium_risks": 6,
            "low_risks": 2,
            "overdue_treatments": 3,
            "upcoming_reviews": 8
        },
        "risks_by_status": {
            "identified": 2,
            "assessed": 8,
            "treating": 4,
            "monitoring": 1,
            "closed": 0
        },
        "risks_by_category": {
            "operational": 6,
            "security": 4,
            "compliance": 3,
            "financial": 1,
            "strategic": 1
        },
        "treatment_effectiveness": {
            "average_likelihood_reduction": 0.25,
            "average_impact_reduction": 0.15,
            "completed_treatments": 12,
            "in_progress_treatments": 8,
            "planned_treatments": 5
        },
        "recent_activities": [
            {
                "type": "risk_created",
                "description": "New cybersecurity risk identified",
                "risk_id": "RISK-2024-004",
                "timestamp": "2024-01-20T14:30:00Z"
            },
            {
                "type": "treatment_completed",
                "description": "Security training program completed",
                "treatment_id": "TREAT-2024-002",
                "timestamp": "2024-01-19T11:15:00Z"
            },
            {
                "type": "risk_reviewed",
                "description": "Supply chain risk reviewed and updated",
                "risk_id": "RISK-2024-002",
                "timestamp": "2024-01-18T16:45:00Z"
            }
        ],
        "risk_trend": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "total_risks": [12, 13, 15, 14, 15, 15],
            "critical_risks": [1, 2, 2, 1, 2, 2],
            "high_risks": [4, 4, 5, 5, 5, 5]
        }
    }

# ================================
# Risk Treatment and Mitigation Endpoints
# ================================

@app.get("/api/v1/risks/{risk_id}/treatments")
async def get_risk_treatments(
    risk_id: int,
    status: str = None,
    strategy: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get treatments for a specific risk"""
    # Mock treatment data
    treatments = [
        {
            "id": 1,
            "treatment_id": "TREAT-2024-001",
            "risk_id": risk_id,
            "title": "Implement Multi-Factor Authentication",
            "description": "Deploy MFA across all critical systems to reduce unauthorized access risk",
            "strategy": "mitigate",
            "status": "in_progress",
            "progress_percentage": 65,
            "planned_start_date": "2024-01-15T00:00:00Z",
            "planned_completion_date": "2024-03-15T00:00:00Z",
            "actual_start_date": "2024-01-20T00:00:00Z",
            "estimated_cost": 50000,
            "actual_cost": 32000,
            "currency": "USD",
            "treatment_owner": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            },
            "expected_likelihood_reduction": 0.4,
            "expected_impact_reduction": 0.2,
            "actual_likelihood_reduction": 0.35,
            "milestone_count": 4,
            "created_at": "2024-01-10T10:00:00Z",
            "updated_at": "2024-01-25T14:30:00Z"
        },
        {
            "id": 2,
            "treatment_id": "TREAT-2024-002",
            "risk_id": risk_id,
            "title": "Security Awareness Training Program",
            "description": "Comprehensive cybersecurity training for all employees to reduce human error risks",
            "strategy": "mitigate",
            "status": "completed",
            "progress_percentage": 100,
            "planned_start_date": "2024-01-01T00:00:00Z",
            "planned_completion_date": "2024-02-01T00:00:00Z",
            "actual_start_date": "2024-01-01T00:00:00Z",
            "actual_completion_date": "2024-01-28T00:00:00Z",
            "estimated_cost": 25000,
            "actual_cost": 23500,
            "currency": "USD",
            "treatment_owner": {
                "id": 5,
                "email": "hr.director@company.com",
                "full_name": "Bob Wilson"
            },
            "expected_likelihood_reduction": 0.3,
            "expected_impact_reduction": 0.1,
            "actual_likelihood_reduction": 0.35,
            "actual_impact_reduction": 0.15,
            "milestone_count": 3,
            "created_at": "2023-12-15T10:00:00Z",
            "updated_at": "2024-01-28T16:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_treatments = treatments
    if status:
        filtered_treatments = [t for t in filtered_treatments if t["status"] == status]
    if strategy:
        filtered_treatments = [t for t in filtered_treatments if t["strategy"] == strategy]
    
    # Apply pagination
    paginated_treatments = filtered_treatments[skip:skip + limit]
    
    return {
        "items": paginated_treatments,
        "total": len(filtered_treatments),
        "skip": skip,
        "limit": limit,
        "total_pages": (len(filtered_treatments) + limit - 1) // limit
    }

@app.post("/api/v1/risks/{risk_id}/treatments")
async def create_risk_treatment(risk_id: int, treatment_data: dict):
    """Create a new treatment for a risk"""
    return {
        "id": 999,
        "treatment_id": "TREAT-2024-999",
        "risk_id": risk_id,
        "title": treatment_data.get("title", "New Treatment"),
        "description": treatment_data.get("description", ""),
        "strategy": treatment_data.get("strategy", "mitigate"),
        "status": "planned",
        "progress_percentage": 0,
        "estimated_cost": treatment_data.get("estimated_cost", 0),
        "currency": treatment_data.get("currency", "USD"),
        "treatment_owner": {
            "id": treatment_data.get("treatment_owner_id", 1),
            "email": "user@company.com",
            "full_name": "Treatment Owner"
        },
        "milestone_count": 0,
        "created_at": "2024-01-25T10:00:00Z",
        "message": "Treatment created successfully"
    }

@app.get("/api/v1/treatments/{treatment_id}")
async def get_treatment(treatment_id: int):
    """Get specific treatment details"""
    if treatment_id == 1:
        return {
            "id": 1,
            "treatment_id": "TREAT-2024-001",
            "risk_id": 1,
            "title": "Implement Multi-Factor Authentication",
            "description": "Deploy MFA across all critical systems to reduce unauthorized access risk. This includes implementing MFA for all admin accounts, critical applications, and remote access systems.",
            "strategy": "mitigate",
            "status": "in_progress",
            "progress_percentage": 65,
            "action_plan": "Phase 1: Pilot MFA on admin accounts (Complete)\nPhase 2: Deploy to critical applications (In Progress)\nPhase 3: Rollout to all users (Planned)\nPhase 4: Integration testing and documentation (Planned)",
            "success_criteria": "100% of critical systems protected with MFA, 95% user adoption rate, zero MFA-related security incidents",
            "resource_requirements": "2 security engineers, 1 project manager, MFA software licenses",
            "planned_start_date": "2024-01-15T00:00:00Z",
            "planned_completion_date": "2024-03-15T00:00:00Z",
            "actual_start_date": "2024-01-20T00:00:00Z",
            "estimated_cost": 50000,
            "actual_cost": 32000,
            "currency": "USD",
            "budget_approved": True,
            "treatment_owner": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            },
            "assigned_team": [3, 7, 12],
            "expected_likelihood_reduction": 0.4,
            "expected_impact_reduction": 0.2,
            "actual_likelihood_reduction": 0.35,
            "dependencies": ["Identity Management System Upgrade", "Policy Update Approval"],
            "constraints": "Must not disrupt business operations, requires user training",
            "monitoring_plan": "Weekly progress reviews, monthly effectiveness assessments, quarterly security metrics analysis",
            "kpis": [
                {"name": "MFA Adoption Rate", "target": 95, "current": 78, "unit": "percent"},
                {"name": "Authentication Failures", "target": 5, "current": 12, "unit": "incidents_per_month"},
                {"name": "User Satisfaction", "target": 80, "current": 75, "unit": "percent"}
            ],
            "milestone_count": 4,
            "created_at": "2024-01-10T10:00:00Z",
            "updated_at": "2024-01-25T14:30:00Z"
        }
    else:
        return {"error": "Treatment not found", "detail": f"Treatment with ID {treatment_id} does not exist"}

@app.put("/api/v1/treatments/{treatment_id}")
async def update_treatment(treatment_id: int, treatment_data: dict):
    """Update treatment details"""
    return {
        "id": treatment_id,
        "message": "Treatment updated successfully",
        "updated_fields": list(treatment_data.keys()),
        "updated_at": "2024-01-25T15:00:00Z"
    }

@app.get("/api/v1/treatments/{treatment_id}/milestones")
async def get_treatment_milestones(treatment_id: int):
    """Get milestones for a treatment"""
    milestones = [
        {
            "id": 1,
            "treatment_id": treatment_id,
            "title": "Pilot MFA Implementation",
            "description": "Deploy MFA for admin accounts and test functionality",
            "target_date": "2024-02-01T00:00:00Z",
            "actual_date": "2024-01-28T00:00:00Z",
            "is_completed": True,
            "completion_notes": "Successfully deployed to 15 admin accounts. No issues reported."
        },
        {
            "id": 2,
            "treatment_id": treatment_id,
            "title": "Critical Applications MFA",
            "description": "Implement MFA for all critical business applications",
            "target_date": "2024-02-15T00:00:00Z",
            "actual_date": None,
            "is_completed": False,
            "completion_notes": None
        },
        {
            "id": 3,
            "treatment_id": treatment_id,
            "title": "User Training and Rollout",
            "description": "Train users and deploy MFA organization-wide",
            "target_date": "2024-03-01T00:00:00Z",
            "actual_date": None,
            "is_completed": False,
            "completion_notes": None
        },
        {
            "id": 4,
            "treatment_id": treatment_id,
            "title": "Integration Testing and Documentation",
            "description": "Final testing and documentation completion",
            "target_date": "2024-03-15T00:00:00Z",
            "actual_date": None,
            "is_completed": False,
            "completion_notes": None
        }
    ]
    
    return {
        "items": milestones,
        "total": len(milestones),
        "completed": len([m for m in milestones if m["is_completed"]]),
        "remaining": len([m for m in milestones if not m["is_completed"]])
    }

@app.post("/api/v1/treatments/{treatment_id}/milestones")
async def create_treatment_milestone(treatment_id: int, milestone_data: dict):
    """Create a new milestone for a treatment"""
    return {
        "id": 999,
        "treatment_id": treatment_id,
        "title": milestone_data.get("title", "New Milestone"),
        "description": milestone_data.get("description", ""),
        "target_date": milestone_data.get("target_date"),
        "is_completed": False,
        "message": "Milestone created successfully"
    }

@app.get("/api/v1/treatments/{treatment_id}/updates")
async def get_treatment_updates(treatment_id: int, limit: int = 50):
    """Get progress updates for a treatment"""
    updates = [
        {
            "id": 1,
            "treatment_id": treatment_id,
            "update_type": "progress",
            "title": "MFA Pilot Phase Complete",
            "description": "Successfully completed MFA pilot for admin accounts. All 15 admin users have been onboarded and trained.",
            "progress_percentage": 65,
            "issues_identified": "Minor user interface confusion with backup codes",
            "actions_taken": "Created additional documentation and video tutorial",
            "next_steps": "Begin rollout to critical applications in next phase",
            "created_at": "2024-01-25T14:30:00Z",
            "creator": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            }
        },
        {
            "id": 2,
            "treatment_id": treatment_id,
            "update_type": "milestone",
            "title": "Pilot Milestone Achieved",
            "description": "Pilot phase milestone completed ahead of schedule",
            "progress_percentage": 25,
            "actions_taken": "Deployed MFA to all admin accounts, conducted training sessions",
            "next_steps": "Proceed to critical applications phase",
            "created_at": "2024-01-28T16:00:00Z",
            "creator": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            }
        }
    ]
    
    return {
        "items": updates[:limit],
        "total": len(updates),
        "limit": limit
    }

@app.post("/api/v1/treatments/{treatment_id}/updates")
async def create_treatment_update(treatment_id: int, update_data: dict):
    """Create a progress update for a treatment"""
    return {
        "id": 999,
        "treatment_id": treatment_id,
        "update_type": update_data.get("update_type", "progress"),
        "title": update_data.get("title", "Progress Update"),
        "description": update_data.get("description", ""),
        "progress_percentage": update_data.get("progress_percentage"),
        "created_at": "2024-01-25T15:00:00Z",
        "message": "Update created successfully"
    }

@app.get("/api/v1/treatments/dashboard")
async def get_treatment_dashboard():
    """Get treatment dashboard summary"""
    return {
        "summary": {
            "total_treatments": 12,
            "in_progress": 7,
            "completed": 3,
            "overdue": 2,
            "planned": 5,
            "on_hold": 1
        },
        "treatments_by_strategy": {
            "mitigate": 8,
            "transfer": 2,
            "accept": 1,
            "avoid": 1
        },
        "treatments_by_status": {
            "planned": 3,
            "in_progress": 5,
            "completed": 2,
            "overdue": 1,
            "on_hold": 1
        },
        "budget_summary": {
            "total_estimated": 500000,
            "total_actual": 280000,
            "remaining_budget": 220000,
            "budget_utilization": 56.0
        },
        "effectiveness_metrics": {
            "average_likelihood_reduction": 0.35,
            "average_impact_reduction": 0.22,
            "on_time_completion_rate": 0.75,
            "budget_adherence_rate": 0.82
        },
        "recent_activity": [
            {
                "type": "treatment_completed",
                "description": "Security awareness training completed",
                "treatment_id": "TREAT-2024-002",
                "timestamp": "2024-01-28T16:00:00Z"
            },
            {
                "type": "milestone_achieved", 
                "description": "MFA pilot phase milestone reached",
                "treatment_id": "TREAT-2024-001",
                "timestamp": "2024-01-28T14:30:00Z"
            }
        ],
        "upcoming_milestones": [
            {
                "treatment_id": "TREAT-2024-001",
                "treatment_title": "Implement Multi-Factor Authentication",
                "milestone_title": "Critical Applications MFA",
                "due_date": "2024-02-15T00:00:00Z",
                "days_remaining": 21
            },
            {
                "treatment_id": "TREAT-2024-003",
                "treatment_title": "Network Segmentation Implementation",
                "milestone_title": "Phase 1 Infrastructure Setup",
                "due_date": "2024-02-20T00:00:00Z",
                "days_remaining": 26
            }
        ]
    }

@app.get("/api/v1/treatments")
async def get_all_treatments(
    status: str = None,
    strategy: str = None,
    owner_id: int = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all treatments with filtering"""
    # Mock data for all treatments
    treatments = [
        {
            "id": 1,
            "treatment_id": "TREAT-2024-001",
            "risk_id": 1,
            "title": "Implement Multi-Factor Authentication",
            "strategy": "mitigate",
            "status": "in_progress",
            "progress_percentage": 65,
            "treatment_owner": {"id": 3, "full_name": "Alice Johnson"},
            "planned_completion_date": "2024-03-15T00:00:00Z"
        },
        {
            "id": 2,
            "treatment_id": "TREAT-2024-002", 
            "risk_id": 1,
            "title": "Security Awareness Training",
            "strategy": "mitigate",
            "status": "completed",
            "progress_percentage": 100,
            "treatment_owner": {"id": 5, "full_name": "Bob Wilson"},
            "actual_completion_date": "2024-01-28T00:00:00Z"
        },
        {
            "id": 3,
            "treatment_id": "TREAT-2024-003",
            "risk_id": 2,
            "title": "Network Segmentation Implementation",
            "strategy": "mitigate", 
            "status": "planned",
            "progress_percentage": 0,
            "treatment_owner": {"id": 7, "full_name": "Charlie Brown"},
            "planned_start_date": "2024-02-01T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_treatments = treatments
    if status:
        filtered_treatments = [t for t in filtered_treatments if t["status"] == status]
    if strategy:
        filtered_treatments = [t for t in filtered_treatments if t["strategy"] == strategy]
    if owner_id:
        filtered_treatments = [t for t in filtered_treatments if t["treatment_owner"]["id"] == owner_id]
    
    # Apply pagination
    paginated_treatments = filtered_treatments[skip:skip + limit]
    
    return {
        "items": paginated_treatments,
        "total": len(filtered_treatments),
        "skip": skip,
        "limit": limit,
        "total_pages": (len(filtered_treatments) + limit - 1) // limit
    }

# ================================
# Risk Reporting and Analytics Endpoints
# ================================

@app.get("/api/v1/reports/risk-heatmap")
async def get_risk_heatmap():
    """Generate risk heatmap data for visualization"""
    return {
        "matrix_data": [
            [
                {"count": 0, "risks": [], "level": "low"},
                {"count": 1, "risks": [{"id": 5, "title": "Minor operational delay"}], "level": "low"},
                {"count": 2, "risks": [{"id": 8, "title": "Process inefficiency"}, {"id": 12, "title": "Resource constraint"}], "level": "medium"},
                {"count": 1, "risks": [{"id": 15, "title": "Service disruption"}], "level": "high"},
                {"count": 0, "risks": [], "level": "critical"}
            ],
            [
                {"count": 1, "risks": [{"id": 3, "title": "Minor compliance gap"}], "level": "low"},
                {"count": 3, "risks": [{"id": 6, "title": "Data processing delay"}, {"id": 9, "title": "System slowdown"}, {"id": 13, "title": "User access issue"}], "level": "medium"},
                {"count": 2, "risks": [{"id": 2, "title": "Supply chain disruption"}, {"id": 11, "title": "Network vulnerability"}], "level": "high"},
                {"count": 1, "risks": [{"id": 4, "title": "Financial system exposure"}], "level": "critical"},
                {"count": 0, "risks": [], "level": "critical"}
            ],
            [
                {"count": 0, "risks": [], "level": "low"},
                {"count": 2, "risks": [{"id": 7, "title": "Configuration drift"}, {"id": 14, "title": "Backup failure"}], "level": "medium"},
                {"count": 1, "risks": [{"id": 1, "title": "Cybersecurity threat"}], "level": "high"},
                {"count": 1, "risks": [{"id": 10, "title": "Critical infrastructure failure"}], "level": "critical"},
                {"count": 0, "risks": [], "level": "critical"}
            ],
            [
                {"count": 0, "risks": [], "level": "low"},
                {"count": 0, "risks": [], "level": "medium"},
                {"count": 1, "risks": [{"id": 16, "title": "Regulatory non-compliance"}], "level": "high"},
                {"count": 0, "risks": [], "level": "critical"},
                {"count": 0, "risks": [], "level": "critical"}
            ],
            [
                {"count": 0, "risks": [], "level": "low"},
                {"count": 0, "risks": [], "level": "medium"},
                {"count": 0, "risks": [], "level": "high"},
                {"count": 0, "risks": [], "level": "critical"},
                {"count": 0, "risks": [], "level": "critical"}
            ]
        ],
        "likelihood_labels": ["Very Low", "Low", "Medium", "High", "Very High"],
        "impact_labels": ["Negligible", "Minor", "Moderate", "Major", "Severe"],
        "total_risks": 16,
        "risk_distribution": {
            "low": 4,
            "medium": 9,
            "high": 6,
            "critical": 2
        }
    }

@app.get("/api/v1/reports/risk-trends")
async def get_risk_trends(
    period: str = "6m",  # 1m, 3m, 6m, 1y
    category: str = None
):
    """Get risk trend analysis over time"""
    
    # Generate trend data based on period
    if period == "1y":
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        risk_counts = [8, 10, 12, 14, 16, 15, 17, 19, 18, 16, 15, 13]
        new_risks = [3, 4, 5, 3, 4, 2, 5, 4, 3, 2, 1, 2]
        closed_risks = [1, 2, 3, 1, 2, 3, 2, 2, 4, 4, 2, 4]
    elif period == "6m":
        labels = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
        risk_counts = [19, 18, 16, 15, 13, 15]
        new_risks = [4, 3, 2, 1, 2, 5]
        closed_risks = [2, 4, 4, 2, 4, 3]
    elif period == "3m":
        labels = ["Nov", "Dec", "Jan"]
        risk_counts = [15, 13, 15]
        new_risks = [1, 2, 5]
        closed_risks = [2, 4, 3]
    else:  # 1m
        labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        risk_counts = [13, 14, 16, 15]
        new_risks = [2, 1, 3, 1]
        closed_risks = [1, 0, 1, 2]
    
    return {
        "trend_data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Total Risks",
                    "data": risk_counts,
                    "borderColor": "#2563eb",
                    "backgroundColor": "rgba(37, 99, 235, 0.1)"
                },
                {
                    "label": "New Risks",
                    "data": new_risks,
                    "borderColor": "#dc2626",
                    "backgroundColor": "rgba(220, 38, 38, 0.1)"
                },
                {
                    "label": "Closed Risks",
                    "data": closed_risks,
                    "borderColor": "#16a34a",
                    "backgroundColor": "rgba(22, 163, 74, 0.1)"
                }
            ]
        },
        "summary": {
            "period": period,
            "total_risks_current": risk_counts[-1],
            "total_risks_previous": risk_counts[0],
            "net_change": risk_counts[-1] - risk_counts[0],
            "new_risks_total": sum(new_risks),
            "closed_risks_total": sum(closed_risks),
            "average_monthly_new": sum(new_risks) / len(new_risks),
            "average_monthly_closed": sum(closed_risks) / len(closed_risks)
        },
        "category_trends": {
            "operational": [6, 7, 6, 5],
            "security": [3, 4, 5, 6],
            "compliance": [2, 2, 3, 2],
            "financial": [1, 1, 1, 2],
            "technical": [1, 0, 1, 0]
        } if not category else None
    }

@app.get("/api/v1/reports/treatment-effectiveness")
async def get_treatment_effectiveness():
    """Analyze treatment effectiveness metrics"""
    return {
        "overall_metrics": {
            "total_treatments": 24,
            "completed_treatments": 18,
            "completion_rate": 0.75,
            "average_time_to_completion": 45.5,  # days
            "budget_utilization": 0.82,
            "on_time_completion_rate": 0.72
        },
        "effectiveness_by_strategy": {
            "mitigate": {
                "count": 16,
                "completion_rate": 0.81,
                "average_likelihood_reduction": 0.42,
                "average_impact_reduction": 0.28,
                "average_cost": 35000,
                "roi": 3.2
            },
            "transfer": {
                "count": 4,
                "completion_rate": 0.75,
                "average_likelihood_reduction": 0.15,
                "average_impact_reduction": 0.65,
                "average_cost": 75000,
                "roi": 2.8
            },
            "accept": {
                "count": 3,
                "completion_rate": 1.0,
                "average_likelihood_reduction": 0.0,
                "average_impact_reduction": 0.0,
                "average_cost": 5000,
                "roi": 1.0
            },
            "avoid": {
                "count": 1,
                "completion_rate": 1.0,
                "average_likelihood_reduction": 1.0,
                "average_impact_reduction": 1.0,
                "average_cost": 120000,
                "roi": 5.5
            }
        },
        "risk_reduction_analysis": {
            "total_inherent_risk_score": 187.5,
            "total_residual_risk_score": 98.2,
            "overall_risk_reduction": 0.476,
            "by_category": {
                "operational": {"inherent": 45.0, "residual": 28.5, "reduction": 0.367},
                "security": {"inherent": 78.0, "residual": 32.1, "reduction": 0.588},
                "compliance": {"inherent": 35.5, "residual": 22.4, "reduction": 0.369},
                "financial": {"inherent": 29.0, "residual": 15.2, "reduction": 0.476}
            }
        },
        "top_performing_treatments": [
            {
                "treatment_id": "TREAT-2024-001",
                "title": "Multi-Factor Authentication Implementation",
                "risk_reduction": 0.65,
                "cost_effectiveness": 4.2,
                "completion_time": 38
            },
            {
                "treatment_id": "TREAT-2024-015",
                "title": "Network Segmentation",
                "risk_reduction": 0.58,
                "cost_effectiveness": 3.8,
                "completion_time": 52
            },
            {
                "treatment_id": "TREAT-2024-008",
                "title": "Employee Security Training",
                "risk_reduction": 0.45,
                "cost_effectiveness": 6.1,
                "completion_time": 25
            }
        ]
    }

@app.get("/api/v1/reports/compliance-dashboard")
async def get_compliance_dashboard():
    """Generate compliance-focused risk dashboard"""
    return {
        "regulatory_frameworks": {
            "GDPR": {
                "total_requirements": 47,
                "compliant": 42,
                "partial": 3,
                "non_compliant": 2,
                "compliance_rate": 0.894,
                "critical_gaps": [
                    {"requirement": "Data breach notification", "gap": "Process automation needed"},
                    {"requirement": "Right to be forgotten", "gap": "Technical implementation pending"}
                ]
            },
            "SOX": {
                "total_requirements": 23,
                "compliant": 20,
                "partial": 2,
                "non_compliant": 1,
                "compliance_rate": 0.870,
                "critical_gaps": [
                    {"requirement": "Financial controls documentation", "gap": "Annual review overdue"}
                ]
            },
            "ISO 27001": {
                "total_requirements": 114,
                "compliant": 95,
                "partial": 12,
                "non_compliant": 7,
                "compliance_rate": 0.833,
                "critical_gaps": [
                    {"requirement": "Incident response procedures", "gap": "Testing and validation needed"},
                    {"requirement": "Supplier security assessment", "gap": "Quarterly reviews missing"}
                ]
            }
        },
        "compliance_trends": {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "gdpr_compliance": [0.82, 0.86, 0.89, 0.894],
            "sox_compliance": [0.78, 0.83, 0.87, 0.870],
            "iso27001_compliance": [0.76, 0.81, 0.83, 0.833]
        },
        "risk_by_regulation": {
            "GDPR": {
                "high_risk": 2,
                "medium_risk": 5,
                "low_risk": 8,
                "total": 15
            },
            "SOX": {
                "high_risk": 1,
                "medium_risk": 3,
                "low_risk": 4,
                "total": 8
            },
            "ISO 27001": {
                "high_risk": 4,
                "medium_risk": 7,
                "low_risk": 12,
                "total": 23
            }
        },
        "upcoming_audits": [
            {
                "framework": "GDPR",
                "audit_type": "Annual Review",
                "scheduled_date": "2024-03-15T00:00:00Z",
                "auditor": "External Compliance Firm",
                "preparation_status": "75%"
            },
            {
                "framework": "SOX",
                "audit_type": "Quarterly Assessment",
                "scheduled_date": "2024-02-28T00:00:00Z",
                "auditor": "Internal Audit Team",
                "preparation_status": "90%"
            }
        ]
    }

@app.get("/api/v1/reports/executive-summary")
async def get_executive_summary():
    """Generate executive-level risk summary report"""
    return {
        "key_metrics": {
            "total_risks": 23,
            "critical_risks": 3,
            "risks_trending_up": 5,
            "risks_trending_down": 8,
            "overall_risk_score": 6.8,
            "risk_score_change": -0.3,  # improvement
            "treatment_completion_rate": 0.75,
            "budget_utilization": 0.82
        },
        "top_risks": [
            {
                "id": 1,
                "title": "Cybersecurity Threat",
                "category": "Security",
                "current_score": 8.5,
                "trend": "stable",
                "owner": "Alice Johnson",
                "status": "treating"
            },
            {
                "id": 4,
                "title": "Financial System Exposure",
                "category": "Financial",
                "current_score": 7.8,
                "trend": "decreasing",
                "owner": "Bob Wilson",
                "status": "monitoring"
            },
            {
                "id": 10,
                "title": "Critical Infrastructure Failure",
                "category": "Operational",
                "current_score": 7.2,
                "trend": "increasing",
                "owner": "Charlie Brown",
                "status": "escalated"
            }
        ],
        "risk_appetite_status": {
            "current_exposure": 6.8,
            "risk_appetite_threshold": 7.5,
            "status": "within_appetite",
            "margin": 0.7
        },
        "strategic_initiatives": [
            {
                "initiative": "Cybersecurity Enhancement Program",
                "progress": 65,
                "expected_risk_reduction": 0.35,
                "investment": 500000,
                "completion_date": "2024-06-30T00:00:00Z"
            },
            {
                "initiative": "Business Continuity Improvement",
                "progress": 40,
                "expected_risk_reduction": 0.25,
                "investment": 300000,
                "completion_date": "2024-09-30T00:00:00Z"
            }
        ],
        "board_recommendations": [
            {
                "priority": "high",
                "recommendation": "Approve additional cybersecurity budget to address emerging threats",
                "rationale": "Current threat landscape requires enhanced protection capabilities",
                "estimated_cost": 200000,
                "expected_benefit": "Reduce cyber risk by 40%"
            },
            {
                "priority": "medium",
                "recommendation": "Establish dedicated risk management committee",
                "rationale": "Improve governance and oversight of enterprise risk management",
                "estimated_cost": 50000,
                "expected_benefit": "Enhanced risk visibility and faster decision making"
            }
        ],
        "quarterly_outlook": {
            "expected_new_risks": 3,
            "risks_planned_for_closure": 5,
            "major_initiatives_completing": 2,
            "anticipated_challenges": [
                "Regulatory compliance deadlines",
                "Resource constraints for security improvements",
                "Market volatility impact on operational risks"
            ]
        }
    }

@app.get("/api/v1/reports/risk-register-export")
async def export_risk_register(
    format: str = "json",  # json, csv, excel
    filters: str = None
):
    """Export risk register data in various formats"""
    
    # Mock comprehensive risk data
    risks_data = [
        {
            "risk_id": "RISK-2024-001",
            "title": "Cybersecurity Threat",
            "description": "Risk of unauthorized access to customer data",
            "category": "Security",
            "status": "treating",
            "inherent_likelihood": "high",
            "inherent_impact": "major",
            "inherent_score": 8.5,
            "residual_likelihood": "medium",
            "residual_impact": "moderate",
            "residual_score": 5.2,
            "risk_owner": "Alice Johnson",
            "identified_date": "2024-01-10T00:00:00Z",
            "last_review_date": "2024-01-25T00:00:00Z",
            "next_review_date": "2024-04-25T00:00:00Z",
            "treatments": [
                {"id": "TREAT-2024-001", "title": "Multi-Factor Authentication", "status": "in_progress"},
                {"id": "TREAT-2024-002", "title": "Security Training", "status": "completed"}
            ]
        },
        {
            "risk_id": "RISK-2024-002",
            "title": "Supply Chain Disruption",
            "description": "Risk of supply chain interruption affecting operations",
            "category": "Operational",
            "status": "monitoring",
            "inherent_likelihood": "medium",
            "inherent_impact": "major",
            "inherent_score": 6.5,
            "residual_likelihood": "low",
            "residual_impact": "moderate",
            "residual_score": 3.8,
            "risk_owner": "Bob Wilson",
            "identified_date": "2024-01-05T00:00:00Z",
            "last_review_date": "2024-01-20T00:00:00Z",
            "next_review_date": "2024-03-20T00:00:00Z",
            "treatments": [
                {"id": "TREAT-2024-005", "title": "Supplier Diversification", "status": "completed"}
            ]
        }
    ]
    
    if format.lower() == "csv":
        return {
            "format": "csv",
            "data": risks_data,
            "headers": ["risk_id", "title", "category", "status", "inherent_score", "residual_score", "risk_owner"],
            "filename": f"risk_register_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "record_count": len(risks_data)
        }
    elif format.lower() == "excel":
        return {
            "format": "excel",
            "data": risks_data,
            "worksheets": ["Risks", "Treatments", "Summary"],
            "filename": f"risk_register_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "record_count": len(risks_data)
        }
    else:  # json
        return {
            "format": "json",
            "data": risks_data,
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_records": len(risks_data),
                "applied_filters": filters,
                "version": "1.0"
            }
        }

@app.get("/api/v1/reports/kpi-dashboard")
async def get_kpi_dashboard():
    """Get key performance indicators for risk management"""
    return {
        "risk_kpis": {
            "total_risks": {
                "value": 23,
                "target": 25,
                "status": "on_track",
                "trend": "decreasing",
                "change": -2
            },
            "critical_risks": {
                "value": 3,
                "target": 5,
                "status": "on_track",
                "trend": "stable",
                "change": 0
            },
            "overdue_reviews": {
                "value": 2,
                "target": 0,
                "status": "attention_needed",
                "trend": "stable",
                "change": 0
            },
            "risk_appetite_utilization": {
                "value": 0.68,
                "target": 0.80,
                "status": "on_track",
                "trend": "stable",
                "change": 0.02
            }
        },
        "treatment_kpis": {
            "completion_rate": {
                "value": 0.75,
                "target": 0.80,
                "status": "attention_needed",
                "trend": "improving",
                "change": 0.05
            },
            "on_time_delivery": {
                "value": 0.72,
                "target": 0.85,
                "status": "below_target",
                "trend": "stable",
                "change": -0.02
            },
            "budget_adherence": {
                "value": 0.82,
                "target": 0.90,
                "status": "attention_needed",
                "trend": "improving",
                "change": 0.08
            },
            "effectiveness_score": {
                "value": 7.8,
                "target": 8.5,
                "status": "attention_needed",
                "trend": "improving",
                "change": 0.3
            }
        },
        "operational_kpis": {
            "incidents_per_month": {
                "value": 2,
                "target": 3,
                "status": "on_track",
                "trend": "decreasing",
                "change": -1
            },
            "time_to_assessment": {
                "value": 5.2,
                "target": 5.0,
                "status": "attention_needed",
                "trend": "stable",
                "change": 0.2
            },
            "stakeholder_satisfaction": {
                "value": 8.1,
                "target": 8.0,
                "status": "on_track",
                "trend": "improving",
                "change": 0.3
            }
        },
        "trend_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "risk_count": [25, 24, 23, 22, 23, 23],
            "completion_rate": [0.65, 0.68, 0.70, 0.72, 0.74, 0.75],
            "budget_utilization": [0.70, 0.74, 0.76, 0.78, 0.80, 0.82]
        }
    }

# ================================
# Risk Approval Workflows and Notifications Endpoints
# ================================

@app.get("/api/v1/approvals/pending")
async def get_pending_approvals(
    approval_type: str = None,  # risk_assessment, treatment_plan, budget_request, etc.
    assignee_id: int = None,
    skip: int = 0,
    limit: int = 100
):
    """Get pending approval requests"""
    
    # Mock pending approvals data
    approvals = [
        {
            "id": 1,
            "approval_id": "APPR-2024-001",
            "type": "risk_assessment",
            "title": "Cybersecurity Risk Assessment Approval",
            "description": "Request approval for updated cybersecurity risk assessment with new threat intelligence",
            "risk_id": 1,
            "risk_title": "Cybersecurity Threat",
            "requested_by": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            },
            "assigned_to": {
                "id": 1,
                "email": "cro@company.com",
                "full_name": "Chief Risk Officer"
            },
            "priority": "high",
            "status": "pending",
            "requested_date": "2024-01-25T09:00:00Z",
            "due_date": "2024-01-30T17:00:00Z",
            "urgency": "urgent",
            "business_justification": "New threat intelligence indicates elevated risk requiring immediate assessment update",
            "attachments": ["threat_analysis.pdf", "risk_update_proposal.docx"]
        },
        {
            "id": 2,
            "approval_id": "APPR-2024-002",
            "type": "treatment_plan",
            "title": "MFA Implementation Budget Approval",
            "description": "Request budget approval for multi-factor authentication implementation project",
            "risk_id": 1,
            "treatment_id": 1,
            "treatment_title": "Implement Multi-Factor Authentication",
            "requested_by": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Alice Johnson"
            },
            "assigned_to": {
                "id": 2,
                "email": "cfo@company.com",
                "full_name": "Chief Financial Officer"
            },
            "priority": "medium",
            "status": "pending",
            "requested_date": "2024-01-22T14:30:00Z",
            "due_date": "2024-02-05T17:00:00Z",
            "requested_amount": 75000,
            "currency": "USD",
            "business_justification": "Critical security enhancement to prevent unauthorized access incidents",
            "expected_roi": 3.2,
            "payback_period": "18 months"
        },
        {
            "id": 3,
            "approval_id": "APPR-2024-003",
            "type": "risk_acceptance",
            "title": "Supply Chain Risk Acceptance",
            "description": "Request approval to accept residual supply chain risk after implementing mitigation measures",
            "risk_id": 2,
            "risk_title": "Supply Chain Disruption",
            "requested_by": {
                "id": 5,
                "email": "operations.manager@company.com",
                "full_name": "Bob Wilson"
            },
            "assigned_to": {
                "id": 1,
                "email": "cro@company.com",
                "full_name": "Chief Risk Officer"
            },
            "priority": "low",
            "status": "pending",
            "requested_date": "2024-01-20T11:15:00Z",
            "due_date": "2024-02-10T17:00:00Z",
            "residual_risk_score": 3.8,
            "risk_appetite_threshold": 4.0,
            "mitigation_summary": "Implemented supplier diversification and emergency response procedures"
        }
    ]
    
    # Apply filters
    filtered_approvals = approvals
    if approval_type:
        filtered_approvals = [a for a in filtered_approvals if a["type"] == approval_type]
    if assignee_id:
        filtered_approvals = [a for a in filtered_approvals if a["assigned_to"]["id"] == assignee_id]
    
    # Apply pagination
    paginated_approvals = filtered_approvals[skip:skip + limit]
    
    return {
        "items": paginated_approvals,
        "total": len(filtered_approvals),
        "skip": skip,
        "limit": limit,
        "summary": {
            "urgent": len([a for a in filtered_approvals if a.get("urgency") == "urgent"]),
            "overdue": len([a for a in filtered_approvals if a["due_date"] < datetime.now().isoformat()]),
            "high_priority": len([a for a in filtered_approvals if a["priority"] == "high"]),
            "total_pending": len(filtered_approvals)
        }
    }

@app.post("/api/v1/approvals/{approval_id}/approve")
async def approve_request(approval_id: int, approval_data: dict):
    """Approve a pending request"""
    return {
        "approval_id": approval_id,
        "status": "approved",
        "approved_by": approval_data.get("approved_by", 1),
        "approval_date": datetime.now().isoformat(),
        "comments": approval_data.get("comments", ""),
        "conditions": approval_data.get("conditions", []),
        "next_steps": approval_data.get("next_steps", []),
        "message": "Request approved successfully",
        "notification_sent": True
    }

@app.post("/api/v1/approvals/{approval_id}/reject")
async def reject_request(approval_id: int, rejection_data: dict):
    """Reject a pending request"""
    return {
        "approval_id": approval_id,
        "status": "rejected",
        "rejected_by": rejection_data.get("rejected_by", 1),
        "rejection_date": datetime.now().isoformat(),
        "reason": rejection_data.get("reason", ""),
        "feedback": rejection_data.get("feedback", ""),
        "resubmission_allowed": rejection_data.get("resubmission_allowed", True),
        "message": "Request rejected",
        "notification_sent": True
    }

@app.post("/api/v1/approvals/{approval_id}/request-changes")
async def request_changes(approval_id: int, change_request_data: dict):
    """Request changes to a pending approval"""
    return {
        "approval_id": approval_id,
        "status": "changes_requested",
        "requested_by": change_request_data.get("requested_by", 1),
        "request_date": datetime.now().isoformat(),
        "requested_changes": change_request_data.get("requested_changes", []),
        "deadline": change_request_data.get("deadline"),
        "message": "Changes requested",
        "notification_sent": True
    }

@app.get("/api/v1/notifications")
async def get_notifications(
    user_id: int = None,
    notification_type: str = None,
    read_status: str = None,  # read, unread, all
    skip: int = 0,
    limit: int = 50
):
    """Get user notifications"""
    
    # Mock notifications data
    notifications = [
        {
            "id": 1,
            "type": "approval_required",
            "title": "Approval Required: Cybersecurity Risk Assessment",
            "message": "A cybersecurity risk assessment requires your approval",
            "related_object_type": "risk_assessment",
            "related_object_id": 1,
            "priority": "high",
            "is_read": False,
            "created_at": "2024-01-25T09:00:00Z",
            "user_id": 1,
            "action_url": "/approvals/1",
            "expires_at": "2024-01-30T17:00:00Z"
        },
        {
            "id": 2,
            "type": "treatment_overdue",
            "title": "Treatment Overdue: Network Security Update",
            "message": "Treatment milestone is 3 days overdue and requires attention",
            "related_object_type": "treatment",
            "related_object_id": 3,
            "priority": "high",
            "is_read": False,
            "created_at": "2024-01-24T15:30:00Z",
            "user_id": 3,
            "action_url": "/treatments/3",
            "expires_at": None
        },
        {
            "id": 3,
            "type": "risk_escalated",
            "title": "Risk Escalated: Critical Infrastructure Failure",
            "message": "Risk has been escalated due to increased severity",
            "related_object_type": "risk",
            "related_object_id": 10,
            "priority": "critical",
            "is_read": True,
            "created_at": "2024-01-23T11:20:00Z",
            "user_id": 1,
            "action_url": "/risks/10",
            "expires_at": None
        },
        {
            "id": 4,
            "type": "review_due",
            "title": "Risk Review Due: Supply Chain Risk",
            "message": "Quarterly risk review is due within 5 days",
            "related_object_type": "risk",
            "related_object_id": 2,
            "priority": "medium",
            "is_read": False,
            "created_at": "2024-01-22T10:00:00Z",
            "user_id": 5,
            "action_url": "/risks/2/review",
            "expires_at": "2024-02-01T17:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_notifications = notifications
    if user_id:
        filtered_notifications = [n for n in filtered_notifications if n["user_id"] == user_id]
    if notification_type:
        filtered_notifications = [n for n in filtered_notifications if n["type"] == notification_type]
    if read_status == "read":
        filtered_notifications = [n for n in filtered_notifications if n["is_read"]]
    elif read_status == "unread":
        filtered_notifications = [n for n in filtered_notifications if not n["is_read"]]
    
    # Apply pagination
    paginated_notifications = filtered_notifications[skip:skip + limit]
    
    return {
        "items": paginated_notifications,
        "total": len(filtered_notifications),
        "unread_count": len([n for n in filtered_notifications if not n["is_read"]]),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: int):
    """Mark a notification as read"""
    return {
        "notification_id": notification_id,
        "is_read": True,
        "read_at": datetime.now().isoformat(),
        "message": "Notification marked as read"
    }

@app.post("/api/v1/notifications/mark-all-read")
async def mark_all_notifications_read(user_id: int):
    """Mark all notifications as read for a user"""
    return {
        "user_id": user_id,
        "marked_read_count": 5,
        "read_at": datetime.now().isoformat(),
        "message": "All notifications marked as read"
    }

@app.get("/api/v1/workflows/approval-templates")
async def get_approval_templates():
    """Get available approval workflow templates"""
    return {
        "templates": [
            {
                "id": 1,
                "name": "Risk Assessment Approval",
                "description": "Standard approval workflow for risk assessments",
                "steps": [
                    {"order": 1, "role": "risk_manager", "required": True, "auto_escalate_days": 3},
                    {"order": 2, "role": "chief_risk_officer", "required": True, "auto_escalate_days": 5}
                ],
                "triggers": ["risk_assessment_update", "new_risk_identification"],
                "sla_hours": 72
            },
            {
                "id": 2,
                "name": "Treatment Budget Approval",
                "description": "Budget approval workflow for risk treatments",
                "steps": [
                    {"order": 1, "role": "department_manager", "required": True, "threshold": 10000},
                    {"order": 2, "role": "chief_financial_officer", "required": True, "threshold": 50000},
                    {"order": 3, "role": "board_approval", "required": True, "threshold": 100000}
                ],
                "triggers": ["treatment_budget_request"],
                "sla_hours": 120
            },
            {
                "id": 3,
                "name": "Risk Acceptance",
                "description": "Approval workflow for accepting residual risks",
                "steps": [
                    {"order": 1, "role": "risk_owner", "required": True},
                    {"order": 2, "role": "chief_risk_officer", "required": True}
                ],
                "triggers": ["risk_acceptance_request"],
                "sla_hours": 48
            }
        ]
    }

@app.post("/api/v1/workflows/initiate")
async def initiate_workflow(workflow_data: dict):
    """Initiate a new approval workflow"""
    return {
        "workflow_id": "WF-2024-001",
        "template_id": workflow_data.get("template_id"),
        "initiated_by": workflow_data.get("initiated_by", 1),
        "status": "initiated",
        "current_step": 1,
        "created_at": datetime.now().isoformat(),
        "estimated_completion": "2024-02-01T17:00:00Z",
        "participants": workflow_data.get("participants", []),
        "message": "Workflow initiated successfully"
    }

@app.get("/api/v1/dashboards/approval-summary")
async def get_approval_dashboard():
    """Get approval workflow dashboard summary"""
    return {
        "summary": {
            "total_pending": 8,
            "urgent_approvals": 2,
            "overdue_approvals": 1,
            "avg_approval_time": 2.5,  # days
            "approval_rate": 0.85,
            "escalated_requests": 1
        },
        "pending_by_type": {
            "risk_assessment": 3,
            "treatment_plan": 2,
            "budget_request": 2,
            "risk_acceptance": 1
        },
        "pending_by_priority": {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 2
        },
        "approval_trends": {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "submitted": [5, 7, 6, 8],
            "approved": [4, 6, 5, 7],
            "rejected": [1, 1, 0, 0],
            "pending": [2, 3, 4, 5]
        },
        "top_approvers": [
            {"name": "Chief Risk Officer", "approved": 12, "avg_time": 1.8},
            {"name": "Chief Financial Officer", "approved": 8, "avg_time": 3.2},
            {"name": "Department Manager", "approved": 15, "avg_time": 1.2}
        ],
        "sla_performance": {
            "within_sla": 0.78,
            "exceeded_sla": 0.22,
            "average_response_time": 2.3  # days
        }
    }

# ================================
# Vulnerability Management System Endpoints
# ================================

@app.get("/api/v1/vulnerabilities")
async def get_vulnerabilities(
    severity: str = None,
    status: str = None,
    vulnerability_type: str = None,
    asset_id: int = None,
    assigned_to: int = None,
    has_exploit: bool = None,
    has_patch: bool = None,
    skip: int = 0,
    limit: int = 100
):
    """Get vulnerabilities with filtering and pagination"""
    
    # Mock vulnerability data
    vulnerabilities = [
        {
            "id": 1,
            "vulnerability_id": "VULN-2024-001",
            "title": "Critical Remote Code Execution in Apache Struts",
            "description": "A critical remote code execution vulnerability exists in Apache Struts 2.x that allows attackers to execute arbitrary code through crafted OGNL expressions.",
            "vulnerability_type": "software",
            "cve_id": "CVE-2024-12345",
            "cwe_id": "CWE-94",
            "severity": "critical",
            "cvss_score": 9.8,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "status": "detected",
            "discovered_date": "2024-01-25T10:30:00Z",
            "discovery_method": "vulnerability_scan",
            "asset": {
                "id": 1,
                "name": "Web Server 01",
                "asset_type": "server",
                "criticality": "critical"
            },
            "affected_software": "Apache Struts",
            "affected_version": "2.5.30",
            "attack_vector": "Network",
            "attack_complexity": "Low",
            "exploit_available": True,
            "exploit_maturity": "Functional",
            "patch_available": True,
            "patch_details": "Upgrade to Apache Struts 2.5.33 or later",
            "priority": "critical",
            "assigned_to": {
                "id": 3,
                "email": "security.admin@company.com",
                "full_name": "Security Administrator"
            },
            "sla_deadline": "2024-01-26T17:00:00Z",
            "remediation_task_count": 1,
            "created_at": "2024-01-25T10:30:00Z"
        },
        {
            "id": 2,
            "vulnerability_id": "VULN-2024-002",
            "title": "SQL Injection in Customer Portal",
            "description": "SQL injection vulnerability in the customer portal login form allows unauthorized data access.",
            "vulnerability_type": "web_application",
            "cwe_id": "CWE-89",
            "severity": "high",
            "cvss_score": 8.1,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N",
            "status": "in_progress",
            "discovered_date": "2024-01-20T14:15:00Z",
            "discovery_method": "penetration_test",
            "asset": {
                "id": 5,
                "name": "Customer Portal",
                "asset_type": "application",
                "criticality": "high"
            },
            "url_path": "/portal/login",
            "attack_vector": "Network",
            "attack_complexity": "Low",
            "exploit_available": False,
            "patch_available": False,
            "workaround_available": True,
            "workaround_details": "Implement parameterized queries and input validation",
            "priority": "high",
            "assigned_to": {
                "id": 7,
                "email": "dev.lead@company.com",
                "full_name": "Development Lead"
            },
            "sla_deadline": "2024-01-27T17:00:00Z",
            "remediation_task_count": 2,
            "created_at": "2024-01-20T14:15:00Z"
        },
        {
            "id": 3,
            "vulnerability_id": "VULN-2024-003",
            "title": "Outdated SSL/TLS Configuration",
            "description": "Server supports weak SSL/TLS protocols and cipher suites that are vulnerable to attack.",
            "vulnerability_type": "configuration",
            "cwe_id": "CWE-326",
            "severity": "medium",
            "cvss_score": 5.9,
            "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N",
            "status": "triaged",
            "discovered_date": "2024-01-22T09:45:00Z",
            "discovery_method": "compliance_scan",
            "asset": {
                "id": 3,
                "name": "Load Balancer",
                "asset_type": "network",
                "criticality": "high"
            },
            "affected_software": "HAProxy",
            "affected_version": "1.8.14",
            "attack_vector": "Network",
            "attack_complexity": "High",
            "exploit_available": False,
            "patch_available": True,
            "patch_details": "Update SSL configuration to disable weak protocols",
            "priority": "medium",
            "assigned_to": {
                "id": 9,
                "email": "network.admin@company.com",
                "full_name": "Network Administrator"
            },
            "sla_deadline": "2024-02-21T17:00:00Z",
            "remediation_task_count": 1,
            "created_at": "2024-01-22T09:45:00Z"
        }
    ]
    
    # Apply filters
    filtered_vulnerabilities = vulnerabilities
    
    if severity:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["severity"] == severity]
    if status:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["status"] == status]
    if vulnerability_type:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["vulnerability_type"] == vulnerability_type]
    if asset_id:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["asset"]["id"] == asset_id]
    if assigned_to:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["assigned_to"]["id"] == assigned_to]
    if has_exploit is not None:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["exploit_available"] == has_exploit]
    if has_patch is not None:
        filtered_vulnerabilities = [v for v in filtered_vulnerabilities if v["patch_available"] == has_patch]
    
    # Apply pagination
    paginated_vulnerabilities = filtered_vulnerabilities[skip:skip + limit]
    
    return {
        "items": paginated_vulnerabilities,
        "total": len(filtered_vulnerabilities),
        "skip": skip,
        "limit": limit,
        "summary": {
            "critical": len([v for v in filtered_vulnerabilities if v["severity"] == "critical"]),
            "high": len([v for v in filtered_vulnerabilities if v["severity"] == "high"]),
            "medium": len([v for v in filtered_vulnerabilities if v["severity"] == "medium"]),
            "low": len([v for v in filtered_vulnerabilities if v["severity"] == "low"]),
            "overdue": len([v for v in filtered_vulnerabilities if v["sla_deadline"] < datetime.now().isoformat()])
        }
    }

@app.post("/api/v1/vulnerabilities")
async def create_vulnerability(vulnerability_data: dict):
    """Create a new vulnerability record"""
    return {
        "id": 999,
        "vulnerability_id": "VULN-2024-999",
        "title": vulnerability_data.get("title", "New Vulnerability"),
        "description": vulnerability_data.get("description", ""),
        "vulnerability_type": vulnerability_data.get("vulnerability_type", "software"),
        "severity": vulnerability_data.get("severity", "medium"),
        "cvss_score": vulnerability_data.get("cvss_score", 5.0),
        "status": "detected",
        "discovered_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "message": "Vulnerability created successfully"
    }

@app.get("/api/v1/vulnerabilities/{vulnerability_id}")
async def get_vulnerability(vulnerability_id: int):
    """Get specific vulnerability details"""
    if vulnerability_id == 1:
        return {
            "id": 1,
            "vulnerability_id": "VULN-2024-001",
            "title": "Critical Remote Code Execution in Apache Struts",
            "description": "A critical remote code execution vulnerability exists in Apache Struts 2.x that allows attackers to execute arbitrary code through crafted OGNL expressions. This vulnerability affects the OGNL (Object-Graph Navigation Language) expression evaluation mechanism and can be exploited by remote attackers without authentication.",
            "vulnerability_type": "software",
            "cve_id": "CVE-2024-12345",
            "cwe_id": "CWE-94",
            "vendor_advisory_id": "ASF-2024-001",
            "external_references": [
                "https://nvd.nist.gov/vuln/detail/CVE-2024-12345",
                "https://struts.apache.org/security/S2-066.html"
            ],
            "severity": "critical",
            "cvss_score": 9.8,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "cvss_version": "3.1",
            "risk_score": 9.5,
            "business_impact_score": 8.8,
            "exploitability_score": 9.9,
            "status": "detected",
            "first_seen": "2024-01-25T10:30:00Z",
            "last_seen": "2024-01-25T10:30:00Z",
            "discovered_date": "2024-01-25T10:30:00Z",
            "discovery_method": "vulnerability_scan",
            "scan_id": 15,
            "reported_by": "Automated Security Scanner",
            "asset": {
                "id": 1,
                "name": "Web Server 01",
                "asset_type": "server",
                "criticality": "critical"
            },
            "affected_systems": ["web-server-01.company.com", "web-server-02.company.com"],
            "network_location": "DMZ",
            "service_port": "8080",
            "affected_software": "Apache Struts",
            "affected_version": "2.5.30",
            "vulnerable_component": "struts2-core",
            "attack_vector": "Network",
            "attack_complexity": "Low",
            "privileges_required": "None",
            "user_interaction": "None",
            "assigned_to": {
                "id": 3,
                "email": "security.admin@company.com",
                "full_name": "Security Administrator"
            },
            "team_assigned": "Security Team",
            "priority": "critical",
            "sla_deadline": "2024-01-26T17:00:00Z",
            "resolution_deadline": "2024-01-26T17:00:00Z",
            "exploit_available": True,
            "exploit_maturity": "Functional",
            "threat_intelligence": {
                "exploit_kits": ["ExploitKit Pro", "BlackHat Toolkit"],
                "active_campaigns": ["Operation WebStrike"],
                "threat_actors": ["APT28", "Criminal Group Alpha"],
                "geographic_targeting": ["North America", "Europe"],
                "industry_targeting": ["Financial Services", "Healthcare"]
            },
            "in_the_wild": True,
            "patch_available": True,
            "patch_details": "Upgrade to Apache Struts 2.5.33 or later. The patch addresses the OGNL injection vulnerability by implementing stricter expression validation and sandboxing.",
            "workaround_available": True,
            "workaround_details": "Disable OGNL expression evaluation or implement web application firewall rules to block malicious payloads.",
            "compliance_frameworks": ["PCI-DSS", "SOX", "GDPR"],
            "regulatory_requirements": ["PCI-DSS 6.2", "GDPR Article 32"],
            "verified": True,
            "verified_by": {
                "id": 5,
                "email": "senior.analyst@company.com",
                "full_name": "Senior Security Analyst"
            },
            "verification_date": "2024-01-25T12:00:00Z",
            "verification_notes": "Confirmed through manual testing. Successful code execution achieved.",
            "false_positive": False,
            "tags": ["critical", "rce", "apache", "struts", "owasp-top10"],
            "custom_fields": {
                "business_unit": "E-commerce",
                "customer_facing": True,
                "revenue_impact": "High"
            },
            "remediation_task_count": 1,
            "assessment_count": 2,
            "exploit_attempt_count": 0,
            "created_at": "2024-01-25T10:30:00Z",
            "updated_at": "2024-01-25T15:45:00Z"
        }
    else:
        return {"error": "Vulnerability not found", "detail": f"Vulnerability with ID {vulnerability_id} does not exist"}

@app.put("/api/v1/vulnerabilities/{vulnerability_id}")
async def update_vulnerability(vulnerability_id: int, vulnerability_data: dict):
    """Update vulnerability details"""
    return {
        "id": vulnerability_id,
        "message": "Vulnerability updated successfully",
        "updated_fields": list(vulnerability_data.keys()),
        "updated_at": datetime.now().isoformat()
    }

@app.post("/api/v1/vulnerabilities/{vulnerability_id}/assess")
async def assess_vulnerability(vulnerability_id: int, assessment_data: dict):
    """Perform vulnerability risk assessment"""
    return {
        "vulnerability_id": vulnerability_id,
        "assessment_id": "ASSESS-VULN-2024-001",
        "base_score": 9.8,
        "temporal_score": 9.5,
        "environmental_score": 9.7,
        "business_risk_score": 8.8,
        "threat_intelligence_score": 9.9,
        "composite_score": 9.5,
        "priority_level": "critical",
        "remediation_urgency": "immediate",
        "confidence_level": 0.95,
        "scoring_method": assessment_data.get("method", "composite"),
        "sla_deadline": "2024-01-26T17:00:00Z",
        "recommendations": [
            "Apply security patch immediately",
            "Implement emergency change process",
            "Monitor for exploitation attempts",
            "Consider temporary service isolation",
            "Verify remediation through re-scanning"
        ],
        "assessment_date": datetime.now().isoformat()
    }

@app.get("/api/v1/vulnerabilities/{vulnerability_id}/remediation-tasks")
async def get_vulnerability_remediation_tasks(vulnerability_id: int):
    """Get remediation tasks for a vulnerability"""
    tasks = [
        {
            "id": 1,
            "task_id": "REM-2024-001",
            "vulnerability_id": vulnerability_id,
            "title": "Emergency Patch Deployment - Apache Struts",
            "description": "Deploy critical security patch for Apache Struts RCE vulnerability",
            "remediation_type": "patch",
            "status": "in_progress",
            "progress_percentage": 75,
            "priority": "critical",
            "assigned_to": {
                "id": 3,
                "email": "security.admin@company.com",
                "full_name": "Security Administrator"
            },
            "planned_start_date": "2024-01-25T18:00:00Z",
            "planned_completion_date": "2024-01-26T06:00:00Z",
            "actual_start_date": "2024-01-25T18:30:00Z",
            "estimated_effort_hours": 8,
            "actual_effort_hours": 6,
            "downtime_required": True,
            "estimated_downtime_hours": 2,
            "approval_required": True,
            "approval_status": "approved",
            "testing_required": True,
            "testing_completed": False,
            "created_at": "2024-01-25T16:00:00Z"
        }
    ]
    
    return {
        "items": tasks,
        "total": len(tasks),
        "vulnerability_id": vulnerability_id
    }

@app.post("/api/v1/vulnerabilities/{vulnerability_id}/remediation-tasks")
async def create_remediation_task(vulnerability_id: int, task_data: dict):
    """Create a new remediation task for a vulnerability"""
    return {
        "id": 999,
        "task_id": "REM-2024-999",
        "vulnerability_id": vulnerability_id,
        "title": task_data.get("title", "New Remediation Task"),
        "description": task_data.get("description", ""),
        "remediation_type": task_data.get("remediation_type", "patch"),
        "status": "not_started",
        "progress_percentage": 0,
        "priority": task_data.get("priority", "medium"),
        "assigned_to": task_data.get("assigned_to"),
        "estimated_effort_hours": task_data.get("estimated_effort_hours"),
        "created_at": datetime.now().isoformat(),
        "message": "Remediation task created successfully"
    }

@app.get("/api/v1/vulnerability-scans")
async def get_vulnerability_scans(
    scan_type: str = None,
    status: str = None,
    initiated_by: int = None,
    skip: int = 0,
    limit: int = 100
):
    """Get vulnerability scans with filtering"""
    
    scans = [
        {
            "id": 1,
            "scan_id": "SCAN-2024-001",
            "name": "Weekly Network Vulnerability Scan",
            "description": "Automated weekly vulnerability scan of the production network",
            "scan_type": "network_scan",
            "scanner_tool": "Nessus Professional",
            "scanner_version": "10.7.2",
            "status": "completed",
            "target_scope": ["10.0.1.0/24", "10.0.2.0/24", "dmz.company.com"],
            "scan_profile": "Full Network Scan",
            "authentication_used": True,
            "credentials_type": "SSH, Windows",
            "start_time": "2024-01-25T02:00:00Z",
            "end_time": "2024-01-25T06:30:00Z",
            "duration_minutes": 270,
            "total_hosts_scanned": 156,
            "total_vulnerabilities": 47,
            "critical_count": 2,
            "high_count": 8,
            "medium_count": 23,
            "low_count": 14,
            "info_count": 12,
            "scan_coverage_percentage": 98.5,
            "false_positive_rate": 0.08,
            "scan_quality_score": 0.92,
            "compliance_frameworks": ["PCI-DSS", "SOC2"],
            "policy_violations": 5,
            "baseline_scan": False,
            "scheduled_scan": True,
            "scan_frequency": "weekly",
            "next_scheduled_scan": "2024-02-01T02:00:00Z",
            "initiator": {
                "id": 1,
                "email": "security.ops@company.com",
                "full_name": "Security Operations"
            },
            "created_at": "2024-01-25T01:55:00Z"
        },
        {
            "id": 2,
            "scan_id": "SCAN-2024-002",
            "name": "Web Application Security Assessment",
            "description": "Comprehensive security assessment of customer-facing web applications",
            "scan_type": "web_app_scan",
            "scanner_tool": "OWASP ZAP",
            "scanner_version": "2.14.0",
            "status": "running",
            "target_scope": ["https://portal.company.com", "https://api.company.com"],
            "scan_profile": "OWASP Top 10 Assessment",
            "authentication_used": True,
            "credentials_type": "OAuth2",
            "start_time": "2024-01-26T10:00:00Z",
            "end_time": None,
            "duration_minutes": None,
            "total_hosts_scanned": 2,
            "total_vulnerabilities": 0,
            "compliance_frameworks": ["OWASP"],
            "baseline_scan": False,
            "scheduled_scan": False,
            "initiator": {
                "id": 7,
                "email": "appsec.team@company.com", 
                "full_name": "Application Security Team"
            },
            "created_at": "2024-01-26T09:55:00Z"
        }
    ]
    
    # Apply filters
    filtered_scans = scans
    if scan_type:
        filtered_scans = [s for s in filtered_scans if s["scan_type"] == scan_type]
    if status:
        filtered_scans = [s for s in filtered_scans if s["status"] == status]
    if initiated_by:
        filtered_scans = [s for s in filtered_scans if s["initiator"]["id"] == initiated_by]
    
    # Apply pagination
    paginated_scans = filtered_scans[skip:skip + limit]
    
    return {
        "items": paginated_scans,
        "total": len(filtered_scans),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/vulnerability-scans")
async def create_vulnerability_scan(scan_data: dict):
    """Initiate a new vulnerability scan"""
    return {
        "id": 999,
        "scan_id": "SCAN-2024-999",
        "name": scan_data.get("name", "New Vulnerability Scan"),
        "description": scan_data.get("description", ""),
        "scan_type": scan_data.get("scan_type", "network_scan"),
        "target_scope": scan_data.get("target_scope", []),
        "status": "initiated",
        "start_time": datetime.now().isoformat(),
        "scheduled_scan": scan_data.get("scheduled_scan", False),
        "created_at": datetime.now().isoformat(),
        "message": "Vulnerability scan initiated successfully"
    }

@app.get("/api/v1/vulnerability-scans/{scan_id}")
async def get_vulnerability_scan(scan_id: int):
    """Get specific vulnerability scan details"""
    if scan_id == 1:
        return {
            "id": 1,
            "scan_id": "SCAN-2024-001",
            "name": "Weekly Network Vulnerability Scan",
            "description": "Automated weekly vulnerability scan of the production network infrastructure to identify security vulnerabilities and compliance issues.",
            "scan_type": "network_scan",
            "scanner_tool": "Nessus Professional",
            "scanner_version": "10.7.2",
            "status": "completed",
            "target_scope": ["10.0.1.0/24", "10.0.2.0/24", "dmz.company.com"],
            "scan_profile": "Full Network Scan with Credentials",
            "authentication_used": True,
            "credentials_type": "SSH, Windows, SNMP",
            "start_time": "2024-01-25T02:00:00Z",
            "end_time": "2024-01-25T06:30:00Z",
            "duration_minutes": 270,
            "total_hosts_scanned": 156,
            "hosts_alive": 142,
            "hosts_with_vulnerabilities": 89,
            "total_vulnerabilities": 47,
            "critical_count": 2,
            "high_count": 8,
            "medium_count": 23,
            "low_count": 14,
            "info_count": 12,
            "new_vulnerabilities": 5,
            "resolved_vulnerabilities": 3,
            "scan_coverage_percentage": 98.5,
            "false_positive_rate": 0.08,
            "scan_quality_score": 0.92,
            "compliance_frameworks": ["PCI-DSS", "SOC2", "NIST"],
            "policy_violations": 5,
            "pci_dss_compliance_score": 0.87,
            "raw_output_file": "/scans/SCAN-2024-001-raw.xml",
            "report_file": "/reports/SCAN-2024-001-report.pdf",
            "baseline_scan": False,
            "comparison_scan_id": None,
            "scheduled_scan": True,
            "scan_frequency": "weekly",
            "next_scheduled_scan": "2024-02-01T02:00:00Z",
            "auto_remediation_enabled": False,
            "scan_notes": "Scan completed successfully. Notable findings include critical RCE vulnerability in web servers.",
            "tags": ["production", "weekly", "automated"],
            "initiator": {
                "id": 1,
                "email": "security.ops@company.com",
                "full_name": "Security Operations Team"
            },
            "vulnerability_summary": [
                {"severity": "critical", "count": 2, "examples": ["CVE-2024-12345", "CVE-2024-12346"]},
                {"severity": "high", "count": 8, "examples": ["CVE-2024-11111", "CVE-2024-11112"]},
                {"severity": "medium", "count": 23, "examples": ["CVE-2024-10001", "CVE-2024-10002"]},
                {"severity": "low", "count": 14, "examples": ["CVE-2024-09001", "CVE-2024-09002"]}
            ],
            "created_at": "2024-01-25T01:55:00Z",
            "updated_at": "2024-01-25T06:35:00Z"
        }
    else:
        return {"error": "Scan not found", "detail": f"Vulnerability scan with ID {scan_id} does not exist"}

@app.get("/api/v1/dashboards/vulnerability-summary")
async def get_vulnerability_dashboard():
    """Get vulnerability management dashboard summary"""
    return {
        "summary": {
            "total_vulnerabilities": 127,
            "critical_vulnerabilities": 8,
            "high_vulnerabilities": 23,
            "medium_vulnerabilities": 67,
            "low_vulnerabilities": 29,
            "new_last_7_days": 12,
            "remediated_last_7_days": 18,
            "overdue_remediations": 5,
            "sla_violations": 3,
            "false_positives": 7
        },
        "vulnerabilities_by_type": {
            "software": 45,
            "configuration": 32,
            "web_application": 28,
            "network": 15,
            "authentication": 7
        },
        "vulnerabilities_by_status": {
            "detected": 15,
            "confirmed": 23,
            "triaged": 31,
            "in_progress": 42,
            "patched": 12,
            "mitigated": 4
        },
        "top_vulnerable_assets": [
            {"asset_name": "Web Server 01", "vulnerability_count": 12, "critical_count": 2},
            {"asset_name": "Database Server", "vulnerability_count": 8, "critical_count": 1},
            {"asset_name": "API Gateway", "vulnerability_count": 7, "critical_count": 1},
            {"asset_name": "Load Balancer", "vulnerability_count": 5, "critical_count": 0}
        ],
        "exploitation_metrics": {
            "exploits_available": 23,
            "active_exploits": 8,
            "in_the_wild": 3,
            "exploit_maturity_distribution": {
                "functional": 8,
                "proof_of_concept": 12,
                "unproven": 3
            }
        },
        "remediation_metrics": {
            "average_time_to_patch_critical": 1.2,  # days
            "average_time_to_patch_high": 5.8,
            "patches_available": 78,
            "workarounds_available": 45,
            "remediation_success_rate": 0.89
        },
        "compliance_status": {
            "pci_dss_compliance": 0.92,
            "nist_compliance": 0.87,
            "iso27001_compliance": 0.89,
            "policy_violations": 8
        },
        "threat_intelligence": {
            "cves_with_active_campaigns": 5,
            "threat_actor_targeting": 12,
            "geographic_risk_score": 7.2,
            "industry_risk_score": 8.1
        },
        "scan_metrics": {
            "total_scans_last_30_days": 28,
            "successful_scans": 26,
            "failed_scans": 2,
            "average_scan_duration": 185,  # minutes
            "scan_coverage": 0.94
        },
        "recent_critical_findings": [
            {
                "vulnerability_id": "VULN-2024-001",
                "title": "Apache Struts RCE",
                "cvss_score": 9.8,
                "discovered_date": "2024-01-25T10:30:00Z"
            },
            {
                "vulnerability_id": "VULN-2024-005",
                "title": "WordPress SQL Injection",
                "cvss_score": 9.1,
                "discovered_date": "2024-01-24T15:20:00Z"
            }
        ],
        "trend_data": {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "new_vulnerabilities": [15, 12, 18, 22],
            "remediated_vulnerabilities": [8, 14, 16, 18],
            "critical_vulnerabilities": [3, 2, 4, 8],
            "sla_compliance": [0.95, 0.92, 0.89, 0.87]
        }
    }

@app.get("/api/v1/reports/vulnerability-heatmap")
async def get_vulnerability_heatmap():
    """Generate vulnerability heatmap data"""
    return {
        "asset_vulnerability_matrix": [
            [
                {"asset": "Web Server 01", "critical": 2, "high": 4, "medium": 6, "low": 3, "total": 15},
                {"asset": "Web Server 02", "critical": 1, "high": 3, "medium": 5, "low": 2, "total": 11},
                {"asset": "Database Server", "critical": 1, "high": 2, "medium": 3, "low": 2, "total": 8},
                {"asset": "API Gateway", "critical": 1, "high": 2, "medium": 3, "low": 1, "total": 7},
                {"asset": "Load Balancer", "critical": 0, "high": 1, "medium": 3, "low": 1, "total": 5}
            ]
        ],
        "severity_distribution": {
            "critical": {"count": 8, "percentage": 6.3},
            "high": {"count": 23, "percentage": 18.1},
            "medium": {"count": 67, "percentage": 52.8},
            "low": {"count": 29, "percentage": 22.8}
        },
        "asset_risk_scores": {
            "Web Server 01": 8.7,
            "Web Server 02": 7.2,
            "Database Server": 7.8,
            "API Gateway": 7.5,
            "Load Balancer": 4.2
        },
        "network_exposure_analysis": {
            "internet_facing": {"assets": 5, "vulnerabilities": 45, "avg_severity": 7.2},
            "dmz": {"assets": 8, "vulnerabilities": 32, "avg_severity": 6.1},
            "internal": {"assets": 45, "vulnerabilities": 50, "avg_severity": 4.8}
        }
    }

@app.post("/api/v1/vulnerabilities/bulk-update")
async def bulk_update_vulnerabilities(bulk_operation: dict):
    """Perform bulk operations on vulnerabilities"""
    
    operation = bulk_operation.get("operation")
    vulnerability_ids = bulk_operation.get("vulnerability_ids", [])
    operation_data = bulk_operation.get("operation_data", {})
    
    success_count = len(vulnerability_ids)
    error_count = 0
    
    return {
        "success": True,
        "operation": operation,
        "processed_count": len(vulnerability_ids),
        "success_count": success_count,
        "error_count": error_count,
        "errors": [],
        "updated_vulnerabilities": vulnerability_ids,
        "operation_summary": f"Successfully {operation} on {success_count} vulnerabilities",
        "timestamp": datetime.now().isoformat()
    }

# ================================
# Incident Response and Crisis Management System Endpoints
# ================================

@app.get("/api/v1/incidents")
async def get_incidents(
    severity: str = None,
    status: str = None,
    category: str = None,
    assigned_team: int = None,
    assigned_responder: int = None,
    escalation_level: str = None,
    date_from: str = None,
    date_to: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get incidents with filtering and pagination"""
    
    incidents = [
        {
            "id": 1,
            "incident_id": "INC-20240125103000-A1B2C3D4",
            "title": "Critical Data Breach - Customer Database Compromised",
            "description": "Unauthorized access detected to customer database containing PII of 50,000 customers. Initial investigation indicates SQL injection attack through web application vulnerability.",
            "category": "data_breach",
            "severity": "critical",
            "status": "containing",
            "reported_at": "2024-01-25T10:30:00Z",
            "detected_at": "2024-01-25T10:15:00Z",
            "occurred_at": "2024-01-25T09:45:00Z",
            "business_impact": "High - Customer PII exposed, potential regulatory fines, reputation damage",
            "affected_systems": ["customer-db-prod", "web-app-portal"],
            "affected_users_count": 50000,
            "financial_impact": 2500000,
            "reputation_impact": "critical",
            "primary_responder_id": 3,
            "incident_commander_id": 1,
            "assigned_team_id": 1,
            "escalation_level": "executive",
            "escalated_at": "2024-01-25T11:00:00Z",
            "requires_regulatory_reporting": True,
            "regulatory_bodies_notified": ["State Attorney General"],
            "regulatory_notification_deadline": "2024-01-27T10:30:00Z",
            "confidentiality_level": "restricted",
            "legal_hold_required": True,
            "detection_method": "automated_scan",
            "detection_source": "SIEM Alert - Anomalous Database Access",
            "tags": ["data-breach", "sql-injection", "customer-data", "regulatory"],
            "reported_by_user": {
                "id": 5,
                "email": "security.analyst@company.com",
                "full_name": "Security Analyst"
            },
            "primary_responder": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Security Team Lead"
            },
            "incident_commander": {
                "id": 1,
                "email": "ciso@company.com",
                "full_name": "Chief Information Security Officer"
            },
            "assigned_team": {
                "id": 1,
                "team_name": "Critical Incident Response Team",
                "specializations": ["data_breach", "security_breach"]
            },
            "activity_count": 15,
            "artifact_count": 8,
            "communication_count": 12,
            "task_count": 6,
            "timeline_entry_count": 22,
            "created_at": "2024-01-25T10:30:00Z",
            "updated_at": "2024-01-25T16:45:00Z"
        },
        {
            "id": 2,
            "incident_id": "INC-20240124145000-B2C3D4E5",
            "title": "Network Infrastructure Outage - Primary Data Center",
            "description": "Complete network outage affecting primary data center. All customer-facing services are down. Root cause appears to be core router failure.",
            "category": "system_outage",
            "severity": "high",
            "status": "recovering",
            "reported_at": "2024-01-24T14:50:00Z",
            "detected_at": "2024-01-24T14:48:00Z",
            "occurred_at": "2024-01-24T14:47:00Z",
            "resolved_at": "2024-01-24T18:30:00Z",
            "business_impact": "Complete service disruption affecting all customers",
            "affected_systems": ["core-router-01", "network-infrastructure", "all-services"],
            "affected_users_count": 150000,
            "financial_impact": 450000,
            "reputation_impact": "high",
            "primary_responder_id": 7,
            "incident_commander_id": 2,
            "assigned_team_id": 2,
            "escalation_level": "l3_advanced",
            "escalated_at": "2024-01-24T15:30:00Z",
            "requires_regulatory_reporting": False,
            "confidentiality_level": "internal",
            "legal_hold_required": False,
            "detection_method": "automated_monitoring",
            "detection_source": "Network Monitoring System",
            "tags": ["outage", "network", "infrastructure", "service-disruption"],
            "reported_by_user": {
                "id": 9,
                "email": "network.ops@company.com",
                "full_name": "Network Operations"
            },
            "primary_responder": {
                "id": 7,
                "email": "network.lead@company.com",
                "full_name": "Network Team Lead"
            },
            "incident_commander": {
                "id": 2,
                "email": "cto@company.com",
                "full_name": "Chief Technology Officer"
            },
            "assigned_team": {
                "id": 2,
                "team_name": "Infrastructure Response Team",
                "specializations": ["system_outage", "network"]
            },
            "activity_count": 28,
            "artifact_count": 5,
            "communication_count": 18,
            "task_count": 12,
            "timeline_entry_count": 35,
            "created_at": "2024-01-24T14:50:00Z",
            "updated_at": "2024-01-24T19:15:00Z"
        },
        {
            "id": 3,
            "incident_id": "INC-20240123092000-C3D4E5F6",
            "title": "Phishing Campaign Targeting Employees",
            "description": "Large-scale phishing campaign targeting employees with credential harvesting emails. 25 employees reported suspicious emails, 3 may have entered credentials.",
            "category": "phishing",
            "severity": "medium",
            "status": "investigating",
            "reported_at": "2024-01-23T09:20:00Z",
            "detected_at": "2024-01-23T09:10:00Z",
            "occurred_at": "2024-01-23T08:30:00Z",
            "business_impact": "Potential account compromise, credential theft",
            "affected_systems": ["email-system", "employee-accounts"],
            "affected_users_count": 25,
            "financial_impact": 15000,
            "reputation_impact": "low",
            "primary_responder_id": 4,
            "incident_commander_id": 3,
            "assigned_team_id": 1,
            "escalation_level": "l2_standard",
            "requires_regulatory_reporting": False,
            "confidentiality_level": "internal",
            "legal_hold_required": False,
            "detection_method": "user_report",
            "detection_source": "Employee Reports",
            "tags": ["phishing", "email", "credentials", "social-engineering"],
            "reported_by_user": {
                "id": 12,
                "email": "hr.manager@company.com",
                "full_name": "HR Manager"
            },
            "primary_responder": {
                "id": 4,
                "email": "security.analyst2@company.com",
                "full_name": "Senior Security Analyst"
            },
            "incident_commander": {
                "id": 3,
                "email": "security.manager@company.com",
                "full_name": "Security Manager"
            },
            "assigned_team": {
                "id": 1,
                "team_name": "Critical Incident Response Team",
                "specializations": ["phishing", "security_breach"]
            },
            "activity_count": 8,
            "artifact_count": 12,
            "communication_count": 6,
            "task_count": 4,
            "timeline_entry_count": 15,
            "created_at": "2024-01-23T09:20:00Z",
            "updated_at": "2024-01-23T15:30:00Z"
        }
    ]
    
    # Apply filters
    filtered_incidents = incidents
    
    if severity:
        filtered_incidents = [i for i in filtered_incidents if i["severity"] == severity]
    if status:
        filtered_incidents = [i for i in filtered_incidents if i["status"] == status]
    if category:
        filtered_incidents = [i for i in filtered_incidents if i["category"] == category]
    if assigned_team:
        filtered_incidents = [i for i in filtered_incidents if i["assigned_team_id"] == assigned_team]
    if assigned_responder:
        filtered_incidents = [i for i in filtered_incidents if i["primary_responder_id"] == assigned_responder]
    if escalation_level:
        filtered_incidents = [i for i in filtered_incidents if i["escalation_level"] == escalation_level]
    
    # Apply pagination
    paginated_incidents = filtered_incidents[skip:skip + limit]
    
    return {
        "items": paginated_incidents,
        "total": len(filtered_incidents),
        "skip": skip,
        "limit": limit,
        "summary": {
            "critical": len([i for i in filtered_incidents if i["severity"] == "critical"]),
            "high": len([i for i in filtered_incidents if i["severity"] == "high"]),
            "medium": len([i for i in filtered_incidents if i["severity"] == "medium"]),
            "low": len([i for i in filtered_incidents if i["severity"] == "low"]),
            "open_incidents": len([i for i in filtered_incidents if i["status"] not in ["closed", "cancelled"]]),
            "overdue_regulatory": len([i for i in filtered_incidents if i.get("requires_regulatory_reporting") and i.get("regulatory_notification_deadline") and i["regulatory_notification_deadline"] < datetime.now().isoformat()])
        }
    }

@app.post("/api/v1/incidents")
async def create_incident(incident_data: dict):
    """Create a new incident"""
    return {
        "id": 999,
        "incident_id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(random.randint(10000000, 99999999)).upper()[:8]}",
        "title": incident_data.get("title", "New Incident"),
        "description": incident_data.get("description", ""),
        "category": incident_data.get("category", "operational_issue"),
        "severity": incident_data.get("severity", "medium"),
        "status": "reported",
        "reported_at": datetime.now().isoformat(),
        "business_impact": incident_data.get("business_impact"),
        "affected_systems": incident_data.get("affected_systems", []),
        "affected_users_count": incident_data.get("affected_users_count", 0),
        "reported_by": incident_data.get("reported_by", 1),
        "escalation_level": "l1_basic",
        "requires_regulatory_reporting": False,
        "confidentiality_level": incident_data.get("confidentiality_level", "internal"),
        "created_at": datetime.now().isoformat(),
        "message": "Incident created successfully"
    }

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(incident_id: int):
    """Get specific incident details"""
    if incident_id == 1:
        return {
            "id": 1,
            "incident_id": "INC-20240125103000-A1B2C3D4",
            "title": "Critical Data Breach - Customer Database Compromised",
            "description": "Unauthorized access detected to customer database containing personally identifiable information (PII) of approximately 50,000 customers. Initial investigation indicates a SQL injection attack through a vulnerability in the customer portal web application. The attack appears to have occurred between 09:45 and 10:15 UTC on January 25, 2024.",
            "category": "data_breach",
            "severity": "critical",
            "status": "containing",
            "reported_at": "2024-01-25T10:30:00Z",
            "detected_at": "2024-01-25T10:15:00Z",
            "occurred_at": "2024-01-25T09:45:00Z",
            "resolved_at": None,
            "closed_at": None,
            "business_impact": "High impact - Customer PII exposed including names, addresses, phone numbers, and email addresses. Potential regulatory fines under GDPR and state privacy laws. Significant reputation damage and customer trust issues expected.",
            "affected_systems": ["customer-db-prod", "web-app-portal", "customer-api"],
            "affected_users_count": 50000,
            "financial_impact": 2500000,
            "reputation_impact": "critical",
            "primary_responder_id": 3,
            "incident_commander_id": 1,
            "assigned_team_id": 1,
            "escalation_level": "executive",
            "escalated_at": "2024-01-25T11:00:00Z",
            "escalated_by": 3,
            "escalation_reason": "Critical data breach with regulatory reporting requirements and high financial impact",
            "requires_regulatory_reporting": True,
            "regulatory_bodies_notified": ["State Attorney General", "EU Data Protection Authority"],
            "regulatory_notification_deadline": "2024-01-27T10:30:00Z",
            "confidentiality_level": "restricted",
            "handling_instructions": "Restricted access - legal privilege applies. All communications must be approved by legal team.",
            "legal_hold_required": True,
            "detection_method": "automated_scan",
            "detection_source": "SIEM Alert - Anomalous Database Access Pattern",
            "tags": ["data-breach", "sql-injection", "customer-data", "regulatory", "gdpr", "critical"],
            "custom_fields": {
                "breach_type": "unauthorized_access",
                "data_types_affected": ["pii", "contact_info"],
                "geographic_scope": ["us", "eu"],
                "notification_status": "in_progress"
            },
            "reported_by_user": {
                "id": 5,
                "email": "security.analyst@company.com",
                "full_name": "Security Analyst"
            },
            "primary_responder": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Security Team Lead"
            },
            "incident_commander": {
                "id": 1,
                "email": "ciso@company.com",
                "full_name": "Chief Information Security Officer"
            },
            "escalated_by_user": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Security Team Lead"
            },
            "assigned_team": {
                "id": 1,
                "team_name": "Critical Incident Response Team",
                "description": "Specialized team for handling critical security incidents",
                "specializations": ["data_breach", "security_breach", "regulatory_response"],
                "team_lead": {
                    "id": 1,
                    "email": "ciso@company.com",
                    "full_name": "Chief Information Security Officer"
                }
            },
            "activity_count": 15,
            "artifact_count": 8,
            "communication_count": 12,
            "task_count": 6,
            "timeline_entry_count": 22,
            "created_at": "2024-01-25T10:30:00Z",
            "updated_at": "2024-01-25T16:45:00Z"
        }
    else:
        return {"error": "Incident not found", "detail": f"Incident with ID {incident_id} does not exist"}

@app.put("/api/v1/incidents/{incident_id}")
async def update_incident(incident_id: int, incident_data: dict):
    """Update incident details"""
    return {
        "id": incident_id,
        "message": "Incident updated successfully",
        "updated_fields": list(incident_data.keys()),
        "updated_at": datetime.now().isoformat()
    }

@app.post("/api/v1/incidents/{incident_id}/escalate")
async def escalate_incident(incident_id: int, escalation_data: dict):
    """Escalate incident to higher level"""
    return {
        "incident_id": incident_id,
        "previous_escalation_level": "l2_standard",
        "new_escalation_level": escalation_data.get("escalation_level", "l3_advanced"),
        "escalation_reason": escalation_data.get("reason", "Manual escalation requested"),
        "escalated_by": escalation_data.get("escalated_by", 1),
        "escalated_at": datetime.now().isoformat(),
        "notification_sent": True,
        "message": "Incident escalated successfully"
    }

@app.post("/api/v1/incidents/classify")
async def classify_incident(classification_request: dict):
    """Automatically classify incident based on description and context"""
    title = classification_request.get("title", "")
    description = classification_request.get("description", "")
    
    # Simple classification logic based on keywords
    text_content = f"{title} {description}".lower()
    
    if any(keyword in text_content for keyword in ["data breach", "unauthorized access", "leaked", "exposed"]):
        category = "data_breach"
        severity = "critical"
        confidence = 0.9
    elif any(keyword in text_content for keyword in ["malware", "virus", "ransomware", "trojan"]):
        category = "malware"
        severity = "high"
        confidence = 0.85
    elif any(keyword in text_content for keyword in ["phishing", "suspicious email", "credential"]):
        category = "phishing"
        severity = "medium"
        confidence = 0.8
    elif any(keyword in text_content for keyword in ["outage", "down", "unavailable", "service"]):
        category = "system_outage"
        severity = "high"
        confidence = 0.75
    else:
        category = "operational_issue"
        severity = "medium"
        confidence = 0.6
    
    escalation_mapping = {
        "critical": "l4_expert",
        "high": "l3_advanced",
        "medium": "l2_standard",
        "low": "l1_basic"
    }
    
    response_time_mapping = {
        "critical": 15,
        "high": 60,
        "medium": 240,
        "low": 1440
    }
    
    return {
        "category": category,
        "severity": severity,
        "confidence_score": confidence,
        "escalation_level": escalation_mapping[severity],
        "required_response_time_minutes": response_time_mapping[severity],
        "required_team": "Security Response Team" if category in ["data_breach", "malware", "phishing"] else "Operations Team",
        "regulatory_reporting_required": category == "data_breach",
        "auto_actions": [
            {"action_type": "isolate_affected_systems", "parameters": {}} if severity == "critical" else None,
            {"action_type": "collect_forensic_evidence", "parameters": {}} if category in ["data_breach", "malware"] else None
        ],
        "reasoning": f"Classification based on keyword analysis. Found indicators for {category} with {severity} severity."
    }

@app.get("/api/v1/incident-response-teams")
async def get_incident_response_teams(
    active: bool = None,
    specialization: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get incident response teams"""
    
    teams = [
        {
            "id": 1,
            "team_name": "Critical Incident Response Team",
            "description": "Specialized team for handling critical security incidents and data breaches",
            "team_lead_id": 1,
            "escalation_contact_id": 1,
            "time_zone": "UTC",
            "specializations": ["data_breach", "security_breach", "malware", "phishing"],
            "max_concurrent_incidents": 3,
            "primary_contact_method": "phone",
            "contact_details": {
                "phone": "+1-555-SECURITY",
                "email": "critical-response@company.com",
                "slack_channel": "#critical-incidents"
            },
            "active": True,
            "team_lead": {
                "id": 1,
                "email": "ciso@company.com",
                "full_name": "Chief Information Security Officer"
            },
            "escalation_contact": {
                "id": 1,
                "email": "ciso@company.com",
                "full_name": "Chief Information Security Officer"
            },
            "member_count": 8,
            "current_incidents": 2,
            "available_capacity": 1,
            "created_at": "2023-01-15T00:00:00Z"
        },
        {
            "id": 2,
            "team_name": "Infrastructure Response Team",
            "description": "Team responsible for system outages and infrastructure incidents",
            "team_lead_id": 2,
            "escalation_contact_id": 2,
            "time_zone": "UTC",
            "specializations": ["system_outage", "network", "infrastructure", "operational_issue"],
            "max_concurrent_incidents": 5,
            "primary_contact_method": "slack",
            "contact_details": {
                "phone": "+1-555-INFRAOPS",
                "email": "infrastructure-response@company.com",
                "slack_channel": "#infrastructure-incidents"
            },
            "active": True,
            "team_lead": {
                "id": 2,
                "email": "cto@company.com",
                "full_name": "Chief Technology Officer"
            },
            "escalation_contact": {
                "id": 2,
                "email": "cto@company.com",
                "full_name": "Chief Technology Officer"
            },
            "member_count": 12,
            "current_incidents": 1,
            "available_capacity": 4,
            "created_at": "2023-01-15T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_teams = teams
    if active is not None:
        filtered_teams = [t for t in filtered_teams if t["active"] == active]
    if specialization:
        filtered_teams = [t for t in filtered_teams if specialization in t["specializations"]]
    
    # Apply pagination
    paginated_teams = filtered_teams[skip:skip + limit]
    
    return {
        "items": paginated_teams,
        "total": len(filtered_teams),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/incident-response-teams")
async def create_incident_response_team(team_data: dict):
    """Create a new incident response team"""
    return {
        "id": 999,
        "team_name": team_data.get("team_name", "New Response Team"),
        "description": team_data.get("description", ""),
        "specializations": team_data.get("specializations", []),
        "max_concurrent_incidents": team_data.get("max_concurrent_incidents", 5),
        "primary_contact_method": team_data.get("primary_contact_method", "email"),
        "active": True,
        "member_count": 0,
        "current_incidents": 0,
        "available_capacity": team_data.get("max_concurrent_incidents", 5),
        "created_at": datetime.now().isoformat(),
        "message": "Incident response team created successfully"
    }

@app.get("/api/v1/incidents/{incident_id}/activities")
async def get_incident_activities(
    incident_id: int,
    activity_type: str = None,
    response_phase: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get activities for an incident"""
    
    activities = [
        {
            "id": 1,
            "incident_id": incident_id,
            "activity_type": "incident_creation",
            "title": "Incident Created",
            "description": "Critical data breach incident created based on SIEM alert detection",
            "performed_by": 5,
            "performed_at": "2024-01-25T10:30:00Z",
            "duration_minutes": 5,
            "response_phase": "identification",
            "outcome": "Incident successfully created and initial responders notified",
            "success": True,
            "next_actions": "Initiate containment procedures",
            "artifacts_created": ["incident-report-initial.pdf"],
            "systems_affected": ["customer-db-prod"],
            "tools_used": ["SIEM", "Incident Management System"],
            "priority": "critical",
            "tags": ["creation", "initial-response"],
            "performer": {
                "id": 5,
                "email": "security.analyst@company.com",
                "full_name": "Security Analyst"
            },
            "created_at": "2024-01-25T10:30:00Z"
        },
        {
            "id": 2,
            "incident_id": incident_id,
            "activity_type": "containment",
            "title": "Database Access Restricted",
            "description": "Implemented emergency access controls to limit database connectivity to essential services only",
            "performed_by": 3,
            "performed_at": "2024-01-25T11:15:00Z",
            "duration_minutes": 30,
            "response_phase": "containment",
            "outcome": "Database access successfully restricted, unauthorized access vector closed",
            "success": True,
            "next_actions": "Continue forensic investigation",
            "artifacts_created": ["firewall-rules-backup.json", "access-logs-pre-containment.log"],
            "systems_affected": ["customer-db-prod", "firewall-cluster"],
            "tools_used": ["Firewall Management", "Database Administration"],
            "priority": "critical",
            "tags": ["containment", "access-control"],
            "performer": {
                "id": 3,
                "email": "security.lead@company.com",
                "full_name": "Security Team Lead"
            },
            "created_at": "2024-01-25T11:15:00Z"
        },
        {
            "id": 3,
            "incident_id": incident_id,
            "activity_type": "investigation",
            "title": "Forensic Analysis Initiated",
            "description": "Started detailed forensic analysis of database logs and web application access patterns",
            "performed_by": 4,
            "performed_at": "2024-01-25T12:00:00Z",
            "duration_minutes": 120,
            "response_phase": "investigation",
            "outcome": "Confirmed SQL injection attack vector, identified affected records",
            "success": True,
            "next_actions": "Prepare customer notification materials",
            "artifacts_created": ["forensic-analysis-report.pdf", "sql-injection-evidence.pcap"],
            "systems_affected": ["customer-db-prod", "web-app-portal"],
            "tools_used": ["Forensic Toolkit", "Log Analysis Platform"],
            "priority": "high",
            "tags": ["investigation", "forensics", "sql-injection"],
            "performer": {
                "id": 4,
                "email": "forensic.analyst@company.com",
                "full_name": "Digital Forensics Analyst"
            },
            "created_at": "2024-01-25T12:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_activities = activities
    if activity_type:
        filtered_activities = [a for a in filtered_activities if a["activity_type"] == activity_type]
    if response_phase:
        filtered_activities = [a for a in filtered_activities if a["response_phase"] == response_phase]
    
    # Apply pagination
    paginated_activities = filtered_activities[skip:skip + limit]
    
    return {
        "items": paginated_activities,
        "total": len(filtered_activities),
        "incident_id": incident_id,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/incidents/{incident_id}/activities")
async def create_incident_activity(incident_id: int, activity_data: dict):
    """Create a new incident activity"""
    return {
        "id": 999,
        "incident_id": incident_id,
        "activity_type": activity_data.get("activity_type", "investigation"),
        "title": activity_data.get("title", "New Activity"),
        "description": activity_data.get("description", ""),
        "performed_by": activity_data.get("performed_by", 1),
        "performed_at": datetime.now().isoformat(),
        "duration_minutes": activity_data.get("duration_minutes"),
        "response_phase": activity_data.get("response_phase", "investigation"),
        "priority": activity_data.get("priority", "medium"),
        "created_at": datetime.now().isoformat(),
        "message": "Incident activity created successfully"
    }

@app.get("/api/v1/incidents/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: int,
    event_type: str = None,
    phase: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get timeline entries for an incident"""
    
    timeline_entries = [
        {
            "id": 1,
            "incident_id": incident_id,
            "timestamp": "2024-01-25T09:45:00Z",
            "event_type": "attack_action",
            "title": "Initial SQL Injection Attempt",
            "description": "Attacker began SQL injection attempts through customer portal login form",
            "source": "Web Application Logs",
            "confidence_level": "high",
            "verified": True,
            "phase": "identification",
            "actor": "Unknown Attacker",
            "target": "Customer Portal Database",
            "technique": "SQL Injection (OWASP T1071)",
            "impact_level": "critical",
            "business_impact": "Unauthorized database access initiated",
            "technical_impact": "Database queries bypassing authentication",
            "supporting_artifacts": [1, 2],
            "indicators": ["192.168.1.100", "malicious.payload.com"],
            "tags": ["attack", "sql-injection", "initial-access"],
            "verified_by": 4,
            "verifier": {
                "id": 4,
                "email": "forensic.analyst@company.com",
                "full_name": "Digital Forensics Analyst"
            },
            "created_at": "2024-01-25T12:30:00Z"
        },
        {
            "id": 2,
            "incident_id": incident_id,
            "timestamp": "2024-01-25T10:15:00Z",
            "event_type": "detection",
            "title": "SIEM Alert Triggered",
            "description": "Automated SIEM system detected anomalous database access patterns",
            "source": "SIEM System",
            "confidence_level": "high",
            "verified": True,
            "phase": "identification",
            "actor": "SIEM System",
            "target": "Customer Database",
            "technique": "Automated Detection",
            "impact_level": "low",
            "business_impact": "Security team alerted to potential threat",
            "technical_impact": "Alert generated and escalated",
            "supporting_artifacts": [3],
            "indicators": ["SIEM-ALERT-DB-001"],
            "tags": ["detection", "siem", "automated"],
            "verified": True,
            "created_at": "2024-01-25T10:16:00Z"
        },
        {
            "id": 3,
            "incident_id": incident_id,
            "timestamp": "2024-01-25T11:15:00Z",
            "event_type": "response_action",
            "title": "Database Access Restricted",
            "description": "Emergency containment: Database access restricted to essential services only",
            "source": "Incident Response Team",
            "confidence_level": "high",
            "verified": True,
            "phase": "containment",
            "actor": "Security Team Lead",
            "target": "Customer Database",
            "technique": "Access Control Implementation",
            "impact_level": "medium",
            "business_impact": "Attack vector closed, services temporarily limited",
            "technical_impact": "Database connectivity restricted",
            "supporting_artifacts": [4, 5],
            "indicators": ["firewall-rule-emergency-001"],
            "tags": ["containment", "access-control", "response"],
            "verified": True,
            "created_at": "2024-01-25T11:16:00Z"
        }
    ]
    
    # Apply filters
    filtered_timeline = timeline_entries
    if event_type:
        filtered_timeline = [t for t in filtered_timeline if t["event_type"] == event_type]
    if phase:
        filtered_timeline = [t for t in filtered_timeline if t["phase"] == phase]
    
    # Apply pagination
    paginated_timeline = filtered_timeline[skip:skip + limit]
    
    return {
        "items": paginated_timeline,
        "total": len(filtered_timeline),
        "incident_id": incident_id,
        "skip": skip,
        "limit": limit
    }

@app.get("/api/v1/dashboards/incident-summary")
async def get_incident_dashboard():
    """Get incident response dashboard summary"""
    return {
        "summary": {
            "total_incidents": 45,
            "open_incidents": 8,
            "incidents_this_month": 12,
            "avg_resolution_time_hours": 18.5,
            "critical_incidents": 2,
            "overdue_incidents": 1,
            "escalated_incidents": 3,
            "regulatory_incidents": 1
        },
        "incidents_by_severity": {
            "critical": 2,
            "high": 6,
            "medium": 15,
            "low": 22
        },
        "incidents_by_category": {
            "security_breach": 8,
            "data_breach": 3,
            "system_outage": 12,
            "phishing": 7,
            "malware": 4,
            "operational_issue": 11
        },
        "incidents_by_status": {
            "reported": 2,
            "triaged": 3,
            "investigating": 8,
            "containing": 2,
            "eradicating": 1,
            "recovering": 3,
            "closed": 26
        },
        "incidents_by_team": {
            "Critical Incident Response Team": 15,
            "Infrastructure Response Team": 18,
            "Application Security Team": 8,
            "Network Operations Team": 4
        },
        "response_time_metrics": {
            "mean_time_to_detect_hours": 2.3,
            "mean_time_to_respond_hours": 0.8,
            "mean_time_to_contain_hours": 4.2,
            "mean_time_to_resolve_hours": 18.5
        },
        "recent_incidents": [
            {
                "incident_id": "INC-20240125103000-A1B2C3D4",
                "title": "Critical Data Breach - Customer Database",
                "severity": "critical",
                "status": "containing",
                "created_at": "2024-01-25T10:30:00Z"
            },
            {
                "incident_id": "INC-20240124145000-B2C3D4E5",
                "title": "Network Infrastructure Outage",
                "severity": "high",
                "status": "closed",
                "created_at": "2024-01-24T14:50:00Z"
            }
        ],
        "critical_incidents": [
            {
                "incident_id": "INC-20240125103000-A1B2C3D4",
                "title": "Critical Data Breach - Customer Database",
                "severity": "critical",
                "escalation_level": "executive",
                "regulatory_reporting": True
            }
        ],
        "trend_data": {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "new_incidents": [8, 12, 15, 10],
            "resolved_incidents": [6, 10, 14, 12],
            "mean_resolution_time": [22.1, 19.8, 17.5, 18.5]
        }
    }

# ================================
# Compliance Management System Endpoints
# ================================

@app.get("/api/v1/compliance/frameworks")
async def get_compliance_frameworks(
    framework_type: str = None,
    active: bool = None,
    mandatory: bool = None,
    skip: int = 0,
    limit: int = 100
):
    """Get compliance frameworks with filtering"""
    
    frameworks = [
        {
            "id": 1,
            "framework_id": "NIST-800-53-R5",
            "name": "NIST SP 800-53 Revision 5",
            "framework_type": "nist_800_53",
            "description": "Security and Privacy Controls for Information Systems and Organizations",
            "version": "Revision 5",
            "authority": "National Institute of Standards and Technology",
            "scope": "Federal information systems and organizations",
            "industry_focus": "Government",
            "geographic_scope": "United States",
            "total_controls": 1000,
            "active": True,
            "mandatory": True,
            "custom_framework": False,
            "automated_assessment": True,
            "assessment_frequency": "quarterly",
            "overall_compliance_score": 78.5,
            "last_assessment_date": "2024-01-20T00:00:00Z",
            "assessment_count": 12,
            "created_at": "2023-06-01T00:00:00Z"
        },
        {
            "id": 2,
            "framework_id": "ISO-27001-2022",
            "name": "ISO/IEC 27001:2022",
            "framework_type": "iso_27001",
            "description": "Information Security Management Systems Requirements",
            "version": "2022",
            "authority": "International Organization for Standardization",
            "scope": "Information security management systems",
            "industry_focus": "All Industries",
            "geographic_scope": "Global",
            "total_controls": 93,
            "active": True,
            "mandatory": False,
            "custom_framework": False,
            "automated_assessment": False,
            "assessment_frequency": "annually",
            "overall_compliance_score": 85.2,
            "last_assessment_date": "2024-01-15T00:00:00Z",
            "assessment_count": 8,
            "created_at": "2023-08-15T00:00:00Z"
        },
        {
            "id": 3,
            "framework_id": "SOX-2024",
            "name": "Sarbanes-Oxley Act",
            "framework_type": "sox",
            "description": "Corporate governance and financial reporting requirements",
            "version": "2024",
            "authority": "Securities and Exchange Commission",
            "scope": "Publicly traded companies",
            "industry_focus": "Financial Services",
            "geographic_scope": "United States",
            "total_controls": 45,
            "active": True,
            "mandatory": True,
            "custom_framework": False,
            "automated_assessment": False,
            "assessment_frequency": "quarterly",
            "overall_compliance_score": 92.1,
            "last_assessment_date": "2024-01-10T00:00:00Z",
            "assessment_count": 16,
            "created_at": "2023-05-01T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_frameworks = frameworks
    if framework_type:
        filtered_frameworks = [f for f in filtered_frameworks if f["framework_type"] == framework_type]
    if active is not None:
        filtered_frameworks = [f for f in filtered_frameworks if f["active"] == active]
    if mandatory is not None:
        filtered_frameworks = [f for f in filtered_frameworks if f["mandatory"] == mandatory]
    
    # Apply pagination
    paginated_frameworks = filtered_frameworks[skip:skip + limit]
    
    return {
        "items": paginated_frameworks,
        "total": len(filtered_frameworks),
        "skip": skip,
        "limit": limit,
        "summary": {
            "active_frameworks": len([f for f in filtered_frameworks if f["active"]]),
            "mandatory_frameworks": len([f for f in filtered_frameworks if f["mandatory"]]),
            "avg_compliance_score": sum(f["overall_compliance_score"] for f in filtered_frameworks) / len(filtered_frameworks) if filtered_frameworks else 0
        }
    }

@app.post("/api/v1/compliance/frameworks")
async def create_compliance_framework(framework_data: dict):
    """Create a new compliance framework"""
    return {
        "id": 999,
        "framework_id": f"CUSTOM-{datetime.now().strftime('%Y%m%d')}",
        "name": framework_data.get("name", "New Framework"),
        "framework_type": framework_data.get("framework_type", "custom"),
        "description": framework_data.get("description", ""),
        "version": framework_data.get("version", "1.0"),
        "active": True,
        "custom_framework": True,
        "total_controls": 0,
        "created_at": datetime.now().isoformat(),
        "message": "Compliance framework created successfully"
    }

@app.get("/api/v1/compliance/frameworks/{framework_id}")
async def get_compliance_framework(framework_id: int):
    """Get specific compliance framework details"""
    if framework_id == 1:
        return {
            "id": 1,
            "framework_id": "NIST-800-53-R5",
            "name": "NIST SP 800-53 Revision 5",
            "framework_type": "nist_800_53",
            "description": "Security and Privacy Controls for Information Systems and Organizations - Comprehensive cybersecurity framework providing a catalog of security and privacy controls for federal information systems and organizations to protect organizational operations and assets.",
            "version": "Revision 5",
            "effective_date": "2020-09-23T00:00:00Z",
            "authority": "National Institute of Standards and Technology (NIST)",
            "scope": "Federal information systems and organizations, and the supply chain",
            "industry_focus": "Government, Federal Contractors",
            "geographic_scope": "United States",
            "total_controls": 1000,
            "control_families": {
                "AC": "Access Control",
                "AT": "Awareness and Training",
                "AU": "Audit and Accountability",
                "CA": "Assessment, Authorization, and Monitoring",
                "CM": "Configuration Management",
                "CP": "Contingency Planning",
                "IA": "Identification and Authentication",
                "IR": "Incident Response",
                "MA": "Maintenance",
                "MP": "Media Protection",
                "PE": "Physical and Environmental Protection",
                "PL": "Planning",
                "PS": "Personnel Security",
                "RA": "Risk Assessment",
                "SA": "System and Services Acquisition",
                "SC": "System and Communications Protection",
                "SI": "System and Information Integrity"
            },
            "framework_hierarchy": {
                "families": 17,
                "controls": 1000,
                "enhancements": 3000
            },
            "active": True,
            "mandatory": True,
            "custom_framework": False,
            "automated_assessment": True,
            "assessment_frequency": "quarterly",
            "overall_compliance_score": 78.5,
            "last_assessment_date": "2024-01-20T00:00:00Z",
            "assessment_count": 12,
            "created_at": "2023-06-01T00:00:00Z",
            "updated_at": "2024-01-20T15:30:00Z"
        }
    else:
        return {"error": "Framework not found", "detail": f"Compliance framework with ID {framework_id} does not exist"}

@app.get("/api/v1/compliance/frameworks/{framework_id}/controls")
async def get_framework_controls(
    framework_id: int,
    control_family: str = None,
    control_type: str = None,
    implementation_status: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get controls for a specific framework"""
    
    controls = [
        {
            "id": 1,
            "control_id": "AC-1",
            "framework_id": framework_id,
            "control_number": "AC-1",
            "control_family": "AC",
            "control_title": "Policy and Procedures",
            "control_objective": "Establish access control policy and procedures",
            "description": "Develop, document, and disseminate access control policy and procedures",
            "control_type": "administrative",
            "control_class": "Low",
            "priority": "high",
            "baseline_impact": "low",
            "privacy_control": False,
            "security_control": True,
            "operational_control": True,
            "implementation_status": "compliant",
            "testing_frequency": "annually",
            "last_test_date": "2024-01-15T00:00:00Z",
            "next_test_date": "2025-01-15T00:00:00Z",
            "automated_testing": False,
            "assessment_count": 5,
            "last_assessment_score": 8.5,
            "finding_count": 0,
            "evidence_count": 3
        },
        {
            "id": 2,
            "control_id": "AC-2",
            "framework_id": framework_id,
            "control_number": "AC-2",
            "control_family": "AC",
            "control_title": "Account Management",
            "control_objective": "Manage information system accounts",
            "description": "Manage information system accounts including establishing conditions for group and role membership",
            "control_type": "technical",
            "control_class": "Moderate",
            "priority": "high",
            "baseline_impact": "moderate",
            "privacy_control": True,
            "security_control": True,
            "operational_control": False,
            "implementation_status": "partially_compliant",
            "testing_frequency": "quarterly",
            "last_test_date": "2024-01-10T00:00:00Z",
            "next_test_date": "2024-04-10T00:00:00Z",
            "automated_testing": True,
            "automation_tool": "Active Directory Scripts",
            "assessment_count": 8,
            "last_assessment_score": 7.2,
            "finding_count": 2,
            "evidence_count": 5
        }
    ]
    
    # Apply filters
    filtered_controls = controls
    if control_family:
        filtered_controls = [c for c in filtered_controls if c["control_family"] == control_family]
    if control_type:
        filtered_controls = [c for c in filtered_controls if c["control_type"] == control_type]
    if implementation_status:
        filtered_controls = [c for c in filtered_controls if c["implementation_status"] == implementation_status]
    
    # Apply pagination
    paginated_controls = filtered_controls[skip:skip + limit]
    
    return {
        "items": paginated_controls,
        "total": len(filtered_controls),
        "framework_id": framework_id,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/compliance/frameworks/{framework_id}/controls")
async def create_control(framework_id: int, control_data: dict):
    """Create a new control in a framework"""
    return {
        "id": 999,
        "control_id": control_data.get("control_id", "CUSTOM-001"),
        "framework_id": framework_id,
        "control_title": control_data.get("control_title", "New Control"),
        "description": control_data.get("description", ""),
        "control_type": control_data.get("control_type", "administrative"),
        "implementation_status": "not_assessed",
        "created_at": datetime.now().isoformat(),
        "message": "Control created successfully"
    }

@app.get("/api/v1/compliance/controls/{control_id}")
async def get_control(control_id: int):
    """Get specific control details"""
    if control_id == 1:
        return {
            "id": 1,
            "control_id": "AC-1",
            "framework_id": 1,
            "control_number": "AC-1",
            "control_family": "AC",
            "control_title": "Access Control Policy and Procedures",
            "control_objective": "Establish, document, and maintain access control policies and procedures",
            "description": "Develop, document, and disseminate access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and develop, document, and disseminate procedures to facilitate the implementation of the access control policy and associated access control controls.",
            "implementation_guidance": "Access control policy and procedures should be consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.",
            "assessment_procedures": "Interview organizational personnel; examine access control policy and procedures documentation; examine system documentation.",
            "control_type": "administrative",
            "control_class": "Low",
            "priority": "high",
            "baseline_impact": "low",
            "privacy_control": False,
            "security_control": True,
            "operational_control": True,
            "implementation_status": "compliant",
            "implementation_notes": "Policy updated annually and procedures reviewed quarterly",
            "compensating_controls": [],
            "testing_frequency": "annually",
            "testing_methodology": "Document review and interview",
            "last_test_date": "2024-01-15T00:00:00Z",
            "next_test_date": "2025-01-15T00:00:00Z",
            "automated_testing": False,
            "parent_control_id": None,
            "dependent_controls": ["AC-2", "AC-3", "AC-4"],
            "related_controls": ["AT-1", "AU-1", "CA-1"],
            "active": True,
            "framework": {
                "id": 1,
                "name": "NIST SP 800-53 Revision 5",
                "framework_type": "nist_800_53"
            },
            "assessment_count": 5,
            "last_assessment_score": 8.5,
            "finding_count": 0,
            "evidence_count": 3,
            "created_at": "2023-06-01T00:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    else:
        return {"error": "Control not found", "detail": f"Control with ID {control_id} does not exist"}

@app.get("/api/v1/compliance/assessments")
async def get_compliance_assessments(
    framework_id: int = None,
    status: str = None,
    assessment_type: str = None,
    lead_assessor: int = None,
    skip: int = 0,
    limit: int = 100
):
    """Get compliance assessments with filtering"""
    
    assessments = [
        {
            "id": 1,
            "assessment_id": "ASSESS-2024-001",
            "framework_id": 1,
            "assessment_name": "Q1 2024 NIST 800-53 Compliance Assessment",
            "assessment_type": "internal",
            "assessment_scope": "All critical systems and controls",
            "status": "completed",
            "progress_percentage": 100,
            "start_date": "2024-01-15T00:00:00Z",
            "end_date": "2024-01-20T00:00:00Z",
            "planned_completion_date": "2024-01-25T00:00:00Z",
            "overall_compliance_score": 78.5,
            "compliant_controls": 785,
            "non_compliant_controls": 125,
            "partially_compliant_controls": 90,
            "not_assessed_controls": 0,
            "total_findings": 45,
            "critical_findings": 3,
            "high_findings": 12,
            "medium_findings": 20,
            "low_findings": 10,
            "framework": {
                "id": 1,
                "name": "NIST SP 800-53 Revision 5",
                "framework_type": "nist_800_53"
            },
            "lead_assessor": {
                "id": 1,
                "email": "lead.assessor@company.com",
                "full_name": "Lead Compliance Assessor"
            },
            "assessment_team": [
                {"id": 2, "email": "assessor1@company.com", "full_name": "Security Assessor 1"},
                {"id": 3, "email": "assessor2@company.com", "full_name": "IT Assessor"}
            ],
            "external_auditor": "External Compliance Firm",
            "created_at": "2024-01-10T00:00:00Z"
        },
        {
            "id": 2,
            "assessment_id": "ASSESS-2024-002",
            "framework_id": 2,
            "assessment_name": "ISO 27001 Annual Assessment",
            "assessment_type": "external",
            "assessment_scope": "Information Security Management System",
            "status": "in_progress",
            "progress_percentage": 65,
            "start_date": "2024-01-20T00:00:00Z",
            "end_date": None,
            "planned_completion_date": "2024-02-15T00:00:00Z",
            "overall_compliance_score": None,
            "compliant_controls": 45,
            "non_compliant_controls": 8,
            "partially_compliant_controls": 12,
            "not_assessed_controls": 28,
            "total_findings": 15,
            "critical_findings": 1,
            "high_findings": 4,
            "medium_findings": 7,
            "low_findings": 3,
            "framework": {
                "id": 2,
                "name": "ISO/IEC 27001:2022",
                "framework_type": "iso_27001"
            },
            "lead_assessor": {
                "id": 4,
                "email": "iso.assessor@company.com",
                "full_name": "ISO Compliance Specialist"
            },
            "external_auditor": "ISO Certification Body",
            "created_at": "2024-01-15T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_assessments = assessments
    if framework_id:
        filtered_assessments = [a for a in filtered_assessments if a["framework_id"] == framework_id]
    if status:
        filtered_assessments = [a for a in filtered_assessments if a["status"] == status]
    if assessment_type:
        filtered_assessments = [a for a in filtered_assessments if a["assessment_type"] == assessment_type]
    if lead_assessor:
        filtered_assessments = [a for a in filtered_assessments if a["lead_assessor"]["id"] == lead_assessor]
    
    # Apply pagination
    paginated_assessments = filtered_assessments[skip:skip + limit]
    
    return {
        "items": paginated_assessments,
        "total": len(filtered_assessments),
        "skip": skip,
        "limit": limit,
        "summary": {
            "active_assessments": len([a for a in filtered_assessments if a["status"] in ["in_progress", "planned"]]),
            "completed_assessments": len([a for a in filtered_assessments if a["status"] == "completed"]),
            "avg_compliance_score": sum(a["overall_compliance_score"] for a in filtered_assessments if a["overall_compliance_score"]) / len([a for a in filtered_assessments if a["overall_compliance_score"]]) if [a for a in filtered_assessments if a["overall_compliance_score"]] else 0
        }
    }

@app.post("/api/v1/compliance/assessments")
async def create_compliance_assessment(assessment_data: dict):
    """Create a new compliance assessment"""
    return {
        "id": 999,
        "assessment_id": f"ASSESS-{datetime.now().strftime('%Y%m%d')}-999",
        "framework_id": assessment_data.get("framework_id"),
        "assessment_name": assessment_data.get("assessment_name", "New Assessment"),
        "assessment_type": assessment_data.get("assessment_type", "internal"),
        "status": "planned",
        "progress_percentage": 0,
        "start_date": assessment_data.get("start_date", datetime.now().isoformat()),
        "planned_completion_date": assessment_data.get("planned_completion_date"),
        "lead_assessor": assessment_data.get("lead_assessor"),
        "created_at": datetime.now().isoformat(),
        "message": "Compliance assessment created successfully"
    }

@app.get("/api/v1/compliance/assessments/{assessment_id}")
async def get_compliance_assessment(assessment_id: int):
    """Get specific compliance assessment details"""
    if assessment_id == 1:
        return {
            "id": 1,
            "assessment_id": "ASSESS-2024-001",
            "framework_id": 1,
            "assessment_name": "Q1 2024 NIST 800-53 Compliance Assessment",
            "assessment_type": "internal",
            "assessment_scope": "Comprehensive assessment of all NIST 800-53 controls across critical infrastructure and information systems",
            "status": "completed",
            "progress_percentage": 100,
            "start_date": "2024-01-15T00:00:00Z",
            "end_date": "2024-01-20T00:00:00Z",
            "planned_completion_date": "2024-01-25T00:00:00Z",
            "assessment_methodology": "NIST SP 800-53A assessment procedures with automated and manual testing",
            "assessment_criteria": "NIST 800-53 Rev 5 control implementation requirements",
            "overall_compliance_score": 78.5,
            "compliant_controls": 785,
            "non_compliant_controls": 125,
            "partially_compliant_controls": 90,
            "not_assessed_controls": 0,
            "total_findings": 45,
            "critical_findings": 3,
            "high_findings": 12,
            "medium_findings": 20,
            "low_findings": 10,
            "executive_summary": "Overall compliance posture is strong with 78.5% compliance rate. Critical findings require immediate attention in access control and incident response areas.",
            "detailed_report_path": "/reports/ASSESS-2024-001-detailed.pdf",
            "framework": {
                "id": 1,
                "name": "NIST SP 800-53 Revision 5",
                "framework_type": "nist_800_53"
            },
            "lead_assessor": {
                "id": 1,
                "email": "lead.assessor@company.com",
                "full_name": "Lead Compliance Assessor"
            },
            "assessment_team": [
                {"id": 2, "email": "assessor1@company.com", "full_name": "Security Assessor 1"},
                {"id": 3, "email": "assessor2@company.com", "full_name": "IT Assessor"},
                {"id": 4, "email": "risk.assessor@company.com", "full_name": "Risk Assessment Specialist"}
            ],
            "external_auditor": "External Compliance Firm LLC",
            "created_at": "2024-01-10T00:00:00Z",
            "updated_at": "2024-01-20T17:00:00Z"
        }
    else:
        return {"error": "Assessment not found", "detail": f"Assessment with ID {assessment_id} does not exist"}

@app.post("/api/v1/compliance/assessments/{assessment_id}/conduct")
async def conduct_assessment(assessment_id: int, assessment_config: dict):
    """Conduct compliance assessment for a framework"""
    return {
        "assessment_id": assessment_id,
        "status": "initiated",
        "estimated_duration": "5-7 business days",
        "total_controls_to_assess": 1000,
        "automated_controls": 450,
        "manual_controls": 550,
        "assessment_methodology": assessment_config.get("methodology", "nist_sp_800_53a"),
        "initiated_at": datetime.now().isoformat(),
        "estimated_completion": "2024-02-05T17:00:00Z",
        "message": "Compliance assessment initiated successfully"
    }

@app.get("/api/v1/compliance/findings")
async def get_compliance_findings(
    assessment_id: int = None,
    control_id: int = None,
    severity: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get compliance findings with filtering"""
    
    findings = [
        {
            "id": 1,
            "finding_id": "FIND-2024-001",
            "assessment_id": 1,
            "control_id": 15,
            "finding_title": "Insufficient Access Control Documentation",
            "finding_description": "Access control procedures lack sufficient detail for privileged account management",
            "finding_type": "deficiency",
            "severity": "high",
            "risk_level": "high",
            "business_impact": "Potential unauthorized access to critical systems",
            "compliance_impact": "Non-compliance with AC-2 requirements",
            "root_cause": "Procedure documentation has not been updated to reflect current processes",
            "remediation_plan": "Update access control procedures to include detailed privileged account management steps",
            "remediation_deadline": "2024-02-15T00:00:00Z",
            "status": "open",
            "remediation_status": "in_progress",
            "validation_required": True,
            "identified_date": "2024-01-18T00:00:00Z",
            "assessment": {
                "id": 1,
                "assessment_name": "Q1 2024 NIST 800-53 Compliance Assessment"
            },
            "control": {
                "id": 15,
                "control_id": "AC-2",
                "control_title": "Account Management"
            },
            "remediation_owner": {
                "id": 3,
                "email": "security.admin@company.com",
                "full_name": "Security Administrator"
            },
            "evidence_count": 2
        },
        {
            "id": 2,
            "finding_id": "FIND-2024-002",
            "assessment_id": 1,
            "control_id": 25,
            "finding_title": "Incomplete Incident Response Testing",
            "finding_description": "Incident response procedures have not been tested in the past 12 months",
            "finding_type": "deficiency",
            "severity": "medium",
            "risk_level": "medium",
            "business_impact": "Reduced effectiveness of incident response capabilities",
            "compliance_impact": "Partial non-compliance with IR-3 testing requirements",
            "root_cause": "Testing schedule was not maintained due to resource constraints",
            "remediation_plan": "Schedule and conduct comprehensive incident response testing",
            "remediation_deadline": "2024-03-01T00:00:00Z",
            "status": "open",
            "remediation_status": "planned",
            "validation_required": True,
            "identified_date": "2024-01-19T00:00:00Z",
            "assessment": {
                "id": 1,
                "assessment_name": "Q1 2024 NIST 800-53 Compliance Assessment"
            },
            "control": {
                "id": 25,
                "control_id": "IR-3",
                "control_title": "Incident Response Testing"
            },
            "remediation_owner": {
                "id": 5,
                "email": "incident.manager@company.com",
                "full_name": "Incident Response Manager"
            },
            "evidence_count": 1
        }
    ]
    
    # Apply filters
    filtered_findings = findings
    if assessment_id:
        filtered_findings = [f for f in filtered_findings if f["assessment_id"] == assessment_id]
    if control_id:
        filtered_findings = [f for f in filtered_findings if f["control_id"] == control_id]
    if severity:
        filtered_findings = [f for f in filtered_findings if f["severity"] == severity]
    if status:
        filtered_findings = [f for f in filtered_findings if f["status"] == status]
    
    # Apply pagination
    paginated_findings = filtered_findings[skip:skip + limit]
    
    return {
        "items": paginated_findings,
        "total": len(filtered_findings),
        "skip": skip,
        "limit": limit,
        "summary": {
            "critical": len([f for f in filtered_findings if f["severity"] == "critical"]),
            "high": len([f for f in filtered_findings if f["severity"] == "high"]),
            "medium": len([f for f in filtered_findings if f["severity"] == "medium"]),
            "low": len([f for f in filtered_findings if f["severity"] == "low"]),
            "open_findings": len([f for f in filtered_findings if f["status"] == "open"])
        }
    }

@app.post("/api/v1/compliance/findings")
async def create_compliance_finding(finding_data: dict):
    """Create a new compliance finding"""
    return {
        "id": 999,
        "finding_id": f"FIND-{datetime.now().strftime('%Y%m%d')}-999",
        "assessment_id": finding_data.get("assessment_id"),
        "control_id": finding_data.get("control_id"),
        "finding_title": finding_data.get("finding_title", "New Finding"),
        "finding_description": finding_data.get("finding_description", ""),
        "finding_type": finding_data.get("finding_type", "deficiency"),
        "severity": finding_data.get("severity", "medium"),
        "status": "open",
        "identified_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "message": "Compliance finding created successfully"
    }

@app.get("/api/v1/compliance/gap-analysis/{framework_id}")
async def get_compliance_gap_analysis(framework_id: int, target_maturity_level: int = 3):
    """Get compliance gap analysis for a framework"""
    return {
        "framework_id": framework_id,
        "analysis_date": datetime.now().isoformat(),
        "overall_compliance_percentage": 78.5,
        "compliant_controls": 785,
        "non_compliant_controls": 125,
        "partially_compliant_controls": 90,
        "not_assessed_controls": 0,
        "critical_gaps": [
            {
                "control_id": "AC-2",
                "control_title": "Account Management",
                "current_maturity": 2,
                "target_maturity": target_maturity_level,
                "gap_size": target_maturity_level - 2,
                "remediation_effort": {
                    "estimated_days": 15,
                    "estimated_cost": 12000,
                    "complexity": "medium"
                }
            },
            {
                "control_id": "IR-3",
                "control_title": "Incident Response Testing",
                "current_maturity": 1,
                "target_maturity": target_maturity_level,
                "gap_size": target_maturity_level - 1,
                "remediation_effort": {
                    "estimated_days": 25,
                    "estimated_cost": 20000,
                    "complexity": "high"
                }
            }
        ],
        "high_priority_gaps": [
            {
                "control_id": "AU-6",
                "control_title": "Audit Record Review",
                "current_maturity": 2,
                "target_maturity": target_maturity_level,
                "gap_size": 1,
                "remediation_effort": {
                    "estimated_days": 10,
                    "estimated_cost": 8000,
                    "complexity": "low"
                }
            }
        ],
        "remediation_roadmap": [
            {
                "control_id": "IR-3",
                "control_title": "Incident Response Testing",
                "priority": 3,
                "quarter": "Q1",
                "effort_days": 25,
                "estimated_cost": 20000
            },
            {
                "control_id": "AC-2",
                "control_title": "Account Management",
                "priority": 2,
                "quarter": "Q1",
                "effort_days": 15,
                "estimated_cost": 12000
            },
            {
                "control_id": "AU-6",
                "control_title": "Audit Record Review",
                "priority": 1,
                "quarter": "Q2",
                "effort_days": 10,
                "estimated_cost": 8000
            }
        ],
        "estimated_remediation_effort": {
            "total_effort_days": 50,
            "total_estimated_cost": 40000,
            "estimated_duration_quarters": 2,
            "average_quarterly_effort": 25
        },
        "recommended_actions": [
            "Prioritize incident response testing implementation",
            "Enhance account management procedures",
            "Implement automated audit log review processes"
        ]
    }

@app.get("/api/v1/compliance/scorecard/{framework_id}")
async def get_compliance_scorecard(framework_id: int, assessment_id: int = None):
    """Get compliance scorecard for a framework"""
    return {
        "framework_id": framework_id,
        "assessment_id": assessment_id or 1,
        "scorecard_date": datetime.now().isoformat(),
        "overall_score": 78.5,
        "maturity_score": 3.2,
        "effectiveness_score": 82.1,
        "implementation_score": 79.8,
        "control_family_scores": {
            "AC": 75.2,
            "AT": 85.1,
            "AU": 82.3,
            "CA": 78.9,
            "CM": 71.5,
            "CP": 69.8,
            "IA": 88.2,
            "IR": 65.4,
            "MA": 79.1,
            "MP": 83.7,
            "PE": 92.3,
            "PL": 87.6,
            "PS": 90.1,
            "RA": 74.8,
            "SA": 68.9,
            "SC": 76.5,
            "SI": 73.2
        },
        "trend_analysis": {
            "overall_trend": "improving",
            "quarterly_scores": [72.1, 75.3, 76.8, 78.5],
            "improvement_rate": 2.1
        },
        "benchmark_comparison": {
            "industry_average": 74.2,
            "peer_group_average": 76.8,
            "percentile": 65
        },
        "executive_summary": "Compliance Assessment Executive Summary\n\nOverall Compliance Score: 78.5/100 (Strong)\n\nAssessment Results:\n- Total Controls Assessed: 1000\n- Total Findings Identified: 45\n- Compliance Level: Strong\n\nKey Observations:\n- Strong compliance posture with minor gaps in incident response and configuration management areas",
        "key_strengths": [
            "Excellent physical and environmental protection controls",
            "Strong personnel security and identification/authentication",
            "Well-established planning and awareness programs"
        ],
        "improvement_areas": [
            "Incident response testing and procedures",
            "Configuration management automation",
            "System acquisition and development controls"
        ],
        "recommendations": [
            "Implement regular incident response testing program",
            "Enhance configuration management tooling",
            "Strengthen secure development lifecycle processes"
        ]
    }

@app.get("/api/v1/dashboards/compliance-summary")
async def get_compliance_dashboard():
    """Get compliance management dashboard summary"""
    return {
        "summary": {
            "total_frameworks": 8,
            "active_assessments": 3,
            "total_controls": 2156,
            "total_findings": 127,
            "overdue_assessments": 1,
            "overdue_remediations": 8,
            "avg_compliance_score": 81.2,
            "compliance_trend": "improving"
        },
        "frameworks_by_status": {
            "compliant": 5,
            "partially_compliant": 2,
            "non_compliant": 1,
            "not_assessed": 0
        },
        "controls_by_status": {
            "compliant": 1723,
            "partially_compliant": 285,
            "non_compliant": 148,
            "not_assessed": 0
        },
        "findings_by_severity": {
            "critical": 8,
            "high": 23,
            "medium": 67,
            "low": 29
        },
        "assessments_by_status": {
            "completed": 12,
            "in_progress": 3,
            "planned": 2,
            "overdue": 1
        },
        "top_frameworks_by_score": [
            {"framework": "SOX", "score": 92.1, "status": "compliant"},
            {"framework": "ISO 27001", "score": 85.2, "status": "compliant"},
            {"framework": "NIST 800-53", "score": 78.5, "status": "partially_compliant"}
        ],
        "recent_assessments": [
            {
                "assessment_name": "Q1 2024 NIST Assessment",
                "framework": "NIST 800-53",
                "completion_date": "2024-01-20T00:00:00Z",
                "score": 78.5
            },
            {
                "assessment_name": "ISO 27001 Annual Review",
                "framework": "ISO 27001",
                "completion_date": "2024-01-15T00:00:00Z",
                "score": 85.2
            }
        ],
        "critical_findings": [
            {
                "finding_id": "FIND-2024-001",
                "title": "Insufficient Access Control Documentation",
                "severity": "high",
                "framework": "NIST 800-53"
            },
            {
                "finding_id": "FIND-2024-003",
                "title": "Missing Encryption Key Management",
                "severity": "critical",
                "framework": "PCI-DSS"
            }
        ],
        "compliance_metrics": {
            "overall_compliance_percentage": 81.2,
            "average_maturity_level": 3.1,
            "control_effectiveness_percentage": 84.5,
            "assessment_completion_rate": 0.92,
            "remediation_success_rate": 0.87
        }
    }

# ================================
# Post-Incident Reviews and Lessons Learned Endpoints
# ================================

@app.get("/api/v1/incidents/{incident_id}/post-incident-review")
async def get_post_incident_review(incident_id: int):
    """Get post-incident review for a specific incident"""
    if incident_id == 1:
        return {
            "id": 1,
            "incident_id": 1,
            "review_name": "Critical Data Breach - Customer Database Compromise Post-Incident Review",
            "review_date": "2024-01-30T14:00:00Z",
            "facilitator_id": 1,
            "facilitator": {
                "id": 1,
                "email": "ciso@company.com",
                "full_name": "Chief Information Security Officer"
            },
            "participants": [1, 3, 5, 7, 9, 12],
            "participant_details": [
                {"id": 1, "email": "ciso@company.com", "full_name": "Chief Information Security Officer", "role": "Facilitator"},
                {"id": 3, "email": "security.lead@company.com", "full_name": "Security Team Lead", "role": "Primary Responder"},
                {"id": 5, "email": "security.analyst@company.com", "full_name": "Security Analyst", "role": "Initial Reporter"},
                {"id": 7, "email": "network.lead@company.com", "full_name": "Network Team Lead", "role": "Technical Expert"},
                {"id": 9, "email": "legal.counsel@company.com", "full_name": "Legal Counsel", "role": "Legal Representative"},
                {"id": 12, "email": "compliance.manager@company.com", "full_name": "Compliance Manager", "role": "Compliance Officer"}
            ],
            "timeline_analysis": {
                "detection_time_minutes": 30,
                "response_time_minutes": 15,
                "containment_time_minutes": 240,
                "resolution_time_minutes": 480,
                "total_incident_duration_minutes": 525
            },
            "effectiveness_assessment": {
                "response_effectiveness": "good",
                "communication_effectiveness": "excellent",
                "coordination_effectiveness": "good",
                "tool_effectiveness": {
                    "siem_system": "excellent",
                    "incident_management_platform": "good",
                    "forensics_tools": "fair",
                    "communication_tools": "excellent"
                }
            },
            "root_cause_analysis": {
                "root_cause": "Unpatched SQL injection vulnerability in customer portal web application",
                "contributing_factors": [
                    "Delayed security patch management process",
                    "Insufficient application security testing",
                    "Lack of web application firewall for the customer portal",
                    "Inadequate database access controls and monitoring"
                ],
                "attack_vectors": [
                    "SQL injection through customer portal login form",
                    "Privilege escalation via database service account",
                    "Data exfiltration through compromised database connection"
                ],
                "vulnerabilities_exploited": [
                    "CVE-2023-12345 - SQL injection in authentication module",
                    "Excessive database service account privileges",
                    "Missing database query logging and monitoring"
                ]
            },
            "impact_assessment": {
                "total_impact_cost": 2850000,
                "cost_breakdown": {
                    "incident_response_costs": 185000,
                    "forensics_investigation": 75000,
                    "system_remediation": 120000,
                    "legal_and_regulatory": 300000,
                    "customer_notification": 45000,
                    "credit_monitoring_services": 250000,
                    "business_disruption": 1200000,
                    "regulatory_fines": 675000
                },
                "business_downtime_hours": 8.75,
                "data_compromised": true,
                "data_compromised_records": 50000,
                "data_types_compromised": ["names", "addresses", "phone_numbers", "email_addresses", "account_numbers"],
                "regulatory_fines": 675000,
                "reputation_impact_assessment": "Significant negative impact on customer trust and brand reputation. Estimated 15% customer churn rate over next 6 months."
            },
            "successes": [
                "SIEM system effectively detected the anomalous database access patterns",
                "Incident response team was mobilized quickly within 15 minutes",
                "Effective coordination between security, legal, and compliance teams",
                "Transparent and timely customer communication strategy",
                "Comprehensive forensics investigation preserved evidence integrity",
                "Database was successfully contained and secured within 4 hours"
            ],
            "effective_controls": [
                "Security Information and Event Management (SIEM) system",
                "Database activity monitoring and alerting",
                "Incident response team training and procedures",
                "Legal and compliance notification processes",
                "Customer communication templates and procedures",
                "Forensics investigation capabilities"
            ],
            "good_decisions": [
                "Immediate escalation to executive level due to data breach severity",
                "Early engagement of legal counsel and compliance team",
                "Decision to take affected systems offline for containment",
                "Proactive customer notification beyond regulatory minimums",
                "Comprehensive forensics investigation before system restoration"
            ],
            "gaps_identified": [
                "Vulnerability management process delays",
                "Lack of web application firewall protection",
                "Insufficient application security testing",
                "Missing database privilege segregation",
                "Delayed threat intelligence integration",
                "Inadequate security awareness training for developers"
            ],
            "improvement_opportunities": [
                "Implement automated vulnerability scanning and patching",
                "Deploy web application firewall for all public-facing applications",
                "Establish regular penetration testing program",
                "Implement database activity monitoring and data loss prevention",
                "Enhance security training for development teams",
                "Improve threat intelligence integration and sharing"
            ],
            "ineffective_controls": [
                "Manual vulnerability patch management process",
                "Basic application security testing procedures",
                "Network perimeter security alone without application-layer protection",
                "Generic database access controls without granular permissions"
            ],
            "recommendations": [
                "Implement automated vulnerability management with priority-based patching",
                "Deploy web application firewall (WAF) for all customer-facing applications",
                "Establish DevSecOps program with security testing in CI/CD pipeline",
                "Implement database access controls with least privilege principles",
                "Enhance security monitoring with user behavior analytics",
                "Create security champion program within development teams",
                "Establish regular tabletop exercises for data breach scenarios"
            ],
            "action_items": [
                {
                    "id": 1,
                    "title": "Deploy Web Application Firewall for Customer Portal",
                    "description": "Implement and configure WAF to protect customer portal from common web attacks",
                    "assigned_to": 7,
                    "assigned_to_name": "Network Team Lead",
                    "priority": "critical",
                    "due_date": "2024-02-15T00:00:00Z",
                    "status": "assigned",
                    "estimated_effort_hours": 40,
                    "category": "technical_control"
                },
                {
                    "id": 2,
                    "title": "Implement Automated Vulnerability Management System",
                    "description": "Deploy automated vulnerability scanning and patch management solution",
                    "assigned_to": 3,
                    "assigned_to_name": "Security Team Lead",
                    "priority": "high",
                    "due_date": "2024-03-01T00:00:00Z",
                    "status": "assigned",
                    "estimated_effort_hours": 120,
                    "category": "process_improvement"
                },
                {
                    "id": 3,
                    "title": "Establish DevSecOps Security Testing Program",
                    "description": "Integrate security testing tools into development CI/CD pipeline",
                    "assigned_to": 15,
                    "assigned_to_name": "Development Manager",
                    "priority": "high",
                    "due_date": "2024-03-15T00:00:00Z",
                    "status": "assigned",
                    "estimated_effort_hours": 80,
                    "category": "process_improvement"
                },
                {
                    "id": 4,
                    "title": "Enhance Database Access Controls",
                    "description": "Implement least privilege database access controls and monitoring",
                    "assigned_to": 11,
                    "assigned_to_name": "Database Administrator",
                    "priority": "high",
                    "due_date": "2024-02-28T00:00:00Z",
                    "status": "assigned",
                    "estimated_effort_hours": 60,
                    "category": "technical_control"
                },
                {
                    "id": 5,
                    "title": "Conduct Data Breach Tabletop Exercise",
                    "description": "Plan and execute tabletop exercise for data breach response",
                    "assigned_to": 1,
                    "assigned_to_name": "Chief Information Security Officer",
                    "priority": "medium",
                    "due_date": "2024-04-01T00:00:00Z",
                    "status": "assigned",
                    "estimated_effort_hours": 24,
                    "category": "training_exercise"
                }
            ],
            "preventive_measures": [
                "Implement security-first development lifecycle with mandatory security reviews",
                "Deploy comprehensive application security testing (SAST, DAST, IAST)",
                "Establish security architecture review board for new applications",
                "Implement continuous security monitoring and threat hunting",
                "Create security awareness program focused on secure coding practices"
            ],
            "detection_improvements": [
                "Deploy user and entity behavior analytics (UEBA) for anomaly detection",
                "Implement application-level monitoring and alerting",
                "Enhance SIEM correlation rules for advanced persistent threats",
                "Deploy data loss prevention (DLP) solutions for sensitive data protection",
                "Establish threat intelligence sharing and integration capabilities"
            ],
            "follow_up_required": true,
            "next_review_date": "2024-04-30T00:00:00Z",
            "action_items_status": {
                "total": 5,
                "assigned": 5,
                "in_progress": 0,
                "completed": 0,
                "overdue": 0
            },
            "executive_summary": "Post-Incident Review Summary\n\nIncident: Critical Data Breach affecting 50,000 customers\nTotal Cost Impact: $2.85M\nResponse Duration: 8.75 hours\n\nKey Findings:\n- Root cause: Unpatched SQL injection vulnerability\n- SIEM detection worked effectively (30 min detection time)\n- Strong incident response coordination\n- Need for improved vulnerability management and application security\n\nCritical Actions Required:\n1. Deploy Web Application Firewall (Due: Feb 15)\n2. Implement automated vulnerability management (Due: Mar 1)\n3. Establish DevSecOps security testing (Due: Mar 15)\n\nOverall Assessment: Response was effective but preventable through better security controls",
            "detailed_report_path": "/reports/incidents/INC-20240125103000-A1B2C3D4-post-incident-review.pdf",
            "supporting_documents": [
                "/documents/forensics-investigation-report.pdf",
                "/documents/legal-notification-summary.pdf",
                "/documents/timeline-reconstruction.pdf",
                "/documents/technical-remediation-plan.pdf"
            ],
            "approved_by": null,
            "approved_at": null,
            "distribution_list": ["executive-team", "security-team", "legal-team", "compliance-team"],
            "confidentiality_level": "restricted",
            "created_at": "2024-01-30T16:00:00Z",
            "updated_at": "2024-01-30T18:30:00Z"
        }
    else:
        return {"error": "Post-incident review not found", "detail": f"No post-incident review found for incident {incident_id}"}

@app.post("/api/v1/incidents/{incident_id}/post-incident-review")
async def create_post_incident_review(incident_id: int, review_data: dict):
    """Create a new post-incident review"""
    return {
        "id": 999,
        "incident_id": incident_id,
        "review_name": review_data.get("review_name", f"Post-Incident Review for Incident {incident_id}"),
        "review_date": review_data.get("review_date", datetime.now().isoformat()),
        "facilitator_id": review_data.get("facilitator_id", 1),
        "participants": review_data.get("participants", []),
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "message": "Post-incident review created successfully"
    }

@app.put("/api/v1/post-incident-reviews/{review_id}")
async def update_post_incident_review(review_id: int, review_data: dict):
    """Update post-incident review details"""
    return {
        "id": review_id,
        "message": "Post-incident review updated successfully",
        "updated_fields": list(review_data.keys()),
        "updated_at": datetime.now().isoformat()
    }

@app.post("/api/v1/post-incident-reviews/{review_id}/approve")
async def approve_post_incident_review(review_id: int, approval_data: dict):
    """Approve post-incident review for distribution"""
    return {
        "id": review_id,
        "approved_by": approval_data.get("approved_by", 1),
        "approved_at": datetime.now().isoformat(),
        "status": "approved",
        "distribution_initiated": True,
        "message": "Post-incident review approved and distribution initiated"
    }

@app.get("/api/v1/post-incident-reviews/{review_id}/action-items")
async def get_post_incident_action_items(review_id: int):
    """Get action items from post-incident review"""
    return {
        "review_id": review_id,
        "action_items": [
            {
                "id": 1,
                "title": "Deploy Web Application Firewall for Customer Portal",
                "description": "Implement and configure WAF to protect customer portal from common web attacks",
                "assigned_to": 7,
                "assigned_to_name": "Network Team Lead",
                "priority": "critical",
                "due_date": "2024-02-15T00:00:00Z",
                "status": "in_progress",
                "progress_percentage": 65,
                "estimated_effort_hours": 40,
                "actual_effort_hours": 26,
                "category": "technical_control",
                "created_at": "2024-01-30T16:00:00Z",
                "started_at": "2024-02-01T09:00:00Z",
                "last_update": "2024-02-10T14:30:00Z",
                "updates": [
                    {
                        "date": "2024-02-10T14:30:00Z",
                        "update": "WAF hardware installed and initial configuration completed. Working on rule customization.",
                        "updated_by": "Network Team Lead"
                    },
                    {
                        "date": "2024-02-05T11:00:00Z", 
                        "update": "WAF solution procured and hardware received. Installation scheduled for Feb 8.",
                        "updated_by": "Network Team Lead"
                    }
                ]
            },
            {
                "id": 2,
                "title": "Implement Automated Vulnerability Management System",
                "description": "Deploy automated vulnerability scanning and patch management solution",
                "assigned_to": 3,
                "assigned_to_name": "Security Team Lead",
                "priority": "high",
                "due_date": "2024-03-01T00:00:00Z",
                "status": "assigned",
                "progress_percentage": 15,
                "estimated_effort_hours": 120,
                "actual_effort_hours": 18,
                "category": "process_improvement",
                "created_at": "2024-01-30T16:00:00Z",
                "started_at": "2024-02-01T09:00:00Z",
                "last_update": "2024-02-08T16:00:00Z",
                "updates": [
                    {
                        "date": "2024-02-08T16:00:00Z",
                        "update": "Completed vendor evaluation. Selected Qualys for vulnerability management. Working on procurement approval.",
                        "updated_by": "Security Team Lead"
                    }
                ]
            },
            {
                "id": 3,
                "title": "Establish DevSecOps Security Testing Program",
                "description": "Integrate security testing tools into development CI/CD pipeline",
                "assigned_to": 15,
                "assigned_to_name": "Development Manager",
                "priority": "high",
                "due_date": "2024-03-15T00:00:00Z",
                "status": "assigned",
                "progress_percentage": 0,
                "estimated_effort_hours": 80,
                "actual_effort_hours": 0,
                "category": "process_improvement",
                "created_at": "2024-01-30T16:00:00Z",
                "last_update": "2024-01-30T16:00:00Z",
                "updates": []
            }
        ],
        "summary": {
            "total_action_items": 3,
            "by_status": {
                "assigned": 2,
                "in_progress": 1,
                "completed": 0,
                "overdue": 0
            },
            "by_priority": {
                "critical": 1,
                "high": 2,
                "medium": 0,
                "low": 0
            },
            "completion_rate": 21.7,
            "overdue_items": 0,
            "at_risk_items": 1
        }
    }

@app.post("/api/v1/post-incident-reviews/{review_id}/action-items")
async def create_action_item(review_id: int, action_item_data: dict):
    """Create new action item from post-incident review"""
    return {
        "id": 999,
        "review_id": review_id,
        "title": action_item_data.get("title"),
        "description": action_item_data.get("description"),
        "assigned_to": action_item_data.get("assigned_to"),
        "priority": action_item_data.get("priority", "medium"),
        "due_date": action_item_data.get("due_date"),
        "status": "assigned",
        "created_at": datetime.now().isoformat(),
        "message": "Action item created successfully"
    }

@app.put("/api/v1/action-items/{action_item_id}")
async def update_action_item(action_item_id: int, update_data: dict):
    """Update action item progress and details"""
    return {
        "id": action_item_id,
        "status": update_data.get("status"),
        "progress_percentage": update_data.get("progress_percentage"),
        "actual_effort_hours": update_data.get("actual_effort_hours"),
        "update_note": update_data.get("update_note"),
        "updated_by": update_data.get("updated_by", 1),
        "updated_at": datetime.now().isoformat(),
        "message": "Action item updated successfully"
    }

@app.get("/api/v1/lessons-learned")
async def get_lessons_learned(
    category: str = None,
    time_period: str = None,
    severity: str = None,
    skip: int = 0,
    limit: int = 50
):
    """Get consolidated lessons learned from post-incident reviews"""
    
    lessons = [
        {
            "id": 1,
            "title": "Importance of Automated Vulnerability Management",
            "lesson": "Manual vulnerability patching processes create significant delays that can be exploited by attackers. Automated vulnerability management with priority-based patching is essential for timely remediation.",
            "incident_ids": [1, 4, 7],
            "incident_titles": [
                "Critical Data Breach - Customer Database Compromised",
                "Web Application Security Incident",
                "Server Compromise via Unpatched Vulnerability"
            ],
            "category": "vulnerability_management",
            "severity_levels": ["critical", "high", "medium"],
            "date_range": "2023-Q4 to 2024-Q1",
            "occurrences": 3,
            "business_impact": "High - Multiple incidents caused by delayed patching resulting in $4.2M total impact",
            "recommended_actions": [
                "Implement automated vulnerability scanning and assessment",
                "Deploy patch management system with risk-based prioritization",
                "Establish emergency patching procedures for critical vulnerabilities",
                "Create vulnerability management metrics and reporting"
            ],
            "implementation_status": "in_progress",
            "preventable_incidents": 3,
            "cost_avoidance_potential": 4200000,
            "knowledge_tags": ["patching", "automation", "vulnerability", "security-operations"],
            "created_at": "2024-01-30T16:00:00Z",
            "last_updated": "2024-02-10T14:00:00Z"
        },
        {
            "id": 2,
            "title": "Need for Application Layer Security Controls",
            "lesson": "Network perimeter security alone is insufficient to protect against application-layer attacks. Web application firewalls and application security testing are critical for public-facing applications.",
            "incident_ids": [1, 3, 6],
            "incident_titles": [
                "Critical Data Breach - Customer Database Compromised",
                "SQL Injection Attack on Customer Portal",
                "Cross-Site Scripting (XSS) Attack"
            ],
            "category": "application_security",
            "severity_levels": ["critical", "high"],
            "date_range": "2023-Q3 to 2024-Q1",
            "occurrences": 3,
            "business_impact": "Very High - Application attacks resulted in data breaches and service disruptions totaling $3.1M",
            "recommended_actions": [
                "Deploy web application firewall for all public-facing applications",
                "Implement security testing in development lifecycle (SAST, DAST)",
                "Establish security code review processes",
                "Create application security training for developers"
            ],
            "implementation_status": "in_progress",
            "preventable_incidents": 3,
            "cost_avoidance_potential": 3100000,
            "knowledge_tags": ["application-security", "waf", "development", "testing"],
            "created_at": "2024-01-25T14:00:00Z",
            "last_updated": "2024-02-08T10:00:00Z"
        },
        {
            "id": 3,
            "title": "Value of Early Executive Escalation",
            "lesson": "Early escalation of security incidents to executive leadership, even if severity is uncertain, enables faster decision-making and resource allocation for effective incident response.",
            "incident_ids": [1, 2, 8],
            "incident_titles": [
                "Critical Data Breach - Customer Database Compromised",
                "Network Infrastructure Outage - Primary Data Center",
                "Ransomware Attack on File Servers"
            ],
            "category": "incident_response",
            "severity_levels": ["critical", "high"],
            "date_range": "2023-Q4 to 2024-Q1",
            "occurrences": 3,
            "business_impact": "Medium - Improved response times and decision-making when executive escalation occurred early",
            "recommended_actions": [
                "Update incident escalation criteria to favor early escalation",
                "Establish executive notification procedures for potential high-impact incidents",
                "Create incident commander training program",
                "Develop escalation decision support tools"
            ],
            "implementation_status": "planned",
            "preventable_incidents": 0,
            "cost_avoidance_potential": 800000,
            "knowledge_tags": ["escalation", "leadership", "decision-making", "incident-management"],
            "created_at": "2024-01-28T11:00:00Z",
            "last_updated": "2024-02-01T09:00:00Z"
        },
        {
            "id": 4,
            "title": "Importance of Database Access Controls and Monitoring",
            "lesson": "Generic database access controls without granular permissions and monitoring create blind spots that attackers can exploit for data exfiltration.",
            "incident_ids": [1, 5],
            "incident_titles": [
                "Critical Data Breach - Customer Database Compromised",
                "Insider Threat - Unauthorized Data Access"
            ],
            "category": "data_protection",
            "severity_levels": ["critical", "high"],
            "date_range": "2023-Q4 to 2024-Q1",
            "occurrences": 2,
            "business_impact": "Very High - Database compromises led to major data breaches with $3.8M total impact",
            "recommended_actions": [
                "Implement database activity monitoring and data loss prevention",
                "Deploy least privilege access controls for database accounts",
                "Establish database query logging and anomaly detection",
                "Create data classification and protection policies"
            ],
            "implementation_status": "assigned",
            "preventable_incidents": 2,
            "cost_avoidance_potential": 3800000,
            "knowledge_tags": ["database-security", "access-control", "monitoring", "data-protection"],
            "created_at": "2024-01-30T17:00:00Z",
            "last_updated": "2024-02-05T13:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_lessons = lessons
    
    if category:
        filtered_lessons = [l for l in filtered_lessons if l["category"] == category]
    if severity:
        filtered_lessons = [l for l in filtered_lessons if severity in l["severity_levels"]]
    
    # Apply pagination
    paginated_lessons = filtered_lessons[skip:skip + limit]
    
    return {
        "items": paginated_lessons,
        "total": len(filtered_lessons),
        "skip": skip,
        "limit": limit,
        "summary": {
            "total_lessons": len(filtered_lessons),
            "by_category": {
                "vulnerability_management": len([l for l in filtered_lessons if l["category"] == "vulnerability_management"]),
                "application_security": len([l for l in filtered_lessons if l["category"] == "application_security"]),
                "incident_response": len([l for l in filtered_lessons if l["category"] == "incident_response"]),
                "data_protection": len([l for l in filtered_lessons if l["category"] == "data_protection"])
            },
            "by_implementation_status": {
                "implemented": len([l for l in filtered_lessons if l["implementation_status"] == "implemented"]),
                "in_progress": len([l for l in filtered_lessons if l["implementation_status"] == "in_progress"]),
                "assigned": len([l for l in filtered_lessons if l["implementation_status"] == "assigned"]),
                "planned": len([l for l in filtered_lessons if l["implementation_status"] == "planned"])
            },
            "total_preventable_incidents": sum(l["preventable_incidents"] for l in filtered_lessons),
            "total_cost_avoidance_potential": sum(l["cost_avoidance_potential"] for l in filtered_lessons)
        }
    }

@app.get("/api/v1/lessons-learned/trends")
async def get_lessons_learned_trends():
    """Get trends and analytics for lessons learned"""
    return {
        "trend_analysis": {
            "lessons_by_quarter": {
                "2023-Q3": 2,
                "2023-Q4": 5,
                "2024-Q1": 8,
                "trend": "increasing"
            },
            "top_categories": [
                {"category": "vulnerability_management", "count": 4, "percentage": 26.7},
                {"category": "application_security", "count": 3, "percentage": 20.0},
                {"category": "incident_response", "count": 3, "percentage": 20.0},
                {"category": "data_protection", "count": 2, "percentage": 13.3}
            ],
            "implementation_progress": {
                "implemented": 3,
                "in_progress": 5,
                "assigned": 4,
                "planned": 3,
                "completion_rate": 20.0
            }
        },
        "impact_metrics": {
            "total_incidents_analyzed": 15,
            "preventable_incidents": 12,
            "prevention_opportunity": 80.0,
            "cost_impact_analyzed": 12500000,
            "potential_cost_avoidance": 11800000,
            "roi_of_lessons_learned": 94.4
        },
        "knowledge_management": {
            "total_knowledge_items": 47,
            "knowledge_by_type": {
                "lessons_learned": 15,
                "best_practices": 18,
                "procedures": 14
            },
            "most_referenced_tags": [
                {"tag": "vulnerability", "count": 8},
                {"tag": "application-security", "count": 6},
                {"tag": "incident-management", "count": 5},
                {"tag": "monitoring", "count": 4}
            ],
            "knowledge_usage_metrics": {
                "views_last_30_days": 284,
                "searches_last_30_days": 97,
                "downloads_last_30_days": 45
            }
        },
        "effectiveness_metrics": {
            "incident_recurrence_rate": 15.2,
            "time_to_implement_lessons": {
                "average_days": 45.3,
                "median_days": 38.0,
                "target_days": 30.0
            },
            "lessons_applied_successfully": 12,
            "lessons_partially_applied": 5,
            "lessons_not_yet_applied": 8
        }
    }

@app.get("/api/v1/lessons-learned/knowledge-base")
async def get_lessons_learned_knowledge_base(
    search_query: str = None,
    tags: str = None,
    category: str = None
):
    """Search and browse lessons learned knowledge base"""
    
    knowledge_items = [
        {
            "id": 1,
            "type": "lesson_learned",
            "title": "Automated Vulnerability Management Best Practices",
            "content": "Based on analysis of 3 major incidents caused by delayed patching, organizations should implement automated vulnerability management with risk-based prioritization. Key components include automated scanning, patch testing environments, and emergency patching procedures.",
            "categories": ["vulnerability_management", "automation"],
            "tags": ["patching", "automation", "vulnerability", "security-operations", "risk-management"],
            "source_incidents": ["INC-20240125103000-A1B2C3D4", "INC-20231215140000-X1Y2Z3W4"],
            "business_impact": "High",
            "implementation_complexity": "Medium",
            "cost_benefit_ratio": "Very High",
            "related_frameworks": ["NIST", "ISO 27001", "CIS Controls"],
            "author": "Security Team Lead",
            "created_at": "2024-01-30T16:00:00Z",
            "last_updated": "2024-02-10T14:00:00Z",
            "views": 142,
            "downloads": 23,
            "rating": 4.8
        },
        {
            "id": 2,
            "type": "best_practice",
            "title": "Web Application Firewall Deployment Guide",
            "content": "Comprehensive guide for deploying web application firewalls based on lessons learned from SQL injection and XSS attacks. Includes configuration recommendations, rule customization, and monitoring best practices.",
            "categories": ["application_security", "technical_controls"],
            "tags": ["waf", "application-security", "sql-injection", "xss", "web-security"],
            "source_incidents": ["INC-20240125103000-A1B2C3D4", "INC-20231201120000-B2C3D4E5"],
            "business_impact": "High",
            "implementation_complexity": "Medium",
            "cost_benefit_ratio": "High",
            "related_frameworks": ["OWASP", "NIST", "PCI-DSS"],
            "author": "Network Team Lead",
            "created_at": "2024-02-01T10:00:00Z",
            "last_updated": "2024-02-08T15:30:00Z",
            "views": 98,
            "downloads": 18,
            "rating": 4.6
        },
        {
            "id": 3,
            "type": "procedure",
            "title": "Incident Escalation Decision Matrix",
            "content": "Decision matrix and procedures for incident escalation based on severity, business impact, and regulatory requirements. Includes escalation timelines, notification templates, and decision criteria.",
            "categories": ["incident_response", "escalation"],
            "tags": ["escalation", "decision-making", "incident-management", "procedures"],
            "source_incidents": ["INC-20240125103000-A1B2C3D4", "INC-20240124145000-B2C3D4E5"],
            "business_impact": "Medium",
            "implementation_complexity": "Low",
            "cost_benefit_ratio": "High",
            "related_frameworks": ["NIST", "ISO 27035"],
            "author": "Chief Information Security Officer",
            "created_at": "2024-01-28T11:00:00Z",
            "last_updated": "2024-02-01T09:00:00Z",
            "views": 76,
            "downloads": 12,
            "rating": 4.4
        }
    ]
    
    # Apply filters
    filtered_items = knowledge_items
    
    if search_query:
        filtered_items = [item for item in filtered_items 
                         if search_query.lower() in item["title"].lower() or 
                         search_query.lower() in item["content"].lower()]
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        filtered_items = [item for item in filtered_items 
                         if any(tag in item["tags"] for tag in tag_list)]
    if category:
        filtered_items = [item for item in filtered_items if category in item["categories"]]
    
    return {
        "items": filtered_items,
        "total": len(filtered_items),
        "facets": {
            "types": {
                "lesson_learned": len([i for i in knowledge_items if i["type"] == "lesson_learned"]),
                "best_practice": len([i for i in knowledge_items if i["type"] == "best_practice"]),
                "procedure": len([i for i in knowledge_items if i["type"] == "procedure"])
            },
            "categories": {
                "vulnerability_management": len([i for i in knowledge_items if "vulnerability_management" in i["categories"]]),
                "application_security": len([i for i in knowledge_items if "application_security" in i["categories"]]),
                "incident_response": len([i for i in knowledge_items if "incident_response" in i["categories"]])
            },
            "popular_tags": [
                {"tag": "vulnerability", "count": 2},
                {"tag": "application-security", "count": 2},
                {"tag": "incident-management", "count": 2},
                {"tag": "automation", "count": 1}
            ]
        },
        "recommendations": {
            "trending_items": [1, 2],
            "recently_updated": [2, 3],
            "highest_rated": [1, 2, 3]
        }
    }

@app.get("/api/v1/dashboards/incident-analytics")
async def get_incident_analytics_dashboard():
    """Get incident response analytics and metrics dashboard"""
    return {
        "summary": {
            "total_incidents_ytd": 24,
            "total_post_incident_reviews": 15,
            "total_lessons_learned": 28,
            "total_action_items": 45,
            "action_items_completed": 32,
            "action_item_completion_rate": 71.1,
            "avg_review_completion_days": 12.5,
            "cost_impact_prevented": 8400000
        },
        "incident_trends": {
            "incidents_by_month": {
                "2024-01": 6,
                "2024-02": 4,
                "2024-03": 8,
                "2024-04": 6,
                "trend": "stable"
            },
            "mttr_trend": {
                "2024-01": 320,
                "2024-02": 285,
                "2024-03": 240,
                "2024-04": 195,
                "trend": "improving",
                "improvement_percentage": 39.1
            },
            "severity_distribution": {
                "critical": 3,
                "high": 8,
                "medium": 10,
                "low": 3
            }
        },
        "post_incident_review_metrics": {
            "reviews_by_status": {
                "completed": 12,
                "in_progress": 2,
                "draft": 1,
                "overdue": 0
            },
            "review_completion_time": {
                "avg_days": 12.5,
                "median_days": 10.0,
                "target_days": 14.0,
                "on_time_percentage": 80.0
            },
            "participation_metrics": {
                "avg_participants_per_review": 5.2,
                "stakeholder_participation_rate": 92.3,
                "executive_participation_rate": 78.6
            }
        },
        "lessons_learned_effectiveness": {
            "lessons_by_category": {
                "vulnerability_management": 8,
                "application_security": 6,
                "incident_response": 5,
                "data_protection": 4,
                "compliance": 3,
                "other": 2
            },
            "implementation_success_rate": 76.9,
            "recurrence_prevention_rate": 84.6,
            "knowledge_base_usage": {
                "monthly_views": 428,
                "monthly_searches": 147,
                "monthly_downloads": 89,
                "user_satisfaction": 4.3
            }
        },
        "action_item_tracking": {
            "by_priority": {
                "critical": {"total": 8, "completed": 6, "completion_rate": 75.0},
                "high": {"total": 15, "completed": 12, "completion_rate": 80.0},
                "medium": {"total": 18, "completed": 12, "completion_rate": 66.7},
                "low": {"total": 4, "completed": 2, "completion_rate": 50.0}
            },
            "by_category": {
                "technical_control": {"total": 20, "completed": 15, "completion_rate": 75.0},
                "process_improvement": {"total": 15, "completed": 10, "completion_rate": 66.7},
                "training_exercise": {"total": 10, "completed": 7, "completion_rate": 70.0}
            },
            "overdue_items": 3,
            "at_risk_items": 5
        },
        "cost_benefit_analysis": {
            "total_incident_cost_ytd": 15200000,
            "prevention_investments": 1800000,
            "estimated_cost_avoided": 8400000,
            "roi_percentage": 366.7,
            "cost_per_prevented_incident": 150000
        },
        "continuous_improvement": {
            "process_maturity_score": 3.2,
            "improvement_trend": "positive",
            "key_improvements": [
                "Reduced average incident response time by 39%",
                "Increased post-incident review completion rate to 80%",
                "Implemented 76.9% of lessons learned recommendations",
                "Achieved 84.6% recurrence prevention rate"
            ],
            "focus_areas": [
                "Automated threat detection and response",
                "Enhanced security awareness training",
                "Supplier security risk management",
                "Cloud security posture management"
            ]
        }
    }


# ==========================================
# POST-INCIDENT ANALYSIS & LESSONS LEARNED
# ==========================================

@app.get("/api/v1/lessons-learned/comprehensive")
async def get_lessons_learned_comprehensive(
    category: str = None,
    implementation_status: str = None,
    severity_prevented: str = None,
    limit: int = 50,
    offset: int = 0
):
    """Get comprehensive lessons learned with detailed filtering"""
    # Mock comprehensive lessons learned data
    lessons = [
        {
            "id": 1,
            "lesson_title": "Multi-Factor Authentication Bypass Prevention",
            "lesson_summary": "Implementing device trust verification prevents sophisticated MFA bypass attacks",
            "lesson_category": "authentication",
            "what_happened": "Attackers bypassed MFA using session hijacking techniques on compromised corporate devices",
            "why_it_happened": "Lack of device trust verification allowed attackers to leverage existing authenticated sessions",
            "what_we_learned": "Device trust and session integrity verification are critical additional layers beyond standard MFA",
            "severity_prevented": "high",
            "implementation_status": "implemented",
            "cost_savings_estimated": 2500000,
            "effectiveness_verified": True,
            "confidence_level": "high",
            "keywords": ["mfa", "authentication", "device_trust", "session_security"],
            "identified_at": "2024-03-15T10:30:00Z",
            "implementation_date": "2024-05-20T00:00:00Z"
        },
        {
            "id": 2,
            "lesson_title": "Cloud Storage Misconfiguration Detection",
            "lesson_summary": "Automated cloud security posture monitoring prevents data exposure incidents",
            "lesson_category": "cloud_security",
            "what_happened": "Misconfigured S3 bucket exposed sensitive customer data due to overly permissive access policies",
            "why_it_happened": "Manual cloud configuration process lacked automated security validation",
            "what_we_learned": "Continuous cloud security posture management with automated remediation is essential",
            "severity_prevented": "critical",
            "implementation_status": "in_progress",
            "cost_savings_estimated": 5000000,
            "effectiveness_verified": False,
            "confidence_level": "medium",
            "keywords": ["cloud", "s3", "misconfiguration", "cspm", "automation"],
            "identified_at": "2024-02-20T14:15:00Z",
            "implementation_date": None
        },
        {
            "id": 3,
            "lesson_title": "Phishing Email Detection Enhancement",
            "lesson_summary": "Advanced threat protection with behavioral analysis significantly reduces successful phishing attacks",
            "lesson_category": "email_security",
            "what_happened": "Sophisticated phishing campaign bypassed traditional email security filters",
            "why_it_happened": "Email security relied primarily on signature-based detection without behavioral analysis",
            "what_we_learned": "Behavioral analysis and user activity monitoring are crucial for detecting advanced phishing",
            "severity_prevented": "medium",
            "implementation_status": "verified",
            "cost_savings_estimated": 800000,
            "effectiveness_verified": True,
            "recurrence_prevented": True,
            "confidence_level": "high",
            "keywords": ["phishing", "email", "behavioral_analysis", "atp"],
            "identified_at": "2024-01-10T09:45:00Z",
            "implementation_date": "2024-03-01T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_lessons = lessons
    if category:
        filtered_lessons = [l for l in filtered_lessons if l["lesson_category"] == category]
    if implementation_status:
        filtered_lessons = [l for l in filtered_lessons if l["implementation_status"] == implementation_status]
    if severity_prevented:
        filtered_lessons = [l for l in filtered_lessons if l["severity_prevented"] == severity_prevented]
    
    # Apply pagination
    total = len(filtered_lessons)
    paginated_lessons = filtered_lessons[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": paginated_lessons,
        "categories": ["authentication", "cloud_security", "email_security", "network_security", "data_protection"],
        "implementation_statuses": ["identified", "planned", "in_progress", "implemented", "verified"],
        "severity_levels": ["low", "medium", "high", "critical"]
    }


@app.post("/api/v1/lessons-learned")
async def create_lesson_learned(lesson_data: dict):
    """Create a new lesson learned"""
    # Mock lesson learned creation
    new_lesson = {
        "id": 99,
        "lesson_title": lesson_data.get("lesson_title"),
        "lesson_summary": lesson_data.get("lesson_summary"),
        "lesson_category": lesson_data.get("lesson_category"),
        "implementation_status": "identified",
        "confidence_level": lesson_data.get("confidence_level", "medium"),
        "identified_at": "2024-08-03T16:30:00Z",
        "created_at": "2024-08-03T16:30:00Z"
    }
    
    return {
        "success": True,
        "lesson": new_lesson,
        "message": "Lesson learned created successfully"
    }


@app.put("/api/v1/lessons-learned/{lesson_id}")
async def update_lesson_learned(lesson_id: int, lesson_data: dict):
    """Update an existing lesson learned"""
    # Mock lesson learned update
    return {
        "success": True,
        "lesson_id": lesson_id,
        "updated_fields": list(lesson_data.keys()),
        "message": "Lesson learned updated successfully"
    }


@app.post("/api/v1/lessons-learned/{lesson_id}/verify")
async def verify_lesson_effectiveness(lesson_id: int, verification_data: dict):
    """Verify the effectiveness of a lesson learned implementation"""
    return {
        "success": True,
        "lesson_id": lesson_id,
        "verification": {
            "effectiveness_verified": True,
            "verification_date": "2024-08-03T16:30:00Z",
            "verification_method": verification_data.get("verification_method"),
            "recurrence_prevented": verification_data.get("recurrence_prevented", True),
            "actual_cost_savings": verification_data.get("actual_cost_savings")
        },
        "message": "Lesson effectiveness verified successfully"
    }


@app.get("/api/v1/action-items")
async def get_action_items(
    status: str = None,
    priority: str = None,
    assigned_to: int = None,
    due_soon: bool = None,
    overdue: bool = None,
    limit: int = 50,
    offset: int = 0
):
    """Get action items with comprehensive filtering"""
    # Mock action items data
    action_items = [
        {
            "id": 1,
            "title": "Implement Zero Trust Network Architecture",
            "description": "Deploy comprehensive zero trust network segmentation to prevent lateral movement",
            "action_type": "technical_control",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": 5,
            "assigned_by": 1,
            "due_date": "2024-09-15T00:00:00Z",
            "progress_percentage": 65,
            "estimated_effort_hours": 160,
            "actual_effort_hours": 104,
            "source": "post_incident_review",
            "incident_id": 12,
            "created_at": "2024-06-01T10:00:00Z"
        },
        {
            "id": 2,
            "title": "Enhanced Security Awareness Training Program",
            "description": "Develop and deploy advanced phishing simulation and security awareness training",
            "action_type": "training",
            "priority": "medium",
            "status": "completed",
            "assigned_to": 8,
            "assigned_by": 2,
            "due_date": "2024-07-30T00:00:00Z",
            "progress_percentage": 100,
            "estimated_effort_hours": 80,
            "actual_effort_hours": 95,
            "effectiveness_rating": 4,
            "completed_at": "2024-07-25T16:30:00Z",
            "source": "lesson_learned",
            "lesson_learned_id": 3,
            "created_at": "2024-05-15T14:20:00Z"
        },
        {
            "id": 3,
            "title": "Cloud Security Posture Management Implementation",
            "description": "Deploy automated CSPM solution for continuous cloud security monitoring",
            "action_type": "technical_control",
            "priority": "critical",
            "status": "open",
            "assigned_to": 3,
            "assigned_by": 1,
            "due_date": "2024-08-20T00:00:00Z",
            "progress_percentage": 0,
            "estimated_effort_hours": 120,
            "source": "post_incident_review",
            "post_incident_review_id": 5,
            "created_at": "2024-07-01T09:15:00Z"
        }
    ]
    
    # Apply filters
    filtered_items = action_items
    if status:
        filtered_items = [item for item in filtered_items if item["status"] == status]
    if priority:
        filtered_items = [item for item in filtered_items if item["priority"] == priority]
    if assigned_to:
        filtered_items = [item for item in filtered_items if item["assigned_to"] == assigned_to]
    
    # Apply date filters
    from datetime import datetime, timedelta
    now = datetime.now()
    if due_soon:
        soon_date = now + timedelta(days=7)
        filtered_items = [item for item in filtered_items 
                         if datetime.fromisoformat(item["due_date"].replace('Z', '+00:00')) <= soon_date]
    if overdue:
        filtered_items = [item for item in filtered_items 
                         if datetime.fromisoformat(item["due_date"].replace('Z', '+00:00')) < now]
    
    # Apply pagination
    total = len(filtered_items)
    paginated_items = filtered_items[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": paginated_items,
        "summary": {
            "by_status": {
                "open": len([item for item in action_items if item["status"] == "open"]),
                "in_progress": len([item for item in action_items if item["status"] == "in_progress"]),
                "completed": len([item for item in action_items if item["status"] == "completed"])
            },
            "by_priority": {
                "critical": len([item for item in action_items if item["priority"] == "critical"]),
                "high": len([item for item in action_items if item["priority"] == "high"]),
                "medium": len([item for item in action_items if item["priority"] == "medium"]),
                "low": len([item for item in action_items if item["priority"] == "low"])
            },
            "overdue_count": len([item for item in action_items 
                                 if datetime.fromisoformat(item["due_date"].replace('Z', '+00:00')) < now]),
            "due_soon_count": len([item for item in action_items 
                                  if datetime.fromisoformat(item["due_date"].replace('Z', '+00:00')) <= now + timedelta(days=7)])
        }
    }


@app.post("/api/v1/action-items")
async def create_action_item(action_item_data: dict):
    """Create a new action item"""
    # Mock action item creation
    new_item = {
        "id": 99,
        "title": action_item_data.get("title"),
        "description": action_item_data.get("description"),
        "priority": action_item_data.get("priority", "medium"),
        "status": "open",
        "assigned_to": action_item_data.get("assigned_to"),
        "assigned_by": action_item_data.get("assigned_by"),
        "due_date": action_item_data.get("due_date"),
        "progress_percentage": 0,
        "created_at": "2024-08-03T16:30:00Z"
    }
    
    return {
        "success": True,
        "action_item": new_item,
        "message": "Action item created successfully"
    }


@app.put("/api/v1/action-items/{action_item_id}")
async def update_action_item(action_item_id: int, update_data: dict):
    """Update an existing action item"""
    return {
        "success": True,
        "action_item_id": action_item_id,
        "updated_fields": list(update_data.keys()),
        "message": "Action item updated successfully"
    }


@app.post("/api/v1/action-items/{action_item_id}/complete")
async def complete_action_item(action_item_id: int, completion_data: dict):
    """Mark an action item as completed"""
    return {
        "success": True,
        "action_item_id": action_item_id,
        "completion": {
            "status": "completed",
            "completed_at": "2024-08-03T16:30:00Z",
            "actual_effort_hours": completion_data.get("actual_effort_hours"),
            "effectiveness_rating": completion_data.get("effectiveness_rating"),
            "completion_notes": completion_data.get("completion_notes")
        },
        "message": "Action item marked as completed"
    }


@app.get("/api/v1/knowledge-articles")
async def get_knowledge_articles(
    category: str = None,
    article_type: str = None,
    published: bool = None,
    search: str = None,
    limit: int = 20,
    offset: int = 0
):
    """Get knowledge base articles with filtering and search"""
    # Mock knowledge articles data
    articles = [
        {
            "id": 1,
            "title": "Incident Response Playbook: Data Breach",
            "article_type": "playbook",
            "category": "incident_response",
            "summary": "Comprehensive step-by-step guide for responding to data breach incidents",
            "published": True,
            "author": {"id": 1, "name": "Security Team"},
            "view_count": 245,
            "usefulness_rating": 4.7,
            "created_at": "2024-01-15T10:00:00Z",
            "last_reviewed": "2024-06-01T14:30:00Z",
            "tags": ["data_breach", "incident_response", "playbook", "gdpr"]
        },
        {
            "id": 2,
            "title": "Multi-Factor Authentication Implementation Guide",
            "article_type": "guide",
            "category": "authentication",
            "summary": "Best practices for implementing and managing multi-factor authentication",
            "published": True,
            "author": {"id": 3, "name": "Identity Team"},
            "view_count": 189,
            "usefulness_rating": 4.5,
            "created_at": "2024-02-20T11:15:00Z",
            "last_reviewed": "2024-07-15T09:45:00Z",
            "tags": ["mfa", "authentication", "identity", "security_controls"]
        },
        {
            "id": 3,
            "title": "Cloud Security Configuration Checklist",
            "article_type": "checklist",
            "category": "cloud_security",
            "summary": "Essential security configurations for major cloud service providers",
            "published": False,
            "author": {"id": 5, "name": "Cloud Team"},
            "view_count": 67,
            "usefulness_rating": 4.2,
            "created_at": "2024-03-10T15:30:00Z",
            "last_reviewed": None,
            "tags": ["cloud", "aws", "azure", "gcp", "configuration"]
        }
    ]
    
    # Apply filters
    filtered_articles = articles
    if category:
        filtered_articles = [a for a in filtered_articles if a["category"] == category]
    if article_type:
        filtered_articles = [a for a in filtered_articles if a["article_type"] == article_type]
    if published is not None:
        filtered_articles = [a for a in filtered_articles if a["published"] == published]
    if search:
        search_lower = search.lower()
        filtered_articles = [a for a in filtered_articles 
                           if search_lower in a["title"].lower() or 
                           search_lower in a["summary"].lower() or
                           any(search_lower in tag for tag in a["tags"])]
    
    # Apply pagination
    total = len(filtered_articles)
    paginated_articles = filtered_articles[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": paginated_articles,
        "categories": ["incident_response", "authentication", "cloud_security", "network_security", "data_protection"],
        "article_types": ["playbook", "guide", "checklist", "procedure", "reference"],
        "facets": {
            "categories": [
                {"category": "incident_response", "count": 1},
                {"category": "authentication", "count": 1},
                {"category": "cloud_security", "count": 1}
            ],
            "article_types": [
                {"type": "playbook", "count": 1},
                {"type": "guide", "count": 1},
                {"type": "checklist", "count": 1}
            ]
        }
    }


@app.post("/api/v1/knowledge-articles")
async def create_knowledge_article(article_data: dict):
    """Create a new knowledge base article"""
    # Mock article creation
    new_article = {
        "id": 99,
        "title": article_data.get("title"),
        "article_type": article_data.get("article_type"),
        "category": article_data.get("category"),
        "summary": article_data.get("summary"),
        "content": article_data.get("content"),
        "published": False,
        "author_id": article_data.get("author_id"),
        "view_count": 0,
        "created_at": "2024-08-03T16:30:00Z"
    }
    
    return {
        "success": True,
        "article": new_article,
        "message": "Knowledge article created successfully"
    }


@app.get("/api/v1/knowledge-articles/{article_id}")
async def get_knowledge_article(article_id: int):
    """Get a specific knowledge article with full content"""
    # Mock article retrieval
    article = {
        "id": article_id,
        "title": "Incident Response Playbook: Data Breach",
        "article_type": "playbook",
        "category": "incident_response",
        "summary": "Comprehensive step-by-step guide for responding to data breach incidents",
        "content": "# Data Breach Incident Response Playbook\n\n## Immediate Actions (0-1 hours)\n\n1. **Containment**\n   - Isolate affected systems\n   - Preserve evidence\n   - Document initial findings\n\n2. **Assessment**\n   - Determine scope of breach\n   - Identify compromised data\n   - Assess business impact\n\n## Detailed Response Procedures...",
        "published": True,
        "author": {"id": 1, "name": "Security Team", "email": "security@company.com"},
        "view_count": 246,  # Incremented
        "usefulness_rating": 4.7,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-06-01T14:30:00Z",
        "last_reviewed": "2024-06-01T14:30:00Z",
        "tags": ["data_breach", "incident_response", "playbook", "gdpr"],
        "related_articles": [2, 5, 8],
        "prerequisites": ["Basic incident response training", "GDPR compliance knowledge"],
        "target_audience": ["security_analysts", "incident_responders", "compliance_team"],
        "version": "2.1"
    }
    
    return article


@app.put("/api/v1/knowledge-articles/{article_id}")
async def update_knowledge_article(article_id: int, update_data: dict):
    """Update an existing knowledge article"""
    return {
        "success": True,
        "article_id": article_id,
        "updated_fields": list(update_data.keys()),
        "new_version": "2.2",
        "message": "Knowledge article updated successfully"
    }


@app.post("/api/v1/knowledge-articles/{article_id}/publish")
async def publish_knowledge_article(article_id: int):
    """Publish a knowledge article"""
    return {
        "success": True,
        "article_id": article_id,
        "published_at": "2024-08-03T16:30:00Z",
        "message": "Knowledge article published successfully"
    }


@app.post("/api/v1/knowledge-articles/search")
async def search_knowledge_base(search_request: dict):
    """Advanced search in knowledge base with faceted results"""
    query = search_request.get("query", "")
    categories = search_request.get("categories", [])
    article_types = search_request.get("article_types", [])
    
    # Mock search results
    results = [
        {
            "id": 1,
            "title": "Incident Response Playbook: Data Breach",
            "summary": "Comprehensive step-by-step guide for responding to data breach incidents",
            "category": "incident_response",
            "article_type": "playbook",
            "relevance_score": 0.95,
            "highlighted_snippets": [
                "...comprehensive step-by-step guide for responding to <mark>data breach</mark> incidents...",
                "...immediate containment procedures for <mark>data breach</mark> scenarios..."
            ]
        },
        {
            "id": 4,
            "title": "Data Classification and Handling Procedures",
            "summary": "Guidelines for proper data classification and secure handling practices",
            "category": "data_protection",
            "article_type": "procedure",
            "relevance_score": 0.87,
            "highlighted_snippets": [
                "...proper <mark>data</mark> classification methodology...",
                "...secure handling of sensitive <mark>data</mark>..."
            ]
        }
    ]
    
    return {
        "total_results": len(results),
        "query": query,
        "results": results,
        "search_suggestions": ["data protection", "breach notification", "incident containment"],
        "related_searches": ["data breach response", "incident playbooks", "security procedures"],
        "facets": {
            "categories": [
                {"name": "incident_response", "count": 1, "selected": "incident_response" in categories},
                {"name": "data_protection", "count": 1, "selected": "data_protection" in categories}
            ],
            "article_types": [
                {"name": "playbook", "count": 1, "selected": "playbook" in article_types},
                {"name": "procedure", "count": 1, "selected": "procedure" in article_types}
            ]
        },
        "search_metadata": {
            "search_time_ms": 45,
            "total_articles_indexed": 127,
            "last_index_update": "2024-08-03T12:00:00Z"
        }
    }


@app.get("/api/v1/trend-analyses")
async def get_trend_analyses(
    analysis_type: str = None,
    time_period: str = None,
    limit: int = 20,
    offset: int = 0
):
    """Get trend analyses with filtering"""
    # Mock trend analyses data
    analyses = [
        {
            "id": 1,
            "analysis_name": "Q2 2024 Security Incident Trends",
            "analysis_type": "incident_trends",
            "time_period_start": "2024-04-01T00:00:00Z",
            "time_period_end": "2024-06-30T23:59:59Z",
            "analyst": {"id": 2, "name": "Analytics Team"},
            "key_trends": [
                "23% increase in phishing attempts",
                "Shift toward cloud-based attack vectors",
                "Reduced mean time to detection by 18%"
            ],
            "confidence_level": "high",
            "approved": True,
            "analysis_date": "2024-07-15T10:00:00Z",
            "created_at": "2024-07-10T14:30:00Z"
        },
        {
            "id": 2,
            "analysis_name": "Lessons Learned Effectiveness Review",
            "analysis_type": "lesson_effectiveness",
            "time_period_start": "2024-01-01T00:00:00Z",
            "time_period_end": "2024-06-30T23:59:59Z",
            "analyst": {"id": 3, "name": "Process Improvement Team"},
            "key_trends": [
                "76.9% implementation success rate for lessons learned",
                "84.6% recurrence prevention rate",
                "Technical controls show highest effectiveness"
            ],
            "confidence_level": "high",
            "approved": True,
            "analysis_date": "2024-07-20T15:00:00Z",
            "created_at": "2024-07-15T09:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_analyses = analyses
    if analysis_type:
        filtered_analyses = [a for a in filtered_analyses if a["analysis_type"] == analysis_type]
    
    # Apply pagination
    total = len(filtered_analyses)
    paginated_analyses = filtered_analyses[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": paginated_analyses,
        "analysis_types": ["incident_trends", "lesson_effectiveness", "response_performance", "cost_analysis"]
    }


@app.post("/api/v1/trend-analyses")
async def create_trend_analysis(analysis_data: dict):
    """Create a new trend analysis"""
    # Mock trend analysis creation
    new_analysis = {
        "id": 99,
        "analysis_name": analysis_data.get("analysis_name"),
        "analysis_type": analysis_data.get("analysis_type"),
        "time_period_start": analysis_data.get("time_period_start"),
        "time_period_end": analysis_data.get("time_period_end"),
        "analyst_id": analysis_data.get("analyst_id"),
        "confidence_level": "medium",
        "approved": False,
        "analysis_date": "2024-08-03T16:30:00Z",
        "created_at": "2024-08-03T16:30:00Z"
    }
    
    return {
        "success": True,
        "analysis": new_analysis,
        "message": "Trend analysis created successfully"
    }


@app.get("/api/v1/trend-analyses/{analysis_id}")
async def get_trend_analysis(analysis_id: int):
    """Get detailed trend analysis"""
    # Mock detailed trend analysis
    analysis = {
        "id": analysis_id,
        "analysis_name": "Q2 2024 Security Incident Trends",
        "analysis_type": "incident_trends",
        "time_period_start": "2024-04-01T00:00:00Z",
        "time_period_end": "2024-06-30T23:59:59Z",
        "analyst": {"id": 2, "name": "Analytics Team"},
        "methodology": "Statistical analysis of incident data with trend identification using time series analysis",
        "key_trends": [
            "23% increase in phishing attempts targeting remote workers",
            "Shift toward cloud-based attack vectors (45% of incidents)",
            "Reduced mean time to detection by 18% due to improved monitoring"
        ],
        "emerging_patterns": [
            "Coordinated attacks during business hours",
            "Increased targeting of SaaS applications",
            "Supply chain attack attempts"
        ],
        "incident_volume_trend": {
            "april": 28,
            "may": 32,
            "june": 34,
            "trend": "increasing"
        },
        "severity_distribution_trend": {
            "critical": {"q2": 8, "q1": 12, "change": -33.3},
            "high": {"q2": 15, "q1": 18, "change": -16.7},
            "medium": {"q2": 45, "q1": 38, "change": 18.4},
            "low": {"q2": 26, "q1": 22, "change": 18.2}
        },
        "strategic_recommendations": [
            "Enhance remote worker security training",
            "Implement advanced cloud security monitoring",
            "Develop supply chain security assessment program"
        ],
        "confidence_level": "high",
        "limitations": "Analysis limited to detected incidents; may not capture all threats",
        "business_impact": "Recommendations could reduce incident volume by estimated 25-30%",
        "approved": True,
        "approved_by": {"id": 1, "name": "CISO"},
        "approved_at": "2024-07-16T11:00:00Z"
    }
    
    return analysis


@app.get("/api/v1/dashboards/post-incident-analytics")
async def get_post_incident_analytics_dashboard():
    """Comprehensive post-incident analytics dashboard"""
    return {
        "lessons_learned_summary": {
            "total_lessons": 28,
            "lessons_this_quarter": 8,
            "implemented_lessons": 22,
            "verified_effectiveness": 18,
            "lessons_by_category": {
                "authentication": 5,
                "cloud_security": 6,
                "email_security": 4,
                "network_security": 7,
                "data_protection": 6
            },
            "implementation_status_distribution": {
                "identified": 3,
                "planned": 2,
                "in_progress": 5,
                "implemented": 10,
                "verified": 8
            },
            "total_cost_savings": 12500000,
            "recurrence_prevention_rate": 84.6
        },
        "knowledge_base_summary": {
            "total_articles": 127,
            "published_articles": 98,
            "articles_this_month": 12,
            "pending_review": 15,
            "articles_by_category": {
                "incident_response": 25,
                "security_procedures": 30,
                "compliance": 18,
                "technical_guides": 35,
                "training_materials": 19
            },
            "most_viewed_articles": [
                {"id": 1, "title": "Incident Response Playbook: Data Breach", "views": 246},
                {"id": 2, "title": "Multi-Factor Authentication Implementation", "views": 189},
                {"id": 3, "title": "Cloud Security Best Practices", "views": 167}
            ],
            "search_activity": {
                "monthly_searches": 847,
                "top_search_terms": ["incident response", "data breach", "mfa", "cloud security"],
                "search_success_rate": 78.5
            }
        },
        "action_items_summary": {
            "total_active": 45,
            "completed_this_quarter": 23,
            "overdue": 3,
            "due_this_week": 8,
            "by_priority": {
                "critical": {"total": 8, "completed": 6, "in_progress": 2},
                "high": {"total": 15, "completed": 12, "in_progress": 3},
                "medium": {"total": 18, "completed": 12, "in_progress": 6},
                "low": {"total": 4, "completed": 2, "in_progress": 2}
            },
            "completion_rate_trend": {
                "q1_2024": 72.5,
                "q2_2024": 78.9,
                "trend": "improving"
            }
        },
        "trend_analysis_summary": {
            "completed_analyses": 6,
            "analyses_this_quarter": 2,
            "key_insights": [
                "Incident volume trending downward (-15% YoY)",
                "Mean time to resolution improved by 23%",
                "Lessons learned implementation rate above target (76.9%)"
            ],
            "upcoming_analyses": [
                {"name": "Q3 Vulnerability Trends", "due": "2024-10-15"},
                {"name": "Cloud Security Posture Review", "due": "2024-11-01"}
            ]
        },
        "effectiveness_metrics": {
            "post_incident_review_completion_rate": 89.2,
            "lessons_learned_implementation_rate": 76.9,
            "knowledge_base_utilization_rate": 65.4,
            "recurrence_prevention_rate": 84.6,
            "cost_benefit_analysis": {
                "total_prevention_investment": 1800000,
                "estimated_cost_avoided": 8400000,
                "roi_percentage": 366.7
            }
        },
        "recent_activities": [
            {
                "type": "lesson_learned",
                "title": "Multi-Factor Authentication Bypass Prevention",
                "date": "2024-08-01T10:30:00Z",
                "status": "implemented"
            },
            {
                "type": "knowledge_article",
                "title": "Cloud Security Configuration Checklist",
                "date": "2024-07-28T14:15:00Z",
                "status": "published"
            },
            {
                "type": "trend_analysis",
                "title": "Q2 2024 Security Incident Trends",
                "date": "2024-07-15T10:00:00Z",
                "status": "approved"
            }
        ]
    }

# =============================================================================
# TRAINING MANAGEMENT API ENDPOINTS
# =============================================================================

# Training Program Management
@app.get("/api/v1/training/programs")
async def get_training_programs(
    skip: int = 0,
    limit: int = 20,
    program_type: str = None,
    priority: str = None,
    mandatory: bool = None,
    active: bool = None,
    target_role: str = None,
    target_department: str = None
):
    """Get training programs with filtering and pagination"""
    programs = [
        {
            "id": 1,
            "program_id": "PROG-A1B2C3D4",
            "name": "Cybersecurity Awareness Training",
            "description": "Comprehensive cybersecurity awareness training covering phishing, social engineering, password security, and data protection",
            "version": "2.1",
            "program_type": "mandatory",
            "priority": "high",
            "duration_hours": 8.0,
            "target_roles": ["all_employees"],
            "target_departments": ["all"],
            "prerequisite_programs": [],
            "required_certifications": [],
            "mandatory": True,
            "recurring": True,
            "recurrence_months": 12,
            "grace_period_days": 30,
            "learning_objectives": [
                "Identify common phishing and social engineering attacks",
                "Apply secure password practices",
                "Understand data classification and handling procedures",
                "Follow incident reporting procedures"
            ],
            "competencies_addressed": ["security_awareness", "phishing_detection", "data_protection"],
            "compliance_frameworks": ["ISO27001", "NIST_CSF", "SOC2"],
            "active": True,
            "auto_enroll": True,
            "approval_required": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "created_by": "admin@company.com",
            "updated_by": "admin@company.com"
        },
        {
            "id": 2,
            "program_id": "PROG-B2C3D4E5",
            "name": "Advanced Threat Detection",
            "description": "Advanced training for security analysts on threat detection, incident analysis, and response procedures",
            "version": "1.0",
            "program_type": "skill_building",
            "priority": "high",
            "duration_hours": 24.0,
            "target_roles": ["security_analyst", "soc_analyst", "incident_responder"],
            "target_departments": ["security", "it"],
            "prerequisite_programs": ["PROG-A1B2C3D4"],
            "required_certifications": [],
            "mandatory": False,
            "recurring": False,
            "recurrence_months": None,
            "grace_period_days": 60,
            "learning_objectives": [
                "Master advanced threat hunting techniques",
                "Analyze complex security incidents",
                "Implement effective response strategies",
                "Use SIEM and threat intelligence tools"
            ],
            "competencies_addressed": ["threat_hunting", "incident_analysis", "siem_operation"],
            "compliance_frameworks": ["NIST_CSF"],
            "active": True,
            "auto_enroll": False,
            "approval_required": True,
            "created_at": "2024-01-10T00:00:00Z",
            "updated_at": "2024-01-20T14:22:00Z",
            "created_by": "security.lead@company.com",
            "updated_by": "security.lead@company.com"
        },
        {
            "id": 3,
            "program_id": "PROG-C3D4E5F6",
            "name": "GDPR Compliance Training",
            "description": "Data protection and GDPR compliance training for all staff handling personal data",
            "version": "1.2",
            "program_type": "certification",
            "priority": "critical",
            "duration_hours": 6.0,
            "target_roles": ["data_handler", "hr", "sales", "marketing"],
            "target_departments": ["hr", "sales", "marketing", "support"],
            "prerequisite_programs": [],
            "required_certifications": [],
            "mandatory": True,
            "recurring": True,
            "recurrence_months": 24,
            "grace_period_days": 15,
            "learning_objectives": [
                "Understand GDPR principles and requirements",
                "Implement data protection by design",
                "Handle data subject requests properly",
                "Recognize and report data breaches"
            ],
            "competencies_addressed": ["gdpr_compliance", "data_protection", "privacy"],
            "compliance_frameworks": ["GDPR", "ISO27001"],
            "active": True,
            "auto_enroll": True,
            "approval_required": False,
            "created_at": "2024-01-05T00:00:00Z",
            "updated_at": "2024-01-25T09:15:00Z",
            "created_by": "compliance@company.com",
            "updated_by": "compliance@company.com"
        }
    ]
    
    # Apply filters
    filtered_programs = programs
    if program_type:
        filtered_programs = [p for p in filtered_programs if p["program_type"] == program_type]
    if priority:
        filtered_programs = [p for p in filtered_programs if p["priority"] == priority]
    if mandatory is not None:
        filtered_programs = [p for p in filtered_programs if p["mandatory"] == mandatory]
    if active is not None:
        filtered_programs = [p for p in filtered_programs if p["active"] == active]
    if target_role:
        filtered_programs = [p for p in filtered_programs if target_role in p["target_roles"] or "all_employees" in p["target_roles"]]
    if target_department:
        filtered_programs = [p for p in filtered_programs if target_department in p["target_departments"] or "all" in p["target_departments"]]
    
    paginated_programs = filtered_programs[skip:skip + limit]
    
    return {
        "items": paginated_programs,
        "total": len(filtered_programs),
        "skip": skip,
        "limit": limit,
        "summary": {
            "mandatory": len([p for p in filtered_programs if p["mandatory"]]),
            "optional": len([p for p in filtered_programs if not p["mandatory"]]),
            "active": len([p for p in filtered_programs if p["active"]]),
            "recurring": len([p for p in filtered_programs if p["recurring"]])
        }
    }

@app.post("/api/v1/training/programs")
async def create_training_program(program_data: dict):
    """Create a new training program"""
    import random
    return {
        "id": random.randint(100, 999),
        "program_id": f"PROG-{random.randint(10000000, 99999999):08X}",
        "name": program_data.get("name"),
        "description": program_data.get("description"),
        "program_type": program_data.get("program_type", "optional"),
        "priority": program_data.get("priority", "medium"),
        "created_at": datetime.now().isoformat(),
        "message": "Training program created successfully"
    }

@app.get("/api/v1/training/programs/{program_id}")
async def get_training_program(program_id: int):
    """Get specific training program details"""
    if program_id == 1:
        return {
            "id": 1,
            "program_id": "PROG-A1B2C3D4",
            "name": "Cybersecurity Awareness Training",
            "description": "Comprehensive cybersecurity awareness training covering phishing, social engineering, password security, and data protection",
            "version": "2.1",
            "program_type": "mandatory",
            "priority": "high",
            "duration_hours": 8.0,
            "target_roles": ["all_employees"],
            "target_departments": ["all"],
            "courses": [
                {
                    "id": 1,
                    "course_id": "COURSE-12345678",
                    "title": "Phishing Awareness",
                    "duration_minutes": 120,
                    "sequence_order": 1,
                    "passing_score": 80.0
                },
                {
                    "id": 2,
                    "course_id": "COURSE-23456789",
                    "title": "Password Security",
                    "duration_minutes": 90,
                    "sequence_order": 2,
                    "passing_score": 75.0
                }
            ],
            "enrollment_statistics": {
                "total_enrolled": 1250,
                "completed": 987,
                "in_progress": 145,
                "not_started": 118,
                "completion_rate": 78.96
            }
        }
    return {"error": "Training program not found"}

# Training Enrollments
@app.get("/api/v1/training/enrollments")
async def get_training_enrollments(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    user_role: str = None,
    department: str = None,
    overdue: bool = None,
    program_id: int = None
):
    """Get training enrollments with filtering"""
    enrollments = [
        {
            "id": 1,
            "enrollment_id": "ENROLL-A1B2C3D4",
            "program_id": 1,
            "program_name": "Cybersecurity Awareness Training",
            "user_id": "user123",
            "user_email": "john.doe@company.com",
            "user_name": "John Doe",
            "user_role": "developer",
            "department": "engineering",
            "enrollment_date": "2024-01-15T00:00:00Z",
            "due_date": "2024-02-15T00:00:00Z",
            "assigned_by": "hr@company.com",
            "enrollment_type": "auto",
            "status": "in_progress",
            "progress_percentage": 65.0,
            "started_date": "2024-01-20T09:00:00Z",
            "completed_date": None,
            "last_accessed": "2024-01-25T14:30:00Z",
            "final_score": None,
            "certificate_issued": False,
            "attempts_count": 1,
            "is_overdue": False
        },
        {
            "id": 2,
            "enrollment_id": "ENROLL-B2C3D4E5",
            "program_id": 1,
            "program_name": "Cybersecurity Awareness Training",
            "user_id": "user456",
            "user_email": "jane.smith@company.com",
            "user_name": "Jane Smith",
            "user_role": "analyst",
            "department": "security",
            "enrollment_date": "2024-01-10T00:00:00Z",
            "due_date": "2024-02-10T00:00:00Z",
            "assigned_by": "security.lead@company.com",
            "enrollment_type": "manual",
            "status": "completed",
            "progress_percentage": 100.0,
            "started_date": "2024-01-12T10:00:00Z",
            "completed_date": "2024-01-22T16:45:00Z",
            "last_accessed": "2024-01-22T16:45:00Z",
            "final_score": 92.5,
            "certificate_issued": True,
            "certificate_id": "CERT-B2C3D4E5",
            "attempts_count": 1,
            "is_overdue": False
        }
    ]
    
    # Apply filters
    filtered_enrollments = enrollments
    if status:
        filtered_enrollments = [e for e in filtered_enrollments if e["status"] == status]
    if user_role:
        filtered_enrollments = [e for e in filtered_enrollments if e["user_role"] == user_role]
    if department:
        filtered_enrollments = [e for e in filtered_enrollments if e["department"] == department]
    if program_id:
        filtered_enrollments = [e for e in filtered_enrollments if e["program_id"] == program_id]
    if overdue is not None:
        filtered_enrollments = [e for e in filtered_enrollments if e["is_overdue"] == overdue]
    
    paginated_enrollments = filtered_enrollments[skip:skip + limit]
    
    return {
        "items": paginated_enrollments,
        "total": len(filtered_enrollments),
        "skip": skip,
        "limit": limit,
        "summary": {
            "completed": len([e for e in filtered_enrollments if e["status"] == "completed"]),
            "in_progress": len([e for e in filtered_enrollments if e["status"] == "in_progress"]),
            "not_started": len([e for e in filtered_enrollments if e["status"] == "not_started"]),
            "overdue": len([e for e in filtered_enrollments if e["is_overdue"]])
        }
    }

@app.post("/api/v1/training/enrollments")
async def create_training_enrollment(enrollment_data: dict):
    """Create a new training enrollment"""
    import random
    return {
        "id": random.randint(100, 999),
        "enrollment_id": f"ENROLL-{random.randint(10000000, 99999999):08X}",
        "program_id": enrollment_data.get("program_id"),
        "user_id": enrollment_data.get("user_id"),
        "user_email": enrollment_data.get("user_email"),
        "enrollment_date": datetime.now().isoformat(),
        "status": "not_started",
        "message": "Training enrollment created successfully"
    }

# Phishing Simulations and Awareness Campaigns
@app.get("/api/v1/training/campaigns")
async def get_awareness_campaigns(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    campaign_type: str = None,
    target_department: str = None
):
    """Get awareness campaigns with filtering"""
    campaigns = [
        {
            "id": 1,
            "campaign_id": "CAMP-A1B2C3D4",
            "name": "Q1 2024 Phishing Simulation",
            "description": "Quarterly phishing simulation targeting all employees with sophisticated email templates",
            "campaign_type": "phishing",
            "status": "completed",
            "scheduled_start": "2024-01-15T09:00:00Z",
            "scheduled_end": "2024-01-22T17:00:00Z",
            "actual_start": "2024-01-15T09:00:00Z",
            "actual_end": "2024-01-22T17:00:00Z",
            "target_users": [],
            "target_departments": ["all"],
            "target_roles": ["all_employees"],
            "total_recipients": 1250,
            "delivered_count": 1245,
            "opened_count": 387,
            "clicked_count": 89,
            "reported_count": 156,
            "failed_count": 5,
            "success_rate": 71.2,
            "click_rate": 7.1,
            "report_rate": 12.5,
            "created_by": "security.awareness@company.com",
            "approved_by": "ciso@company.com",
            "approval_date": "2024-01-10T10:00:00Z",
            "tags": ["quarterly", "phishing", "company-wide"]
        },
        {
            "id": 2,
            "campaign_id": "CAMP-B2C3D4E5",
            "name": "Executive Security Briefing",
            "description": "Monthly security awareness briefing for executive leadership team",
            "campaign_type": "awareness",
            "status": "active",
            "scheduled_start": "2024-01-25T10:00:00Z",
            "scheduled_end": "2024-01-25T11:00:00Z",
            "actual_start": "2024-01-25T10:00:00Z",
            "actual_end": None,
            "target_users": ["ceo", "cto", "cfo", "ciso"],
            "target_departments": ["executive"],
            "target_roles": ["c_level"],
            "total_recipients": 4,
            "delivered_count": 4,
            "opened_count": 4,
            "clicked_count": 0,
            "reported_count": 0,
            "failed_count": 0,
            "success_rate": 100.0,
            "click_rate": 0.0,
            "report_rate": 0.0,
            "created_by": "security.awareness@company.com",
            "approved_by": "ciso@company.com",
            "approval_date": "2024-01-20T14:00:00Z",
            "tags": ["monthly", "executive", "briefing"]
        }
    ]
    
    # Apply filters
    filtered_campaigns = campaigns
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c["status"] == status]
    if campaign_type:
        filtered_campaigns = [c for c in filtered_campaigns if c["campaign_type"] == campaign_type]
    if target_department:
        filtered_campaigns = [c for c in filtered_campaigns if target_department in c["target_departments"] or "all" in c["target_departments"]]
    
    paginated_campaigns = filtered_campaigns[skip:skip + limit]
    
    return {
        "items": paginated_campaigns,
        "total": len(filtered_campaigns),
        "skip": skip,
        "limit": limit,
        "summary": {
            "active": len([c for c in filtered_campaigns if c["status"] == "active"]),
            "completed": len([c for c in filtered_campaigns if c["status"] == "completed"]),
            "scheduled": len([c for c in filtered_campaigns if c["status"] == "scheduled"]),
            "phishing": len([c for c in filtered_campaigns if c["campaign_type"] == "phishing"])
        }
    }

@app.get("/api/v1/training/campaigns/{campaign_id}/results")
async def get_campaign_results(campaign_id: int):
    """Get detailed results for a specific campaign"""
    if campaign_id == 1:
        return {
            "campaign_id": campaign_id,
            "campaign_name": "Q1 2024 Phishing Simulation",
            "overall_metrics": {
                "total_recipients": 1250,
                "delivered_count": 1245,
                "opened_count": 387,
                "clicked_count": 89,
                "reported_count": 156,
                "failed_count": 5,
                "success_rate": 71.2,
                "click_rate": 7.1,
                "report_rate": 12.5
            },
            "department_breakdown": [
                {
                    "department": "engineering",
                    "recipients": 450,
                    "clicked": 28,
                    "reported": 67,
                    "click_rate": 6.2,
                    "report_rate": 14.9
                },
                {
                    "department": "sales",
                    "recipients": 200,
                    "clicked": 18,
                    "reported": 22,
                    "click_rate": 9.0,
                    "report_rate": 11.0
                },
                {
                    "department": "hr",
                    "recipients": 50,
                    "clicked": 8,
                    "reported": 12,
                    "click_rate": 16.0,
                    "report_rate": 24.0
                }
            ],
            "risk_users": [
                {
                    "user_id": "user789",
                    "user_email": "risky.user@company.com",
                    "department": "sales",
                    "clicked": True,
                    "reported": False,
                    "response_time_seconds": 45,
                    "training_assigned": True
                }
            ],
            "simulation_details": {
                "template_name": "Invoice Payment Request",
                "difficulty_level": "intermediate",
                "attack_vector": "email",
                "indicators": ["urgent_language", "external_sender", "suspicious_link"]
            }
        }
    return {"error": "Campaign results not found"}

@app.post("/api/v1/training/campaigns")
async def create_awareness_campaign(campaign_data: dict):
    """Create a new awareness campaign"""
    import random
    return {
        "id": random.randint(100, 999),
        "campaign_id": f"CAMP-{random.randint(10000000, 99999999):08X}",
        "name": campaign_data.get("name"),
        "campaign_type": campaign_data.get("campaign_type", "awareness"),
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "message": "Awareness campaign created successfully"
    }

# Security Competencies and Assessments
@app.get("/api/v1/training/competencies")
async def get_security_competencies(
    skip: int = 0,
    limit: int = 20,
    skill_level: str = None,
    domain: str = None,
    active: bool = None
):
    """Get security competencies with filtering"""
    competencies = [
        {
            "id": 1,
            "competency_id": "COMP-A1B2C3D4",
            "name": "Phishing Detection",
            "description": "Ability to identify and respond to phishing attempts across various communication channels",
            "category": "awareness",
            "skill_level": "beginner",
            "domain": "email_security",
            "framework_reference": "NIST-NICE-SP-RSK-001",
            "applicable_roles": ["all_employees"],
            "applicable_departments": ["all"],
            "assessment_methods": ["simulation", "quiz"],
            "proficiency_indicators": [
                "Correctly identifies 90% of phishing emails",
                "Reports suspicious emails within 15 minutes",
                "Completes phishing training with 85% score"
            ],
            "active": True,
            "version": "1.0"
        },
        {
            "id": 2,
            "competency_id": "COMP-B2C3D4E5",
            "name": "Incident Response Coordination",
            "description": "Advanced skills in coordinating and managing security incident response activities",
            "category": "technical",
            "skill_level": "advanced",
            "domain": "incident_response",
            "framework_reference": "NIST-NICE-IN-IR-001",
            "applicable_roles": ["incident_responder", "security_analyst", "soc_manager"],
            "applicable_departments": ["security", "it"],
            "assessment_methods": ["practical", "simulation"],
            "proficiency_indicators": [
                "Successfully coordinates major incident response within 4 hours",
                "Maintains accurate incident documentation",
                "Effectively communicates with stakeholders during incidents"
            ],
            "active": True,
            "version": "2.0"
        }
    ]
    
    # Apply filters
    filtered_competencies = competencies
    if skill_level:
        filtered_competencies = [c for c in filtered_competencies if c["skill_level"] == skill_level]
    if domain:
        filtered_competencies = [c for c in filtered_competencies if c["domain"] == domain]
    if active is not None:
        filtered_competencies = [c for c in filtered_competencies if c["active"] == active]
    
    paginated_competencies = filtered_competencies[skip:skip + limit]
    
    return {
        "items": paginated_competencies,
        "total": len(filtered_competencies),
        "skip": skip,
        "limit": limit,
        "summary": {
            "beginner": len([c for c in filtered_competencies if c["skill_level"] == "beginner"]),
            "intermediate": len([c for c in filtered_competencies if c["skill_level"] == "intermediate"]),
            "advanced": len([c for c in filtered_competencies if c["skill_level"] == "advanced"]),
            "expert": len([c for c in filtered_competencies if c["skill_level"] == "expert"])
        }
    }

@app.get("/api/v1/training/user-competencies/{user_id}")
async def get_user_competencies(user_id: str):
    """Get competency status for a specific user"""
    return {
        "user_id": user_id,
        "competencies": [
            {
                "competency_id": "COMP-A1B2C3D4",
                "competency_name": "Phishing Detection",
                "current_level": "intermediate",
                "target_level": "advanced",
                "proficient": True,
                "last_assessed": "2024-01-20T10:00:00Z",
                "last_assessment_score": 87.5,
                "assessment_count": 3,
                "training_hours": 4.5,
                "expires_at": "2025-01-20T10:00:00Z",
                "renewal_required": False
            },
            {
                "competency_id": "COMP-B2C3D4E5",
                "competency_name": "Incident Response Coordination",
                "current_level": "beginner",
                "target_level": "intermediate",
                "proficient": False,
                "last_assessed": None,
                "last_assessment_score": None,
                "assessment_count": 0,
                "training_hours": 0.0,
                "expires_at": None,
                "renewal_required": False,
                "next_assessment_due": "2024-02-15T00:00:00Z"
            }
        ],
        "summary": {
            "total_competencies": 2,
            "proficient_competencies": 1,
            "assessments_due": 1,
            "certifications_expiring_soon": 0
        }
    }

# Training Certifications
@app.get("/api/v1/training/certifications")
async def get_training_certifications(
    skip: int = 0,
    limit: int = 20,
    certification_type: str = None,
    active: bool = None
):
    """Get training certifications with filtering"""
    certifications = [
        {
            "id": 1,
            "certification_id": "CERT-A1B2C3D4",
            "name": "Cybersecurity Awareness Certification",
            "description": "Certification for completing comprehensive cybersecurity awareness training",
            "issuing_organization": "Aegis Security Training",
            "certification_type": "internal",
            "required_training_programs": [1],
            "required_competencies": [1],
            "validity_period_months": 12,
            "renewal_required": True,
            "renewal_grace_period_days": 30,
            "continuing_education_required": False,
            "compliance_frameworks": ["ISO27001", "SOC2"],
            "minimum_score": 80.0,
            "assessment_required": True,
            "practical_demonstration": False,
            "active": True
        },
        {
            "id": 2,
            "certification_id": "CERT-B2C3D4E5",
            "name": "Advanced Incident Response Certification",
            "description": "Advanced certification for incident response specialists",
            "issuing_organization": "Aegis Security Training",
            "certification_type": "internal",
            "required_training_programs": [2],
            "required_competencies": [2],
            "validity_period_months": 24,
            "renewal_required": True,
            "renewal_grace_period_days": 60,
            "continuing_education_required": True,
            "compliance_frameworks": ["NIST_CSF"],
            "minimum_score": 85.0,
            "assessment_required": True,
            "practical_demonstration": True,
            "active": True
        }
    ]
    
    # Apply filters
    filtered_certifications = certifications
    if certification_type:
        filtered_certifications = [c for c in filtered_certifications if c["certification_type"] == certification_type]
    if active is not None:
        filtered_certifications = [c for c in filtered_certifications if c["active"] == active]
    
    paginated_certifications = filtered_certifications[skip:skip + limit]
    
    return {
        "items": paginated_certifications,
        "total": len(filtered_certifications),
        "skip": skip,
        "limit": limit,
        "summary": {
            "internal": len([c for c in filtered_certifications if c["certification_type"] == "internal"]),
            "external": len([c for c in filtered_certifications if c["certification_type"] == "external"]),
            "regulatory": len([c for c in filtered_certifications if c["certification_type"] == "regulatory"])
        }
    }

@app.get("/api/v1/training/user-certifications/{user_id}")
async def get_user_certifications(user_id: str):
    """Get certification status for a specific user"""
    return {
        "user_id": user_id,
        "certifications": [
            {
                "certification_id": "CERT-A1B2C3D4",
                "certification_name": "Cybersecurity Awareness Certification",
                "status": "completed",
                "earned_date": "2024-01-22T16:45:00Z",
                "expires_date": "2025-01-22T16:45:00Z",
                "certificate_number": "CSA-2024-001234",
                "digital_badge_url": "https://badges.company.com/csa-001234",
                "final_score": 92.5,
                "verified": True,
                "renewal_due_date": "2025-01-22T16:45:00Z",
                "renewal_reminders_sent": 0,
                "days_until_expiration": 362
            },
            {
                "certification_id": "CERT-B2C3D4E5",
                "certification_name": "Advanced Incident Response Certification",
                "status": "in_progress",
                "earned_date": None,
                "expires_date": None,
                "certificate_number": None,
                "digital_badge_url": None,
                "final_score": None,
                "verified": False,
                "renewal_due_date": None,
                "renewal_reminders_sent": 0,
                "progress_percentage": 45.0
            }
        ],
        "summary": {
            "total_certifications": 2,
            "earned_certifications": 1,
            "in_progress_certifications": 1,
            "expiring_soon": 0
        }
    }

# Training Analytics and Dashboard
@app.get("/api/v1/dashboards/training")
async def get_training_dashboard():
    """Get training management dashboard summary"""
    return {
        "overview_metrics": {
            "total_programs": 25,
            "active_programs": 18,
            "total_enrollments": 3420,
            "completed_enrollments": 2756,
            "completion_rate": 80.6,
            "average_score": 84.2,
            "overdue_trainings": 145,
            "certificates_issued": 2156,
            "active_campaigns": 3,
            "this_month_enrollments": 247
        },
        "phishing_simulation_results": {
            "total_simulations": 12,
            "total_recipients": 15000,
            "overall_click_rate": 8.3,
            "overall_report_rate": 15.7,
            "improvement_rate": 12.4,
            "high_risk_users": 89,
            "training_assignments": 156
        },
        "compliance_training": {
            "mandatory_completion_rate": 92.3,
            "gdpr_compliance_rate": 96.8,
            "security_awareness_rate": 89.1,
            "overdue_mandatory": 78,
            "expiring_certifications": 23
        },
        "competency_analysis": {
            "total_competencies": 45,
            "assessed_users": 1250,
            "proficient_users": 987,
            "proficiency_rate": 78.9,
            "skills_gaps": 15,
            "assessment_completion_rate": 85.2
        },
        "training_trends": {
            "monthly_completions": [180, 195, 220, 247],
            "monthly_enrollments": [250, 280, 310, 295],
            "phishing_click_rates": [12.3, 10.8, 9.2, 8.3],
            "competency_improvements": [15, 22, 18, 25]
        },
        "department_performance": [
            {"department": "engineering", "completion_rate": 87.2, "avg_score": 86.1},
            {"department": "sales", "completion_rate": 79.8, "avg_score": 82.3},
            {"department": "hr", "completion_rate": 95.1, "avg_score": 91.4},
            {"department": "finance", "completion_rate": 88.7, "avg_score": 84.9}
        ]
    }

@app.get("/api/v1/training/analytics/user-progress/{user_id}")
async def get_user_training_progress(user_id: str):
    """Get detailed training progress for a specific user"""
    return {
        "user_id": user_id,
        "user_email": "john.doe@company.com",
        "user_name": "John Doe",
        "active_training": [
            {
                "program_id": 1,
                "program_name": "Cybersecurity Awareness Training",
                "enrollment_id": "ENROLL-A1B2C3D4",
                "progress_percentage": 65.0,
                "due_date": "2024-02-15T00:00:00Z",
                "days_until_due": 21,
                "last_accessed": "2024-01-25T14:30:00Z"
            }
        ],
        "completed_training": [
            {
                "program_id": 3,
                "program_name": "GDPR Compliance Training",
                "completion_date": "2024-01-10T16:30:00Z",
                "final_score": 89.5,
                "certificate_id": "CERT-GDPR-001"
            }
        ],
        "recent_phishing_results": [
            {
                "campaign_id": 1,
                "campaign_name": "Q1 2024 Phishing Simulation",
                "result": "reported",
                "response_time_seconds": 127,
                "risk_level": "low"
            }
        ],
        "competency_summary": [
            {
                "competency_name": "Phishing Detection",
                "current_level": "intermediate",
                "proficient": True,
                "last_assessment_score": 87.5
            }
        ],
        "certifications": [
            {
                "certification_name": "Cybersecurity Awareness Certification",
                "status": "earned",
                "expires_date": "2025-01-22T16:45:00Z"
            }
        ],
        "summary": {
            "total_programs_enrolled": 2,
            "completed_programs": 1,
            "completion_rate": 50.0,
            "average_score": 89.5,
            "overdue_trainings": 0,
            "certifications_earned": 1
        }
    }

# ===================== Business Continuity and Disaster Recovery API Endpoints =====================

# Business Continuity Plans
@app.get("/api/v1/continuity/plans")
async def get_continuity_plans(
    status: str = None,
    business_unit: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get business continuity plans with filtering"""
    plans = [
        {
            "id": 1,
            "plan_id": "BCP-001",
            "name": "IT Systems Business Continuity Plan",
            "description": "Comprehensive continuity plan for critical IT systems",
            "version": "2.1",
            "status": "active",
            "scope": "All IT infrastructure and applications",
            "business_units": ["IT", "Operations", "Customer Service"],
            "geographic_scope": ["Primary Data Center", "DR Site"],
            "objectives": "Ensure 99.9% uptime for critical systems",
            "next_review_date": "2024-12-15T00:00:00Z",
            "created_at": "2024-01-15T09:00:00Z",
            "created_by": "john.doe@company.com"
        },
        {
            "id": 2,
            "plan_id": "BCP-002",
            "name": "Facilities Emergency Response Plan",
            "description": "Business continuity for physical facilities",
            "version": "1.3",
            "status": "active",
            "scope": "All office locations and facilities",
            "business_units": ["Facilities", "HR", "Security"],
            "geographic_scope": ["HQ Building", "Branch Offices"],
            "objectives": "Maintain operations during facility disruptions",
            "next_review_date": "2024-11-30T00:00:00Z",
            "created_at": "2024-02-10T10:30:00Z",
            "created_by": "jane.smith@company.com"
        }
    ]
    
    # Apply filters
    if status:
        plans = [p for p in plans if p["status"] == status]
    if business_unit:
        plans = [p for p in plans if business_unit in p["business_units"]]
    
    return {
        "plans": plans[skip:skip+limit],
        "total": len(plans),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/continuity/plans")
async def create_continuity_plan():
    """Create a new business continuity plan"""
    return {
        "id": 3,
        "plan_id": "BCP-003",
        "name": "New Business Continuity Plan",
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "Business continuity plan created successfully"
    }

@app.get("/api/v1/continuity/plans/{plan_id}")
async def get_continuity_plan(plan_id: str):
    """Get detailed continuity plan"""
    return {
        "id": 1,
        "plan_id": plan_id,
        "name": "IT Systems Business Continuity Plan",
        "description": "Comprehensive continuity plan for critical IT systems",
        "version": "2.1",
        "status": "active",
        "scope": "All IT infrastructure and applications",
        "business_units": ["IT", "Operations", "Customer Service"],
        "geographic_scope": ["Primary Data Center", "DR Site"],
        "objectives": "Ensure 99.9% uptime for critical systems",
        "assumptions": "Power and network connectivity available at DR site",
        "dependencies": {
            "systems": ["ERP", "CRM", "Email"],
            "suppliers": ["Cloud Provider", "ISP"],
            "personnel": ["IT Staff", "Operations Team"]
        },
        "approved_by": "cto@company.com",
        "approved_date": "2024-03-01T00:00:00Z",
        "next_review_date": "2024-12-15T00:00:00Z",
        "review_frequency_months": 12,
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-03-01T10:15:00Z",
        "created_by": "john.doe@company.com",
        "updated_by": "cto@company.com"
    }

@app.put("/api/v1/continuity/plans/{plan_id}")
async def update_continuity_plan(plan_id: str):
    """Update continuity plan"""
    return {
        "plan_id": plan_id,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "message": "Business continuity plan updated successfully"
    }

# Business Impact Analysis
@app.get("/api/v1/continuity/plans/{plan_id}/business-impact")
async def get_business_impact_analyses(plan_id: str):
    """Get business impact analyses for a plan"""
    return {
        "analyses": [
            {
                "id": 1,
                "analysis_id": "BIA-001",
                "business_process": "Customer Order Processing",
                "process_owner": "operations.manager@company.com",
                "department": "Operations",
                "impact_level": "severe",
                "rto_hours": 2.0,
                "rpo_hours": 0.5,
                "financial_impact_hourly": 50000.0,
                "financial_impact_daily": 1200000.0,
                "minimum_service_level": 25.0,
                "critical_dependencies": {
                    "systems": ["ERP", "Payment Gateway"],
                    "personnel": ["Order Processing Team"],
                    "facilities": ["Primary Data Center"]
                },
                "peak_periods": ["Black Friday", "Holiday Season"],
                "created_at": "2024-01-20T10:00:00Z"
            },
            {
                "id": 2,
                "analysis_id": "BIA-002",
                "business_process": "Customer Support Services",
                "process_owner": "support.manager@company.com",
                "department": "Customer Service",
                "impact_level": "significant",
                "rto_hours": 4.0,
                "rpo_hours": 1.0,
                "financial_impact_hourly": 15000.0,
                "financial_impact_daily": 360000.0,
                "minimum_service_level": 50.0,
                "critical_dependencies": {
                    "systems": ["CRM", "Phone System"],
                    "personnel": ["Support Team"],
                    "facilities": ["Call Center"]
                },
                "peak_periods": ["Monday Mornings", "Product Launches"],
                "created_at": "2024-01-22T14:30:00Z"
            }
        ],
        "total": 2
    }

@app.post("/api/v1/continuity/plans/{plan_id}/business-impact")
async def create_business_impact_analysis(plan_id: str):
    """Create business impact analysis"""
    return {
        "id": 3,
        "analysis_id": "BIA-003",
        "business_process": "New Business Process",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "Business impact analysis created successfully"
    }

# Disaster Recovery Procedures
@app.get("/api/v1/continuity/plans/{plan_id}/procedures")
async def get_recovery_procedures(plan_id: str, priority: str = None, category: str = None):
    """Get disaster recovery procedures for a plan"""
    procedures = [
        {
            "id": 1,
            "procedure_id": "DRP-001",
            "name": "Database Server Recovery",
            "description": "Restore primary database server operations",
            "category": "IT Systems",
            "priority": "critical",
            "target_rto_hours": 1.0,
            "target_rpo_hours": 0.25,
            "estimated_recovery_time": 0.8,
            "automated": True,
            "last_tested": "2024-07-15T10:00:00Z",
            "test_success_rate": 95.0,
            "recovery_steps": [
                {"step_number": 1, "description": "Assess database server status", "estimated_duration_minutes": 10},
                {"step_number": 2, "description": "Initiate failover to backup server", "estimated_duration_minutes": 15},
                {"step_number": 3, "description": "Verify data integrity", "estimated_duration_minutes": 20},
                {"step_number": 4, "description": "Update DNS records", "estimated_duration_minutes": 5}
            ],
            "required_personnel": ["Database Administrator", "Network Engineer"],
            "created_at": "2024-01-25T09:00:00Z"
        },
        {
            "id": 2,
            "procedure_id": "DRP-002",
            "name": "Web Application Recovery",
            "description": "Restore web application services",
            "category": "IT Systems",
            "priority": "high",
            "target_rto_hours": 2.0,
            "target_rpo_hours": 0.5,
            "estimated_recovery_time": 1.5,
            "automated": False,
            "last_tested": "2024-06-20T14:00:00Z",
            "test_success_rate": 88.0,
            "recovery_steps": [
                {"step_number": 1, "description": "Check application server status", "estimated_duration_minutes": 15},
                {"step_number": 2, "description": "Deploy from backup images", "estimated_duration_minutes": 45},
                {"step_number": 3, "description": "Restore application configuration", "estimated_duration_minutes": 30},
                {"step_number": 4, "description": "Perform functional testing", "estimated_duration_minutes": 30}
            ],
            "required_personnel": ["Application Administrator", "DevOps Engineer"],
            "created_at": "2024-01-28T11:15:00Z"
        }
    ]
    
    # Apply filters
    if priority:
        procedures = [p for p in procedures if p["priority"] == priority]
    if category:
        procedures = [p for p in procedures if p["category"] == category]
    
    return {
        "procedures": procedures,
        "total": len(procedures)
    }

@app.post("/api/v1/continuity/plans/{plan_id}/procedures")
async def create_recovery_procedure(plan_id: str):
    """Create disaster recovery procedure"""
    return {
        "id": 3,
        "procedure_id": "DRP-003",
        "name": "New Recovery Procedure",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "Recovery procedure created successfully"
    }

@app.get("/api/v1/continuity/procedures/{procedure_id}")
async def get_recovery_procedure(procedure_id: str):
    """Get detailed recovery procedure"""
    return {
        "id": 1,
        "procedure_id": procedure_id,
        "name": "Database Server Recovery",
        "description": "Restore primary database server operations",
        "category": "IT Systems",
        "priority": "critical",
        "target_rto_hours": 1.0,
        "target_rpo_hours": 0.25,
        "estimated_recovery_time": 0.8,
        "preparation_steps": [
            {
                "step_number": 1,
                "description": "Verify backup systems are operational",
                "responsible_role": "Database Administrator",
                "automated": True,
                "validation_criteria": "Backup system health check passes"
            }
        ],
        "activation_triggers": [
            "Primary database server failure",
            "Data center power outage affecting database tier",
            "Network connectivity loss to database server"
        ],
        "recovery_steps": [
            {
                "step_number": 1,
                "description": "Assess database server status",
                "estimated_duration_minutes": 10,
                "responsible_role": "Database Administrator",
                "automated": False,
                "validation_criteria": "Server status confirmed as down"
            },
            {
                "step_number": 2,
                "description": "Initiate failover to backup server",
                "estimated_duration_minutes": 15,
                "responsible_role": "Database Administrator",
                "automated": True,
                "script_path": "/scripts/db_failover.sh",
                "validation_criteria": "Backup server accepting connections"
            }
        ],
        "validation_steps": [
            {
                "step_number": 1,
                "description": "Verify database connectivity",
                "estimated_duration_minutes": 5,
                "validation_criteria": "Application can connect to database"
            }
        ],
        "required_personnel": ["Database Administrator", "Network Engineer"],
        "required_equipment": ["Backup Database Server", "Network Monitoring Tools"],
        "required_facilities": ["Secondary Data Center"],
        "estimated_cost": 5000.0,
        "automated": True,
        "automation_script": "/scripts/db_recovery_automation.sh",
        "manual_intervention_required": True,
        "test_frequency_months": 3,
        "last_tested": "2024-07-15T10:00:00Z",
        "test_success_rate": 95.0,
        "created_at": "2024-01-25T09:00:00Z",
        "updated_at": "2024-07-15T11:30:00Z"
    }

# Continuity Testing
@app.get("/api/v1/continuity/tests")
async def get_continuity_tests(
    status: str = None,
    test_type: str = None,
    plan_id: str = None,
    skip: int = 0,
    limit: int = 50
):
    """Get continuity tests with filtering"""
    tests = [
        {
            "id": 1,
            "test_id": "CT-001",
            "name": "Q3 2024 Database Recovery Test",
            "description": "Comprehensive test of database recovery procedures",
            "test_type": "Full Test",
            "continuity_plan_id": 1,
            "status": "completed",
            "scheduled_date": "2024-07-15T10:00:00Z",
            "actual_start_time": "2024-07-15T10:05:00Z",
            "actual_end_time": "2024-07-15T11:30:00Z",
            "test_coordinator": "test.coordinator@company.com",
            "overall_success": True,
            "rto_achieved": 0.8,
            "rpo_achieved": 0.2,
            "participants": ["Database Administrator", "Network Engineer", "Operations Manager"],
            "scenarios_tested": 3,
            "scenarios_passed": 3,
            "created_at": "2024-06-15T14:00:00Z"
        },
        {
            "id": 2,
            "test_id": "CT-002",
            "name": "Facilities Evacuation Tabletop",
            "description": "Tabletop exercise for facility emergency procedures",
            "test_type": "Tabletop",
            "continuity_plan_id": 2,
            "status": "completed",
            "scheduled_date": "2024-06-20T14:00:00Z",
            "actual_start_time": "2024-06-20T14:10:00Z",
            "actual_end_time": "2024-06-20T16:00:00Z",
            "test_coordinator": "facilities.manager@company.com",
            "overall_success": True,
            "rto_achieved": None,  # Not applicable for tabletop
            "rpo_achieved": None,
            "participants": ["Facilities Manager", "HR Director", "Security Chief", "Floor Wardens"],
            "scenarios_tested": 2,
            "scenarios_passed": 2,
            "created_at": "2024-05-20T10:30:00Z"
        }
    ]
    
    # Apply filters
    if status:
        tests = [t for t in tests if t["status"] == status]
    if test_type:
        tests = [t for t in tests if t["test_type"] == test_type]
    if plan_id:
        tests = [t for t in tests if str(t["continuity_plan_id"]) == plan_id]
    
    return {
        "tests": tests[skip:skip+limit],
        "total": len(tests),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/continuity/tests")
async def schedule_continuity_test():
    """Schedule a new continuity test"""
    return {
        "id": 3,
        "test_id": "CT-003",
        "name": "New Continuity Test",
        "status": "planned",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "Continuity test scheduled successfully"
    }

@app.get("/api/v1/continuity/tests/{test_id}")
async def get_continuity_test(test_id: str):
    """Get detailed continuity test"""
    return {
        "id": 1,
        "test_id": test_id,
        "name": "Q3 2024 Database Recovery Test",
        "description": "Comprehensive test of database recovery procedures",
        "test_type": "Full Test",
        "scope": "Database recovery and application failover",
        "continuity_plan_id": 1,
        "status": "completed",
        "scheduled_date": "2024-07-15T10:00:00Z",
        "actual_start_time": "2024-07-15T10:05:00Z",
        "actual_end_time": "2024-07-15T11:30:00Z",
        "test_coordinator": "test.coordinator@company.com",
        "participants": ["Database Administrator", "Network Engineer", "Operations Manager"],
        "observers": ["CTO", "Compliance Officer"],
        "objectives": [
            {
                "objective": "Verify database failover capability",
                "success_criteria": "Failover completes within RTO",
                "measurement_method": "Automated monitoring"
            },
            {
                "objective": "Test application recovery procedures",
                "success_criteria": "Applications restore functionality",
                "measurement_method": "Functional testing"
            }
        ],
        "scenarios": [
            {
                "name": "Primary Database Failure",
                "description": "Simulate complete failure of primary database",
                "type": "full_test",
                "target_rto_hours": 1.0,
                "target_rpo_hours": 0.25,
                "procedures_to_test": ["DRP-001"],
                "result": {
                    "success": True,
                    "rto_achieved": 0.8,
                    "rpo_achieved": 0.2,
                    "issues": []
                }
            }
        ],
        "overall_success": True,
        "rto_achieved": 0.8,
        "rpo_achieved": 0.2,
        "issues_identified": [],
        "recommendations": [
            "Consider automating DNS update process",
            "Review backup verification procedures"
        ],
        "test_report": "Test completed successfully with all objectives met. Database failover performed within target RTO.",
        "lessons_learned": "Automated failover scripts performed well. Manual verification steps could be streamlined.",
        "action_items": [
            {
                "item": "Automate DNS update process",
                "assigned_to": "Network Engineer",
                "due_date": "2024-08-15T00:00:00Z",
                "priority": "medium"
            }
        ],
        "created_at": "2024-06-15T14:00:00Z",
        "updated_at": "2024-07-15T12:00:00Z"
    }

@app.post("/api/v1/continuity/tests/{test_id}/execute")
async def execute_continuity_test(test_id: str):
    """Execute a scheduled continuity test"""
    return {
        "test_id": test_id,
        "execution_started": datetime.utcnow().isoformat() + "Z",
        "status": "in_progress",
        "message": "Test execution initiated successfully"
    }

# Plan Activation
@app.get("/api/v1/continuity/activations")
async def get_plan_activations(active_only: bool = True, skip: int = 0, limit: int = 50):
    """Get plan activations"""
    activations = [
        {
            "id": 1,
            "activation_id": "PA-001",
            "continuity_plan_id": 1,
            "trigger_event": "Primary data center power outage",
            "activation_level": "partial_activation",
            "activated_by": "operations.manager@company.com",
            "activation_reason": "Extended power outage affecting critical systems",
            "activation_time": "2024-07-20T14:30:00Z",
            "expected_duration": 8.0,
            "affected_business_units": ["IT", "Operations", "Customer Service"],
            "current_status": "In Progress",
            "completion_percentage": 65.0,
            "deactivation_time": None,
            "created_at": "2024-07-20T14:30:00Z"
        }
    ]
    
    if active_only:
        activations = [a for a in activations if a["deactivation_time"] is None]
    
    return {
        "activations": activations[skip:skip+limit],
        "total": len(activations),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/continuity/plans/{plan_id}/activate")
async def activate_continuity_plan(plan_id: str):
    """Activate a business continuity plan"""
    return {
        "activation_id": "PA-002",
        "plan_id": plan_id,
        "activation_time": datetime.utcnow().isoformat() + "Z",
        "status": "activated",
        "message": "Business continuity plan activated successfully"
    }

@app.get("/api/v1/continuity/activations/{activation_id}")
async def get_plan_activation(activation_id: str):
    """Get detailed plan activation"""
    return {
        "id": 1,
        "activation_id": activation_id,
        "continuity_plan_id": 1,
        "trigger_event": "Primary data center power outage",
        "activation_level": "partial_activation",
        "activated_by": "operations.manager@company.com",
        "activation_reason": "Extended power outage affecting critical systems",
        "activation_time": "2024-07-20T14:30:00Z",
        "expected_duration": 8.0,
        "affected_business_units": ["IT", "Operations", "Customer Service"],
        "activated_procedures": ["DRP-001", "DRP-002"],
        "personnel_notified": [
            "Database Administrator",
            "Network Engineer", 
            "Operations Manager",
            "Customer Service Manager"
        ],
        "current_status": "In Progress",
        "completion_percentage": 65.0,
        "stakeholder_notifications": [
            {
                "type": "email",
                "recipients": ["management@company.com"],
                "sent_at": "2024-07-20T14:35:00Z",
                "subject": "Business Continuity Plan Activated"
            }
        ],
        "communication_log": [
            {
                "timestamp": "2024-07-20T14:30:00Z",
                "type": "activation",
                "message": "Plan activated due to power outage",
                "user": "operations.manager@company.com"
            },
            {
                "timestamp": "2024-07-20T15:15:00Z",
                "type": "update", 
                "message": "Database failover completed successfully",
                "user": "database.admin@company.com"
            }
        ],
        "success_metrics": {
            "procedures_executed": 2,
            "procedures_successful": 2,
            "systems_recovered": ["Database", "Web Application"],
            "users_affected": 1200,
            "service_downtime_minutes": 45
        },
        "actual_rto": 0.75,
        "actual_rpo": 0.1,
        "lessons_learned": "Response was effective. Consider automating notification process.",
        "deactivated_by": None,
        "deactivation_time": None,
        "deactivation_reason": None,
        "created_at": "2024-07-20T14:30:00Z",
        "updated_at": "2024-07-20T18:45:00Z"
    }

@app.put("/api/v1/continuity/activations/{activation_id}/deactivate")
async def deactivate_plan(activation_id: str):
    """Deactivate a business continuity plan"""
    return {
        "activation_id": activation_id,
        "deactivation_time": datetime.utcnow().isoformat() + "Z",
        "status": "deactivated",
        "message": "Business continuity plan deactivated successfully"
    }

# Procedure Execution
@app.get("/api/v1/continuity/executions")
async def get_procedure_executions(
    procedure_id: int = None,
    activation_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 50
):
    """Get procedure executions"""
    executions = [
        {
            "id": 1,
            "execution_id": "PE-001",
            "procedure_id": 1,
            "activation_id": 1,
            "executed_by": "database.admin@company.com",
            "execution_context": "Actual Incident",
            "start_time": "2024-07-20T15:00:00Z",
            "end_time": "2024-07-20T15:45:00Z",
            "duration_minutes": 45.0,
            "status": "Completed",
            "successful": True,
            "rto_met": True,
            "rpo_met": True,
            "actual_recovery_time": 0.75,
            "actual_data_loss": 0.1,
            "created_at": "2024-07-20T15:00:00Z"
        }
    ]
    
    # Apply filters
    if procedure_id:
        executions = [e for e in executions if e["procedure_id"] == procedure_id]
    if activation_id:
        executions = [e for e in executions if e["activation_id"] == activation_id]
    if status:
        executions = [e for e in executions if e["status"] == status]
    
    return {
        "executions": executions[skip:skip+limit],
        "total": len(executions),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/continuity/procedures/{procedure_id}/execute")
async def execute_recovery_procedure(procedure_id: str):
    """Execute a disaster recovery procedure"""
    return {
        "execution_id": "PE-002",
        "procedure_id": procedure_id,
        "start_time": datetime.utcnow().isoformat() + "Z",
        "status": "Started",
        "message": "Recovery procedure execution initiated"
    }

@app.get("/api/v1/continuity/executions/{execution_id}")
async def get_procedure_execution(execution_id: str):
    """Get detailed procedure execution"""
    return {
        "id": 1,
        "execution_id": execution_id,
        "procedure_id": 1,
        "activation_id": 1,
        "executed_by": "database.admin@company.com",
        "execution_context": "Actual Incident",
        "start_time": "2024-07-20T15:00:00Z",
        "end_time": "2024-07-20T15:45:00Z",
        "duration_minutes": 45.0,
        "status": "Completed",
        "completion_percentage": 100.0,
        "successful": True,
        "rto_met": True,
        "rpo_met": True,
        "issues_encountered": [],
        "deviations_from_plan": None,
        "execution_log": [
            {
                "step_number": 1,
                "step_type": "recovery",
                "description": "Assess database server status",
                "start_time": "2024-07-20T15:00:00Z",
                "end_time": "2024-07-20T15:10:00Z",
                "success": True
            },
            {
                "step_number": 2,
                "step_type": "recovery",
                "description": "Initiate failover to backup server",
                "start_time": "2024-07-20T15:10:00Z",
                "end_time": "2024-07-20T15:25:00Z",
                "success": True
            }
        ],
        "notes": "Execution proceeded smoothly with all steps completed successfully",
        "evidence_collected": [
            {
                "type": "screenshot",
                "description": "Database failover confirmation",
                "timestamp": "2024-07-20T15:25:00Z"
            }
        ],
        "actual_recovery_time": 0.75,
        "actual_data_loss": 0.1,
        "resource_utilization": {
            "cpu": "65%",
            "memory": "78%",
            "network": "45%"
        },
        "created_at": "2024-07-20T15:00:00Z",
        "updated_at": "2024-07-20T15:45:00Z"
    }

# Metrics and Analytics
@app.get("/api/v1/continuity/metrics")
async def get_continuity_metrics():
    """Get continuity metrics and KPIs"""
    return {
        "rto_metrics": {
            "average_rto_hours": 1.2,
            "target_rto_hours": 2.0,
            "rto_compliance_rate": 95.5,
            "procedures_meeting_rto": 18,
            "total_procedures": 20
        },
        "rpo_metrics": {
            "average_rpo_hours": 0.3,
            "target_rpo_hours": 0.5,
            "rpo_compliance_rate": 98.2,
            "procedures_meeting_rpo": 19,
            "total_procedures": 20
        },
        "test_metrics": {
            "tests_completed_this_quarter": 8,
            "test_success_rate": 87.5,
            "overdue_tests": 2,
            "scheduled_tests_next_month": 4
        },
        "plan_metrics": {
            "active_plans": 3,
            "plans_needing_review": 1,
            "plans_activated_this_year": 2,
            "average_activation_response_time": 15.5
        }
    }

@app.get("/api/v1/continuity/dashboard")
async def get_continuity_dashboard():
    """Get comprehensive continuity management dashboard"""
    return {
        "summary": {
            "total_plans": 3,
            "active_plans": 3,
            "total_procedures": 20,
            "recent_tests": 8,
            "active_activations": 0,
            "overdue_reviews": 1
        },
        "active_plans": [
            {
                "plan_id": "BCP-001",
                "name": "IT Systems Business Continuity Plan",
                "business_units": ["IT", "Operations"],
                "last_tested": "2024-07-15T10:00:00Z",
                "next_review": "2024-12-15T00:00:00Z"
            },
            {
                "plan_id": "BCP-002", 
                "name": "Facilities Emergency Response Plan",
                "business_units": ["Facilities", "HR"],
                "last_tested": "2024-06-20T14:00:00Z",
                "next_review": "2024-11-30T00:00:00Z"
            }
        ],
        "recent_tests": [
            {
                "test_id": "CT-001",
                "name": "Q3 2024 Database Recovery Test",
                "test_type": "Full Test",
                "date": "2024-07-15T10:00:00Z",
                "success": True,
                "rto_achieved": 0.8
            },
            {
                "test_id": "CT-002",
                "name": "Facilities Evacuation Tabletop",
                "test_type": "Tabletop",
                "date": "2024-06-20T14:00:00Z",
                "success": True,
                "rto_achieved": None
            }
        ],
        "active_activations": [],
        "metrics": {
            "plans_tracked": 3,
            "average_rto": 1.2,
            "average_rpo": 0.3,
            "compliance_rate": 95.5,
            "critical_issues": []
        },
        "upcoming_tests": [
            {
                "test_id": "CT-003",
                "name": "Q4 Application Recovery Test",
                "scheduled_date": "2024-10-15T10:00:00Z",
                "test_type": "Simulation"
            }
        ],
        "overdue_reviews": [
            {
                "plan_id": "BCP-003",
                "name": "Legacy Systems Continuity Plan",
                "review_due_date": "2024-06-30T00:00:00Z",
                "days_overdue": 45
            }
        ]
    }

# Resources Management
@app.get("/api/v1/continuity/resources")
async def get_continuity_resources(
    resource_type: str = None,
    available: bool = None,
    skip: int = 0,
    limit: int = 50
):
    """Get continuity resources"""
    resources = [
        {
            "id": 1,
            "resource_id": "CR-001",
            "name": "Backup Data Center",
            "resource_type": "Facility",
            "category": "Infrastructure",
            "description": "Secondary data center for disaster recovery",
            "available": True,
            "capacity": 100.0,
            "current_utilization": 25.0,
            "location": "West Coast Facility",
            "criticality_level": "Critical",
            "created_at": "2024-01-10T09:00:00Z"
        },
        {
            "id": 2,
            "resource_id": "CR-002",
            "name": "Emergency Communication System",
            "resource_type": "Equipment",
            "category": "Communication",
            "description": "Satellite communication system for emergencies",
            "available": True,
            "capacity": 50.0,
            "current_utilization": 0.0,
            "location": "Mobile Unit",
            "criticality_level": "Important",
            "created_at": "2024-01-15T11:30:00Z"
        }
    ]
    
    # Apply filters
    if resource_type:
        resources = [r for r in resources if r["resource_type"] == resource_type]
    if available is not None:
        resources = [r for r in resources if r["available"] == available]
    
    return {
        "resources": resources[skip:skip+limit],
        "total": len(resources),
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/continuity/resources")
async def create_continuity_resource():
    """Create a new continuity resource"""
    return {
        "id": 3,
        "resource_id": "CR-003",
        "name": "New Continuity Resource",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "Continuity resource created successfully"
    }

@app.get("/api/v1/continuity/resources/{resource_id}")
async def get_continuity_resource(resource_id: str):
    """Get detailed continuity resource"""
    return {
        "id": 1,
        "resource_id": resource_id,
        "name": "Backup Data Center",
        "resource_type": "Facility",
        "category": "Infrastructure",
        "description": "Secondary data center for disaster recovery operations",
        "available": True,
        "capacity": 100.0,
        "current_utilization": 25.0,
        "location": "West Coast Facility - 123 Business Park Dr",
        "contact_information": {
            "facility_manager": "facility.manager@company.com",
            "phone": "+1-555-0123",
            "emergency_contact": "+1-555-0199"
        },
        "specifications": {
            "power_capacity": "2MW",
            "cooling_capacity": "500 tons",
            "floor_space": "10,000 sq ft",
            "network_bandwidth": "10 Gbps"
        },
        "capabilities": [
            "Full server hosting",
            "Network equipment hosting",
            "24/7 monitoring",
            "Environmental controls"
        ],
        "limitations": [
            "Limited parking",
            "No helicopter landing pad",
            "Single fiber connection"
        ],
        "maintenance_schedule": [
            {
                "type": "HVAC maintenance",
                "frequency": "Monthly",
                "next_date": "2024-09-15T10:00:00Z"
            }
        ],
        "last_maintenance": "2024-08-15T10:00:00Z",
        "next_maintenance": "2024-09-15T10:00:00Z",
        "replacement_date": "2030-12-31T00:00:00Z",
        "acquisition_cost": 5000000.0,
        "maintenance_cost_annual": 500000.0,
        "replacement_cost": 8000000.0,
        "criticality_level": "Critical",
        "dependencies": [
            "Power grid connection",
            "Internet service provider",
            "Physical security system"
        ],
        "dependents": [
            "Primary business applications",
            "Customer-facing services",
            "Internal IT systems"
        ],
        "backup_resources": ["CR-004", "CR-005"],
        "alternative_sources": ["Cloud provider resources", "Partner facility agreements"],
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-08-15T11:00:00Z"
    }

# ====================================
# THIRD-PARTY RISK MANAGEMENT ENDPOINTS
# ====================================

@app.get("/api/v1/vendors")
async def get_vendors(
    tier: str = None,
    status: str = None,
    risk_level: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all vendors with optional filtering"""
    return {
        "vendors": [
            {
                "id": 1,
                "vendor_id": "VEN-A1B2C3D4",
                "name": "CloudTech Solutions",
                "legal_name": "CloudTech Solutions Inc.",
                "vendor_type": "software",
                "tier": "critical",
                "status": "active",
                "criticality": "high",
                "industry": "Cloud Services",
                "services_provided": ["Cloud Infrastructure", "Data Storage", "API Services"],
                "contract_value_annual": 500000.0,
                "overall_risk_score": 75.2,
                "last_risk_assessment": "2024-07-15T10:00:00Z",
                "next_assessment_due": "2025-01-15T10:00:00Z",
                "relationship_manager": "John Smith",
                "contract_end_date": "2025-12-31T23:59:59Z",
                "created_at": "2023-01-15T09:00:00Z",
                "updated_at": "2024-08-01T14:30:00Z"
            },
            {
                "id": 2,
                "vendor_id": "VEN-E5F6G7H8",
                "name": "SecureAuth Systems",
                "legal_name": "SecureAuth Systems Ltd",
                "vendor_type": "security",
                "tier": "high",
                "status": "active",
                "criticality": "medium",
                "industry": "Cybersecurity",
                "services_provided": ["Identity Management", "Multi-Factor Authentication"],
                "contract_value_annual": 120000.0,
                "overall_risk_score": 85.6,
                "last_risk_assessment": "2024-06-20T10:00:00Z",
                "next_assessment_due": "2024-12-20T10:00:00Z",
                "relationship_manager": "Sarah Johnson",
                "contract_end_date": "2025-06-30T23:59:59Z",
                "created_at": "2023-03-10T11:00:00Z",
                "updated_at": "2024-07-25T16:15:00Z"
            },
            {
                "id": 3,
                "vendor_id": "VEN-I9J0K1L2",
                "name": "DataProcess Corp",
                "legal_name": "DataProcess Corporation",
                "vendor_type": "service",
                "tier": "medium",
                "status": "active",
                "criticality": "low",
                "industry": "Data Processing",
                "services_provided": ["Data Analytics", "Reporting Services"],
                "contract_value_annual": 75000.0,
                "overall_risk_score": 68.3,
                "last_risk_assessment": "2024-05-10T10:00:00Z",
                "next_assessment_due": "2024-11-10T10:00:00Z",
                "relationship_manager": "Mike Davis",
                "contract_end_date": "2024-12-31T23:59:59Z",
                "created_at": "2023-05-20T13:00:00Z",
                "updated_at": "2024-08-10T10:45:00Z"
            }
        ],
        "total": 3,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/vendors")
async def create_vendor(vendor_data: dict):
    """Create a new vendor"""
    return {
        "id": 4,
        "vendor_id": "VEN-M3N4O5P6",
        "name": vendor_data.get("name"),
        "status": "prospect",
        "tier": vendor_data.get("tier", "low"),
        "overall_risk_score": 0.0,
        "created_at": "2024-08-15T12:00:00Z",
        "message": "Vendor created successfully"
    }

@app.get("/api/v1/vendors/{vendor_id}")
async def get_vendor(vendor_id: str):
    """Get detailed vendor information"""
    return {
        "id": 1,
        "vendor_id": vendor_id,
        "name": "CloudTech Solutions",
        "legal_name": "CloudTech Solutions Inc.",
        "business_name": "CloudTech",
        "vendor_type": "software",
        "primary_contact_name": "Alex Rodriguez",
        "primary_contact_email": "alex.rodriguez@cloudtech.com",
        "primary_contact_phone": "+1-555-0123",
        "website": "https://www.cloudtech.com",
        "industry": "Cloud Services",
        "business_model": "SaaS",
        "number_of_employees": 1250,
        "annual_revenue": 50000000.0,
        "founding_year": 2015,
        "headquarters_address": {
            "street": "123 Tech Boulevard",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94105"
        },
        "tier": "critical",
        "status": "active",
        "criticality": "high",
        "services_provided": ["Cloud Infrastructure", "Data Storage", "API Services", "CDN"],
        "service_categories": ["Infrastructure", "Platform", "Storage"],
        "data_types_accessed": ["Customer Data", "Financial Records", "System Logs"],
        "systems_accessed": ["Production Database", "API Gateway", "Monitoring Systems"],
        "contract_value_annual": 500000.0,
        "contract_value_total": 1500000.0,
        "payment_terms": "Net 30",
        "overall_risk_score": 75.2,
        "last_risk_assessment": "2024-07-15T10:00:00Z",
        "next_assessment_due": "2025-01-15T10:00:00Z",
        "certifications": [
            {"name": "ISO 27001", "valid_until": "2025-06-30T23:59:59Z"},
            {"name": "SOC 2 Type II", "valid_until": "2025-03-31T23:59:59Z"}
        ],
        "compliance_frameworks": ["GDPR", "SOX", "HIPAA"],
        "security_attestations": [
            {"type": "Penetration Test", "date": "2024-05-15T10:00:00Z", "result": "Passed"}
        ],
        "relationship_manager": "John Smith",
        "vendor_account_manager": "Lisa Chen",
        "escalation_contacts": [
            {"name": "Mike Johnson", "role": "VP Engineering", "email": "mike.j@cloudtech.com", "phone": "+1-555-0124"}
        ],
        "onboarding_date": "2023-01-15T09:00:00Z",
        "contract_start_date": "2023-02-01T00:00:00Z",
        "contract_end_date": "2025-12-31T23:59:59Z",
        "termination_notice_period": 90,
        "tags": ["critical-vendor", "cloud-provider", "high-volume"],
        "created_at": "2023-01-15T09:00:00Z",
        "updated_at": "2024-08-01T14:30:00Z"
    }

@app.put("/api/v1/vendors/{vendor_id}")
async def update_vendor(vendor_id: str, vendor_data: dict):
    """Update vendor information"""
    return {
        "vendor_id": vendor_id,
        "message": "Vendor updated successfully",
        "updated_fields": list(vendor_data.keys()),
        "updated_at": "2024-08-15T12:30:00Z"
    }

@app.get("/api/v1/vendors/{vendor_id}/assessments")
async def get_vendor_assessments(vendor_id: str):
    """Get all risk assessments for a vendor"""
    return {
        "vendor_id": vendor_id,
        "assessments": [
            {
                "id": 1,
                "assessment_id": "VRA-A1B2C3D4",
                "assessment_name": "Annual Risk Assessment 2024",
                "assessment_type": "annual",
                "status": "completed",
                "assessment_start_date": "2024-07-01T09:00:00Z",
                "assessment_end_date": "2024-07-15T17:00:00Z",
                "overall_risk_score": 75.2,
                "overall_risk_level": "medium",
                "category_scores": {
                    "information_security": 78.5,
                    "data_protection": 82.1,
                    "operational": 71.3,
                    "financial": 79.8,
                    "compliance": 85.2,
                    "business_continuity": 68.9
                },
                "assessor": "Jane Wilson",
                "next_assessment_due": "2025-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "assessment_id": "VRA-E5F6G7H8",
                "assessment_name": "Triggered Assessment - Security Incident",
                "assessment_type": "triggered",
                "status": "in_progress",
                "assessment_start_date": "2024-08-01T10:00:00Z",
                "progress_percentage": 65.0,
                "assessor": "Security Team",
                "created_at": "2024-08-01T10:00:00Z"
            }
        ],
        "total": 2
    }

@app.post("/api/v1/vendors/{vendor_id}/assessments")
async def create_vendor_assessment(vendor_id: str, assessment_data: dict):
    """Create a new vendor risk assessment"""
    return {
        "id": 3,
        "assessment_id": "VRA-I9J0K1L2",
        "vendor_id": vendor_id,
        "assessment_name": assessment_data.get("assessment_name"),
        "assessment_type": assessment_data.get("assessment_type", "periodic"),
        "status": "not_started",
        "assessment_start_date": "2024-08-15T09:00:00Z",
        "due_date": assessment_data.get("due_date"),
        "created_at": "2024-08-15T12:00:00Z",
        "message": "Assessment created successfully"
    }

@app.get("/api/v1/assessments/{assessment_id}")
async def get_assessment_details(assessment_id: str):
    """Get detailed assessment information"""
    return {
        "id": 1,
        "assessment_id": assessment_id,
        "vendor_id": 1,
        "vendor_name": "CloudTech Solutions",
        "assessment_name": "Annual Risk Assessment 2024",
        "assessment_type": "annual",
        "assessment_methodology": "questionnaire",
        "scope_description": "Comprehensive security, operational, and compliance assessment",
        "status": "completed",
        "progress_percentage": 100.0,
        "assessment_start_date": "2024-07-01T09:00:00Z",
        "assessment_end_date": "2024-07-15T17:00:00Z",
        "due_date": "2024-07-31T23:59:59Z",
        "overall_risk_score": 75.2,
        "overall_risk_level": "medium",
        "previous_risk_score": 72.8,
        "risk_trend": "improving",
        "category_scores": {
            "information_security": 78.5,
            "data_protection": 82.1,
            "operational": 71.3,
            "financial": 79.8,
            "compliance": 85.2,
            "business_continuity": 68.9,
            "reputational": 74.6
        },
        "strengths": [
            "Strong ISO 27001 implementation",
            "Excellent incident response procedures",
            "Regular security training program"
        ],
        "weaknesses": [
            "Limited disaster recovery testing",
            "Inconsistent change management processes",
            "Gaps in third-party vendor management"
        ],
        "gaps": [
            "Missing backup site validation",
            "Incomplete business continuity documentation"
        ],
        "recommendations": [
            "Implement quarterly DR testing",
            "Enhance change management automation",
            "Establish vendor risk assessment program"
        ],
        "questionnaire_responses": {
            "sec_001": true,
            "sec_002": false,
            "dp_001": true,
            "fin_001": "A-"
        },
        "site_visit_conducted": true,
        "site_visit_findings": [
            "Physical security controls adequate",
            "Environmental controls properly maintained"
        ],
        "reviewed_by": "Jane Wilson",
        "review_date": "2024-07-16T10:00:00Z",
        "approved_by": "David Lee",
        "approval_date": "2024-07-17T14:00:00Z",
        "next_assessment_due": "2025-01-15T10:00:00Z",
        "created_at": "2024-07-01T09:00:00Z",
        "updated_at": "2024-07-17T14:00:00Z"
    }

@app.put("/api/v1/assessments/{assessment_id}")
async def update_assessment(assessment_id: str, assessment_data: dict):
    """Update assessment information"""
    return {
        "assessment_id": assessment_id,
        "message": "Assessment updated successfully",
        "updated_fields": list(assessment_data.keys()),
        "updated_at": "2024-08-15T12:30:00Z"
    }

@app.get("/api/v1/vendors/{vendor_id}/contracts")
async def get_vendor_contracts(vendor_id: str):
    """Get all contracts for a vendor"""
    return {
        "vendor_id": vendor_id,
        "contracts": [
            {
                "id": 1,
                "contract_id": "VCT-A1B2C3D4",
                "contract_name": "Master Service Agreement",
                "contract_type": "MSA",
                "contract_number": "MSA-2023-001",
                "status": "active",
                "effective_date": "2023-02-01T00:00:00Z",
                "expiration_date": "2025-12-31T23:59:59Z",
                "auto_renewal": true,
                "renewal_notice_days": 90,
                "contract_value": 1500000.0,
                "currency": "USD",
                "payment_terms": "Net 30",
                "contract_owner": "Legal Team",
                "business_owner": "IT Director",
                "renewal_alerts_sent": 0,
                "created_at": "2023-01-20T10:00:00Z"
            },
            {
                "id": 2,
                "contract_id": "VCT-E5F6G7H8",
                "contract_name": "Data Processing Agreement",
                "contract_type": "DPA",
                "status": "active",
                "effective_date": "2023-02-01T00:00:00Z",
                "expiration_date": "2025-12-31T23:59:59Z",
                "contract_owner": "Privacy Officer",
                "business_owner": "Data Protection Team",
                "created_at": "2023-02-01T09:00:00Z"
            }
        ],
        "total": 2
    }

@app.post("/api/v1/vendors/{vendor_id}/contracts")
async def create_vendor_contract(vendor_id: str, contract_data: dict):
    """Create a new vendor contract"""
    return {
        "id": 3,
        "contract_id": "VCT-I9J0K1L2",
        "vendor_id": vendor_id,
        "contract_name": contract_data.get("contract_name"),
        "contract_type": contract_data.get("contract_type"),
        "status": "draft",
        "effective_date": contract_data.get("effective_date"),
        "expiration_date": contract_data.get("expiration_date"),
        "created_at": "2024-08-15T12:00:00Z",
        "message": "Contract created successfully"
    }

@app.get("/api/v1/contracts/{contract_id}")
async def get_contract_details(contract_id: str):
    """Get detailed contract information"""
    return {
        "id": 1,
        "contract_id": contract_id,
        "vendor_id": 1,
        "vendor_name": "CloudTech Solutions",
        "contract_name": "Master Service Agreement",
        "contract_type": "MSA",
        "contract_number": "MSA-2023-001",
        "status": "active",
        "effective_date": "2023-02-01T00:00:00Z",
        "expiration_date": "2025-12-31T23:59:59Z",
        "auto_renewal": true,
        "renewal_notice_days": 90,
        "termination_notice_days": 30,
        "contract_value": 1500000.0,
        "currency": "USD",
        "payment_terms": "Net 30",
        "payment_schedule": "monthly",
        "service_levels": [
            {"metric": "Uptime", "target": 99.9, "unit": "%"},
            {"metric": "Response Time", "target": 200, "unit": "ms"},
            {"metric": "Support Response", "target": 4, "unit": "hours"}
        ],
        "performance_metrics": [
            {"name": "Availability", "current": 99.95, "target": 99.9, "status": "meeting"},
            {"name": "Performance", "current": 180, "target": 200, "status": "exceeding"}
        ],
        "security_requirements": [
            "ISO 27001 certification maintenance",
            "Annual penetration testing",
            "Quarterly security reviews"
        ],
        "compliance_requirements": [
            "GDPR compliance",
            "SOC 2 Type II certification",
            "Data residency requirements"
        ],
        "liability_cap": 5000000.0,
        "insurance_requirements": [
            {"type": "Professional Liability", "minimum": 2000000.0},
            {"type": "Cyber Liability", "minimum": 1000000.0}
        ],
        "contract_owner": "Legal Team",
        "business_owner": "IT Director",
        "legal_reviewer": "Sarah Martinez",
        "renewal_date": "2025-10-01T00:00:00Z",
        "renewal_status": "pending_review",
        "renewal_alerts_sent": 1,
        "last_alert_date": "2024-07-01T09:00:00Z",
        "created_at": "2023-01-20T10:00:00Z",
        "updated_at": "2024-07-01T09:15:00Z"
    }

@app.get("/api/v1/vendors/{vendor_id}/monitoring")
async def get_vendor_monitoring(vendor_id: str):
    """Get vendor monitoring status and metrics"""
    return {
        "vendor_id": vendor_id,
        "monitoring": {
            "id": 1,
            "monitoring_id": "VMN-A1B2C3D4",
            "monitoring_type": "comprehensive",
            "monitoring_frequency": "continuous",
            "status": "active",
            "automated_monitoring": true,
            "last_check_date": "2024-08-15T12:00:00Z",
            "next_check_date": "2024-08-15T13:00:00Z",
            "security_posture_score": 85.2,
            "service_availability": 99.95,
            "response_time_ms": 180,
            "compliance_status": "compliant",
            "financial_health_score": 82.5,
            "credit_rating": "A-",
            "news_sentiment": 0.3,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-08-15T12:00:00Z"
        },
        "recent_checks": [
            {
                "timestamp": "2024-08-15T12:00:00Z",
                "check_type": "security_scan",
                "status": "passed",
                "score": 85.2
            },
            {
                "timestamp": "2024-08-15T11:00:00Z",
                "check_type": "availability",
                "status": "excellent",
                "uptime": 99.95
            },
            {
                "timestamp": "2024-08-15T10:00:00Z",
                "check_type": "news_sentiment",
                "status": "positive",
                "sentiment": 0.3
            }
        ],
        "active_alerts": []
    }

@app.get("/api/v1/vendors/{vendor_id}/incidents")
async def get_vendor_incidents(vendor_id: str):
    """Get all incidents for a vendor"""
    return {
        "vendor_id": vendor_id,
        "incidents": [
            {
                "id": 1,
                "incident_id": "VIN-A1B2C3D4",
                "title": "Service Outage - API Gateway",
                "description": "Partial outage affecting API gateway services",
                "incident_type": "operational",
                "severity": "high",
                "status": "resolved",
                "business_impact": "medium",
                "affected_services": ["API Gateway", "Authentication Service"],
                "affected_users": 1250,
                "financial_impact": 50000.0,
                "discovered_date": "2024-07-20T14:30:00Z",
                "reported_date": "2024-07-20T14:35:00Z",
                "acknowledged_date": "2024-07-20T14:40:00Z",
                "resolved_date": "2024-07-20T16:15:00Z",
                "root_cause": "Database connection pool exhaustion",
                "resolution_summary": "Increased connection pool size and implemented connection monitoring",
                "incident_manager": "Mike Johnson",
                "priority": "high",
                "vendor_incident_id": "INC-2024-0720-001",
                "created_at": "2024-07-20T14:35:00Z"
            }
        ],
        "total": 1,
        "summary": {
            "open_incidents": 0,
            "resolved_incidents": 1,
            "average_resolution_time_hours": 1.75,
            "incidents_this_month": 1,
            "incidents_this_quarter": 3
        }
    }

@app.post("/api/v1/vendors/{vendor_id}/incidents")
async def create_vendor_incident(vendor_id: str, incident_data: dict):
    """Create a new vendor incident"""
    return {
        "id": 2,
        "incident_id": "VIN-E5F6G7H8",
        "vendor_id": vendor_id,
        "title": incident_data.get("title"),
        "incident_type": incident_data.get("incident_type"),
        "severity": incident_data.get("severity"),
        "status": "open",
        "discovered_date": incident_data.get("discovered_date"),
        "created_at": "2024-08-15T12:00:00Z",
        "message": "Incident created successfully"
    }

@app.get("/api/v1/vendors/{vendor_id}/action-items")
async def get_vendor_action_items(vendor_id: str):
    """Get all action items for a vendor"""
    return {
        "vendor_id": vendor_id,
        "action_items": [
            {
                "id": 1,
                "action_id": "VAC-A1B2C3D4",
                "assessment_id": 1,
                "title": "Implement Quarterly DR Testing",
                "description": "Establish regular disaster recovery testing program",
                "category": "business_continuity",
                "priority": "high",
                "status": "in_progress",
                "progress_percentage": 65.0,
                "assigned_to": "IT Operations Team",
                "vendor_contact": "Alex Rodriguez",
                "due_date": "2024-09-30T23:59:59Z",
                "estimated_effort_hours": 40.0,
                "implementation_plan": "1. Define DR test scenarios 2. Schedule quarterly tests 3. Document procedures",
                "business_justification": "Ensure business continuity and compliance requirements",
                "cost_estimate": 15000.0,
                "created_at": "2024-07-17T15:00:00Z",
                "updated_at": "2024-08-10T10:30:00Z"
            },
            {
                "id": 2,
                "action_id": "VAC-E5F6G7H8",
                "assessment_id": 1,
                "title": "Enhance Change Management Process",
                "description": "Implement automated change management workflows",
                "category": "operational",
                "priority": "medium",
                "status": "open",
                "progress_percentage": 0.0,
                "assigned_to": "DevOps Team",
                "vendor_contact": "Lisa Chen",
                "due_date": "2024-10-31T23:59:59Z",
                "estimated_effort_hours": 60.0,
                "created_at": "2024-07-17T15:00:00Z"
            }
        ],
        "total": 2,
        "summary": {
            "open": 1,
            "in_progress": 1,
            "completed": 0,
            "overdue": 0
        }
    }

@app.get("/api/v1/vendors/{vendor_id}/sla-monitoring")
async def get_vendor_sla_monitoring(vendor_id: str):
    """Get SLA monitoring data for a vendor"""
    return {
        "vendor_id": vendor_id,
        "sla_metrics": [
            {
                "id": 1,
                "sla_id": "SLA-A1B2C3D4",
                "contract_id": 1,
                "sla_name": "Service Availability",
                "metric_name": "uptime_percentage",
                "metric_unit": "%",
                "target_value": 99.9,
                "current_value": 99.95,
                "warning_threshold": 99.5,
                "critical_threshold": 99.0,
                "measurement_period": "monthly",
                "status": "meeting",
                "breach_count": 0,
                "consecutive_breaches": 0,
                "service_credits_earned": 0.0,
                "penalties_applied": 0.0,
                "trend_direction": "stable",
                "last_breach_date": null,
                "reporting_frequency": "monthly",
                "created_at": "2023-02-01T10:00:00Z"
            },
            {
                "id": 2,
                "sla_id": "SLA-E5F6G7H8",
                "contract_id": 1,
                "sla_name": "Response Time",
                "metric_name": "avg_response_time_ms",
                "metric_unit": "ms",
                "target_value": 200.0,
                "current_value": 180.0,
                "warning_threshold": 250.0,
                "critical_threshold": 300.0,
                "measurement_period": "monthly",
                "status": "exceeding",
                "breach_count": 0,
                "consecutive_breaches": 0,
                "trend_direction": "improving",
                "created_at": "2023-02-01T10:00:00Z"
            }
        ],
        "overall_sla_performance": {
            "meeting_slas": 2,
            "breached_slas": 0,
            "at_risk_slas": 0,
            "overall_score": 98.5
        }
    }

@app.get("/api/v1/supply-chain")
async def get_supply_chain_overview():
    """Get supply chain overview and risk analysis"""
    return {
        "supply_chain_nodes": [
            {
                "id": 1,
                "node_id": "SCN-A1B2C3D4",
                "name": "CloudTech Solutions",
                "node_type": "vendor",
                "tier_level": 1,
                "criticality_level": "high",
                "services_provided": ["Cloud Infrastructure", "Data Storage"],
                "dependency_level": "critical",
                "single_point_of_failure": true,
                "replacement_time_days": 90,
                "switching_cost": 250000.0,
                "visibility_level": "full",
                "operational_status": "active",
                "inherent_risk_score": 75.2,
                "residual_risk_score": 65.8,
                "concentration_risk": 35.0,
                "backup_options": ["Alternative Cloud Provider A", "Hybrid Setup"],
                "created_at": "2023-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "node_id": "SCN-E5F6G7H8",
                "name": "SecureAuth Systems",
                "node_type": "vendor",
                "tier_level": 1,
                "criticality_level": "medium",
                "services_provided": ["Identity Management"],
                "dependency_level": "important",
                "single_point_of_failure": false,
                "replacement_time_days": 30,
                "switching_cost": 75000.0,
                "visibility_level": "partial",
                "operational_status": "active",
                "inherent_risk_score": 45.6,
                "residual_risk_score": 38.2,
                "concentration_risk": 15.0,
                "backup_options": ["Internal IAM System", "Alternative Provider"],
                "created_at": "2023-03-10T11:00:00Z"
            }
        ],
        "risk_analysis": {
            "total_nodes": 2,
            "critical_dependencies": 1,
            "single_points_of_failure": 1,
            "average_concentration_risk": 25.0,
            "high_risk_nodes": 1,
            "backup_coverage": 100.0,
            "visibility_gaps": 0
        },
        "key_metrics": {
            "supplier_diversity_score": 75.0,
            "geographic_risk_score": 60.0,
            "regulatory_compliance_score": 85.0,
            "business_continuity_score": 80.0
        }
    }

@app.get("/api/v1/due-diligence")
async def get_due_diligence_overview():
    """Get due diligence overview for all vendors"""
    return {
        "due_diligence_summary": {
            "total_vendors": 25,
            "completed_assessments": 22,
            "pending_assessments": 3,
            "overdue_reviews": 1,
            "approval_rate": 88.0,
            "average_completion_time_days": 14.5
        },
        "recent_assessments": [
            {
                "id": 1,
                "due_diligence_id": "VDD-A1B2C3D4",
                "vendor_id": 1,
                "vendor_name": "CloudTech Solutions",
                "due_diligence_type": "annual",
                "overall_rating": "approved",
                "financial_stability_rating": "A-",
                "security_assessment_completed": true,
                "privacy_assessment_completed": true,
                "reference_checks_completed": true,
                "reviewed_by": "Procurement Team",
                "review_date": "2024-07-15T10:00:00Z",
                "approved_by": "Chief Procurement Officer",
                "approval_date": "2024-07-17T14:00:00Z",
                "valid_until": "2025-07-17T23:59:59Z",
                "next_review_due": "2025-01-17T10:00:00Z"
            }
        ],
        "pending_reviews": [
            {
                "vendor_name": "New Vendor Corp",
                "due_diligence_type": "initial",
                "days_pending": 5,
                "assigned_to": "Risk Assessment Team"
            }
        ]
    }

@app.get("/api/v1/third-party-dashboard")
async def get_third_party_dashboard():
    """Get comprehensive third-party risk management dashboard"""
    return {
        "portfolio_summary": {
            "total_vendors": 25,
            "active_vendors": 23,
            "critical_vendors": 5,
            "high_risk_vendors": 8,
            "total_contract_value": 5750000.0,
            "average_risk_score": 72.5,
            "concentration_risk_percentage": 45.2
        },
        "risk_distribution": {
            "critical": 3,
            "high": 8,
            "medium": 10,
            "low": 4
        },
        "tier_distribution": {
            "critical": 5,
            "high": 8,
            "medium": 10,
            "low": 2
        },
        "key_metrics": {
            "overdue_assessments": 4,
            "contract_renewals_due_30_days": 3,
            "active_incidents": 2,
            "sla_breaches_this_month": 1,
            "open_action_items": 15,
            "compliance_exceptions": 2
        },
        "risk_trends": {
            "overall_trend": "improving",
            "risk_score_change_30_days": -2.3,
            "new_high_risk_vendors": 1,
            "resolved_high_risk_vendors": 2
        },
        "upcoming_activities": [
            {
                "type": "assessment",
                "vendor_name": "DataProcess Corp",
                "due_date": "2024-08-30T23:59:59Z",
                "priority": "high"
            },
            {
                "type": "contract_renewal",
                "vendor_name": "SecureAuth Systems",
                "due_date": "2024-09-15T23:59:59Z",
                "priority": "medium"
            }
        ],
        "top_risk_vendors": [
            {
                "vendor_name": "Legacy Systems Inc",
                "risk_score": 92.5,
                "tier": "critical",
                "contract_value": 750000.0,
                "issues": ["Outdated security practices", "No backup provider"]
            },
            {
                "vendor_name": "Global Data Services",
                "risk_score": 88.3,
                "tier": "high",
                "contract_value": 320000.0,
                "issues": ["Regulatory compliance gaps", "Geographic concentration"]
            }
        ],
        "recent_alerts": [
            {
                "vendor_name": "CloudTech Solutions",
                "alert_type": "availability_threshold",
                "severity": "medium",
                "triggered_at": "2024-08-15T10:30:00Z"
            }
        ]
    }


if __name__ == "__main__":
    import random
    
    # Use random 5-digit TCP port to avoid conflicts (as per user requirements)
    port = random.randint(10000, 65535)
    print(f"🚀 Starting Aegis Platform backend on port {port}")
    print(f"📡 API will be available at: http://localhost:{port}")
    print(f"📋 API documentation: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0", 
        port=port,
        reload=True,
        log_level="info"
    )