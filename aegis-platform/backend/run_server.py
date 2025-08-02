#!/usr/bin/env python3
"""
Direct server runner for debugging uvicorn import issues
"""

import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Aegis Backend Server...")
    print(f"Python path: {sys.path[:3]}...")
    
    try:
        # Import the app to verify it works
        from main import app
        print("✅ Successfully imported FastAPI app")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to avoid subprocess issues
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
