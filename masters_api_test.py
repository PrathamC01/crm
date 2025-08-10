#!/usr/bin/env python3
"""
Masters API Testing Suite
Tests all Masters API endpoints for the integrated CRM system
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class MastersAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            "uoms": [],
            "products": [],
            "pricelists": []
        }
        
    def log_test(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
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
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
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

    def test_departments_retrieval(self):
        """Test GET /api/masters/departments"""
        try:
            response = self.make_request("GET", "/masters/departments")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    departments = data["data"]
                    if isinstance(departments, list) and len(departments) > 0:
                        self.log_test("Departments Retrieval", True, f"Retrieved {len(departments)} departments")
                        
                        # Verify department structure
                        first_dept = departments[0]
                        required_fields = ["id", "department_name"]
                        if all(field in first_dept for field in required_fields):
                            self.log_test("Departments Structure", True, "Department structure is valid")
                        else:
                            self.log_test("Departments Structure", False, f"Missing required fields in department: {first_dept}")
                        
                        return True
                    else:
                        self.log_test("Departments Retrieval", False, "No departments found or invalid format")
                        return False
                else:
                    self.log_test("Departments Retrieval", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Departments Retrieval", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Departments Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_roles_retrieval(self):
        """Test GET /api/masters/roles"""
        try:
            response = self.make_request("GET", "/masters/roles")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    roles = data["data"]
                    if isinstance(roles, list) and len(roles) > 0:
                        self.log_test("Roles Retrieval", True, f"Retrieved {len(roles)} roles")
                        
                        # Verify role structure
                        first_role = roles[0]
                        required_fields = ["id", "role_name"]
                        if all(field in first_role for field in required_fields):
                            self.log_test("Roles Structure", True, "Role structure is valid")
                        else:
                            self.log_test("Roles Structure", False, f"Missing required fields in role: {first_role}")
                        
                        return True
                    else:
                        self.log_test("Roles Retrieval", False, "No roles found or invalid format")
                        return False
                else:
                    self.log_test("Roles Retrieval", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Roles Retrieval", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Roles Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_uoms_retrieval_with_pagination(self):
        """Test GET /api/masters/uoms with pagination"""
        try:
            # Test without pagination parameters
            response = self.make_request("GET", "/masters/uoms")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    uoms_data = data["data"]
                    
                    # Check if it's paginated response
                    if "items" in uoms_data and "pagination" in uoms_data:
                        uoms = uoms_data["items"]
                        pagination = uoms_data["pagination"]
                        
                        self.log_test("UOMs Retrieval", True, f"Retrieved {len(uoms)} UOMs with pagination")
                        
                        # Verify pagination structure
                        required_pagination_fields = ["total", "page", "per_page", "pages"]
                        if all(field in pagination for field in required_pagination_fields):
                            self.log_test("UOMs Pagination Structure", True, f"Pagination: {pagination}")
                        else:
                            self.log_test("UOMs Pagination Structure", False, f"Missing pagination fields: {pagination}")
                        
                        # Verify UOM structure
                        if uoms and len(uoms) > 0:
                            first_uom = uoms[0]
                            required_fields = ["id", "code", "name"]
                            if all(field in first_uom for field in required_fields):
                                self.log_test("UOMs Structure", True, "UOM structure is valid")
                            else:
                                self.log_test("UOMs Structure", False, f"Missing required fields in UOM: {first_uom}")
                        
                        return True
                    else:
                        self.log_test("UOMs Retrieval", False, f"Invalid UOMs response format: {uoms_data}")
                        return False
                else:
                    self.log_test("UOMs Retrieval", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("UOMs Retrieval", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("UOMs Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_products_retrieval_with_pagination(self):
        """Test GET /api/masters/products with pagination"""
        try:
            response = self.make_request("GET", "/masters/products")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    products_data = data["data"]
                    
                    # Check if it's paginated response
                    if "items" in products_data and "pagination" in products_data:
                        products = products_data["items"]
                        pagination = products_data["pagination"]
                        
                        self.log_test("Products Retrieval", True, f"Retrieved {len(products)} products with pagination")
                        
                        # Verify pagination structure
                        required_pagination_fields = ["total", "page", "per_page", "pages"]
                        if all(field in pagination for field in required_pagination_fields):
                            self.log_test("Products Pagination Structure", True, f"Pagination: {pagination}")
                        else:
                            self.log_test("Products Pagination Structure", False, f"Missing pagination fields: {pagination}")
                        
                        # Verify product structure if products exist
                        if products and len(products) > 0:
                            first_product = products[0]
                            required_fields = ["id", "name", "sku_code"]
                            if all(field in first_product for field in required_fields):
                                self.log_test("Products Structure", True, "Product structure is valid")
                            else:
                                self.log_test("Products Structure", False, f"Missing required fields in product: {first_product}")
                        
                        return True
                    else:
                        self.log_test("Products Retrieval", False, f"Invalid products response format: {products_data}")
                        return False
                else:
                    self.log_test("Products Retrieval", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Products Retrieval", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Products Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_pricelists_retrieval(self):
        """Test GET /api/masters/pricelists"""
        try:
            response = self.make_request("GET", "/masters/pricelists")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    pricelists_data = data["data"]
                    
                    # Check if it's paginated response
                    if "items" in pricelists_data and "pagination" in pricelists_data:
                        pricelists = pricelists_data["items"]
                        pagination = pricelists_data["pagination"]
                        
                        self.log_test("Price Lists Retrieval", True, f"Retrieved {len(pricelists)} price lists with pagination")
                        
                        # Verify pagination structure
                        required_pagination_fields = ["total", "page", "per_page", "pages"]
                        if all(field in pagination for field in required_pagination_fields):
                            self.log_test("Price Lists Pagination Structure", True, f"Pagination: {pagination}")
                        else:
                            self.log_test("Price Lists Pagination Structure", False, f"Missing pagination fields: {pagination}")
                        
                        return True
                    else:
                        self.log_test("Price Lists Retrieval", False, f"Invalid price lists response format: {pricelists_data}")
                        return False
                else:
                    self.log_test("Price Lists Retrieval", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Price Lists Retrieval", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Price Lists Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_create_uom(self):
        """Test POST /api/masters/uoms - Create new UOM with validation"""
        try:
            # Test creating a valid UOM
            uom_data = {
                "code": f"TEST_UOM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "name": "Test Unit of Measure",
                "description": "Test UOM for API testing",
                "is_active": True
            }
            
            response = self.make_request("POST", "/masters/uoms", uom_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    created_uom = data["data"]
                    self.created_resources["uoms"].append(created_uom["id"])
                    
                    # Verify created UOM structure
                    required_fields = ["id", "code", "name"]
                    if all(field in created_uom for field in required_fields):
                        self.log_test("UOM Creation", True, f"UOM created successfully with ID: {created_uom['id']}")
                        
                        # Verify the code matches what we sent
                        if created_uom["code"] == uom_data["code"]:
                            self.log_test("UOM Code Validation", True, "UOM code matches input")
                        else:
                            self.log_test("UOM Code Validation", False, f"UOM code mismatch: expected {uom_data['code']}, got {created_uom['code']}")
                        
                        return True
                    else:
                        self.log_test("UOM Creation", False, f"Missing required fields in created UOM: {created_uom}")
                        return False
                else:
                    self.log_test("UOM Creation", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("UOM Creation", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("UOM Creation", False, f"Exception: {str(e)}")
            return False

    def test_create_duplicate_uom(self):
        """Test duplicate UOM code validation"""
        try:
            # Try to create a UOM with duplicate code
            duplicate_uom_data = {
                "code": "KG",  # This should already exist from seeded data
                "name": "Duplicate Kilogram",
                "description": "This should fail due to duplicate code",
                "is_active": True
            }
            
            response = self.make_request("POST", "/masters/uoms", duplicate_uom_data)
            if response and response.status_code in [400, 422, 409]:
                self.log_test("UOM Duplicate Validation", True, "Duplicate UOM code properly rejected")
                return True
            elif response and response.status_code == 200:
                self.log_test("UOM Duplicate Validation", False, "Duplicate UOM code was accepted (should have been rejected)")
                return False
            else:
                self.log_test("UOM Duplicate Validation", False, f"Unexpected response status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("UOM Duplicate Validation", False, f"Exception: {str(e)}")
            return False

    def test_create_product_with_auto_sku(self):
        """Test POST /api/masters/products - Create product with auto SKU generation"""
        try:
            product_data = {
                "name": f"Test Product {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "cat1_type": "Hardware",
                "cat2_category": "Servers",
                "cat3_sub_category": "Rack Servers",
                "description": "Test product for API testing",
                "is_active": True,
                "uom_ids": [1, 2]  # Assuming these UOM IDs exist from seeded data
            }
            
            response = self.make_request("POST", "/masters/products", product_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    created_product = data["data"]
                    self.created_resources["products"].append(created_product["id"])
                    
                    # Verify created product structure
                    required_fields = ["id", "name", "sku_code"]
                    if all(field in created_product for field in required_fields):
                        self.log_test("Product Creation", True, f"Product created successfully with ID: {created_product['id']}")
                        
                        # Verify auto-generated SKU code
                        sku_code = created_product["sku_code"]
                        if sku_code and len(sku_code) > 0:
                            self.log_test("Product SKU Generation", True, f"Auto-generated SKU: {sku_code}")
                        else:
                            self.log_test("Product SKU Generation", False, "SKU code not generated")
                        
                        # Verify product name auto-generation from categories
                        expected_name_parts = ["Hardware", "Servers", "Rack Servers"]
                        if any(part in created_product["name"] for part in expected_name_parts):
                            self.log_test("Product Name Generation", True, "Product name includes category information")
                        else:
                            self.log_test("Product Name Generation", False, f"Product name doesn't reflect categories: {created_product['name']}")
                        
                        return True
                    else:
                        self.log_test("Product Creation", False, f"Missing required fields in created product: {created_product}")
                        return False
                else:
                    self.log_test("Product Creation", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Product Creation", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Product Creation", False, f"Exception: {str(e)}")
            return False

    def test_create_pricelist(self):
        """Test POST /api/masters/pricelists - Create price list"""
        try:
            pricelist_data = {
                "name": f"Test Price List {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test price list for API testing",
                "currency": "INR",
                "is_active": True,
                "effective_from": "2024-01-01",
                "effective_to": "2024-12-31"
            }
            
            response = self.make_request("POST", "/masters/pricelists", pricelist_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    created_pricelist = data["data"]
                    self.created_resources["pricelists"].append(created_pricelist["id"])
                    
                    # Verify created price list structure
                    required_fields = ["id", "name", "currency"]
                    if all(field in created_pricelist for field in required_fields):
                        self.log_test("Price List Creation", True, f"Price list created successfully with ID: {created_pricelist['id']}")
                        
                        # Verify currency
                        if created_pricelist["currency"] == pricelist_data["currency"]:
                            self.log_test("Price List Currency", True, f"Currency set correctly: {created_pricelist['currency']}")
                        else:
                            self.log_test("Price List Currency", False, f"Currency mismatch: expected {pricelist_data['currency']}, got {created_pricelist['currency']}")
                        
                        return True
                    else:
                        self.log_test("Price List Creation", False, f"Missing required fields in created price list: {created_pricelist}")
                        return False
                else:
                    self.log_test("Price List Creation", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Price List Creation", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Price List Creation", False, f"Exception: {str(e)}")
            return False

    def test_invalid_enum_values(self):
        """Test validation with invalid enum values"""
        try:
            # Test invalid currency in price list
            invalid_pricelist_data = {
                "name": "Invalid Currency Test",
                "description": "Test with invalid currency",
                "currency": "INVALID_CURRENCY",
                "is_active": True,
                "effective_from": "2024-01-01",
                "effective_to": "2024-12-31"
            }
            
            response = self.make_request("POST", "/masters/pricelists", invalid_pricelist_data)
            if response and response.status_code in [400, 422]:
                self.log_test("Invalid Enum Validation", True, "Invalid currency properly rejected")
                return True
            elif response and response.status_code == 200:
                self.log_test("Invalid Enum Validation", False, "Invalid currency was accepted (should have been rejected)")
                return False
            else:
                self.log_test("Invalid Enum Validation", False, f"Unexpected response status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Invalid Enum Validation", False, f"Exception: {str(e)}")
            return False

    def test_required_field_validation(self):
        """Test required field validation"""
        try:
            # Test UOM creation without required fields
            invalid_uom_data = {
                "description": "Missing required fields"
                # Missing code and name
            }
            
            response = self.make_request("POST", "/masters/uoms", invalid_uom_data)
            if response and response.status_code in [400, 422]:
                self.log_test("Required Field Validation", True, "Missing required fields properly rejected")
                return True
            elif response and response.status_code == 200:
                self.log_test("Required Field Validation", False, "Missing required fields were accepted (should have been rejected)")
                return False
            else:
                self.log_test("Required Field Validation", False, f"Unexpected response status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Required Field Validation", False, f"Exception: {str(e)}")
            return False

    def test_pagination_parameters(self):
        """Test pagination parameters"""
        try:
            # Test with specific pagination parameters
            params = {
                "page": 1,
                "per_page": 5
            }
            
            response = self.make_request("GET", "/masters/uoms", params=params)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") == True and "data" in data:
                    uoms_data = data["data"]
                    
                    if "items" in uoms_data and "pagination" in uoms_data:
                        pagination = uoms_data["pagination"]
                        items = uoms_data["items"]
                        
                        # Verify pagination parameters are respected
                        if pagination.get("page") == 1 and pagination.get("per_page") == 5:
                            self.log_test("Pagination Parameters", True, f"Pagination parameters respected: page={pagination['page']}, per_page={pagination['per_page']}")
                        else:
                            self.log_test("Pagination Parameters", False, f"Pagination parameters not respected: {pagination}")
                        
                        # Verify items count doesn't exceed per_page
                        if len(items) <= 5:
                            self.log_test("Pagination Item Count", True, f"Items count ({len(items)}) respects per_page limit")
                        else:
                            self.log_test("Pagination Item Count", False, f"Items count ({len(items)}) exceeds per_page limit (5)")
                        
                        return True
                    else:
                        self.log_test("Pagination Parameters", False, f"Invalid response format: {uoms_data}")
                        return False
                else:
                    self.log_test("Pagination Parameters", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Pagination Parameters", False, f"Request failed with status {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Pagination Parameters", False, f"Exception: {str(e)}")
            return False

    def test_response_format_consistency(self):
        """Test that all responses follow standard format"""
        try:
            endpoints_to_test = [
                "/masters/departments",
                "/masters/roles",
                "/masters/uoms",
                "/masters/products",
                "/masters/pricelists"
            ]
            
            all_consistent = True
            
            for endpoint in endpoints_to_test:
                response = self.make_request("GET", endpoint)
                if response and response.status_code == 200:
                    data = response.json()
                    
                    # Check standard response format
                    required_fields = ["status", "message", "data"]
                    if all(field in data for field in required_fields):
                        self.log_test(f"Response Format - {endpoint}", True, "Standard response format followed")
                    else:
                        self.log_test(f"Response Format - {endpoint}", False, f"Missing standard fields: {data}")
                        all_consistent = False
                else:
                    self.log_test(f"Response Format - {endpoint}", False, f"Request failed: {response.status_code if response else 'No response'}")
                    all_consistent = False
            
            return all_consistent
        except Exception as e:
            self.log_test("Response Format Consistency", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Masters API tests"""
        print("🚀 Starting Masters API Comprehensive Testing")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - cannot proceed")
            return False
        
        # Master data retrieval tests
        self.test_departments_retrieval()
        self.test_roles_retrieval()
        self.test_uoms_retrieval_with_pagination()
        self.test_products_retrieval_with_pagination()
        self.test_pricelists_retrieval()
        
        # Create operations tests
        self.test_create_uom()
        self.test_create_duplicate_uom()
        self.test_create_product_with_auto_sku()
        self.test_create_pricelist()
        
        # Validation tests
        self.test_invalid_enum_values()
        self.test_required_field_validation()
        
        # Pagination tests
        self.test_pagination_parameters()
        
        # Response format tests
        self.test_response_format_consistency()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 Masters API Testing Summary")
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
        
        print(f"\n📊 Created Resources:")
        print(f"  - UOMs: {len(self.created_resources['uoms'])}")
        print(f"  - Products: {len(self.created_resources['products'])}")
        print(f"  - Price Lists: {len(self.created_resources['pricelists'])}")
        
        print("\n" + "=" * 60)
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = MastersAPITester()
    
    try:
        success = tester.run_all_tests()
        overall_success = tester.print_summary()
        
        # Save detailed results
        with open("/app/masters_api_test_results.log", "w") as f:
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