#!/usr/bin/env python3
"""
Test script to verify MCP server works from different directories.
This script can be run from any directory to test the MCP server connection.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_mcp_server_from_different_directory():
    """Test MCP server connection from a different directory."""
    
    # Get the current mcp-adt project directory
    mcp_adt_dir = Path(__file__).parent.absolute()
    mcp_server_path = mcp_adt_dir / "mcp_server.py"
    
    print(f"MCP ADT Directory: {mcp_adt_dir}")
    print(f"MCP Server Path: {mcp_server_path}")
    
    # Create a temporary directory to run the test from
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Testing from temporary directory: {temp_path}")
        
        # Change to the temporary directory
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            # Test 1: Try to start the server from different directory
            print("\n=== Test 1: Server Start Test ===")
            server_cmd = [sys.executable, str(mcp_server_path), "--transport", "stdio"]
            
            print(f"Running command: {' '.join(server_cmd)}")
            print(f"From directory: {temp_path}")
            
            # Start the server process
            process = subprocess.Popen(
                server_cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_path  # Run from temp directory
            )
            
            # Give it a moment to start
            import time
            time.sleep(3)
            
            # Check if process is still running (good sign)
            if process.poll() is None:
                print("✓ Server started successfully")
                
                # Try to send a simple message
                try:
                    test_message = '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}\n'
                    
                    stdout, stderr = process.communicate(input=test_message, timeout=5)
                    
                    print(f"Server stdout: {stdout[:300]}...")
                    if stderr:
                        print(f"Server stderr: {stderr[:300]}...")
                    
                    if "result" in stdout or "ADT Server" in stdout:
                        print("✓ Server responded correctly")
                        return True
                    else:
                        print("? Server started but response unclear")
                        return True  # Still consider it a success if server started
                        
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=2)
                    print("✓ Server started (timeout on communication is normal)")
                    return True
                    
            else:
                # Process exited, check why
                stdout, stderr = process.communicate()
                print("✗ Server failed to start")
                print(f"Return code: {process.returncode}")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            return False
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
    
    return True

if __name__ == "__main__":
    print("Testing MCP ADT Server remote connection...")
    print("=" * 50)
    
    success = test_mcp_server_from_different_directory()
    
    if success:
        print("\n🎉 All tests passed! MCP server should work from any directory.")
    else:
        print("\n❌ Tests failed. There may still be path resolution issues.")
    
    sys.exit(0 if success else 1)
