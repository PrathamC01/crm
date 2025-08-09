#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for CRM System
Tests all API endpoints and functionality including the reported issues
"""

import requests
import sys
import json
from datetime import datetime

class CRMAPITester:
    def __init__(self, base_url="http://10.60.90.76:8000"):
        self.base_url = base_url
        self.admin_token = None
        self.sales_token = None
        self.reviewer_token = None
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
        
        if details and success:
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

    def test_admin_login(self):
        """Test admin login"""
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
                    self.admin_token = data["data"]["token"]
                    self.log_test("Admin Login", True, f"Token received: {self.admin_token[:20]}...")
                    return True
                else:
                    self.log_test("Admin Login", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Admin Login", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_sales_login(self):
        """Test sales user login"""
        try:
            login_data = {
                "email_or_username": "sales",
                "password": "sales123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True and "token" in data.get("data", {}):
                    self.sales_token = data["data"]["token"]
                    self.log_test("Sales Login", True, f"Token received: {self.sales_token[:20]}...")
                    return True
                else:
                    self.log_test("Sales Login", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Sales Login", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Sales Login", False, f"Exception: {str(e)}")
            return False

    def test_reviewer_login(self):
        """Test reviewer user login"""
        try:
            login_data = {
                "email_or_username": "reviewer",
                "password": "reviewer123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True and "token" in data.get("data", {}):
                    self.reviewer_token = data["data"]["token"]
                    self.log_test("Reviewer Login", True, f"Token received: {self.reviewer_token[:20]}...")
                    return True
                else:
                    self.log_test("Reviewer Login", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Reviewer Login", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Reviewer Login", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_access(self):
        """Test protected dashboard endpoint"""
        if not self.admin_token:
            self.log_test("Dashboard Access", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
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

    def test_company_creation_with_valid_gst(self):
        """Test company creation with valid GST format"""
        if not self.admin_token:
            self.log_test("Company Creation (Valid GST)", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            company_data = {
                "name": "Test Company Ltd",
                "gst_number": "22AAAAA0000A1Z5",  # Valid GST format
                "pan_number": "AAAAA0000A",       # Valid PAN format
                "industry_category": "Technology",
                "address": "123 Test Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400001",
                "website": "https://testcompany.com",
                "description": "Test company for API testing"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/companies/",
                json=company_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Company Creation (Valid GST)", True, f"Company created successfully")
                    return True
                else:
                    self.log_test("Company Creation (Valid GST)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Creation (Valid GST)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Creation (Valid GST)", False, f"Exception: {str(e)}")
            return False

    def test_company_listing_admin(self):
        """Test company listing with admin user"""
        if not self.admin_token:
            self.log_test("Company Listing (Admin)", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/companies/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Company Listing (Admin)", True, f"Companies retrieved successfully")
                    return True
                else:
                    self.log_test("Company Listing (Admin)", False, f"Response: {data}")
                    return False
            elif response.status_code == 500:
                self.log_test("Company Listing (Admin)", False, f"500 Internal Server Error - likely GST validation issue: {response.text}")
                return False
            else:
                self.log_test("Company Listing (Admin)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Listing (Admin)", False, f"Exception: {str(e)}")
            return False

    def test_leads_access_sales_user(self):
        """Test leads access with sales user - this should work"""
        if not self.sales_token:
            self.log_test("Leads Access (Sales User)", False, "No sales token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.sales_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/leads/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Leads Access (Sales User)", True, f"Leads retrieved successfully")
                    return True
                else:
                    self.log_test("Leads Access (Sales User)", False, f"Response: {data}")
                    return False
            elif response.status_code == 403:
                self.log_test("Leads Access (Sales User)", False, f"403 Forbidden - Role-based access control issue: {response.text}")
                return False
            else:
                self.log_test("Leads Access (Sales User)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Leads Access (Sales User)", False, f"Exception: {str(e)}")
            return False

    def test_contacts_listing(self):
        """Test contacts listing"""
        if not self.admin_token:
            self.log_test("Contacts Listing", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/contacts/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Contacts Listing", True, f"Contacts retrieved successfully")
                    return True
                else:
                    self.log_test("Contacts Listing", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Contacts Listing", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Contacts Listing", False, f"Exception: {str(e)}")
            return False

    def test_opportunities_listing(self):
        """Test opportunities listing"""
        if not self.admin_token:
            self.log_test("Opportunities Listing", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/opportunities/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Opportunities Listing", True, f"Opportunities retrieved successfully")
                    return True
                else:
                    self.log_test("Opportunities Listing", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Opportunities Listing", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Opportunities Listing", False, f"Exception: {str(e)}")
            return False

    def test_users_listing(self):
        """Test users listing"""
        if not self.admin_token:
            self.log_test("Users Listing", False, "No admin token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.base_url}/api/users/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Users Listing", True, f"Users retrieved successfully")
                    return True
                else:
                    self.log_test("Users Listing", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Users Listing", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Users Listing", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive CRM API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_admin_login,
            self.test_sales_login,
            self.test_reviewer_login,
            self.test_dashboard_access,
            self.test_company_creation_with_valid_gst,
            self.test_company_listing_admin,
            self.test_leads_access_sales_user,
            self.test_contacts_listing,
            self.test_opportunities_listing,
            self.test_users_listing
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
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