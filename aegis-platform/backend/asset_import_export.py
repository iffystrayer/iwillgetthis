"""
Asset Bulk Import/Export System
Handles CSV, JSON, and Excel formats for asset data management
"""

import pandas as pd
import json
import csv
import io
import zipfile
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import tempfile
import logging

from sqlalchemy.orm import Session
from models.asset import Asset, AssetCategory
from models.asset_relationship import AssetRelationship
from schemas.asset import AssetCreate, AssetResponse
from schemas.asset_relationship import AssetRelationshipCreate


logger = logging.getLogger(__name__)


class AssetImportExportManager:
    """Manages bulk import and export operations for assets"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.supported_formats = ['csv', 'json', 'xlsx', 'xml']
        
    def export_assets(
        self, 
        format: str = 'csv',
        asset_ids: Optional[List[int]] = None,
        include_relationships: bool = False,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Export assets to specified format"""
        
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
        
        # Get assets
        query = self.db.query(Asset)
        if asset_ids:
            query = query.filter(Asset.id.in_(asset_ids))
        
        assets = query.filter(Asset.is_active == True).all()
        
        # Convert to dictionaries
        asset_data = []
        for asset in assets:
            asset_dict = {
                'id': asset.id,
                'name': asset.name,
                'description': asset.description,
                'asset_type': asset.asset_type.value,
                'criticality': asset.criticality.value,
                'category_id': asset.category_id,
                'owner_id': asset.owner_id,
                'ip_address': asset.ip_address,
                'hostname': asset.hostname,
                'operating_system': asset.operating_system,
                'version': asset.version,
                'location': asset.location,
                'environment': asset.environment,
                'business_unit': asset.business_unit,
                'cost_center': asset.cost_center,
                'compliance_scope': asset.compliance_scope,
                'status': asset.status,
                'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
                'warranty_expiry': asset.warranty_expiry.isoformat() if asset.warranty_expiry else None,
                'last_scan_date': asset.last_scan_date.isoformat() if asset.last_scan_date else None,
                'tags': asset.tags,
                'custom_fields': asset.custom_fields,
                'created_at': asset.created_at.isoformat(),
                'updated_at': asset.updated_at.isoformat() if asset.updated_at else None
            }
            
            if include_metadata:
                # Add category information
                if asset.category:
                    asset_dict['category_name'] = asset.category.name
                    asset_dict['category_description'] = asset.category.description
                
                # Add owner information
                if asset.owner:
                    asset_dict['owner_email'] = asset.owner.email
                    asset_dict['owner_name'] = asset.owner.full_name
            
            asset_data.append(asset_dict)
        
        # Export relationships if requested
        relationships_data = []
        if include_relationships:
            relationships = self.db.query(AssetRelationship).filter(
                AssetRelationship.is_active == True
            )
            
            if asset_ids:
                relationships = relationships.filter(
                    (AssetRelationship.source_asset_id.in_(asset_ids)) |
                    (AssetRelationship.target_asset_id.in_(asset_ids))
                )
            
            for rel in relationships.all():
                relationships_data.append({
                    'id': rel.id,
                    'source_asset_id': rel.source_asset_id,
                    'target_asset_id': rel.target_asset_id,
                    'relationship_type': rel.relationship_type.value,
                    'relationship_strength': rel.relationship_strength.value,
                    'description': rel.description,
                    'port': rel.port,
                    'protocol': rel.protocol,
                    'data_flow_direction': rel.data_flow_direction,
                    'impact_percentage': rel.impact_percentage,
                    'recovery_time_minutes': rel.recovery_time_minutes,
                    'is_validated': rel.is_validated,
                    'discovered_method': rel.discovered_method,
                    'created_at': rel.created_at.isoformat()
                })
        
        # Generate export based on format
        if format == 'csv':
            return self._export_to_csv(asset_data, relationships_data, include_relationships)
        elif format == 'json':
            return self._export_to_json(asset_data, relationships_data, include_relationships)
        elif format == 'xlsx':
            return self._export_to_excel(asset_data, relationships_data, include_relationships)
        elif format == 'xml':
            return self._export_to_xml(asset_data, relationships_data, include_relationships)
    
    def _export_to_csv(self, assets: List[Dict], relationships: List[Dict], include_relationships: bool) -> Dict[str, Any]:
        """Export to CSV format"""
        assets_csv = io.StringIO()
        
        if assets:
            df = pd.DataFrame(assets)
            df.to_csv(assets_csv, index=False)
        
        result = {
            'format': 'csv',
            'assets_csv': assets_csv.getvalue(),
            'asset_count': len(assets),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        if include_relationships and relationships:
            relationships_csv = io.StringIO()
            rel_df = pd.DataFrame(relationships)
            rel_df.to_csv(relationships_csv, index=False)
            result['relationships_csv'] = relationships_csv.getvalue()
            result['relationship_count'] = len(relationships)
        
        return result
    
    def _export_to_json(self, assets: List[Dict], relationships: List[Dict], include_relationships: bool) -> Dict[str, Any]:
        """Export to JSON format"""
        result = {
            'format': 'json',
            'export_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': self.user_id,
                'asset_count': len(assets),
                'includes_relationships': include_relationships
            },
            'assets': assets
        }
        
        if include_relationships:
            result['relationships'] = relationships
            result['export_metadata']['relationship_count'] = len(relationships)
        
        return result
    
    def _export_to_excel(self, assets: List[Dict], relationships: List[Dict], include_relationships: bool) -> Dict[str, Any]:
        """Export to Excel format"""
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Assets sheet
            if assets:
                assets_df = pd.DataFrame(assets)
                assets_df.to_excel(writer, sheet_name='Assets', index=False)
            
            # Relationships sheet
            if include_relationships and relationships:
                rel_df = pd.DataFrame(relationships)
                rel_df.to_excel(writer, sheet_name='Relationships', index=False)
            
            # Metadata sheet
            metadata = {
                'Generated At': [datetime.utcnow().isoformat()],
                'Generated By User': [self.user_id],
                'Asset Count': [len(assets)],
                'Relationship Count': [len(relationships) if include_relationships else 0],
                'Includes Relationships': [include_relationships]
            }
            metadata_df = pd.DataFrame(metadata)
            metadata_df.to_excel(writer, sheet_name='Export Info', index=False)
        
        excel_buffer.seek(0)
        
        return {
            'format': 'xlsx',
            'excel_data': excel_buffer.getvalue(),
            'asset_count': len(assets),
            'relationship_count': len(relationships) if include_relationships else 0,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _export_to_xml(self, assets: List[Dict], relationships: List[Dict], include_relationships: bool) -> Dict[str, Any]:
        """Export to XML format"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<aegis_export>\n'
        xml_content += f'  <metadata>\n'
        xml_content += f'    <generated_at>{datetime.utcnow().isoformat()}</generated_at>\n'
        xml_content += f'    <generated_by_user>{self.user_id}</generated_by_user>\n'
        xml_content += f'    <asset_count>{len(assets)}</asset_count>\n'
        xml_content += f'    <relationship_count>{len(relationships) if include_relationships else 0}</relationship_count>\n'
        xml_content += f'  </metadata>\n'
        
        # Assets
        xml_content += '  <assets>\n'
        for asset in assets:
            xml_content += '    <asset>\n'
            for key, value in asset.items():
                if value is not None:
                    xml_content += f'      <{key}>{self._escape_xml(str(value))}</{key}>\n'
            xml_content += '    </asset>\n'
        xml_content += '  </assets>\n'
        
        # Relationships
        if include_relationships and relationships:
            xml_content += '  <relationships>\n'
            for rel in relationships:
                xml_content += '    <relationship>\n'
                for key, value in rel.items():
                    if value is not None:
                        xml_content += f'      <{key}>{self._escape_xml(str(value))}</{key}>\n'
                xml_content += '    </relationship>\n'
            xml_content += '  </relationships>\n'
        
        xml_content += '</aegis_export>'
        
        return {
            'format': 'xml',
            'xml_content': xml_content,
            'asset_count': len(assets),
            'relationship_count': len(relationships) if include_relationships else 0,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def import_assets(
        self, 
        file_content: Union[str, bytes], 
        format: str = 'csv',
        validate_only: bool = False,
        update_existing: bool = False,
        create_categories: bool = True
    ) -> Dict[str, Any]:
        """Import assets from file content"""
        
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
        
        # Parse file content based on format
        if format == 'csv':
            parsed_data = self._parse_csv(file_content)
        elif format == 'json':
            parsed_data = self._parse_json(file_content)
        elif format == 'xlsx':
            parsed_data = self._parse_excel(file_content)
        elif format == 'xml':
            parsed_data = self._parse_xml(file_content)
        
        # Validate data
        validation_result = self._validate_import_data(parsed_data)
        
        if validate_only:
            return validation_result
        
        if not validation_result['is_valid']:
            return validation_result
        
        # Process import
        return self._process_import(parsed_data, update_existing, create_categories)
    
    def _parse_csv(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Parse CSV content"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        csv_file = io.StringIO(content)
        df = pd.read_csv(csv_file)
        
        # Clean up the dataframe
        df = df.fillna('')  # Replace NaN with empty strings
        
        assets = df.to_dict('records')
        
        return {
            'assets': assets,
            'relationships': [],  # CSV typically only contains assets
            'format': 'csv',
            'row_count': len(df)
        }
    
    def _parse_json(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Parse JSON content"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        data = json.loads(content)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Simple list of assets
            return {
                'assets': data,
                'relationships': [],
                'format': 'json',
                'row_count': len(data)
            }
        elif isinstance(data, dict):
            # Structured export
            return {
                'assets': data.get('assets', []),
                'relationships': data.get('relationships', []),
                'format': 'json',
                'row_count': len(data.get('assets', []))
            }
        else:
            raise ValueError("Invalid JSON structure")
    
    def _parse_excel(self, content: bytes) -> Dict[str, Any]:
        """Parse Excel content"""
        excel_file = io.BytesIO(content)
        
        # Read all sheets
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        assets = []
        relationships = []
        
        # Look for assets in 'Assets' sheet or first sheet
        if 'Assets' in excel_data:
            assets_df = excel_data['Assets'].fillna('')
            assets = assets_df.to_dict('records')
        elif len(excel_data) > 0:
            # Use first sheet as assets
            first_sheet = list(excel_data.values())[0].fillna('')
            assets = first_sheet.to_dict('records')
        
        # Look for relationships in 'Relationships' sheet
        if 'Relationships' in excel_data:
            rel_df = excel_data['Relationships'].fillna('')
            relationships = rel_df.to_dict('records')
        
        return {
            'assets': assets,
            'relationships': relationships,
            'format': 'xlsx',
            'row_count': len(assets)
        }
    
    def _parse_xml(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Parse XML content (basic implementation)"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        # Simple XML parsing - in production, use xml.etree.ElementTree or lxml
        assets = []
        relationships = []
        
        # This is a simplified parser - would need proper XML handling in production
        lines = content.split('\n')
        current_asset = {}
        current_relationship = {}
        in_asset = False
        in_relationship = False
        
        for line in lines:
            line = line.strip()
            
            if '<asset>' in line:
                in_asset = True
                current_asset = {}
            elif '</asset>' in line:
                in_asset = False
                if current_asset:
                    assets.append(current_asset)
                current_asset = {}
            elif '<relationship>' in line:
                in_relationship = True
                current_relationship = {}
            elif '</relationship>' in line:
                in_relationship = False
                if current_relationship:
                    relationships.append(current_relationship)
                current_relationship = {}
            elif in_asset and '<' in line and '>' in line and '</' in line:
                # Parse simple XML tag
                tag_start = line.find('<') + 1
                tag_end = line.find('>')
                close_tag_start = line.find('</')
                
                if tag_start < tag_end < close_tag_start:
                    tag_name = line[tag_start:tag_end]
                    value = line[tag_end+1:close_tag_start]
                    current_asset[tag_name] = value
            elif in_relationship and '<' in line and '>' in line and '</' in line:
                # Parse relationship XML tag
                tag_start = line.find('<') + 1
                tag_end = line.find('>')
                close_tag_start = line.find('</')
                
                if tag_start < tag_end < close_tag_start:
                    tag_name = line[tag_start:tag_end]
                    value = line[tag_end+1:close_tag_start]
                    current_relationship[tag_name] = value
        
        return {
            'assets': assets,
            'relationships': relationships,
            'format': 'xml',
            'row_count': len(assets)
        }
    
    def _validate_import_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parsed import data"""
        errors = []
        warnings = []
        valid_assets = []
        
        assets = parsed_data.get('assets', [])
        
        for i, asset_data in enumerate(assets):
            asset_errors = []
            asset_warnings = []
            
            # Required fields validation
            if not asset_data.get('name'):
                asset_errors.append("Missing required field: name")
            
            if not asset_data.get('asset_type'):
                asset_errors.append("Missing required field: asset_type")
            
            # Asset type validation
            valid_asset_types = ['server', 'workstation', 'network_device', 'application', 
                               'database', 'cloud_service', 'mobile_device', 'iot_device', 'other']
            if asset_data.get('asset_type') and asset_data['asset_type'] not in valid_asset_types:
                asset_errors.append(f"Invalid asset_type: {asset_data['asset_type']}")
            
            # Criticality validation
            valid_criticalities = ['low', 'medium', 'high', 'critical']
            if asset_data.get('criticality') and asset_data['criticality'] not in valid_criticalities:
                asset_errors.append(f"Invalid criticality: {asset_data['criticality']}")
            
            # IP address format validation (basic)
            if asset_data.get('ip_address'):
                ip = asset_data['ip_address']
                if not (ip.count('.') == 3 or ':' in ip):  # Basic IPv4/IPv6 check
                    asset_warnings.append(f"IP address format may be invalid: {ip}")
            
            # Duplicate name check
            existing_asset = self.db.query(Asset).filter(
                Asset.name == asset_data.get('name'),
                Asset.is_active == True
            ).first()
            
            if existing_asset:
                asset_warnings.append(f"Asset with name '{asset_data['name']}' already exists (ID: {existing_asset.id})")
            
            if asset_errors:
                errors.append(f"Row {i + 1}: " + "; ".join(asset_errors))
            else:
                valid_assets.append(asset_data)
            
            if asset_warnings:
                warnings.extend([f"Row {i + 1}: " + warning for warning in asset_warnings])
        
        return {
            'is_valid': len(errors) == 0,
            'total_rows': len(assets),
            'valid_rows': len(valid_assets),
            'error_count': len(errors),
            'warning_count': len(warnings),
            'errors': errors,
            'warnings': warnings,
            'valid_assets': valid_assets
        }
    
    def _process_import(
        self, 
        parsed_data: Dict[str, Any], 
        update_existing: bool, 
        create_categories: bool
    ) -> Dict[str, Any]:
        """Process the actual import of validated data"""
        
        success_count = 0
        error_count = 0
        update_count = 0
        created_assets = []
        errors = []
        
        assets = parsed_data.get('assets', [])
        
        # Create categories if needed
        if create_categories:
            self._create_missing_categories(assets)
        
        for i, asset_data in enumerate(assets):
            try:
                # Check if asset exists
                existing_asset = None
                if update_existing and asset_data.get('name'):
                    existing_asset = self.db.query(Asset).filter(
                        Asset.name == asset_data['name'],
                        Asset.is_active == True
                    ).first()
                
                if existing_asset:
                    # Update existing asset
                    self._update_asset_from_data(existing_asset, asset_data)
                    self.db.commit()
                    created_assets.append(existing_asset)
                    update_count += 1
                else:
                    # Create new asset
                    new_asset = self._create_asset_from_data(asset_data)
                    self.db.add(new_asset)
                    self.db.commit()
                    created_assets.append(new_asset)
                    success_count += 1
                    
            except Exception as e:
                error_count += 1
                errors.append(f"Row {i + 1}: {str(e)}")
                self.db.rollback()
        
        return {
            'success': True,
            'total_processed': len(assets),
            'created_count': success_count,
            'updated_count': update_count,
            'error_count': error_count,
            'errors': errors,
            'imported_assets': [self._asset_to_dict(asset) for asset in created_assets]
        }
    
    def _create_missing_categories(self, assets: List[Dict[str, Any]]):
        """Create asset categories that don't exist"""
        category_names = set()
        
        for asset in assets:
            if asset.get('category_name'):
                category_names.add(asset['category_name'])
        
        for category_name in category_names:
            existing = self.db.query(AssetCategory).filter(
                AssetCategory.name == category_name
            ).first()
            
            if not existing:
                new_category = AssetCategory(
                    name=category_name,
                    description=f"Auto-created category: {category_name}",
                    color="#6c757d"  # Default gray color
                )
                self.db.add(new_category)
                self.db.commit()
    
    def _create_asset_from_data(self, asset_data: Dict[str, Any]) -> Asset:
        """Create Asset model instance from dictionary data"""
        
        # Map category name to ID if provided
        category_id = asset_data.get('category_id')
        if asset_data.get('category_name') and not category_id:
            category = self.db.query(AssetCategory).filter(
                AssetCategory.name == asset_data['category_name']
            ).first()
            if category:
                category_id = category.id
        
        # Parse dates
        purchase_date = None
        if asset_data.get('purchase_date'):
            try:
                purchase_date = datetime.fromisoformat(asset_data['purchase_date'].replace('Z', '+00:00'))
            except:
                pass
        
        warranty_expiry = None
        if asset_data.get('warranty_expiry'):
            try:
                warranty_expiry = datetime.fromisoformat(asset_data['warranty_expiry'].replace('Z', '+00:00'))
            except:
                pass
        
        # Create asset
        new_asset = Asset(
            name=asset_data['name'],
            description=asset_data.get('description', ''),
            asset_type=asset_data['asset_type'],
            criticality=asset_data.get('criticality', 'medium'),
            category_id=category_id,
            owner_id=asset_data.get('owner_id'),
            ip_address=asset_data.get('ip_address'),
            hostname=asset_data.get('hostname'),
            operating_system=asset_data.get('operating_system'),
            version=asset_data.get('version'),
            location=asset_data.get('location'),
            environment=asset_data.get('environment'),
            business_unit=asset_data.get('business_unit'),
            cost_center=asset_data.get('cost_center'),
            compliance_scope=asset_data.get('compliance_scope'),
            status=asset_data.get('status', 'active'),
            purchase_date=purchase_date,
            warranty_expiry=warranty_expiry,
            tags=asset_data.get('tags'),
            custom_fields=asset_data.get('custom_fields'),
            created_by=self.user_id
        )
        
        return new_asset
    
    def _update_asset_from_data(self, asset: Asset, asset_data: Dict[str, Any]):
        """Update existing asset with new data"""
        
        # Update fields if provided
        if 'description' in asset_data:
            asset.description = asset_data['description']
        if 'asset_type' in asset_data:
            asset.asset_type = asset_data['asset_type']
        if 'criticality' in asset_data:
            asset.criticality = asset_data['criticality']
        if 'ip_address' in asset_data:
            asset.ip_address = asset_data['ip_address']
        if 'hostname' in asset_data:
            asset.hostname = asset_data['hostname']
        if 'operating_system' in asset_data:
            asset.operating_system = asset_data['operating_system']
        if 'version' in asset_data:
            asset.version = asset_data['version']
        if 'location' in asset_data:
            asset.location = asset_data['location']
        if 'environment' in asset_data:
            asset.environment = asset_data['environment']
        if 'business_unit' in asset_data:
            asset.business_unit = asset_data['business_unit']
        if 'cost_center' in asset_data:
            asset.cost_center = asset_data['cost_center']
        if 'compliance_scope' in asset_data:
            asset.compliance_scope = asset_data['compliance_scope']
        if 'tags' in asset_data:
            asset.tags = asset_data['tags']
        if 'custom_fields' in asset_data:
            asset.custom_fields = asset_data['custom_fields']
    
    def _asset_to_dict(self, asset: Asset) -> Dict[str, Any]:
        """Convert Asset model to dictionary"""
        return {
            'id': asset.id,
            'name': asset.name,
            'description': asset.description,
            'asset_type': asset.asset_type.value,
            'criticality': asset.criticality.value,
            'category_id': asset.category_id,
            'owner_id': asset.owner_id,
            'ip_address': asset.ip_address,
            'hostname': asset.hostname,
            'operating_system': asset.operating_system,
            'version': asset.version,
            'location': asset.location,
            'environment': asset.environment,
            'business_unit': asset.business_unit,
            'status': asset.status,
            'created_at': asset.created_at.isoformat() if asset.created_at else None,
            'updated_at': asset.updated_at.isoformat() if asset.updated_at else None
        }
    
    def generate_template(self, format: str = 'csv', include_relationships: bool = False) -> Dict[str, Any]:
        """Generate import template with sample data"""
        
        sample_assets = [
            {
                'name': 'Example Web Server',
                'description': 'Production web server hosting main application',
                'asset_type': 'server',
                'criticality': 'high',
                'category_name': 'Servers',
                'ip_address': '192.168.1.100',
                'hostname': 'web-prod-01',
                'operating_system': 'Ubuntu 22.04 LTS',
                'version': '22.04.3',
                'location': 'Data Center 1 - Rack A1',
                'environment': 'production',
                'business_unit': 'Engineering',
                'cost_center': 'ENG-001',
                'compliance_scope': '["SOC2", "ISO27001"]',
                'status': 'active',
                'tags': '["web", "production", "critical"]',
                'custom_fields': '{"backup_schedule": "daily", "monitoring_enabled": true}'
            },
            {
                'name': 'Example Database Server',
                'description': 'Primary PostgreSQL database server',
                'asset_type': 'database',
                'criticality': 'critical',
                'category_name': 'Databases',
                'ip_address': '192.168.1.101',
                'hostname': 'db-prod-01',
                'operating_system': 'CentOS 8',
                'version': '8.5',
                'location': 'Data Center 1 - Rack A2',
                'environment': 'production',
                'business_unit': 'Engineering',
                'cost_center': 'ENG-001',
                'compliance_scope': '["SOC2", "ISO27001", "PCI-DSS"]',
                'status': 'active',
                'tags': '["database", "postgresql", "production"]',
                'custom_fields': '{"backup_schedule": "hourly", "encryption_enabled": true}'
            }
        ]
        
        sample_relationships = [
            {
                'source_asset_name': 'Example Web Server',
                'target_asset_name': 'Example Database Server',
                'relationship_type': 'depends_on',
                'relationship_strength': 'critical',
                'description': 'Web server depends on database for data storage',
                'port': '5432',
                'protocol': 'TCP',
                'data_flow_direction': 'source_to_target',
                'impact_percentage': 90.0,
                'recovery_time_minutes': 15
            }
        ] if include_relationships else []
        
        if format == 'csv':
            return self._export_to_csv(sample_assets, sample_relationships, include_relationships)
        elif format == 'json':
            return self._export_to_json(sample_assets, sample_relationships, include_relationships)
        elif format == 'xlsx':
            return self._export_to_excel(sample_assets, sample_relationships, include_relationships)
        elif format == 'xml':
            return self._export_to_xml(sample_assets, sample_relationships, include_relationships)
        else:
            raise ValueError(f"Unsupported template format: {format}")