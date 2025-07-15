@echo off
echo Starting JSON-RPC Server for General Form Filler...
echo Server will run on: http://localhost:8080
echo.
echo Use with OpenRPC MCP in Claude Desktop:
echo 1. Call method: fillPDFForm
echo 2. Server URL: http://localhost:8080
echo 3. Parameters: target_id, form_data, conditions
echo.
echo Place your PDFs and mappings in blanks_and_json folder
echo.

"C:\Program Files\Python312\python.exe" json_rpc_server.py

pause