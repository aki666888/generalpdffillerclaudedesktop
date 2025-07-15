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
                output_filename = f"filled_form_{timestamp}.pdf"
            
            # Save filled PDF
            output_path = self.output_dir / output_filename
            pdf_document.save(str(output_path))
            pdf_document.close()
            
            logger.info(f"PDF filled successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error filling PDF: {str(e)}")
            raise
    
    def _process_form_data(self, form_data, mapping):
        """Process form data to handle numeric field references"""
        processed = {}
        fields = mapping.get('fields', {})
        field_list = list(fields.keys())
        
        for key, value in form_data.items():
            # Check if key is a number (field reference)
            if key.isdigit():
                field_index = int(key) - 1  # Convert to 0-based index
                if 0 <= field_index < len(field_list):
                    field_name = field_list[field_index]
                    processed[field_name] = value
                else:
                    logger.warning(f"Field number {key} out of range")
            else:
                # Use key as is (field name)
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
        """Add text to a field with proper formatting"""
        coords = field_info['coordinates']
        # Use font size 8 as default for better text fitting
        font_size = field_info.get('font_size', 8)
        
        x1, y1, x2, y2 = coords
        
        # Calculate box dimensions
        box_width = x2 - x1
        box_height = y2 - y1
        
        # Use consistent padding and spacing like symptoms field
        padding = 3
        line_height = font_size + 1  # Tight line spacing
        
        # Wrap text to fit width
        lines = self._wrap_text(text, box_width - (padding * 2), font_size)
        
        # Calculate how many lines we can actually fit
        max_lines = int((box_height - (padding * 2)) / line_height)
        
        # Draw the lines that fit
        y_pos = y1 + padding + font_size
        for i, line in enumerate(lines[:max_lines]):
            page.insert_text(
                (x1 + padding, y_pos),
                line,
                fontsize=font_size,
                color=(0, 0, 0),
                fontname="helv"
            )
            y_pos += line_height
            
        # Log if text was truncated
        if len(lines) > max_lines:
            logger.debug(f"Text truncated - {len(lines) - max_lines} lines omitted")
    
    def _highlight_box(self, page, box_info):
        """Highlight a condition box"""
        coords = box_info['coordinates']
        x1, y1, x2, y2 = coords
        
        # Create highlight annotation
        rect = fitz.Rect(x1, y1, x2, y2)
        
        # Draw filled rectangle with transparency
        page.draw_rect(rect, color=(1, 0.8, 0), fill=(1, 0.8, 0), opacity=0.3)
        
        # Optionally add border
        page.draw_rect(rect, color=(1, 0.5, 0), width=1)
    
    def _wrap_text(self, text, max_width, font_size):
        """Wrap text to fit within specified width"""
        # Better character width approximation for font size 8
        # Use 0.4 multiplier for tighter text fitting
        avg_char_width = font_size * 0.4
        max_chars_per_line = int(max_width / avg_char_width)
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # Check if adding this word exceeds the line limit
            if current_length + word_length + len(current_line) > max_chars_per_line:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    # Word is too long, split it
                    while len(word) > max_chars_per_line:
                        lines.append(word[:max_chars_per_line])
                        word = word[max_chars_per_line:]
                    if word:
                        current_line = [word]
                        current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines