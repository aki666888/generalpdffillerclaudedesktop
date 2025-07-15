@echo off
echo Starting PharmaCare Form JSON-RPC Server...
echo.
echo This server handles fillPharmaCareForm requests from Claude Desktop.
echo.

cd /d "C:\mcp-servers\pharmacare-form"

REM Start the JSON-RPC server on port 8080
"C:\Program Files\Python312\python.exe" -u json_rpc_server.py

pause