#!/usr/bin/env python3
"""Add basic frameworks to the database"""

import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models.framework import Framework, Control
import json

def add_frameworks():
    """Add basic frameworks to the database"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if frameworks already exist
        existing_frameworks = db.query(Framework).count()
        if existing_frameworks > 0:
            print(f"✅ {existing_frameworks} frameworks already exist in database")
            return
        
        # Create NIST CSF Framework
        nist_csf = Framework(
            name="NIST Cybersecurity Framework",
            version="2.0",
            description="NIST Cybersecurity Framework 2.0 - Comprehensive cybersecurity risk management",
            framework_type="security",
            is_public=True,
            is_active=True
        )
        db.add(nist_csf)
        db.commit()
        db.refresh(nist_csf)
        
        # Add some basic NIST CSF controls
        nist_controls = [
            {
                "control_id": "ID.AM-1",
                "title": "Asset Management",
                "description": "Inventories of hardware, software, systems, and services are maintained",
                "category": "Identify",
                "function": "Asset Management",
                "control_type": "mandatory"
            },
            {
                "control_id": "PR.AC-1", 
                "title": "Access Control",
                "description": "Identities and credentials for authorized devices and users are managed",
                "category": "Protect",
                "function": "Access Control",
                "control_type": "mandatory"
            },
            {
                "control_id": "DE.CM-1",
                "title": "Continuous Monitoring",
                "description": "Networks and network communications are monitored to detect cybersecurity events",
                "category": "Detect", 
                "function": "Continuous Monitoring",
                "control_type": "mandatory"
            },
            {
                "control_id": "RS.RP-1",
                "title": "Response Planning",
                "description": "Response processes and procedures are executed and maintained",
                "category": "Respond",
                "function": "Response Planning", 
                "control_type": "mandatory"
            },
            {
                "control_id": "RC.RP-1",
                "title": "Recovery Planning",
                "description": "Recovery processes and procedures are executed and maintained",
                "category": "Recover",
                "function": "Recovery Planning",
                "control_type": "mandatory"
            }
        ]
        
        for control_data in nist_controls:
            control = Control(
                framework_id=nist_csf.id,
                control_id=control_data["control_id"],
                title=control_data["title"],
                description=control_data["description"],
                category=control_data["category"],
                function=control_data["function"],
                control_type=control_data["control_type"],
                maturity_level="basic",
                is_active=True
            )
            db.add(control)
        
        # Create ISO 27001 Framework
        iso27001 = Framework(
            name="ISO 27001:2022",
            version="2022",
            description="ISO/IEC 27001:2022 Information Security Management Systems",
            framework_type="compliance",
            is_public=True,
            is_active=True
        )
        db.add(iso27001)
        db.commit()
        db.refresh(iso27001)
        
        # Add some basic ISO 27001 controls
        iso_controls = [
            {
                "control_id": "A.5.1",
                "title": "Information Security Policies",
                "description": "Information security policy and topic-specific policies shall be defined",
                "category": "Organizational",
                "function": "Governance",
                "control_type": "mandatory"
            },
            {
                "control_id": "A.8.1",
                "title": "Asset Management",
                "description": "Assets associated with information and information processing facilities shall be identified",
                "category": "Technological",
                "function": "Asset Management", 
                "control_type": "mandatory"
            },
            {
                "control_id": "A.9.1",
                "title": "Access Control",
                "description": "Access to information and information processing facilities shall be restricted",
                "category": "Technological",
                "function": "Access Control",
                "control_type": "mandatory"
            }
        ]
        
        for control_data in iso_controls:
            control = Control(
                framework_id=iso27001.id,
                control_id=control_data["control_id"],
                title=control_data["title"],
                description=control_data["description"],
                category=control_data["category"],
                function=control_data["function"],
                control_type=control_data["control_type"],
                maturity_level="basic",
                is_active=True
            )
            db.add(control)
        
        db.commit()
        
        print("✅ Frameworks created successfully!")
        print(f"   - {nist_csf.name} with {len(nist_controls)} controls")
        print(f"   - {iso27001.name} with {len(iso_controls)} controls")
        
    except Exception as e:
        print(f"❌ Error creating frameworks: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_frameworks()