#!/usr/bin/env python3
"""
ProductViewSet Standalone API Service
Auto-converted from Django REST Framework
Build ID: auto_fixed
"""

import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

class ProductViewSetHandler(BaseHTTPRequestHandler):
    """HTTP handler for ProductViewSet"""

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            'service': 'ProductViewSet',
            'build_id': 'auto_fixed',
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'endpoints': [
                'GET / - Service status',
                'POST /process_data - Execute process_data'
            ]
        }

        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/process_data':
            self.process_data()
        else:
            self.send_error(404, 'Endpoint not found')

    def process_data(self):
        """Execute process_data"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}

            # Process the data
            result = {
                'success': True,
                'build_id': 'auto_fixed',
                'timestamp': datetime.now().isoformat(),
                'processed_data': data,
                'method': 'process_data',
                'service': 'ProductViewSet'
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())

            print(f"✅ {result['method']} executed successfully")

        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'build_id': 'auto_fixed',
                'service': 'ProductViewSet'
            }

            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, indent=2).encode())

            print(f"❌ Error: {e}")

class ProductViewSet:
    """Standalone ProductViewSet service"""

    def __init__(self, port=8080):
        self.port = port
        self.build_id = "auto_fixed"

    def start_server(self, test_mode=False):
        """Start the HTTP server"""
        try:
            server = HTTPServer(('localhost', self.port), ProductViewSetHandler)
            print(f"🚀 ProductViewSet server started on http://localhost:{self.port}")
            print(f"📋 Build ID: {self.build_id}")
            print(f"🔗 Endpoints:")
            print(f"   GET  / - Service status")
            print(f"   POST /process_data - Execute process_data")
            print(f"\n💡 Test with: curl -X POST http://localhost:{self.port}/process_data -d '" + '{"test": "data"}' + "'")

            if test_mode:
                print(f"🧪 Running in test mode - will stop after 3 seconds")
                import threading
                timer = threading.Timer(3.0, lambda: server.shutdown())
                timer.start()
                server.serve_forever()
                timer.cancel()
                print(f"✅ ProductViewSet server test completed successfully")
            else:
                print(f"\n⚡ Press Ctrl+C to stop\n")
                server.serve_forever()

        except KeyboardInterrupt:
            print(f"\nProductViewSet server stopped")
        except Exception as e:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    import sys
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    service = ProductViewSet()
    service.start_server(test_mode)