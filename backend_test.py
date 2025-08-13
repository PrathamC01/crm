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

class EnhancedLeadsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.jwt_token = None
        self.auth_headers = {}
        self.test_results = {}
        self.created_lead_id = None
        self.created_company_id = None
        self.created_contact_id = None
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n=== Authenticating with CRM System ===")
        try:
            login_data = {
                "email_or_username": "sales@company.com",
                "password": "sales123"
            }
            response = self.make_request("POST", "/api/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("token"):
                    self.jwt_token = data["data"]["token"]
                    self.auth_headers = {"Authorization": f"Bearer {self.jwt_token}"}
                    # Also update session_headers to use the same token for session endpoints
                    self.session_headers = {"Authorization": f"Bearer {self.jwt_token}"}
                    self.log_test("Authentication", True, "Successfully authenticated with JWT token")
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

    def test_authentication_permissions(self):
        """Test authentication and permissions for sales user"""
        print("\n=== Testing Authentication and Permissions ===")
        
        # Test session info to verify user permissions
        try:
            response = self.make_request("GET", "/api/session/info", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    user_data = data["data"]
                    permissions = user_data.get("permissions", [])
                    
                    # Check for required permissions
                    required_permissions = ["leads:read", "leads:write", "companies:read", "contacts:read"]
                    missing_permissions = []
                    
                    for perm in required_permissions:
                        if perm not in permissions:
                            missing_permissions.append(perm)
                    
                    if not missing_permissions:
                        self.log_test("Auth - Sales User Permissions", True, 
                                    f"Sales user has all required permissions: {required_permissions}")
                    else:
                        self.log_test("Auth - Sales User Permissions", False, 
                                    f"Missing permissions: {missing_permissions}", user_data)
                else:
                    self.log_test("Auth - Sales User Permissions", False, "Invalid session response", data)
            else:
                self.log_test("Auth - Sales User Permissions", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth - Sales User Permissions", False, f"Request failed: {str(e)}")

    def test_companies_api(self):
        """Test Companies API endpoints needed for lead form dropdowns"""
        print("\n=== Testing Companies API ===")
        
        # Test 1: Get All Companies
        try:
            response = self.make_request("GET", "/api/companies/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    companies_data = data["data"]
                    if "companies" in companies_data and isinstance(companies_data["companies"], list):
                        self.log_test("Companies - Get All", True, 
                                    f"Companies retrieved successfully ({len(companies_data['companies'])} found)")
                        
                        # Store first company ID for lead creation
                        if companies_data["companies"]:
                            self.created_company_id = companies_data["companies"][0].get("id")
                    else:
                        self.log_test("Companies - Get All", False, "Invalid companies response format", data)
                else:
                    self.log_test("Companies - Get All", False, "Invalid response format", data)
            else:
                self.log_test("Companies - Get All", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Companies - Get All", False, f"Request failed: {str(e)}")
        
        # Test 2: Create a test company if none exist
        if not self.created_company_id:
            company_data = {
                "name": "Test Technology Solutions Pvt Ltd",
                "industry": "Information Technology",
                "website": "https://testtechsolutions.com",
                "phone": "+91-11-12345678",
                "email": "info@testtechsolutions.com",
                "address": {
                    "street": "123 Tech Park",
                    "city": "New Delhi",
                    "state": "Delhi",
                    "country": "India",
                    "postal_code": "110001"
                },
                "company_type": "Private Limited",
                "annual_revenue": 50000000.00,
                "employee_count": 150,
                "description": "Leading technology solutions provider"
            }
            
            try:
                response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=company_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data", {}).get("id"):
                        self.created_company_id = data["data"]["id"]
                        self.log_test("Companies - Create Company", True, "Test company created successfully")
                    else:
                        self.log_test("Companies - Create Company", False, "Invalid create response", data)
                else:
                    self.log_test("Companies - Create Company", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Companies - Create Company", False, f"Request failed: {str(e)}")

    def test_contacts_api(self):
        """Test Contacts API endpoints needed for lead form"""
        print("\n=== Testing Contacts API ===")
        
        # Test 1: Get All Contacts
        try:
            response = self.make_request("GET", "/api/contacts/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    contacts_data = data["data"]
                    if "contacts" in contacts_data and isinstance(contacts_data["contacts"], list):
                        self.log_test("Contacts - Get All", True, 
                                    f"Contacts retrieved successfully ({len(contacts_data['contacts'])} found)")
                        
                        # Store first contact ID for lead creation
                        if contacts_data["contacts"]:
                            self.created_contact_id = contacts_data["contacts"][0].get("id")
                    else:
                        self.log_test("Contacts - Get All", False, "Invalid contacts response format", data)
                else:
                    self.log_test("Contacts - Get All", False, "Invalid response format", data)
            else:
                self.log_test("Contacts - Get All", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Contacts - Get All", False, f"Request failed: {str(e)}")
        
        # Test 2: Create a test contact if none exist and we have a company
        if not self.created_contact_id and self.created_company_id:
            contact_data = {
                "company_id": self.created_company_id,
                "first_name": "Arjun",
                "last_name": "Patel",
                "email": "arjun.patel@testtechsolutions.com",
                "phone": "+91-9876543210",
                "designation": "Chief Technology Officer",
                "department": "Technology",
                "is_decision_maker": True,
                "decision_making_authority": 85,
                "address": {
                    "street": "123 Tech Park",
                    "city": "New Delhi",
                    "state": "Delhi",
                    "country": "India",
                    "postal_code": "110001"
                }
            }
            
            try:
                response = self.make_request("POST", "/api/contacts/", headers=self.auth_headers, data=contact_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status"):
                        self.log_test("Contacts - Create Contact", True, "Test contact created successfully")
                        # Get the created contact ID by fetching contacts again
                        self.test_get_created_contact()
                    else:
                        self.log_test("Contacts - Create Contact", False, "Invalid create response", data)
                else:
                    self.log_test("Contacts - Create Contact", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Contacts - Create Contact", False, f"Request failed: {str(e)}")

    def test_get_created_contact(self):
        """Helper method to get the created contact ID"""
        try:
            response = self.make_request("GET", "/api/contacts/?skip=0&limit=1", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("contacts"):
                    contacts = data["data"]["contacts"]
                    if contacts:
                        self.created_contact_id = contacts[0].get("id")
        except Exception:
            pass  # Ignore errors in helper method

    def test_leads_functionality(self):
        """Test comprehensive leads functionality"""
        print("\n=== Testing Enhanced Leads Functionality ===")
        
        # Ensure we have required data
        if not self.created_company_id:
            self.log_test("Leads - Prerequisites", False, "No company available for lead creation")
            return
        
        # Sample lead data with realistic information
        lead_data = {
            "project_title": "Digital Transformation Initiative for Government Department",
            "lead_source": "Direct Marketing",
            "lead_sub_type": "Pre-Tender",
            "tender_sub_type": "Open Tender",
            "products_services": ["Enterprise CRM Software", "Implementation Services", "Training & Support"],
            "company_id": self.created_company_id,
            "sub_business_type": "Government Solutions",
            "end_customer_id": self.created_company_id,  # Using same company as end customer for simplicity
            "end_customer_region": "North India",
            "partner_involved": False,
            "partners_data": [],
            "tender_fee": 75000.00,
            "currency": "INR",
            "submission_type": "Online",
            "tender_authority": "Department of Information Technology",
            "tender_for": "Ministry of Electronics and Information Technology",
            "emd_required": True,
            "emd_amount": 150000.00,
            "emd_currency": "INR",
            "bg_required": True,
            "bg_amount": 750000.00,
            "bg_currency": "INR",
            "important_dates": [
                {
                    "label": "Pre-bid Meeting",
                    "key": "pre_bid_date",
                    "value": "2024-12-20"
                },
                {
                    "label": "Submission Deadline",
                    "key": "submission_date",
                    "value": "2025-01-15"
                }
            ],
            "clauses": [
                {
                    "clause_type": "Technical",
                    "criteria_description": "Minimum 7 years experience in government CRM implementations"
                },
                {
                    "clause_type": "Financial",
                    "criteria_description": "Annual turnover of minimum 10 crores in last 3 years"
                }
            ],
            "expected_revenue": 8500000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2025-01-20",
            "competitors": [
                {
                    "name": "TechCorp Solutions",
                    "description": "Major competitor with government sector experience"
                },
                {
                    "name": "InfoSys Government Solutions",
                    "description": "Established player in government IT solutions"
                }
            ],
            "documents": [],
            "status": "New",
            "priority": "High",
            "qualification_notes": "High-value government tender with strong potential. Client has confirmed budget allocation.",
            "lead_score": 88,
            "contacts": [
                {
                    "designation": "Joint Secretary",
                    "salutation": "Dr.",
                    "first_name": "Priya",
                    "middle_name": "Kumari",
                    "last_name": "Singh",
                    "email": "priya.singh@gov.in",
                    "primary_phone": "+91-11-23456789",
                    "decision_maker": True,
                    "decision_maker_percentage": 90,
                    "comments": "Primary decision maker for IT procurement"
                },
                {
                    "designation": "Technical Director",
                    "salutation": "Mr.",
                    "first_name": "Vikram",
                    "middle_name": "",
                    "last_name": "Gupta",
                    "email": "vikram.gupta@gov.in",
                    "primary_phone": "+91-11-23456790",
                    "decision_maker": False,
                    "decision_maker_percentage": 30,
                    "comments": "Technical evaluation committee member"
                }
            ]
        }
        
        # Test 1: Create Lead
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.created_lead_id = data["data"]["id"]
                    self.log_test("Leads - Create Lead", True, 
                                f"Lead created successfully with ID: {self.created_lead_id}")
                else:
                    self.log_test("Leads - Create Lead", False, "Invalid create response", data)
            else:
                self.log_test("Leads - Create Lead", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - Create Lead", False, f"Request failed: {str(e)}")
        
        # Test 2: Get All Leads (List functionality)
        try:
            response = self.make_request("GET", "/api/leads/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("leads"):
                    leads = data["data"]["leads"]
                    total = data["data"].get("total", 0)
                    self.log_test("Leads - List Leads", True, 
                                f"Leads listing successful ({len(leads)} leads, total: {total})")
                else:
                    self.log_test("Leads - List Leads", False, "Invalid leads list response", data)
            else:
                self.log_test("Leads - List Leads", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - List Leads", False, f"Request failed: {str(e)}")
        
        # Test 3: Get Lead by ID
        if self.created_lead_id:
            try:
                response = self.make_request("GET", f"/api/leads/{self.created_lead_id}", headers=self.auth_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data", {}).get("id") == self.created_lead_id:
                        lead_data = data["data"]
                        self.log_test("Leads - Get Lead by ID", True, 
                                    f"Lead retrieved successfully: {lead_data.get('project_title')}")
                    else:
                        self.log_test("Leads - Get Lead by ID", False, "Invalid lead response", data)
                else:
                    self.log_test("Leads - Get Lead by ID", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Leads - Get Lead by ID", False, f"Request failed: {str(e)}")
        
        # Test 4: Update Lead (Edit functionality)
        if self.created_lead_id:
            update_data = {
                "qualification_notes": "Updated after detailed discussion with client. Confirmed technical requirements and budget approval process.",
                "lead_score": 92,
                "status": "Qualified",
                "priority": "High"
            }
            try:
                response = self.make_request("PUT", f"/api/leads/{self.created_lead_id}", 
                                           headers=self.auth_headers, data=update_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status"):
                        self.log_test("Leads - Update Lead", True, "Lead updated successfully")
                    else:
                        self.log_test("Leads - Update Lead", False, "Invalid update response", data)
                else:
                    self.log_test("Leads - Update Lead", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Leads - Update Lead", False, f"Request failed: {str(e)}")
        
        # Test 5: Lead Status Changes
        if self.created_lead_id:
            status_changes = [
                {"status": "Contacted", "notes": "Initial contact made with decision maker"},
                {"status": "Qualified", "notes": "Lead qualified after technical discussion"},
                {"status": "Active", "notes": "Proposal submitted, awaiting response"}
            ]
            
            for i, status_change in enumerate(status_changes):
                try:
                    response = self.make_request("PUT", f"/api/leads/{self.created_lead_id}", 
                                               headers=self.auth_headers, data=status_change)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status"):
                            self.log_test(f"Leads - Status Change {i+1}", True, 
                                        f"Status changed to {status_change['status']}")
                        else:
                            self.log_test(f"Leads - Status Change {i+1}", False, "Invalid status update", data)
                    else:
                        self.log_test(f"Leads - Status Change {i+1}", False, 
                                    f"HTTP {response.status_code}", response.text)
                except Exception as e:
                    self.log_test(f"Leads - Status Change {i+1}", False, f"Request failed: {str(e)}")
        
        # Test 6: Get Lead Statistics
        try:
            response = self.make_request("GET", "/api/leads/stats", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    stats = data["data"]
                    self.log_test("Leads - Get Statistics", True, 
                                f"Lead statistics retrieved: {stats.get('total', 0)} total leads")
                else:
                    self.log_test("Leads - Get Statistics", False, "Invalid stats response", data)
            else:
                self.log_test("Leads - Get Statistics", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - Get Statistics", False, f"Request failed: {str(e)}")

    def test_lead_conversion_workflow(self):
        """Test lead to opportunity conversion workflow"""
        print("\n=== Testing Lead Conversion Workflow ===")
        
        if not self.created_lead_id:
            self.log_test("Conversion - Prerequisites", False, "No lead available for conversion testing")
            return
        
        # Test 1: Request Conversion
        conversion_request_data = {
            "notes": "Lead is fully qualified and ready for conversion. Client has confirmed budget and timeline."
        }
        try:
            response = self.make_request("POST", f"/api/leads/{self.created_lead_id}/request-conversion", 
                                       headers=self.auth_headers, data=conversion_request_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("Conversion - Request Conversion", True, 
                                "Conversion request submitted successfully")
                else:
                    self.log_test("Conversion - Request Conversion", False, "Invalid conversion request", data)
            else:
                self.log_test("Conversion - Request Conversion", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Request Conversion", False, f"Request failed: {str(e)}")
        
        # Test 2: Review Conversion Request (Admin action)
        review_data = {
            "decision": "Approved",
            "comments": "Lead meets all criteria for conversion. Revenue potential and client commitment verified."
        }
        try:
            response = self.make_request("POST", f"/api/leads/{self.created_lead_id}/review", 
                                       headers=self.auth_headers, data=review_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("Conversion - Review Request", True, "Conversion request approved successfully")
                else:
                    self.log_test("Conversion - Review Request", False, "Invalid review response", data)
            else:
                self.log_test("Conversion - Review Request", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Review Request", False, f"Request failed: {str(e)}")
        
        # Test 3: Convert to Opportunity
        conversion_data = {
            "opportunity_name": "Digital Transformation Initiative - Government Department Opportunity",
            "notes": "Converting qualified lead to opportunity. All stakeholders aligned and budget confirmed."
        }
        try:
            response = self.make_request("POST", f"/api/leads/{self.created_lead_id}/convert-to-opportunity", 
                                       headers=self.auth_headers, data=conversion_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("opportunity_id"):
                    opportunity_id = data["data"]["opportunity_id"]
                    self.log_test("Conversion - Convert to Opportunity", True, 
                                f"Lead converted to opportunity successfully (ID: {opportunity_id})")
                    return opportunity_id
                else:
                    self.log_test("Conversion - Convert to Opportunity", False, "Invalid conversion response", data)
            else:
                self.log_test("Conversion - Convert to Opportunity", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Convert to Opportunity", False, f"Request failed: {str(e)}")
        
        return None

    def test_validation_scenarios(self):
        """Test lead creation with validation scenarios"""
        print("\n=== Testing Lead Validation Scenarios ===")
        
        # Test 1: Lead creation with missing required fields
        invalid_lead_data = {
            "project_title": "",  # Empty title
            "lead_source": "Direct Marketing",
            "expected_revenue": -1000,  # Negative revenue
            "contacts": []  # No contacts
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_lead_data)
            if response.status_code == 400:
                self.log_test("Validation - Missing Required Fields", True, 
                            "Validation correctly rejected lead with missing required fields")
            elif response.status_code == 422:
                self.log_test("Validation - Missing Required Fields", True, 
                            "Validation correctly rejected lead with validation errors")
            else:
                self.log_test("Validation - Missing Required Fields", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Missing Required Fields", False, f"Request failed: {str(e)}")
        
        # Test 2: Lead creation with invalid data types
        invalid_data_lead = {
            "project_title": "Valid Project Title",
            "lead_source": "Invalid Source",  # Invalid enum value
            "expected_revenue": "not_a_number",  # Invalid data type
            "company_id": "not_an_integer",  # Invalid data type
            "contacts": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "invalid-email",  # Invalid email format
                    "primary_phone": "123"  # Invalid phone format
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_data_lead)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Invalid Data Types", True, 
                            "Validation correctly rejected lead with invalid data types")
            else:
                self.log_test("Validation - Invalid Data Types", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Invalid Data Types", False, f"Request failed: {str(e)}")

    def run_enhanced_leads_tests(self):
        """Run all enhanced leads functionality tests"""
        print("🚀 Starting Enhanced Leads Functionality Testing")
        print(f"Backend URL: {self.base_url}")
        
        # First authenticate to get JWT token
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with protected endpoint tests.")
            return
        
        # Run focused test suites
        self.test_authentication_permissions()
        self.test_companies_api()
        self.test_contacts_api()
        self.test_leads_functionality()
        self.test_lead_conversion_workflow()
        self.test_validation_scenarios()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🏁 ENHANCED LEADS FUNCTIONALITY TEST SUMMARY")
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
    tester = EnhancedLeadsTester()
    tester.run_enhanced_leads_tests()
    
    # Exit with appropriate code
    passed, failed = tester.print_summary()
    sys.exit(0 if failed == 0 else 1)