#!/usr/bin/env python3
"""
Database initialization script for Aegis Risk Management Platform.
This script creates the database schema and loads initial seed data.
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database import Base
from models.user import User, Role, UserRole
from models.framework import Framework, Control, ControlMapping
from models.asset import AssetCategory
from models.risk import RiskMatrix

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(db):
    """Create default admin user."""
    print("Creating admin user...")
    
    # Create admin role
    admin_role = Role(
        name="admin",
        description="System Administrator with full access",
        permissions={
            "users": ["create", "read", "update", "delete"],
            "assets": ["create", "read", "update", "delete"],
            "risks": ["create", "read", "update", "delete"],
            "assessments": ["create", "read", "update", "delete"],
            "frameworks": ["create", "read", "update", "delete"],
            "tasks": ["create", "read", "update", "delete"],
            "evidence": ["create", "read", "update", "delete"],
            "reports": ["create", "read", "update", "delete"],
            "integrations": ["create", "read", "update", "delete"],
            "ai_services": ["create", "read", "update", "delete"]
        }
    )
    db.add(admin_role)
    
    # Create analyst role
    analyst_role = Role(
        name="analyst",
        description="Cybersecurity Analyst with assessment and analysis capabilities",
        permissions={
            "assets": ["read", "update"],
            "risks": ["create", "read", "update"],
            "assessments": ["create", "read", "update"],
            "frameworks": ["read"],
            "tasks": ["create", "read", "update"],
            "evidence": ["create", "read", "update"],
            "reports": ["create", "read"],
            "integrations": ["read"],
            "ai_services": ["read"]
        }
    )
    db.add(analyst_role)
    
    # Create readonly role
    readonly_role = Role(
        name="readonly",
        description="Read-only access to all modules",
        permissions={
            "assets": ["read"],
            "risks": ["read"],
            "assessments": ["read"],
            "frameworks": ["read"],
            "tasks": ["read"],
            "evidence": ["read"],
            "reports": ["read"],
            "integrations": ["read"],
            "ai_services": ["read"]
        }
    )
    db.add(readonly_role)
    
    db.commit()
    
    # Create admin user
    hashed_password = pwd_context.hash("admin123")
    admin_user = User(
        email="admin@aegis-platform.com",
        username="admin",
        full_name="System Administrator",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    
    # Assign admin role to admin user
    user_role = UserRole(
        user_id=admin_user.id,
        role_id=admin_role.id
    )
    db.add(user_role)
    db.commit()
    
    print(f"Admin user created: {admin_user.email} (password: admin123)")
    print("Please change the default password after first login!")


def load_nist_csf_framework(db):
    """Load NIST Cybersecurity Framework."""
    print("Loading NIST CSF framework...")
    
    nist_framework = Framework(
        name="NIST Cybersecurity Framework",
        version="1.1",
        description="A framework to improve cybersecurity risk management",
        framework_type="compliance",
        is_public=True
    )
    db.add(nist_framework)
    db.commit()
    
    # NIST CSF Functions and Controls
    nist_controls = [
        # IDENTIFY
        {
            "control_id": "ID.AM-1",
            "title": "Physical devices and systems are inventoried",
            "description": "Physical devices and systems within the organization are inventoried",
            "category": "Asset Management",
            "function": "Identify"
        },
        {
            "control_id": "ID.AM-2",
            "title": "Software platforms and applications are inventoried",
            "description": "Software platforms and applications within the organization are inventoried",
            "category": "Asset Management",
            "function": "Identify"
        },
        {
            "control_id": "ID.GV-1",
            "title": "Organizational cybersecurity policy is established",
            "description": "Organizational cybersecurity policy is established and communicated",
            "category": "Governance",
            "function": "Identify"
        },
        
        # PROTECT
        {
            "control_id": "PR.AC-1",
            "title": "Identities and credentials are issued and managed",
            "description": "Identities and credentials are issued, managed, verified, revoked, and audited",
            "category": "Identity Management",
            "function": "Protect"
        },
        {
            "control_id": "PR.AC-3",
            "title": "Remote access is managed",
            "description": "Remote access is managed according to organizational policy",
            "category": "Identity Management",
            "function": "Protect"
        },
        {
            "control_id": "PR.DS-1",
            "title": "Data-at-rest is protected",
            "description": "Data-at-rest is protected with appropriate encryption and access controls",
            "category": "Data Security",
            "function": "Protect"
        },
        
        # DETECT
        {
            "control_id": "DE.AE-1",
            "title": "A baseline of network operations is established",
            "description": "A baseline of network operations and expected data flows is established and managed",
            "category": "Anomalies and Events",
            "function": "Detect"
        },
        {
            "control_id": "DE.CM-1",
            "title": "Networks are monitored",
            "description": "The network is monitored to detect potential cybersecurity events",
            "category": "Security Continuous Monitoring",
            "function": "Detect"
        },
        
        # RESPOND
        {
            "control_id": "RS.RP-1",
            "title": "Response plan is executed",
            "description": "Response plan is executed during or after an incident",
            "category": "Response Planning",
            "function": "Respond"
        },
        {
            "control_id": "RS.CO-2",
            "title": "Incidents are reported",
            "description": "Incidents are reported consistent with established criteria",
            "category": "Communications",
            "function": "Respond"
        },
        
        # RECOVER
        {
            "control_id": "RC.RP-1",
            "title": "Recovery plan is executed",
            "description": "Recovery plan is executed during or after a cybersecurity incident",
            "category": "Recovery Planning",
            "function": "Recover"
        },
        {
            "control_id": "RC.IM-1",
            "title": "Recovery plans incorporate lessons learned",
            "description": "Recovery plans incorporate lessons learned from organizational experience",
            "category": "Improvements",
            "function": "Recover"
        }
    ]
    
    for control_data in nist_controls:
        control = Control(
            framework_id=nist_framework.id,
            control_id=control_data["control_id"],
            title=control_data["title"],
            description=control_data["description"],
            category=control_data["category"],
            function=control_data["function"],
            control_type="mandatory",
            maturity_level="basic"
        )
        db.add(control)
    
    db.commit()
    print(f"NIST CSF framework loaded with {len(nist_controls)} controls")


def load_cis_controls_framework(db):
    """Load CIS Controls framework."""
    print("Loading CIS Controls framework...")
    
    cis_framework = Framework(
        name="CIS Controls",
        version="8.0",
        description="Critical Security Controls for Effective Cyber Defense",
        framework_type="compliance",
        is_public=True
    )
    db.add(cis_framework)
    db.commit()
    
    # CIS Controls (subset)
    cis_controls = [
        {
            "control_id": "CIS-1",
            "title": "Inventory and Control of Hardware Assets",
            "description": "Actively manage all hardware devices to ensure authorized devices are present",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-2",
            "title": "Inventory and Control of Software Assets",
            "description": "Actively manage all software on the network to ensure authorized software is present",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-3",
            "title": "Continuous Vulnerability Management",
            "description": "Continuously acquire, assess, and take action on new information",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-4",
            "title": "Controlled Use of Administrative Privileges",
            "description": "Processes and tools used to track, control, prevent, and correct use of administrative privileges",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-5",
            "title": "Secure Configuration for Hardware and Software",
            "description": "Establish, implement, and actively manage security configurations",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-6",
            "title": "Maintenance, Monitoring, and Analysis of Audit Logs",
            "description": "Collect, manage, and analyze audit logs to detect anomalous activity",
            "category": "Basic CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-7",
            "title": "Email and Web Browser Protections",
            "description": "Minimize the attack surface and opportunities for attackers",
            "category": "Foundational CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-8",
            "title": "Malware Defenses",
            "description": "Control the installation, spread, and execution of malicious code",
            "category": "Foundational CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-9",
            "title": "Limitation and Control of Network Ports",
            "description": "Manage network infrastructure to limit communications",
            "category": "Foundational CIS Controls",
            "function": "Foundational"
        },
        {
            "control_id": "CIS-10",
            "title": "Data Recovery Capabilities",
            "description": "Processes and tools used to properly back up critical information",
            "category": "Foundational CIS Controls",
            "function": "Foundational"
        }
    ]
    
    for control_data in cis_controls:
        control = Control(
            framework_id=cis_framework.id,
            control_id=control_data["control_id"],
            title=control_data["title"],
            description=control_data["description"],
            category=control_data["category"],
            function=control_data["function"],
            control_type="mandatory",
            maturity_level="basic"
        )
        db.add(control)
    
    db.commit()
    print(f"CIS Controls framework loaded with {len(cis_controls)} controls")


def load_asset_categories(db):
    """Load default asset categories."""
    print("Loading asset categories...")
    
    categories = [
        {"name": "Servers", "description": "Physical and virtual servers"},
        {"name": "Workstations", "description": "Employee workstations and laptops"},
        {"name": "Network Equipment", "description": "Routers, switches, firewalls"},
        {"name": "Databases", "description": "Database systems and repositories"},
        {"name": "Applications", "description": "Software applications and systems"},
        {"name": "Cloud Services", "description": "Cloud-based services and platforms"},
        {"name": "Mobile Devices", "description": "Smartphones, tablets, and mobile devices"},
        {"name": "IoT Devices", "description": "Internet of Things devices"},
        {"name": "Storage Systems", "description": "Data storage systems and devices"}
    ]
    
    for category_data in categories:
        category = AssetCategory(
            name=category_data["name"],
            description=category_data["description"]
        )
        db.add(category)
    
    db.commit()
    print(f"Loaded {len(categories)} asset categories")


def load_risk_matrices(db):
    """Load default risk assessment matrices."""
    print("Loading risk matrices...")
    
    # Standard 5x5 Risk Matrix
    standard_matrix = RiskMatrix(
        name="Standard 5x5 Risk Matrix",
        description="Standard 5x5 qualitative risk assessment matrix",
        matrix_type="qualitative",
        likelihood_levels={
            "very_low": {"value": 1, "label": "Very Low", "description": "Rare occurrence"},
            "low": {"value": 2, "label": "Low", "description": "Unlikely to occur"},
            "medium": {"value": 3, "label": "Medium", "description": "Possible to occur"},
            "high": {"value": 4, "label": "High", "description": "Likely to occur"},
            "very_high": {"value": 5, "label": "Very High", "description": "Almost certain to occur"}
        },
        impact_levels={
            "very_low": {"value": 1, "label": "Very Low", "description": "Minimal impact"},
            "low": {"value": 2, "label": "Low", "description": "Minor impact"},
            "medium": {"value": 3, "label": "Medium", "description": "Moderate impact"},
            "high": {"value": 4, "label": "High", "description": "Major impact"},
            "very_high": {"value": 5, "label": "Very High", "description": "Severe impact"}
        },
        risk_levels={
            "1-4": "low",
            "5-9": "medium",
            "10-14": "high",
            "15-25": "critical"
        },
        is_default=True
    )
    db.add(standard_matrix)
    db.commit()
    
    print("Risk matrices loaded")


def main():
    """Main initialization function."""
    print("Initializing Aegis Risk Management Platform database...")
    
    # Create database engine
    engine = create_engine(settings.database_url)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Load seed data
        create_admin_user(db)
        load_nist_csf_framework(db)
        load_cis_controls_framework(db)
        load_asset_categories(db)
        load_risk_matrices(db)
        
        print("\nDatabase initialization completed successfully!")
        print("\nDefault credentials:")
        print("Email: admin@aegis-platform.com")
        print("Password: admin123")
        print("\nPlease change the default password after first login!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()