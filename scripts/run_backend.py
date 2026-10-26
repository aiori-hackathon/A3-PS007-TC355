#!/usr/bin/env python3
"""
Run Backend Server Script
Starts the Flask REST API on port 5000 with CORS and hot-reload.
"""
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app

def main():
    print("=" * 60)
    print("Starting PrivacyGuard IPv6 - Flask REST API Backend")
    print("=" * 60)
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Backend API listening on: http://127.0.0.1:{port}")
    print(f"Health endpoint:         http://127.0.0.1:{port}/api/health")
    print(f"Dashboard endpoint:      http://127.0.0.1:{port}/api/dashboard")
    print("Press Ctrl+C to stop the server.")
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()
