#!/usr/bin/env python3
"""
Lightweight Local HTTP Server for OnePlus 10R Battery Command Center
Serves dashboard at http://localhost:5050
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 5050
DIRECTORY = Path(__file__).resolve().parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, format, *args):
        # Suppress noisy logs
        pass

def start_server():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"🚀 OnePlus 10R Battery Command Center running at:")
        print(f"👉 http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    start_server()
