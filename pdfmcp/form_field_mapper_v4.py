#!/usr/bin/env python3
"""
Enhanced Form Field Mapper V4
- Creates targetid folders and saves mapping to "blanks and json" folder
- PDF name serves as targetid
- Saves mapping JSON in both targetid folder and "blanks and json" folder
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import json
import os

class FormFieldMapperV4:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PharmaCare Form Field Mapper V4 - Enhanced")
        self.root.geometry("1600x900")
        
        # Variables
        self.pdf_path = None
        self.pdf_doc = None
        self.current_page = 0
        self.photo = None
        self.scale = 1.0
        self.fields = {}
        self.condition_boxes = []
        self.mode = "field"  # "field" or "condition"
        self.font_size = 10  # Fixed font size
        
        # Drawing state
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.temp_rect = None
        self.field_rectangles = {}  # Store canvas rectangles for editing
        self.condition_rectangles = {}  # Store condition rectangles
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        # Top frame for controls
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Load PDF button
        tk.Button(control_frame, text="Load PDF", command=self.load_pdf,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Mode selection
        tk.Label(control_frame, text="Mode:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(20, 5))
        mode_frame = tk.Frame(control_frame, bg="#f0f0f0")
        mode_frame.pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="field")
        tk.Radiobutton(mode_frame, text="Field Mode", variable=self.mode_var, 
                      value="field", command=self.switch_mode, bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Condition Mode", variable=self.mode_var, 
                      value="condition", command=self.switch_mode, bg="#f0f0f0").pack(side=tk.LEFT)
        
        # Field type dropdown (for field mode)
        self.field_frame = tk.Frame(control_frame, bg="#f0f0f0")
        self.field_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(self.field_frame, text="Field Type:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.field_type_var = tk.StringVar()
        self.field_dropdown = ttk.Combobox(self.field_frame, textvariable=self.field_type_var,
                                          width=30, font=("Arial", 10))
        self.field_dropdown.pack(side=tk.LEFT)
        
        # Set pharmacare field types
        field_types = [
            'last_name', 'first_name', 'middle_name',
            'date_of_birth', 'health_number', 'pharmacare_number',
            'address_line1', 'address_line2', 'city', 'postal_code',
            'phone_number', 'physician_name', 'physician_msp',
            'pharmacy_name', 'pharmacy_phone', 'pharmacy_fax',
            'medication_name', 'din', 'strength', 'quantity',
            'days_supply', 'refills', 'generic_substitution',
            'special_instructions', 'diagnosis', 'icd_code',
            'signature', 'date_signed', 'effective_date',
            'checkbox_yes', 'checkbox_no', 'checkbox_new', 'checkbox_refill'
        ]
        
        self.field_dropdown['values'] = field_types
        if field_types:
            self.field_dropdown.set(field_types[0])
        
        # Navigation
        nav_frame = tk.Frame(control_frame, bg="#f0f0f0")
        nav_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(nav_frame, text="◄ Prev", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        self.page_label = tk.Label(nav_frame, text="Page: 0/0", bg="#f0f0f0")
        self.page_label.pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Next ►", command=self.next_page).pack(side=tk.LEFT, padx=2)
        
        # Main area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for PDF display
        pdf_frame = tk.Frame(main_frame, bg="#ddd", relief=tk.SUNKEN, bd=2)
        pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas for PDF
        self.canvas = tk.Canvas(pdf_frame, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(pdf_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = tk.Scrollbar(pdf_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Right panel for field list
        right_panel = tk.Frame(main_frame, width=300, bg="#f5f5f5")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="Mapped Fields", font=("Arial", 12, "bold"), 
                bg="#f5f5f5").pack(pady=5)
        
        # Field list
        list_frame = tk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.field_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       font=("Arial", 9), height=25)
        self.field_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.field_listbox.yview)
        
        # Bind double-click to edit
        self.field_listbox.bind('<Double-Button-1>', self.edit_field_name)
        
        # Bottom controls
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Action buttons
        tk.Button(bottom_frame, text="Save Mapping", command=self.save_mapping,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Load Mapping", command=self.load_mapping,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Clear All", command=self.clear_all,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Delete Selected", command=self.delete_selected,
                 bg="#795548", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        self.instruction_label = tk.Label(bottom_frame, 
                                        text="📌 Draw rectangles around fields | Double-click list to edit names",
                                        bg="#f0f0f0", fg="#666", font=("Arial", 10))
        self.instruction_label.pack(side=tk.RIGHT, padx=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to load PDF")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Start the GUI
        self.root.mainloop()
    
    def switch_mode(self):
        """Switch between field and condition mode"""
        self.mode = self.mode_var.get()
        if self.mode == "field":
            self.field_frame.pack(side=tk.LEFT, padx=20)
            self.instruction_label.config(text="📌 Draw rectangles around fields | Double-click list to edit names")
        else:
            self.field_frame.pack_forget()
            self.instruction_label.config(text="📌 Draw rectangles around condition boxes (auto-numbered)")
        self.redraw_all()
        self.status_var.set(f"Switched to {self.mode} mode")
    
    def on_mouse_down(self, event):
        """Start drawing rectangle"""
        if not self.pdf_doc:
            return
        
        # Convert canvas coordinates to PDF coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        self.drawing = True
        self.start_x = canvas_x
        self.start_y = canvas_y
        
        # Create temporary rectangle
        self.temp_rect = self.canvas.create_rectangle(
            canvas_x, canvas_y, canvas_x, canvas_y,
            outline="blue", width=2, dash=(5, 5),
            tags="temp"
        )
    
    def on_mouse_drag(self, event):
        """Update rectangle while dragging"""
        if not self.drawing or not self.temp_rect:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Update temporary rectangle
        self.canvas.coords(self.temp_rect, self.start_x, self.start_y, canvas_x, canvas_y)
    
    def on_mouse_up(self, event):
        """Finish drawing rectangle"""
        if not self.drawing:
            return
        
        self.drawing = False
        
        if self.temp_rect:
            # Get final coordinates
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            # Convert to PDF coordinates (accounting for scale)
            x1 = min(self.start_x, canvas_x) / self.scale
            y1 = min(self.start_y, canvas_y) / self.scale
            x2 = max(self.start_x, canvas_x) / self.scale
            y2 = max(self.start_y, canvas_y) / self.scale
            
            # Minimum size check
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 5:
                if self.mode == "field":
                    self.add_field(x1, y1, x2, y2)
                else:
                    self.add_condition_box(x1, y1, x2, y2)
            
            # Remove temporary rectangle
            self.canvas.delete(self.temp_rect)
            self.temp_rect = None
            
            # Redraw all markers
            self.redraw_all()
            self.update_field_list()
    
    def add_field(self, x1, y1, x2, y2):
        """Add a field with current type"""
        field_type = self.field_type_var.get()
        if not field_type:
            messagebox.showwarning("Field Type", "Please select a field type")
            return
        
        # Add to fields
        if field_type not in self.fields:
            self.fields[field_type] = []
        
        self.fields[field_type].append({
            'page': self.current_page,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        })
        
        self.status_var.set(f"Added field: {field_type}")
    
    def add_condition_box(self, x1, y1, x2, y2):
        """Add a numbered condition box"""
        # Auto-number the box
        box_number = len(self.condition_boxes) + 1
        
        self.condition_boxes.append({
            'number': box_number,
            'page': self.current_page,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        })
        
        self.status_var.set(f"Added condition box #{box_number}")
    
    def redraw_all(self):
        """Redraw all field and condition markers"""
        # Clear existing markers (except the PDF image)
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "field" in tags or "condition" in tags or "temp" in tags:
                self.canvas.delete(item)
        
        # Clear tracking dictionaries
        self.field_rectangles.clear()
        self.condition_rectangles.clear()
        
        # Draw field boxes
        if self.mode == "field":
            for field_type, boxes in self.fields.items():
                for i, box in enumerate(boxes):
                    if box['page'] == self.current_page:
                        self.draw_field_box(field_type, box, i)
        
        # Draw condition boxes
        for cond_box in self.condition_boxes:
            if cond_box['page'] == self.current_page:
                self.draw_condition_box(cond_box)
    
    def draw_field_box(self, field_type, box, index):
        """Draw a single field box"""
        x1 = box['x1'] * self.scale
        y1 = box['y1'] * self.scale
        x2 = box['x2'] * self.scale
        y2 = box['y2'] * self.scale
        
        # Draw rectangle
        rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red", width=2,
            tags=("field", f"field_{field_type}_{index}")
        )
        
        # Draw label
        text_id = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=field_type,
            fill="red", font=("Arial", self.font_size, "bold"),
            tags=("field", f"field_{field_type}_{index}")
        )
        
        # Store reference for editing
        key = f"{field_type}_{index}"
        self.field_rectangles[key] = {
            'rect_id': rect_id,
            'text_id': text_id,
            'field_type': field_type,
            'index': index
        }
    
    def draw_condition_box(self, cond_box):
        """Draw a single condition box"""
        x1 = cond_box['x1'] * self.scale
        y1 = cond_box['y1'] * self.scale
        x2 = cond_box['x2'] * self.scale
        y2 = cond_box['y2'] * self.scale
        
        # Draw yellow-bordered rectangle
        rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="gold", width=3,
            tags=("condition", f"condition_{cond_box['number']}")
        )
        
        # Draw number
        text_id = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=str(cond_box['number']),
            fill="gold", font=("Arial", self.font_size + 4, "bold"),
            tags=("condition", f"condition_{cond_box['number']}")
        )
        
        # Store reference
        self.condition_rectangles[cond_box['number']] = {
            'rect_id': rect_id,
            'text_id': text_id
        }
    
    def load_pdf(self):
        """Load a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF Form",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.pdf_path = file_path
            self.pdf_doc = fitz.open(file_path)
            self.current_page = 0
            self.fields.clear()
            self.condition_boxes.clear()
            self.display_page()
            self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
    
    def display_page(self):
        """Display current PDF page"""
        if not self.pdf_doc:
            return
        
        # Get the page
        page = self.pdf_doc[self.current_page]
        
        # Render page to pixmap
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for clarity
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(tk.io.BytesIO(img_data))
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Update page label
        self.page_label.config(text=f"Page: {self.current_page + 1}/{len(self.pdf_doc)}")
        
        # Store scale factor
        self.scale = 2.0
        
        # Redraw markers
        self.redraw_all()
        self.update_field_list()
    
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.display_page()
    
    def update_field_list(self):
        """Update the field list display"""
        self.field_listbox.delete(0, tk.END)
        
        # Add fields
        for field_type, boxes in self.fields.items():
            for i, box in enumerate(boxes):
                page_num = box['page'] + 1
                self.field_listbox.insert(tk.END, f"[Field] {field_type} - Page {page_num}")
        
        # Add condition boxes
        for cond_box in self.condition_boxes:
            page_num = cond_box['page'] + 1
            self.field_listbox.insert(tk.END, f"[Condition] Box #{cond_box['number']} - Page {page_num}")
    
    def edit_field_name(self, event):
        """Edit field name on double-click"""
        selection = self.field_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        item_text = self.field_listbox.get(index)
        
        if "[Field]" in item_text:
            # Count to find which field this is
            field_count = 0
            for field_type, boxes in self.fields.items():
                for i, box in enumerate(boxes):
                    if field_count == index:
                        # Found the field, prompt for new name
                        new_name = simpledialog.askstring(
                            "Edit Field Name",
                            f"Enter new name for '{field_type}':",
                            initialvalue=field_type
                        )
                        
                        if new_name and new_name != field_type:
                            # Create new field list without the old one
                            old_boxes = self.fields.pop(field_type)
                            
                            # Add with new name
                            if new_name not in self.fields:
                                self.fields[new_name] = []
                            self.fields[new_name].extend(old_boxes)
                            
                            # Update display
                            self.redraw_all()
                            self.update_field_list()
                            self.status_var.set(f"Renamed '{field_type}' to '{new_name}'")
                        return
                    field_count += 1
    
    def delete_selected(self):
        """Delete selected field or condition box"""
        selection = self.field_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a field or condition box to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Delete selected item?"):
            index = selection[0]
            item_text = self.field_listbox.get(index)
            
            if "[Field]" in item_text:
                # Delete field
                field_count = 0
                for field_type in list(self.fields.keys()):
                    boxes = self.fields[field_type]
                    for i in range(len(boxes)):
                        if field_count == index:
                            boxes.pop(i)
                            if not boxes:
                                del self.fields[field_type]
                            self.redraw_all()
                            self.update_field_list()
                            self.status_var.set(f"Deleted field")
                            return
                        field_count += 1
            else:
                # Delete condition box
                # Adjust for fields in the list
                field_count = sum(len(boxes) for boxes in self.fields.values())
                cond_index = index - field_count
                
                if 0 <= cond_index < len(self.condition_boxes):
                    self.condition_boxes.pop(cond_index)
                    # Renumber remaining boxes
                    for i, box in enumerate(self.condition_boxes):
                        box['number'] = i + 1
                    self.redraw_all()
                    self.update_field_list()
                    self.status_var.set(f"Deleted condition box")
    
    def clear_all(self):
        """Clear all mappings"""
        if messagebox.askyesno("Clear All", "Remove all field mappings and condition boxes?"):
            self.fields.clear()
            self.condition_boxes.clear()
            self.redraw_all()
            self.update_field_list()
            self.status_var.set("Cleared all mappings")
    
    def save_mapping(self):
        """Save field and condition mapping"""
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please load a PDF first")
            return
        
        # Get PDF name without extension to use as targetid
        pdf_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Get script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create "blanks and json" folder if it doesn't exist
        blanks_json_dir = os.path.join(script_dir, "blanks and json")
        os.makedirs(blanks_json_dir, exist_ok=True)
        
        # Create targetid folder if it doesn't exist
        targetid_dir = os.path.join(script_dir, pdf_name)
        os.makedirs(targetid_dir, exist_ok=True)
        
        # Prepare mapping data
        mapping_data = {
            'pdf_file': os.path.basename(self.pdf_path),
            'targetid': pdf_name,
            'fields': self.fields,
            'condition_boxes': self.condition_boxes,
            'font_size': self.font_size,
            'context': 'PharmaCare MACS form with numbered condition boxes'
        }
        
        # Save to "blanks and json" folder
        json_path = os.path.join(blanks_json_dir, f"{pdf_name}.json")
        with open(json_path, 'w') as f:
            json.dump(mapping_data, f, indent=2)
        
        messagebox.showinfo("Success", 
                          f"Mapping saved!\n\n"
                          f"JSON saved to: blanks and json/{pdf_name}.json\n"
                          f"Output folder created: {pdf_name}/\n\n"
                          f"Place your blank PDF as: blanks and json/{pdf_name}.pdf")
        self.status_var.set(f"Saved: {pdf_name}.json in blanks and json folder")
    
    def load_mapping(self):
        """Load existing mapping"""
        file_path = filedialog.askopenfilename(
            title="Load Mapping",
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "blanks and json"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.fields = data.get('fields', {})
            self.condition_boxes = data.get('condition_boxes', [])
            self.font_size = data.get('font_size', 10)
            
            # Try to load the associated PDF
            pdf_name = data.get('pdf_file', '')
            if pdf_name:
                # Look in "blanks and json" folder first
                script_dir = os.path.dirname(os.path.abspath(__file__))
                pdf_path = os.path.join(script_dir, "blanks and json", pdf_name)
                
                if os.path.exists(pdf_path):
                    self.pdf_path = pdf_path
                    self.pdf_doc = fitz.open(pdf_path)
                    self.current_page = 0
                    self.display_page()
                else:
                    messagebox.showinfo("PDF Not Found", 
                                      f"Associated PDF not found in blanks and json folder.\n"
                                      f"Expected: {pdf_name}\n"
                                      f"Please load the PDF manually.")
            
            self.redraw_all()
            self.update_field_list()
            self.status_var.set(f"Loaded mapping: {os.path.basename(file_path)}")

if __name__ == "__main__":
    app = FormFieldMapperV4()