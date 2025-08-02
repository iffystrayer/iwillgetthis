#!/usr/bin/env python3
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
