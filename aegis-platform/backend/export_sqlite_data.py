#!/usr/bin/env python3
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
