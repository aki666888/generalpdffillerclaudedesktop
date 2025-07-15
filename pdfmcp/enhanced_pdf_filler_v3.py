#!/usr/bin/env python3
"""
Enhanced PDF Filler V3 - Uses new folder structure
- Reads blank PDFs and mappings from "blanks and json" folder
- Saves filled PDFs to targetid folders with timestamps
- Supports targetid-based automation
"""

import os
import json
import fitz  # PyMuPDF
from datetime import datetime
import sys

class EnhancedPDFFillerV3:
    def __init__(self, targetid=None):
        """Initialize with targetid"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.blanks_json_dir = os.path.join(self.script_dir, "blanks and json")
        
        # Ensure blanks and json directory exists
        if not os.path.exists(self.blanks_json_dir):
            os.makedirs(self.blanks_json_dir)
            print(f"Created directory: {self.blanks_json_dir}", file=sys.stderr)
        
        self.targetid = targetid
        self.mapping = None
        self.blank_pdf_path = None
        self.output_dir = None
        
        if targetid:
            self.setup_paths(targetid)
            self.load_mapping()
        
    def setup_paths(self, targetid):
        """Setup paths based on targetid"""
        # Blank PDF path
        self.blank_pdf_path = os.path.join(self.blanks_json_dir, f"{targetid}.pdf")
        
        # Mapping JSON path
        self.mapping_file = os.path.join(self.blanks_json_dir, f"{targetid}.json")
        
        # Output directory
        self.output_dir = os.path.join(self.script_dir, targetid)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}", file=sys.stderr)
        
    def load_mapping(self):
        """Load the field mapping"""
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r') as f:
                self.mapping = json.load(f)
                print(f"Loaded mapping from: {self.mapping_file}", file=sys.stderr)
        else:
            print(f"ERROR: Mapping file not found: {self.mapping_file}", file=sys.stderr)
            print(f"Please ensure {self.targetid}.json exists in 'blanks and json' folder", file=sys.stderr)
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
    
    def check_condition_box(self, doc, box_number, check=True):
        """Check or uncheck a condition box by number"""
        if not self.mapping or 'condition_boxes' not in self.mapping:
            print(f"Warning: No condition boxes defined in mapping", file=sys.stderr)
            return
        
        # Find the box with the given number
        for box in self.mapping['condition_boxes']:
            if box['number'] == box_number:
                page_num = box['page']
                page = doc[page_num]
                
                # Draw an X or checkmark in the box
                x1, y1 = box['x1'], box['y1']
                x2, y2 = box['x2'], box['y2']
                
                if check:
                    # Draw an X
                    shape = page.new_shape()
                    shape.draw_line(fitz.Point(x1, y1), fitz.Point(x2, y2))
                    shape.draw_line(fitz.Point(x2, y1), fitz.Point(x1, y2))
                    shape.finish(color=(0, 0, 0), width=2)
                    shape.commit()
                    print(f"Checked condition box #{box_number}", file=sys.stderr)
                
                return
        
        print(f"Warning: Condition box #{box_number} not found", file=sys.stderr)
    
    def fill_field(self, doc, field_name, value):
        """Fill a specific field with a value"""
        if not self.mapping or 'fields' not in self.mapping:
            print(f"Warning: No fields defined in mapping", file=sys.stderr)
            return
        
        if field_name not in self.mapping['fields']:
            print(f"Warning: Field '{field_name}' not found in mapping", file=sys.stderr)
            return
        
        font_size = self.mapping.get('font_size', 10)
        
        for field in self.mapping['fields'][field_name]:
            page_num = field['page']
            page = doc[page_num]
            
            # Calculate text position (center of field box)
            x = (field['x1'] + field['x2']) / 2
            y = (field['y1'] + field['y2']) / 2
            
            # Handle checkbox fields
            if field_name.startswith('checkbox_'):
                if str(value).lower() in ['true', 'yes', '1', 'x']:
                    # Draw an X for checkbox
                    shape = page.new_shape()
                    shape.draw_line(
                        fitz.Point(field['x1'], field['y1']), 
                        fitz.Point(field['x2'], field['y2'])
                    )
                    shape.draw_line(
                        fitz.Point(field['x2'], field['y1']), 
                        fitz.Point(field['x1'], field['y2'])
                    )
                    shape.finish(color=(0, 0, 0), width=2)
                    shape.commit()
                    print(f"Checked: {field_name}", file=sys.stderr)
            else:
                # Insert text
                text_rect = fitz.Rect(field['x1'], field['y1'], field['x2'], field['y2'])
                page.insert_textbox(
                    text_rect,
                    str(value),
                    fontsize=font_size,
                    fontname="helv",
                    color=(0, 0, 0),
                    align=1  # Center alignment
                )
                print(f"Filled {field_name}: {value}", file=sys.stderr)
    
    def fill_pdf(self, form_data, output_filename=None):
        """Fill the PDF with provided data"""
        if not self.blank_pdf_path or not os.path.exists(self.blank_pdf_path):
            print(f"ERROR: Blank PDF not found: {self.blank_pdf_path}", file=sys.stderr)
            print(f"Please ensure {self.targetid}.pdf exists in 'blanks and json' folder", file=sys.stderr)
            raise FileNotFoundError(f"Blank PDF not found: {self.blank_pdf_path}")
        
        # Open the blank PDF
        doc = fitz.open(self.blank_pdf_path)
        
        try:
            # Fill regular fields
            for field_name, value in form_data.items():
                if field_name.startswith('condition_'):
                    # Handle condition boxes (e.g., "condition_1": true)
                    try:
                        box_number = int(field_name.split('_')[1])
                        if value:
                            self.check_condition_box(doc, box_number)
                    except (ValueError, IndexError):
                        print(f"Warning: Invalid condition box format: {field_name}", file=sys.stderr)
                else:
                    # Regular field
                    self.fill_field(doc, field_name, value)
            
            # Generate output filename with timestamp
            if not output_filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_filename = f"{self.targetid}_{timestamp}.pdf"
            
            # Full output path
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save the filled PDF
            doc.save(output_path)
            print(f"Saved filled PDF: {output_path}", file=sys.stderr)
            
            return output_path
            
        finally:
            doc.close()
    
    def get_available_fields(self):
        """Return list of available fields and condition boxes"""
        if not self.mapping:
            return {"fields": [], "condition_boxes": []}
        
        fields = list(self.mapping.get('fields', {}).keys())
        condition_boxes = [f"condition_{box['number']}" for box in self.mapping.get('condition_boxes', [])]
        
        return {
            "fields": fields,
            "condition_boxes": condition_boxes,
            "targetid": self.targetid,
            "blank_pdf": self.blank_pdf_path,
            "output_dir": self.output_dir
        }

def main():
    """Example usage and testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fill PDF forms using targetid')
    parser.add_argument('targetid', help='Target ID (PDF name without extension)')
    parser.add_argument('--list-fields', action='store_true', help='List available fields')
    parser.add_argument('--test', action='store_true', help='Run test fill')
    
    args = parser.parse_args()
    
    try:
        # Initialize filler with targetid
        filler = EnhancedPDFFillerV3(targetid=args.targetid)
        
        if args.list_fields:
            # List available fields
            info = filler.get_available_fields()
            print(f"\nTarget ID: {info['targetid']}")
            print(f"Blank PDF: {info['blank_pdf']}")
            print(f"Output Directory: {info['output_dir']}")
            print(f"\nAvailable fields:")
            for field in info['fields']:
                print(f"  - {field}")
            print(f"\nCondition boxes:")
            for box in info['condition_boxes']:
                print(f"  - {box}")
        
        elif args.test:
            # Test fill with sample data
            test_data = {
                'last_name': 'DOE',
                'first_name': 'JOHN',
                'date_of_birth': '01/01/1970',
                'health_number': '1234567890',
                'address_line1': '123 Test Street',
                'city': 'Vancouver',
                'postal_code': 'V1A 1A1',
                'phone_number': '604-555-1234',
                'condition_1': True,  # Check condition box 1
                'condition_3': True,  # Check condition box 3
                'checkbox_yes': True
            }
            
            output_path = filler.fill_pdf(test_data)
            print(f"\nTest PDF created: {output_path}")
        
        else:
            print(f"Filler ready for targetid: {args.targetid}")
            print("Use --list-fields to see available fields")
            print("Use --test to create a test filled PDF")
            
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()