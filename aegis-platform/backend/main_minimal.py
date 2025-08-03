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