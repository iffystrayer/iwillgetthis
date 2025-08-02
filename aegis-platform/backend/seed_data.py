"""Seed data for Aegis Risk Management Platform"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models.user import User, Role
from models.asset import Asset, AssetCategory
from models.framework import Framework, Control, ControlFamily
from models.risk import Risk, RiskCategory, RiskAssessment
from models.task import Task, TaskStatus, TaskPriority
from models.assessment import Assessment, AssessmentStatus
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_seed_data():
    """Create comprehensive seed data for the platform"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Create Roles
        admin_role = Role(
            name="Admin",
            description="Full system access",
            permissions=json.dumps([
                "read_all", "write_all", "delete_all", "manage_users", 
                "manage_settings", "manage_integrations"
            ])
        )
        
        analyst_role = Role(
            name="Analyst", 
            description="Risk analysis and assessment access",
            permissions=json.dumps([
                "read_assets", "read_risks", "write_risks", "read_assessments",
                "write_assessments", "read_tasks", "write_tasks", "read_evidence"
            ])
        )
        
        readonly_role = Role(
            name="ReadOnly",
            description="View-only access to all modules", 
            permissions=json.dumps([
                "read_assets", "read_risks", "read_assessments", "read_tasks", 
                "read_evidence", "read_reports"
            ])
        )
        
        db.add_all([admin_role, analyst_role, readonly_role])
        db.commit()
        
        # 2. Create Users
        admin_user = User(
            username="admin",
            email="admin@aegis.local",
            full_name="System Administrator",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            role_id=admin_role.id
        )
        
        analyst_user = User(
            username="analyst",
            email="analyst@aegis.local", 
            full_name="Security Analyst",
            hashed_password=pwd_context.hash("analyst123"),
            is_active=True,
            role_id=analyst_role.id
        )
        
        readonly_user = User(
            username="viewer",
            email="viewer@aegis.local",
            full_name="Report Viewer", 
            hashed_password=pwd_context.hash("viewer123"),
            is_active=True,
            role_id=readonly_role.id
        )
        
        db.add_all([admin_user, analyst_user, readonly_user])
        db.commit()
        
        # 3. Create Asset Categories
        categories = [
            AssetCategory(name="Servers", description="Physical and virtual servers"),
            AssetCategory(name="Network Equipment", description="Routers, switches, firewalls"),
            AssetCategory(name="Workstations", description="Employee desktop and laptop computers"),
            AssetCategory(name="Mobile Devices", description="Smartphones and tablets"),
            AssetCategory(name="Applications", description="Software applications and systems"),
            AssetCategory(name="Databases", description="Database systems and storage"),
            AssetCategory(name="Cloud Services", description="Cloud-based services and infrastructure")
        ]
        
        db.add_all(categories)
        db.commit()
        
        # 4. Create Sample Assets
        assets = [
            Asset(
                name="Web Application Server",
                description="Primary web application server hosting customer portal",
                asset_type="Server",
                category_id=categories[0].id,
                criticality="High",
                location="Data Center 1",
                owner="IT Team",
                metadata=json.dumps({
                    "os": "Ubuntu 22.04",
                    "ip_address": "10.0.1.10",
                    "environment": "production"
                })
            ),
            Asset(
                name="Database Server",
                description="Primary MySQL database server",
                asset_type="Database",
                category_id=categories[5].id,
                criticality="Critical",
                location="Data Center 1", 
                owner="Database Team",
                metadata=json.dumps({
                    "database_type": "MySQL",
                    "version": "8.0",
                    "backup_frequency": "daily"
                })
            ),
            Asset(
                name="Employee Workstations",
                description="Windows 11 workstations for employees",
                asset_type="Workstation",
                category_id=categories[2].id,
                criticality="Medium",
                location="Office",
                owner="IT Support",
                metadata=json.dumps({
                    "os": "Windows 11",
                    "count": 150,
                    "antivirus": "Windows Defender"
                })
            ),
            Asset(
                name="AWS EC2 Instances",
                description="Cloud compute instances on AWS",
                asset_type="Cloud Service",
                category_id=categories[6].id,
                criticality="High",
                location="AWS us-east-1",
                owner="DevOps Team",
                metadata=json.dumps({
                    "instance_types": ["t3.medium", "t3.large"],
                    "count": 25,
                    "auto_scaling": True
                })
            )
        ]
        
        db.add_all(assets)
        db.commit()
        
        # 5. Create Control Families
        nist_families = [
            ControlFamily(name="AC", full_name="Access Control", description="Controls for managing system access"),
            ControlFamily(name="AU", full_name="Audit and Accountability", description="Controls for system auditing"),
            ControlFamily(name="CA", full_name="Assessment, Authorization, and Monitoring", description="Security assessment controls"),
            ControlFamily(name="CM", full_name="Configuration Management", description="System configuration controls"),
            ControlFamily(name="CP", full_name="Contingency Planning", description="Business continuity controls"),
            ControlFamily(name="IA", full_name="Identification and Authentication", description="User identification controls"),
            ControlFamily(name="IR", full_name="Incident Response", description="Security incident management"),
            ControlFamily(name="RA", full_name="Risk Assessment", description="Risk management controls"),
            ControlFamily(name="SC", full_name="System and Communications Protection", description="System security controls"),
            ControlFamily(name="SI", full_name="System and Information Integrity", description="System integrity controls")
        ]
        
        db.add_all(nist_families)
        db.commit()
        
        # 6. Create Framework
        nist_framework = Framework(
            name="NIST Cybersecurity Framework",
            version="1.1",
            description="NIST Cybersecurity Framework v1.1",
            type="Cybersecurity",
            is_active=True
        )
        
        db.add(nist_framework)
        db.commit()
        
        # 7. Create Sample Controls
        controls = [
            Control(
                framework_id=nist_framework.id,
                family_id=nist_families[0].id,  # Access Control
                control_id="AC-1",
                title="Access Control Policy and Procedures",
                description="Develop, document, and disseminate access control policy and procedures",
                implementation_guidance="Establish formal access control policies and procedures",
                supplemental_guidance="Access control policy addresses purpose, scope, roles, responsibilities",
                control_enhancements="AC-1(1) Review and update procedures"
            ),
            Control(
                framework_id=nist_framework.id,
                family_id=nist_families[0].id,  # Access Control
                control_id="AC-2",
                title="Account Management",
                description="Manage information system accounts and group memberships",
                implementation_guidance="Implement automated account management functions",
                supplemental_guidance="Account management includes establishing conditions for group membership",
                control_enhancements="AC-2(1) Automated system account management"
            ),
            Control(
                framework_id=nist_framework.id,
                family_id=nist_families[5].id,  # IA
                control_id="IA-2",
                title="Identification and Authentication (Organizational Users)",
                description="Uniquely identify and authenticate organizational users",
                implementation_guidance="Use multi-factor authentication for privileged accounts",
                supplemental_guidance="Authentication occurs prior to allowing access to the system",
                control_enhancements="IA-2(1) Network access to privileged accounts"
            ),
            Control(
                framework_id=nist_framework.id,
                family_id=nist_families[8].id,  # SC
                control_id="SC-7",
                title="Boundary Protection",
                description="Monitor and control communications at external boundaries",
                implementation_guidance="Implement firewalls and boundary protection devices",
                supplemental_guidance="Boundary protection mechanisms include firewalls, gateways",
                control_enhancements="SC-7(3) Access points"
            )
        ]
        
        db.add_all(controls)
        db.commit()
        
        # 8. Create Risk Categories
        risk_categories = [
            RiskCategory(name="Cybersecurity", description="Information security and cyber threats"),
            RiskCategory(name="Operational", description="Business operations and processes"),
            RiskCategory(name="Compliance", description="Regulatory and compliance requirements"),
            RiskCategory(name="Financial", description="Financial and economic risks"),
            RiskCategory(name="Strategic", description="Strategic business risks")
        ]
        
        db.add_all(risk_categories)
        db.commit()
        
        # 9. Create Sample Risks
        risks = [
            Risk(
                title="Unauthorized Access to Database",
                description="Risk of unauthorized users gaining access to sensitive customer data",
                category_id=risk_categories[0].id,
                asset_id=assets[1].id,  # Database Server
                likelihood=4,
                impact=5,
                risk_score=20,
                status="Open",
                owner_id=analyst_user.id,
                metadata=json.dumps({
                    "threat_sources": ["Internal threat", "External attacker"],
                    "vulnerabilities": ["Weak authentication", "Unpatched software"],
                    "business_impact": "Data breach, regulatory fines"
                })
            ),
            Risk(
