"""
Server entry point for supervisor
"""
import sys
import os

# Add the crm package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crm'))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)