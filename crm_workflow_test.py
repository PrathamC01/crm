#!/usr/bin/env python3
"""
CRM Workflow Testing - Lead Creation → Qualification → Conversion to Opportunity
Tests the complete CRM workflow as requested by the user
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class CRMWorkflowTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.admin_token = None
        self.sales_token = None
        self.reviewer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_lead_id = None
        self.created_opportunity_id = None

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

    def setup_authentication(self):
        """Setup authentication tokens for all user types"""
        try:
            # Admin login
            login_data = {"email_or_username": "admin", "password": "admin123"}
            response = self.session.post(f"{self.base_url}/api/login", json=login_data)
            if response.status_code == 200:
                self.admin_token = response.json()["data"]["token"]
                print("🔑 Admin authentication successful")
            
            # Sales login
            login_data = {"email_or_username": "sales", "password": "sales123"}
            response = self.session.post(f"{self.base_url}/api/login", json=login_data)
            if response.status_code == 200:
                self.sales_token = response.json()["data"]["token"]
                print("🔑 Sales authentication successful")
            
            # Reviewer login
            login_data = {"email_or_username": "reviewer", "password": "reviewer123"}
            response = self.session.post(f"{self.base_url}/api/login", json=login_data)
            if response.status_code == 200:
                self.reviewer_token = response.json()["data"]["token"]
                print("🔑 Reviewer authentication successful")
                
            return True
        except Exception as e:
            print(f"❌ Authentication setup failed: {e}")
            return False

    def test_lead_creation(self):
        """Test creating a new lead with sales user"""
        if not self.sales_token:
            self.log_test("Lead Creation", False, "No sales token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.sales_token}",
                "Content-Type": "application/json"
            }
            
            # Create a comprehensive lead
            lead_data = {
                "project_title": "Enterprise CRM Implementation Project",
                "lead_source": "website",
                "lead_sub_type": "inbound",
                "tender_sub_type": "open",
                "products_services": ["CRM Software", "Implementation Services", "Training"],
                "company_id": 1,  # Tech Corp Ltd
                "sub_business_type": "B2B Software",
                "end_customer_region": "Mumbai",
                "partner_involved": False,
                "tender_fee": 50000.0,
                "currency": "INR",
                "submission_type": "online",
                "tender_authority": "Tech Corp Ltd",
                "tender_for": "CRM System Implementation",
                "emd_required": True,
                "emd_amount": 100000.0,
                "emd_currency": "INR",
                "bg_required": False,
                "expected_revenue": 2500000.0,
                "revenue_currency": "INR",
                "convert_to_opportunity_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "competitors": ["Salesforce", "HubSpot"],
                "status": "new",
                "priority": "high",
                "qualification_notes": "High-value enterprise client with immediate need for CRM solution",
                "contacts": [
                    {
                        "name": "John Smith",
                        "email": "john.smith@techcorp.com",
                        "phone": "+91-9876543210",
                        "designation": "IT Director",
                        "decision_maker": True
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/",
                json=lead_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.created_lead_id = data["data"]["id"]
                    self.log_test("Lead Creation", True, f"Lead created with ID: {self.created_lead_id}")
                    return True
                else:
                    self.log_test("Lead Creation", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead Creation", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lead Creation", False, f"Exception: {str(e)}")
            return False

    def test_lead_qualification(self):
        """Test lead qualification and update"""
        if not self.sales_token or not self.created_lead_id:
            self.log_test("Lead Qualification", False, "No sales token or lead ID available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.sales_token}",
                "Content-Type": "application/json"
            }
            
            # Update lead with qualification information
            qualification_data = {
                "status": "qualified",
                "priority": "high",
                "qualification_notes": "Lead qualified after detailed discussion. Client has budget approved and timeline confirmed.",
                "lead_score": 85,
                "ready_for_conversion": True
            }
            
            response = self.session.put(
                f"{self.base_url}/api/leads/{self.created_lead_id}",
                json=qualification_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Lead Qualification", True, f"Lead qualified successfully")
                    return True
                else:
                    self.log_test("Lead Qualification", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Lead Qualification", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lead Qualification", False, f"Exception: {str(e)}")
            return False

    def test_conversion_request(self):
        """Test requesting conversion to opportunity"""
        if not self.sales_token or not self.created_lead_id:
            self.log_test("Conversion Request", False, "No sales token or lead ID available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.sales_token}",
                "Content-Type": "application/json"
            }
            
            # Request conversion to opportunity
            request_data = {
                "notes": "Lead is fully qualified and ready for conversion. Client has confirmed budget and timeline."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{self.created_lead_id}/request-conversion",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Conversion Request", True, f"Conversion requested successfully")
                    return True
                else:
                    self.log_test("Conversion Request", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Conversion Request", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conversion Request", False, f"Exception: {str(e)}")
            return False

    def test_admin_review_approval(self):
        """Test admin review and approval of conversion request"""
        if not self.admin_token or not self.created_lead_id:
            self.log_test("Admin Review Approval", False, "No admin token or lead ID available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Approve the conversion request
            review_data = {
                "decision": "approved",
                "comments": "Lead meets all criteria for conversion. Approved for opportunity creation."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{self.created_lead_id}/review",
                json=review_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Admin Review Approval", True, f"Conversion approved successfully")
                    return True
                else:
                    self.log_test("Admin Review Approval", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Admin Review Approval", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Review Approval", False, f"Exception: {str(e)}")
            return False

    def test_convert_to_opportunity(self):
        """Test converting approved lead to opportunity"""
        if not self.sales_token or not self.created_lead_id:
            self.log_test("Convert to Opportunity", False, "No sales token or lead ID available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.sales_token}",
                "Content-Type": "application/json"
            }
            
            # Convert to opportunity
            conversion_data = {
                "opportunity_name": "Enterprise CRM Implementation Opportunity",
                "notes": "Converted from qualified lead. High-priority enterprise client."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/leads/{self.created_lead_id}/convert-to-opportunity",
                json=conversion_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.created_opportunity_id = data["data"]["opportunity_id"]
                    pot_id = data["data"]["opportunity_pot_id"]
                    self.log_test("Convert to Opportunity", True, f"Opportunity created with POT ID: {pot_id}")
                    return True
                else:
                    self.log_test("Convert to Opportunity", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Convert to Opportunity", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Convert to Opportunity", False, f"Exception: {str(e)}")
            return False

    def test_opportunity_verification(self):
        """Test that the opportunity was created correctly"""
        if not self.admin_token or not self.created_opportunity_id:
            self.log_test("Opportunity Verification", False, "No admin token or opportunity ID available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Get the created opportunity
            response = self.session.get(
                f"{self.base_url}/api/opportunities/{self.created_opportunity_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    opportunity = data["data"]
                    pot_id = opportunity.get("pot_id", "")
                    stage = opportunity.get("stage", "")
                    self.log_test("Opportunity Verification", True, f"Opportunity verified - POT ID: {pot_id}, Stage: {stage}")
                    return True
                else:
                    self.log_test("Opportunity Verification", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Opportunity Verification", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Opportunity Verification", False, f"Exception: {str(e)}")
            return False

    def run_workflow_tests(self):
        """Run complete CRM workflow tests"""
        print("🚀 Starting CRM Workflow Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Aborting tests.")
            return 1
        
        print()
        
        # Test sequence - Complete CRM workflow
        tests = [
            self.test_lead_creation,
            self.test_lead_qualification,
            self.test_conversion_request,
            self.test_admin_review_approval,
            self.test_convert_to_opportunity,
            self.test_opportunity_verification
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 70)
        print(f"📊 Workflow Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 Complete CRM workflow tested successfully!")
            print(f"✨ Lead → Qualification → Conversion → Opportunity workflow is working!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} workflow tests failed")
            return 1

def main():
    """Main test runner"""
    backend_url = "http://localhost:8001"
    
    print(f"🔧 Using backend URL: {backend_url}")
    
    tester = CRMWorkflowTester(backend_url)
    return tester.run_workflow_tests()

if __name__ == "__main__":
    sys.exit(main())