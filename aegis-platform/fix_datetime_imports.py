#!/usr/bin/env python3
"""
Fix datetime import issues across the entire backend codebase
"""

import os
import re
import sys

def fix_datetime_imports(backend_path):
    """
    Find all Python files using datetime without import and add the import
    """
    files_fixed = 0
    errors = []
    
    for root, dirs, files in os.walk(backend_path):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['__pycache__', '.git', 'venv', 'node_modules', 'test_env', 'site-packages']):
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file uses datetime.* without import
                if re.search(r'\bdatetime\.(now|utcnow|fromisoformat)', content):
                    # Check if datetime is already imported
                    has_datetime_import = (
                        'from datetime import' in content or
                        'import datetime' in content
                    )
                    
                    if not has_datetime_import:
                        print(f"Fixing {file_path}")
                        
                        # Find the right place to add the import
                        lines = content.split('\n')
                        insert_position = 0
                        
                        # Find the last import statement
                        for i, line in enumerate(lines):
                            if line.startswith('from ') or line.startswith('import '):
                                insert_position = i + 1
                        
                        # Insert the datetime import
                        lines.insert(insert_position, 'from datetime import datetime')
                        
                        # Write back the fixed content
                        fixed_content = '\n'.join(lines)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        files_fixed += 1
                
            except Exception as e:
                errors.append(f"Error processing {file_path}: {e}")
    
    print(f"\n✅ Fixed {files_fixed} files")
    if errors:
        print(f"❌ Errors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    return files_fixed, errors

if __name__ == "__main__":
    backend_path = "/Users/ifiokmoses/code/iwillgetthis/aegis-platform/backend"
    
    if not os.path.exists(backend_path):
        print(f"❌ Backend path not found: {backend_path}")
        sys.exit(1)
    
    print("🔧 Fixing datetime imports across backend codebase...")
    files_fixed, errors = fix_datetime_imports(backend_path)
    
    if files_fixed > 0:
        print(f"\n🚀 Recommendation: Rebuild the backend container to apply fixes")
        print("   docker-compose -f docker/docker-compose.yml build backend")
        print("   docker-compose -f docker/docker-compose.yml up -d backend")
    
    sys.exit(0 if not errors else 1)