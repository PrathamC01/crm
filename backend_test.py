#!/usr/bin/env python3
"""
Comprehensive CRM Backend Testing Suite
Tests all major CRM functionality including database, authentication, and CRUD operations
"""

import requests
import json
import sys
from datetime import datetime, date
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api"

class CRMTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.current_user = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if token exists
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            # Try the health endpoint without /api prefix
            url = f"{BASE_URL}/health"
            response = self.session.get(url)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Health Check", True, "Backend is healthy")
                    return True
                else:
                    self.log_test("Health Check", False, f"Health check failed: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Health endpoint returned {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = self.make_request("GET", "")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "CRM" in data.get("message", ""):
                    self.log_test("Root Endpoint", True, "Root endpoint working correctly")
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected root response: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"Root endpoint returned {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_authentication(self):
        """Test authentication with different user roles"""
        test_users = [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "reviewer", "password": "reviewer123", "role": "reviewer"},
            {"username": "sales", "password": "sales123", "role": "sales"}
        ]
        
        auth_success = False
        
        for user in test_users:
            try:
                login_data = {
                    "email_or_username": user["username"],
                    "password": user["password"]
                }
                
                response = self.make_request("POST", "/login", login_data)
                
                if response and response.status_code == 200:
                    data = response.json()
                    if data.get("status") == True and "token" in data.get("data", {}):
                        self.log_test(f"Authentication - {user['role']}", True, f"Login successful for {user['username']}")
                        
                        # Store admin token for subsequent tests
                        if user["role"] == "admin":
                            self.auth_token = data["data"]["token"]
                            self.current_user = data["data"]
                            auth_success = True
                    else:
                        self.log_test(f"Authentication - {user['role']}", False, f"Login failed for {user['username']}: {data}")
                else:
                    self.log_test(f"Authentication - {user['role']}", False, f"Login request failed for {user['username']}: {response.status_code if response else 'No response'}")
                    
            except Exception as e:
                self.log_test(f"Authentication - {user['role']}", False, f"Exception during login for {user['username']}: {str(e)}")
        
        return auth_success

    def test_dashboard(self):
        """Test dashboard endpoint"""
        if not self.auth_token:
            self.log_test("Dashboard", False, "No auth token available")
            return False
            
        try:
            response = self.make_request("GET", "/dashboard")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Dashboard", True, "Dashboard data retrieved successfully")
                    return True
                else:
                    self.log_test("Dashboard", False, f"Dashboard failed: {data}")
                    return False
            else:
                self.log_test("Dashboard", False, f"Dashboard returned {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_companies_crud(self):
        """Test Companies CRUD operations"""
        if not self.auth_token:
            self.log_test("Companies CRUD", False, "No auth token available")
            return False
            
        company_id = None
        
        try:
            # Test CREATE
            company_data = {
                "name": "Test Company Ltd",
                "gst_number": "29TESTCO1234F1Z1",
                "pan_number": "TESTCO1234",
                "industry_category": "Technology",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "country": "India",
                "postal_code": "123456",
                "website": "www.testcompany.com",
                "description": "Test company for CRM testing"
            }
            
            response = self.make_request("POST", "/companies", company_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    company_id = data["data"]["id"]
                    self.log_test("Companies CREATE", True, f"Company created with ID: {company_id}")
                else:
                    self.log_test("Companies CREATE", False, f"Company creation failed: {data}")
                    return False
            else:
                self.log_test("Companies CREATE", False, f"Company creation returned {response.status_code if response else 'No response'}")
                return False
                
            # Test READ
            response = self.make_request("GET", f"/companies/{company_id}")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and data["data"]["name"] == "Test Company Ltd":
                    self.log_test("Companies READ", True, "Company retrieved successfully")
                else:
                    self.log_test("Companies READ", False, f"Company retrieval failed: {data}")
            else:
                self.log_test("Companies READ", False, f"Company retrieval returned {response.status_code if response else 'No response'}")
                
            # Test LIST
            response = self.make_request("GET", "/companies")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "companies" in data.get("data", {}):
                    self.log_test("Companies LIST", True, f"Companies list retrieved with {len(data['data']['companies'])} companies")
                else:
                    self.log_test("Companies LIST", False, f"Companies list failed: {data}")
            else:
                self.log_test("Companies LIST", False, f"Companies list returned {response.status_code if response else 'No response'}")
                
            # Test UPDATE
            update_data = {
                "description": "Updated test company description"
            }
            response = self.make_request("PUT", f"/companies/{company_id}", update_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Companies UPDATE", True, "Company updated successfully")
                else:
                    self.log_test("Companies UPDATE", False, f"Company update failed: {data}")
            else:
                self.log_test("Companies UPDATE", False, f"Company update returned {response.status_code if response else 'No response'}")
                
            return True
            
        except Exception as e:
            self.log_test("Companies CRUD", False, f"Exception: {str(e)}")
            return False

    def test_contacts_crud(self):
        """Test Contacts CRUD operations"""
        if not self.auth_token:
            self.log_test("Contacts CRUD", False, "No auth token available")
            return False
            
        contact_id = None
        
        try:
            # First get a company ID
            response = self.make_request("GET", "/companies")
            if not response or response.status_code != 200:
                self.log_test("Contacts CRUD", False, "Could not get companies for contact test")
                return False
                
            companies_data = response.json()
            if not companies_data.get("status") or not companies_data["data"]["companies"]:
                self.log_test("Contacts CRUD", False, "No companies available for contact test")
                return False
                
            company_id = companies_data["data"]["companies"][0]["id"]
            
            # Test CREATE
            contact_data = {
                "full_name": "John Test Contact",
                "designation": "Test Manager",
                "email": "john.test@testcompany.com",
                "phone_number": "+91-98765-43210",
                "company_id": company_id,
                "role_type": "DECISION_MAKER"
            }
            
            response = self.make_request("POST", "/contacts", contact_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    contact_id = data["data"]["id"]
                    self.log_test("Contacts CREATE", True, f"Contact created with ID: {contact_id}")
                else:
                    self.log_test("Contacts CREATE", False, f"Contact creation failed: {data}")
                    return False
            else:
                self.log_test("Contacts CREATE", False, f"Contact creation returned {response.status_code if response else 'No response'}")
                return False
                
            # Test READ
            response = self.make_request("GET", f"/contacts/{contact_id}")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and data["data"]["full_name"] == "John Test Contact":
                    self.log_test("Contacts READ", True, "Contact retrieved successfully")
                else:
                    self.log_test("Contacts READ", False, f"Contact retrieval failed: {data}")
            else:
                self.log_test("Contacts READ", False, f"Contact retrieval returned {response.status_code if response else 'No response'}")
                
            # Test LIST
            response = self.make_request("GET", "/contacts")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "contacts" in data.get("data", {}):
                    self.log_test("Contacts LIST", True, f"Contacts list retrieved with {len(data['data']['contacts'])} contacts")
                else:
                    self.log_test("Contacts LIST", False, f"Contacts list failed: {data}")
            else:
                self.log_test("Contacts LIST", False, f"Contacts list returned {response.status_code if response else 'No response'}")
                
            return True
            
        except Exception as e:
            self.log_test("Contacts CRUD", False, f"Exception: {str(e)}")
            return False

    def test_leads_crud(self):
        """Test Leads CRUD operations with proper data types"""
        if not self.auth_token:
            self.log_test("Leads CRUD", False, "No auth token available")
            return False
            
        lead_id = None
        
        try:
            # Get company and end customer IDs
            response = self.make_request("GET", "/companies")
            if not response or response.status_code != 200:
                self.log_test("Leads CRUD", False, "Could not get companies for lead test")
                return False
                
            companies_data = response.json()
            if not companies_data.get("status") or len(companies_data["data"]["companies"]) < 2:
                self.log_test("Leads CRUD", False, "Need at least 2 companies for lead test")
                return False
                
            company_id = companies_data["data"]["companies"][0]["id"]
            end_customer_id = companies_data["data"]["companies"][1]["id"]
            
            # Test CREATE with proper data types
            lead_data = {
                "project_title": "Test CRM Integration Project",
                "lead_source": "Direct Marketing",
                "lead_sub_type": "Pre-Tender",
                "tender_sub_type": "Open Tender",
                "products_services": ["CRM Software", "Integration Services"],
                "company_id": company_id,
                "sub_business_type": "Upgrade",
                "end_customer_id": end_customer_id,
                "end_customer_region": "North",
                "partner_involved": True,
                "partners_data": [
                    {
                        "name": "Tech Partner Ltd",
                        "role": "Implementation Partner",
                        "contact": "partner@techpartner.com"
                    }
                ],
                "tender_fee": 50000.00,  # Number, not string
                "currency": "INR",
                "submission_type": "Online",
                "tender_authority": "Government IT Department",
                "tender_for": "CRM System Implementation",
                "emd_required": True,
                "emd_amount": 100000.00,  # Number, not string
                "emd_currency": "INR",
                "bg_required": True,
                "bg_amount": 500000.00,  # Number, not string
                "bg_currency": "INR",
                "important_dates": [
                    {
                        "date_type": "Submission Deadline",
                        "date": "2024-12-31",
                        "description": "Final submission date"
                    }
                ],
                "clauses": [
                    {
                        "clause_type": "Payment Terms",
                        "description": "30-60-90 payment schedule"
                    }
                ],
                "expected_revenue": 2500000.00,  # Number, not string
                "revenue_currency": "INR",
                "convert_to_opportunity_date": "2024-12-15",
                "competitors": [
                    {
                        "name": "Competitor Corp",
                        "strength": "Market presence",
                        "weakness": "Higher pricing"
                    }
                ],
                "documents": [
                    {
                        "document_type": "RFP",
                        "file_path": "/uploads/rfp_document.pdf",
                        "description": "Request for Proposal document"
                    }
                ],
                "status": "New",
                "priority": "High",
                "qualification_notes": "High potential client with clear requirements",
                "contacts": [
                    {
                        "name": "Jane Decision Maker",
                        "email": "jane@endcustomer.com",
                        "phone": "+91-98765-12345",
                        "designation": "IT Director",
                        "decision_maker": True
                    }
                ]
            }
            
            response = self.make_request("POST", "/leads", lead_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    lead_id = data["data"]["id"]
                    self.log_test("Leads CREATE", True, f"Lead created with ID: {lead_id}")
                    
                    # Verify data types are preserved
                    response = self.make_request("GET", f"/leads/{lead_id}")
                    if response and response.status_code == 200:
                        lead_detail = response.json()
                        if lead_detail.get("status") == True:
                            lead_data_returned = lead_detail["data"]
                            
                            # Check that amounts are numbers, not strings
                            if isinstance(lead_data_returned.get("tender_fee"), (int, float)):
                                self.log_test("Leads Data Types - tender_fee", True, "tender_fee is numeric")
                            else:
                                self.log_test("Leads Data Types - tender_fee", False, f"tender_fee is {type(lead_data_returned.get('tender_fee'))}, expected numeric")
                                
                            if isinstance(lead_data_returned.get("expected_revenue"), (int, float)):
                                self.log_test("Leads Data Types - expected_revenue", True, "expected_revenue is numeric")
                            else:
                                self.log_test("Leads Data Types - expected_revenue", False, f"expected_revenue is {type(lead_data_returned.get('expected_revenue'))}, expected numeric")
                                
                            if isinstance(lead_data_returned.get("emd_amount"), (int, float)):
                                self.log_test("Leads Data Types - emd_amount", True, "emd_amount is numeric")
                            else:
                                self.log_test("Leads Data Types - emd_amount", False, f"emd_amount is {type(lead_data_returned.get('emd_amount'))}, expected numeric")
                        
                else:
                    self.log_test("Leads CREATE", False, f"Lead creation failed: {data}")
                    return False
            else:
                self.log_test("Leads CREATE", False, f"Lead creation returned {response.status_code if response else 'No response'}")
                return False
                
            # Test LIST with status filtering
            response = self.make_request("GET", "/leads?status=New")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "leads" in data.get("data", {}):
                    self.log_test("Leads LIST with Filter", True, f"Leads list retrieved with {len(data['data']['leads'])} leads")
                else:
                    self.log_test("Leads LIST with Filter", False, f"Leads list failed: {data}")
            else:
                self.log_test("Leads LIST with Filter", False, f"Leads list returned {response.status_code if response else 'No response'}")
                
            # Test UPDATE
            update_data = {
                "status": "Qualified",
                "qualification_notes": "Updated qualification notes after review"
            }
            response = self.make_request("PUT", f"/leads/{lead_id}", update_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Leads UPDATE", True, "Lead updated successfully")
                else:
                    self.log_test("Leads UPDATE", False, f"Lead update failed: {data}")
            else:
                self.log_test("Leads UPDATE", False, f"Lead update returned {response.status_code if response else 'No response'}")
                
            return True
            
        except Exception as e:
            self.log_test("Leads CRUD", False, f"Exception: {str(e)}")
            return False

    def test_lead_conversion_workflow(self):
        """Test Lead to Opportunity conversion workflow"""
        if not self.auth_token:
            self.log_test("Lead Conversion Workflow", False, "No auth token available")
            return False
            
        try:
            # Get a qualified lead
            response = self.make_request("GET", "/leads?status=Qualified")
            if not response or response.status_code != 200:
                self.log_test("Lead Conversion Workflow", False, "Could not get qualified leads")
                return False
                
            leads_data = response.json()
            if not leads_data.get("status") or not leads_data["data"]["leads"]:
                self.log_test("Lead Conversion Workflow", False, "No qualified leads available for conversion test")
                return False
                
            lead_id = leads_data["data"]["leads"][0]["id"]
            
            # Test conversion request
            conversion_request = {
                "notes": "Ready for conversion to opportunity"
            }
            
            response = self.make_request("POST", f"/leads/{lead_id}/request-conversion", conversion_request)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Lead Conversion Request", True, "Conversion request submitted successfully")
                else:
                    self.log_test("Lead Conversion Request", False, f"Conversion request failed: {data}")
                    return False
            else:
                self.log_test("Lead Conversion Request", False, f"Conversion request returned {response.status_code if response else 'No response'}")
                return False
                
            # Test review approval (as admin)
            review_data = {
                "decision": "Approved",
                "comments": "Lead meets all criteria for conversion"
            }
            
            response = self.make_request("POST", f"/leads/{lead_id}/review", review_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Lead Review Approval", True, "Lead conversion approved successfully")
                else:
                    self.log_test("Lead Review Approval", False, f"Lead review failed: {data}")
                    return False
            else:
                self.log_test("Lead Review Approval", False, f"Lead review returned {response.status_code if response else 'No response'}")
                return False
                
            # Test actual conversion to opportunity
            conversion_data = {
                "opportunity_name": "Test CRM Integration Opportunity",
                "notes": "Converted from qualified lead"
            }
            
            response = self.make_request("POST", f"/leads/{lead_id}/convert-to-opportunity", conversion_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "opportunity_pot_id" in data.get("data", {}):
                    pot_id = data["data"]["opportunity_pot_id"]
                    self.log_test("Lead to Opportunity Conversion", True, f"Lead converted to opportunity with POT-ID: {pot_id}")
                else:
                    self.log_test("Lead to Opportunity Conversion", False, f"Lead conversion failed: {data}")
                    return False
            else:
                self.log_test("Lead to Opportunity Conversion", False, f"Lead conversion returned {response.status_code if response else 'No response'}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Lead Conversion Workflow", False, f"Exception: {str(e)}")
            return False

    def test_opportunities_crud(self):
        """Test Opportunities CRUD operations with POT-ID generation"""
        if not self.auth_token:
            self.log_test("Opportunities CRUD", False, "No auth token available")
            return False
            
        opportunity_id = None
        
        try:
            # Get company and contact IDs
            response = self.make_request("GET", "/companies")
            if not response or response.status_code != 200:
                self.log_test("Opportunities CRUD", False, "Could not get companies for opportunity test")
                return False
                
            companies_data = response.json()
            if not companies_data.get("status") or not companies_data["data"]["companies"]:
                self.log_test("Opportunities CRUD", False, "No companies available for opportunity test")
                return False
                
            company_id = companies_data["data"]["companies"][0]["id"]
            
            # Get contacts
            response = self.make_request("GET", "/contacts")
            if not response or response.status_code != 200:
                self.log_test("Opportunities CRUD", False, "Could not get contacts for opportunity test")
                return False
                
            contacts_data = response.json()
            if not contacts_data.get("status") or not contacts_data["data"]["contacts"]:
                self.log_test("Opportunities CRUD", False, "No contacts available for opportunity test")
                return False
                
            contact_id = contacts_data["data"]["contacts"][0]["id"]
            
            # Test CREATE
            opportunity_data = {
                "company_id": company_id,
                "contact_id": contact_id,
                "name": "Test CRM Opportunity",
                "amount": 1500000.00,  # Number, not string
                "stage": "L1_Prospect",
                "status": "Open",
                "probability": 25,
                "notes": "Test opportunity for CRM system implementation",
                "close_date": "2024-12-31"
            }
            
            response = self.make_request("POST", "/opportunities", opportunity_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    opportunity_id = data["data"]["id"]
                    pot_id = data["data"]["pot_id"]
                    
                    # Verify POT-ID format
                    if pot_id and pot_id.startswith("POT-") and len(pot_id) == 8:
                        self.log_test("Opportunities CREATE", True, f"Opportunity created with ID: {opportunity_id}, POT-ID: {pot_id}")
                        self.log_test("POT-ID Generation", True, f"POT-ID format is correct: {pot_id}")
                    else:
                        self.log_test("Opportunities CREATE", True, f"Opportunity created with ID: {opportunity_id}")
                        self.log_test("POT-ID Generation", False, f"POT-ID format is incorrect: {pot_id}")
                else:
                    self.log_test("Opportunities CREATE", False, f"Opportunity creation failed: {data}")
                    return False
            else:
                self.log_test("Opportunities CREATE", False, f"Opportunity creation returned {response.status_code if response else 'No response'}")
                return False
                
            # Test READ
            response = self.make_request("GET", f"/opportunities/{opportunity_id}")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and data["data"]["name"] == "Test CRM Opportunity":
                    self.log_test("Opportunities READ", True, "Opportunity retrieved successfully")
                    
                    # Check amount data type
                    if isinstance(data["data"].get("amount"), (int, float)):
                        self.log_test("Opportunities Data Types - amount", True, "amount is numeric")
                    else:
                        self.log_test("Opportunities Data Types - amount", False, f"amount is {type(data['data'].get('amount'))}, expected numeric")
                        
                else:
                    self.log_test("Opportunities READ", False, f"Opportunity retrieval failed: {data}")
            else:
                self.log_test("Opportunities READ", False, f"Opportunity retrieval returned {response.status_code if response else 'No response'}")
                
            # Test LIST
            response = self.make_request("GET", "/opportunities")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "opportunities" in data.get("data", {}):
                    self.log_test("Opportunities LIST", True, f"Opportunities list retrieved with {len(data['data']['opportunities'])} opportunities")
                else:
                    self.log_test("Opportunities LIST", False, f"Opportunities list failed: {data}")
            else:
                self.log_test("Opportunities LIST", False, f"Opportunities list returned {response.status_code if response else 'No response'}")
                
            # Test stage update
            stage_update = {
                "stage": "L1_Qualification",
                "notes": "Moving to qualification stage",
                "stage_specific_data": {
                    "qualification_notes": "Initial qualification completed"
                }
            }
            
            response = self.make_request("PATCH", f"/opportunities/{opportunity_id}/stage", stage_update)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    self.log_test("Opportunities Stage Update", True, "Opportunity stage updated successfully")
                else:
                    self.log_test("Opportunities Stage Update", False, f"Stage update failed: {data}")
            else:
                self.log_test("Opportunities Stage Update", False, f"Stage update returned {response.status_code if response else 'No response'}")
                
            return True
            
        except Exception as e:
            self.log_test("Opportunities CRUD", False, f"Exception: {str(e)}")
            return False

    def test_users_management(self):
        """Test Users management endpoints"""
        if not self.auth_token:
            self.log_test("Users Management", False, "No auth token available")
            return False
            
        try:
            # Test LIST users
            response = self.make_request("GET", "/users")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "users" in data.get("data", {}):
                    users_count = len(data["data"]["users"])
                    self.log_test("Users LIST", True, f"Users list retrieved with {users_count} users")
                    
                    # Verify we have the expected test users
                    usernames = [user.get("username") for user in data["data"]["users"]]
                    expected_users = ["admin", "reviewer", "sales"]
                    
                    for expected_user in expected_users:
                        if expected_user in usernames:
                            self.log_test(f"User Exists - {expected_user}", True, f"User {expected_user} found in system")
                        else:
                            self.log_test(f"User Exists - {expected_user}", False, f"User {expected_user} not found in system")
                            
                else:
                    self.log_test("Users LIST", False, f"Users list failed: {data}")
                    return False
            else:
                self.log_test("Users LIST", False, f"Users list returned {response.status_code if response else 'No response'}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Users Management", False, f"Exception: {str(e)}")
            return False

    def test_database_constraints(self):
        """Test database constraints and validations"""
        if not self.auth_token:
            self.log_test("Database Constraints", False, "No auth token available")
            return False
            
        try:
            # Test invalid company creation (missing required fields)
            invalid_company = {
                "name": "",  # Empty name should fail
                "gst_number": "INVALID"
            }
            
            response = self.make_request("POST", "/companies", invalid_company)
            if response and response.status_code in [400, 422]:
                self.log_test("Database Constraints - Invalid Company", True, "Invalid company creation properly rejected")
            else:
                self.log_test("Database Constraints - Invalid Company", False, f"Invalid company creation should have been rejected but got {response.status_code if response else 'No response'}")
                
            # Test invalid lead creation (missing required fields)
            invalid_lead = {
                "project_title": "",  # Empty title should fail
                "lead_source": "Invalid Source"
            }
            
            response = self.make_request("POST", "/leads", invalid_lead)
            if response and response.status_code in [400, 422]:
                self.log_test("Database Constraints - Invalid Lead", True, "Invalid lead creation properly rejected")
            else:
                self.log_test("Database Constraints - Invalid Lead", False, f"Invalid lead creation should have been rejected but got {response.status_code if response else 'No response'}")
                
            return True
            
        except Exception as e:
            self.log_test("Database Constraints", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting CRM Backend Comprehensive Testing")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Authentication tests
        auth_success = self.test_authentication()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with authenticated tests")
            return False
            
        self.test_dashboard()
        
        # CRUD operations tests
        self.test_companies_crud()
        self.test_contacts_crud()
        self.test_leads_crud()
        self.test_opportunities_crud()
        
        # Workflow tests
        self.test_lead_conversion_workflow()
        
        # Management tests
        self.test_users_management()
        
        # Validation tests
        self.test_database_constraints()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 CRM Backend Testing Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 60)
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = CRMTester()
    
    try:
        success = tester.run_all_tests()
        overall_success = tester.print_summary()
        
        # Save detailed results
        with open("/app/crm_test_results_final.log", "w") as f:
            json.dump(tester.test_results, f, indent=2, default=str)
            
        return 0 if overall_success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())