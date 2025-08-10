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
        self.session_headers = {"x-session-id": TEST_SESSION_ID}
        self.test_results = {}
        
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
                if data.get("status") and "CRM Management System API" in data.get("message", ""):
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
            response = self.make_request("GET", "/api/session/info", headers=self.session_headers)
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
            response = self.make_request("POST", "/api/session/refresh", headers=self.session_headers)
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
            response = self.make_request("POST", "/api/logout", headers=self.session_headers)
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
                response = self.make_request("GET", endpoint, headers=self.session_headers)
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
                                       headers=self.session_headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data.get("data", {}).get("file_path"):
                    file_path = data["data"]["file_path"]
                    self.log_test("File Upload - Upload", True, "File uploaded successfully")
                    
                    # Test get file URL
                    try:
                        response = self.make_request("GET", f"/api/files/{file_path}", 
                                                   headers=self.session_headers)
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
                                                   headers=self.session_headers)
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
        print(f"Test Session ID: {TEST_SESSION_ID}")
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_session_management()
        self.test_dashboard_endpoints()
        self.test_file_upload_endpoints()
        self.test_masters_endpoints()
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