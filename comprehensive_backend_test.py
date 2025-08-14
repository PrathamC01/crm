#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for CRM Company Management
Tests all company and document management endpoints as requested by main agent
"""

import requests
import sys
import json
import io
import os
from datetime import datetime

class ComprehensiveAPITester:
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

    # ========== AUTHENTICATION TESTS ==========
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
                    user_info = data["data"].get("user", {})
                    self.log_test("Admin Login", True, f"Token received, User: {user_info.get('name', 'Unknown')}")
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

    # ========== COMPANY MANAGEMENT TESTS ==========
    def test_company_creation_comprehensive(self):
        """Test POST /api/companies/ - Company Creation with comprehensive data"""
        if not self.token:
            self.log_test("Company Creation (Comprehensive)", False, "No authentication token")
            return False
            
        try:
            # Use the exact sample data provided by main agent
            company_data = {
                "name": "Test Company API",
                "gst_number": "29ABCDE1234F1Z5",
                "pan_number": "ABCDE1234F",
                "industry_category": "Technology",
                "address": "123 API Test Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400001",
                "website": "https://apitest.com",
                "description": "Test company for API validation"
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
                    
                    # Verify complete company data is returned (not null)
                    required_fields = ["id", "name", "gst_number", "pan_number", "industry_category", 
                                     "address", "city", "state", "country", "postal_code", "website", "description"]
                    missing_fields = [field for field in required_fields if company_info.get(field) is None]
                    
                    if not missing_fields:
                        self.log_test("Company Creation (Comprehensive)", True, 
                                    f"Company created: {company_info.get('name')} (ID: {self.created_company_id})")
                        return True
                    else:
                        self.log_test("Company Creation (Comprehensive)", False, 
                                    f"Missing fields in response: {missing_fields}")
                        return False
                else:
                    self.log_test("Company Creation (Comprehensive)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Creation (Comprehensive)", False, 
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Creation (Comprehensive)", False, f"Exception: {str(e)}")
            return False

    def test_company_listing_with_pagination(self):
        """Test GET /api/companies/ - Company Listing with pagination"""
        if not self.token:
            self.log_test("Company Listing (Pagination)", False, "No authentication token")
            return False
            
        try:
            # Test with pagination parameters
            response = self.session.get(
                f"{self.base_url}/api/companies/?skip=0&limit=10",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    companies_data = data.get("data", {})
                    companies = companies_data.get("companies", [])
                    total = companies_data.get("total", 0)
                    skip = companies_data.get("skip", 0)
                    limit = companies_data.get("limit", None)
                    
                    self.log_test("Company Listing (Pagination)", True, 
                                f"Retrieved {len(companies)} companies (Total: {total}, Skip: {skip}, Limit: {limit})")
                    return True
                else:
                    self.log_test("Company Listing (Pagination)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Listing (Pagination)", False, 
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Listing (Pagination)", False, f"Exception: {str(e)}")
            return False

    def test_company_search_functionality(self):
        """Test GET /api/companies/ - Search functionality"""
        if not self.token:
            self.log_test("Company Search", False, "No authentication token")
            return False
            
        try:
            # Test search functionality
            response = self.session.get(
                f"{self.base_url}/api/companies/?search=Test",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    companies_data = data.get("data", {})
                    companies = companies_data.get("companies", [])
                    self.log_test("Company Search", True, f"Search returned {len(companies)} companies")
                    return True
                else:
                    self.log_test("Company Search", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Search", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Company Search", False, f"Exception: {str(e)}")
            return False

    def test_company_get_by_id_with_documents(self):
        """Test GET /api/companies/{id} - Get by ID with include_documents parameter"""
        if not self.token:
            self.log_test("Company Get by ID (With Documents)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Get by ID (With Documents)", False, "No company ID available")
            return False
            
        try:
            # Test with include_documents=true
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}?include_documents=true",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company = data.get("data", {})
                    self.log_test("Company Get by ID (With Documents)", True, 
                                f"Retrieved company: {company.get('name')} with documents parameter")
                    return True
                else:
                    self.log_test("Company Get by ID (With Documents)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Get by ID (With Documents)", False, 
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Get by ID (With Documents)", False, f"Exception: {str(e)}")
            return False

    def test_company_get_by_id_without_documents(self):
        """Test GET /api/companies/{id} - Get by ID without include_documents parameter"""
        if not self.token:
            self.log_test("Company Get by ID (Without Documents)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Get by ID (Without Documents)", False, "No company ID available")
            return False
            
        try:
            # Test without include_documents parameter
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    company = data.get("data", {})
                    self.log_test("Company Get by ID (Without Documents)", True, 
                                f"Retrieved company: {company.get('name')} without documents parameter")
                    return True
                else:
                    self.log_test("Company Get by ID (Without Documents)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Get by ID (Without Documents)", False, 
                            f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Company Get by ID (Without Documents)", False, f"Exception: {str(e)}")
            return False

    def test_company_partial_update(self):
        """Test PUT /api/companies/{id} - Partial update (only some fields)"""
        if not self.token:
            self.log_test("Company Partial Update", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Company Partial Update", False, "No company ID available")
            return False
            
        try:
            # Test partial update - only updating some fields
            update_data = {
                "description": "Updated description for comprehensive testing",
                "website": "https://updated-apitest.com"
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
                    # Verify updated data is returned properly
                    if (company.get("description") == update_data["description"] and 
                        company.get("website") == update_data["website"]):
                        self.log_test("Company Partial Update", True, 
                                    f"Partial update successful: {company.get('name')}")
                        return True
                    else:
                        self.log_test("Company Partial Update", False, 
                                    "Updated data not properly returned")
                        return False
                else:
                    self.log_test("Company Partial Update", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Company Partial Update", False, 
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Company Partial Update", False, f"Exception: {str(e)}")
            return False

    # ========== GST/PAN VALIDATION TESTS ==========
    def test_gst_validation_comprehensive(self):
        """Test GST validation with various formats"""
        if not self.token:
            self.log_test("GST Validation (Comprehensive)", False, "No authentication token")
            return False
            
        try:
            # Test invalid GST formats
            invalid_gst_cases = [
                "INVALID_GST",
                "12345678901234567890",  # Too long
                "123",  # Too short
                "29ABCDE1234F1Z",  # Missing digit
            ]
            
            for invalid_gst in invalid_gst_cases:
                company_data = {
                    "name": f"Invalid GST Test {datetime.now().strftime('%H%M%S')}",
                    "gst_number": invalid_gst,
                    "pan_number": "ABCDE1234F",
                    "industry_category": "Technology"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/companies/",
                    json=company_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code != 422:  # Should be validation error
                    self.log_test("GST Validation (Comprehensive)", False, 
                                f"Invalid GST '{invalid_gst}' was accepted")
                    return False
            
            self.log_test("GST Validation (Comprehensive)", True, 
                        "All invalid GST formats correctly rejected")
            return True
                
        except Exception as e:
            self.log_test("GST Validation (Comprehensive)", False, f"Exception: {str(e)}")
            return False

    def test_pan_validation_comprehensive(self):
        """Test PAN validation with various formats"""
        if not self.token:
            self.log_test("PAN Validation (Comprehensive)", False, "No authentication token")
            return False
            
        try:
            # Test invalid PAN formats
            invalid_pan_cases = [
                "INVALID_PAN",
                "123456789012345",  # Too long
                "ABC",  # Too short
                "ABCDE1234",  # Missing character
            ]
            
            for invalid_pan in invalid_pan_cases:
                company_data = {
                    "name": f"Invalid PAN Test {datetime.now().strftime('%H%M%S')}",
                    "gst_number": "29ABCDE1234F1Z5",
                    "pan_number": invalid_pan,
                    "industry_category": "Technology"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/companies/",
                    json=company_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code != 422:  # Should be validation error
                    self.log_test("PAN Validation (Comprehensive)", False, 
                                f"Invalid PAN '{invalid_pan}' was accepted")
                    return False
            
            self.log_test("PAN Validation (Comprehensive)", True, 
                        "All invalid PAN formats correctly rejected")
            return True
                
        except Exception as e:
            self.log_test("PAN Validation (Comprehensive)", False, f"Exception: {str(e)}")
            return False

    # ========== DOCUMENT MANAGEMENT TESTS ==========
    def test_document_upload_pdf(self):
        """Test POST /api/companies/{id}/upload - Upload PDF file"""
        if not self.token:
            self.log_test("Document Upload (PDF)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Upload (PDF)", False, "No company ID available")
            return False
            
        try:
            # Create a dummy PDF file content
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
            
            files = {
                'file': ('test_gst_certificate.pdf', io.BytesIO(pdf_content), 'application/pdf')
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
                    self.log_test("Document Upload (PDF)", True, 
                                f"PDF uploaded: {doc_info.get('original_filename')}")
                    return True
                else:
                    self.log_test("Document Upload (PDF)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Document Upload (PDF)", False, 
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload (PDF)", False, f"Exception: {str(e)}")
            return False

    def test_document_upload_image(self):
        """Test POST /api/companies/{id}/upload - Upload image file"""
        if not self.token:
            self.log_test("Document Upload (Image)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Upload (Image)", False, "No company ID available")
            return False
            
        try:
            # Create a dummy image file content (minimal JPEG header)
            jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            
            files = {
                'file': ('test_pan_card.jpg', io.BytesIO(jpeg_content), 'image/jpeg')
            }
            data = {
                'document_type': 'PAN_CARD'
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
                    self.log_test("Document Upload (Image)", True, 
                                f"Image uploaded: {doc_info.get('original_filename')}")
                    return True
                else:
                    self.log_test("Document Upload (Image)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Document Upload (Image)", False, 
                            f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload (Image)", False, f"Exception: {str(e)}")
            return False

    def test_document_upload_file_validation(self):
        """Test file validation (size, type)"""
        if not self.token:
            self.log_test("Document Upload (File Validation)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Upload (File Validation)", False, "No company ID available")
            return False
            
        try:
            # Test invalid file type
            text_content = b"This is a text file which should be rejected"
            
            files = {
                'file': ('invalid_file.txt', io.BytesIO(text_content), 'text/plain')
            }
            data = {
                'document_type': 'OTHER'
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = self.session.post(
                f"{self.base_url}/api/companies/{self.created_company_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 400:  # Bad request expected for invalid file type
                self.log_test("Document Upload (File Validation)", True, 
                            "Invalid file type correctly rejected")
                return True
            else:
                self.log_test("Document Upload (File Validation)", False, 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload (File Validation)", False, f"Exception: {str(e)}")
            return False

    def test_document_types_validation(self):
        """Test document types: GST_CERTIFICATE, PAN_CARD, OTHER"""
        if not self.token:
            self.log_test("Document Types Validation", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Types Validation", False, "No company ID available")
            return False
            
        try:
            # Test valid document types
            valid_types = ['GST_CERTIFICATE', 'PAN_CARD', 'OTHER']
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n>>\nstartxref\n32\n%%EOF"
            
            for doc_type in valid_types:
                files = {
                    'file': (f'test_{doc_type.lower()}.pdf', io.BytesIO(pdf_content), 'application/pdf')
                }
                data = {
                    'document_type': doc_type
                }
                
                headers = {"Authorization": f"Bearer {self.token}"}
                
                response = self.session.post(
                    f"{self.base_url}/api/companies/{self.created_company_id}/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code != 200:
                    self.log_test("Document Types Validation", False, 
                                f"Valid document type '{doc_type}' was rejected")
                    return False
            
            # Test invalid document type
            files = {
                'file': ('test_invalid.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {
                'document_type': 'INVALID_TYPE'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/companies/{self.created_company_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 400:  # Should reject invalid type
                self.log_test("Document Types Validation", True, 
                            "All document type validations working correctly")
                return True
            else:
                self.log_test("Document Types Validation", False, 
                            "Invalid document type was accepted")
                return False
                
        except Exception as e:
            self.log_test("Document Types Validation", False, f"Exception: {str(e)}")
            return False

    def test_document_listing_comprehensive(self):
        """Test GET /api/companies/{id}/documents - Document Listing"""
        if not self.token:
            self.log_test("Document Listing (Comprehensive)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Listing (Comprehensive)", False, "No company ID available")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/companies/{self.created_company_id}/documents",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") is True:
                    documents_data = data.get("data", {})
                    documents = documents_data.get("documents", [])
                    
                    # Verify document structure
                    if documents:
                        doc = documents[0]
                        required_fields = ["id", "filename", "original_filename", "file_size", 
                                         "document_type", "mime_type", "uploaded_on"]
                        missing_fields = [field for field in required_fields if field not in doc]
                        
                        if not missing_fields:
                            self.log_test("Document Listing (Comprehensive)", True, 
                                        f"Retrieved {len(documents)} documents with complete structure")
                            return True
                        else:
                            self.log_test("Document Listing (Comprehensive)", False, 
                                        f"Missing fields in document structure: {missing_fields}")
                            return False
                    else:
                        self.log_test("Document Listing (Comprehensive)", True, 
                                    "Retrieved 0 documents (empty list)")
                        return True
                else:
                    self.log_test("Document Listing (Comprehensive)", False, f"Response: {data}")
                    return False
            else:
                self.log_test("Document Listing (Comprehensive)", False, 
                            f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Listing (Comprehensive)", False, f"Exception: {str(e)}")
            return False

    def test_document_delete_comprehensive(self):
        """Test DELETE /api/companies/{id}/documents/{doc_id} - Document Delete"""
        if not self.token:
            self.log_test("Document Delete (Comprehensive)", False, "No authentication token")
            return False
            
        if not self.created_company_id:
            self.log_test("Document Delete (Comprehensive)", False, "No company ID available")
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
                            self.log_test("Document Delete (Comprehensive)", True, 
                                        f"Document {doc_id} deleted successfully")
                            return True
                        else:
                            self.log_test("Document Delete (Comprehensive)", False, 
                                        f"Delete response: {delete_data}")
                            return False
                    else:
                        self.log_test("Document Delete (Comprehensive)", False, 
                                    f"Delete status code: {delete_response.status_code}")
                        return False
                else:
                    self.log_test("Document Delete (Comprehensive)", True, 
                                "No documents available to delete (expected after previous tests)")
                    return True
            else:
                self.log_test("Document Delete (Comprehensive)", False, 
                            f"Failed to get documents: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Delete (Comprehensive)", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all comprehensive API tests"""
        print("🚀 Starting Comprehensive CRM Company Management API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test sequence - order matters for dependencies
        tests = [
            # Authentication
            ("Admin Login", self.test_admin_login),
            
            # Company Management - Core CRUD
            ("Company Creation (Comprehensive)", self.test_company_creation_comprehensive),
            ("Company Listing (Pagination)", self.test_company_listing_with_pagination),
            ("Company Search", self.test_company_search_functionality),
            ("Company Get by ID (With Documents)", self.test_company_get_by_id_with_documents),
            ("Company Get by ID (Without Documents)", self.test_company_get_by_id_without_documents),
            ("Company Partial Update", self.test_company_partial_update),
            
            # Validation Tests
            ("GST Validation (Comprehensive)", self.test_gst_validation_comprehensive),
            ("PAN Validation (Comprehensive)", self.test_pan_validation_comprehensive),
            
            # Document Management
            ("Document Upload (PDF)", self.test_document_upload_pdf),
            ("Document Upload (Image)", self.test_document_upload_image),
            ("Document Upload (File Validation)", self.test_document_upload_file_validation),
            ("Document Types Validation", self.test_document_types_validation),
            ("Document Listing (Comprehensive)", self.test_document_listing_comprehensive),
            ("Document Delete (Comprehensive)", self.test_document_delete_comprehensive),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            test_func()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All comprehensive tests passed! CRM Company Management is fully functional.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    backend_url = "http://localhost:8001"
    
    print(f"🔧 Using backend URL: {backend_url}")
    
    tester = ComprehensiveAPITester(backend_url)
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())