#!/usr/bin/env python3
"""
Comprehensive test script for MCP ADT Server
"""

import json
import subprocess
import sys
import time
import os

class MCPTester:
    def __init__(self, server_script="mcp_server.py", env_file=None):
        self.server_script = server_script
        self.env_file = env_file
        self.process = None
        self.request_id = 1
    
    def start_server(self):
        """Start the MCP server"""
        cmd = [sys.executable, self.server_script]
        if self.env_file:
            cmd.extend(['--env', self.env_file])
        
        print(f"🚀 Starting server: {' '.join(cmd)}")
        
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        time.sleep(2)  # Wait for server to start
        
        if self.process.poll() is not None:
            stderr = self.process.stderr.read()
            raise RuntimeError(f"Server failed to start. Error: {stderr}")
        
        print("✅ Server started successfully")
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.process:
            try:
                # Send shutdown request
                shutdown_request = {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "method": "shutdown"
                }
                self.send_request_raw(shutdown_request)
                
                # Close pipes
                if self.process.stdin:
                    self.process.stdin.close()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()
                
                # Terminate process
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
                self.process.wait()
            
            print("🛑 Server stopped")
    
    def send_request_raw(self, request):
        """Send a raw request without waiting for response"""
        if not self.process:
            raise RuntimeError("Server not started")
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
    
    def send_request(self, method, params=None, timeout=10.0):
        """Send a request and wait for response"""
        if not self.process:
            raise RuntimeError("Server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        self.request_id += 1
        
        request_json = json.dumps(request) + "\n"
        print(f"📤 {method}: {request_json.strip()}")
        
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                raise RuntimeError(f"Server terminated unexpectedly. Error: {stderr}")
            
            response_line = self.process.stdout.readline()
            if response_line:
                print(f"📥 Response: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    return response
                except json.JSONDecodeError as e:
                    raise RuntimeError(f"Invalid JSON response: {response_line}. Error: {e}")
            
            time.sleep(0.1)
        
        raise RuntimeError(f"Timeout waiting for {method} response")
    
    def test_initialize(self):
        """Test server initialization"""
        print("\n🔧 Testing initialization...")
        
        response = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "comprehensive-test-client", "version": "1.0.0"}
        })
        
        if "error" in response:
            raise RuntimeError(f"Initialization failed: {response['error']}")
        
        result = response.get("result", {})
        server_info = result.get("serverInfo", {})
        capabilities = result.get("capabilities", {})
        
        print(f"✅ Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
        print(f"✅ Protocol: {result.get('protocolVersion', 'Unknown')}")
        print(f"✅ Capabilities: {list(capabilities.keys())}")
        
        return result
    
    def test_tools_list(self):
        """Test tools listing"""
        print("\n🛠️ Testing tools list...")
        
        response = self.send_request("tools/list")
        
        if "error" in response:
            raise RuntimeError(f"Tools list failed: {response['error']}")
        
        tools = response.get("result", {}).get("tools", [])
        print(f"✅ Found {len(tools)} tools:")
        
        tool_names = []
        for tool in tools:
            name = tool.get("name", "Unknown")
            description = tool.get("description", "No description")
            tool_names.append(name)
            print(f"  • {name}: {description[:80]}{'...' if len(description) > 80 else ''}")
        
        return tool_names
    
    def test_btp_connection_status(self):
        """Test BTP connection status tool"""
        print("\n🔗 Testing BTP connection status...")
        
        try:
            response = self.send_request("tools/call", {
                "name": "get_btp_connection_status_mcp"
            })
            
            if "error" in response:
                print(f"⚠️ BTP connection status failed: {response['error']}")
                return False
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content:
                text_content = content[0].get("text", "")
                print(f"✅ BTP Status: {text_content[:100]}{'...' if len(text_content) > 100 else ''}")
            else:
                print("✅ BTP connection status tool executed successfully")
            
            return True
            
        except Exception as e:
            print(f"⚠️ BTP connection test failed: {e}")
            return False
    
    def test_search_objects(self):
        """Test ABAP object search"""
        print("\n🔍 Testing ABAP object search...")
        
        try:
            response = self.send_request("tools/call", {
                "name": "get_search_objects_mcp",
                "arguments": {
                    "query": "CL_*",
                    "max_results": 3
                }
            })
            
            if "error" in response:
                print(f"⚠️ Search objects failed: {response['error']}")
                return False
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content:
                text_content = content[0].get("text", "")
                print(f"✅ Search results: {text_content[:200]}{'...' if len(text_content) > 200 else ''}")
            else:
                print("✅ Search objects tool executed successfully")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Search objects test failed: {e}")
            return False
    
    def test_sql_query(self):
        """Test SQL query functionality"""
        print("\n💾 Testing SQL query...")
        
        try:
            response = self.send_request("tools/call", {
                "name": "get_sql_query_mcp",
                "arguments": {
                    "sql_query": "SELECT TOP 1 * FROM T000",
                    "max_rows": 1
                }
            })
            
            if "error" in response:
                print(f"⚠️ SQL query failed: {response['error']}")
                return False
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content:
                text_content = content[0].get("text", "")
                print(f"✅ SQL query results: {text_content[:200]}{'...' if len(text_content) > 200 else ''}")
            else:
                print("✅ SQL query tool executed successfully")
            
            return True
            
        except Exception as e:
            print(f"⚠️ SQL query test failed: {e}")
            return False

def main():
    """Main test function"""
    print("🧪 Comprehensive MCP ADT Server Test")
    print("=" * 50)
    
    tester = MCPTester()
    test_results = {}
    
    try:
        # Start server
        tester.start_server()
        
        # Run tests
        print("\n📋 Running test suite...")
        
        # Test 1: Initialize
        try:
            tester.test_initialize()
            test_results["initialize"] = True
        except Exception as e:
            print(f"❌ Initialize test failed: {e}")
            test_results["initialize"] = False
        
        # Test 2: Tools list
        try:
            tools = tester.test_tools_list()
            test_results["tools_list"] = True
            
            # Check for expected tools
            expected_tools = [
                "get_btp_connection_status_mcp",
                "get_search_objects_mcp",
                "get_sql_query_mcp",
                "get_program_source_mcp",
                "get_class_source_mcp"
            ]
            
            missing_tools = [tool for tool in expected_tools if tool not in tools]
            if missing_tools:
                print(f"⚠️ Missing expected tools: {missing_tools}")
            else:
                print("✅ All expected tools found")
                
        except Exception as e:
            print(f"❌ Tools list test failed: {e}")
            test_results["tools_list"] = False
        
        # Test 3: BTP connection status
        test_results["btp_status"] = tester.test_btp_connection_status()
        
        # Test 4: Search objects
        test_results["search_objects"] = tester.test_search_objects()
        
        # Test 5: SQL query
        test_results["sql_query"] = tester.test_sql_query()
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1
    
    finally:
        tester.stop_server()
    
    # Print results
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Server is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Server may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
