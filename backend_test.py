#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Enterprise CRM System
Tests Dashboard, Session Management, File Upload, Masters, and Health endpoints
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional
import tempfile
from io import BytesIO

# Backend URL from frontend environment
BACKEND_URL = "http://localhost:8000"
TEST_SESSION_ID = "test_session_123"

class CRMBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.jwt_token = None
        self.auth_headers = {}
        self.test_results = {}
        
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

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n=== Testing Health Endpoints ===")
        
        # Test root endpoint
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and ("CRM" in data.get("message", "") or "API" in data.get("message", "")):
                    self.log_test("Health - Root Endpoint", True, "Root endpoint working correctly")
                else:
                    self.log_test("Health - Root Endpoint", False, "Invalid response format", data)
            else:
                self.log_test("Health - Root Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health - Root Endpoint", False, f"Request failed: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "healthy" in data.get("message", "").lower():
                    self.log_test("Health - Health Check", True, "Health check endpoint working correctly")
                else:
                    self.log_test("Health - Health Check", False, "Invalid health response", data)
            else:
                self.log_test("Health - Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health - Health Check", False, f"Request failed: {str(e)}")

    def test_session_management(self):
        """Test session management endpoints"""
        print("\n=== Testing Session Management ===")
        
        # Test session info
        try:
            response = self.make_request("GET", "/api/session/info", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    user_data = data["data"]
                    if "id" in user_data and "name" in user_data and "email" in user_data:
                        self.log_test("Session - Get Info", True, "Session info retrieved successfully")
                    else:
                        self.log_test("Session - Get Info", False, "Incomplete user data", user_data)
                else:
                    self.log_test("Session - Get Info", False, "Invalid response format", data)
            else:
                self.log_test("Session - Get Info", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Session - Get Info", False, f"Request failed: {str(e)}")
        
        # Test session refresh
        try:
            response = self.make_request("POST", "/api/session/refresh", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "refresh" in data.get("message", "").lower():
                    self.log_test("Session - Refresh", True, "Session refreshed successfully")
                else:
                    self.log_test("Session - Refresh", False, "Invalid refresh response", data)
            else:
                self.log_test("Session - Refresh", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Session - Refresh", False, f"Request failed: {str(e)}")
        
        # Test logout
        try:
            response = self.make_request("POST", "/api/logout", headers=self.auth_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "logout" in data.get("message", "").lower():
                    self.log_test("Session - Logout", True, "Logout successful")
                else:
                    self.log_test("Session - Logout", False, "Invalid logout response", data)
            else:
                self.log_test("Session - Logout", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Session - Logout", False, f"Request failed: {str(e)}")

    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n=== Testing Dashboard Endpoints ===")
        
        dashboard_types = [
            ("overview", "/api/dashboard/overview"),
            ("sales", "/api/dashboard/sales"),
            ("presales", "/api/dashboard/presales"),
            ("product", "/api/dashboard/product")
        ]
        
        for dashboard_name, endpoint in dashboard_types:
            try:
                response = self.make_request("GET", endpoint, headers=self.auth_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data") is not None:
                        self.log_test(f"Dashboard - {dashboard_name.title()}", True, 
                                    f"{dashboard_name.title()} dashboard data retrieved successfully")
                    else:
                        self.log_test(f"Dashboard - {dashboard_name.title()}", False, 
                                    "Invalid dashboard response", data)
                else:
                    self.log_test(f"Dashboard - {dashboard_name.title()}", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test(f"Dashboard - {dashboard_name.title()}", False, 
                            f"Request failed: {str(e)}")

    def test_file_upload_endpoints(self):
        """Test file upload endpoints"""
        print("\n=== Testing File Upload Endpoints ===")
        
        # Create a test file
        test_file_content = b"This is a test file for CRM system testing"
        test_filename = "test_document.txt"
        
        # Test file upload
        try:
            files = {"file": (test_filename, BytesIO(test_file_content), "text/plain")}
            response = self.make_request("POST", "/api/files/upload", 
                                       headers=self.auth_headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("file_path"):
                    file_path = data["data"]["file_path"]
                    self.log_test("File Upload - Upload", True, "File uploaded successfully")
                    
                    # Test get file URL
                    try:
                        response = self.make_request("GET", f"/api/files/{file_path}", 
                                                   headers=self.auth_headers)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status") and data.get("data", {}).get("file_url"):
                                self.log_test("File Upload - Get URL", True, "File URL generated successfully")
                            else:
                                self.log_test("File Upload - Get URL", False, "Invalid URL response", data)
                        else:
                            self.log_test("File Upload - Get URL", False, f"HTTP {response.status_code}", response.text)
                    except Exception as e:
                        self.log_test("File Upload - Get URL", False, f"Request failed: {str(e)}")
                    
                    # Test delete file
                    try:
                        response = self.make_request("DELETE", f"/api/files/{file_path}", 
                                                   headers=self.auth_headers)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status"):
                                self.log_test("File Upload - Delete", True, "File deleted successfully")
                            else:
                                self.log_test("File Upload - Delete", False, "Invalid delete response", data)
                        else:
                            self.log_test("File Upload - Delete", False, f"HTTP {response.status_code}", response.text)
                    except Exception as e:
                        self.log_test("File Upload - Delete", False, f"Request failed: {str(e)}")
                        
                else:
                    self.log_test("File Upload - Upload", False, "Invalid upload response", data)
            else:
                self.log_test("File Upload - Upload", False, f"HTTP {response.status_code}", response.text)
                # If upload fails, mark other file operations as not tested
                self.log_test("File Upload - Get URL", False, "Skipped due to upload failure")
                self.log_test("File Upload - Delete", False, "Skipped due to upload failure")
        except Exception as e:
            self.log_test("File Upload - Upload", False, f"Request failed: {str(e)}")
            self.log_test("File Upload - Get URL", False, "Skipped due to upload failure")
            self.log_test("File Upload - Delete", False, "Skipped due to upload failure")

    def test_masters_endpoints(self):
        """Test masters module endpoints"""
        print("\n=== Testing Masters Module ===")
        
        # Test get products
        try:
            response = self.make_request("GET", "/api/masters/products", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "data" in data:
                    self.log_test("Masters - Get Products", True, "Products retrieved successfully")
                else:
                    self.log_test("Masters - Get Products", False, "Invalid products response", data)
            else:
                self.log_test("Masters - Get Products", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Get Products", False, f"Request failed: {str(e)}")
        
        # Test get UOMs
        try:
            response = self.make_request("GET", "/api/masters/uoms", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "data" in data:
                    self.log_test("Masters - Get UOMs", True, "UOMs retrieved successfully")
                else:
                    self.log_test("Masters - Get UOMs", False, "Invalid UOMs response", data)
            else:
                self.log_test("Masters - Get UOMs", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Get UOMs", False, f"Request failed: {str(e)}")
        
        # Test get departments
        try:
            response = self.make_request("GET", "/api/masters/departments", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "data" in data:
                    self.log_test("Masters - Get Departments", True, "Departments retrieved successfully")
                else:
                    self.log_test("Masters - Get Departments", False, "Invalid departments response", data)
            else:
                self.log_test("Masters - Get Departments", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Get Departments", False, f"Request failed: {str(e)}")
        
        # Test get roles
        try:
            response = self.make_request("GET", "/api/masters/roles", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "data" in data:
                    self.log_test("Masters - Get Roles", True, "Roles retrieved successfully")
                else:
                    self.log_test("Masters - Get Roles", False, "Invalid roles response", data)
            else:
                self.log_test("Masters - Get Roles", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Masters - Get Roles", False, f"Request failed: {str(e)}")

    def test_leads_api(self):
        """Test Leads API endpoints"""
        print("\n=== Testing Leads API ===")
        
        # Sample lead data for testing
        lead_data = {
            "project_title": "Enterprise CRM Implementation Project",
            "lead_source": "Direct Marketing",
            "lead_sub_type": "Pre-Tender",
            "tender_sub_type": "Open Tender",
            "products_services": ["CRM Software", "Implementation Services"],
            "company_id": 1,
            "sub_business_type": "Technology Solutions",
            "end_customer_id": 1,
            "end_customer_region": "North India",
            "partner_involved": False,
            "partners_data": [],
            "tender_fee": 50000.00,
            "currency": "INR",
            "submission_type": "Online",
            "tender_authority": "Government of India",
            "tender_for": "Ministry of Technology",
            "emd_required": True,
            "emd_amount": 100000.00,
            "emd_currency": "INR",
            "bg_required": True,
            "bg_amount": 500000.00,
            "bg_currency": "INR",
            "important_dates": [
                {
                    "label": "Submission Deadline",
                    "key": "submission_date",
                    "value": "2024-12-31"
                }
            ],
            "clauses": [
                {
                    "clause_type": "Technical",
                    "criteria_description": "Must have 5+ years experience"
                }
            ],
            "expected_revenue": 5000000.00,
            "revenue_currency": "INR",
            "convert_to_opportunity_date": "2024-12-15",
            "competitors": [
                {
                    "name": "Competitor A",
                    "description": "Major competitor in CRM space"
                }
            ],
            "documents": [],
            "status": "New",
            "priority": "High",
            "qualification_notes": "High potential client with immediate requirements",
            "lead_score": 85,
            "contacts": [
                {
                    "designation": "IT Director",
                    "salutation": "Mr.",
                    "first_name": "Rajesh",
                    "middle_name": "Kumar",
                    "last_name": "Sharma",
                    "email": "rajesh.sharma@testcompany.com",
                    "primary_phone": "+91-9876543210",
                    "decision_maker": True,
                    "decision_maker_percentage": 80,
                    "comments": "Primary decision maker for IT purchases"
                }
            ]
        }
        
        created_lead_id = None
        
        # Test 1: Create Lead
        try:
            response = self.make_request("POST", "/api/leads/", headers=self.session_headers, data=lead_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("id"):
                    created_lead_id = data["data"]["id"]
                    self.log_test("Leads - Create Lead", True, "Lead created successfully")
                else:
                    self.log_test("Leads - Create Lead", False, "Invalid create response", data)
            else:
                self.log_test("Leads - Create Lead", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - Create Lead", False, f"Request failed: {str(e)}")
        
        # Test 2: Get All Leads
        try:
            response = self.make_request("GET", "/api/leads/?skip=0&limit=10", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and "data" in data and "leads" in data["data"]:
                    self.log_test("Leads - Get All Leads", True, "Leads retrieved successfully")
                else:
                    self.log_test("Leads - Get All Leads", False, "Invalid leads list response", data)
            else:
                self.log_test("Leads - Get All Leads", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - Get All Leads", False, f"Request failed: {str(e)}")
        
        # Test 3: Get Lead by ID (if we have a created lead)
        if created_lead_id:
            try:
                response = self.make_request("GET", f"/api/leads/{created_lead_id}", headers=self.session_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") and data.get("data", {}).get("id") == created_lead_id:
                        self.log_test("Leads - Get Lead by ID", True, "Lead retrieved by ID successfully")
                    else:
                        self.log_test("Leads - Get Lead by ID", False, "Invalid lead response", data)
                else:
                    self.log_test("Leads - Get Lead by ID", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Leads - Get Lead by ID", False, f"Request failed: {str(e)}")
        else:
            self.log_test("Leads - Get Lead by ID", False, "Skipped due to lead creation failure")
        
        # Test 4: Update Lead (if we have a created lead)
        if created_lead_id:
            update_data = {
                "qualification_notes": "Updated qualification notes after initial review",
                "lead_score": 90,
                "status": "Qualified"
            }
            try:
                response = self.make_request("PUT", f"/api/leads/{created_lead_id}", 
                                           headers=self.session_headers, data=update_data)
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
        else:
            self.log_test("Leads - Update Lead", False, "Skipped due to lead creation failure")
        
        # Test 5: Get Lead Stats
        try:
            response = self.make_request("GET", "/api/leads/stats", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data"):
                    self.log_test("Leads - Get Stats", True, "Lead statistics retrieved successfully")
                else:
                    self.log_test("Leads - Get Stats", False, "Invalid stats response", data)
            else:
                self.log_test("Leads - Get Stats", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads - Get Stats", False, f"Request failed: {str(e)}")
        
        return created_lead_id

    def test_lead_to_opportunity_conversion(self, lead_id=None):
        """Test Lead to Opportunity Conversion Workflow"""
        print("\n=== Testing Lead to Opportunity Conversion ===")
        
        if not lead_id:
            self.log_test("Conversion - Request Conversion", False, "No lead ID available for conversion testing")
            self.log_test("Conversion - Review Request", False, "Skipped due to no lead ID")
            self.log_test("Conversion - Convert to Opportunity", False, "Skipped due to no lead ID")
            return None
        
        # Test 1: Request Conversion
        conversion_request_data = {
            "notes": "Lead is qualified and ready for conversion to opportunity"
        }
        try:
            response = self.make_request("POST", f"/api/leads/{lead_id}/request-conversion", 
                                       headers=self.session_headers, data=conversion_request_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("Conversion - Request Conversion", True, "Conversion request submitted successfully")
                else:
                    self.log_test("Conversion - Request Conversion", False, "Invalid conversion request response", data)
            else:
                self.log_test("Conversion - Request Conversion", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Request Conversion", False, f"Request failed: {str(e)}")
        
        # Test 2: Review Conversion Request (Admin action)
        review_data = {
            "decision": "Approved",
            "comments": "Lead meets all criteria for conversion to opportunity"
        }
        try:
            response = self.make_request("POST", f"/api/leads/{lead_id}/review", 
                                       headers=self.session_headers, data=review_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.log_test("Conversion - Review Request", True, "Conversion request reviewed successfully")
                else:
                    self.log_test("Conversion - Review Request", False, "Invalid review response", data)
            else:
                self.log_test("Conversion - Review Request", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Review Request", False, f"Request failed: {str(e)}")
        
        # Test 3: Convert to Opportunity
        conversion_data = {
            "opportunity_name": "Enterprise CRM Implementation Opportunity",
            "notes": "Converting qualified lead to opportunity for further sales process"
        }
        opportunity_id = None
        try:
            response = self.make_request("POST", f"/api/leads/{lead_id}/convert-to-opportunity", 
                                       headers=self.session_headers, data=conversion_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("opportunity_id"):
                    opportunity_id = data["data"]["opportunity_id"]
                    self.log_test("Conversion - Convert to Opportunity", True, "Lead converted to opportunity successfully")
                else:
                    self.log_test("Conversion - Convert to Opportunity", False, "Invalid conversion response", data)
            else:
                self.log_test("Conversion - Convert to Opportunity", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversion - Convert to Opportunity", False, f"Request failed: {str(e)}")
        
        return opportunity_id

    def test_opportunities_api(self, opportunity_id=None):
        """Test Opportunities API endpoints"""
        print("\n=== Testing Opportunities API ===")
        
        # Test 1: Get All Opportunities
        try:
            response = self.make_request("GET", "/api/opportunities/?skip=0&limit=10", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") or data.get("success"):  # Handle different response formats
                    self.log_test("Opportunities - Get All", True, "Opportunities retrieved successfully")
                else:
                    self.log_test("Opportunities - Get All", False, "Invalid opportunities list response", data)
            else:
                self.log_test("Opportunities - Get All", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Opportunities - Get All", False, f"Request failed: {str(e)}")
        
        # Test 2: Get Opportunity by ID (if we have one)
        if opportunity_id:
            try:
                response = self.make_request("GET", f"/api/opportunities/{opportunity_id}", headers=self.session_headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") or data.get("success"):
                        self.log_test("Opportunities - Get by ID", True, "Opportunity retrieved by ID successfully")
                    else:
                        self.log_test("Opportunities - Get by ID", False, "Invalid opportunity response", data)
                else:
                    self.log_test("Opportunities - Get by ID", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Opportunities - Get by ID", False, f"Request failed: {str(e)}")
        else:
            self.log_test("Opportunities - Get by ID", False, "Skipped due to no opportunity ID available")
        
        # Test 3: Get Opportunity Statistics
        try:
            response = self.make_request("GET", "/api/opportunities/statistics/overview", headers=self.session_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") or data.get("success"):
                    self.log_test("Opportunities - Get Statistics", True, "Opportunity statistics retrieved successfully")
                else:
                    self.log_test("Opportunities - Get Statistics", False, "Invalid statistics response", data)
            else:
                self.log_test("Opportunities - Get Statistics", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Opportunities - Get Statistics", False, f"Request failed: {str(e)}")
        
        # Test 4: Update Sales Stage (if we have an opportunity)
        if opportunity_id:
            stage_update_data = {
                "status": "In Progress",
                "completion_date": "2024-12-20",
                "comments": "Moving to need analysis stage"
            }
            try:
                response = self.make_request("PUT", f"/api/opportunities/{opportunity_id}/sales-process/stage/L2_Need_Analysis", 
                                           headers=self.session_headers, data=stage_update_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") or data.get("success"):
                        self.log_test("Opportunities - Update Sales Stage", True, "Sales stage updated successfully")
                    else:
                        self.log_test("Opportunities - Update Sales Stage", False, "Invalid stage update response", data)
                else:
                    self.log_test("Opportunities - Update Sales Stage", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Opportunities - Update Sales Stage", False, f"Request failed: {str(e)}")
        else:
            self.log_test("Opportunities - Update Sales Stage", False, "Skipped due to no opportunity ID available")

    def test_integration_scenarios(self):
        """Test integration scenarios"""
        print("\n=== Testing Integration Scenarios ===")
        
        # Test that session authentication works across different modules
        try:
            # Test dashboard with session
            dashboard_response = self.make_request("GET", "/api/dashboard/overview", headers=self.session_headers)
            
            # Test masters with session
            masters_response = self.make_request("GET", "/api/masters/products", headers=self.session_headers)
            
            if dashboard_response.status_code == 200 and masters_response.status_code == 200:
                self.log_test("Integration - Session Auth", True, "Session authentication working across modules")
            else:
                self.log_test("Integration - Session Auth", False, 
                            f"Dashboard: {dashboard_response.status_code}, Masters: {masters_response.status_code}")
        except Exception as e:
            self.log_test("Integration - Session Auth", False, f"Request failed: {str(e)}")
        
        # Test without session header (should fail)
        try:
            response = self.make_request("GET", "/api/dashboard/overview")
            if response.status_code == 401:
                self.log_test("Integration - Auth Required", True, "Proper authentication required")
            else:
                self.log_test("Integration - Auth Required", False, 
                            f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Integration - Auth Required", False, f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive CRM Backend Testing")
        print(f"Backend URL: {self.base_url}")
        
        # First authenticate to get JWT token
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with protected endpoint tests.")
            return
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_session_management()
        self.test_dashboard_endpoints()
        self.test_file_upload_endpoints()
        self.test_masters_endpoints()
        
        # Test Leads and Opportunities workflow
        created_lead_id = self.test_leads_api()
        opportunity_id = self.test_lead_to_opportunity_conversion(created_lead_id)
        self.test_opportunities_api(opportunity_id)
        
        self.test_integration_scenarios()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {test_name}: {result['message']}")
        
        print("\n" + "="*60)
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = CRMBackendTester()
    tester.run_all_tests()
    
    # Exit with appropriate code
    passed, failed = tester.print_summary()
    sys.exit(0 if failed == 0 else 1)