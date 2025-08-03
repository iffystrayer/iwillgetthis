"""
Test suite for Asset Import/Export System
"""

import pytest
import pandas as pd
import json
import io
from unittest.mock import Mock, MagicMock, patch
from asset_import_export import AssetImportExportManager


class TestAssetImportExportManager:
    """Test cases for AssetImportExportManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.user_id = 1
        self.manager = AssetImportExportManager(self.mock_db, self.user_id)

    def test_manager_initialization(self):
        """Test that manager initializes correctly"""
        assert self.manager.db == self.mock_db
        assert self.manager.user_id == self.user_id
        assert len(self.manager.supported_formats) == 4
        assert 'csv' in self.manager.supported_formats
        assert 'json' in self.manager.supported_formats

    def test_export_unsupported_format(self):
        """Test export with unsupported format raises error"""
        with pytest.raises(ValueError, match="Unsupported format"):
            self.manager.export_assets(format='unsupported')

    def test_export_csv_format(self):
        """Test CSV export functionality"""
        # Mock assets
        mock_assets = [
            Mock(
                id=1, name="Test Server", description="Test description",
                asset_type=Mock(value="server"), criticality=Mock(value="high"),
                category_id=1, owner_id=1, ip_address="192.168.1.100",
                hostname="test-server", operating_system="Ubuntu",
                version="20.04", location="DC1", environment="production",
                business_unit="IT", cost_center="IT-001", compliance_scope='["SOC2"]',
                status="active", purchase_date=None, warranty_expiry=None,
                last_scan_date=None, tags='["server"]', custom_fields='{}',
                created_at=Mock(isoformat=Mock(return_value="2024-01-01T00:00:00")),
                updated_at=None, category=None, owner=None
            )
        ]
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_assets
        self.mock_db.query.return_value = mock_query
        
        result = self.manager.export_assets(format='csv')
        
        assert result['format'] == 'csv'
        assert 'assets_csv' in result
        assert result['asset_count'] == 1
        assert 'generated_at' in result

    def test_export_json_format(self):
        """Test JSON export functionality"""
        # Mock assets
        mock_assets = [
            Mock(
                id=1, name="Test Server", description="Test description",
                asset_type=Mock(value="server"), criticality=Mock(value="high"),
                category_id=1, owner_id=1, ip_address="192.168.1.100",
                hostname="test-server", operating_system="Ubuntu",
                version="20.04", location="DC1", environment="production",
                business_unit="IT", cost_center="IT-001", compliance_scope='["SOC2"]',
                status="active", purchase_date=None, warranty_expiry=None,
                last_scan_date=None, tags='["server"]', custom_fields='{}',
                created_at=Mock(isoformat=Mock(return_value="2024-01-01T00:00:00")),
                updated_at=None, category=None, owner=None
            )
        ]
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_assets
        self.mock_db.query.return_value = mock_query
        
        result = self.manager.export_assets(format='json')
        
        assert result['format'] == 'json'
        assert 'export_metadata' in result
        assert 'assets' in result
        assert len(result['assets']) == 1
        assert result['export_metadata']['asset_count'] == 1

    def test_export_with_relationships(self):
        """Test export including relationships"""
        # Mock assets
        mock_assets = [Mock(id=1, name="Test Server", asset_type=Mock(value="server"))]
        
        # Mock relationships
        mock_relationships = [
            Mock(
                id=1, source_asset_id=1, target_asset_id=2,
                relationship_type=Mock(value="depends_on"),
                relationship_strength=Mock(value="critical"),
                description="Test dependency", port="80", protocol="HTTP",
                data_flow_direction="bidirectional", impact_percentage=90.0,
                recovery_time_minutes=30, is_validated=True,
                discovered_method="manual",
                created_at=Mock(isoformat=Mock(return_value="2024-01-01T00:00:00"))
            )
        ]
        
        # Mock database queries
        self.mock_db.query.side_effect = [
            Mock(filter=Mock(return_value=Mock(all=Mock(return_value=mock_assets)))),
            Mock(filter=Mock(return_value=Mock(all=Mock(return_value=mock_relationships))))
        ]
        
        result = self.manager.export_assets(format='json', include_relationships=True)
        
        assert 'relationships' in result
        assert len(result['relationships']) == 1

    def test_parse_csv_content(self):
        """Test CSV parsing functionality"""
        csv_content = """name,asset_type,criticality
Test Server,server,high
Test Database,database,critical"""
        
        result = self.manager._parse_csv(csv_content)
        
        assert result['format'] == 'csv'
        assert len(result['assets']) == 2
        assert result['assets'][0]['name'] == 'Test Server'
        assert result['assets'][1]['asset_type'] == 'database'

    def test_parse_json_content_list(self):
        """Test JSON parsing with list format"""
        json_content = json.dumps([
            {"name": "Test Server", "asset_type": "server"},
            {"name": "Test Database", "asset_type": "database"}
        ])
        
        result = self.manager._parse_json(json_content)
        
        assert result['format'] == 'json'
        assert len(result['assets']) == 2
        assert result['assets'][0]['name'] == 'Test Server'

    def test_parse_json_content_structured(self):
        """Test JSON parsing with structured format"""
        json_content = json.dumps({
            "assets": [
                {"name": "Test Server", "asset_type": "server"}
            ],
            "relationships": [
                {"source_asset_id": 1, "target_asset_id": 2}
            ]
        })
        
        result = self.manager._parse_json(json_content)
        
        assert result['format'] == 'json'
        assert len(result['assets']) == 1
        assert len(result['relationships']) == 1

    def test_validate_import_data_valid(self):
        """Test validation with valid data"""
        valid_data = {
            'assets': [
                {
                    'name': 'Valid Server',
                    'asset_type': 'server',
                    'criticality': 'high',
                    'ip_address': '192.168.1.100'
                }
            ]
        }
        
        # Mock database query for duplicate check
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.manager._validate_import_data(valid_data)
        
        assert result['is_valid'] is True
        assert result['total_rows'] == 1
        assert result['valid_rows'] == 1
        assert result['error_count'] == 0

    def test_validate_import_data_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_data = {
            'assets': [
                {
                    'description': 'Missing name and asset_type'
                }
            ]
        }
        
        result = self.manager._validate_import_data(invalid_data)
        
        assert result['is_valid'] is False
        assert result['error_count'] == 1
        assert 'Missing required field: name' in result['errors'][0]
        assert 'Missing required field: asset_type' in result['errors'][0]

    def test_validate_import_data_invalid_values(self):
        """Test validation with invalid field values"""
        invalid_data = {
            'assets': [
                {
                    'name': 'Test Server',
                    'asset_type': 'invalid_type',
                    'criticality': 'invalid_criticality'
                }
            ]
        }
        
        result = self.manager._validate_import_data(invalid_data)
        
        assert result['is_valid'] is False
        assert 'Invalid asset_type' in result['errors'][0]
        assert 'Invalid criticality' in result['errors'][0]

    def test_validate_import_data_duplicate_warning(self):
        """Test validation generates warning for duplicates"""
        data = {
            'assets': [
                {
                    'name': 'Existing Server',
                    'asset_type': 'server',
                    'criticality': 'high'
                }
            ]
        }
        
        # Mock existing asset
        mock_existing = Mock(id=1, name='Existing Server')
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        
        result = self.manager._validate_import_data(data)
        
        assert result['is_valid'] is True
        assert result['warning_count'] == 1
        assert 'already exists' in result['warnings'][0]

    def test_create_asset_from_data(self):
        """Test asset creation from dictionary data"""
        asset_data = {
            'name': 'Test Server',
            'description': 'Test description',
            'asset_type': 'server',
            'criticality': 'high',
            'ip_address': '192.168.1.100',
            'hostname': 'test-server',
            'environment': 'production'
        }
        
        # Mock category lookup
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('asset_import_export.Asset') as MockAsset:
            asset = self.manager._create_asset_from_data(asset_data)
            
            MockAsset.assert_called_once()
            call_args = MockAsset.call_args[1]
            assert call_args['name'] == 'Test Server'
            assert call_args['asset_type'] == 'server'
            assert call_args['created_by'] == self.user_id

    def test_create_missing_categories(self):
        """Test creation of missing categories"""
        assets = [
            {'category_name': 'New Category 1'},
            {'category_name': 'New Category 2'},
            {'category_name': 'Existing Category'}
        ]
        
        # Mock existing category
        mock_existing = Mock()
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            None, None, mock_existing  # First two don't exist, third exists
        ]
        
        with patch('asset_import_export.AssetCategory') as MockCategory:
            self.manager._create_missing_categories(assets)
            
            # Should create 2 new categories
            assert MockCategory.call_count == 2

    def test_update_asset_from_data(self):
        """Test updating existing asset with new data"""
        mock_asset = Mock()
        update_data = {
            'description': 'Updated description',
            'environment': 'staging',
            'criticality': 'medium'
        }
        
        self.manager._update_asset_from_data(mock_asset, update_data)
        
        assert mock_asset.description == 'Updated description'
        assert mock_asset.environment == 'staging'
        assert mock_asset.criticality == 'medium'

    def test_generate_template_csv(self):
        """Test CSV template generation"""
        result = self.manager.generate_template(format='csv')
        
        assert result['format'] == 'csv'
        assert 'assets_csv' in result
        assert result['asset_count'] == 2  # Sample data has 2 assets

    def test_generate_template_json(self):
        """Test JSON template generation"""
        result = self.manager.generate_template(format='json')
        
        assert result['format'] == 'json'
        assert 'assets' in result
        assert len(result['assets']) == 2

    def test_generate_template_with_relationships(self):
        """Test template generation including relationships"""
        result = self.manager.generate_template(format='json', include_relationships=True)
        
        assert 'relationships' in result
        assert len(result['relationships']) == 1

    def test_escape_xml(self):
        """Test XML character escaping"""
        test_string = 'Test & "quotes" <tags> and \'apostrophes\''
        escaped = self.manager._escape_xml(test_string)
        
        assert '&amp;' in escaped
        assert '&quot;' in escaped
        assert '&lt;' in escaped
        assert '&gt;' in escaped
        assert '&apos;' in escaped

    def test_asset_to_dict(self):
        """Test asset model to dictionary conversion"""
        mock_asset = Mock(
            id=1, name="Test Server", description="Test description",
            asset_type=Mock(value="server"), criticality=Mock(value="high"),
            category_id=1, owner_id=1, ip_address="192.168.1.100",
            hostname="test-server", operating_system="Ubuntu",
            version="20.04", location="DC1", environment="production",
            business_unit="IT", status="active",
            created_at=Mock(isoformat=Mock(return_value="2024-01-01T00:00:00")),
            updated_at=None
        )
        
        result = self.manager._asset_to_dict(mock_asset)
        
        assert result['id'] == 1
        assert result['name'] == "Test Server"
        assert result['asset_type'] == "server"
        assert result['criticality'] == "high"

    def test_import_unsupported_format(self):
        """Test import with unsupported format raises error"""
        with pytest.raises(ValueError, match="Unsupported format"):
            self.manager.import_assets("test content", format='unsupported')


class TestImportExportIntegration:
    """Integration tests for import/export workflows"""

    def setup_method(self):
        """Set up integration test fixtures"""
        self.mock_db = Mock()
        self.user_id = 1
        self.manager = AssetImportExportManager(self.mock_db, self.user_id)

    def test_full_csv_import_workflow(self):
        """Test complete CSV import workflow"""
        csv_content = """name,asset_type,criticality,environment
Test Server 1,server,high,production
Test Server 2,server,medium,staging"""
        
        # Mock database interactions
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('asset_import_export.Asset') as MockAsset:
            result = self.manager.import_assets(csv_content, format='csv')
            
            assert result['success'] is True
            assert result['total_processed'] == 2

    def test_validation_only_workflow(self):
        """Test validation-only import workflow"""
        csv_content = """name,asset_type,criticality
Valid Server,server,high
Invalid Server,invalid_type,invalid_criticality"""
        
        result = self.manager.import_assets(csv_content, format='csv', validate_only=True)
        
        assert 'is_valid' in result
        assert result['total_rows'] == 2

    def test_export_import_roundtrip(self):
        """Test export-import roundtrip workflow"""
        # Mock export data
        mock_assets = [
            Mock(
                id=1, name="Test Server", description="Test",
                asset_type=Mock(value="server"), criticality=Mock(value="high"),
                category_id=None, owner_id=None, ip_address=None,
                hostname=None, operating_system=None, version=None,
                location=None, environment="production", business_unit=None,
                cost_center=None, compliance_scope=None, status="active",
                purchase_date=None, warranty_expiry=None, last_scan_date=None,
                tags=None, custom_fields=None,
                created_at=Mock(isoformat=Mock(return_value="2024-01-01T00:00:00")),
                updated_at=None, category=None, owner=None
            )
        ]
        
        # Mock export
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_assets
        self.mock_db.query.return_value = mock_query
        
        # Export to JSON
        export_result = self.manager.export_assets(format='json')
        
        # Re-import the exported data
        export_json = json.dumps(export_result)
        
        with patch('asset_import_export.Asset'):
            import_result = self.manager.import_assets(export_json, format='json')
            
            assert import_result['success'] is True


if __name__ == "__main__":
    # Run basic functionality tests
    print("Running Asset Import/Export Tests...")
    
    # Test 1: Manager initialization
    mock_db = Mock()
    manager = AssetImportExportManager(mock_db, 1)
    print("✓ AssetImportExportManager initialized successfully")
    
    # Test 2: CSV parsing
    csv_content = "name,asset_type\nTest Server,server\nTest Database,database"
    result = manager._parse_csv(csv_content)
    assert len(result['assets']) == 2
    print("✓ CSV parsing working correctly")
    
    # Test 3: JSON parsing
    json_content = json.dumps([{"name": "Test", "asset_type": "server"}])
    result = manager._parse_json(json_content)
    assert len(result['assets']) == 1
    print("✓ JSON parsing working correctly")
    
    # Test 4: Data validation
    valid_data = {
        'assets': [{'name': 'Valid Server', 'asset_type': 'server'}]
    }
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = manager._validate_import_data(valid_data)
    assert result['is_valid'] is True
    print("✓ Data validation working correctly")
    
    # Test 5: Template generation
    template = manager.generate_template('csv')
    assert template['format'] == 'csv'
    print("✓ Template generation working correctly")
    
    # Test 6: XML escaping
    escaped = manager._escape_xml('Test & <tags>')
    assert '&amp;' in escaped and '&lt;' in escaped
    print("✓ XML escaping working correctly")
    
    print("\n🎉 All basic tests passed! Asset import/export system is working correctly.")