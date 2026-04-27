#!/usr/bin/env python3
"""
Digital Quiz Tool - Single File Runner
Run this file to start the entire application (backend + frontend build)
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("""
=============================================================

              DIGITAL QUIZ TOOL - EXAM PORTAL

=============================================================
    """)

def check_dependencies():
    """Check if required packages are installed."""
    print("[INFO] Checking dependencies...")
    required = ['flask', 'flask_login', 'flask_cors', 'werkzeug']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[MISSING] Missing packages: {', '.join(missing)}")
        print("[INSTALL] Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("[OK] Dependencies installed!\n")
    else:
        print("[OK] All dependencies ready!\n")

def setup_database():
    """Initialize the database."""
    print("[DB] Setting up database...")
    from database import init_db
    init_db()
    print("[OK] Database ready!\n")

def start_backend():
    """Start Flask backend server."""
    print("[START] Starting Backend Server...")
    print("   URL: http://127.0.0.1:5000")
    print("   API Docs: http://127.0.0.1:5000/api/\n")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'exam-portal-secret-key-2026'
    
    # Import and run app
    from app import app
    
    def run_server():
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    
    # Run in thread so we can do other things
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    print("[OK] Backend running!\n")

def start_cloudflare_tunnel():
    """Start cloudflare tunnel for public access."""
    print("[TUNNEL] Starting Cloudflare Tunnel (for public URL)...")
    print("   This creates a public URL for WhatsApp sharing\n")
    
    try:
        # Check if cloudflared is installed
        result = subprocess.run(
            ['cloudflared', 'version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("[WARN] Cloudflared not found. Public URL not available.")
            print("   Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
            print("   Or use the deployment guide for permanent hosting.\n")
            return None
        
        # Start tunnel
        tunnel_process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://127.0.0.1:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for URL
        public_url = None
        start_time = time.time()
        
        while time.time() - start_time < 30:  # Wait max 30 seconds
            line = tunnel_process.stdout.readline()
            if line:
                print(f"   {line.strip()}")
                # Extract URL from output
                if 'trycloudflare.com' in line:
                    import re
                    match = re.search(r'https://[^\s]+\.trycloudflare\.com', line)
                    if match:
                        public_url = match.group(0)
                        break
        
        if public_url:
            print(f"\n[OK] Public URL: {public_url}")
            print(f"   Share link will be: {public_url}/join/{{token}}\n")
            
            # Update admin.py with new URL
            update_share_url(public_url)
            
            return public_url
        else:
            print("[WARN] Tunnel started but couldn't extract URL\n")
            return None
            
    except FileNotFoundError:
        print("[WARN] Cloudflared not installed. Public URL not available.\n")
        return None
    except Exception as e:
        print(f"[WARN] Tunnel error: {e}\n")
        return None

def update_share_url(public_url):
    """Update the share URL in admin.py."""
    try:
        admin_file = Path(__file__).parent / 'admin.py'
        if admin_file.exists():
            content = admin_file.read_text()
            
            # Replace the public_url line
            import re
            new_content = re.sub(
                r"public_url\s*=\s*['\"][^'\"]*['\"]",
                f"public_url = '{public_url}'",
                content
            )
            
            if new_content != content:
                admin_file.write_text(new_content)
                print(f"[OK] Updated admin.py with new public URL\n")
    except Exception as e:
        print(f"[WARN] Could not update admin.py: {e}\n")

def open_browser():
    """Open browser to the application."""
    time.sleep(3)
    print("[BROWSER] Opening browser...")
    webbrowser.open('http://127.0.0.1:5000')
    print("[OK] Browser opened!\n")

def print_instructions(public_url=None):
    """Print usage instructions."""
    print("═" * 60)
    print("QUICK START GUIDE")
    print("═" * 60)
    print()
    print("1. OPEN IN BROWSER:")
    print(f"   Local:    http://127.0.0.1:5000")
    if public_url:
        print(f"   Public:   {public_url}")
    print()
    print("2. LOGIN CREDENTIALS:")
    print("   Username: tulasi")
    print("   Password: tulasi@2005")
    print()
    print("3. GENERATE SHARE LINK:")
    print("   - Login as admin")
    print("   - Go to Dashboard")
    print("   - Click 'Generate Shareable Link'")
    print("   - Copy and share via WhatsApp")
    print()
    print("4. STOP THE SERVER:")
    print("   Press Ctrl+C to stop")
    print()
    print("═" * 60)
    print()

def main():
    """Main entry point."""
    print_banner()
    
    try:
        # Step 1: Check dependencies
        check_dependencies()
        
        # Step 2: Setup database
        setup_database()
        
        # Step 3: Start backend
        start_backend()
        
        # Step 4: Start cloudflare tunnel (optional)
        public_url = start_cloudflare_tunnel()
        
        # Step 5: Print instructions
        print_instructions(public_url)
        
        # Step 6: Open browser
        open_browser()
        
        # Step 7: Keep running
        print("[RUNNING] Server is running. Press Ctrl+C to stop.\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Stopping server...")
        print("[OK] Server stopped. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
