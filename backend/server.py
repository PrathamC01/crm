"""
Backend server entry point for supervisor
"""
import sys
import os

# Add the crm package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crm'))

try:
    from app.main import app
except ImportError as e:
    print(f"Failed to import app.main: {e}")
    import app.main as main_module
    app = main_module.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)