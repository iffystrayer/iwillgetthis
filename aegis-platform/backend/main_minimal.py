from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from config import settings
from database import engine, Base

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
                    "risks": ["read", "write", "delete"]
                },
                "is_active": True
            }
        ]
    }

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