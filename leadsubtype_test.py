#!/usr/bin/env python3
"""
Lead Management API Testing with leadSubType and tenderDetails functionality
Focus on testing the new lead form fields and data transformation
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime, date

# Backend URL from frontend environment
BACKEND_URL = "https://swayatta-crm.preview.emergentagent.com"
TEST_SESSION_ID = "test_session_123"

class LeadSubTypeTenderDetailsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.jwt_token = None
        self.auth_headers = {}
        self.test_results = {}
        self.created_lead_ids = []
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
        
        # First try to get existing companies
        try:
            response = self.make_request("GET", "/api/companies/?skip=0&limit=1", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("companies"):
                    companies = data["data"]["companies"]
                    if companies:
                        self.created_company_id = companies[0].get("id")
                        self.log_test("Setup - Use Existing Company", True, f"Using existing company ID: {self.created_company_id}")
                        return
        except Exception:
            pass
        
        # Create test company if none exist
        company_data = {
            "name": "Government Technology Solutions Ltd",
            "industry": "Information Technology",
            "website": "https://govtechsolutions.in",
            "phone": "+91-11-23456789",
            "email": "info@govtechsolutions.in",
            "address": {
                "street": "Block A, Technology Hub",
                "city": "New Delhi",
                "state": "Delhi",
                "country": "India",
                "postal_code": "110001"
            },
            "company_type": "Private Limited",
            "annual_revenue": 75000000.00,
            "employee_count": 200,
            "description": "Leading government technology solutions provider"
        }
        
        try:
            response = self.make_request("POST", "/api/companies/", headers=self.auth_headers, data=company_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    self.created_company_id = data["data"]["id"]
                    self.log_test("Setup - Create Company", True, "Test company created successfully")
                else:
                    self.log_test("Setup - Create Company", False, "Invalid create response", data)
            else:
                self.log_test("Setup - Create Company", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Setup - Create Company", False, f"Request failed: {str(e)}")

    def test_create_lead_with_tender_subtype(self):
        """Test creating leads with leadSubType = TENDER and complete tenderDetails"""
        print("\n=== Testing Lead Creation with TENDER SubType ===")
        
        if not self.created_company_id:
            self.log_test("TENDER Lead - Prerequisites", False, "No company available for lead creation")
            return
        
        # Test data with leadSubType = TENDER and complete tenderDetails
        tender_lead_data = {
            "project_title": "Digital India Initiative - E-Governance Platform",
            "lead_source": "Direct Marketing",
            "leadSubType": "TENDER",  # Frontend format
            "tender_sub_type": "Open Tender",
            "products_services": ["E-Governance Platform", "Digital Identity Management", "Cloud Infrastructure"],
            "company_id": self.created_company_id,
            "sub_business_type": "Government Solutions",
            "end_customer_id": self.created_company_id,
            "end_customer_region": "North India",
            "partner_involved": False,
            "partners_data": [],
            "tender_fee": 125000.00,
            "currency": "INR",
            "submission_type": "Online",
            "tender_authority": "National Informatics Centre",
            "tender_for": "Ministry of Electronics and Information Technology",
            "tenderDetails": {  # Frontend format
                "tenderId": "NIC/MEITY/2024/DIG-001",
                "authority": "National Informatics Centre, Delhi",
                "bidDueDate": "2025-02-15"
            },
            "emd_required": True,
            "emd_amount": 250000.00,
            "emd_currency": "INR",
            "bg_required": True,
            "bg_amount": 1250000.00,
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
                    "criteria_description": "Minimum 10 years experience in government e-governance projects"
                }
            ],
            "expected_revenue": 15000000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2025-02-20",
            "competitors": [
                {
                    "name": "TCS Government Solutions",
                    "description": "Major competitor with extensive government portfolio"
                }
            ],
            "documents": [],
            "status": "New",
            "priority": "High",
            "qualification_notes": "High-value government tender with confirmed budget allocation.",
            "lead_score": 92,
            "contacts": [
                {
                    "designation": "Director (IT)",
                    "salutation": "Dr.",
                    "first_name": "Rajesh",
                    "middle_name": "Kumar",
                    "last_name": "Sharma",
                    "email": "rajesh.sharma@nic.in",
                    "primary_phone": "+91-11-24305000",
                    "decision_maker": True,
                    "decision_maker_percentage": 85,
                    "comments": "Primary technical decision maker for e-governance projects"
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=tender_lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    lead_id = data["data"]["id"]
                    self.created_lead_ids.append(lead_id)
                    self.log_test("TENDER Lead - Create", True, 
                                f"TENDER lead created successfully with ID: {lead_id}")
                    return lead_id
                else:
                    self.log_test("TENDER Lead - Create", False, "Invalid create response", data)
            else:
                self.log_test("TENDER Lead - Create", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("TENDER Lead - Create", False, f"Request failed: {str(e)}")
        
        return None

    def test_create_lead_with_non_tender_subtype(self):
        """Test creating leads with leadSubType = NON_TENDER (tenderDetails should be optional)"""
        print("\n=== Testing Lead Creation with NON_TENDER SubType ===")
        
        if not self.created_company_id:
            self.log_test("NON_TENDER Lead - Prerequisites", False, "No company available for lead creation")
            return
        
        # Test data with leadSubType = NON_TENDER and no tenderDetails
        non_tender_lead_data = {
            "project_title": "Enterprise CRM Solution for Private Sector",
            "lead_source": "Referral",
            "leadSubType": "NON_TENDER",  # Frontend format
            "tender_sub_type": "Single Tender",
            "products_services": ["CRM Software", "Implementation Services", "Training"],
            "company_id": self.created_company_id,
            "sub_business_type": "Enterprise Solutions",
            "end_customer_id": self.created_company_id,
            "end_customer_region": "West India",
            "partner_involved": False,
            "partners_data": [],
            # No tenderDetails for NON_TENDER
            "emd_required": False,
            "bg_required": False,
            "important_dates": [
                {
                    "label": "Proposal Submission",
                    "key": "proposal_date",
                    "value": "2025-01-30"
                }
            ],
            "clauses": [
                {
                    "clause_type": "Commercial",
                    "criteria_description": "Flexible payment terms and competitive pricing"
                }
            ],
            "expected_revenue": 3500000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2025-02-10",
            "competitors": [
                {
                    "name": "Salesforce",
                    "description": "Leading CRM platform provider"
                }
            ],
            "documents": [],
            "status": "New",
            "priority": "Medium",
            "qualification_notes": "Direct enterprise client with immediate CRM needs. Budget confirmed.",
            "lead_score": 78,
            "contacts": [
                {
                    "designation": "IT Manager",
                    "salutation": "Ms.",
                    "first_name": "Priya",
                    "middle_name": "",
                    "last_name": "Patel",
                    "email": "priya.patel@enterprise.com",
                    "primary_phone": "+91-22-12345678",
                    "decision_maker": True,
                    "decision_maker_percentage": 70,
                    "comments": "IT decision maker for CRM implementation"
                }
            ]
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=non_tender_lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    lead_id = data["data"]["id"]
                    self.created_lead_ids.append(lead_id)
                    self.log_test("NON_TENDER Lead - Create", True, 
                                f"NON_TENDER lead created successfully with ID: {lead_id}")
                    return lead_id
                else:
                    self.log_test("NON_TENDER Lead - Create", False, "Invalid create response", data)
            else:
                self.log_test("NON_TENDER Lead - Create", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("NON_TENDER Lead - Create", False, f"Request failed: {str(e)}")
        
        return None

    def test_validation_errors_missing_tender_details(self):
        """Test validation errors for missing tenderDetails when leadSubType requires it"""
        print("\n=== Testing Validation: Missing Tender Details ===")
        
        if not self.created_company_id:
            self.log_test("Validation - Prerequisites", False, "No company available for validation testing")
            return
        
        # Test data with leadSubType = TENDER but missing tenderDetails
        invalid_tender_lead_data = {
            "project_title": "Invalid Tender Lead - Missing Details",
            "lead_source": "Direct Marketing",
            "leadSubType": "TENDER",  # Requires tenderDetails
            "tender_sub_type": "Open Tender",
            "products_services": ["Software Solution"],
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
                    "decision_maker_percentage": 100
                }
            ]
            # Missing tenderDetails - should cause validation error
        }
        
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.auth_headers, data=invalid_tender_lead_data)
            if response.status_code in [400, 422]:
                self.log_test("Validation - Missing Tender Details", True, 
                            "Validation correctly rejected TENDER lead without tenderDetails")
            else:
                self.log_test("Validation - Missing Tender Details", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Validation - Missing Tender Details", False, f"Request failed: {str(e)}")

    def test_get_leads_format_transformation(self):
        """Test GET /api/leads returns data in both frontend format (leadSubType, tenderDetails) and backend format"""
        print("\n=== Testing GET /api/leads Format Transformation ===")
        
        try:
            response = self.make_request("GET", "/api/leads/?skip=0&limit=10", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("leads"):
                    leads = data["data"]["leads"]
                    if leads:
                        # Check first lead for format transformation
                        first_lead = leads[0]
                        
                        # Check for both frontend and backend format fields
                        has_frontend_format = "leadSubType" in first_lead and "tenderDetails" in first_lead
                        has_backend_format = "lead_sub_type" in first_lead
                        
                        if has_frontend_format and has_backend_format:
                            self.log_test("GET Leads - Format Transformation", True, 
                                        f"Leads returned with both frontend and backend formats. Found {len(leads)} leads.")
                            
                            # Verify tenderDetails structure for TENDER leads
                            for lead in leads:
                                if lead.get("leadSubType") == "TENDER":
                                    tender_details = lead.get("tenderDetails", {})
                                    if "tenderId" in tender_details or "authority" in tender_details or "bidDueDate" in tender_details:
                                        self.log_test("GET Leads - Tender Details Structure", True, 
                                                    "TENDER lead contains properly structured tenderDetails")
                                        break
                        else:
                            self.log_test("GET Leads - Format Transformation", False, 
                                        f"Missing format fields. Frontend: {has_frontend_format}, Backend: {has_backend_format}")
                    else:
                        self.log_test("GET Leads - Format Transformation", True, 
                                    "No leads found, but API response is valid")
                else:
                    self.log_test("GET Leads - Format Transformation", False, "Invalid leads list response", data)
            else:
                self.log_test("GET Leads - Format Transformation", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET Leads - Format Transformation", False, f"Request failed: {str(e)}")

    def test_get_lead_by_id_format_transformation(self):
        """Test GET /api/leads/{id} returns individual lead with proper format transformation"""
        print("\n=== Testing GET /api/leads/{id} Format Transformation ===")
        
        if not self.created_lead_ids:
            self.log_test("GET Lead by ID - Prerequisites", False, "No created leads available for testing")
            return
        
        lead_id = self.created_lead_ids[0]
        
        try:
            response = self.make_request("GET", f"/api/leads/{lead_id}", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    lead = data["data"]
                    
                    # Check for both frontend and backend format fields
                    has_frontend_format = "leadSubType" in lead and "tenderDetails" in lead
                    has_backend_format = "lead_sub_type" in lead
                    
                    if has_frontend_format and has_backend_format:
                        self.log_test("GET Lead by ID - Format Transformation", True, 
                                    f"Lead {lead_id} returned with both frontend and backend formats")
                        
                        # Verify tenderDetails structure if it's a TENDER lead
                        if lead.get("leadSubType") == "TENDER":
                            tender_details = lead.get("tenderDetails", {})
                            required_fields = ["tenderId", "authority", "bidDueDate"]
                            missing_fields = [field for field in required_fields if not tender_details.get(field)]
                            
                            if not missing_fields:
                                self.log_test("GET Lead by ID - Tender Details Complete", True, 
                                            "TENDER lead contains all required tenderDetails fields")
                            else:
                                self.log_test("GET Lead by ID - Tender Details Complete", False, 
                                            f"Missing tenderDetails fields: {missing_fields}")
                    else:
                        self.log_test("GET Lead by ID - Format Transformation", False, 
                                    f"Missing format fields. Frontend: {has_frontend_format}, Backend: {has_backend_format}")
                else:
                    self.log_test("GET Lead by ID - Format Transformation", False, "Invalid lead response", data)
            else:
                self.log_test("GET Lead by ID - Format Transformation", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET Lead by ID - Format Transformation", False, f"Request failed: {str(e)}")

    def test_update_lead_with_tender_details_changes(self):
        """Test PUT /api/leads/{id} for updating leads with leadSubType and tenderDetails changes"""
        print("\n=== Testing PUT /api/leads/{id} with Tender Details Changes ===")
        
        if not self.created_lead_ids:
            self.log_test("UPDATE Lead - Prerequisites", False, "No created leads available for testing")
            return
        
        lead_id = self.created_lead_ids[0]
        
        # Update data with changes to leadSubType and tenderDetails
        update_data = {
            "leadSubType": "PRE_TENDER",  # Change from TENDER to PRE_TENDER
            "tenderDetails": {
                "tenderId": "NIC/MEITY/2024/DIG-001-UPDATED",
                "authority": "National Informatics Centre, Mumbai",
                "bidDueDate": "2025-03-01"
            },
            "qualification_notes": "Updated after pre-tender meeting. Requirements clarified and timeline extended.",
            "lead_score": 95,
            "status": "Qualified"
        }
        
        try:
            response = self.make_request("PUT", f"/api/leads/{lead_id}", headers=self.auth_headers, data=update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("UPDATE Lead - Tender Details", True, 
                                f"Lead {lead_id} updated successfully with new leadSubType and tenderDetails")
                    
                    # Verify the update by fetching the lead
                    self.verify_lead_update(lead_id, update_data)
                else:
                    self.log_test("UPDATE Lead - Tender Details", False, "Invalid update response", data)
            else:
                self.log_test("UPDATE Lead - Tender Details", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("UPDATE Lead - Tender Details", False, f"Request failed: {str(e)}")

    def verify_lead_update(self, lead_id: str, expected_data: dict):
        """Verify that lead update was successful by fetching the updated lead"""
        try:
            response = self.make_request("GET", f"/api/leads/{lead_id}", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    lead = data["data"]
                    
                    # Check if leadSubType was updated
                    if lead.get("leadSubType") == expected_data.get("leadSubType"):
                        self.log_test("UPDATE Verification - LeadSubType", True, 
                                    f"LeadSubType correctly updated to {expected_data.get('leadSubType')}")
                    else:
                        self.log_test("UPDATE Verification - LeadSubType", False, 
                                    f"LeadSubType not updated. Expected: {expected_data.get('leadSubType')}, Got: {lead.get('leadSubType')}")
                    
                    # Check if tenderDetails were updated
                    tender_details = lead.get("tenderDetails", {})
                    expected_tender_details = expected_data.get("tenderDetails", {})
                    
                    if tender_details.get("tenderId") == expected_tender_details.get("tenderId"):
                        self.log_test("UPDATE Verification - Tender Details", True, 
                                    "TenderDetails correctly updated")
                    else:
                        self.log_test("UPDATE Verification - Tender Details", False, 
                                    f"TenderDetails not updated correctly")
                else:
                    self.log_test("UPDATE Verification", False, "Could not fetch updated lead")
        except Exception as e:
            self.log_test("UPDATE Verification", False, f"Verification failed: {str(e)}")

    def run_leadsubtype_tenderdetails_tests(self):
        """Run all leadSubType and tenderDetails functionality tests"""
        print("🚀 Starting Lead SubType and Tender Details Testing")
        print(f"Backend URL: {self.base_url}")
        
        # First authenticate to get JWT token
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with protected endpoint tests.")
            return
        
        # Setup test data
        self.setup_test_data()
        
        # Run focused test suites for leadSubType and tenderDetails
        self.test_create_lead_with_tender_subtype()
        self.test_create_lead_with_non_tender_subtype()
        self.test_validation_errors_missing_tender_details()
        self.test_get_leads_format_transformation()
        self.test_get_lead_by_id_format_transformation()
        self.test_update_lead_with_tender_details_changes()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🏁 LEAD SUBTYPE AND TENDER DETAILS TEST SUMMARY")
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
    tester = LeadSubTypeTenderDetailsTester()
    tester.run_leadsubtype_tenderdetails_tests()
    
    # Exit with appropriate code
    passed, failed = tester.print_summary()
    sys.exit(0 if failed == 0 else 1)