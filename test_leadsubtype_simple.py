#!/usr/bin/env python3
"""
Simplified test for leadSubType and tenderDetails functionality
"""

import requests
import json
from datetime import date

BACKEND_URL = "https://codebase-cleanup-7.preview.emergentagent.com"

def authenticate():
    """Get JWT token"""
    auth_response = requests.post(f'{BACKEND_URL}/api/login', json={
        'email_or_username': 'sales@company.com', 
        'password': 'sales123'
    })
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        if auth_data.get('status') and auth_data.get('data', {}).get('token'):
            token = auth_data['data']['token']
            return {'Authorization': f'Bearer {token}'}
    return None

def test_lead_creation():
    """Test creating leads with leadSubType and tenderDetails"""
    headers = authenticate()
    if not headers:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test 1: Create lead with TENDER type and tenderDetails
    tender_lead_data = {
        "project_title": "Government E-Platform Tender",
        "lead_source": "Direct Marketing",
        "leadSubType": "TENDER",  # Frontend format
        "tender_sub_type": "Open Tender",
        "products_services": ["Platform Development", "Cloud Services"],
        "company_id": 1,  # Use any ID for testing transformation
        "end_customer_id": 1,
        "tenderDetails": {  # Frontend format  
            "tenderId": "GOV/2024/EPL-001",
            "authority": "National Informatics Centre",
            "bidDueDate": "2025-02-15"
        },
        "expected_revenue": 5000000.00,
        "convert_to_opportunity_date": "2025-02-20",
        "contacts": [
            {
                "first_name": "John",
                "last_name": "Doe", 
                "email": "john@gov.in",
                "primary_phone": "9876543210",
                "decision_maker": True
            }
        ]
    }
    
    print("\n=== Testing TENDER Lead Creation ===")
    response = requests.post(f'{BACKEND_URL}/api/leads/', json=tender_lead_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status'):
            lead_id = result.get('data', {}).get('id')
            print(f"✅ TENDER Lead created successfully: ID {lead_id}")
            
            # Test getting the lead back and verify format transformation
            print("\n=== Testing Lead Retrieval Format ===")
            get_response = requests.get(f'{BACKEND_URL}/api/leads/{lead_id}', headers=headers)
            if get_response.status_code == 200:
                lead_data = get_response.json()
                if lead_data.get('status'):
                    lead = lead_data.get('data', {})
                    print(f"✅ Lead retrieved successfully")
                    print(f"   leadSubType: {lead.get('leadSubType')}")
                    print(f"   lead_sub_type: {lead.get('lead_sub_type')}")
                    print(f"   tenderDetails: {lead.get('tenderDetails')}")
                    
                    # Verify both formats are present
                    if lead.get('leadSubType') and lead.get('tenderDetails'):
                        print("✅ Frontend format (leadSubType, tenderDetails) present")
                    else:
                        print("❌ Frontend format missing")
                        
                    if lead.get('lead_sub_type'):
                        print("✅ Backend format (lead_sub_type) present")  
                    else:
                        print("❌ Backend format missing")
                else:
                    print("❌ Get lead failed:", lead_data)
            else:
                print(f"❌ Get lead request failed: {get_response.status_code}")
                print(get_response.text)
                
        else:
            print("❌ Lead creation failed:", result)
    else:
        print("❌ Request failed:", response.text)
    
    # Test 2: Create lead with NON_TENDER (tenderDetails should be optional)
    print("\n=== Testing NON_TENDER Lead Creation ===")
    non_tender_lead_data = {
        "project_title": "Corporate Software Development",
        "lead_source": "Referral", 
        "leadSubType": "NON_TENDER",  # Frontend format
        "tender_sub_type": "Open Tender",
        "products_services": ["Custom Software"],
        "company_id": 1,
        "end_customer_id": 1,
        # No tenderDetails for NON_TENDER
        "expected_revenue": 2000000.00,
        "convert_to_opportunity_date": "2025-03-01",
        "contacts": [
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@corp.com", 
                "primary_phone": "9876543211",
                "decision_maker": False
            }
        ]
    }
    
    response = requests.post(f'{BACKEND_URL}/api/leads/', json=non_tender_lead_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status'):
            print(f"✅ NON_TENDER Lead created successfully: ID {result.get('data', {}).get('id')}")
        else:
            print("❌ NON_TENDER Lead creation failed:", result)
    else:
        print("❌ NON_TENDER Request failed:", response.text)
        
    # Test 3: Validation - TENDER lead without tenderDetails (should fail)
    print("\n=== Testing Validation: TENDER without tenderDetails ===")
    invalid_lead_data = {
        "project_title": "Invalid Tender Lead",
        "lead_source": "Direct Marketing",
        "leadSubType": "TENDER",  # Requires tenderDetails
        "tender_sub_type": "Open Tender", 
        "products_services": ["Platform"],
        "company_id": 1,
        "end_customer_id": 1,
        # Missing tenderDetails - should cause validation error
        "expected_revenue": 1000000.00,
        "convert_to_opportunity_date": "2025-03-01",
        "contacts": [
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@test.com",
                "primary_phone": "9876543212", 
                "decision_maker": True
            }
        ]
    }
    
    response = requests.post(f'{BACKEND_URL}/api/leads/', json=invalid_lead_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400 or response.status_code == 422:
        print("✅ Validation working: TENDER lead without tenderDetails rejected")
    elif response.status_code == 200:
        print("❌ Validation not working: TENDER lead without tenderDetails was accepted")
    else:
        print(f"❌ Unexpected response: {response.text}")

if __name__ == "__main__":
    print("🚀 Testing leadSubType and tenderDetails Functionality")
    test_lead_creation()
    print("🏁 Test completed")