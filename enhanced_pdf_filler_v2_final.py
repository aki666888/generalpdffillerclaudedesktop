#!/usr/bin/env python3
"""
Enhanced PDF Filler V2 - Better Text Wrapping
Fixes text running off page with proper wrapping and smaller font
"""

import os
import json
import fitz  # PyMuPDF
from datetime import datetime
import sys

class EnhancedPDFFillerV2:
    def __init__(self, mapping_file=None):
        """Initialize with mapping file"""
        # Check multiple locations for the mapping file
        if mapping_file:
            self.mapping_file = mapping_file
        else:
            # Updated to use the correct path
            possible_paths = [
                r"C:\mcp-servers\pharmacare-form\macs_form_mapping_v3.json",
                r"C:\forms\macs_form_mapping_v3_updated.json",
                r"C:\forms\macs_form_mapping_v3.json",
                os.path.join(os.path.dirname(__file__), "macs_form_mapping_v3.json")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.mapping_file = path
                    break
            else:
                self.mapping_file = possible_paths[0]  # Default to first option
        
        self.mapping = None
        self.load_mapping()
        
    def load_mapping(self):
        """Load the field mapping"""
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r') as f:
                self.mapping = json.load(f)
                print(f"Loaded mapping from: {self.mapping_file}", file=sys.stderr)
        else:
            # Default mapping if file doesn't exist
            print(f"Mapping file not found at: {self.mapping_file}, using defaults", file=sys.stderr)
            self.mapping = {
                'pdf_file': 'blank.pdf',
                'fields': {},
                'condition_boxes': [],
                'font_size': 10,
                'context': 'PharmaCare MACS form'
            }
    
    def highlight_condition_box(self, page, box_number):
        """Highlight a specific condition box by number"""
        for box in self.mapping.get('condition_boxes', []):
            if box['number'] == box_number:
                # Draw a red checkmark in the box
                check_x = box['x1'] + 5
                check_y = box['y1'] + 20
                
                # First stroke of checkmark
                page.draw_line(
                    fitz.Point(check_x, check_y),
                    fitz.Point(check_x + 15, check_y + 15),
                    color=(1, 0, 0),
                    width=3
                )
                
                # Second stroke of checkmark
                page.draw_line(
                    fitz.Point(check_x + 15, check_y + 15),
                    fitz.Point(check_x + 35, check_y - 20),
                    color=(1, 0, 0),
                    width=3
                )
                
                return True
        return False
    
    def fill_pdf(self, data):
        """Fill PDF with field data and highlighted conditions"""
        try:
            # Debug: Log received data
            print(f"DEBUG: Received data for {data.get('patient_name', 'Unknown')}", file=sys.stderr)
            print(f"DEBUG: Symptoms length: {len(data.get('symptoms', ''))}", file=sys.stderr)
            print(f"DEBUG: Medication length: {len(data.get('medication', ''))}", file=sys.stderr)
            
            # Get PDF path - updated to look in correct location
            pdf_path = os.path.join(os.path.dirname(self.mapping_file), self.mapping['pdf_file'])
            if not os.path.exists(pdf_path):
                # Try alternative locations
                pdf_path = os.path.join(r"C:\mcp-servers\pharmacare-form", self.mapping['pdf_file'])
                if not os.path.exists(pdf_path):
                    pdf_path = r"C:\Users\info0\Downloads\blank.pdf"
            
            print(f"DEBUG: Using PDF from: {pdf_path}", file=sys.stderr)
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Handle condition numbers
            condition_numbers = data.get('condition_numbers', [])
            if isinstance(condition_numbers, int):
                condition_numbers = [condition_numbers]
            elif isinstance(condition_numbers, str):
                # Parse string like "1,3,5" or "1 3 5"
                condition_numbers = [int(x.strip()) for x in condition_numbers.replace(',', ' ').split() if x.strip().isdigit()]
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Highlight condition boxes
                for box_num in condition_numbers:
                    self.highlight_condition_box(page, box_num)
                
                # Fill field boxes
                for field_type, boxes in self.mapping.get('fields', {}).items():
                    # Get value for this field
                    value = self._get_field_value(field_type, data)
                    print(f"DEBUG: Processing field '{field_type}' with value: '{value[:50] if value else 'None'}'...", file=sys.stderr)
                    
                    if value:
                        for box in boxes:
                            if box['page'] == page_num:
                                # Special handling for multi-line fields
                                if field_type == 'symptoms':
                                    # Symptoms field - use smaller font and tighter spacing
                                    # Create a rectangle with small padding
                                    rect = fitz.Rect(
                                        box['x1'] + 2,  # Small left padding
                                        box['y1'] + 2,  # Small top padding
                                        box['x2'] - 2,  # Small right padding
                                        box['y2'] - 2   # Small bottom padding
                                    )
                                    
                                    # Use PyMuPDF's insert_textbox for proper wrapping
                                    # Font size 7 with tight line spacing
                                    rc = page.insert_textbox(
                                        rect,
                                        str(value),
                                        fontsize=7,          # Smaller font size
                                        fontname="helv",     # Helvetica font
                                        color=(0, 0, 0),
                                        align=0,             # Left align
                                        expandtabs=0,        # No tab expansion
                                        charwidthfactor=0.5, # Tighter character spacing
                                        lineheight=0.85      # Tighter line spacing (85% of font size)
                                    )
                                    
                                    # Check if all text fit
                                    if rc < 0:
                                        print(f"WARNING: Not all symptoms text fit in box. Overflow: {-rc} characters", file=sys.stderr)
                                    else:
                                        print(f"DEBUG: Successfully inserted symptoms text", file=sys.stderr)
                                        
                                elif field_type == 'medication':
                                    # Medication field - also use smaller font
                                    rect = fitz.Rect(
                                        box['x1'] + 2,
                                        box['y1'] + 2,
                                        box['x2'] - 2,
                                        box['y2'] - 2
                                    )
                                    
                                    rc = page.insert_textbox(
                                        rect,
                                        str(value),
                                        fontsize=7,          # Smaller font
                                        fontname="helv",
                                        color=(0, 0, 0),
                                        align=0,
                                        expandtabs=0,
                                        lineheight=0.9       # 90% line height
                                    )
                                    
                                    if rc < 0:
                                        print(f"WARNING: Medication text overflow: {-rc} characters", file=sys.stderr)
                                        
                                else:
                                    # Regular field - single line
                                    # Center text vertically
                                    text_y = box['y1'] + (box['y2'] - box['y1']) / 2 + 4
                                    page.insert_text(
                                        (box['x1'] + 5, text_y),
                                        str(value),
                                        fontsize=self.mapping.get('font_size', 10),
                                        color=(0, 0, 0)
                                    )
            
            # Generate output filename
            patient_name = data.get('patient_name', 'Unknown').replace(' ', '_').replace(',', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output directory if needed
            output_dir = r"C:\forms"
            patient_dir = os.path.join(output_dir, patient_name.split('_')[0])
            os.makedirs(patient_dir, exist_ok=True)
            
            # Save PDF
            output_filename = f"MACS_Form_{patient_name}_{timestamp}.pdf"
            output_path = os.path.join(patient_dir, output_filename)
            doc.save(output_path)
            doc.close()
            
            # Also save the data as JSON for reference
            json_filename = f"MACS_Form_{patient_name}_{timestamp}.json"
            json_path = os.path.join(patient_dir, json_filename)
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return {
                "success": True,
                "pdf_path": output_path,
                "json_path": json_path,
                "conditions_highlighted": condition_numbers
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_field_value(self, field_type, data):
        """Get value for a specific field type from data"""
        # Simple direct mapping - no confusion!
        field_mappings = {
            'patient_name': 'patient_name',
            'phn': 'phn',
            'phone': 'phone',
            'symptoms': 'symptoms',  # Simple direct mapping
            'medical_history': 'medical_history',
            'diagnosis': 'diagnosis',
            'medication': 'medication',
            'date': 'date'
        }
        
        # Get the data key for this field type
        data_key = field_mappings.get(field_type, field_type)
        
        # Get the value from data
        if data_key == 'date' and data_key not in data:
            return datetime.now().strftime("%Y-%m-%d")
        
        return data.get(data_key, '')

# Quick function for MCP
def fill_pdf_with_numbers(data):
    """Fill PDF using numbered condition boxes"""
    filler = EnhancedPDFFillerV2()
    result = filler.fill_pdf(data)
    
    if result["success"]:
        conditions = result.get("conditions_highlighted", [])
        conditions_text = f"Conditions {', '.join(map(str, conditions))}" if conditions else "No conditions"
        return f"Form saved successfully!\nPDF: {result['pdf_path']}\n{conditions_text} highlighted"
    else:
        return f"Error: {result['error']}"

if __name__ == "__main__":
    # Test with condition numbers
    test_data = {
        "patient_name": "John Doe",
        "phn": "9876543210",
        "phone": "(250) 555-1234",
        "condition_numbers": [2, 5, 8],  # Claude Desktop specifies box numbers
        "symptoms": "Various symptoms that should wrap properly without running off the page. This is a longer text to test the wrapping functionality.",
        "medical_history": "No known allergies",
        "diagnosis": "Multiple conditions",
        "medication": "As prescribed with detailed instructions that should also wrap properly in the box.",
        "date": "2024-01-14"
    }
    
    result = fill_pdf_with_numbers(test_data)
    print(result)