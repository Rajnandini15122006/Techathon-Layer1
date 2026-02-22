"""
Simple server startup script with better error handling
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("Starting PuneRakshak Server")
print("="*70)

try:
    import uvicorn
    from app.main import app
    
    print("\n✓ Imports successful")
    print("\nStarting server at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
