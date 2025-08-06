"""
Utility functions for Product Management
"""
import random
import string
import re
from typing import Optional


def generate_abbreviation(name: str, existing_abbreviations: list = None) -> str:
    """
    Generate 2-digit abbreviation from name
    
    Args:
        name: Name to create abbreviation from
        existing_abbreviations: List of existing abbreviations to avoid duplicates
    
    Returns:
        2-character abbreviation
    """
    if existing_abbreviations is None:
        existing_abbreviations = []
    
    # Clean the name - remove special characters and spaces
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.upper())
    
    # Strategy 1: First two characters
    if len(clean_name) >= 2:
        abbrev = clean_name[:2]
        if abbrev not in existing_abbreviations:
            return abbrev
    
    # Strategy 2: First letter of each word
    words = clean_name.split()
    if len(words) >= 2:
        abbrev = words[0][0] + words[1][0]
        if abbrev not in existing_abbreviations:
            return abbrev
    
    # Strategy 3: First and last character
    if len(clean_name) >= 2:
        abbrev = clean_name[0] + clean_name[-1]
        if abbrev not in existing_abbreviations:
            return abbrev
    
    # Strategy 4: First character + random number
    base_char = clean_name[0] if clean_name else 'A'
    for i in range(0, 10):
        abbrev = base_char + str(i)
        if abbrev not in existing_abbreviations:
            return abbrev
    
    # Strategy 5: Random two characters/numbers (fallback)
    for _ in range(10):
        abbrev = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        if abbrev not in existing_abbreviations:
            return abbrev
    
    # Final fallback
    return random.choices(string.ascii_uppercase, k=2)[0] + random.choices(string.digits, k=1)[0]


def generate_sku_code(product_type_abbrev: str = "PR", 
                     category_abbrev: str = "CA", 
                     sub_category_abbrev: str = "SC",
                     oem_abbrev: str = "OE",
                     config_abbrev: str = "CF",
                     existing_skus: list = None) -> str:
    """
    Generate 16-character alphanumeric SKU code
    
    Format: [TYPE][CATEGORY][SUB][OEM][CONFIG][RANDOM]
    Example: PRSCFWMSCF123ABC
    
    Args:
        product_type_abbrev: Product type abbreviation (2 chars)
        category_abbrev: Category abbreviation (2 chars)  
        sub_category_abbrev: Sub category abbreviation (2 chars)
        oem_abbrev: OEM abbreviation (2 chars)
        config_abbrev: Configuration abbreviation (2 chars)
        existing_skus: List of existing SKUs to avoid duplicates
    
    Returns:
        16-character SKU code
    """
    if existing_skus is None:
        existing_skus = []
    
    # Ensure all abbreviations are 2 characters
    product_type_abbrev = (product_type_abbrev or "PR")[:2].ljust(2, '0')
    category_abbrev = (category_abbrev or "CA")[:2].ljust(2, '0') 
    sub_category_abbrev = (sub_category_abbrev or "SC")[:2].ljust(2, '0')
    oem_abbrev = (oem_abbrev or "OE")[:2].ljust(2, '0')
    config_abbrev = (config_abbrev or "CF")[:2].ljust(2, '0')
    
    # Base: 10 characters from abbreviations
    base_sku = product_type_abbrev + category_abbrev + sub_category_abbrev + oem_abbrev + config_abbrev
    
    # Add 6 random characters to make it 16 characters total
    for attempt in range(100):  # Max 100 attempts to avoid infinite loop
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        sku_code = base_sku + random_suffix
        
        if sku_code not in existing_skus:
            return sku_code
    
    # Fallback: timestamp-based suffix
    import time
    timestamp_suffix = str(int(time.time()))[-6:]
    return base_sku + timestamp_suffix


def validate_sku_format(sku_code: str) -> bool:
    """
    Validate SKU code format
    
    Args:
        sku_code: SKU code to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not sku_code or len(sku_code) != 16:
        return False
    
    # Should be alphanumeric
    return sku_code.isalnum() and sku_code.isupper()


def parse_sku_components(sku_code: str) -> dict:
    """
    Parse SKU code into components
    
    Args:
        sku_code: 16-character SKU code
    
    Returns:
        Dictionary with SKU components
    """
    if not validate_sku_format(sku_code):
        return {}
    
    return {
        'product_type': sku_code[0:2],
        'category': sku_code[2:4], 
        'sub_category': sku_code[4:6],
        'oem': sku_code[6:8],
        'configuration': sku_code[8:10],
        'random_suffix': sku_code[10:16]
    }