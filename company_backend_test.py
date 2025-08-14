#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for CRM Company Management
Tests all company and document management endpoints as requested
"""

import requests
import sys
import json
import io
import os
from datetime import datetime

class CompanyAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_company_id = None

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

    def test_admin_login(self):
        """Test admin login to get authentication token"""
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
                    self.log_test("Admin Login", True, f"Token received: {self.token[:20]}...")
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

    def test_company_creation(self):
        """Test POST /api/companies/ - Company Creation"""
        if not self.token:
            self.log_test("Company Creation", False, "No authentication token")
            return False
            
        try:
            company_data = {
                "name": f"Test Company Ltd {datetime.now().strftime('%H%M%S')}",
                "gst_number": "22AAAAA0000A1Z5",  # Valid GST format
                "pan_number": "AAAAA0000A",       # Valid PAN format
                "industry_category": "Technology",
                "address": "123 Test Street, Tech Park",
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
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company_info = data.get("data", {})
                    self.created_company_id = company_info.get("id")
                    self.log_test("Company Creation", True, f"Company created: {company_info.get('name')} (ID: {self.created_company_id})")
                    return True
                else:
                    self.log_test("Company Creation", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Creation", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Creation", False, f"Exception: {str(e)}")
            return False

    def test_company_listing(self):
        """Test GET /api/companies/ - Company Listing"""
        if not self.token:
            self.log_test("Company Listing", False, "No authentication token")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/companies/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    companies_data = data.get("data", {})
                    companies = companies_data.get("companies", [])
                    total = companies_data.get("total", 0)
                    self.log_test("Company Listing", True, f"Retrieved {len(companies)} companies (Total: {total})")
                    return True
                else:
                    self.log_test("Company Listing", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Listing", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Listing", False, f"Exception: {str(e)}")
            return False

    def test_company_get_by_id(self):
        """Test GET /api/companies/{id} - Company Get by ID"""
        if not self.token:
            self.log_test("Company Get by ID", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Get by ID", False, "No company ID available")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company = data.get("data", {})
                    self.log_test("Company Get by ID", True, f"Retrieved company: {company.get('name')}")
                    return True
                else:
                    self.log_test("Company Get by ID", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Get by ID", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Get by ID", False, f"Exception: {str(e)}")
            return False

    def test_company_update(self):
        """Test PUT /api/companies/{id} - Company Update"""
        if not self.token:
            self.log_test("Company Update", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Update", False, "No company ID available")
            return False
            
        try:
            update_data = {
                "description": "Updated description for testing",
                "website": "https://updated-testcompany.com",
                "industry_category": "Software Development"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/companies/{self.created_company_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company = data.get("data", {})
                    self.log_test("Company Update", True, f"Updated company: {company.get('name')}")
                    return True
                else:
                    self.log_test("Company Update", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Update", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Update", False, f"Exception: {str(e)}")
            return False

    def test_gst_pan_validation(self):
        """Test GST/PAN validation during company creation"""
        if not self.token:
            self.log_test("GST/PAN Validation", False, "No authentication token")
            return False
            
        try:
            # Test invalid GST
            invalid_company_data = {
                "name": f"Invalid GST Company {datetime.now().strftime('%H%M%S')}",
                "gst_number": "INVALID_GST",  # Invalid GST format
                "pan_number": "AAAAA0000A",
                "industry_category": "Technology"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/companies/",
                json=invalid_company_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 422:  # Validation error expected
                self.log_test("GST/PAN Validation", True, "Invalid GST correctly rejected")
                return True
            else:
                self.log_test("GST/PAN Validation", False, f"Expected 422, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GST/PAN Validation", False, f"Exception: {str(e)}")
            return False

    def test_document_upload_valid(self):
        """Test POST /api/companies/{id}/upload - Document Upload with valid file"""
        if not self.token:
            self.log_test("Document Upload (Valid)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Upload (Valid)", False, "No company ID available")
            return False
            
        try:
            # Create a dummy PDF file content
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
            
            files = {
                'file': ('test_document.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {
                'document_type': 'GST_CERTIFICATE'
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = self.session.post(
                f"{self.base_url}/api/companies/{self.created_company_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    doc_info = data.get("data", {})
                    self.log_test("Document Upload (Valid)", True, f"Document uploaded: {doc_info.get('original_filename')}")
                    return True
                else:
                    self.log_test("Document Upload (Valid)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Document Upload (Valid)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload (Valid)", False, f"Exception: {str(e)}")
            return False

    def test_document_upload_invalid_type(self):
        """Test document upload with invalid file type"""
        if not self.token:
            self.log_test("Document Upload (Invalid Type)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Upload (Invalid Type)", False, "No company ID available")
            return False
            
        try:
            # Create a dummy text file (invalid type)
            text_content = b"This is a text file which should be rejected"
            
            files = {
                'file': ('test_document.txt', io.BytesIO(text_content), 'text/plain')
            }
            data = {
                'document_type': 'GST_CERTIFICATE'
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = self.session.post(
                f"{self.base_url}/api/companies/{self.created_company_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 400:  # Bad request expected for invalid file type
                self.log_test("Document Upload (Invalid Type)", True, "Invalid file type correctly rejected")
                return True
            else:
                self.log_test("Document Upload (Invalid Type)", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload (Invalid Type)", False, f"Exception: {str(e)}")
            return False

    def test_document_listing(self):
        """Test GET /api/companies/{id}/documents - Document Listing"""
        if not self.token:
            self.log_test("Document Listing", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Listing", False, "No company ID available")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}/documents",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    documents = data.get("data", {}).get("documents", [])
                    self.log_test("Document Listing", True, f"Retrieved {len(documents)} documents")
                    return True
                else:
                    self.log_test("Document Listing", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Document Listing", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Listing", False, f"Exception: {str(e)}")
            return False

    def test_document_delete(self):
        """Test DELETE /api/companies/{id}/documents/{doc_id} - Document Delete"""
        if not self.token:
            self.log_test("Document Delete", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Delete", False, "No company ID available")
            return False
            
        try:
            # First get documents to find one to delete
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}/documents",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("data", {}).get("documents", [])
                
                if documents:
                    doc_id = documents[0]["id"]
                    
                    # Now delete the document
                    delete_response = self.session.delete(
                        f"{self.base_url}/api/companies/{self.created_company_id}/documents/{doc_id}",
                        headers=self.get_auth_headers()
                    )
                    
                    if delete_response.status_code == 200:
                        delete_data = delete_response.json()
                        if delete_data.get("status") is True:
                            self.log_test("Document Delete", True, f"Document {doc_id} deleted successfully")
                            return True
                        else:
                            self.log_test("Document Delete", False, f"Delete response: {delete_data}")
                            return False
                    else:
                        self.log_test("Document Delete", False, f"Delete status code: {delete_response.status_code}")
                        return False
                else:
                    self.log_test("Document Delete", False, "No documents available to delete")
                    return False
            else:
                self.log_test("Document Delete", False, f"Failed to get documents: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Delete", False, f"Exception: {str(e)}")
            return False

    def test_company_delete(self):
        """Test DELETE /api/companies/{id} - Company Delete"""
        if not self.token:
            self.log_test("Company Delete", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Delete", False, "No company ID available")
            return False
            
        try:
            response = self.session.delete(
                f"{self.base_url}/api/companies/{self.created_company_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    self.log_test("Company Delete", True, f"Company {self.created_company_id} deleted successfully")
                    return True
                else:
                    self.log_test("Company Delete", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Delete", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Delete", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all company management API tests"""
        print("🚀 Starting Company Management API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence - order matters for dependencies
        tests = [
            ("Admin Login", self.test_admin_login),
            ("Company Creation", self.test_company_creation),
            ("Company Listing", self.test_company_listing),
            ("Company Get by ID", self.test_company_get_by_id),
            ("Company Update", self.test_company_update),
            ("GST/PAN Validation", self.test_gst_pan_validation),
            ("Document Upload (Valid)", self.test_document_upload_valid),
            ("Document Upload (Invalid Type)", self.test_document_upload_invalid_type),
            ("Document Listing", self.test_document_listing),
            ("Document Delete", self.test_document_delete),
            ("Company Delete", self.test_company_delete),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            test_func()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All company management tests passed!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    backend_url = "http://localhost:8001"
    
    print(f"🔧 Using backend URL: {backend_url}")
    
    tester = CompanyAPITester(backend_url)
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())