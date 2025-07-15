# PharmaCare Symptoms Field Fix

## Quick Fix Instructions

### 1. Verify JSON Mapping File
Make sure `C:\forms\macs_form_mapping_v3_updated.json` has the field named `"symptoms"` (not "Patient Symptoms and Signs"):

```json
"symptoms": [
  {
    "page": 0,
    "x1": 27.0,
    "y1": 287.0,
    "x2": 585.0,
    "y2": 325.0
  }
]
```

### 2. Use the Fixed Filler
Copy `enhanced_pdf_filler_v2_fixed.py` to `C:\mcp-servers\pharmacare-form\` and rename it to `enhanced_pdf_filler_v2.py` (replace the old one).

The fixed version handles both field names:
- `"symptoms"` (matches LLM output)
- `"Patient Symptoms and Signs"` (old name for compatibility)

### 3. Restart JSON-RPC Server
```bash
cd C:\mcp-servers\pharmacare-form
python json_rpc_server.py
```

### 4. Test
The LLM request looks correct:
```json
{
  "patient_name": "Shokal, Norman",
  "phn": "9128109391",
  "phone": "(250) 816-1904",
  "condition_numbers": [17],
  "symptoms": "Heartburn and acid regurgitation...",
  "diagnosis": "Gastroesophageal reflux disease (GERD)",
  "medication": "Pantoprazole 40mg..."
}
```

This should now work because:
- LLM sends `"symptoms"`
- JSON file has field named `"symptoms"`
- Fixed filler accepts both `"symptoms"` and `"Patient Symptoms and Signs"`

## No Claude Desktop Config Changes Needed
Since you're using OpenRPC → JSON-RPC approach, no changes to Claude Desktop config are required.