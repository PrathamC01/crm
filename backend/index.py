"""
Root application entry point
"""
import sys
import os

# Add the crm package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crm'))

try:
    from app.main import app
except ImportError:
    print("Failed to import app.main, trying alternative import...")
    import app.main as main_module
    app = main_module.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
