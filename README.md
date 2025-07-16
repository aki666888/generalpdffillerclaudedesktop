# General PDF Form Filler

A flexible PDF form filling system that works with Claude Desktop through JSON-RPC.

## Features
- Fill any PDF form using mapped field coordinates
- Automatic text wrapping and font size adjustment
- Support for condition checkboxes
- Works with Claude Desktop via JSON-RPC server

## Setup

1. Install required Python packages:
```bash
pip install PyMuPDF
```

2. Place your blank PDF forms in the `blanks_and_json` folder

3. Use the PDF mapper to create field mappings:
```bash
python pdf_mapper.py
```

4. Start the JSON-RPC server:
```bash
python json_rpc_server.py
```

5. Configure Claude Desktop with `claude_config.json`

## File Structure
```
generalformmcp/
├── claude_config.json      # Claude Desktop configuration
├── json_rpc_server.py      # JSON-RPC server for Claude integration
├── pdf_filler.py          # Core PDF filling logic
├── pdf_mapper.py          # Visual tool for mapping PDF fields
├── run_pdf_mapper.bat     # Windows batch file to run mapper
├── start_json_rpc_server.bat  # Windows batch file to start server
├── blanks_and_json/       # Store blank PDFs and mapping JSONs here
└── logs/                  # Log files directory
```

## Usage

### Creating Field Mappings
1. Run `run_pdf_mapper.bat` (or `python pdf_mapper.py`)
2. Load your blank PDF
3. Draw rectangles around form fields
4. Name each field
5. Save the mapping as JSON

### Filling Forms via Claude Desktop
1. Start the server with `start_json_rpc_server.bat`
2. Use Claude Desktop to send form data
3. Filled PDFs will be saved in the output directory

## Field Types
- Regular text fields (automatic wrapping)
- Condition checkboxes (numbered boxes)
- Multi-line fields (automatic font size adjustment)

## API

The JSON-RPC server accepts requests at `http://localhost:8000` with method `fillForm`:

```json
{
  "jsonrpc": "2.0",
  "method": "fillForm",
  "params": {
    "template": "form_template.pdf",
    "mapping": "form_mapping.json",
    "data": {
      "name": "John Doe",
      "date": "2024-01-15",
      "description": "Long text that will wrap automatically"
    },
    "conditions": [1, 3, 5]
  },
  "id": 1
}
```

## License
MIT License