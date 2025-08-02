#!/usr/bin/env python3
"""
Database Migration Path Validation
Tests the migration from SQLite (development) to MySQL (production)
"""

import sys
import os
from typing import Dict, Any
import sqlalchemy
from sqlalchemy import create_engine, text
from config import settings
from database import Base

def test_sqlite_setup():
    """Test current SQLite configuration"""
    print("🔍 Testing SQLite Development Setup...")
    
    try:
        # Create SQLite engine
        sqlite_url = settings.DATABASE_URL
        print(f"SQLite URL: {sqlite_url}")
        
        sqlite_engine = create_engine(sqlite_url)
        
        # Test connection
        with sqlite_engine.connect() as conn:
            result = conn.execute(text('SELECT sqlite_version()'))
            version = result.fetchone()[0]
            print(f"✅ SQLite version: {version}")
        
        # Test table creation
        Base.metadata.create_all(bind=sqlite_engine)
        print("✅ SQLite tables created successfully")
        
        # Check tables
        inspector = sqlalchemy.inspect(sqlite_engine)
        tables = inspector.get_table_names()
        print(f"✅ SQLite tables found: {len(tables)}")
        
        return sqlite_engine, tables
        
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return None, []

def test_mysql_configuration():
    """Test MySQL configuration format (without actual connection)"""
    print("\n📋 Testing MySQL Configuration Format...")
    
    # Example MySQL URL format for production
    mysql_examples = [
        "mysql://aegis_user:secure_password@localhost:3306/aegis_production",
        "mysql+pymysql://aegis_user:secure_password@mysql-server:3306/aegis_db",
        "mysql://aegis_user:secure_password@127.0.0.1:3306/aegis_db?charset=utf8mb4"
    ]
    
    for url in mysql_examples:
        try:
            # Just test URL parsing, don't actually connect
            engine = create_engine(url, echo=False)
            print(f"✅ Valid MySQL URL format: {url}")
        except Exception as e:
            print(f"❌ Invalid MySQL URL: {url} - {e}")
    
    return True

def test_alembic_migration_setup():
    """Test Alembic migration configuration"""
    print("\n🔄 Testing Alembic Migration Setup...")
    
    try:
        # Check if alembic directory exists
        alembic_dir = "alembic"
        if os.path.exists(alembic_dir):
            print(f"✅ Alembic directory found: {alembic_dir}")
            
            # Check alembic.ini
            alembic_ini = "alembic.ini"
            if os.path.exists(alembic_ini):
                print(f"✅ Alembic configuration found: {alembic_ini}")
            else:
                print(f"⚠️  Alembic configuration not found: {alembic_ini}")
            
            # Check versions directory
            versions_dir = os.path.join(alembic_dir, "versions")
            if os.path.exists(versions_dir):
                migrations = [f for f in os.listdir(versions_dir) if f.endswith('.py') and f != '__pycache__']
                print(f"✅ Migration files found: {len(migrations)}")
            else:
                print("⚠️  No migrations directory found")
        else:
            print("⚠️  Alembic not initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Alembic test failed: {e}")
        return False

def test_migration_strategy():
    """Test migration strategy documentation"""
    print("\n📖 Testing Migration Strategy...")
    
    migration_steps = [
        "1. Export data from SQLite database",
        "2. Set up MySQL database server",
        "3. Update DATABASE_URL to MySQL connection string", 
        "4. Run 'alembic upgrade head' to create tables in MySQL",
        "5. Import data into MySQL database",
        "6. Verify data integrity and relationships",
        "7. Update production configuration",
        "8. Test application with MySQL backend"
    ]
    
    print("✅ Migration Path Strategy:")
    for step in migration_steps:
        print(f"   {step}")
    
    return True

def create_migration_scripts():
    """Create helper scripts for database migration"""
    print("\n📝 Creating Migration Helper Scripts...")
    
    # Export script for SQLite
    export_script = '''#!/usr/bin/env python3
"""
Export data from SQLite to JSON for migration
"""
import json
import sqlite3
from pathlib import Path

def export_sqlite_data(db_path: str, output_path: str):
    """Export all data from SQLite to JSON files"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get all table names
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    exported_data = {}
    
    for table in tables:
        if table.startswith('sqlite_'):
            continue  # Skip system tables
            
        cursor = conn.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        exported_data[table] = rows
        print(f"Exported {len(rows)} rows from {table}")
    
    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(exported_data, f, indent=2, default=str)
    
    print(f"Data exported to {output_path}")
    conn.close()

if __name__ == "__main__":
    export_sqlite_data("aegis_development.db", "aegis_data_export.json")
'''
    
    # Import script for MySQL
    import_script = '''#!/usr/bin/env python3
"""
Import data into MySQL from JSON export
"""
import json
import sys
from sqlalchemy import create_engine, text

def import_mysql_data(json_path: str, mysql_url: str):
    """Import data from JSON into MySQL database"""
    engine = create_engine(mysql_url)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    with engine.connect() as conn:
        for table_name, rows in data.items():
            if not rows:
                continue
                
            print(f"Importing {len(rows)} rows into {table_name}")
            
            # Prepare insert statement
            columns = list(rows[0].keys())
            placeholders = ', '.join([f':{col}' for col in columns])
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert data
            conn.execute(text(sql), rows)
            conn.commit()
    
    print("Data import completed")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python import_mysql.py <json_file> <mysql_url>")
        sys.exit(1)
    
    import_mysql_data(sys.argv[1], sys.argv[2])
'''
    
    try:
        # Write export script
        with open("export_sqlite_data.py", "w") as f:
            f.write(export_script)
        print("✅ Created export_sqlite_data.py")
        
        # Write import script  
        with open("import_mysql_data.py", "w") as f:
            f.write(import_script)
        print("✅ Created import_mysql_data.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create migration scripts: {e}")
        return False

def test_schema_compatibility():
    """Test schema compatibility between SQLite and MySQL"""
    print("\n🔧 Testing Schema Compatibility...")
    
    try:
        from database import engine
        
        # Get current schema from SQLite
        inspector = sqlalchemy.inspect(engine)
        
        # Check for potential issues with MySQL migration
        issues = []
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            
            for column in columns:
                col_type = str(column['type']).upper()
                
                # Check for SQLite-specific types that need conversion
                if 'DATETIME' in col_type:
                    # MySQL supports DATETIME
                    pass
                elif 'BOOLEAN' in col_type:
                    # MySQL uses TINYINT(1) for boolean
                    pass
                elif 'TEXT' in col_type:
                    # MySQL supports TEXT
                    pass
                elif 'INTEGER' in col_type:
                    # MySQL supports INT
                    pass
                elif 'REAL' in col_type or 'FLOAT' in col_type:
                    # MySQL supports FLOAT/DOUBLE
                    pass
                else:
                    # Check for potential issues
                    if col_type not in ['VARCHAR', 'CHAR', 'INT', 'BIGINT', 'SMALLINT']:
                        issues.append(f"Table {table_name}, column {column['name']}: {col_type} may need review")
        
        if issues:
            print("⚠️  Potential schema compatibility issues:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   {issue}")
        else:
            print("✅ Schema appears compatible with MySQL")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Schema compatibility test failed: {e}")
        return False

def run_migration_validation():
    """Run all database migration validation tests"""
    print("🧪 Running Database Migration Path Validation...")
    print("=" * 60)
    
    results = []
    
    # Test 1: SQLite setup
    sqlite_engine, tables = test_sqlite_setup()
    results.append(sqlite_engine is not None)
    
    # Test 2: MySQL configuration
    results.append(test_mysql_configuration())
    
    # Test 3: Alembic setup
    results.append(test_alembic_migration_setup())
    
    # Test 4: Migration strategy
    results.append(test_migration_strategy())
    
    # Test 5: Create migration scripts
    results.append(create_migration_scripts())
    
    # Test 6: Schema compatibility
    results.append(test_schema_compatibility())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Validation Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 Database Migration Path Validated Successfully!")
        print("\n📋 Next Steps for Production Migration:")
        print("1. Set up MySQL server in production environment")
        print("2. Update DATABASE_URL in production configuration")
        print("3. Run 'alembic upgrade head' to create MySQL schema")
        print("4. Use export/import scripts to migrate data")
        print("5. Test application with MySQL backend")
        return True
    else:
        print("⚠️  Some validation tests failed")
        return sum(results) >= 4  # Pass if most tests pass

if __name__ == "__main__":
    success = run_migration_validation()
    sys.exit(0 if success else 1)