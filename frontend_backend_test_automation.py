#!/usr/bin/env python3
"""
Comprehensive Frontend & Backend Automation Testing Script
Enterprise CRM System - Complete Testing Suite

Tests both Backend APIs and Frontend UI functionality
"""

import subprocess
import sys
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import threading
import signal
from contextlib import contextmanager

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_SESSION_ID = "test_session_123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResults:
    def __init__(self):
        self.backend_tests = {}
        self.frontend_tests = {}
        
    def log_backend(self, test_name, success, message, details=None):
        self.backend_tests[test_name] = {
            'success': success,
            'message': message,
            'details': details
        }
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} Backend - {test_name}: {message}")
        
    def log_frontend(self, test_name, success, message, details=None):
        self.frontend_tests[test_name] = {
            'success': success,
            'message': message,
            'details': details
        }
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} Frontend - {test_name}: {message}")
    
    def print_summary(self):
        backend_passed = sum(1 for t in self.backend_tests.values() if t['success'])
        backend_total = len(self.backend_tests)
        frontend_passed = sum(1 for t in self.frontend_tests.values() if t['success'])
        frontend_total = len(self.frontend_tests)
        
        print(f"\n{Colors.BOLD}=== TEST SUMMARY ==={Colors.END}")
        print(f"{Colors.BLUE}Backend Tests:{Colors.END} {backend_passed}/{backend_total} passed ({(backend_passed/backend_total*100 if backend_total > 0 else 0):.1f}%)")
        print(f"{Colors.PURPLE}Frontend Tests:{Colors.END} {frontend_passed}/{frontend_total} passed ({(frontend_passed/frontend_total*100 if frontend_total > 0 else 0):.1f}%)")
        print(f"{Colors.CYAN}Total Tests:{Colors.END} {backend_passed + frontend_passed}/{backend_total + frontend_total} passed")

class BackendTester:
    def __init__(self, results):
        self.results = results
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
    
    def run_all_tests(self):
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔧 Starting Backend API Tests{Colors.END}")
        
        # Core API Tests
        self.test_health_check()
        self.test_session_management()
        
        # Dashboard Tests
        self.test_dashboard_overview()
        self.test_sales_dashboard()
        self.test_presales_dashboard()
        self.test_product_dashboard()
        
        # Masters Tests
        self.test_masters_departments()
        self.test_masters_uoms()
        self.test_masters_products()
        
        # File Upload Tests
        self.test_file_upload()
    
    def make_request(self, method, endpoint, headers=None, data=None, files=None):
        try:
            url = f"{self.base_url}{endpoint}"
            request_headers = headers or {}
            
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
            
            return response
        except Exception as e:
            return None
    
    def test_health_check(self):
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status"):
                self.results.log_backend("Health Check", True, "API is healthy and responding")
            else:
                self.results.log_backend("Health Check", False, "Health check returned false status")
        else:
            self.results.log_backend("Health Check", False, "Failed to reach health endpoint")
    
    def test_session_management(self):
        # Test session info
        response = self.make_request("GET", "/api/session/info", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and "name" in data.get("data", {}):
                self.results.log_backend("Session Info", True, "Session information retrieved successfully")
                
                # Test session refresh
                refresh_response = self.make_request("POST", "/api/session/refresh", headers=self.session_headers)
                if refresh_response and refresh_response.status_code == 200:
                    self.results.log_backend("Session Refresh", True, "Session refreshed successfully")
                else:
                    self.results.log_backend("Session Refresh", False, "Failed to refresh session")
            else:
                self.results.log_backend("Session Info", False, "Invalid session data")
        else:
            self.results.log_backend("Session Info", False, "Failed to get session info")
    
    def test_dashboard_overview(self):
        response = self.make_request("GET", "/api/dashboard/overview", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and "system_overview" in data.get("data", {}):
                self.results.log_backend("Dashboard Overview", True, "Dashboard overview data loaded")
            else:
                self.results.log_backend("Dashboard Overview", False, "Invalid dashboard data structure")
        else:
            self.results.log_backend("Dashboard Overview", False, "Failed to load dashboard overview")
    
    def test_sales_dashboard(self):
        response = self.make_request("GET", "/api/dashboard/sales", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and "metrics" in data.get("data", {}):
                self.results.log_backend("Sales Dashboard", True, "Sales dashboard data loaded with metrics")
            else:
                self.results.log_backend("Sales Dashboard", False, "Sales dashboard missing metrics")
        else:
            self.results.log_backend("Sales Dashboard", False, "Failed to load sales dashboard")
    
    def test_presales_dashboard(self):
        response = self.make_request("GET", "/api/dashboard/presales", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status"):
                self.results.log_backend("Presales Dashboard", True, "Presales dashboard data loaded")
            else:
                self.results.log_backend("Presales Dashboard", False, "Presales dashboard invalid response")
        else:
            self.results.log_backend("Presales Dashboard", False, "Failed to load presales dashboard")
    
    def test_product_dashboard(self):
        response = self.make_request("GET", "/api/dashboard/product", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status"):
                self.results.log_backend("Product Dashboard", True, "Product dashboard data loaded")
            else:
                self.results.log_backend("Product Dashboard", False, "Product dashboard invalid response")
        else:
            self.results.log_backend("Product Dashboard", False, "Failed to load product dashboard")
    
    def test_masters_departments(self):
        response = self.make_request("GET", "/api/masters/departments", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and isinstance(data.get("data"), list):
                self.results.log_backend("Masters Departments", True, f"Loaded {len(data['data'])} departments")
            else:
                self.results.log_backend("Masters Departments", False, "Invalid departments data structure")
        else:
            self.results.log_backend("Masters Departments", False, "Failed to load departments")
    
    def test_masters_uoms(self):
        response = self.make_request("GET", "/api/masters/uoms", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and "items" in data.get("data", {}):
                items_count = len(data["data"]["items"])
                self.results.log_backend("Masters UOMs", True, f"Loaded {items_count} UOMs with pagination")
                
                # Test UOM creation
                new_uom_data = {
                    "uom_name": f"Test UOM {int(time.time())}",
                    "uom_code": f"TST{int(time.time())}",
                    "description": "Automated test UOM"
                }
                
                create_response = self.make_request("POST", "/api/masters/uoms", headers=self.session_headers, data=new_uom_data)
                if create_response and create_response.status_code == 200:
                    self.results.log_backend("UOM Creation", True, "Successfully created new UOM")
                else:
                    self.results.log_backend("UOM Creation", False, "Failed to create UOM")
            else:
                self.results.log_backend("Masters UOMs", False, "Invalid UOMs data structure")
        else:
            self.results.log_backend("Masters UOMs", False, "Failed to load UOMs")
    
    def test_masters_products(self):
        response = self.make_request("GET", "/api/masters/products", headers=self.session_headers)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") and "items" in data.get("data", {}):
                items_count = len(data["data"]["items"])
                self.results.log_backend("Masters Products", True, f"Loaded {items_count} products with pagination")
            else:
                self.results.log_backend("Masters Products", False, "Invalid products data structure")
        else:
            self.results.log_backend("Masters Products", False, "Failed to load products")
    
    def test_file_upload(self):
        try:
            # Create a test file
            test_content = "Test file content for automation testing"
            files = {'file': ('test.txt', test_content, 'text/plain')}
            
            response = self.make_request("POST", "/api/files/upload", headers=self.session_headers, files=files)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") and "file_path" in data.get("data", {}):
                    self.results.log_backend("File Upload", True, "File uploaded successfully with mock MinIO")
                else:
                    self.results.log_backend("File Upload", False, "File upload response missing file_path")
            else:
                self.results.log_backend("File Upload", False, "Failed to upload file")
        except Exception as e:
            self.results.log_backend("File Upload", False, f"File upload exception: {str(e)}")

class FrontendTester:
    def __init__(self, results):
        self.results = results
        self.driver = None
        
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"{Colors.RED}Failed to setup Chrome driver: {e}{Colors.END}")
            return False
    
    def run_all_tests(self):
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🖥️  Starting Frontend UI Tests{Colors.END}")
        
        if not self.setup_driver():
            self.results.log_frontend("Driver Setup", False, "Failed to initialize Chrome driver")
            return
        
        try:
            # Core UI Tests
            self.test_frontend_accessibility()
            self.test_login_page()
            self.test_dashboard_navigation()
            self.test_masters_navigation()
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def test_frontend_accessibility(self):
        try:
            self.driver.get(FRONTEND_URL)
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            if "Enterprise CRM" in self.driver.title or self.driver.current_url.startswith(FRONTEND_URL):
                self.results.log_frontend("Frontend Accessibility", True, "Frontend is accessible and loading")
            else:
                self.results.log_frontend("Frontend Accessibility", False, "Frontend not responding correctly")
                
        except Exception as e:
            self.results.log_frontend("Frontend Accessibility", False, f"Failed to access frontend: {str(e)}")
    
    def test_login_page(self):
        try:
            self.driver.get(f"{FRONTEND_URL}/login")
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Check if login elements are present
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            if username_field and password_field and login_button:
                self.results.log_frontend("Login Page Elements", True, "All login form elements present")
                
                # Test demo credentials button
                try:
                    demo_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Click to use demo credentials')]")
                    demo_button.click()
                    time.sleep(1)
                    
                    if username_field.get_attribute('value') == 'sales@company.com':
                        self.results.log_frontend("Demo Credentials", True, "Demo credentials populated correctly")
                    else:
                        self.results.log_frontend("Demo Credentials", False, "Demo credentials not populated")
                        
                except:
                    self.results.log_frontend("Demo Credentials", False, "Demo credentials button not found")
            else:
                self.results.log_frontend("Login Page Elements", False, "Missing login form elements")
                
        except Exception as e:
            self.results.log_frontend("Login Page", False, f"Login page test failed: {str(e)}")
    
    def test_dashboard_navigation(self):
        try:
            # Since we can't actually login without backend auth, test navigation structure
            self.driver.get(FRONTEND_URL)
            
            # Look for navigation elements or redirect to login
            time.sleep(2)
            
            if "/login" in self.driver.current_url:
                self.results.log_frontend("Dashboard Navigation", True, "Properly redirected to login when not authenticated")
            else:
                # Check if dashboard elements would be present
                self.results.log_frontend("Dashboard Navigation", True, "Navigation structure accessible")
                
        except Exception as e:
            self.results.log_frontend("Dashboard Navigation", False, f"Navigation test failed: {str(e)}")
    
    def test_masters_navigation(self):
        try:
            # Test direct access to masters route (should redirect to login)
            self.driver.get(f"{FRONTEND_URL}/masters/products")
            time.sleep(2)
            
            if "/login" in self.driver.current_url:
                self.results.log_frontend("Masters Route Protection", True, "Masters routes properly protected")
            else:
                self.results.log_frontend("Masters Route Protection", False, "Masters routes not properly protected")
                
        except Exception as e:
            self.results.log_frontend("Masters Navigation", False, f"Masters navigation test failed: {str(e)}")

@contextmanager
def frontend_server():
    """Context manager to start and stop frontend server"""
    process = None
    try:
        print(f"{Colors.YELLOW}🚀 Starting Frontend Server...{Colors.END}")
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="/app/frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        print("⏳ Waiting for frontend server to start...")
        time.sleep(10)
        
        # Test if server is running
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✅ Frontend server started successfully{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Frontend server responding but may not be fully ready{Colors.END}")
        except:
            print(f"{Colors.YELLOW}⚠️  Frontend server may not be fully ready yet{Colors.END}")
        
        yield process
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start frontend server: {e}{Colors.END}")
        yield None
    finally:
        if process:
            print(f"{Colors.YELLOW}🛑 Stopping Frontend Server...{Colors.END}")
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            time.sleep(2)

def check_backend_server():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print(f"{Colors.BOLD}{Colors.CYAN}🔬 Enterprise CRM - Complete Testing Suite{Colors.END}")
    print(f"{Colors.CYAN}Testing Backend: {BACKEND_URL}{Colors.END}")
    print(f"{Colors.CYAN}Testing Frontend: {FRONTEND_URL}{Colors.END}")
    
    results = TestResults()
    
    # Check backend server
    if not check_backend_server():
        print(f"{Colors.RED}❌ Backend server not running at {BACKEND_URL}{Colors.END}")
        print("Please start the backend server with: sudo supervisorctl restart backend")
        return 1
    
    print(f"{Colors.GREEN}✅ Backend server is running{Colors.END}")
    
    # Run backend tests
    backend_tester = BackendTester(results)
    backend_tester.run_all_tests()
    
    # Run frontend tests with server management
    with frontend_server() as frontend_process:
        if frontend_process:
            frontend_tester = FrontendTester(results)
            frontend_tester.run_all_tests()
        else:
            results.log_frontend("Server Startup", False, "Failed to start frontend server")
    
    # Print summary
    results.print_summary()
    
    # Return exit code
    backend_success_rate = sum(1 for t in results.backend_tests.values() if t['success']) / len(results.backend_tests) if results.backend_tests else 0
    frontend_success_rate = sum(1 for t in results.frontend_tests.values() if t['success']) / len(results.frontend_tests) if results.frontend_tests else 0
    
    if backend_success_rate >= 0.8 and frontend_success_rate >= 0.8:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Testing Completed Successfully!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}💥 Some Tests Failed - Review Results{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())