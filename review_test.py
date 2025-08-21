#!/usr/bin/env python3
"""
Review Request Test - TechnoSoft Solutions Company Creation
"""

import requests
import json
from datetime import datetime

class ReviewTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.session_headers = {}

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_login(self):
        """Test login and get session"""
        url = f"{self.base_url}/api/login"
        data = {"email_or_username": "admin", "password": "admin123"}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status'):
                    token = response_data.get('data', {}).get('token')
                    if token:
                        self.token = token
                        self.session_headers = {'Authorization': f'Bearer {token}'}
                        self.log("✅ Login successful")
                        return True
            
            self.log("❌ Login failed")
            return False
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            return False

    def test_create_technosoft_solutions(self):
        """Test creating TechnoSoft Solutions - should be classified as HOT"""
        company_data = {
            "name": "TechnoSoft Solutions",
            "company_type": "DOMESTIC_GST",
            "industry": "IT_ITeS",
            "sub_industry": "Software Development",
            "annual_revenue": 75000000,  # 7.5 crore
            "employee_count": 120,
            "gst_number": "27TECHS1234F1Z5",
            "pan_number": "TECHS1234F",
            "supporting_documents": ["GST_CERTIFICATE_technosoft.pdf", "PAN_CARD_technosoft.pdf"],
            "verification_source": "GST",
            "verification_date": datetime.now().isoformat(),
            "verified_by": "admin",
            "address": "Tech Park IT Corridor Software City Mumbai",
            "country": "India",
            "state": "Maharashtra",
            "city": "Mumbai",
            "pin_code": "400001",
            "parent_child_mapping_confirmed": True,
            "linked_subsidiaries": ["None"],
            "website": "https://technosoft.com",
            "description": "TechnoSoft Solutions - IT company with 120 employees and 7.5 crore revenue"
        }

        url = f"{self.base_url}/api/companies"
        
        try:
            response = requests.post(url, json=company_data, headers=self.session_headers, timeout=10)
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status'):
                    company = response_data.get('data')
                    if company:
                        self.log(f"✅ Company created successfully!")
                        self.log(f"   ID: {company.get('id')}")
                        self.log(f"   Name: {company.get('name')}")
                        self.log(f"   Lead Status: {company.get('lead_status')}")
                        self.log(f"   Validation Score: {company.get('validation_score')}")
                        self.log(f"   Country ID: {company.get('country_id')}")
                        self.log(f"   State ID: {company.get('state_id')}")
                        self.log(f"   City ID: {company.get('city_id')}")
                        
                        # Verify HOT classification
                        if company.get('lead_status') == 'HOT':
                            self.log("✅ PASS: Company correctly classified as HOT")
                        else:
                            self.log(f"❌ FAIL: Expected HOT, got {company.get('lead_status')}")
                        
                        # Verify geographic integration
                        if company.get('country_id') and company.get('state_id') and company.get('city_id'):
                            self.log("✅ PASS: Geographic IDs properly set")
                        else:
                            self.log("❌ FAIL: Geographic IDs missing")
                        
                        # Verify validation score
                        score = company.get('validation_score')
                        if score and score >= 80:
                            self.log(f"✅ PASS: High validation score ({score})")
                        else:
                            self.log(f"❌ FAIL: Low validation score ({score})")
                        
                        return True
                    else:
                        self.log("❌ FAIL: No company data in response")
                else:
                    self.log(f"❌ FAIL: Response status false: {response_data.get('message')}")
            else:
                self.log(f"❌ FAIL: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                except:
                    self.log(f"   Raw response: {response.text}")
            
            return False
            
        except Exception as e:
            self.log(f"❌ Error creating company: {e}")
            return False

    def test_geographic_apis(self):
        """Test geographic APIs"""
        self.log("🌍 Testing Geographic APIs")
        
        # Test countries
        url = f"{self.base_url}/api/companies/masters/countries"
        try:
            response = requests.get(url, headers=self.session_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    countries = data.get('data', [])
                    self.log(f"✅ Countries API: {len(countries)} countries found")
                    india_found = any(c.get('name') == 'India' for c in countries)
                    if india_found:
                        self.log("✅ India found in countries")
                    else:
                        self.log("❌ India not found in countries")
                else:
                    self.log("❌ Countries API failed")
            else:
                self.log(f"❌ Countries API HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ Countries API error: {e}")
        
        # Test states for India
        url = f"{self.base_url}/api/companies/masters/states/IN"
        try:
            response = requests.get(url, headers=self.session_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    states = data.get('data', [])
                    self.log(f"✅ States API: {len(states)} states found for India")
                    maharashtra_found = any(s.get('name') == 'Maharashtra' for s in states)
                    if maharashtra_found:
                        self.log("✅ Maharashtra found in states")
                    else:
                        self.log("❌ Maharashtra not found in states")
                else:
                    self.log("❌ States API failed")
            else:
                self.log(f"❌ States API HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ States API error: {e}")
        
        # Test cities for Maharashtra
        url = f"{self.base_url}/api/companies/masters/cities/IN/Maharashtra"
        try:
            response = requests.get(url, headers=self.session_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    cities_data = data.get('data', {})
                    cities = cities_data.get('cities', [])
                    self.log(f"✅ Cities API: {len(cities)} cities found for Maharashtra")
                    mumbai_found = 'Mumbai' in cities
                    if mumbai_found:
                        self.log("✅ Mumbai found in cities")
                    else:
                        self.log("❌ Mumbai not found in cities")
                else:
                    self.log("❌ Cities API failed")
            else:
                self.log(f"❌ Cities API HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ Cities API error: {e}")

    def run_review_tests(self):
        """Run all review tests"""
        self.log("🚀 Starting Review Request Tests")
        self.log("=" * 60)
        
        # Test 1: Login
        if not self.test_login():
            self.log("❌ Cannot proceed without authentication")
            return
        
        # Test 2: Geographic APIs
        self.test_geographic_apis()
        
        # Test 3: Create TechnoSoft Solutions
        self.log("\n🔥 Testing TechnoSoft Solutions Creation")
        self.log("-" * 50)
        success = self.test_create_technosoft_solutions()
        
        if success:
            self.log("\n🎉 REVIEW TESTS PASSED!")
        else:
            self.log("\n❌ REVIEW TESTS FAILED!")

if __name__ == "__main__":
    tester = ReviewTester()
    tester.run_review_tests()