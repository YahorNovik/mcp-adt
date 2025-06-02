#!/usr/bin/env python3
"""
SAP BTP Browser Authentication Utility

This script opens a browser for SAP BTP authentication and extracts JWT tokens
from the browser session, ported from the original Node.js version.

Usage:
    python sap_btp_browser_auth.py auth --key sk.json
    python sap_btp_browser_auth.py auth --key sk.json --browser chrome
"""

import argparse
import json
import sys
import time
import webbrowser
import http.server
import threading
import urllib.parse
import urllib.request
import base64
import os
import subprocess
import shutil
from tools.btp_utils import parse_service_key_file, BtpServiceKey


def find_browser_executable(browser_name: str) -> str:
    """
    Find browser executable path across different platforms.
    
    Args:
        browser_name: Name of browser ('chrome', 'edge', 'firefox')
        
    Returns:
        Path to browser executable or None if not found
    """
    browser_paths = {
        'chrome': {
            'nt': [  # Windows
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe',
                r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe',
                r'%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe'
            ],
            'darwin': [  # macOS
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable'
            ],
            'posix': [  # Linux
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/snap/bin/chromium',
                '/usr/local/bin/chrome'
            ]
        },
        'edge': {
            'nt': [  # Windows
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                r'%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe',
                r'%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe',
                r'%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe'
            ],
            'darwin': [  # macOS
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
            ],
            'posix': [  # Linux
                '/usr/bin/microsoft-edge',
                '/usr/bin/microsoft-edge-stable',
                '/usr/bin/microsoft-edge-beta',
                '/usr/bin/microsoft-edge-dev'
            ]
        },
        'firefox': {
            'nt': [  # Windows
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
                r'%LOCALAPPDATA%\Mozilla Firefox\firefox.exe',
                r'%PROGRAMFILES%\Mozilla Firefox\firefox.exe',
                r'%PROGRAMFILES(X86)%\Mozilla Firefox\firefox.exe'
            ],
            'darwin': [  # macOS
                '/Applications/Firefox.app/Contents/MacOS/firefox'
            ],
            'posix': [  # Linux
                '/usr/bin/firefox',
                '/usr/bin/firefox-esr',
                '/snap/bin/firefox',
                '/usr/local/bin/firefox'
            ]
        }
    }
    
    os_name = os.name
    if os_name not in browser_paths.get(browser_name, {}):
        return None
    
    paths_to_check = browser_paths[browser_name][os_name]
    
    for path in paths_to_check:
        # Expand environment variables on Windows
        if os_name == 'nt':
            expanded_path = os.path.expandvars(path)
        else:
            expanded_path = path
            
        if os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK):
            return expanded_path
    
    # Try using 'which' command on Unix-like systems
    if os_name != 'nt':
        try:
            result = subprocess.run(['which', browser_name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # Try using shutil.which as a last resort
    return shutil.which(browser_name)


def open_browser_with_subprocess(browser_path: str, url: str) -> bool:
    """
    Open browser using subprocess for reliable cross-platform support.
    
    Args:
        browser_path: Path to browser executable
        url: URL to open
        
    Returns:
        True if browser opened successfully, False otherwise
    """
    try:
        # Different arguments for different operating systems
        if os.name == 'nt':  # Windows
            subprocess.Popen([browser_path, url], shell=False)
        else:  # macOS and Linux
            subprocess.Popen([browser_path, url])
        return True
    except Exception as e:
        print(f"   ⚠️ Failed to launch browser with subprocess: {e}")
        return False


def open_browser_robust(url: str, preferred_browser: str = None) -> bool:
    """
    Robust cross-platform browser opening with multiple fallback methods.
    
    Args:
        url: URL to open
        preferred_browser: Preferred browser ('chrome', 'edge', 'firefox', 'system') or None
        
    Returns:
        True if browser opened successfully, False otherwise
    """
    if preferred_browser is None:
        # No browser specified - don't try to open any browser
        return False
        
    print(f"🌐 Attempting to open browser: {preferred_browser}")

    # Method 1: Try direct executable path for specific browsers
    if preferred_browser != "system":
        print(f"   Method 1: Looking for {preferred_browser} executable...")
        browser_path = find_browser_executable(preferred_browser)
        if browser_path:
            print(f"   Found {preferred_browser} at: {browser_path}")
            if open_browser_with_subprocess(browser_path, url):
                print(f"✅ Successfully opened {preferred_browser}")
                return True
        else:
            print(f"   {preferred_browser} executable not found")
    
    # Method 2: Try webbrowser module with specific browser names
    if preferred_browser != "system":
        print(f"   Method 2: Trying webbrowser module for {preferred_browser}...")
        browser_names = {
            'chrome': ['chrome', 'google-chrome', 'chromium'],
            'edge': ['edge', 'microsoft-edge'],
            'firefox': ['firefox', 'mozilla']
        }
        
        for browser_name in browser_names.get(preferred_browser, []):
            try:
                browser_obj = webbrowser.get(browser_name)
                browser_obj.open(url, new=2)
                print(f"✅ Successfully opened {browser_name} via webbrowser module")
                return True
            except webbrowser.Error:
                print(f"   Failed to get {browser_name} via webbrowser module")
                continue
    
    # Method 3: Try system default browser with webbrowser module (only if preferred_browser is "system")
    if preferred_browser == "system":
        print("   Method 3: Trying system default browser via webbrowser module...")
        try:
            webbrowser.open(url, new=2)
            print("✅ Successfully opened system default browser")
            return True
        except Exception as e:
            print(f"   Failed to open default browser: {e}")
    
    # Method 4: Platform-specific fallback commands (only if preferred_browser is "system")
    if preferred_browser == "system":
        print("   Method 4: Trying platform-specific commands...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', url], shell=True)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', url])
            else:  # Linux and other Unix-like systems
                subprocess.Popen(['xdg-open', url])
            print("✅ Successfully opened browser via platform-specific command")
            return True
        except Exception as e:
            print(f"   Platform-specific command failed: {e}")
    
    print("❌ All browser opening methods failed")
    return False


class AuthCaptureHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth authorization code."""
    
    captured_code = None
    captured_token = None
    server_should_stop = False
    
    def do_GET(self):
        """Handle GET request - capture authorization code from redirect."""
        parsed_url = urllib.parse.urlparse(self.path)
        
        if parsed_url.path == '/callback':
            # Parse query parameters
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Check for authorization code in query parameters
            if 'code' in query_params:
                AuthCaptureHandler.captured_code = query_params['code'][0]
                print("Authorization code received")
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                success_html = '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>SAP BTP Authentication</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            text-align: center;
                            margin: 0;
                            padding: 50px 20px;
                            background: linear-gradient(135deg, #0070f3 0%, #00d4ff 100%);
                            color: white;
                            min-height: 100vh;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            border-radius: 20px;
                            padding: 40px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                            max-width: 500px;
                            width: 100%;
                        }
                        .success-icon {
                            font-size: 4rem;
                            margin-bottom: 20px;
                            color: #4ade80;
                            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                        }
                        h1 {
                            margin: 0 0 20px 0;
                            font-size: 2rem;
                            font-weight: 300;
                        }
                        p {
                            margin: 0;
                            font-size: 1.1rem;
                            opacity: 0.9;
                            line-height: 1.5;
                        }
                        .sap-logo {
                            margin-top: 30px;
                            font-weight: bold;
                            opacity: 0.7;
                            font-size: 0.9rem;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✓</div>
                        <h1>Authentication Successful!</h1>
                        <p>You have successfully authenticated with SAP BTP.</p>
                        <p>You can now close this browser window.</p>
                        <div class="sap-logo">SAP Business Technology Platform</div>
                    </div>
                </body>
                </html>
                '''
                self.wfile.write(success_html.encode('utf-8'))
                AuthCaptureHandler.server_should_stop = True
                return
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Error: Authorization code missing')
                AuthCaptureHandler.server_should_stop = True
                return
        
        # Default response
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def start_callback_server(port=3001):
    """Start local HTTP server to capture OAuth callback."""
    handler = AuthCaptureHandler
    
    try:
        httpd = http.server.HTTPServer(("localhost", port), handler)
        print(f"Authentication server started on port {port}")
        
        def serve_until_code():
            while not handler.server_should_stop:
                try:
                    httpd.timeout = 0.5  # Set timeout for handle_request
                    httpd.handle_request()
                except Exception:
                    if handler.server_should_stop:
                        break
                time.sleep(0.1)
        
        server_thread = threading.Thread(target=serve_until_code)
        server_thread.daemon = True
        server_thread.start()
        
        return httpd, server_thread
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            return start_callback_server(port + 1)
        raise


def build_auth_url(service_key: BtpServiceKey, redirect_uri: str) -> str:
    """Build OAuth authorization URL for SAP BTP."""
    # SAP BTP uses /oauth/authorize endpoint
    auth_url = service_key.oauth_url.rstrip('/') + '/oauth/authorize'
    
    params = {
        'client_id': service_key.client_id,
        'response_type': 'code',  # Authorization code flow
        'redirect_uri': redirect_uri
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{auth_url}?{query_string}"


def exchange_code_for_token(service_key: BtpServiceKey, code: str, redirect_uri: str) -> str:
    """Exchange authorization code for access token."""
    try:
        token_url = service_key.oauth_url.rstrip('/') + '/oauth/token'
        
        print(f"🔄 Exchanging authorization code for token...")
        print(f"   Token URL: {token_url}")
        print(f"   Redirect URI: {redirect_uri}")
        print(f"   Authorization code: {code[:20]}..." if len(code) > 20 else f"   Authorization code: {code}")
        
        # Prepare request data
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        # Create basic auth header
        auth_string = f"{service_key.client_id}:{service_key.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        print(f"   Client ID: {service_key.client_id}")
        print(f"   Making POST request to token endpoint...")
        
        # Prepare request
        req_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(
            token_url,
            data=req_data,
            headers={
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Make request with timeout
        print(f"   Sending request...")
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"   Response status: {response.getcode()}")
            response_text = response.read().decode('utf-8')
            print(f"   Response length: {len(response_text)} characters")
            response_data = json.loads(response_text)
            
        if 'access_token' in response_data:
            token_length = len(response_data['access_token'])
            print(f"✅ OAuth token received successfully! (Length: {token_length} chars)")
            return response_data['access_token']
        else:
            print(f"❌ Response does not contain access_token")
            print(f"   Available keys: {list(response_data.keys())}")
            raise ValueError("Response does not contain access_token")
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else 'No error body'
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(f"   Error body: {error_body}")
        raise
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error obtaining OAuth token: {e}")
        raise


def authenticate_with_browser(service_key: BtpServiceKey, browser: str = None, timeout: int = 300) -> str:
    """
    Authenticate with SAP BTP using browser and capture JWT token.
    
    Args:
        service_key: BTP service key instance
        browser: Browser to use (system, chrome, edge, firefox) or None to only show URL
        timeout: Timeout in seconds for authentication
        
    Returns:
        JWT access token
    """
    # Start local callback server
    httpd, server_thread = start_callback_server()
    server_port = httpd.server_address[1]
    redirect_uri = f"http://localhost:{server_port}/callback"
    
    try:
        # Build authorization URL
        auth_url = build_auth_url(service_key, redirect_uri)
        
        print("\n🔐 SAP BTP Browser Authentication")
        print("=" * 50)
        print(f"OAuth URL: {service_key.oauth_url}")
        print(f"Client ID: {service_key.client_id}")
        print(f"Redirect URI: {redirect_uri}")
        
        # Handle browser opening based on parameter
        if browser is None:
            # No browser parameter specified - only show URL for manual copying
            print("\n📋 Please manually copy and open this URL in your browser:")
            print(f"🔗 {auth_url}")
            print("\nThen complete the authentication process.")
        else:
            # Browser parameter specified - try to open browser
            print(f"\n📱 Opening browser ({browser}) for authentication...")
            
            # Use robust browser opening with multiple fallback methods
            browser_opened = open_browser_robust(auth_url, browser)
            
            if not browser_opened:
                print(f"⚠️  Could not open {browser} browser automatically")
                print(f"Please manually open this URL in your browser:")
                print(f"🔗 {auth_url}")
                print("\nThen complete the authentication process.")
        
        # Wait for authorization code capture
        start_time = time.time()
        while not AuthCaptureHandler.captured_code and (time.time() - start_time) < timeout:
            time.sleep(1)
            if time.time() - start_time > 30 and (time.time() - start_time) % 30 < 1:
                remaining = timeout - (time.time() - start_time)
                print(f"⏳ Still waiting for authentication... ({remaining:.0f}s remaining)")
        
        if AuthCaptureHandler.captured_code:
            print("✅ Authorization code captured. Exchanging for token...")
            # Exchange authorization code for access token
            token = exchange_code_for_token(service_key, AuthCaptureHandler.captured_code, redirect_uri)
            print(f"🎉 Token successfully obtained! Returning to main function...")
            return token
        else:
            raise TimeoutError(f"Authentication timed out after {timeout} seconds")
            
    finally:
        # Stop server properly
        print("🛑 Shutting down authentication server...")
        try:
            # Set stop flag first
            AuthCaptureHandler.server_should_stop = True
            print("   Stop flag set")
            
            # Make a dummy request to wake up the server from handle_request()
            try:
                dummy_req = urllib.request.Request(f"http://localhost:{server_port}/shutdown")
                urllib.request.urlopen(dummy_req, timeout=1)
            except:
                pass  # Expected to fail, just to wake up the server
            
            # Wait a bit for server to notice the stop flag
            time.sleep(0.5)
            
            # Forcefully close the server
            if hasattr(httpd, 'server_close'):
                print("   Calling httpd.server_close()")
                httpd.server_close()
            
            # Force thread termination
            if server_thread.is_alive():
                print("   Waiting for server thread to finish...")
                server_thread.join(timeout=1)
                if server_thread.is_alive():
                    print("   ⚠️ Server thread did not finish gracefully")
            
            print("✅ Server shutdown complete")
        except Exception as e:
            print(f"⚠️ Warning: Could not properly close server: {e}")
        
        # Reset handler state for next use
        AuthCaptureHandler.captured_code = None
        AuthCaptureHandler.server_should_stop = False


def update_env_file(updates, env_file_path=".env"):
    """Updates the .env file with new values, similar to the original JS version."""
    try:
        # Always remove the old .env file if it exists
        if os.path.exists(env_file_path):
            os.unlink(env_file_path)
        
        lines = []
        if updates.get('SAP_AUTH_TYPE') == 'jwt':
            # jwt: write only relevant params
            jwt_allowed = [
                'SAP_URL',
                'SAP_CLIENT', 
                'SAP_LANGUAGE',
                'TLS_REJECT_UNAUTHORIZED',
                'SAP_AUTH_TYPE',
                'SAP_JWT_TOKEN'
            ]
            for key in jwt_allowed:
                if updates.get(key):
                    lines.append(f"{key}={updates[key]}")
            
            lines.append("")
            lines.append("# For JWT authentication")
            lines.append("# SAP_USERNAME=your_username")
            lines.append("# SAP_PASSWORD=your_password")
        else:
            # basic: write only relevant params
            basic_allowed = [
                'SAP_URL',
                'SAP_CLIENT',
                'SAP_LANGUAGE', 
                'TLS_REJECT_UNAUTHORIZED',
                'SAP_AUTH_TYPE',
                'SAP_USERNAME',
                'SAP_PASSWORD'
            ]
            for key in basic_allowed:
                if updates.get(key):
                    lines.append(f"{key}={updates[key]}")
            
            lines.append("")
            lines.append("# For JWT authentication (not used for basic)")
            lines.append("# SAP_JWT_TOKEN=your_jwt_token_here")
        
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        
        print(".env file created successfully.")
        
    except Exception as e:
        print(f"Error updating .env file: {e}")
        sys.exit(1)


def generate_env_with_browser_auth(service_key_file: str, browser: str = "system", env_file_path: str = ".env"):
    """Generate .env file using browser authentication, following the original JS logic."""
    try:
        print("Starting authentication process...")
        
        # Parse service key
        service_key = parse_service_key_file(service_key_file)
        print("Service key read successfully.")
        
        # Validate required fields in service key (following original JS validation)
        abap_url = service_key.abap_endpoint
        if not abap_url:
            print("SAP_URL is missing in the service key. Please check your service key JSON file.")
            sys.exit(1)
        
        # Authenticate with browser
        print("🚀 Starting browser authentication...")
        token = authenticate_with_browser(service_key, browser)
        print(f"✅ Browser authentication completed! Token length: {len(token) if token else 0}")
        print("🔙 Returned from authenticate_with_browser function")
        
        if not token:
            print("JWT token was not obtained. Authentication failed.")
            sys.exit(1)
        
        print("📝 Preparing .env file updates...")
        # Collect all relevant parameters from service key (following original JS logic)
        env_updates = {
            'SAP_URL': abap_url,
            'TLS_REJECT_UNAUTHORIZED': '0',
            'SAP_AUTH_TYPE': 'jwt',
            'SAP_JWT_TOKEN': token
        }
        
        print("💾 Writing .env file...")
        # Optional: client (not available in our BtpServiceKey, but keeping structure)
        # Optional: language (not available in our BtpServiceKey, but keeping structure)
        
        update_env_file(env_updates, env_file_path)
        print("Authentication completed successfully!")
        print(f"📁 .env file created at: {env_file_path}")
        
        return env_file_path
        
    except Exception as e:
        print(f"Error during authentication: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="sap-abap-auth-browser",
        description="CLI utility for authentication in SAP BTP ABAP Environment (Steampunk) via browser.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth command
    auth_parser = subparsers.add_parser(
        'auth',
        help='Authenticate in SAP BTP ABAP Environment (Steampunk) via browser and update .env file (JWT)'
    )
    auth_parser.add_argument(
        '-k', '--key',
        required=True,
        help='Path to the service key file in JSON format'
    )
    auth_parser.add_argument(
        '-b', '--browser',
        choices=['chrome', 'edge', 'firefox', 'system'],
        default=None,
        help='Browser to open (chrome, edge, firefox, system). If not specified, only display URL for manual copying'
    )
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'auth':
        if not args.key:
            print("Service key file (--key) is required for authentication. Please provide a valid service key JSON file.")
            sys.exit(1)
        
        generate_env_with_browser_auth(
            service_key_file=args.key,
            browser=args.browser
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Unexpected error: {error}")
        sys.exit(1)
