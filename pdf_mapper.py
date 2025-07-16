import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import fitz
from PIL import Image, ImageTk
import json
import os
from datetime import datetime
import math

class PDFFieldMapper:
    def __init__(self, root):
        self.root = root
        self.root.title("General PDF Field Mapper - Auto-saves as targetid.json")
        self.root.state('zoomed')
        
        self.pdf_path = None
        self.pdf_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.fields = {}
        self.condition_boxes = {}
        self.current_mode = "field"
        self.selected_box = None
        self.double_click_mode = None
        self.edit_start_pos = None
        
        self.drag_start_x = None
        self.drag_start_y = None
        self.current_rect = None
        
        self.setup_ui()
        
    def setup_ui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Button(control_frame, text="Load PDF", command=self.load_pdf).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Mapping", command=self.save_mapping).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Load Mapping", command=self.load_mapping).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Mode:").pack(side=tk.LEFT, padx=(20, 5))
        self.mode_var = tk.StringVar(value="field")
        tk.Radiobutton(control_frame, text="Field Mode", variable=self.mode_var, 
                      value="field", command=self.change_mode).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="Condition Mode", variable=self.mode_var, 
                      value="condition", command=self.change_mode).pack(side=tk.LEFT)
        
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Button(nav_frame, text="Previous Page", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next Page", command=self.next_page).pack(side=tk.LEFT, padx=5)
        self.page_label = tk.Label(nav_frame, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        tk.Label(nav_frame, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        tk.Button(nav_frame, text="-", command=self.zoom_out).pack(side=tk.LEFT)
        self.zoom_label = tk.Label(nav_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="+", command=self.zoom_in).pack(side=tk.LEFT)
        
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="gray", 
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        self.status_bar = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            self.pdf_path = file_path
            self.pdf_document = fitz.open(file_path)
            self.current_page = 0
            self.display_page()
            self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
            
    def display_page(self):
        if not self.pdf_document:
            return
            
        page = self.pdf_document[self.current_page]
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")
        
        self.page_image = Image.open(tk.io.BytesIO(img_data))
        self.photo_image = ImageTk.PhotoImage(self.page_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        self.draw_existing_boxes()
        
        self.page_label.config(text=f"Page: {self.current_page + 1}/{len(self.pdf_document)}")
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
    def draw_existing_boxes(self):
        for field_name, field_data in self.fields.items():
            if field_data['page'] == self.current_page:
                x1, y1, x2, y2 = field_data['coordinates']
                x1, y1 = self.pdf_to_canvas_coords(x1, y1)
                x2, y2 = self.pdf_to_canvas_coords(x2, y2)
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                  outline="blue", width=2,
                                                  tags=("field", field_name))
                text = self.canvas.create_text(x1, y1 - 5, text=field_name, 
                                             anchor=tk.SW, fill="blue",
                                             tags=("field_text", field_name))
                
        for num, box_data in self.condition_boxes.items():
            if box_data['page'] == self.current_page:
                x1, y1, x2, y2 = box_data['coordinates']
                x1, y1 = self.pdf_to_canvas_coords(x1, y1)
                x2, y2 = self.pdf_to_canvas_coords(x2, y2)
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                  outline="orange", width=2,
                                                  tags=("condition", str(num)))
                text = self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, 
                                             text=str(num), fill="orange",
                                             font=("Arial", 12, "bold"),
                                             tags=("condition_text", str(num)))
                
    def change_mode(self):
        self.current_mode = self.mode_var.get()
        self.status_bar.config(text=f"Mode: {self.current_mode}")
        
    def on_mouse_down(self, event):
        if self.double_click_mode:
            if self.double_click_mode == "resize":
                self.start_resize(event)
            elif self.double_click_mode == "move":
                self.start_move(event)
            return
            
        self.drag_start_x = self.canvas.canvasx(event.x)
        self.drag_start_y = self.canvas.canvasy(event.y)
        
    def on_mouse_drag(self, event):
        if self.double_click_mode == "move" and self.selected_box:
            self.perform_move(event)
            return
            
        if self.drag_start_x and self.drag_start_y:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            if self.current_rect:
                self.canvas.delete(self.current_rect)
                
            self.current_rect = self.canvas.create_rectangle(
                self.drag_start_x, self.drag_start_y, current_x, current_y,
                outline="red", width=2, dash=(5, 5)
            )
            
    def on_mouse_up(self, event):
        if self.double_click_mode == "resize" and self.drag_start_x:
            self.finish_resize(event)
            return
        elif self.double_click_mode == "move":
            return
            
        if self.drag_start_x and self.drag_start_y:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            if abs(current_x - self.drag_start_x) > 5 and abs(current_y - self.drag_start_y) > 5:
                self.create_box(self.drag_start_x, self.drag_start_y, current_x, current_y)
                
        if self.current_rect:
            self.canvas.delete(self.current_rect)
            self.current_rect = None
            
        self.drag_start_x = None
        self.drag_start_y = None
        
    def on_double_click(self, event):
        clicked_x = self.canvas.canvasx(event.x)
        clicked_y = self.canvas.canvasy(event.y)
        
        overlapping = self.canvas.find_overlapping(clicked_x-1, clicked_y-1, clicked_x+1, clicked_y+1)
        
        for item in overlapping:
            tags = self.canvas.gettags(item)
            if "field" in tags or "condition" in tags:
                box_id = tags[1]
                
                if not self.double_click_mode:
                    self.show_double_click_menu(event, box_id, tags[0])
                else:
                    self.double_click_mode = None
                    self.selected_box = None
                    self.status_bar.config(text="Edit mode ended")
                return
                
    def show_double_click_menu(self, event, box_id, box_type):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Resize", command=lambda: self.enter_resize_mode(box_id, box_type))
        menu.add_command(label="Move", command=lambda: self.enter_move_mode(box_id, box_type))
        menu.add_command(label="Change Font Size", command=lambda: self.change_font_size(box_id, box_type))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self.delete_box(box_id, box_type))
        
        menu.post(event.x_root, event.y_root)
        
    def enter_resize_mode(self, box_id, box_type):
        self.double_click_mode = "resize"
        self.selected_box = (box_id, box_type)
        
        items = self.canvas.find_withtag(box_type)
        for item in items:
            if box_id in self.canvas.gettags(item):
                self.canvas.delete(item)
                
        items = self.canvas.find_withtag(f"{box_type}_text")
        for item in items:
            if box_id in self.canvas.gettags(item):
                self.canvas.delete(item)
                
        self.status_bar.config(text="Resize mode: Drag to create new box, double-click to exit")
        
    def enter_move_mode(self, box_id, box_type):
        self.double_click_mode = "move"
        self.selected_box = (box_id, box_type)
        self.status_bar.config(text="Move mode: Drag box to new position, double-click to exit")
        
    def change_font_size(self, box_id, box_type):
        if box_type == "field":
            current_size = self.fields.get(box_id, {}).get('font_size', 10)
        else:
            current_size = self.condition_boxes.get(int(box_id), {}).get('font_size', 10)
            
        new_size = simpledialog.askinteger("Font Size", 
                                          f"Enter new font size (current: {current_size}):",
                                          initialvalue=current_size,
                                          minvalue=6, maxvalue=72)
        
        if new_size:
            if box_type == "field":
                if box_id in self.fields:
                    self.fields[box_id]['font_size'] = new_size
            else:
                if int(box_id) in self.condition_boxes:
                    self.condition_boxes[int(box_id)]['font_size'] = new_size
                    
            self.status_bar.config(text=f"Font size changed to {new_size}")
            
    def delete_box(self, box_id, box_type):
        if messagebox.askyesno("Delete Box", f"Delete this {box_type} box?"):
            items = self.canvas.find_withtag(box_type)
            for item in items:
                if box_id in self.canvas.gettags(item):
                    self.canvas.delete(item)
                    
            items = self.canvas.find_withtag(f"{box_type}_text")
            for item in items:
                if box_id in self.canvas.gettags(item):
                    self.canvas.delete(item)
                    
            if box_type == "field":
                if box_id in self.fields:
                    del self.fields[box_id]
            else:
                if int(box_id) in self.condition_boxes:
                    del self.condition_boxes[int(box_id)]
                    
            self.status_bar.config(text=f"{box_type.capitalize()} box deleted")
            
    def start_resize(self, event):
        self.drag_start_x = self.canvas.canvasx(event.x)
        self.drag_start_y = self.canvas.canvasy(event.y)
        
    def finish_resize(self, event):
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        if abs(current_x - self.drag_start_x) > 5 and abs(current_y - self.drag_start_y) > 5:
            box_id, box_type = self.selected_box
            
            x1, y1 = self.canvas_to_pdf_coords(self.drag_start_x, self.drag_start_y)
            x2, y2 = self.canvas_to_pdf_coords(current_x, current_y)
            
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            if box_type == "field":
                self.fields[box_id]['coordinates'] = [x1, y1, x2, y2]
            else:
                self.condition_boxes[int(box_id)]['coordinates'] = [x1, y1, x2, y2]
                
            self.display_page()
            
        self.double_click_mode = None
        self.selected_box = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.status_bar.config(text="Resize completed")
        
    def start_move(self, event):
        clicked_x = self.canvas.canvasx(event.x)
        clicked_y = self.canvas.canvasy(event.y)
        
        box_id, box_type = self.selected_box
        
        if box_type == "field":
            coords = self.fields[box_id]['coordinates']
        else:
            coords = self.condition_boxes[int(box_id)]['coordinates']
            
        x1, y1 = self.pdf_to_canvas_coords(coords[0], coords[1])
        x2, y2 = self.pdf_to_canvas_coords(coords[2], coords[3])
        
        self.edit_start_pos = (clicked_x - x1, clicked_y - y1, x2 - x1, y2 - y1)
        
    def perform_move(self, event):
        if not self.edit_start_pos:
            return
            
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        offset_x, offset_y, width, height = self.edit_start_pos
        
        new_x1 = current_x - offset_x
        new_y1 = current_y - offset_y
        new_x2 = new_x1 + width
        new_y2 = new_y1 + height
        
        box_id, box_type = self.selected_box
        
        items = self.canvas.find_withtag(box_type)
        for item in items:
            if box_id in self.canvas.gettags(item):
                self.canvas.coords(item, new_x1, new_y1, new_x2, new_y2)
                
        items = self.canvas.find_withtag(f"{box_type}_text")
        for item in items:
            if box_id in self.canvas.gettags(item):
                if box_type == "field":
                    self.canvas.coords(item, new_x1, new_y1 - 5)
                else:
                    self.canvas.coords(item, (new_x1 + new_x2) / 2, (new_y1 + new_y2) / 2)
                    
        x1, y1 = self.canvas_to_pdf_coords(new_x1, new_y1)
        x2, y2 = self.canvas_to_pdf_coords(new_x2, new_y2)
        
        if box_type == "field":
            self.fields[box_id]['coordinates'] = [x1, y1, x2, y2]
        else:
            self.condition_boxes[int(box_id)]['coordinates'] = [x1, y1, x2, y2]
            
    def on_mouse_move(self, event):
        if not self.pdf_document:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        pdf_x, pdf_y = self.canvas_to_pdf_coords(canvas_x, canvas_y)
        
        self.status_bar.config(text=f"PDF Coords: ({pdf_x:.1f}, {pdf_y:.1f})")
        
    def create_box(self, x1, y1, x2, y2):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        pdf_x1, pdf_y1 = self.canvas_to_pdf_coords(x1, y1)
        pdf_x2, pdf_y2 = self.canvas_to_pdf_coords(x2, y2)
        
        if self.current_mode == "field":
            field_name = simpledialog.askstring("Field Name", "Enter field name:")
            if field_name:
                self.fields[field_name] = {
                    'coordinates': [pdf_x1, pdf_y1, pdf_x2, pdf_y2],
                    'page': self.current_page,
                    'font_size': 10
                }
                self.display_page()
        else:
            next_num = len([b for b in self.condition_boxes.values() 
                          if b['page'] == self.current_page]) + 1
            
            self.condition_boxes[next_num] = {
                'coordinates': [pdf_x1, pdf_y1, pdf_x2, pdf_y2],
                'page': self.current_page,
                'font_size': 10
            }
            self.display_page()
            
    def canvas_to_pdf_coords(self, canvas_x, canvas_y):
        pdf_x = canvas_x / self.zoom_level
        pdf_y = canvas_y / self.zoom_level
        return pdf_x, pdf_y
        
    def pdf_to_canvas_coords(self, pdf_x, pdf_y):
        canvas_x = pdf_x * self.zoom_level
        canvas_y = pdf_y * self.zoom_level
        return canvas_x, canvas_y
        
    def zoom_in(self):
        self.zoom_level = min(self.zoom_level * 1.25, 5.0)
        self.display_page()
        
    def zoom_out(self):
        self.zoom_level = max(self.zoom_level / 1.25, 0.5)
        self.display_page()
        
    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.display_page()
            
    def save_mapping(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "No PDF loaded")
            return
        
        # Get the PDF filename without extension for targetid
        pdf_basename = os.path.basename(self.pdf_path)
        targetid = os.path.splitext(pdf_basename)[0]
        
        # Set default save path in blanks_and_json folder
        default_dir = os.path.join(os.path.dirname(__file__), "blanks_and_json")
        os.makedirs(default_dir, exist_ok=True)
        
        # Default filename is targetid.json
        default_filename = f"{targetid}.json"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=default_dir,
            initialfile=default_filename
        )
        
        if file_path:
            mapping_data = {
                'pdf_file': pdf_basename,
                'created_date': datetime.now().isoformat(),
                'fields': self.fields,
                'condition_boxes': {str(k): v for k, v in self.condition_boxes.items()}
            }
            
            with open(file_path, 'w') as f:
                json.dump(mapping_data, f, indent=2)
                
            messagebox.showinfo("Success", f"Mapping saved as {os.path.basename(file_path)}")
            
    def load_mapping(self):
        default_dir = os.path.join(os.path.dirname(__file__), "blanks_and_json")
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=default_dir
        )
        
        if file_path:
            with open(file_path, 'r') as f:
                mapping_data = json.load(f)
                
            self.fields = mapping_data.get('fields', {})
            self.condition_boxes = {int(k): v for k, v in 
                                  mapping_data.get('condition_boxes', {}).items()}
            
            self.display_page()
            messagebox.showinfo("Success", "Mapping loaded successfully")
            
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Remove all fields and condition boxes?"):
            self.fields = {}
            self.condition_boxes = {}
            self.display_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFFieldMapper(root)
    root.mainloop()