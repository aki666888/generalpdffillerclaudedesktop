# Final Symptoms Fix - Simple Steps

## The Problem
The mapping JSON file has "Patient Symptoms and Signs" but everything else uses "symptoms".

## The Solution

### Step 1: Replace the mapping file
Copy `macs_form_mapping_v3_fixed.json` to `C:\mcp-servers\pharmacare-form\macs_form_mapping_v3.json`

This file has:
- Changed "Patient Symptoms and Signs" → "symptoms" (line 40)
- Everything else stays the same

### Step 2: That's it!
The filler code already looks for "symptoms", so once the JSON file uses "symptoms", everything will work.

## Why This Will Work
1. Claude sends: `"symptoms": "text here"`
2. JSON file now has: `"symptoms": [coordinates]`
3. Filler code looks for: `if field_type == 'symptoms':`
4. Perfect match = symptoms appear!

## Test Command
```bash
cd C:\mcp-servers\pharmacare-form
copy macs_form_mapping_v3_fixed.json macs_form_mapping_v3.json
```

Then restart the JSON-RPC server and try again.