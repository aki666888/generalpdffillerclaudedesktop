@echo off
echo Starting JSON-RPC Server for General PDF Form Filler...
echo Server will run on: http://localhost:8000
echo.
echo Use with Claude Desktop OpenRPC configuration
echo Method: fillForm
echo.
python json_rpc_server.py
pause