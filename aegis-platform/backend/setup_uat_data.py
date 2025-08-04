#!/usr/bin/env python3
"""
UAT Test Data Setup Script
Creates realistic test data for User Acceptance Testing
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import hashlib

class UATDataGenerator:
    def __init__(self):
        self.organizations = [
            {
                "name": "Acme Financial Services",
                "type": "Financial Services",
                "size": "Large Enterprise",
                "compliance_frameworks": ["SOX", "GDPR", "NIST CSF", "ISO 27001"]
            },
            {
                "name": "TechStart Inc",
                "type": "Technology",
                "size": "Mid-size Company",
                "compliance_frameworks": ["NIST CSF", "ISO 27001", "SOC 2"]
            },
            {
                "name": "City Municipal Government",
                "type": "Public Sector",
                "size": "Government Entity",
                "compliance_frameworks": ["NIST CSF", "FISMA", "ISO 27001"]
            }
        ]
        
        self.departments = [
            "Information Technology", "Human Resources", "Finance", 
            "Operations", "Legal", "Compliance", "Risk Management",
            "Customer Service", "Marketing", "Sales", "Security"
        ]
        
        self.asset_types = [
            "server", "workstation", "network_device", "application", 
            "database", "cloud_service", "mobile_device", "iot_device"
        ]
        
        self.risk_categories = [
            "cybersecurity", "operational", "compliance", "strategic",
            "financial", "reputational", "legal", "environmental"
        ]

    def generate_users(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic user accounts for UAT"""
        users = []
        roles = ["viewer", "analyst", "manager", "admin", "super_admin"]
        
        # Pre-defined key users
        key_users = [
            {"username": "risk.director", "full_name": "Sarah Johnson", "role": "admin", "department": "Risk Management"},
            {"username": "compliance.manager", "full_name": "Michael Chen", "role": "manager", "department": "Compliance"},
            {"username": "it.security", "full_name": "David Rodriguez", "role": "manager", "department": "Information Technology"},
            {"username": "analyst.1", "full_name": "Jennifer Smith", "role": "analyst", "department": "Risk Management"},
            {"username": "analyst.2", "full_name": "Robert Wilson", "role": "analyst", "department": "Compliance"},
        ]
        
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Jennifer", "William", "Amanda"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        # Add key users first
        for i, user in enumerate(key_users):
            users.append({
                "id": i + 1,
                "username": user["username"],
                "email": f"{user['username']}@company.com",
                "full_name": user["full_name"],
                "role": user["role"],
                "department": user["department"],
                "is_active": True,
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "last_login": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "password_hash": self._generate_password_hash("TempPassword123!")
            })
        
        # Generate additional users
        for i in range(len(key_users), count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            users.append({
                "id": i + 1,
                "username": username,
                "email": f"{username}@company.com",
                "full_name": f"{first_name} {last_name}",
                "role": random.choice(roles),
                "department": random.choice(self.departments),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "last_login": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat() if random.random() > 0.1 else None,
                "password_hash": self._generate_password_hash("TempPassword123!")
            })
        
        return users

    def generate_assets(self, count: int = 500) -> List[Dict[str, Any]]:
        """Generate realistic asset inventory for UAT"""
        assets = []
        
        asset_names = {
            "server": ["Web Server", "Database Server", "Application Server", "File Server", "Domain Controller"],
            "workstation": ["Executive Workstation", "Developer Workstation", "Analyst Workstation", "HR Workstation"],
            "network_device": ["Core Router", "Access Switch", "Firewall", "Load Balancer", "Wireless Controller"],
            "application": ["CRM System", "ERP System", "Email Server", "Web Portal", "Analytics Platform"],
            "database": ["Customer Database", "Financial Database", "HR Database", "Audit Database", "Reporting Database"],
            "cloud_service": ["AWS EC2", "Office 365", "Salesforce", "Google Workspace", "Azure Storage"]
        }
        
        locations = ["Data Center A", "Data Center B", "Office Building 1", "Office Building 2", "Cloud - AWS", "Cloud - Azure"]
        criticality_levels = ["low", "medium", "high", "critical"]
        operating_systems = ["Windows Server 2019", "Ubuntu 20.04", "RHEL 8", "Windows 10", "macOS Monterey"]
        
        for i in range(count):
            asset_type = random.choice(self.asset_types)
            base_name = random.choice(asset_names.get(asset_type, ["Generic Asset"]))
            
            assets.append({
                "id": i + 1,
                "name": f"{base_name} {i+1:03d}",
                "asset_type": asset_type,
                "description": f"{base_name} used for {random.choice(self.departments)} operations",
                "owner": f"user{random.randint(1, 50)}",
                "location": random.choice(locations),
                "criticality": random.choice(criticality_levels),
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}" if asset_type in ["server", "network_device"] else None,
                "operating_system": random.choice(operating_systems) if asset_type in ["server", "workstation"] else None,
                "business_service": random.choice(["Customer Management", "Financial Processing", "HR Operations", "IT Infrastructure"]),
                "compliance_requirements": random.sample(["SOX", "GDPR", "HIPAA", "PCI-DSS", "NIST"], k=random.randint(1, 3)),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "last_updated": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        
        return assets

    def generate_risks(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate realistic risk scenarios for UAT"""
        risks = []
        
        risk_scenarios = {
            "cybersecurity": [
                "Unauthorized database access due to weak authentication",
                "Malware infection through email attachments",
                "DDoS attack on public-facing services",
                "Insider threat data exfiltration",
                "Ransomware encryption of critical systems"
            ],
            "operational": [
                "Key personnel departure causing knowledge loss",
                "System failure during peak business hours",
                "Vendor service disruption affecting operations",
                "Natural disaster impacting primary facility",
                "Supply chain disruption affecting delivery"
            ],
            "compliance": [
                "Regulatory audit findings requiring remediation",
                "Data privacy violation due to improper handling",
                "Financial reporting inaccuracy",
                "Failure to meet contractual obligations",
                "Non-compliance with industry standards"
            ]
        }
        
        statuses = ["identified", "assessed", "treatment_planned", "mitigation_in_progress", "monitoring", "closed"]
        
        for i in range(count):
            category = random.choice(self.risk_categories)
            scenario = random.choice(risk_scenarios.get(category, ["Generic risk scenario"]))
            likelihood = random.randint(1, 5)
            impact = random.randint(1, 5)
            risk_score = likelihood * impact
            
            # Determine risk level based on score
            if risk_score >= 20:
                risk_level = "critical"
            elif risk_score >= 12:
                risk_level = "high"
            elif risk_score >= 6:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            risks.append({
                "id": i + 1,
                "title": f"Risk {i+1:03d}: {scenario[:50]}...",
                "description": scenario,
                "category": category,
                "affected_assets": random.sample(range(1, 501), k=random.randint(1, 5)),
                "likelihood": likelihood,
                "impact": impact,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "owner": f"user{random.randint(1, 50)}",
                "status": random.choice(statuses),
                "identified_date": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
                "last_assessment_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "tags": random.sample(["critical", "regulatory", "technical", "process", "security"], k=random.randint(1, 3)),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            })
        
        return risks

    def generate_assessments(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate compliance assessments for UAT"""
        assessments = []
        
        frameworks = [
            {"name": "NIST Cybersecurity Framework", "controls": 108},
            {"name": "ISO 27001:2013", "controls": 114},
            {"name": "SOC 2 Type II", "controls": 64},
            {"name": "PCI DSS v3.2.1", "controls": 78},
            {"name": "GDPR Compliance", "controls": 45}
        ]
        
        assessment_types = ["internal", "external", "self-assessment", "third-party"]
        statuses = ["planning", "in_progress", "review", "approved", "completed"]
        
        for i in range(count):
            framework = random.choice(frameworks)
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            target_completion = start_date + timedelta(days=random.randint(30, 120))
            
            assessments.append({
                "id": i + 1,
                "name": f"Q{random.randint(1, 4)} 2024 {framework['name']} Assessment",
                "framework_name": framework["name"],
                "framework_version": "2024.1",
                "scope": f"{random.choice(['Enterprise-wide', 'Department-specific', 'System-specific'])} assessment",
                "assessor": f"user{random.randint(1, 10)}",
                "start_date": start_date.isoformat(),
                "target_completion_date": target_completion.isoformat(),
                "actual_completion_date": target_completion.isoformat() if random.random() > 0.3 else None,
                "assessment_type": random.choice(assessment_types),
                "status": random.choice(statuses),
                "total_controls": framework["controls"],
                "controls_assessed": random.randint(0, framework["controls"]),
                "controls_compliant": random.randint(0, framework["controls"] // 2),
                "compliance_percentage": round(random.uniform(60, 95), 1),
                "created_at": start_date.isoformat()
            })
        
        return assessments

    def generate_training_programs(self, count: int = 15) -> List[Dict[str, Any]]:
        """Generate training programs for UAT"""
        programs = []
        
        program_types = [
            "Security Awareness", "Phishing Simulation", "Compliance Training",
            "Technical Security", "Risk Management", "Incident Response",
            "Data Privacy", "Business Continuity", "Third-Party Risk"
        ]
        
        for i in range(count):
            program_type = random.choice(program_types)
            
            programs.append({
                "id": i + 1,
                "name": f"{program_type} Training Program {i+1}",
                "description": f"Comprehensive {program_type.lower()} training for all employees",
                "program_type": program_type.lower().replace(" ", "_"),
                "target_audience": random.choice(["all_employees", "it_staff", "management", "specific_roles"]),
                "duration_hours": random.randint(1, 8),
                "frequency": random.choice(["annual", "quarterly", "monthly", "as_needed"]),
                "mandatory": random.choice([True, False]),
                "created_by": f"user{random.randint(1, 10)}",
                "enrollment_count": random.randint(10, 200),
                "completion_rate": round(random.uniform(70, 98), 1),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            })
        
        return programs

    def generate_continuity_plans(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate business continuity plans for UAT"""
        plans = []
        
        plan_types = [
            "IT Disaster Recovery", "Business Continuity", "Emergency Response",
            "Data Backup and Recovery", "Communication Plan", "Vendor Contingency"
        ]
        
        for i in range(count):
            plan_type = random.choice(plan_types)
            
            plans.append({
                "id": i + 1,
                "name": f"{plan_type} Plan v{random.randint(1, 5)}.{random.randint(0, 9)}",
                "description": f"Comprehensive {plan_type.lower()} plan for business continuity",
                "plan_type": plan_type.lower().replace(" ", "_"),
                "scope": random.choice(["enterprise", "department", "system", "process"]),
                "owner": f"user{random.randint(1, 20)}",
                "approval_status": random.choice(["draft", "review", "approved", "active"]),
                "last_test_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "next_test_date": (datetime.now() + timedelta(days=random.randint(30, 180))).isoformat(),
                "rto_hours": random.randint(1, 72),  # Recovery Time Objective
                "rpo_hours": random.randint(1, 24),  # Recovery Point Objective
                "created_at": (datetime.now() - timedelta(days=random.randint(60, 730))).isoformat(),
                "last_updated": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
            })
        
        return plans

    def generate_vendors(self, count: int = 25) -> List[Dict[str, Any]]:
        """Generate third-party vendors for UAT"""
        vendors = []
        
        vendor_names = [
            "CloudTech Solutions", "SecureIT Services", "DataSafe Corp", "NetGuard Systems",
            "CyberShield Inc", "InfoProtect Ltd", "TechSecure Partners", "SafeCloud Enterprises",
            "DigitalDefense Co", "SecureBase Solutions", "CloudGuard Systems", "DataVault Inc"
        ]
        
        service_types = [
            "Cloud Services", "IT Support", "Security Services", "Software Development",
            "Data Processing", "Consulting", "Managed Services", "SaaS Platform"
        ]
        
        risk_levels = ["low", "medium", "high", "critical"]
        
        for i in range(count):
            vendor_name = random.choice(vendor_names)
            
            vendors.append({
                "id": i + 1,
                "name": f"{vendor_name} {i+1}",
                "service_type": random.choice(service_types),
                "contact_email": f"contact@{vendor_name.lower().replace(' ', '')}.com",
                "contact_phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "risk_level": random.choice(risk_levels),
                "contract_value": random.randint(10000, 1000000),
                "contract_start_date": (datetime.now() - timedelta(days=random.randint(30, 1095))).isoformat(),
                "contract_end_date": (datetime.now() + timedelta(days=random.randint(30, 730))).isoformat(),
                "last_assessment_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "next_assessment_date": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                "compliance_status": random.choice(["compliant", "non_compliant", "pending_review"]),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 1095))).isoformat()
            })
        
        return vendors

    def _generate_password_hash(self, password: str) -> str:
        """Generate a simple password hash for testing"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_complete_dataset(self) -> Dict[str, Any]:
        """Generate complete UAT dataset"""
        print("🔄 Generating UAT test data...")
        
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "description": "UAT test data for Aegis Risk Management Platform"
            },
            "organizations": self.organizations,
            "users": self.generate_users(50),
            "assets": self.generate_assets(500),
            "risks": self.generate_risks(100),
            "assessments": self.generate_assessments(20),
            "training_programs": self.generate_training_programs(15),
            "continuity_plans": self.generate_continuity_plans(10),
            "vendors": self.generate_vendors(25)
        }
        
        print("✅ UAT test data generation completed!")
        print(f"   - Organizations: {len(dataset['organizations'])}")
        print(f"   - Users: {len(dataset['users'])}")
        print(f"   - Assets: {len(dataset['assets'])}")
        print(f"   - Risks: {len(dataset['risks'])}")
        print(f"   - Assessments: {len(dataset['assessments'])}")
        print(f"   - Training Programs: {len(dataset['training_programs'])}")
        print(f"   - Continuity Plans: {len(dataset['continuity_plans'])}")
        print(f"   - Vendors: {len(dataset['vendors'])}")
        
        return dataset

    def save_dataset(self, dataset: Dict[str, Any], filename: str = "uat_test_data.json") -> str:
        """Save dataset to JSON file"""
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2, default=str)
        
        print(f"💾 UAT test data saved to: {filename}")
        return filename

def main():
    """Generate and save UAT test data"""
    generator = UATDataGenerator()
    dataset = generator.generate_complete_dataset()
    filename = generator.save_dataset(dataset)
    
    print("\n" + "="*60)
    print("🎯 UAT TEST DATA GENERATION SUMMARY")
    print("="*60)
    print(f"✅ Complete test dataset generated successfully")
    print(f"✅ Data saved to: {filename}")
    print(f"✅ Ready for UAT environment setup")
    print("\nNext steps:")
    print("1. Review generated test data")
    print("2. Load data into UAT database")
    print("3. Configure UAT user accounts")
    print("4. Begin UAT testing process")
    
    return dataset

if __name__ == "__main__":
    main()