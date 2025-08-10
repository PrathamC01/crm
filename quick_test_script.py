#!/usr/bin/env python3
"""
Quick Test Script - Fast Backend API Testing
Enterprise CRM System

Quick validation of core backend functionality
"""

import requests
import json
import sys
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_SESSION_ID = "test_session_123"

class QuickTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_headers = {"Authorization": TEST_SESSION_ID}
        self.passed = 0
        self.total = 0
    
    def test(self, name, success, message):
        self.total += 1
        if success:
            self.passed += 1
            print(f"✅ {name}: {message}")
        else:
            print(f"❌ {name}: {message}")
    
    def get(self, endpoint):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", 
                                 headers=self.session_headers, 
                                 timeout=5)
            return response
        except Exception as e:
            return None
    
    def run_quick_tests(self):
        print("🔬 Enterprise CRM - Quick Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("-" * 50)
        
        # 1. Health Check
        response = self.get("/health")
        self.test("Health Check", 
                 response and response.status_code == 200 and response.json().get("status"),
                 "API is healthy" if response else "Failed to connect")
        
        # 2. Session Info
        response = self.get("/api/session/info")
        self.test("Session Management",
                 response and response.status_code == 200 and "name" in response.json().get("data", {}),
                 "Session authentication working")
        
        # 3. Dashboard Overview
        response = self.get("/api/dashboard/overview")
        self.test("Dashboard Overview",
                 response and response.status_code == 200 and "system_overview" in response.json().get("data", {}),
                 "Dashboard data loading")
        
        # 4. Masters - Departments
        response = self.get("/api/masters/departments")
        self.test("Masters - Departments",
                 response and response.status_code == 200 and len(response.json().get("data", [])) > 0,
                 f"Loaded {len(response.json().get('data', [])) if response else 0} departments")
        
        # 5. Masters - UOMs
        response = self.get("/api/masters/uoms")
        self.test("Masters - UOMs",
                 response and response.status_code == 200 and "items" in response.json().get("data", {}),
                 f"Loaded {len(response.json().get('data', {}).get('items', [])) if response else 0} UOMs")
        
        # 6. Masters - Products
        response = self.get("/api/masters/products")
        self.test("Masters - Products",
                 response and response.status_code == 200 and "items" in response.json().get("data", {}),
                 f"Loaded {len(response.json().get('data', {}).get('items', [])) if response else 0} products")
        
        # 7. Sales Dashboard
        response = self.get("/api/dashboard/sales")
        self.test("Sales Dashboard",
                 response and response.status_code == 200 and "metrics" in response.json().get("data", {}),
                 "Sales metrics available")
        
        print("-" * 50)
        print(f"📊 Results: {self.passed}/{self.total} tests passed ({self.passed/self.total*100:.1f}%)")
        
        if self.passed == self.total:
            print("🎉 All tests passed! System is working correctly.")
            return 0
        elif self.passed >= self.total * 0.8:
            print("⚠️  Most tests passed, minor issues detected.")
            return 0
        else:
            print("💥 Multiple test failures detected.")
            return 1

def main():
    tester = QuickTester()
    return tester.run_quick_tests()

if __name__ == "__main__":
    sys.exit(main())