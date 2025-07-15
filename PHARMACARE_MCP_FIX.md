# PharmaCare MCP Server Fix

## The Problem

The `mcp_server_simple.py` was causing symptoms not to be populated because:
1. It doesn't have a `fillPharmaCareForm` tool
2. It only has `test_pharmacare` and `open_form` tools
3. Claude Desktop needs `fillPharmaCareForm` to work properly

## The Solution

### Option 1: Use the Proper MCP Server (Recommended)

1. Copy `mcp_server_pharmacare.py` to `C:\mcp-servers\pharmacare-form\`
2. Update Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "pharmacare-form": {
      "command": "C:\\Program Files\\Python312\\python.exe",
      "args": ["-u", "C:\\mcp-servers\\pharmacare-form\\mcp_server_pharmacare.py"]
    }
  }
}
```
3. Restart Claude Desktop
4. Now `fillPharmaCareForm` will work properly with symptoms

### Option 2: Use JSON-RPC Server with OpenRPC

1. Start the JSON-RPC server:
```bash
cd C:\mcp-servers\pharmacare-form
python json_rpc_server.py
```

2. In Claude Desktop, use OpenRPC to call:
```json
{
  "server_url": "http://localhost:8080",
  "method_name": "fillPharmaCareForm",
  "params": {
    "patient_name": "Last, First",
    "phn": "9123456789",
    "phone": "(250) 555-1234",
    "condition_numbers": [16],
    "symptoms": "This will now appear in the PDF!",
    "diagnosis": "Your diagnosis",
    "medication": "Medication details"
  }
}
```

## Why Symptoms Weren't Working

The `mcp_server_simple.py` doesn't handle form filling at all. When Claude Desktop tried to call `fillPharmaCareForm`, the server couldn't respond properly, so no data (including symptoms) was being passed to the PDF filler.

## Testing

To verify symptoms are now working:
```python
# Test with the new MCP server
{
  "patient_name": "TEST, PATIENT",
  "phn": "9999999999", 
  "phone": "(250) 555-TEST",
  "condition_numbers": [16],
  "symptoms": "TEST: If you see this text in the PDF, symptoms are working!",
  "diagnosis": "Test diagnosis",
  "medication": "Test medication"
}
```

Check the generated PDF - the symptoms should appear in the "Patient Symptoms and Signs" field.