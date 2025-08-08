#!/usr/bin/env python3
"""
Complete Database Initialization and Seeding for Aegis Risk Management Platform

This script creates all necessary tables and populates them with initial data including:
- Default roles and users
- NIST CSF and CIS Controls frameworks
- Sample assets, risks, and other entities
- Risk matrices and scoring configurations
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from config import settings
from database import Base
from models import *
from models.asset import AssetType, AssetCriticality
from models.risk import RiskCategory, RiskStatus
from auth import get_password_hash


def create_database_tables(engine):
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def create_roles(session):
    """Create default roles."""
    print("Creating default roles...")
    
    roles = [
        {
            "name": "Admin",
            "description": "Full administrative access to all platform features",
            "permissions": json.dumps([
                "create_user", "update_user", "delete_user", "view_user",
                "create_asset", "update_asset", "delete_asset", "view_asset",
                "create_risk", "update_risk", "delete_risk", "view_risk",
                "create_task", "update_task", "delete_task", "view_task",
                "create_assessment", "update_assessment", "delete_assessment", "view_assessment",
                "create_evidence", "update_evidence", "delete_evidence", "view_evidence",
                "approve_task", "reject_task", "review_evidence",
                "generate_report", "view_report", "export_data",
                "configure_system", "view_audit_log"
            ])
        },
        {
            "name": "Analyst",
            "description": "Security analyst with assessment and risk management capabilities",
            "permissions": json.dumps([
                "view_user", "create_asset", "update_asset", "view_asset",
                "create_risk", "update_risk", "view_risk",
                "create_task", "update_task", "view_task",
                "create_assessment", "update_assessment", "view_assessment",
                "create_evidence", "update_evidence", "view_evidence",
                "generate_report", "view_report"
            ])
        },
        {
            "name": "ReadOnly",
            "description": "Read-only access to view reports and dashboards",
            "permissions": json.dumps([
                "view_user", "view_asset", "view_risk", "view_task",
                "view_assessment", "view_evidence", "view_report"
            ])
        }
    ]
    
    for role_data in roles:
        existing_role = session.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            session.add(role)
    
    session.commit()
    print("✅ Default roles created")


def create_default_users(session):
    """Create default users for testing."""
    print("Creating default users...")
    
    users = [
        {
            "email": "admin@aegis-platform.com",
            "username": "admin",
            "full_name": "System Administrator",
            "department": "Information Security",
            "job_title": "Security Administrator",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "is_verified": True,
            "role_name": "Admin"
        },
        {
            "email": "analyst@aegis-platform.com",
            "username": "analyst",
            "full_name": "Security Analyst",
            "department": "Information Security",
            "job_title": "Cybersecurity Analyst",
            "hashed_password": get_password_hash("analyst123"),
            "is_active": True,
            "is_verified": True,
            "role_name": "Analyst"
        },
        {
            "email": "viewer@aegis-platform.com",
            "username": "viewer",
            "full_name": "Report Viewer",
            "department": "Management",
            "job_title": "Manager",
            "hashed_password": get_password_hash("viewer123"),
            "is_active": True,
            "is_verified": True,
            "role_name": "ReadOnly"
        }
    ]
    
    for user_data in users:
        existing_user = session.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            role_name = user_data.pop("role_name")
            user = User(**user_data)
            session.add(user)
            session.flush()  # Get the user ID
            
            # Assign role
            role = session.query(Role).filter(Role.name == role_name).first()
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                session.add(user_role)
    
    session.commit()
    print("✅ Default users created")


def create_asset_categories(session):
    """Create asset categories."""
    print("Creating asset categories...")
    
    categories = [
        {"name": "Infrastructure", "description": "Physical and virtual infrastructure components"},
        {"name": "Applications", "description": "Software applications and systems"},
        {"name": "Data", "description": "Databases and data repositories"},
        {"name": "Network", "description": "Network equipment and components"},
        {"name": "Endpoints", "description": "End-user devices and workstations"},
        {"name": "Cloud", "description": "Cloud services and resources"}
    ]
    
    for category_data in categories:
        existing_category = session.query(AssetCategory).filter(
            AssetCategory.name == category_data["name"]
        ).first()
        if not existing_category:
            category = AssetCategory(**category_data)
            session.add(category)
    
    session.commit()
    print("✅ Asset categories created")


def create_frameworks(session):
    """Create NIST CSF and CIS Controls frameworks."""
    print("Creating security frameworks...")
    
    # NIST Cybersecurity Framework
    nist_framework = session.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
    if not nist_framework:
        nist_framework = Framework(
            name="NIST CSF 2.0",
            version="2.0",
            description="NIST Cybersecurity Framework 2.0 - NIST cybersecurity framework",
            is_active=True
        )
        session.add(nist_framework)
        session.flush()
        
        # NIST CSF Controls
        nist_controls = [
            # Identify
            {"control_id": "ID.AM-1", "title": "Asset Management", "description": "Inventory of authorized and unauthorized devices", "category": "Asset Management", "function": "Identify"},
            {"control_id": "ID.AM-2", "title": "Software Assets", "description": "Inventory of authorized and unauthorized software", "category": "Asset Management", "function": "Identify"},
            {"control_id": "ID.BE-1", "title": "Business Environment", "description": "Organization's role in the supply chain", "category": "Business Environment", "function": "Identify"},
            {"control_id": "ID.GV-1", "title": "Governance Policy", "description": "Organizational cybersecurity policy", "category": "Governance", "function": "Identify"},
            {"control_id": "ID.RA-1", "title": "Risk Assessment", "description": "Asset vulnerabilities are identified and documented", "category": "Risk Assessment", "function": "Identify"},
            
            # Protect
            {"control_id": "PR.AC-1", "title": "Access Control", "description": "Identities and credentials are issued, managed, verified, revoked, and audited", "category": "Identity Management and Access Control", "function": "Protect"},
            {"control_id": "PR.AC-3", "title": "Remote Access", "description": "Remote access is managed", "category": "Identity Management and Access Control", "function": "Protect"},
            {"control_id": "PR.AT-1", "title": "Security Training", "description": "All users are informed and trained", "category": "Awareness and Training", "function": "Protect"},
            {"control_id": "PR.DS-1", "title": "Data Protection", "description": "Data-at-rest is protected", "category": "Data Security", "function": "Protect"},
            {"control_id": "PR.PT-1", "title": "Protective Technology", "description": "Audit/log records are determined, documented, implemented, and reviewed", "category": "Protective Technology", "function": "Protect"},
            
            # Detect
            {"control_id": "DE.AE-1", "title": "Security Monitoring", "description": "A baseline of network operations and expected data flows is established and managed", "category": "Anomalies and Events", "function": "Detect"},
            {"control_id": "DE.CM-1", "title": "Continuous Monitoring", "description": "The network is monitored to detect potential cybersecurity events", "category": "Security Continuous Monitoring", "function": "Detect"},
            {"control_id": "DE.DP-1", "title": "Detection Processes", "description": "Roles and responsibilities for detection are well defined", "category": "Detection Processes", "function": "Detect"},
            
            # Respond
            {"control_id": "RS.RP-1", "title": "Response Planning", "description": "Response plan is executed during or after an incident", "category": "Response Planning", "function": "Respond"},
            {"control_id": "RS.CO-1", "title": "Response Communications", "description": "Personnel know their roles and order of operations", "category": "Communications", "function": "Respond"},
            {"control_id": "RS.AN-1", "title": "Response Analysis", "description": "Notifications from detection systems are investigated", "category": "Analysis", "function": "Respond"},
            
            # Recover
            {"control_id": "RC.RP-1", "title": "Recovery Planning", "description": "Recovery plan is executed during or after a cybersecurity incident", "category": "Recovery Planning", "function": "Recover"},
            {"control_id": "RC.CO-1", "title": "Recovery Communications", "description": "Public relations are managed", "category": "Communications", "function": "Recover"},
        ]
        
        for control_data in nist_controls:
            # Remove fields that don't exist in the Control model
            filtered_data = {k: v for k, v in control_data.items() if k in ['control_id', 'title', 'description']}
            filtered_data["framework_id"] = nist_framework.id
            control = Control(**filtered_data)
            session.add(control)
    
    # CIS Controls
    cis_framework = session.query(Framework).filter(Framework.name == "CIS Controls v8").first()
    if not cis_framework:
        cis_framework = Framework(
            name="CIS Controls v8",
            version="8.0",
            description="CIS Critical Security Controls Version 8 - Center for Internet Security cybersecurity framework",
            is_active=True
        )
        session.add(cis_framework)
        session.flush()
        
        # CIS Controls
        cis_controls = [
            {"control_id": "CIS-1", "title": "Inventory and Control of Enterprise Assets", "description": "Actively manage (inventory, track, and correct) all enterprise assets", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-2", "title": "Inventory and Control of Software Assets", "description": "Actively manage (inventory, track, and correct) all software", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-3", "title": "Data Protection", "description": "Develop processes and technical controls to identify, classify, securely handle, retain, and dispose of data", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-4", "title": "Secure Configuration of Enterprise Assets and Software", "description": "Establish and maintain the secure configuration of enterprise assets and software", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-5", "title": "Account Management", "description": "Use processes and tools to assign access privileges to enterprise assets and software", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-6", "title": "Access Control Management", "description": "Use processes and tools to create, assign, manage, and revoke access credentials and privileges", "category": "Basic Controls", "function": "Foundational"},
            {"control_id": "CIS-7", "title": "Continuous Vulnerability Management", "description": "Develop a plan to continuously assess and track vulnerabilities", "category": "Organizational Controls", "function": "Foundational"},
            {"control_id": "CIS-8", "title": "Audit Log Management", "description": "Collect, alert, review, and retain audit logs", "category": "Organizational Controls", "function": "Foundational"},
            {"control_id": "CIS-9", "title": "Email and Web Browser Protections", "description": "Improve protections and detections of threats from email and web vectors", "category": "Organizational Controls", "function": "Foundational"},
            {"control_id": "CIS-10", "title": "Malware Defenses", "description": "Prevent or control the installation, spread, and execution of malicious applications", "category": "Organizational Controls", "function": "Foundational"},
            {"control_id": "CIS-11", "title": "Data Recovery", "description": "Establish and maintain data recovery practices", "category": "Organizational Controls", "function": "Foundational"},
            {"control_id": "CIS-12", "title": "Network Infrastructure Management", "description": "Establish, implement, and actively manage enterprise assets connected to the network", "category": "Organizational Controls", "function": "Foundational"},
        ]
        
        for control_data in cis_controls:
            # Remove fields that don't exist in the Control model
            filtered_data = {k: v for k, v in control_data.items() if k in ['control_id', 'title', 'description']}
            filtered_data["framework_id"] = cis_framework.id
            control = Control(**filtered_data)
            session.add(control)
    
    session.commit()
    print("✅ Security frameworks created")


def create_sample_assets(session):
    """Create sample assets for demonstration."""
    print("Creating sample assets...")
    
    # Get categories
    infra_cat = session.query(AssetCategory).filter(AssetCategory.name == "Infrastructure").first()
    app_cat = session.query(AssetCategory).filter(AssetCategory.name == "Applications").first()
    data_cat = session.query(AssetCategory).filter(AssetCategory.name == "Data").first()
    network_cat = session.query(AssetCategory).filter(AssetCategory.name == "Network").first()
    
    # Get admin user
    admin_user = session.query(User).filter(User.username == "admin").first()
    
    assets = [
        {
            "name": "Web Server 01",
            "description": "Primary web application server hosting customer portal",
            "asset_type": AssetType.SERVER,
            "category_id": infra_cat.id if infra_cat else None,
            "criticality": AssetCriticality.CRITICAL,
            "status": "active",
            "ip_address": "10.1.1.10",
            "hostname": "web01.company.com",
            "operating_system": "Ubuntu 22.04 LTS",
            "location": "Data Center A",
            "environment": "production",
            "business_unit": "IT Operations",
            "created_by": admin_user.id if admin_user else 1
        },
        {
            "name": "Database Server - Production",
            "description": "Primary PostgreSQL database server",
            "asset_type": AssetType.DATABASE,
            "category_id": data_cat.id if data_cat else None,
            "criticality": AssetCriticality.CRITICAL,
            "status": "active",
            "ip_address": "10.1.1.20",
            "hostname": "db01.company.com",
            "operating_system": "CentOS 8",
            "location": "Data Center A",
            "environment": "production",
            "business_unit": "IT Operations",
            "created_by": admin_user.id if admin_user else 1
        },
        {
            "name": "Employee Workstation Fleet",
            "description": "Standard employee workstations (approximately 250 units)",
            "asset_type": AssetType.WORKSTATION,
            "category_id": infra_cat.id if infra_cat else None,
            "criticality": AssetCriticality.MEDIUM,
            "status": "active",
            "location": "Corporate Offices",
            "environment": "production",
            "business_unit": "Human Resources",
            "created_by": admin_user.id if admin_user else 1
        },
        {
            "name": "Network Firewall",
            "description": "Primary perimeter firewall protecting internal network",
            "asset_type": AssetType.NETWORK_DEVICE,
            "category_id": network_cat.id if network_cat else None,
            "criticality": AssetCriticality.HIGH,
            "status": "active",
            "ip_address": "10.1.1.1",
            "hostname": "fw01.company.com",
            "location": "Data Center A",
            "environment": "production",
            "business_unit": "IT Operations",
            "created_by": admin_user.id if admin_user else 1
        }
    ]
    
    for asset_data in assets:
        existing_asset = session.query(Asset).filter(Asset.name == asset_data["name"]).first()
        if not existing_asset:
            asset = Asset(**asset_data)
            session.add(asset)
    
    session.commit()
    print("✅ Sample assets created")


def create_risk_matrices(session):
    """Create risk assessment matrices."""
    print("Creating risk matrices...")
    
    # Standard 5x5 Risk Matrix
    risk_matrix = session.query(RiskMatrix).filter(RiskMatrix.name == "Standard 5x5").first()
    if not risk_matrix:
        risk_matrix = RiskMatrix(
            name="Standard 5x5",
            description="Standard 5x5 risk assessment matrix",
            likelihood_levels=json.dumps([
                {"level": 1, "name": "Very Low", "description": "Extremely unlikely to occur"},
                {"level": 2, "name": "Low", "description": "Unlikely to occur"},
                {"level": 3, "name": "Medium", "description": "Possible to occur"},
                {"level": 4, "name": "High", "description": "Likely to occur"},
                {"level": 5, "name": "Very High", "description": "Almost certain to occur"}
            ]),
            impact_levels=json.dumps([
                {"level": 1, "name": "Very Low", "description": "Minimal impact"},
                {"level": 2, "name": "Low", "description": "Minor impact"},
                {"level": 3, "name": "Medium", "description": "Moderate impact"},
                {"level": 4, "name": "High", "description": "Major impact"},
                {"level": 5, "name": "Very High", "description": "Catastrophic impact"}
            ]),
            risk_levels=json.dumps([
                {"min_score": 1, "max_score": 4, "level": "low", "color": "green"},
                {"min_score": 5, "max_score": 9, "level": "medium", "color": "yellow"},
                {"min_score": 10, "max_score": 14, "level": "high", "color": "orange"},
                {"min_score": 15, "max_score": 25, "level": "critical", "color": "red"}
            ]),
            is_default=True
        )
        session.add(risk_matrix)
    
    session.commit()
    print("✅ Risk matrices created")


def create_sample_risks(session):
    """Create sample risks for demonstration."""
    print("Creating sample risks...")
    
    # Get assets
    web_server = session.query(Asset).filter(Asset.name == "Web Server 01").first()
    db_server = session.query(Asset).filter(Asset.name == "Database Server - Production").first()
    workstations = session.query(Asset).filter(Asset.name == "Employee Workstation Fleet").first()
    
    # Get admin user
    admin_user = session.query(User).filter(User.username == "admin").first()
    
    risks = [
        {
            "title": "Unpatched Web Server Vulnerability",
            "description": "Critical security vulnerability in web server requires immediate patching",
            "category": RiskCategory.TECHNICAL,
            "asset_id": web_server.id if web_server else None,
            "inherent_likelihood": 4,
            "inherent_impact": 5,
            "inherent_risk_score": 20,
            "residual_risk_score": 8,
            "risk_level": "critical",
            "status": RiskStatus.MITIGATING,
            "created_by": admin_user.id if admin_user else 1,
            "identified_date": datetime.utcnow() - timedelta(days=5)
        },
        {
            "title": "Third-Party Vendor Data Access",
            "description": "External vendor has excessive access to sensitive customer data",
            "category": RiskCategory.OPERATIONAL,
            "inherent_likelihood": 3,
            "inherent_impact": 4,
            "inherent_risk_score": 12,
            "residual_risk_score": 6,
            "risk_level": "high",
            "status": RiskStatus.ASSESSED,
            "created_by": admin_user.id if admin_user else 1,
            "identified_date": datetime.utcnow() - timedelta(days=12)
        },
        {
            "title": "Inadequate Backup Recovery Testing",
            "description": "Backup systems have not been tested for recovery in over 6 months",
            "category": RiskCategory.OPERATIONAL,
            "asset_id": db_server.id if db_server else None,
            "inherent_likelihood": 2,
            "inherent_impact": 4,
            "inherent_risk_score": 8,
            "residual_risk_score": 4,
            "risk_level": "medium",
            "status": RiskStatus.IDENTIFIED,
            "created_by": admin_user.id if admin_user else 1,
            "identified_date": datetime.utcnow() - timedelta(days=8)
        },
        {
            "title": "Employee Security Awareness Gap",
            "description": "Staff lack adequate training on phishing and social engineering attacks",
            "category": RiskCategory.OPERATIONAL,
            "asset_id": workstations.id if workstations else None,
            "inherent_likelihood": 3,
            "inherent_impact": 3,
            "inherent_risk_score": 9,
            "residual_risk_score": 6,
            "risk_level": "medium",
            "status": RiskStatus.MITIGATING,
            "created_by": admin_user.id if admin_user else 1,
            "identified_date": datetime.utcnow() - timedelta(days=20)
        }
    ]
    
    for risk_data in risks:
        existing_risk = session.query(Risk).filter(Risk.title == risk_data["title"]).first()
        if not existing_risk:
            risk = Risk(**risk_data)
            session.add(risk)
    
    session.commit()
    print("✅ Sample risks created")


def create_sample_tasks(session):
    """Create sample tasks for demonstration."""
    print("Creating sample tasks...")
    
    # Get users and risks
    admin_user = session.query(User).filter(User.username == "admin").first()
    analyst_user = session.query(User).filter(User.username == "analyst").first()
    
    web_risk = session.query(Risk).filter(Risk.title == "Unpatched Web Server Vulnerability").first()
    backup_risk = session.query(Risk).filter(Risk.title == "Inadequate Backup Recovery Testing").first()
    
    tasks = [
        {
            "title": "Apply Critical Security Patches to Web Server",
            "description": "Apply latest security patches to web server to address critical vulnerability",
            "task_type": "remediation",
            "priority": "critical",
            "status": "in_progress",
            "progress_percentage": 60,
            "risk_id": web_risk.id if web_risk else None,
            "assigned_to_id": analyst_user.id if analyst_user else 1,
            "created_by_id": admin_user.id if admin_user else 1,
            "due_date": datetime.utcnow() + timedelta(days=2)
        },
        {
            "title": "Conduct Backup Recovery Test",
            "description": "Perform comprehensive backup recovery test for all critical systems",
            "task_type": "validation",
            "priority": "high",
            "status": "open",
            "progress_percentage": 0,
            "risk_id": backup_risk.id if backup_risk else None,
            "assigned_to_id": analyst_user.id if analyst_user else 1,
            "created_by_id": admin_user.id if admin_user else 1,
            "due_date": datetime.utcnow() + timedelta(days=7)
        },
        {
            "title": "Review Vendor Access Permissions",
            "description": "Audit and reduce third-party vendor access to sensitive data",
            "task_type": "review",
            "priority": "medium",
            "status": "open",
            "progress_percentage": 0,
            "assigned_to_id": admin_user.id if admin_user else 1,
            "created_by_id": admin_user.id if admin_user else 1,
            "due_date": datetime.utcnow() + timedelta(days=14)
        }
    ]
    
    for task_data in tasks:
        existing_task = session.query(Task).filter(Task.title == task_data["title"]).first()
        if not existing_task:
            task = Task(**task_data)
            session.add(task)
    
    session.commit()
    print("✅ Sample tasks created")


def main():
    """Main initialization function."""
    print("🚀 Initializing Aegis Risk Management Platform Database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Test database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Create tables and seed data
    try:
        create_database_tables(engine)
        
        session = SessionLocal()
        try:
            create_roles(session)
            create_default_users(session)
            create_asset_categories(session)
            create_frameworks(session)
            create_sample_assets(session)
            create_risk_matrices(session)
            create_sample_risks(session)
            create_sample_tasks(session)
            
            print("\n🎉 Database initialization completed successfully!")
            print("\n📊 Summary:")
            print(f"   • Roles: {session.query(Role).count()}")
            print(f"   • Users: {session.query(User).count()}")
            print(f"   • Asset Categories: {session.query(AssetCategory).count()}")
            print(f"   • Frameworks: {session.query(Framework).count()}")
            print(f"   • Controls: {session.query(Control).count()}")
            print(f"   • Assets: {session.query(Asset).count()}")
            print(f"   • Risks: {session.query(Risk).count()}")
            print(f"   • Tasks: {session.query(Task).count()}")
            
            print("\n🔐 Default Login Credentials:")
            print("   • Admin: admin@aegis-platform.com / admin123")
            print("   • Analyst: analyst@aegis-platform.com / analyst123")
            print("   • Viewer: viewer@aegis-platform.com / viewer123")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
