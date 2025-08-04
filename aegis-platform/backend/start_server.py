#!/usr/bin/env python3
"""
Start Aegis Platform Development Server
Simple script to launch the platform for manual testing
"""

import uvicorn
import sys
import os
from pathlib import Path

def start_development_server():
    """Start the development server with optimal settings for manual testing"""
    
    print("🚀 Starting Aegis Risk Management Platform...")
    print("="*60)
    
    # Server configuration
    config = {
        "app": "main_minimal:app",  # Use minimal version for testing
        "host": "127.0.0.1",
        "port": 30641,  # Random port to avoid conflicts
        "reload": True,  # Auto-reload on file changes
        "log_level": "info",
        "access_log": True,
        "reload_dirs": ["."],  # Watch current directory
    }
    
    print(f"🌐 Server URL: http://{config['host']}:{config['port']}")
    print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
    print(f"📖 ReDoc Documentation: http://{config['host']}:{config['port']}/redoc")
    print(f"🔍 OpenAPI Spec: http://{config['host']}:{config['port']}/openapi.json")
    print("="*60)
    print("✅ Server starting... Press CTRL+C to stop")
    print()
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("main_minimal.py").exists():
        print("❌ Error: main_minimal.py not found in current directory")
        print("Please run this script from the backend directory")
        sys.exit(1)
    
    start_development_server()