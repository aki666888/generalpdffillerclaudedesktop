#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import os
from datetime import datetime
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_filler import GeneralPDFFiller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class JSONRPCHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.pdf_filler = GeneralPDFFiller()
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Received request: {request.get('method')}")
            
            # Handle JSON-RPC request
            response = self.handle_json_rpc(request)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": None
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_json_rpc(self, request):
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        try:
            if method == 'fillPDFForm':
                result = self.fill_pdf_form(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        except Exception as e:
            logger.error(f"Error in {method}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": str(e)
                },
                "id": request_id
            }
    
    def fill_pdf_form(self, params):
        target_id = params.get('target_id')
        form_data = params.get('form_data', {})
        conditions = params.get('conditions', [])
        
        if not target_id:
            raise ValueError("target_id is required")
        
        # Build paths based on target_id
        base_dir = Path(__file__).parent
        blanks_dir = base_dir / "blanks_and_json"
        
        pdf_template = blanks_dir / f"{target_id}.pdf"
        mapping_file = blanks_dir / f"{target_id}.json"
        
        # Check if files exist
        if not pdf_template.exists():
            raise FileNotFoundError(f"PDF template not found: {pdf_template}")
        if not mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
        
        # Create target-specific output directory
        output_dir = Path(__file__).parent / "output" / target_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{target_id}_{timestamp}.pdf"
        
        # Update pdf_filler to use target-specific directory
        self.pdf_filler.output_dir = output_dir
        
        # Fill the PDF
        output_path = self.pdf_filler.fill_pdf(
            str(pdf_template),
            str(mapping_file),
            form_data,
            conditions,
            output_filename
        )
        
        return {
            "success": True,
            "output_path": output_path,
            "message": f"PDF form filled successfully",
            "target_id": target_id
        }
    
    def log_message(self, format, *args):
        # Override to use our logger
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8080):
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, JSONRPCHandler)
    
    logger.info(f"General Form JSON-RPC Server running on http://localhost:{port}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()