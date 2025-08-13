#!/usr/bin/env python3
"""
Lead Management API Testing for leadSubType and tenderDetails
Focus on testing the new frontend data structure integration
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

# Backend URL from frontend environment
BACKEND_URL = "https://swayatta-crm.preview.emergentagent.com"
TEST_SESSION_ID = "test_session_123"

class LeadSubTypeTenderTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.jwt_token = None
        self.auth_headers = {}
        self.test_results = {}
        self.created_lead_id = None
        self.created_company_id = None
        
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

    def setup_test_data(self):
        """Setup required test data (company)"""
        print("\n=== Setting up Test Data ===")
        
        # Get existing companies first
        try:
            response = self.make_request("GET", "/api/companies/?skip=0&limit=1", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("companies"):
                    companies = data["data"]["companies"]
                    if companies:
                        self.created_company_id = companies[0].get("id")
                        self.log_test("Setup - Get Company", True, f"Using existing company ID: {self.created_company_id}")
                        return True
        except Exception as e:
            pass
        
        # Create test company if none exist
        company_data = {
            "name": "TenderTech Solutions Pvt Ltd",
            "industry": "Information Technology",
            "website": "https://tendertech.com",
            "phone": "+91-11-98765432",
            "email": "info@tendertech.com",
            "address": {
                "street": "456 Business Park",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400001"
            },
            "company_type": "Private Limited",
            "annual_revenue": 75000000.00,
            "employee_count": 200,
            "description": "Leading tender management solutions provider"
        }
        
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=company_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.created_company_id = data["data"]["id"]
                    self.log_test("Setup - Create Company", True, "Test company created successfully")
                    return True
                else:
                    self.log_test("Setup - Create Company", False, "Invalid create response", data)
                    return False
            else:
                self.log_test("Setup - Create Company", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Setup - Create Company", False, f"Request failed: {str(e)}")
            return False

    def test_create_lead_with_tender_subtype(self):
        """Test CREATE Lead API with different leadSubType values and tenderDetails"""
        print("\n=== Testing CREATE Lead API with leadSubType and tenderDetails ===")
        
        if not self.created_company_id:
            self.log_test("Create Lead - Prerequisites", False, "No company available for lead creation")
            return
        
        # Test Case 1: TENDER leadSubType with complete tenderDetails
        tender_lead_data = {
            "project_title": "Government E-Governance Platform Tender",
            "lead_source": "Direct Marketing",
            "leadSubType": "TENDER",  # Frontend format
            "tender_sub_type": "Open Tender",
            "products_services": ["CRM Software", "Implementation Services"],
            "company_id": self.created_company_id,
            "sub_business_type": "Government Solutions",
            "end_customer_id": self.created_company_id,
            "end_customer_region": "North India",
            "partner_involved": False,
            "partners_data": [],
            "tender_fee": 50000.00,
            "currency": "INR",
            "submission_type": "Online",
            "tender_authority": "Department of IT",
            "tender_for": "Ministry of Electronics and IT",
            "tenderDetails": {  # Frontend format
                "tenderId": "TENDER-2025-GOV-001",
                "authority": "Government of India - Department of IT",
                "bidDueDate": "2025-02-15"
            },
            "emd_required": True,
            "emd_amount": 100000.00,
            "emd_currency": "INR",
            "bg_required": True,
            "bg_amount": 500000.00,
            "bg_currency": "INR",
            "important_dates": [
                {
                    "label": "Pre-bid Meeting",
                    "key": "pre_bid_date",
                    "value": "2025-01-20"
                }
            ],
            "clauses": [
                {
                    "clause_type": "Technical",
                    "criteria_description": "Minimum 5 years experience in government projects"
                }
            ],
            "expected_revenue": 5000000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2025-02-20",
            "competitors": [
                {
                    "name": "GovTech Solutions",
                    "description": "Major competitor in government sector"
                }
            ],
            "documents": [],
            "status": "New",
            "priority": "High",
            "qualification_notes": "High-value government tender with confirmed budget allocation.",
            "lead_score": 85,
            "contacts": [
                {
                    "designation": "Joint Secretary",
                    "salutation": "Dr.",
                    "first_name": "Rajesh",
                    "middle_name": "Kumar",
                    "last_name": "Sharma",
                    "email": "rajesh.sharma@gov.in",
                    "primary_phone": "+91-11-23456789",
                    "decision_maker": True,
                    "decision_maker_percentage": 85,
                    "comments": "Primary decision maker for IT procurement"
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=tender_lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.created_lead_id = data["data"]["id"]
                    self.log_test("Create Lead - TENDER with tenderDetails", True, 
                                f"Lead created successfully with ID: {self.created_lead_id}")
                else:
                    self.log_test("Create Lead - TENDER with tenderDetails", False, "Invalid create response", data)
            else:
                self.log_test("Create Lead - TENDER with tenderDetails", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Lead - TENDER with tenderDetails", False, f"Request failed: {str(e)}")
        
        # Test Case 2: NON_TENDER leadSubType (tenderDetails should be optional)
        non_tender_lead_data = {
            "project_title": "Direct Sales CRM Implementation",
            "lead_source": "Referral",
            "leadSubType": "NON_TENDER",  # Frontend format
            "tender_sub_type": "Open Tender",  # This might be ignored for NON_TENDER
            "products_services": ["CRM Software", "Training"],
            "company_id": self.created_company_id,
            "sub_business_type": "Enterprise Solutions",
            "end_customer_id": self.created_company_id,
            "end_customer_region": "West India",
            "partner_involved": False,
            "partners_data": [],
            "expected_revenue": 2500000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2025-01-30",
            "status": "New",
            "priority": "Medium",
            "qualification_notes": "Direct sales opportunity with existing client.",
            "lead_score": 70,
            "contacts": [
                {
                    "designation": "IT Manager",
                    "salutation": "Mr.",
                    "first_name": "Amit",
                    "last_name": "Patel",
                    "email": "amit.patel@company.com",
                    "primary_phone": "+91-22-87654321",
                    "decision_maker": True,
                    "decision_maker_percentage": 75,
                    "comments": "IT decision maker"
                }
            ]
            # Note: No tenderDetails provided for NON_TENDER
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=non_tender_lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.log_test("Create Lead - NON_TENDER without tenderDetails", True, 
                                "NON_TENDER lead created successfully without tenderDetails")
                else:
                    self.log_test("Create Lead - NON_TENDER without tenderDetails", False, "Invalid create response", data)
            else:
                self.log_test("Create Lead - NON_TENDER without tenderDetails", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Lead - NON_TENDER without tenderDetails", False, f"Request failed: {str(e)}")

    def test_create_lead_validation_scenarios(self):
        """Test validation scenarios for leadSubType and tenderDetails"""
        print("\n=== Testing Validation Scenarios ===")
        
        if not self.created_company_id:
            return
        
        # Test Case 1: TENDER leadSubType without tenderDetails (should fail)
        invalid_tender_data = {
            "project_title": "Invalid Tender Lead",
            "lead_source": "Direct Marketing",
            "leadSubType": "TENDER",  # Requires tenderDetails
            "tender_sub_type": "Open Tender",
            "products_services": ["CRM Software"],
            "company_id": self.created_company_id,
            "end_customer_id": self.created_company_id,
            "expected_revenue": 1000000.00,
            "contacts": [
                {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 80
                }
            ]
            # Missing tenderDetails for TENDER type
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_tender_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - TENDER without tenderDetails", True, 
                            "Correctly rejected TENDER lead without tenderDetails")
            else:
                self.log_test("Validation - TENDER without tenderDetails", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - TENDER without tenderDetails", False, f"Request failed: {str(e)}")
        
        # Test Case 2: Invalid leadSubType value
        invalid_subtype_data = {
            "project_title": "Invalid SubType Lead",
            "lead_source": "Direct Marketing",
            "leadSubType": "INVALID_TYPE",  # Invalid value
            "tender_sub_type": "Open Tender",
            "products_services": ["CRM Software"],
            "company_id": self.created_company_id,
            "end_customer_id": self.created_company_id,
            "expected_revenue": 1000000.00,
            "contacts": [
                {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 80
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_subtype_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Invalid leadSubType", True, 
                            "Correctly rejected lead with invalid leadSubType")
            else:
                self.log_test("Validation - Invalid leadSubType", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Invalid leadSubType", False, f"Request failed: {str(e)}")
        
        # Test Case 3: Invalid tenderDetails field values
        invalid_tender_details_data = {
            "project_title": "Invalid Tender Details Lead",
            "lead_source": "Direct Marketing",
            "leadSubType": "PRE_TENDER",
            "tender_sub_type": "Open Tender",
            "products_services": ["CRM Software"],
            "company_id": self.created_company_id,
            "end_customer_id": self.created_company_id,
            "expected_revenue": 1000000.00,
            "tenderDetails": {
                "tenderId": "A",  # Too short (should be 2-100 chars)
                "authority": "B",  # Too short (should be 2-200 chars)
                "bidDueDate": "invalid-date"  # Invalid date format
            },
            "contacts": [
                {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 80
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_tender_details_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Invalid tenderDetails values", True, 
                            "Correctly rejected lead with invalid tenderDetails values")
            else:
                self.log_test("Validation - Invalid tenderDetails values", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Invalid tenderDetails values", False, f"Request failed: {str(e)}")

    def test_read_lead_apis(self):
        """Test READ Lead APIs and verify data mapping"""
        print("\n=== Testing READ Lead APIs and Data Mapping ===")
        
        if not self.created_lead_id:
            self.log_test("Read Lead - Prerequisites", False, "No lead available for reading")
            return
        
        # Test Case 1: Get Lead by ID
        try:
            response = self.make_request("GET", f"/api/leads/{self.created_lead_id}", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    lead_data = data["data"]
                    
                    # Verify frontend format fields are present
                    has_lead_sub_type = "leadSubType" in lead_data
                    has_tender_details = "tenderDetails" in lead_data
                    
                    # Verify backend format fields are also present
                    has_backend_lead_sub_type = "lead_sub_type" in lead_data
                    
                    # Verify tenderDetails structure
                    tender_details_valid = False
                    if has_tender_details and lead_data["tenderDetails"]:
                        td = lead_data["tenderDetails"]
                        tender_details_valid = (
                            "tenderId" in td and 
                            "authority" in td and 
                            "bidDueDate" in td
                        )
                    
                    if has_lead_sub_type and has_tender_details and has_backend_lead_sub_type and tender_details_valid:
                        self.log_test("Read Lead - Data Mapping", True, 
                                    "Lead data correctly mapped between frontend and backend formats")
                    else:
                        self.log_test("Read Lead - Data Mapping", False, 
                                    f"Data mapping issues: leadSubType={has_lead_sub_type}, tenderDetails={has_tender_details}, backend_format={has_backend_lead_sub_type}, tender_valid={tender_details_valid}", lead_data)
                else:
                    self.log_test("Read Lead - Data Mapping", False, "Invalid lead response", data)
            else:
                self.log_test("Read Lead - Data Mapping", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Read Lead - Data Mapping", False, f"Request failed: {str(e)}")
        
        # Test Case 2: Get All Leads (List)
        try:
            response = self.make_request("GET", "/api/leads/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("leads"):
                    leads = data["data"]["leads"]
                    if leads:
                        # Check first lead for proper data mapping
                        first_lead = leads[0]
                        has_frontend_format = "leadSubType" in first_lead and "tenderDetails" in first_lead
                        has_backend_format = "lead_sub_type" in first_lead
                        
                        if has_frontend_format and has_backend_format:
                            self.log_test("Read Leads - List Data Mapping", True, 
                                        f"Leads list correctly mapped ({len(leads)} leads)")
                        else:
                            self.log_test("Read Leads - List Data Mapping", False, 
                                        "Leads list missing proper data mapping", first_lead)
                    else:
                        self.log_test("Read Leads - List Data Mapping", False, "No leads found in list")
                else:
                    self.log_test("Read Leads - List Data Mapping", False, "Invalid leads list response", data)
            else:
                self.log_test("Read Leads - List Data Mapping", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Read Leads - List Data Mapping", False, f"Request failed: {str(e)}")

    def test_update_lead_api(self):
        """Test UPDATE Lead API with leadSubType and tenderDetails"""
        print("\n=== Testing UPDATE Lead API ===")
        
        if not self.created_lead_id:
            self.log_test("Update Lead - Prerequisites", False, "No lead available for updating")
            return
        
        # Test Case 1: Update leadSubType and tenderDetails
        update_data = {
            "leadSubType": "POST_TENDER",  # Change from TENDER to POST_TENDER
            "tenderDetails": {
                "tenderId": "TENDER-2025-GOV-001-UPDATED",
                "authority": "Updated Government Authority",
                "bidDueDate": "2025-03-01"
            },
            "qualification_notes": "Updated after post-tender discussions",
            "lead_score": 90
        }
        
        try:
            response = self.make_request("PUT", f"/api/leads/{self.created_lead_id}", 
                                       headers=self.auth_headers, data=update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("Update Lead - leadSubType and tenderDetails", True, 
                                "Lead updated successfully with new leadSubType and tenderDetails")
                    
                    # Verify the update by reading the lead back
                    self.verify_lead_update()
                else:
                    self.log_test("Update Lead - leadSubType and tenderDetails", False, "Invalid update response", data)
            else:
                self.log_test("Update Lead - leadSubType and tenderDetails", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Update Lead - leadSubType and tenderDetails", False, f"Request failed: {str(e)}")

    def verify_lead_update(self):
        """Verify that the lead update was successful"""
        try:
            response = self.make_request("GET", f"/api/leads/{self.created_lead_id}", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    lead_data = data["data"]
                    
                    # Check if leadSubType was updated
                    updated_lead_sub_type = lead_data.get("leadSubType") == "POST_TENDER"
                    
                    # Check if tenderDetails were updated
                    tender_details = lead_data.get("tenderDetails", {})
                    updated_tender_id = tender_details.get("tenderId") == "TENDER-2025-GOV-001-UPDATED"
                    updated_authority = tender_details.get("authority") == "Updated Government Authority"
                    
                    if updated_lead_sub_type and updated_tender_id and updated_authority:
                        self.log_test("Update Verification", True, 
                                    "Lead update verification successful - all fields updated correctly")
                    else:
                        self.log_test("Update Verification", False, 
                                    f"Update verification failed: leadSubType={updated_lead_sub_type}, tenderId={updated_tender_id}, authority={updated_authority}")
                else:
                    self.log_test("Update Verification", False, "Invalid verification response", data)
            else:
                self.log_test("Update Verification", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Update Verification", False, f"Verification failed: {str(e)}")

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n=== Testing Edge Cases ===")
        
        if not self.created_company_id:
            return
        
        # Test Case 1: PRE_TENDER with minimal tenderDetails
        pre_tender_data = {
            "project_title": "Pre-Tender Inquiry Lead",
            "lead_source": "Event",
            "leadSubType": "PRE_TENDER",
            "tender_sub_type": "Limited Tender",
            "products_services": ["Consultation"],
            "company_id": self.created_company_id,
            "end_customer_id": self.created_company_id,
            "expected_revenue": 500000.00,
            "tenderDetails": {
                "tenderId": "PT-2025-001",  # Minimal valid length
                "authority": "Local Authority",  # Minimal valid length
                "bidDueDate": "2025-01-25"
            },
            "contacts": [
                {
                    "first_name": "Pre",
                    "last_name": "Tender",
                    "email": "pretender@example.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 60
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=pre_tender_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.log_test("Edge Case - PRE_TENDER minimal data", True, 
                                "PRE_TENDER lead created with minimal valid tenderDetails")
                else:
                    self.log_test("Edge Case - PRE_TENDER minimal data", False, "Invalid create response", data)
            else:
                self.log_test("Edge Case - PRE_TENDER minimal data", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Edge Case - PRE_TENDER minimal data", False, f"Request failed: {str(e)}")
        
        # Test Case 2: Maximum length tenderDetails fields
        max_length_data = {
            "project_title": "Maximum Length Tender Details Test",
            "lead_source": "Advertisement",
            "leadSubType": "TENDER",
            "tender_sub_type": "GeM Tender",
            "products_services": ["Enterprise Software"],
            "company_id": self.created_company_id,
            "end_customer_id": self.created_company_id,
            "expected_revenue": 10000000.00,
            "tenderDetails": {
                "tenderId": "T" * 100,  # Maximum length (100 chars)
                "authority": "A" * 200,  # Maximum length (200 chars)
                "bidDueDate": "2025-12-31"
            },
            "contacts": [
                {
                    "first_name": "Max",
                    "last_name": "Length",
                    "email": "maxlength@example.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 90
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=max_length_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.log_test("Edge Case - Maximum length tenderDetails", True, 
                                "Lead created with maximum length tenderDetails fields")
                else:
                    self.log_test("Edge Case - Maximum length tenderDetails", False, "Invalid create response", data)
            else:
                self.log_test("Edge Case - Maximum length tenderDetails", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Edge Case - Maximum length tenderDetails", False, f"Request failed: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests for leadSubType and tenderDetails"""
        print("🚀 Starting Lead Management API Testing for leadSubType and tenderDetails")
        print(f"Backend URL: {self.base_url}")
        
        # First authenticate to get JWT token
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with protected endpoint tests.")
            return
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Test data setup failed. Cannot proceed with lead tests.")
            return
        
        # Run focused test suites
        self.test_create_lead_with_tender_subtype()
        self.test_create_lead_validation_scenarios()
        self.test_read_lead_apis()
        self.test_update_lead_api()
        self.test_edge_cases()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 LEAD MANAGEMENT API TEST SUMMARY - leadSubType & tenderDetails")
        print("="*80)
        
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
        
        print("\n" + "="*80)
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = LeadSubTypeTenderTester()
    tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    passed, failed = tester.print_summary()
    sys.exit(0 if failed == 0 else 1)