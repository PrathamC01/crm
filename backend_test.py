#!/usr/bin/env python3
"""
Backend API Testing for CRM JWT Authentication System
Tests all API endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime

class CRMAPITester:
    def __init__(self, base_url="http://10.60.90.76:8000"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")

    def test_health_check(self):
        """Test GET / endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Health Check", True, f"Status: {response.status_code}, Message: {data.get('message')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Status field not True: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_login_with_email(self):
        """Test login with email"""
        try:
            login_data = {
                "email_or_username": "admin@crm.com",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True and "token" in data.get("data", {}):
                    self.token = data["data"]["token"]
                    self.log_test("Login with Email", True, f"Token received: {self.token[:20]}...")
                    return True
                else:
                    self.log_test("Login with Email", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Login with Email", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login with Email", False, f"Exception: {str(e)}")
            return False

    def test_login_with_username(self):
        """Test login with username"""
        try:
            login_data = {
                "email_or_username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True and "token" in data.get("data", {}):
                    # Update token for subsequent tests
                    self.token = data["data"]["token"]
                    self.log_test("Login with Username", True, f"Token received: {self.token[:20]}...")
                    return True
                else:
                    self.log_test("Login with Username", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Login with Username", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login with Username", False, f"Exception: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            login_data = {
                "email_or_username": "invalid@test.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                data = response.json()
                if data.get("status") is False:
                    self.log_test("Invalid Login", True, f"Correctly rejected with 401: {data.get('message')}")
                    return True
                else:
                    self.log_test("Invalid Login", False, f"Status should be False: {data}")
                    return False
            else:
                self.log_test("Invalid Login", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Login", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_access(self):
        """Test protected dashboard endpoint"""
        if not self.token:
            self.log_test("Dashboard Access", False, "No token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True and "data" in data:
                    user_data = data["data"]
                    required_fields = ["id", "name", "email", "username", "role", "department", "is_active"]
                    
                    missing_fields = [field for field in required_fields if field not in user_data]
                    if not missing_fields:
                        self.log_test("Dashboard Access", True, f"User data: {user_data['name']} ({user_data['email']})")
                        return True
                    else:
                        self.log_test("Dashboard Access", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Dashboard Access", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Dashboard Access", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Access", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_without_token(self):
        """Test dashboard access without token"""
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard")
            
            if response.status_code == 403:  # FastAPI HTTPBearer returns 403 for missing token
                self.log_test("Dashboard Without Token", True, "Correctly rejected access without token")
                return True
            elif response.status_code == 401:  # Some configurations might return 401
                self.log_test("Dashboard Without Token", True, "Correctly rejected access without token (401)")
                return True
            else:
                self.log_test("Dashboard Without Token", False, f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Without Token", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_with_invalid_token(self):
        """Test dashboard access with invalid token"""
        try:
            headers = {
                "Authorization": "Bearer invalid_token_here",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/dashboard", headers=headers)
            
            if response.status_code == 401:
                self.log_test("Dashboard Invalid Token", True, "Correctly rejected invalid token")
                return True
            else:
                self.log_test("Dashboard Invalid Token", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Invalid Token", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting CRM API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 50)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_login_with_email,
            self.test_login_with_username,
            self.test_invalid_login,
            self.test_dashboard_access,
            self.test_dashboard_without_token,
            self.test_dashboard_with_invalid_token
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    """Main test runner"""
    # Try to determine the correct backend URL
    backend_url = "http://localhost:8001"
    
    # Check if we can read the frontend .env to get the backend URL
    try:
        with open("/app/frontend/.env", "r") as f:
            for line in f:
                if line.startswith("VITE_BACKEND_URL="):
                    backend_url = line.split("=", 1)[1].strip()
                    break
    except:
        pass
    
    print(f"🔧 Using backend URL: {backend_url}")
    
    tester = CRMAPITester(backend_url)
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())