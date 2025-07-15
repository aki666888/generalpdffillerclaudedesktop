#!/usr/bin/env python3
import fitz
import json
import os
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeneralPDFFiller:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def fill_pdf(self, pdf_template, mapping_file, form_data, conditions_to_highlight, output_filename=None):
        """
        Fill PDF with provided data
        
        Args:
            pdf_template: Path to PDF template
            mapping_file: Path to JSON mapping file
            form_data: Dictionary with field data (keys can be field names or numbers)
            conditions_to_highlight: List of condition numbers to highlight
            output_filename: Optional output filename
        """
        try:
            # Load mapping
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
            
            # Open PDF
            pdf_document = fitz.open(pdf_template)
            
            # Process form data - convert numeric keys to field references
            processed_data = self._process_form_data(form_data, mapping)
            
            # Fill each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Fill regular fields
                self._fill_fields(page, mapping.get('fields', {}), processed_data, page_num)
                
                # Highlight condition boxes
                self._highlight_conditions(page, mapping.get('condition_boxes', {}), 
                                         conditions_to_highlight, page_num)
            
            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(pdf_template).stem
                output_filename = f"{base_name}_filled_{timestamp}.pdf"
            
            # Save filled PDF
            output_path = self.output_dir / output_filename
            pdf_document.save(str(output_path))
            pdf_document.close()
            
            logger.info(f"PDF saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error filling PDF: {e}")
            raise
    
    def _process_form_data(self, form_data, mapping):
        """Process form data, converting numeric references to field names"""
        processed = {}
        field_number_map = mapping.get('field_numbers', {})
        
        for key, value in form_data.items():
            # If key is a number (as string), look up field name
            if str(key).isdigit() and str(key) in field_number_map:
                field_name = field_number_map[str(key)]
                processed[field_name] = value
            else:
                # Use key directly as field name
                processed[key] = value
        
        return processed
    
    def _fill_fields(self, page, fields, form_data, page_num):
        """Fill regular fields on the page"""
        for field_name, field_info in fields.items():
            if field_info['page'] == page_num and field_name in form_data:
                self._add_text_to_field(page, field_info, str(form_data[field_name]))
    
    def _highlight_conditions(self, page, condition_boxes, conditions_to_highlight, page_num):
        """Highlight condition boxes on the page"""
        for condition in conditions_to_highlight:
            # Handle both numeric and string format (e.g., 5 or "5c")
            if isinstance(condition, str) and condition.endswith('c'):
                condition_num = condition[:-1]
            else:
                condition_num = str(condition)
            
            box_info = condition_boxes.get(condition_num)
            if box_info and box_info['page'] == page_num:
                self._highlight_box(page, box_info)
    
    def _add_text_to_field(self, page, field_info, text):
        """Add text to a field with proper formatting using textbox for wrapping"""
        coords = field_info['coordinates']
        # Use smaller font size for better fitting
        font_size = field_info.get('font_size', 7)  # Default to 7pt like symptoms fix
        
        x1, y1, x2, y2 = coords
        
        # Create rectangle with small padding
        rect = fitz.Rect(
            x1 + 2,  # Small left padding
            y1 + 2,  # Small top padding
            x2 - 2,  # Small right padding
            y2 - 2   # Small bottom padding
        )
        
        try:
            # Use PyMuPDF's insert_textbox for automatic text wrapping
            # This prevents text from running off the page
            rc = page.insert_textbox(
                rect,
                text,
                fontsize=font_size,          # Smaller font size
                fontname="helv",             # Helvetica font
                color=(0, 0, 0),            # Black color
                align=0,                     # Left align
                expandtabs=0,                # No tab expansion
                lineheight=0.9               # Tighter line spacing (90% of font size)
            )
            
            # Check if all text fit
            if rc < 0:
                logger.warning(f"Text overflow in field '{field_info.get('name', 'unknown')}': {-rc} characters didn't fit")
            else:
                logger.debug(f"Successfully inserted text in field '{field_info.get('name', 'unknown')}'")
                
        except Exception as e:
            logger.error(f"Error inserting text: {e}")
            # Fallback to simple text insertion if textbox fails
            y_center = y1 + (y2 - y1) / 2 + font_size / 3
            page.insert_text(
                (x1 + 2, y_center),
                text[:50] + "..." if len(text) > 50 else text,  # Truncate if too long
                fontsize=font_size,
                color=(0, 0, 0)
            )
    
    def _highlight_box(self, page, box_info):
        """Highlight a condition box"""
        coords = box_info['coordinates']
        x1, y1, x2, y2 = coords
        
        # Create highlight annotation
        rect = fitz.Rect(x1, y1, x2, y2)
        
        # Draw filled rectangle with transparency
        page.draw_rect(rect, color=(1, 0.8, 0), fill=(1, 0.8, 0), opacity=0.3)
        
        # Optionally add border
        page.draw_rect(rect, color=(0.8, 0.6, 0), width=1)
    
    def _wrap_text(self, text, max_width, font_size):
        """Simple text wrapping (kept for backward compatibility but not used)"""
        words = text.split()
        lines = []
        current_line = []
        
        # Approximate character width
        char_width = font_size * 0.5
        max_chars = int(max_width / char_width)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

# Example usage
if __name__ == "__main__":
    filler = GeneralPDFFiller()
    
    # Example form data
    form_data = {
        "name": "John Doe",
        "date": "2024-01-15",
        "description": "This is a long description that should wrap properly within the field boundaries without running off the page. The text will be automatically wrapped by PyMuPDF's textbox feature.",
        "1": "Field referenced by number"
    }
    
    conditions = [1, 3, "5c"]
    
    # Fill PDF
    output_path = filler.fill_pdf(
        pdf_template="template.pdf",
        mapping_file="mapping.json",
        form_data=form_data,
        conditions_to_highlight=conditions
    )
    
    print(f"Filled PDF saved to: {output_path}")