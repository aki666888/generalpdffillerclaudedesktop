# General PDF Form Filler for Claude Desktop

Universal PDF form filling system that works with any PDF using a target ID approach.

## Overview

This system allows you to fill any PDF form by using a target ID system. Each PDF form type has its own ID (e.g., "medical", "invoice", "application") and Claude can fill it based on your instructions.

## Architecture

```
Claude Desktop → OpenRPC MCP → JSON-RPC Server (8080) → PDF Filler
```

## Directory Structure

```
generalformmcp/
├── blanks_and_json/      # Place PDFs and their mappings here
│   ├── medical.pdf       # Blank PDF template
│   ├── medical.json      # Field mapping for medical.pdf
│   ├── invoice.pdf       
│   └── invoice.json      
├── output/               # Filled PDFs organized by target ID
│   ├── medical/          
│   │   ├── medical_20240115_123456.pdf
│   │   └── medical_20240115_134512.pdf
│   └── invoice/
│       └── invoice_20240115_145623.pdf
├── pdf_filler.py         # PDF filling logic
├── json_rpc_server.py    # JSON-RPC server
├── pdf_mapper.py         # GUI tool for creating mappings
├── run_pdf_mapper.bat    # Launch the mapper tool
├── start_json_rpc_server.bat  # Start the server
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.12
- Node.js
- Claude Desktop

### 1. Install Prerequisites

- Python 3.12 or higher
- Node.js (for OpenRPC)
- Claude Desktop
- PyMuPDF: `pip install PyMuPDF`

### 2. Configure Claude Desktop

Add this to your Claude Desktop configuration file at `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openrpc": {
      "command": "npx",
      "args": ["-y", "@open-rpc/server-js"],
      "env": {}
    }
  }
}
```

**Note**: You only need ONE OpenRPC server configured, even if you use multiple JSON-RPC backends.

### 3. Start the JSON-RPC Server

Double-click `start_json_rpc_server.bat` or run:

```bash
python json_rpc_server.py
```

The server will run on `http://localhost:8080`

### 4. Restart Claude Desktop

Completely quit and restart Claude Desktop to load the OpenRPC configuration.

## Creating Form Mappings

### 1. Place your blank PDF in `blanks_and_json/` folder

For example: `blanks_and_json/medical.pdf`

### 2. Run the Mapper Tool

Double-click `run_pdf_mapper.bat` or run:

```bash
python pdf_mapper.py
```

### 3. Create Field Mappings

1. Load your PDF from `blanks_and_json/`
2. Draw rectangles around form fields
3. Double-click boxes to edit options
4. Switch to "Condition Mode" for numbered highlight boxes
5. Save - it will auto-suggest `targetid.json` (e.g., `medical.json`)

### Field Numbering System

- **Regular fields**: Referenced as 1, 2, 3, 4...
- **Condition boxes**: Referenced as 1c, 2c, 3c, 4c...

## Using with Claude Desktop

### Basic Usage

Tell Claude to use the RPC tool to call fillPDFForm. Examples:

#### Example 1: Medical Form
```
Use the RPC tool to call fillPDFForm at http://localhost:8080 with:
- target_id: "medical"
- form_data: {"1": "John Doe", "2": "555-1234", "3": "Headache"}
- conditions: ["1c", "5c", "10c"]
```

#### Example 2: Invoice Form
```
Fill the invoice form where:
- Field 1 (company name) = "ABC Corporation"
- Field 2 (amount) = "$1,234.56"
- Field 3 (date) = "2024-01-15"
```

### Natural Language Usage

You can define field meanings in your conversation:

```
For the medical form:
- Field 1 is patient name
- Field 2 is phone number
- Field 3 is symptoms
- Condition 1c is "Headache"
- Condition 5c is "Fever"

Now fill it for John Doe with phone 555-1234 who has headache and fever.
```

## Adding New Forms

1. Copy your blank PDF to `blanks_and_json/` (e.g., `application.pdf`)
2. Run the mapper tool
3. Create field mappings
4. Save as `application.json`
5. Use with target_id: "application"

## Troubleshooting

### "Cannot connect to localhost:8080"
- Ensure the JSON-RPC server is running
- Check Windows Firewall settings

### "Target ID not found"
- Verify both PDF and JSON exist in `blanks_and_json/`
- Check that filenames match (e.g., `invoice.pdf` and `invoice.json`)

### OpenRPC not showing in Claude
- Ensure Node.js is installed (`node --version`)
- Restart Claude Desktop completely
- Check logs at `%APPDATA%\Claude\logs\`

## API Reference

### fillPDFForm Method

**Parameters:**
- `target_id` (string): The form identifier (filename without extension)
- `form_data` (object): Key-value pairs for field data
  - Keys can be numbers ("1", "2") or field names
- `conditions` (array): List of condition boxes to highlight
  - Format: ["1c", "2c"] or [1, 2]

**Returns:**
- `success` (boolean): Operation status
- `output_path` (string): Path to the filled PDF
- `message` (string): Status message
- `target_id` (string): The target ID used

## Tips

1. **Consistent Naming**: Keep PDF and JSON names identical (except extension)
2. **Field Organization**: Number fields logically (top to bottom, left to right)
3. **Backup Mappings**: Keep copies of your JSON mapping files
4. **Test First**: Test with sample data before production use

## License

MIT