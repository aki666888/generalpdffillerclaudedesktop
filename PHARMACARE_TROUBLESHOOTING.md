# PharmaCare Form Troubleshooting Guide

## Issue: Symptoms Not Appearing in PDF

### The Problem
Claude Desktop is providing symptoms data but it's not appearing in the filled PDF form.

### Solution

#### 1. Use the Correct Server
The MCP server (`mcp_server_simple.py`) doesn't handle form filling. You need to use the JSON-RPC server instead.

**Start the JSON-RPC Server:**
```bash
cd C:\mcp-servers\pharmacare-form
python json_rpc_server.py
```

This server listens on `http://localhost:8080` and handles the `fillPharmaCareForm` method.

#### 2. Verify the Mapping File
Check that `macs_form_mapping_v3_updated.json` includes the symptoms field:
```json
"Patient Symptoms and Signs": [
  {
    "page": 0,
    "x1": 27.0,
    "y1": 287.0,
    "x2": 585.0,
    "y2": 325.0
  }
]
```

#### 3. Claude Desktop Configuration
Update `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "chrome-mcp": {
      "command": "node",
      "args": ["C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\npm\\node_modules\\mcp-chrome-bridge\\dist\\mcp\\mcp-server-stdio.js"]
    }
  }
}
```

Note: Don't add the pharmacare-form server here - it runs separately as a JSON-RPC server.

#### 4. Correct Usage in Claude Desktop

When using Claude Desktop with OpenRPC, make sure to:

1. Start the JSON-RPC server first (runs on port 8080)
2. Use the OpenRPC MCP tool with:
```json
{
  "server_url": "http://localhost:8080",
  "method_name": "fillPharmaCareForm",
  "params": {
    "patient_name": "Smith, John",
    "phn": "9876543210",
    "phone": "(250) 555-1234",
    "condition_numbers": [16],
    "symptoms": "Your symptoms text here",
    "diagnosis": "Your diagnosis",
    "medication": "Medication details"
  }
}
```

### Testing the Symptoms Field

Run this test script to verify symptoms are being filled:

```python
import requests
import json

# Test data with symptoms
test_data = {
    "jsonrpc": "2.0",
    "method": "fillPharmaCareForm",
    "params": {
        "patient_name": "Test, Patient",
        "phn": "9123456789",
        "phone": "(250) 555-1234",
        "condition_numbers": [16],
        "symptoms": "This is a test of the symptoms field. It should appear in the PDF.",
        "diagnosis": "Test diagnosis",
        "medication": "Test medication"
    },
    "id": 1
}

# Send to JSON-RPC server
response = requests.post('http://localhost:8080', json=test_data)
print(response.json())
```

### Debug Checklist

- [ ] JSON-RPC server is running on port 8080
- [ ] Using `enhanced_pdf_filler_v2.py` (not v3)
- [ ] Mapping file has "Patient Symptoms and Signs" field
- [ ] OpenRPC is calling correct server URL
- [ ] Symptoms text is being passed in params
- [ ] Check server console for debug output

### Server Logs

The server prints debug information:
```
DEBUG: Received data for Test, Patient
DEBUG: Symptoms length: 65
DEBUG: Medication length: 15
```

If symptoms length is 0, the data isn't being passed correctly.

## Alternative: Direct Python Script

If the MCP approach continues to fail, use the direct Python script:

```bash
cd C:\mcp-servers\pharmacare-form
python enhanced_pdf_filler_v2.py
```

Then manually enter the data when prompted.