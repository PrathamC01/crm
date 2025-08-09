#!/usr/bin/env python3
"""
Comprehensive CRM Backend API Testing
Tests all CRM functionality including authentication, leads, opportunities, companies, contacts, and conversion workflow
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class CRMComprehensiveTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_resources = {
            'companies': [],
            'contacts': [],
            'leads': [],
            'opportunities': []
        }

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

    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.token:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # ========== HEALTH CHECK TESTS ==========
    def test_health_check(self):
        """Test root health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Health Check", True, f"API is running: {data.get('message')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Status not True: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    # ========== AUTHENTICATION TESTS ==========
    def test_login_admin(self):
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
                    self.token = data["data"]["token"]
                    self.log_test("Admin Login", True, f"Token received, user: {data['data'].get('user', {}).get('name', 'Unknown')}")
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

    def test_dashboard_access(self):
        """Test dashboard access with token"""
        if not self.token:
            self.log_test("Dashboard Access", False, "No token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    user_data = data.get("data", {})
                    self.log_test("Dashboard Access", True, f"User: {user_data.get('name')} ({user_data.get('role')})")
                    return True
                else:
                    self.log_test("Dashboard Access", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Dashboard Access", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Access", False, f"Exception: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            login_data = {
                "email_or_username": "invalid_user",
                "password": "wrong_password"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_test("Invalid Login Test", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_test("Invalid Login Test", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Login Test", False, f"Exception: {str(e)}")
            return False

    # ========== COMPANY MANAGEMENT TESTS ==========
    def test_create_company(self):
        """Test company creation"""
        if not self.token:
            self.log_test("Create Company", False, "No authentication token")
            return False
            
        try:
            company_data = {
                "name": f"Test Company {uuid.uuid4().hex[:8]}",
                "gst_number": f"29ABCDE{uuid.uuid4().hex[:4].upper()}F1Z1",
                "pan_number": f"ABCDE{uuid.uuid4().hex[:4].upper()}F",
                "industry_category": "Technology",
                "address": "123 Test Street",
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India",
                "postal_code": "560001",
                "website": "www.testcompany.com",
                "description": "Test company for CRM testing"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/companies",
                json=company_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company_id = data.get("data", {}).get("id")
                    if company_id:
                        self.created_resources['companies'].append(company_id)
                    self.log_test("Create Company", True, f"Company created: {data.get('data', {}).get('name')}")
                    return True
                else:
                    self.log_test("Create Company", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Create Company", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Company", False, f"Exception: {str(e)}")
            return False

    def test_get_companies(self):
        """Test getting companies list"""
        if not self.token:
            self.log_test("Get Companies", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/companies",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    companies = data.get("data", {}).get("companies", [])
                    self.log_test("Get Companies", True, f"Retrieved {len(companies)} companies")
                    return True
                else:
                    self.log_test("Get Companies", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Get Companies", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Companies", False, f"Exception: {str(e)}")
            return False

    # ========== CONTACT MANAGEMENT TESTS ==========
    def test_create_contact(self):
        """Test contact creation"""
        if not self.token:
            self.log_test("Create Contact", False, "No authentication token")
            return False
            
        # Get a company ID first
        company_id = None
        if self.created_resources['companies']:
            company_id = self.created_resources['companies'][0]
        else:
            # Try to get existing companies
            try:
                response = self.session.get(f"{self.base_url}/api/companies", headers=self.get_auth_headers())
                if response.status_code == 200:
                    data = response.json()
                    companies = data.get("data", {}).get("companies", [])
                    if companies:
                        company_id = companies[0].get("id")
            except:
                pass
                
        if not company_id:
            self.log_test("Create Contact", False, "No company available for contact")
            return False
            
        try:
            contact_data = {
                "full_name": f"John Doe {uuid.uuid4().hex[:4]}",
                "designation": "CTO",
                "email": f"john.doe.{uuid.uuid4().hex[:4]}@testcompany.com",
                "phone_number": "+91-98765-43210",
                "company_id": company_id,
                "role_type": "DECISION_MAKER"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/contacts",
                json=contact_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    contact_id = data.get("data", {}).get("id")
                    if contact_id:
                        self.created_resources['contacts'].append(contact_id)
                    self.log_test("Create Contact", True, f"Contact created: {data.get('data', {}).get('full_name')}")
                    return True
                else:
                    self.log_test("Create Contact", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Create Contact", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Contact", False, f"Exception: {str(e)}")
            return False

    def test_get_contacts(self):
        """Test getting contacts list"""
        if not self.token:
            self.log_test("Get Contacts", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/contacts",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    contacts = data.get("data", {}).get("contacts", [])
                    self.log_test("Get Contacts", True, f"Retrieved {len(contacts)} contacts")
                    return True
                else:
                    self.log_test("Get Contacts", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Get Contacts", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Contacts", False, f"Exception: {str(e)}")
            return False

    # ========== LEAD MANAGEMENT TESTS ==========
    def test_create_lead(self):
        """Test lead creation with comprehensive data"""
        if not self.token:
            self.log_test("Create Lead", False, "No authentication token")
            return False
            
        # Get company ID
        company_id = None
        if self.created_resources['companies']:
            company_id = self.created_resources['companies'][0]
        else:
            try:
                response = self.session.get(f"{self.base_url}/api/companies", headers=self.get_auth_headers())
                if response.status_code == 200:
                    data = response.json()
                    companies = data.get("data", {}).get("companies", [])
                    if companies:
                        company_id = companies[0].get("id")
            except:
                pass
                
        if not company_id:
            self.log_test("Create Lead", False, "No company available for lead")
            return False
            
        try:
            lead_data = {
                "project_title": f"CRM Integration Project {uuid.uuid4().hex[:4]}",
                "lead_source": "WEBSITE",
                "lead_sub_type": "DIRECT",
                "tender_sub_type": "OPEN",
                "products_services": ["CRM Software", "Integration Services"],
                "company_id": company_id,
                "sub_business_type": "B2B Software",
                "partner_involved": False,
                "tender_fee": 5000.0,
                "currency": "INR",
                "submission_type": "ONLINE",
                "tender_authority": "IT Department",
                "tender_for": "CRM System Implementation",
                "emd_required": True,
                "emd_amount": 50000.0,
                "emd_currency": "INR",
                "bg_required": False,
                "expected_revenue": 500000.0,
                "revenue_currency": "INR",
                "convert_to_opportunity_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "competitors": ["Salesforce", "HubSpot"],
                "status": "NEW",
                "priority": "HIGH",
                "qualification_notes": "High potential client with immediate need",
                "lead_score": 85,
                "contacts": []
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads",
                json=lead_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    lead_id = data.get("data", {}).get("id")
                    if lead_id:
                        self.created_resources['leads'].append(lead_id)
                    self.log_test("Create Lead", True, f"Lead created: {data.get('data', {}).get('project_title')}")
                    return True
                else:
                    self.log_test("Create Lead", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Create Lead", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Lead", False, f"Exception: {str(e)}")
            return False

    def test_get_leads(self):
        """Test getting leads list"""
        if not self.token:
            self.log_test("Get Leads", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/leads",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    leads = data.get("data", {}).get("leads", [])
                    self.log_test("Get Leads", True, f"Retrieved {len(leads)} leads")
                    return True
                else:
                    self.log_test("Get Leads", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Get Leads", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Leads", False, f"Exception: {str(e)}")
            return False

    def test_lead_status_update(self):
        """Test updating lead status"""
        if not self.token:
            self.log_test("Lead Status Update", False, "No authentication token")
            return False
            
        if not self.created_resources['leads']:
            self.log_test("Lead Status Update", False, "No leads available for testing")
            return False
            
        try:
            lead_id = self.created_resources['leads'][0]
            update_data = {
                "status": "CONTACTED",
                "qualification_notes": "Initial contact made, client interested"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/leads/{lead_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Lead Status Update", True, f"Lead status updated to: {data.get('data', {}).get('status')}")
                    return True
                else:
                    self.log_test("Lead Status Update", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead Status Update", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Lead Status Update", False, f"Exception: {str(e)}")
            return False

    def test_lead_conversion_request(self):
        """Test requesting lead conversion to opportunity"""
        if not self.token:
            self.log_test("Lead Conversion Request", False, "No authentication token")
            return False
            
        if not self.created_resources['leads']:
            self.log_test("Lead Conversion Request", False, "No leads available for testing")
            return False
            
        try:
            lead_id = self.created_resources['leads'][0]
            
            # First update lead to QUALIFIED status
            update_data = {"status": "QUALIFIED"}
            self.session.put(
                f"{self.base_url}/api/leads/{lead_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            # Now request conversion
            conversion_data = {
                "notes": "Lead is qualified and ready for conversion to opportunity"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{lead_id}/request-conversion",
                json=conversion_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Lead Conversion Request", True, f"Conversion requested: {data.get('message')}")
                    return True
                else:
                    self.log_test("Lead Conversion Request", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead Conversion Request", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lead Conversion Request", False, f"Exception: {str(e)}")
            return False

    def test_lead_conversion_review(self):
        """Test admin review of conversion request"""
        if not self.token:
            self.log_test("Lead Conversion Review", False, "No authentication token")
            return False
            
        if not self.created_resources['leads']:
            self.log_test("Lead Conversion Review", False, "No leads available for testing")
            return False
            
        try:
            lead_id = self.created_resources['leads'][0]
            review_data = {
                "decision": "APPROVED",
                "comments": "Lead meets all criteria for conversion to opportunity"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{lead_id}/review",
                json=review_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Lead Conversion Review", True, f"Review completed: {data.get('message')}")
                    return True
                else:
                    self.log_test("Lead Conversion Review", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead Conversion Review", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lead Conversion Review", False, f"Exception: {str(e)}")
            return False

    def test_lead_to_opportunity_conversion(self):
        """Test converting approved lead to opportunity"""
        if not self.token:
            self.log_test("Lead to Opportunity Conversion", False, "No authentication token")
            return False
            
        if not self.created_resources['leads']:
            self.log_test("Lead to Opportunity Conversion", False, "No leads available for testing")
            return False
            
        try:
            lead_id = self.created_resources['leads'][0]
            conversion_data = {
                "opportunity_name": f"CRM Opportunity {uuid.uuid4().hex[:4]}",
                "notes": "Converting qualified lead to opportunity"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{lead_id}/convert-to-opportunity",
                json=conversion_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    opportunity_id = data.get("data", {}).get("opportunity_id")
                    pot_id = data.get("data", {}).get("opportunity_pot_id")
                    if opportunity_id:
                        self.created_resources['opportunities'].append(opportunity_id)
                    self.log_test("Lead to Opportunity Conversion", True, f"Opportunity created: {pot_id}")
                    return True
                else:
                    self.log_test("Lead to Opportunity Conversion", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead to Opportunity Conversion", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lead to Opportunity Conversion", False, f"Exception: {str(e)}")
            return False

    # ========== OPPORTUNITY MANAGEMENT TESTS ==========
    def test_create_opportunity_direct(self):
        """Test creating opportunity directly (not from lead conversion)"""
        if not self.token:
            self.log_test("Create Opportunity Direct", False, "No authentication token")
            return False
            
        # Get company and contact IDs
        company_id = None
        contact_id = None
        
        if self.created_resources['companies']:
            company_id = self.created_resources['companies'][0]
        if self.created_resources['contacts']:
            contact_id = self.created_resources['contacts'][0]
            
        if not company_id:
            self.log_test("Create Opportunity Direct", False, "No company available")
            return False
            
        try:
            opportunity_data = {
                "company_id": company_id,
                "contact_id": contact_id,
                "name": f"Direct Opportunity {uuid.uuid4().hex[:4]}",
                "amount": 750000.0,
                "notes": "Direct opportunity creation test",
                "close_date": (datetime.now() + timedelta(days=60)).isoformat(),
                "stage": "L1_Prospect",
                "status": "Open"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/opportunities",
                json=opportunity_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    opportunity_id = data.get("data", {}).get("id")
                    pot_id = data.get("data", {}).get("pot_id")
                    if opportunity_id:
                        self.created_resources['opportunities'].append(opportunity_id)
                    self.log_test("Create Opportunity Direct", True, f"Opportunity created: {pot_id}")
                    return True
                else:
                    self.log_test("Create Opportunity Direct", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Create Opportunity Direct", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Opportunity Direct", False, f"Exception: {str(e)}")
            return False

    def test_get_opportunities(self):
        """Test getting opportunities list"""
        if not self.token:
            self.log_test("Get Opportunities", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/opportunities",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    opportunities = data.get("data", {}).get("opportunities", [])
                    self.log_test("Get Opportunities", True, f"Retrieved {len(opportunities)} opportunities")
                    return True
                else:
                    self.log_test("Get Opportunities", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Get Opportunities", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Opportunities", False, f"Exception: {str(e)}")
            return False

    def test_opportunity_stage_progression(self):
        """Test opportunity stage progression L1 -> L2"""
        if not self.token:
            self.log_test("Opportunity Stage Progression", False, "No authentication token")
            return False
            
        if not self.created_resources['opportunities']:
            self.log_test("Opportunity Stage Progression", False, "No opportunities available")
            return False
            
        try:
            opportunity_id = self.created_resources['opportunities'][0]
            stage_data = {
                "stage": "L2_Qualification",
                "notes": "Moving to qualification stage",
                "stage_specific_data": {
                    "qualification_completed": True,
                    "budget_confirmed": True,
                    "decision_maker_identified": True
                }
            }
            
            response = self.session.patch(
                f"{self.base_url}/api/opportunities/{opportunity_id}/stage",
                json=stage_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    stage = data.get("data", {}).get("stage")
                    probability = data.get("data", {}).get("probability")
                    self.log_test("Opportunity Stage Progression", True, f"Stage updated to: {stage} (Probability: {probability}%)")
                    return True
                else:
                    self.log_test("Opportunity Stage Progression", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Opportunity Stage Progression", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Opportunity Stage Progression", False, f"Exception: {str(e)}")
            return False

    # ========== USER MANAGEMENT TESTS ==========
    def test_get_users(self):
        """Test getting users list"""
        if not self.token:
            self.log_test("Get Users", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/users",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    users = data.get("data", {}).get("users", [])
                    self.log_test("Get Users", True, f"Retrieved {len(users)} users")
                    return True
                else:
                    self.log_test("Get Users", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Get Users", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Users", False, f"Exception: {str(e)}")
            return False

    def test_role_based_access(self):
        """Test role-based access control by trying different user roles"""
        # Test with sales user
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
                    sales_token = data["data"]["token"]
                    
                    # Test sales user can access leads
                    headers = {"Authorization": f"Bearer {sales_token}", "Content-Type": "application/json"}
                    leads_response = self.session.get(f"{self.base_url}/api/leads", headers=headers)
                    
                    if leads_response.status_code == 200:
                        self.log_test("Role-Based Access Control", True, "Sales user can access leads")
                        return True
                    else:
                        self.log_test("Role-Based Access Control", False, f"Sales user cannot access leads: {leads_response.status_code}")
                        return False
                else:
                    self.log_test("Role-Based Access Control", False, "Sales login failed")
                    return False
            else:
                self.log_test("Role-Based Access Control", False, f"Sales login status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Role-Based Access Control", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all CRM tests in sequence"""
        print("🚀 Starting Comprehensive CRM API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence - order matters for dependencies
        tests = [
            # Health and Authentication
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_login_admin),
            ("Dashboard Access", self.test_dashboard_access),
            ("Invalid Login", self.test_invalid_login),
            
            # Company Management
            ("Company Creation", self.test_create_company),
            ("Company Listing", self.test_get_companies),
            
            # Contact Management
            ("Contact Creation", self.test_create_contact),
            ("Contact Listing", self.test_get_contacts),
            
            # Lead Management
            ("Lead Creation", self.test_create_lead),
            ("Lead Listing", self.test_get_leads),
            ("Lead Status Update", self.test_lead_status_update),
            
            # Lead Conversion Workflow
            ("Lead Conversion Request", self.test_lead_conversion_request),
            ("Lead Conversion Review", self.test_lead_conversion_review),
            ("Lead to Opportunity Conversion", self.test_lead_to_opportunity_conversion),
            
            # Opportunity Management
            ("Direct Opportunity Creation", self.test_create_opportunity_direct),
            ("Opportunity Listing", self.test_get_opportunities),
            ("Opportunity Stage Progression", self.test_opportunity_stage_progression),
            
            # User Management & RBAC
            ("User Management", self.test_get_users),
            ("Role-Based Access Control", self.test_role_based_access),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            test_func()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! CRM backend is fully functional.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    # Use the backend URL from frontend env
    backend_url = "http://10.60.90.76:8000"
    
    try:
        with open("/app/frontend/.env", "r") as f:
            for line in f:
                if line.startswith("VITE_BACKEND_URL="):
                    backend_url = line.split("=", 1)[1].strip()
                    break
    except:
        pass
    
    print(f"🔧 Using backend URL: {backend_url}")
    
    tester = CRMComprehensiveTester(backend_url)
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())