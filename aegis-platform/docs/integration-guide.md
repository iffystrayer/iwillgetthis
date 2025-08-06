# Integration Guide - Aegis Risk Management Platform

## Overview

The Aegis Platform is designed with an integration-first architecture, enabling seamless connectivity with existing security tools, IT infrastructure, and business systems. This guide provides detailed procedures for configuring and managing integrations to maximize the platform's value within your organizational ecosystem.

## Integration Architecture

### API-First Design
- **RESTful APIs**: Comprehensive REST API with OpenAPI 3.0 specification
- **Authentication**: OAuth 2.0, JWT tokens, and API key authentication
- **Rate Limiting**: Configurable rate limits with burst capacity management
- **Webhook Support**: Real-time event notifications and bidirectional communication
- **SDK Support**: Official SDKs for Python, JavaScript, Java, and .NET

### Integration Patterns
- **Pull Integration**: Platform retrieves data from external systems on schedule
- **Push Integration**: External systems send data to platform via APIs
- **Bidirectional Sync**: Two-way data synchronization with conflict resolution
- **Event-Driven**: Real-time integration using webhooks and message queues
- **Batch Processing**: Scheduled bulk data transfer and processing

### Security Model
- **Encrypted Communication**: TLS 1.3 for all integration endpoints
- **Certificate Management**: Mutual TLS authentication for high-security environments
- **IP Whitelisting**: Network-based access control for integration endpoints
- **Audit Logging**: Comprehensive logging of all integration activities
- **Data Encryption**: End-to-end encryption for sensitive data transfers

## Security Information and Event Management (SIEM)

### Splunk Integration

#### Configuration Steps
1. **Install Splunk Add-on**
   ```bash
   # Download Aegis Splunk Add-on
   wget https://platform.aegis.io/integrations/splunk/aegis-splunk-addon.tar.gz
   
   # Install in Splunk
   $SPLUNK_HOME/bin/splunk install app aegis-splunk-addon.tar.gz
   ```

2. **Configure API Connectivity**
   ```ini
   # inputs.conf
   [aegis_api]
   endpoint = https://your-aegis-instance.com/api/v1
   api_key = your-api-key-here
   interval = 300
   index = aegis_risk
   sourcetype = aegis:risk
   ```

3. **Data Collection Setup**
   - **Risk Data**: Automated risk register synchronization
   - **Asset Information**: Asset inventory and classification data
   - **Control Status**: Security control effectiveness and testing results
   - **Compliance Events**: Framework compliance status changes

#### Use Cases
- **Risk Event Correlation**: Correlate security events with risk assessments
- **Automated Risk Updates**: Update risk scores based on security incidents
- **Threat Intelligence**: Enrich risk data with threat intelligence feeds
- **Incident Response**: Trigger risk assessments for security incidents

### IBM QRadar Integration

#### Setup Process
1. **DSM Configuration**
   ```bash
   # Install Aegis DSM
   qradar-dsm-editor -action create -name "Aegis Risk Platform"
   ```

2. **Log Source Configuration**
   - **Protocol**: HTTPS REST API
   - **Endpoint**: `/api/v1/events`
   - **Authentication**: API Key authentication
   - **Format**: JSON structured events

3. **Event Mapping**
   ```json
   {
     "event_definitions": [
       {
         "name": "Risk Created",
         "category": "Risk Management",
         "severity": "medium",
         "properties": ["risk_id", "asset_id", "risk_score", "owner"]
       },
       {
         "name": "Control Failed",
         "category": "Compliance",
         "severity": "high",
         "properties": ["control_id", "framework", "failure_reason"]
       }
     ]
   }
   ```

### Azure Sentinel Integration

#### Connector Deployment
1. **Data Connector Setup**
   ```json
   {
     "name": "AegisRiskPlatform",
     "kind": "APIPolling",
     "properties": {
       "connectorUiConfig": {
         "title": "Aegis Risk Platform",
         "publisher": "Aegis Security",
         "descriptionMarkdown": "Connect to Aegis Risk Platform"
       },
       "pollingConfig": {
         "auth": {
           "authType": "APIKey",
           "APIKeyName": "x-api-key"
         },
         "request": {
           "apiEndpoint": "https://api.aegis.io/v1/events",
           "httpMethod": "GET"
         }
       }
     }
   }
   ```

2. **Workbook Configuration**
   - **Risk Dashboard**: Real-time risk posture visualization
   - **Compliance Overview**: Multi-framework compliance status
   - **Asset Risk Correlation**: Asset-based risk analysis
   - **Trend Analysis**: Historical risk and compliance trends

## Vulnerability Management

### OpenVAS Integration

#### Scanner Configuration
1. **API Setup**
   ```python
   import openvas_api
   
   # Configure OpenVAS connection
   config = {
       'host': 'openvas.internal.com',
       'port': 9390,
       'username': 'aegis-integration',
       'password': 'secure-password'
   }
   
   # Initialize scanner
   scanner = openvas_api.OpenVASAPI(config)
   ```

2. **Automated Scanning Workflow**
   ```yaml
   # scanning-workflow.yml
   name: Automated Vulnerability Scanning
   trigger:
     - schedule: "0 2 * * 1"  # Weekly Monday 2 AM
     - asset_added
   
   steps:
     - name: Create Scan Target
       action: create_target
       parameters:
         hosts: "{{ asset.ip_address }}"
         port_list: "All IANA assigned TCP and UDP"
   
     - name: Start Scan
       action: start_task
       parameters:
         target_id: "{{ target.id }}"
         scanner_id: "OpenVAS Scanner"
   
     - name: Process Results
       action: import_results
       parameters:
         format: "xml"
         destination: "aegis_api"
   ```

3. **Risk Correlation**
   - **CVSS Mapping**: Automatic CVSS score to risk rating conversion
   - **Asset Context**: Vulnerability prioritization based on asset criticality
   - **Control Validation**: Validate security controls against vulnerabilities
   - **Remediation Tracking**: Track vulnerability remediation as risk treatment

### Nessus Integration

#### Plugin Configuration
1. **Nessus API Setup**
   ```bash
   # Configure Nessus integration
   curl -X POST https://nessus.internal.com:8834/session \
     -H "Content-Type: application/json" \
     -d '{"username":"aegis","password":"password"}'
   ```

2. **Scan Policy Configuration**
   ```json
   {
     "uuid": "aegis-risk-assessment",
     "settings": {
       "name": "Aegis Risk Assessment",
       "description": "Comprehensive scan for risk assessment",
       "scanner_policy": "Advanced Scan",
       "acl": [{"permissions": 64, "owner": 1}]
     }
   }
   ```

3. **Result Processing**
   - **Automated Import**: Direct vulnerability import via API
   - **Risk Calculation**: Convert CVSS scores to organizational risk ratings
   - **Asset Correlation**: Link vulnerabilities to asset inventory
   - **Compliance Mapping**: Map vulnerabilities to compliance requirements

### Qualys VMDR Integration

#### API Configuration
1. **Authentication Setup**
   ```python
   import requests
   
   # Qualys API authentication
   auth_data = {
       'action': 'login',
       'username': 'aegis-integration',
       'password': 'secure-password'
   }
   
   session = requests.Session()
   session.post('https://qualysapi.qualys.com/api/2.0/fo/session/', data=auth_data)
   ```

2. **Scan Management**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <ServiceRequest>
     <data>
       <Scan>
         <title>Aegis Risk Assessment</title>
         <asset_groups>
           <AssetGroup>
             <title>Critical Assets</title>
           </AssetGroup>
         </asset_groups>
         <option_profile>
           <title>Comprehensive Scan</title>
         </option_profile>
       </Scan>
     </data>
   </ServiceRequest>
   ```

## Identity and Access Management

### Active Directory Integration

#### LDAP Configuration
1. **Connection Setup**
   ```yaml
   # ldap-config.yml
   ldap:
     server: ldap://dc.internal.com:389
     bind_dn: "CN=aegis-service,OU=Service Accounts,DC=internal,DC=com"
     bind_password: "service-account-password"
     base_dn: "DC=internal,DC=com"
     
     user_search:
       base: "OU=Users,DC=internal,DC=com"
       filter: "(objectClass=user)"
       attributes:
         - sAMAccountName
         - mail
         - displayName
         - memberOf
   
     group_search:
       base: "OU=Groups,DC=internal,DC=com"
       filter: "(objectClass=group)"
       attributes:
         - cn
         - member
   ```

2. **User Synchronization**
   ```python
   # user-sync.py
   import ldap3
   
   def sync_users():
       # Connect to LDAP
       server = ldap3.Server('ldap://dc.internal.com:389')
       conn = ldap3.Connection(server, user='aegis-service', password='password')
       
       # Search for users
       conn.search('OU=Users,DC=internal,DC=com', 
                  '(objectClass=user)',
                  attributes=['sAMAccountName', 'mail', 'displayName', 'memberOf'])
       
       # Process results and update Aegis users
       for entry in conn.entries:
           update_aegis_user(entry)
   ```

3. **Role Mapping**
   ```json
   {
     "role_mappings": [
       {
         "ad_group": "CN=Security Admins,OU=Groups,DC=internal,DC=com",
         "aegis_role": "administrator"
       },
       {
         "ad_group": "CN=Risk Managers,OU=Groups,DC=internal,DC=com",
         "aegis_role": "risk_manager"
       },
       {
         "ad_group": "CN=Asset Owners,OU=Groups,DC=internal,DC=com",
         "aegis_role": "asset_owner"
       }
     ]
   }
   ```

### Azure Active Directory Integration

#### OAuth 2.0 Setup
1. **App Registration**
   ```bash
   # Azure CLI app registration
   az ad app create \
     --display-name "Aegis Risk Platform" \
     --identifier-uris "https://aegis.internal.com" \
     --reply-urls "https://aegis.internal.com/auth/callback"
   ```

2. **SAML Configuration**
   ```xml
   <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                        entityID="https://aegis.internal.com">
     <md:SPSSODescriptor AuthnRequestsSigned="false"
                         WantAssertionsSigned="false"
                         protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
       <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                   Location="https://aegis.internal.com/saml/acs"
                                   index="1" />
     </md:SPSSODescriptor>
   </md:EntityDescriptor>
   ```

3. **Graph API Integration**
   ```python
   # Microsoft Graph API integration
   import requests
   
   def get_azure_users():
       headers = {
           'Authorization': f'Bearer {access_token}',
           'Content-Type': 'application/json'
       }
       
       response = requests.get(
           'https://graph.microsoft.com/v1.0/users',
           headers=headers
       )
       
       return response.json()
   ```

### Okta Integration

#### SCIM Provisioning
1. **SCIM Endpoint Configuration**
   ```json
   {
     "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
     "userName": "user@company.com",
     "name": {
       "formatted": "John Doe",
       "givenName": "John",
       "familyName": "Doe"
     },
     "emails": [
       {
         "primary": true,
         "value": "user@company.com",
         "type": "work"
       }
     ],
     "active": true
   }
   ```

2. **Custom Attributes**
   ```python
   # Custom SCIM attributes for Aegis
   CUSTOM_ATTRIBUTES = {
       'riskRole': 'urn:ietf:params:scim:schemas:extension:aegis:2.0:User:riskRole',
       'assetOwnership': 'urn:ietf:params:scim:schemas:extension:aegis:2.0:User:assetOwnership',
       'complianceLevel': 'urn:ietf:params:scim:schemas:extension:aegis:2.0:User:complianceLevel'
   }
   ```

## IT Service Management

### ServiceNow Integration

#### Service Graph Connector
1. **Integration Hub Setup**
   ```javascript
   // ServiceNow Integration Hub spoke
   var AegisRiskConnector = Class.create();
   AegisRiskConnector.prototype = {
       initialize: function() {
           this.apiEndpoint = 'https://aegis.internal.com/api/v1';
           this.apiKey = gs.getProperty('aegis.api.key');
       },
       
       syncRisks: function() {
           var request = new sn_ws.RESTMessageV2();
           request.setEndpoint(this.apiEndpoint + '/risks');
           request.setHttpMethod('GET');
           request.setRequestHeader('Authorization', 'Bearer ' + this.apiKey);
           
           var response = request.execute();
           return JSON.parse(response.getBody());
       }
   };
   ```

2. **Business Rule Configuration**
   ```javascript
   // Incident to Risk correlation
   (function executeRule(current, previous) {
       if (current.priority <= 2) {  // High priority incidents
           var aegis = new AegisRiskConnector();
           var risks = aegis.getRisksByAsset(current.cmdb_ci);
           
           if (risks.length > 0) {
               current.work_notes = 'Related risks found: ' + risks.join(', ');
           }
       }
   })(current, previous);
   ```

3. **Workflow Integration**
   - **Risk-based Prioritization**: Prioritize tickets based on asset risk levels
   - **Automated Risk Updates**: Update risk status based on ticket resolution
   - **Compliance Tracking**: Track compliance remediation through service desk
   - **Change Risk Assessment**: Assess change requests against risk register

### Jira Integration

#### REST API Configuration
1. **Webhook Setup**
   ```json
   {
     "name": "Aegis Risk Updates",
     "url": "https://aegis.internal.com/webhooks/jira",
     "events": [
       "jira:issue_created",
       "jira:issue_updated",
       "jira:issue_deleted"
     ],
     "filters": {
       "issue-related-events-section": [
         {
           "project": {
             "key": "RISK"
           }
         }
       ]
     }
   }
   ```

2. **Custom Fields Mapping**
   ```python
   # Jira custom fields for risk management
   RISK_FIELDS = {
       'risk_id': 'customfield_10001',
       'risk_score': 'customfield_10002',
       'asset_id': 'customfield_10003',
       'compliance_framework': 'customfield_10004',
       'risk_owner': 'customfield_10005'
   }
   
   def create_risk_issue(risk_data):
       issue_data = {
           'project': {'key': 'RISK'},
           'issuetype': {'name': 'Risk'},
           'summary': risk_data['title'],
           'description': risk_data['description'],
           RISK_FIELDS['risk_id']: risk_data['id'],
           RISK_FIELDS['risk_score']: risk_data['score']
       }
       
       return jira_client.create_issue(fields=issue_data)
   ```

## Network and Infrastructure

### Network Discovery Integration

#### Nmap Integration
1. **Automated Network Scanning**
   ```bash
   #!/bin/bash
   # network-discovery.sh
   
   # Define network ranges
   NETWORKS=(
       "10.0.0.0/16"
       "192.168.0.0/16"
       "172.16.0.0/12"
   )
   
   for network in "${NETWORKS[@]}"; do
       nmap -sn $network | grep "Nmap scan report" | \
       awk '{print $5}' | \
       while read host; do
           # Send discovered host to Aegis API
           curl -X POST https://aegis.internal.com/api/v1/assets \
               -H "Authorization: Bearer $API_TOKEN" \
               -H "Content-Type: application/json" \
               -d "{\"hostname\":\"$host\",\"discovery_method\":\"nmap\"}"
       done
   done
   ```

2. **Service Detection**
   ```python
   import nmap
   import requests
   
   def scan_and_register_services():
       nm = nmap.PortScanner()
       
       for host in discovered_hosts:
           # Scan for services
           nm.scan(host, '1-1000')
           
           services = []
           for port in nm[host]['tcp']:
               service_info = nm[host]['tcp'][port]
               services.append({
                   'port': port,
                   'service': service_info['name'],
                   'version': service_info.get('version', '')
               })
           
           # Register with Aegis
           register_asset_services(host, services)
   ```

### CMDB Integration

#### Asset Synchronization
1. **CMDB Data Mapping**
   ```yaml
   # cmdb-mapping.yml
   asset_mapping:
     - cmdb_field: "name"
       aegis_field: "hostname"
       required: true
   
     - cmdb_field: "ip_address"
       aegis_field: "primary_ip"
       validation: "ipv4"
   
     - cmdb_field: "operating_system"
       aegis_field: "os_family"
       transform: "normalize_os_name"
   
     - cmdb_field: "business_service"
       aegis_field: "business_function"
       lookup: "business_service_mapping"
   
     - cmdb_field: "environment"
       aegis_field: "environment"
       values: ["production", "staging", "development", "test"]
   ```

2. **Relationship Mapping**
   ```python
   def sync_asset_relationships():
       # Fetch CMDB relationships
       relationships = cmdb_client.get_relationships()
       
       for rel in relationships:
           if rel['type'] == 'Depends on':
               # Create dependency in Aegis
               create_asset_dependency(
                   source=rel['source_ci'],
                   target=rel['target_ci'],
                   relationship_type='dependency'
               )
           elif rel['type'] == 'Hosted on':
               # Create hosting relationship
               create_asset_relationship(
                   child=rel['source_ci'],
                   parent=rel['target_ci'],
                   relationship_type='hosting'
               )
   ```

## Cloud Platform Integrations

### Amazon Web Services (AWS)

#### CloudFormation Template
```yaml
# aegis-aws-integration.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Aegis Risk Platform AWS Integration'

Resources:
  AegisIntegrationRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: AegisIntegrationRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/SecurityAudit
        - arn:aws:iam::aws:policy/ReadOnlyAccess

  AegisSecretKey:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: aegis-integration-credentials
      Description: API credentials for Aegis integration
      SecretString: !Sub |
        {
          "api_key": "${AegisAPIKey}",
          "endpoint": "${AegisEndpoint}"
        }

  AegisLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: aegis-asset-sync
      Runtime: python3.9
      Handler: lambda_function.lambda_handler
      Role: !GetAtt AegisLambdaRole.Arn
      Code:
        ZipFile: |
          import boto3
          import json
          import requests
          
          def lambda_handler(event, context):
              # Sync AWS resources with Aegis
              ec2 = boto3.client('ec2')
              instances = ec2.describe_instances()
              
              for reservation in instances['Reservations']:
                  for instance in reservation['Instances']:
                      sync_instance_to_aegis(instance)
              
              return {'statusCode': 200, 'body': 'Sync completed'}
```

#### Config Rules Integration
```python
# aws-config-aegis.py
import boto3
import requests

def evaluate_compliance(configuration_item, rule_parameters):
    """
    AWS Config rule to evaluate resource compliance
    and send results to Aegis platform
    """
    compliance_type = 'COMPLIANT'
    annotation = 'Resource is compliant'
    
    # Evaluate resource configuration
    if not is_encrypted(configuration_item):
        compliance_type = 'NON_COMPLIANT'
        annotation = 'Resource is not encrypted'
        
        # Create risk in Aegis
        create_aegis_risk({
            'title': f'Unencrypted resource: {configuration_item["resourceId"]}',
            'description': 'AWS resource lacks encryption',
            'severity': 'high',
            'asset_id': configuration_item["resourceId"],
            'compliance_framework': 'aws-security-baseline'
        })
    
    return {
        'compliance_type': compliance_type,
        'annotation': annotation
    }
```

### Microsoft Azure

#### ARM Template
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "aegisEndpoint": {
      "type": "string",
      "metadata": {
        "description": "Aegis platform API endpoint"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.ManagedIdentity/userAssignedIdentities",
      "apiVersion": "2018-11-30",
      "name": "aegis-integration-identity",
      "location": "[resourceGroup().location]"
    },
    {
      "type": "Microsoft.Logic/workflows",
      "apiVersion": "2017-07-01",
      "name": "aegis-resource-sync",
      "location": "[resourceGroup().location]",
      "properties": {
        "definition": {
          "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
          "triggers": {
            "Recurrence": {
              "recurrence": {
                "frequency": "Hour",
                "interval": 1
              },
              "type": "Recurrence"
            }
          },
          "actions": {
            "List_Resources": {
              "type": "Http",
              "inputs": {
                "method": "GET",
                "uri": "https://management.azure.com/subscriptions/@{parameters('subscriptionId')}/resources",
                "headers": {
                  "Authorization": "Bearer @{parameters('accessToken')}"
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

### Google Cloud Platform (GCP)

#### Cloud Functions Deployment
```python
# main.py - GCP Cloud Function
import functions_framework
from google.cloud import asset_v1
import requests

@functions_framework.http
def sync_gcp_assets(request):
    """
    Cloud Function to sync GCP assets with Aegis platform
    """
    client = asset_v1.AssetServiceClient()
    project_id = "your-project-id"
    
    # List all assets
    parent = f"projects/{project_id}"
    assets = client.list_assets(request={"parent": parent})
    
    for asset in assets:
        # Sync to Aegis
        aegis_data = {
            'name': asset.name,
            'asset_type': asset.asset_type,
            'resource': asset.resource,
            'iam_policy': asset.iam_policy,
            'org_policy': asset.org_policy
        }
        
        # Send to Aegis API
        response = requests.post(
            'https://aegis.internal.com/api/v1/assets',
            json=aegis_data,
            headers={'Authorization': f'Bearer {api_key}'}
        )
    
    return 'Sync completed'
```

#### Cloud Security Command Center Integration
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        # Create Cloud SCC finding source
        gcloud scc sources create \
          --display-name="Aegis Risk Platform" \
          --description="Risk findings from Aegis platform" \
          --organization=$PROJECT_NUMBER

  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        # Deploy finding sync function
        gcloud functions deploy aegis-scc-sync \
          --runtime=python39 \
          --trigger-http \
          --allow-unauthenticated
```

## Data Integration and ETL

### Database Connectors

#### PostgreSQL Integration
```python
# postgresql-connector.py
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

class PostgreSQLConnector:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
    
    def extract_asset_data(self):
        """Extract asset data from PostgreSQL"""
        query = """
        SELECT 
            hostname,
            ip_address,
            os_type,
            business_owner,
            criticality_level,
            compliance_scope
        FROM asset_inventory
        WHERE active = true
        """
        return pd.read_sql(query, self.engine)
    
    def sync_to_aegis(self, asset_data):
        """Sync extracted data to Aegis platform"""
        for _, asset in asset_data.iterrows():
            aegis_payload = {
                'hostname': asset['hostname'],
                'ip_address': asset['ip_address'],
                'os_family': asset['os_type'],
                'owner': asset['business_owner'],
                'criticality': asset['criticality_level'],
                'compliance_frameworks': asset['compliance_scope'].split(',')
            }
            
            # Send to Aegis API
            self.send_to_aegis(aegis_payload)
```

#### Oracle Integration
```python
# oracle-connector.py
import cx_Oracle
import requests

def extract_oracle_cmdb():
    """Extract CMDB data from Oracle database"""
    connection = cx_Oracle.connect(
        user="aegis_readonly",
        password="secure_password",
        dsn="oracle.internal.com:1521/XE"
    )
    
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            ci.configuration_item_id,
            ci.name,
            ci.category,
            ci.subcategory,
            ci.status,
            ci.business_service,
            attr.ip_address,
            attr.operating_system
        FROM configuration_items ci
        LEFT JOIN ci_attributes attr ON ci.ci_id = attr.ci_id
        WHERE ci.status = 'Active'
    """)
    
    return cursor.fetchall()
```

### File-Based Integration

#### CSV Import/Export
```python
# csv-integration.py
import pandas as pd
import requests
from datetime import datetime

class CSVIntegration:
    def __init__(self, aegis_api_key):
        self.api_key = aegis_api_key
        self.base_url = "https://aegis.internal.com/api/v1"
    
    def import_risks_from_csv(self, csv_file):
        """Import risk data from CSV file"""
        df = pd.read_csv(csv_file)
        
        for _, row in df.iterrows():
            risk_data = {
                'title': row['Risk Title'],
                'description': row['Description'],
                'likelihood': row['Likelihood'],
                'impact': row['Impact'],
                'owner': row['Owner'],
                'asset_ids': row['Affected Assets'].split(',')
            }
            
            self.create_risk(risk_data)
    
    def export_compliance_to_csv(self, framework):
        """Export compliance data to CSV"""
        response = requests.get(
            f"{self.base_url}/compliance/{framework}/export",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        df = pd.DataFrame(response.json()['data'])
        filename = f"compliance_{framework}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        
        return filename
```

#### Excel Integration
```python
# excel-integration.py
import openpyxl
from openpyxl.styles import Font, PatternFill
import requests

def create_compliance_workbook(framework_data):
    """Create Excel workbook with compliance data"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Compliance Overview"
    
    # Headers
    headers = ['Control ID', 'Description', 'Status', 'Evidence', 'Owner', 'Due Date']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # Data rows
    for row, control in enumerate(framework_data, 2):
        ws.cell(row=row, column=1, value=control['id'])
        ws.cell(row=row, column=2, value=control['description'])
        ws.cell(row=row, column=3, value=control['status'])
        ws.cell(row=row, column=4, value=control['evidence_count'])
        ws.cell(row=row, column=5, value=control['owner'])
        ws.cell(row=row, column=6, value=control['due_date'])
    
    return wb
```

## Custom Integration Development

### SDK Usage Examples

#### Python SDK
```python
# python-sdk-example.py
from aegis_sdk import AegisClient
from aegis_sdk.models import Risk, Asset, Control

# Initialize client
client = AegisClient(
    base_url="https://aegis.internal.com/api/v1",
    api_key="your-api-key"
)

# Create an asset
asset = Asset(
    hostname="web-server-01",
    ip_address="10.0.1.100",
    os_family="linux",
    criticality="high",
    owner="john.doe@company.com"
)
created_asset = client.assets.create(asset)

# Create a risk
risk = Risk(
    title="Unpatched vulnerability on web server",
    description="Critical vulnerability CVE-2023-12345 detected",
    likelihood=4,
    impact=4,
    asset_ids=[created_asset.id],
    owner="security-team@company.com"
)
created_risk = client.risks.create(risk)

# Query risks with filters
high_risks = client.risks.list(
    filters={'severity': 'high', 'status': 'open'},
    limit=50
)

for risk in high_risks:
    print(f"Risk: {risk.title} - Score: {risk.risk_score}")
```

#### JavaScript SDK
```javascript
// javascript-sdk-example.js
const { AegisClient } = require('@aegis/sdk');

const client = new AegisClient({
    baseURL: 'https://aegis.internal.com/api/v1',
    apiKey: 'your-api-key'
});

// Async/await usage
async function manageRisks() {
    try {
        // Get all assets
        const assets = await client.assets.list();
        
        // Create risk for each critical asset
        for (const asset of assets) {
            if (asset.criticality === 'critical') {
                const risk = await client.risks.create({
                    title: `Security review required for ${asset.hostname}`,
                    description: 'Critical asset requires security review',
                    likelihood: 3,
                    impact: 4,
                    assetIds: [asset.id],
                    owner: 'security-team@company.com'
                });
                
                console.log(`Created risk ${risk.id} for asset ${asset.hostname}`);
            }
        }
    } catch (error) {
        console.error('Error managing risks:', error);
    }
}

manageRisks();
```

### Custom Webhook Handlers

#### Risk Event Handler
```python
# webhook-handler.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

def verify_signature(payload, signature):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected_signature}")

@app.route('/webhooks/risk-events', methods=['POST'])
def handle_risk_events():
    """Handle risk-related webhook events"""
    signature = request.headers.get('X-Aegis-Signature')
    payload = request.get_data(as_text=True)
    
    if not verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_data = json.loads(payload)
    event_type = event_data.get('event_type')
    
    if event_type == 'risk.created':
        handle_risk_created(event_data['data'])
    elif event_type == 'risk.updated':
        handle_risk_updated(event_data['data'])
    elif event_type == 'risk.resolved':
        handle_risk_resolved(event_data['data'])
    
    return jsonify({'status': 'processed'}), 200

def handle_risk_created(risk_data):
    """Process new risk creation"""
    if risk_data['severity'] == 'critical':
        # Send alert to security team
        send_security_alert(risk_data)
        
        # Create ServiceNow incident
        create_servicenow_incident(risk_data)
        
        # Update SIEM with risk context
        update_siem_context(risk_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## Integration Monitoring and Troubleshooting

### Health Checks

#### Integration Health Dashboard
```python
# health-check.py
import requests
import json
from datetime import datetime, timedelta

class IntegrationHealthChecker:
    def __init__(self, config):
        self.integrations = config['integrations']
        self.thresholds = config['thresholds']
    
    def check_all_integrations(self):
        """Check health of all configured integrations"""
        results = {}
        
        for integration in self.integrations:
            try:
                result = self.check_integration_health(integration)
                results[integration['name']] = result
            except Exception as e:
                results[integration['name']] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return results
    
    def check_integration_health(self, integration):
        """Check health of specific integration"""
        health_data = {
            'name': integration['name'],
            'status': 'healthy',
            'last_sync': None,
            'error_rate': 0,
            'response_time': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check API connectivity
        if integration['type'] == 'api':
            response_time = self.check_api_health(integration['endpoint'])
            health_data['response_time'] = response_time
            
            if response_time > self.thresholds['response_time']:
                health_data['status'] = 'degraded'
        
        # Check last sync time
        last_sync = self.get_last_sync_time(integration['name'])
        if last_sync:
            health_data['last_sync'] = last_sync
            sync_age = datetime.utcnow() - last_sync
            
            if sync_age > timedelta(hours=self.thresholds['sync_age_hours']):
                health_data['status'] = 'stale'
        
        return health_data
```

### Error Handling and Retry Logic

#### Resilient Integration Pattern
```python
# resilient-integration.py
import time
import logging
from functools import wraps
from typing import Callable, Any

def retry_with_backoff(
    max_retries: int = 3,
    backoff_base: float = 2,
    max_backoff: float = 60,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying operations with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logging.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                    
                    backoff_time = min(backoff_base ** attempt, max_backoff)
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {backoff_time}s")
                    time.sleep(backoff_time)
            
            raise last_exception
        
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, exceptions=(requests.RequestException,))
def sync_asset_data(asset_data):
    """Sync asset data with retry logic"""
    response = requests.post(
        'https://aegis.internal.com/api/v1/assets',
        json=asset_data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()
```

### Logging and Observability

#### Integration Logging Framework
```python
# integration-logger.py
import logging
import json
import traceback
from datetime import datetime
from pythonjsonlogger import jsonlogger

class IntegrationLogger:
    def __init__(self, integration_name):
        self.integration_name = integration_name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup structured JSON logging"""
        logger = logging.getLogger(f"aegis.integration.{self.integration_name}")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(integration)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_sync_start(self, sync_type, record_count=None):
        """Log start of synchronization"""
        self.logger.info("Synchronization started", extra={
            'timestamp': datetime.utcnow().isoformat(),
            'integration': self.integration_name,
            'sync_type': sync_type,
            'record_count': record_count,
            'event_type': 'sync_start'
        })
    
    def log_sync_success(self, sync_type, records_processed, duration):
        """Log successful synchronization"""
        self.logger.info("Synchronization completed successfully", extra={
            'timestamp': datetime.utcnow().isoformat(),
            'integration': self.integration_name,
            'sync_type': sync_type,
            'records_processed': records_processed,
            'duration_seconds': duration,
            'event_type': 'sync_success'
        })
    
    def log_sync_error(self, sync_type, error, context=None):
        """Log synchronization error"""
        self.logger.error("Synchronization failed", extra={
            'timestamp': datetime.utcnow().isoformat(),
            'integration': self.integration_name,
            'sync_type': sync_type,
            'error': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'event_type': 'sync_error'
        })
```

---

**Last Updated**: August 6, 2025  
**Version**: 1.0  
**Applies To**: Aegis Platform v1.0+