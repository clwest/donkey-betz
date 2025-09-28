#!/usr/bin/env python3
"""
🚀 START DJANGO WITH WEBSOCKET SUPPORT
Start the Django server properly with Daphne for WebSocket support
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required = ['django', 'channels', 'daphne', 'websockets']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print(f"Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        print("✅ Packages installed")
    else:
        print("✅ All required packages installed")

def start_with_daphne():
    """Start Django with Daphne for WebSocket support"""
    print("="*60)
    print("🚀 STARTING DJANGO WITH WEBSOCKET SUPPORT")
    print("="*60)
    
    # Check requirements
    check_requirements()
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
    
    print("\n📋 Configuration:")
    print("  • Server: Daphne ASGI")
    print("  • HTTP: http://localhost:8000")
    print("  • WebSocket: ws://localhost:8000/ws/*")
    print("  • Admin: http://localhost:8000/admin")
    print("  • API: http://localhost:8000/api/")
    
    print("\n🔌 Available WebSocket endpoints:")
    print("  • /ws/dashboard/ - Dashboard updates")
    print("  • /ws/agents/ - Agent monitoring")
    print("  • /ws/assistant/ - AI Assistant chat")
    print("  • /ws/notifications/ - System notifications")
    print("  • /ws/test/echo/ - Echo test endpoint")
    
    print("\n🚀 Starting Daphne...")
    print("-"*60)
    
    try:
        # Start Daphne
        subprocess.run([
            'daphne',
            '-b', '0.0.0.0',
            '-p', '8000',
            'ai_core.asgi:application'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user")
    except FileNotFoundError:
        print("\n❌ Daphne not found. Falling back to runserver...")
        print("   Note: WebSocket support will be limited")
        subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("\n" + "🚀"*20)
    print("UNIFIED DONKEY BETZ - WEBSOCKET SERVER")
    print("🚀"*20 + "\n")
    
    # Check if manage.py exists
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    start_with_daphne()

if __name__ == "__main__":
    main()
