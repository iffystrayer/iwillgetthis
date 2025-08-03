from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

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