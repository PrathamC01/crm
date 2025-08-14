#!/usr/bin/env python3
"""
Backend API Testing for Company Approval Workflow Removal
Tests the complete company creation workflow to ensure approval process has been removed.
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import time

class CRMAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.session_headers = {}
        self.tests_run = 0
        self.tests_passed = 0
        self.created_company_id = None

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = {**self.session_headers}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    self.log(f"   Raw response: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Request timeout")
            return False, {}
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "/",
            200
        )
        return success

    def test_login(self, username, password):
        """Test login and get session"""
        success, response = self.run_test(
            f"Login as {username}",
            "POST",
            "/api/login",
            200,
            data={"email_or_username": username, "password": password}
        )
        
        if success and response.get('status') and response.get('data'):
            token = response['data'].get('token') or response['data'].get('access_token')
            if token:
                self.token = token
                self.session_headers = {'Authorization': f'Bearer {token}'}
                self.log(f"✅ Login successful, token acquired")
                return True
            else:
                self.log(f"❌ Login response missing token")
                self.log(f"   Response data: {response.get('data', {})}")
                return False
        return False

    def test_get_companies(self):
        """Test getting companies list"""
        success, response = self.run_test(
            "Get Companies List",
            "GET",
            "/api/companies",
            200
        )
        
        if success and response.get('status'):
            companies = response.get('data', {}).get('companies', [])
            self.log(f"✅ Found {len(companies)} companies")
            return True, companies
        return False, []

    def test_create_company_immediate_active(self):
        """Test creating a company that should be immediately active (no approval workflow)"""
        company_data = {
            "name": f"Test Company {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "company_type": "DOMESTIC_GST",
            "industry": "BFSI",
            "sub_industry": "BANKING — Retail Banking",
            "annual_revenue": 50000000,
            "gst_number": "27ABCDE1234F1Z5",
            "pan_number": "ABCDE1234F",
            "verification_source": "GST",
            "verification_date": datetime.now().isoformat(),
            "verified_by": "admin",
            "address": "123 Test Street, Test Area, Test Locality",
            "country": "India",
            "state": "Maharashtra",
            "city": "Mumbai",
            "pin_code": "400001",
            "parent_child_mapping_confirmed": True,
            "linked_subsidiaries": ["None"],
            "website": "https://testcompany.com",
            "description": "Test company for approval workflow removal testing"
        }

        success, response = self.run_test(
            "Create Company (Should be Immediately Active)",
            "POST",
            "/api/companies",
            200,
            data=company_data
        )

        if success and response.get('status'):
            company = response.get('data')
            if company:
                self.created_company_id = company.get('id')
                status = company.get('status')
                self.log(f"✅ Company created with ID: {self.created_company_id}")
                self.log(f"✅ Company status: {status}")
                
                # Verify the company is ACTIVE immediately
                if status == "ACTIVE":
                    self.log(f"✅ PASS: Company is immediately ACTIVE (no approval workflow)")
                    return True, company
                else:
                    self.log(f"❌ FAIL: Company status is '{status}', expected 'ACTIVE'")
                    return False, company
            else:
                self.log(f"❌ FAIL: No company data in response")
                return False, {}
        return False, {}

    def test_get_created_company(self):
        """Test retrieving the created company to verify its status"""
        if not self.created_company_id:
            self.log("❌ No company ID available for testing")
            return False

        success, response = self.run_test(
            f"Get Created Company (ID: {self.created_company_id})",
            "GET",
            f"/api/companies/{self.created_company_id}",
            200
        )

        if success and response.get('status'):
            company = response.get('data')
            if company:
                status = company.get('status')
                self.log(f"✅ Retrieved company status: {status}")
                
                if status == "ACTIVE":
                    self.log(f"✅ PASS: Company remains ACTIVE")
                    return True, company
                else:
                    self.log(f"❌ FAIL: Company status is '{status}', expected 'ACTIVE'")
                    return False, company
        return False, {}

    def test_company_in_dropdown(self):
        """Test that newly created company appears in company dropdown for leads"""
        if not self.created_company_id:
            self.log("❌ No company ID available for dropdown testing")
            return False

        # Get all companies to simulate dropdown population
        success, companies = self.test_get_companies()
        
        if success:
            # Check if our created company is in the list
            created_company = None
            for company in companies:
                if company.get('id') == self.created_company_id:
                    created_company = company
                    break
            
            if created_company:
                self.log(f"✅ PASS: Created company found in companies list")
                self.log(f"✅ Company name: {created_company.get('name')}")
                self.log(f"✅ Company status: {created_company.get('status')}")
                return True
            else:
                self.log(f"❌ FAIL: Created company not found in companies list")
                return False
        return False

    def test_user_roles_company_creation(self):
        """Test company creation with different user roles"""
        # Test with sales user
        sales_login_success = self.test_login("sales", "sales123")
        
        if sales_login_success:
            company_data = {
                "name": f"Sales Test Company {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "company_type": "DOMESTIC_GST",
                "industry": "BFSI",
                "sub_industry": "BANKING — Retail Banking",
                "annual_revenue": 25000000,
                "gst_number": "27SALES1234F1Z5",
                "pan_number": "SALES1234F",
                "verification_source": "GST",
                "verification_date": datetime.now().isoformat(),
                "verified_by": "sales",
                "address": "456 Sales Street, Sales Area, Sales Locality",
                "country": "India",
                "state": "Maharashtra",
                "city": "Mumbai",
                "pin_code": "400002",
                "parent_child_mapping_confirmed": True,
                "linked_subsidiaries": ["None"],
                "description": "Test company created by sales user"
            }

            success, response = self.run_test(
                "Create Company as Sales User",
                "POST",
                "/api/companies",
                200,
                data=company_data
            )

            if success and response.get('status'):
                company = response.get('data')
                if company and company.get('status') == "ACTIVE":
                    self.log(f"✅ PASS: Sales user can create companies immediately active")
                    return True
                else:
                    self.log(f"❌ FAIL: Sales user company not immediately active")
                    return False
            else:
                self.log(f"❌ FAIL: Sales user cannot create companies")
                return False
        else:
            self.log(f"❌ FAIL: Could not login as sales user")
            return False

    def test_no_approval_endpoints(self):
        """Test that approval-related endpoints are not accessible or return appropriate responses"""
        # These endpoints should either not exist or return appropriate responses
        approval_endpoints = [
            "/api/companies/pending-approval",
            "/api/companies/approve",
            "/api/companies/reject"
        ]

        for endpoint in approval_endpoints:
            success, response = self.run_test(
                f"Check Approval Endpoint: {endpoint}",
                "GET",
                endpoint,
                404  # Should return 404 as these endpoints should not exist
            )
            if success:
                self.log(f"✅ PASS: Approval endpoint {endpoint} properly removed (404)")
            else:
                self.log(f"⚠️  WARNING: Approval endpoint {endpoint} still exists")

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting CRM Company Approval Workflow Removal Tests")
        self.log("=" * 60)

        # Test 1: Health Check
        if not self.test_health_check():
            self.log("❌ CRITICAL: API health check failed, stopping tests")
            return False

        # Test 2: Admin Login
        if not self.test_login("admin", "admin123"):
            self.log("❌ CRITICAL: Admin login failed, stopping tests")
            return False

        # Test 3: Create Company (should be immediately active)
        company_created, company_data = self.test_create_company_immediate_active()
        if not company_created:
            self.log("❌ CRITICAL: Company creation failed")
            return False

        # Test 4: Verify created company status
        if not self.test_get_created_company():
            self.log("❌ CRITICAL: Could not retrieve created company")

        # Test 5: Check company appears in dropdown
        if not self.test_company_in_dropdown():
            self.log("❌ CRITICAL: Created company not available in dropdown")

        # Test 6: Test different user roles
        # Re-login as admin for role testing
        self.test_login("admin", "admin123")
        if not self.test_user_roles_company_creation():
            self.log("❌ WARNING: Sales user company creation test failed")

        # Test 7: Verify approval endpoints are removed
        self.test_no_approval_endpoints()

        # Final Results
        self.log("=" * 60)
        self.log(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 ALL TESTS PASSED: Company approval workflow successfully removed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            self.log(f"⚠️  {failed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    print("CRM Backend API Testing - Company Approval Workflow Removal")
    print("=" * 70)
    
    tester = CRMAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())