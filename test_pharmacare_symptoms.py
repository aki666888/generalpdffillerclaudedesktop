#!/usr/bin/env python3
"""
Test script to verify symptoms field is working correctly
"""

import sys
import os

# Add the pharmacare-form directory to path
sys.path.insert(0, r"C:\mcp-servers\pharmacare-form")

from enhanced_pdf_filler_v2 import EnhancedPDFFillerV2

def test_symptoms_field():
    """Test if symptoms field is being filled correctly"""
    
    # Initialize the filler
    filler = EnhancedPDFFillerV2()
    
    # Test data with clear symptoms
    test_data = {
        "patient_name": "TEST, SYMPTOMS",
        "phn": "9999999999",
        "phone": "(250) 555-TEST",
        "condition_numbers": [16],  # Tinea pedis
        "symptoms": "TEST SYMPTOMS: This text should appear in the Patient Symptoms and Signs field. If you can read this, the symptoms field is working correctly. This is a longer text to test wrapping.",
        "diagnosis": "Test diagnosis for symptoms field",
        "medication": "Test medication - Check if symptoms appear above",
        "date": "2024-01-15"
    }
    
    print("Testing symptoms field with the following data:")
    print(f"Symptoms: {test_data['symptoms']}")
    print(f"Length: {len(test_data['symptoms'])} characters")
    
    # Fill the PDF
    result = filler.fill_pdf(test_data)
    
    if result["success"]:
        print(f"\nSuccess! PDF saved to: {result['pdf_path']}")
        print("\nPlease check the PDF and verify:")
        print("1. The symptoms text appears in the 'Patient Symptoms and Signs' field")
        print("2. The text is properly formatted and readable")
        print("3. Condition box 16 (Tinea pedis) is checked")
    else:
        print(f"\nError: {result['error']}")

if __name__ == "__main__":
    test_symptoms_field()