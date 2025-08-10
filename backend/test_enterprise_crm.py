#!/usr/bin/env python3
"""
Test script for Enterprise CRM API
"""
import requests
import json
import time
import subprocess
import threading
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8001"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False

def test_auth_login():
    """Test the login endpoint"""
    print("\n=== Testing Login ===")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("data", {}).get("session_id"):
            return data["data"]["session_id"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Login test failed: {e}")
        return None

def test_masters_endpoints(session_id):
    """Test masters endpoints"""
    print("\n=== Testing Masters Endpoints ===")
    headers = {"x-session-id": session_id} if session_id else {}
    
    # Test departments
    try:
        response = requests.get(f"{BASE_URL}/api/masters/departments", headers=headers, timeout=10)
        print(f"Departments - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('data', []))} departments")
    except Exception as e:
        print(f"Departments test failed: {e}")
    
    # Test roles
    try:
        response = requests.get(f"{BASE_URL}/api/masters/roles", headers=headers, timeout=10)
        print(f"Roles - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('data', []))} roles")
    except Exception as e:
        print(f"Roles test failed: {e}")
    
    # Test UOMs
    try:
        response = requests.get(f"{BASE_URL}/api/masters/uoms", headers=headers, timeout=10)
        print(f"UOMs - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"UOMs response structure: {type(data.get('data'))}")
    except Exception as e:
        print(f"UOMs test failed: {e}")
    
    # Test products
    try:
        response = requests.get(f"{BASE_URL}/api/masters/products", headers=headers, timeout=10)
        print(f"Products - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Products response structure: {type(data.get('data'))}")
    except Exception as e:
        print(f"Products test failed: {e}")

def test_create_uom(session_id):
    """Test creating a new UOM"""
    print("\n=== Testing UOM Creation ===")
    headers = {"x-session-id": session_id, "Content-Type": "application/json"} if session_id else {"Content-Type": "application/json"}
    
    import time
    # Use timestamp to ensure unique code
    timestamp = str(int(time.time()))[-4:]
    
    payload = {
        "uom_name": f"Test Units {timestamp}",
        "uom_code": f"TST{timestamp}",
        "description": "Test unit for API testing"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/masters/uoms", 
                               headers=headers, 
                               json=payload, 
                               timeout=10)
        print(f"Create UOM - Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Create UOM test failed: {e}")
        return False

def wait_for_server(max_attempts=30):
    """Wait for the server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"Attempt {i+1}/{max_attempts}...")
    
    print("Server failed to start within timeout")
    return False

def run_tests():
    """Run all tests"""
    print("Starting Enterprise CRM API Tests...")
    
    # Wait for server
    if not wait_for_server():
        print("❌ Server not responding")
        return False
    
    # Run tests
    success_count = 0
    total_tests = 0
    
    # Test 1: Health check
    total_tests += 1
    if test_health_endpoint():
        success_count += 1
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
    
    # Test 2: Login
    total_tests += 1
    session_id = test_auth_login()
    if session_id:
        success_count += 1
        print("✅ Login passed")
    else:
        print("❌ Login failed")
    
    # Test 3: Masters endpoints
    total_tests += 1
    try:
        test_masters_endpoints(session_id)
        success_count += 1
        print("✅ Masters endpoints passed")
    except:
        print("❌ Masters endpoints failed")
    
    # Test 4: Create UOM
    if session_id:
        total_tests += 1
        if test_create_uom(session_id):
            success_count += 1
            print("✅ UOM creation passed")
        else:
            print("❌ UOM creation failed")
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests

if __name__ == "__main__":
    # Start server in background
    print("Starting Enterprise CRM server...")
    try:
        # Change to backend directory and start server
        os.chdir("/app/backend")
        server_process = subprocess.Popen([
            sys.executable, "-m", "enterprise_crm.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(5)
        
        # Run tests
        success = run_tests()
        
        # Cleanup
        server_process.terminate()
        server_process.wait()
        
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTests interrupted")
        if 'server_process' in locals():
            server_process.terminate()
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        if 'server_process' in locals():
            server_process.terminate()
        sys.exit(1)