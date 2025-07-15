# PDF Form Automation - Folder Structure Guide

## Overview

This system uses a targetid-based folder structure where the PDF filename (without extension) serves as the unique identifier for each form automation.

## Folder Structure

```
pdfmcp/
├── form_field_mapper_v4.py     # Mapping tool
├── enhanced_pdf_filler_v3.py   # Filling tool
├── blanks and json/            # Central storage
│   ├── xyz.pdf                 # Blank PDF (you place here)
│   ├── xyz.json                # Mapping file (created by mapper)
│   ├── abc.pdf                 # Another blank PDF
│   └── abc.json                # Another mapping
├── xyz/                        # Output folder (created by mapper)
│   ├── xyz_2024-01-15_10-30-45.pdf
│   └── xyz_2024-01-15_14-22-10.pdf
└── abc/                        # Another output folder
    └── abc_2024-01-15_11-15-30.pdf
```

## Workflow

### 1. Setup New Form Automation

1. **Place blank PDF**: Drop your blank PDF (e.g., `xyz.pdf`) into the `blanks and json` folder
2. **Create mapping**: Run `form_field_mapper_v4.py`
   - Load your PDF
   - Draw rectangles around fields
   - Save mapping (automatically creates `xyz` folder and saves `xyz.json` to `blanks and json`)

### 2. Fill Forms

```python
# Initialize with targetid
filler = EnhancedPDFFillerV3(targetid="xyz")

# Fill with data
form_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'condition_1': True  # Check condition box 1
}

# Creates: xyz/xyz_2024-01-15_10-30-45.pdf
output_path = filler.fill_pdf(form_data)
```

### 3. Command Line Usage

```bash
# List available fields for a form
python enhanced_pdf_filler_v3.py xyz --list-fields

# Test fill with sample data
python enhanced_pdf_filler_v3.py xyz --test
```

## Key Concepts

- **targetid**: The PDF filename without extension (e.g., `xyz` from `xyz.pdf`)
- **Blank PDFs**: Always stored in `blanks and json` folder
- **Mapping JSONs**: Always stored in `blanks and json` folder
- **Filled PDFs**: Always saved to targetid-named folders with timestamps

## Benefits

1. **No conflicts**: Timestamp-based naming prevents overwrites
2. **Organized**: Each form type has its own output folder
3. **Scalable**: Easy to add new forms - just drop PDF and create mapping
4. **Clear structure**: Input files separate from output files

## Example

For a form called `pharmacare_form.pdf`:
- Blank PDF: `blanks and json/pharmacare_form.pdf`
- Mapping: `blanks and json/pharmacare_form.json`
- Output folder: `pharmacare_form/`
- Filled PDFs: `pharmacare_form/pharmacare_form_2024-01-15_10-30-45.pdf`