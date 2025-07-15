#!/usr/bin/env python3
"""
MCP Server for PharmaCare Form Filler
This server properly handles fillPharmaCareForm requests from Claude Desktop
"""

import asyncio
import sys
import os
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server import NotificationOptions, Server

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the PDF filler
try:
    from enhanced_pdf_filler_v2 import fill_pdf_with_numbers
except ImportError:
    # If not in same directory, try the full path
    sys.path.insert(0, r"C:\mcp-servers\pharmacare-form")
    from enhanced_pdf_filler_v2 import fill_pdf_with_numbers

# Initialize MCP server
server = Server("pharmacare-form")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="fillPharmaCareForm",
            description="Fill a PharmaCare MACS form with patient data",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "Patient's full name (Last, First)"
                    },
                    "phn": {
                        "type": "string",
                        "description": "10-digit Personal Health Number"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Patient phone number"
                    },
                    "condition_numbers": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Array of condition box numbers to check"
                    },
                    "symptoms": {
                        "type": "string",
                        "description": "Patient symptoms and signs"
                    },
                    "medical_history": {
                        "type": "string",
                        "description": "Medical history, allergies, contraindications"
                    },
                    "diagnosis": {
                        "type": "string",
                        "description": "Clinical diagnosis"
                    },
                    "medication": {
                        "type": "string",
                        "description": "Medication details including sig, quantity, refills"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date (optional, defaults to today)"
                    }
                },
                "required": ["patient_name", "phn", "phone", "symptoms", "diagnosis", "medication"]
            }
        ),
        Tool(
            name="test_pharmacare",
            description="Test if PharmaCare MCP server is working",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "test_pharmacare":
        return [TextContent(
            type="text", 
            text="✅ PharmaCare MCP server is working! You can now use fillPharmaCareForm."
        )]
    
    elif name == "fillPharmaCareForm":
        try:
            # Log the received data for debugging
            print(f"Received fillPharmaCareForm request", file=sys.stderr)
            print(f"Patient: {arguments.get('patient_name')}", file=sys.stderr)
            print(f"Symptoms length: {len(arguments.get('symptoms', ''))}", file=sys.stderr)
            
            # Call the PDF filler
            result = fill_pdf_with_numbers(arguments)
            
            return [TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            error_msg = f"❌ Error filling form: {str(e)}"
            print(error_msg, file=sys.stderr)
            return [TextContent(
                type="text",
                text=error_msg
            )]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pharmacare-form",
                server_version="2.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())