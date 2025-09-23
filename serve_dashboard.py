#!/usr/bin/env python3
"""
Simple HTTP server to serve the AI-proof jobs learning dashboard
This ensures the dashboard stays live and accessible for recording
"""

import os
import sys
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from pathlib import Path

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/donkeyking/development/unified-donkey-betz", **kwargs)

    def end_headers(self):
        # Add CORS headers for API access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_dashboard_server(port=8080):
    """Start the dashboard server"""
    print(f"🚀 Starting AI-Proof Jobs Learning Dashboard Server on port {port}")
    print(f"📊 Dashboard URL: http://localhost:{port}/ai_proof_jobs_learning_dashboard.html")
    print(f"🔴 READY FOR RECORDING!")
    print("-" * 60)

    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"✅ Server running at http://localhost:{port}/")
            print(f"🎬 Navigate to: http://localhost:{port}/ai_proof_jobs_learning_dashboard.html")
            print("\nPress Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_dashboard_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir("/Users/donkeyking/development/unified-donkey-betz")

    # Check if Django server is running
    django_running = False
    try:
        import requests
        response = requests.get("http://localhost:8001/api/learning/dashboard/", timeout=2)
        if response.status_code == 200:
            django_running = True
            print("✅ Django API server detected on port 8001")
    except:
        print("⚠️  Django API server not detected - dashboard will use simulation mode")

    print(f"🧠 Learning data backup: /tmp/learning_data_backup.rdb")
    print(f"💾 Redis data: {'LIVE' if django_running else 'SIMULATED'}")

    start_dashboard_server()