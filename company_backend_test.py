#!/usr/bin/env python3
"""
Company Management Module Testing for Swayatta 4.0 CRM System
Focus on comprehensive company management functionality, validation, and workflows
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional
import tempfile
from io import BytesIO
from datetime import datetime

# Backend URL from frontend environment (using the correct port)
BACKEND_URL = "http://localhost:8001"
TEST_SESSION_ID = "test_session_123"

class CompanyManagementTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.jwt_token = None
        self.auth_headers = {}
        self.test_results = {}
        self.created_company_id = None
        self.test_company_data = None
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("\n=== Authenticating with Admin Credentials ===")
        try:
            login_data = {
                "email_or_username": "admin",
                "password": "admin123"
            }
            response = self.make_request("POST", "/api/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("access_token"):
                    self.jwt_token = data["data"]["access_token"]
                    self.auth_headers = {"Authorization": f"Bearer {self.jwt_token}"}
                    self.log_test("Authentication", True, "Successfully authenticated with admin credentials")
                    return True
                else:
                    self.log_test("Authentication", False, "Invalid login response", data)
                    return False
            else:
                self.log_test("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication failed: {str(e)}")
            return False

    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "details": details
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, headers: Optional[Dict] = None, 
                    data: Any = None, files: Any = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        request_headers = headers or {}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=request_headers, files=files, timeout=10)
                else:
                    response = requests.post(url, headers=request_headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=request_headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {method} {url}: {e}")
            raise

    def test_masters_endpoints(self):
        """Test master data endpoints for company form dropdowns"""
        print("\n=== Testing Master Data Endpoints ===")
        
        # Test 1: Industry Masters
        try:
            response = self.make_request("GET", "/api/companies/masters/industries", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    industries = data["data"]
                    if isinstance(industries, dict) and len(industries) > 0:
                        # Check if we have expected industries
                        expected_industries = ["BFSI", "Government", "IT_ITeS", "Manufacturing"]
                        found_industries = [ind for ind in expected_industries if ind in industries]
                        if len(found_industries) >= 2:
                            self.log_test("Masters - Industry Data", True, 
                                        f"Industry masters retrieved successfully ({len(industries)} industries)")
                        else:
                            self.log_test("Masters - Industry Data", False, 
                                        f"Expected industries not found. Got: {list(industries.keys())[:5]}")
                    else:
                        self.log_test("Masters - Industry Data", False, "Invalid industry data format", data)
                else:
                    self.log_test("Masters - Industry Data", False, "Invalid response format", data)
            else:
                self.log_test("Masters - Industry Data", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Industry Data", False, f"Request failed: {str(e)}")
        
        # Test 2: Country-State Masters
        try:
            response = self.make_request("GET", "/api/companies/masters/countries-states", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    countries = data["data"]
                    if isinstance(countries, dict) and "India" in countries:
                        indian_states = countries["India"]
                        if isinstance(indian_states, list) and len(indian_states) > 20:
                            self.log_test("Masters - Country-State Data", True, 
                                        f"Country-state masters retrieved successfully ({len(countries)} countries)")
                        else:
                            self.log_test("Masters - Country-State Data", False, 
                                        f"Insufficient Indian states. Got: {len(indian_states) if isinstance(indian_states, list) else 0}")
                    else:
                        self.log_test("Masters - Country-State Data", False, "India not found in countries", data)
                else:
                    self.log_test("Masters - Country-State Data", False, "Invalid response format", data)
            else:
                self.log_test("Masters - Country-State Data", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Country-State Data", False, f"Request failed: {str(e)}")

    def test_company_crud_operations(self):
        """Test comprehensive company CRUD operations"""
        print("\n=== Testing Company CRUD Operations ===")
        
        # Prepare comprehensive test company data
        self.test_company_data = {
            "name": "Swayatta Test Technologies Pvt Ltd",
            "parent_company_name": "",
            "company_type": "DOMESTIC_GST",
            "industry": "IT_ITeS",
            "sub_industry": "Software Development",
            "annual_revenue": 25000000.00,  # ₹2.5 crore (should trigger high revenue tag)
            
            # Identification & Compliance
            "gst_number": "27AAAAA0000A1Z5",
            "pan_number": "AAAAA0000A",
            "supporting_documents": ["test_gst_certificate.pdf"],
            "verification_source": "GST",
            "verification_date": datetime.now().strftime("%Y-%m-%d"),
            "verified_by": "admin",
            
            # Registered Address
            "address": "123 Tech Park, Sector 62, Electronic City Phase 1, Bangalore",
            "country": "India",
            "state": "Karnataka",
            "city": "Bangalore",
            "pin_code": "560100",
            
            # Hierarchy & Linkages
            "parent_child_mapping_confirmed": True,
            "linked_subsidiaries": ["None"],
            "associated_channel_partner": "",
            
            # Additional Information
            "website": "https://swayattatest.com",
            "description": "Leading technology solutions provider specializing in CRM and enterprise software"
        }
        
        # Test 1: Create Company
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=self.test_company_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.created_company_id = data["data"]["id"]
                    company_data = data["data"]
                    
                    # Check if high revenue auto-tagging worked
                    is_high_revenue = company_data.get("is_high_revenue", False)
                    if is_high_revenue:
                        self.log_test("Company - Create with Auto-tagging", True, 
                                    f"Company created successfully with high revenue auto-tagging (ID: {self.created_company_id})")
                    else:
                        self.log_test("Company - Create", True, 
                                    f"Company created successfully (ID: {self.created_company_id})")
                        self.log_test("Company - Auto-tagging", False, 
                                    "High revenue auto-tagging not working", company_data)
                else:
                    self.log_test("Company - Create", False, "Invalid create response", data)
            else:
                self.log_test("Company - Create", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Company - Create", False, f"Request failed: {str(e)}")
        
        # Test 2: Get Company by ID
        if self.created_company_id:
            try:
                response = self.make_request("GET", f"/api/companies/{self.created_company_id}", headers=self.auth_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data", {}).get("id") == self.created_company_id:
                        company_data = data["data"]
                        self.log_test("Company - Get by ID", True, 
                                    f"Company retrieved successfully: {company_data.get('name')}")
                        
                        # Validate key fields
                        validation_checks = [
                            ("GST Number", company_data.get("gst_number") == self.test_company_data["gst_number"]),
                            ("PAN Number", company_data.get("pan_number") == self.test_company_data["pan_number"]),
                            ("Industry", company_data.get("industry") == self.test_company_data["industry"]),
                            ("Annual Revenue", float(company_data.get("annual_revenue", 0)) == self.test_company_data["annual_revenue"]),
                            ("Address", company_data.get("address") == self.test_company_data["address"])
                        ]
                        
                        failed_validations = [check[0] for check in validation_checks if not check[1]]
                        if not failed_validations:
                            self.log_test("Company - Data Validation", True, "All company data fields validated successfully")
                        else:
                            self.log_test("Company - Data Validation", False, 
                                        f"Validation failed for: {', '.join(failed_validations)}")
                    else:
                        self.log_test("Company - Get by ID", False, "Invalid company response", data)
                else:
                    self.log_test("Company - Get by ID", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Company - Get by ID", False, f"Request failed: {str(e)}")
        
        # Test 3: Update Company
        if self.created_company_id:
            update_data = {
                "description": "Updated description: Leading technology solutions provider with enhanced CRM capabilities",
                "website": "https://swayattatest-updated.com",
                "annual_revenue": 35000000.00  # Increase revenue
            }
            try:
                response = self.make_request("PUT", f"/api/companies/{self.created_company_id}", 
                                           headers=self.auth_headers, data=update_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status"):
                        self.log_test("Company - Update", True, "Company updated successfully")
                    else:
                        self.log_test("Company - Update", False, "Invalid update response", data)
                else:
                    self.log_test("Company - Update", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Company - Update", False, f"Request failed: {str(e)}")
        
        # Test 4: Get All Companies (List functionality)
        try:
            response = self.make_request("GET", "/api/companies/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("companies"):
                    companies = data["data"]["companies"]
                    total = data["data"].get("total", 0)
                    self.log_test("Company - List Companies", True, 
                                f"Companies listing successful ({len(companies)} companies, total: {total})")
                    
                    # Check if our created company is in the list
                    if self.created_company_id:
                        found_company = any(c.get("id") == self.created_company_id for c in companies)
                        if found_company:
                            self.log_test("Company - List Contains Created", True, "Created company found in list")
                        else:
                            self.log_test("Company - List Contains Created", False, "Created company not found in list")
                else:
                    self.log_test("Company - List Companies", False, "Invalid companies list response", data)
            else:
                self.log_test("Company - List Companies", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Company - List Companies", False, f"Request failed: {str(e)}")

    def test_company_validation_rules(self):
        """Test comprehensive validation rules"""
        print("\n=== Testing Company Validation Rules ===")
        
        # Test 1: Missing Required Fields
        invalid_data = {
            "name": "",  # Empty name
            "company_type": "",  # Empty type
            "annual_revenue": -1000  # Negative revenue
        }
        
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=invalid_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Missing Required Fields", True, 
                            "Validation correctly rejected company with missing required fields")
            else:
                self.log_test("Validation - Missing Required Fields", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Missing Required Fields", False, f"Request failed: {str(e)}")
        
        # Test 2: Invalid GST Format
        invalid_gst_data = {
            "name": "Test GST Validation Company",
            "company_type": "DOMESTIC_GST",
            "industry": "IT_ITeS",
            "sub_industry": "Software Development",
            "annual_revenue": 1000000.00,
            "gst_number": "INVALID_GST_FORMAT",  # Invalid GST
            "pan_number": "AAAAA0000A",
            "verification_source": "GST",
            "verification_date": datetime.now().strftime("%Y-%m-%d"),
            "verified_by": "admin",
            "address": "Test Address",
            "country": "India",
            "state": "Karnataka",
            "city": "Bangalore",
            "pin_code": "560001",
            "parent_child_mapping_confirmed": True,
            "linked_subsidiaries": ["None"]
        }
        
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=invalid_gst_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Invalid GST Format", True, 
                            "Validation correctly rejected company with invalid GST format")
            else:
                self.log_test("Validation - Invalid GST Format", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Invalid GST Format", False, f"Request failed: {str(e)}")
        
        # Test 3: Invalid PAN Format
        invalid_pan_data = invalid_gst_data.copy()
        invalid_pan_data["gst_number"] = "27AAAAA0000A1Z5"  # Valid GST
        invalid_pan_data["pan_number"] = "INVALID_PAN"  # Invalid PAN
        
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=invalid_pan_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Invalid PAN Format", True, 
                            "Validation correctly rejected company with invalid PAN format")
            else:
                self.log_test("Validation - Invalid PAN Format", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Invalid PAN Format", False, f"Request failed: {str(e)}")

    def test_company_filtering_and_search(self):
        """Test company filtering and search functionality"""
        print("\n=== Testing Company Filtering and Search ===")
        
        # Test 1: Filter by Company Type
        try:
            response = self.make_request("GET", "/api/companies/?company_type=DOMESTIC_GST", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("companies"):
                    companies = data["data"]["companies"]
                    # Check if all returned companies are DOMESTIC_GST type
                    all_domestic_gst = all(c.get("company_type") == "DOMESTIC_GST" for c in companies)
                    if all_domestic_gst:
                        self.log_test("Filtering - Company Type", True, 
                                    f"Company type filtering working ({len(companies)} DOMESTIC_GST companies)")
                    else:
                        self.log_test("Filtering - Company Type", False, 
                                    "Filter returned companies with different types")
                else:
                    self.log_test("Filtering - Company Type", False, "Invalid filter response", data)
            else:
                self.log_test("Filtering - Company Type", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Filtering - Company Type", False, f"Request failed: {str(e)}")
        
        # Test 2: Filter by Industry
        try:
            response = self.make_request("GET", "/api/companies/?industry=IT_ITeS", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("companies"):
                    companies = data["data"]["companies"]
                    self.log_test("Filtering - Industry", True, 
                                f"Industry filtering working ({len(companies)} IT_ITeS companies)")
                else:
                    self.log_test("Filtering - Industry", False, "Invalid filter response", data)
            else:
                self.log_test("Filtering - Industry", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Filtering - Industry", False, f"Request failed: {str(e)}")
        
        # Test 3: Search by Company Name
        if self.created_company_id and self.test_company_data:
            search_term = "Swayatta"
            try:
                response = self.make_request("GET", f"/api/companies/?search={search_term}", headers=self.auth_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data", {}).get("companies"):
                        companies = data["data"]["companies"]
                        # Check if our created company is found
                        found_company = any(search_term.lower() in c.get("name", "").lower() for c in companies)
                        if found_company:
                            self.log_test("Search - Company Name", True, 
                                        f"Company name search working ({len(companies)} results for '{search_term}')")
                        else:
                            self.log_test("Search - Company Name", False, 
                                        f"Created company not found in search results for '{search_term}'")
                    else:
                        self.log_test("Search - Company Name", False, "Invalid search response", data)
                else:
                    self.log_test("Search - Company Name", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Search - Company Name", False, f"Request failed: {str(e)}")

    def test_duplicate_check_functionality(self):
        """Test duplicate company detection"""
        print("\n=== Testing Duplicate Check Functionality ===")
        
        if not self.test_company_data:
            self.log_test("Duplicate Check - Prerequisites", False, "No test company data available")
            return
        
        # Test duplicate check with existing company data
        try:
            response = self.make_request("POST", "/api/companies/check-duplicates", 
                                       headers=self.auth_headers, data=self.test_company_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    duplicate_result = data["data"]
                    is_duplicate = duplicate_result.get("is_duplicate", False)
                    if is_duplicate:
                        self.log_test("Duplicate Check - Detection", True, 
                                    f"Duplicate detection working: {duplicate_result.get('match_type', 'Unknown match')}")
                    else:
                        self.log_test("Duplicate Check - No Duplicates", True, 
                                    "Duplicate check completed - no duplicates found")
                else:
                    self.log_test("Duplicate Check - Response", False, "Invalid duplicate check response", data)
            else:
                self.log_test("Duplicate Check - Response", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Duplicate Check - Response", False, f"Request failed: {str(e)}")

    def run_company_management_tests(self):
        """Run all company management tests"""
        print("🚀 Starting Company Management Module Testing")
        print(f"Backend URL: {self.base_url}")
        
        # First authenticate with admin credentials
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with protected endpoint tests.")
            return
        
        # Run comprehensive test suites
        self.test_masters_endpoints()
        self.test_company_crud_operations()
        self.test_company_validation_rules()
        self.test_company_filtering_and_search()
        self.test_duplicate_check_functionality()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🏁 COMPANY MANAGEMENT MODULE TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        categories = {}
        for test_name, result in self.test_results.items():
            category = test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append((test_name, result))
        
        print("\n📊 RESULTS BY CATEGORY:")
        for category, data in categories.items():
            total_cat = data["passed"] + data["failed"]
            success_rate = (data["passed"] / total_cat) * 100 if total_cat > 0 else 0
            print(f"  {category}: {data['passed']}/{total_cat} passed ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {test_name}: {result['message']}")
                    if result.get("details"):
                        print(f"    Details: {str(result['details'])[:200]}...")
        
        print("\n" + "="*70)
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = CompanyManagementTester()
    tester.run_company_management_tests()
    
    # Exit with appropriate code
    passed, failed = tester.print_summary()
    sys.exit(0 if failed == 0 else 1)