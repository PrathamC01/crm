"""
Validation utilities for Indian GST, PAN, etc.
"""
import re
from typing import Optional

def validate_gst_number(gst: str) -> bool:
    """
    Validate Indian GST number format
    Format: 15 digits - 2 digits (state code) + 10 digits (PAN) + 3 digits (additional)
    Example: 22AAAAA0000A1Z5
    """
    if not gst:
        return True  # GST is optional
    
    # Remove spaces and convert to uppercase
    gst = gst.replace(" ", "").upper()
    
    # GST pattern: 2 digits + 10 alphanumeric (PAN format) + 1 digit + 1 letter + 1 alphanumeric
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    
    return bool(re.match(gst_pattern, gst))

def validate_pan_number(pan: str) -> bool:
    """
    Validate Indian PAN number format
    Format: 5 letters + 4 digits + 1 letter
    Example: AAAAA0000A
    """
    if not pan:
        return True  # PAN is optional
    
    # Remove spaces and convert to uppercase
    pan = pan.replace(" ", "").upper()
    
    # PAN pattern: 5 letters + 4 digits + 1 letter
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    return bool(re.match(pan_pattern, pan))

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number (Indian format)
    Accepts various formats: +91-9876543210, 9876543210, +919876543210
    """
    if not phone:
        return True  # Phone is optional
    
    # Remove spaces, dashes, parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Indian phone number patterns
    patterns = [
        r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digits starting with 6-9
        r'^91[6-9]\d{9}$',    # 91 followed by 10 digits starting with 6-9
        r'^[6-9]\d{9}$',      # 10 digits starting with 6-9
    ]
    
    return any(bool(re.match(pattern, phone)) for pattern in patterns)

def validate_email(email: str) -> bool:
    """
    Validate email address format
    """
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_postal_code(postal_code: str, country: str = "India") -> bool:
    """
    Validate postal code based on country
    """
    if not postal_code:
        return True  # Postal code is optional
    
    if country.lower() == "india":
        # Indian PIN code: 6 digits
        return bool(re.match(r'^\d{6}$', postal_code))
    
    # Add other country validations as needed
    return len(postal_code.strip()) > 0

def sanitize_gst_number(gst: Optional[str]) -> Optional[str]:
    """
    Sanitize GST number by removing spaces and converting to uppercase
    """
    if not gst:
        return None
    return gst.replace(" ", "").upper()

def sanitize_pan_number(pan: Optional[str]) -> Optional[str]:
    """
    Sanitize PAN number by removing spaces and converting to uppercase
    """
    if not pan:
        return None
    return pan.replace(" ", "").upper()

def sanitize_phone_number(phone: Optional[str]) -> Optional[str]:
    """
    Sanitize phone number by removing extra characters
    """
    if not phone:
        return None
    
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # If starts with +91 or 91, keep as is, otherwise add +91 if it's a 10-digit number
    if cleaned.startswith('+91'):
        return cleaned
    elif cleaned.startswith('91') and len(cleaned) == 12:
        return '+' + cleaned
    elif len(cleaned) == 10 and cleaned[0] in '6789':
        return '+91' + cleaned
    
    return cleaned

def validate_amount_with_justification(amount: Optional[float], justification: Optional[str]) -> tuple[bool, str]:
    """
    Validate amount and justification business rule
    """
    if amount is None:
        return True, ""
    
    # Amount >= ₹10,00,000 (10 lakhs) needs justification
    if amount >= 1000000:
        if not justification or len(justification.strip()) < 10:
            return False, "Amount ≥ ₹10,00,000 requires detailed justification (minimum 10 characters)"
    
    return True, ""

def validate_opportunity_stage_transition(current_stage: str, new_stage: str) -> tuple[bool, str]:
    """
    Validate stage transition for opportunities
    """
    stages = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    
    if current_stage not in stages or new_stage not in stages:
        return False, "Invalid stage"
    
    current_index = stages.index(current_stage)
    new_index = stages.index(new_stage)
    
    # Allow progression forward or staying in same stage, but not backward beyond 1 stage
    if new_index < current_index - 1:
        return False, f"Cannot move from {current_stage} to {new_stage}. Backward movement limited to 1 stage."
    
    return True, ""