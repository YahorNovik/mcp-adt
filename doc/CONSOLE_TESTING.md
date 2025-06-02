# Console Testing Guide for MCP ADT Server

This guide explains how to test the MCP ADT Server from the command line using different transport protocols.

## 🧪 Testing Overview

The MCP ADT Server supports three transport protocols, but they have different testing approaches:
- **STDIO**: Requires MCP client (difficult to test manually)
- **SSE**: Requires session management (complex for curl)
- **Streamable HTTP**: Requires specific headers and session handling

## ⚠️ Important Note

**Direct curl testing of SSE/HTTP transports DOES NOT WORK** due to MCP protocol complexity:
- Complex session management and initialization
- Specific headers and authentication requirements
- Event streaming protocols that require proper MCP client implementation

**Only working approach**: Use the automated test script or proper MCP clients (Cline, Claude Desktop).

---

## 🚀 Recommended Testing Method

### Automated Test Script

The easiest way to test the server is using the included test script:

```bash
# Test from any directory
python /path/to/mcp-adt/test_remote_connection.py
```

This script:
- ✅ Tests server startup from different directories
- ✅ Verifies STDIO transport communication
- ✅ Checks proper MCP protocol handling
- ✅ Provides clear success/failure feedback

---

## 🔧 Manual Testing (Advanced)

### STDIO Transport Testing

STDIO transport is the standard MCP protocol and requires proper MCP client communication:

```bash
# Start server
python mcp_server.py --transport stdio

# Test with echo (basic connectivity)
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | python mcp_server.py --transport stdio
```

### SSE Transport Testing

SSE requires session management and proper headers:

```bash
# Start SSE server
python mcp_server.py --transport sse
# Server starts on http://127.0.0.1:8000

# SSE requires session_id parameter
curl -H "Accept: text/event-stream" "http://127.0.0.1:8000/messages/?session_id=test123"
# Returns: session_id is required or Invalid session ID
```

**Note**: SSE transport requires proper session initialization through MCP client, not direct curl.

### Streamable HTTP Testing

Streamable HTTP requires specific headers and session handling:

```bash
# Start HTTP server
python mcp_server.py --transport streamable-http
# Server starts on http://127.0.0.1:8000

# Attempt basic connection (will fail due to missing requirements)
curl -X POST http://127.0.0.1:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
# Returns: Bad Request: Missing session ID
```

**Note**: HTTP transport requires session management that's handled by MCP clients, not manual curl.

---

## 🎯 Practical Testing Scenarios

### 1. Server Startup Test

```bash
# Test if server starts without errors
python mcp_server.py --transport stdio &
sleep 2
ps aux | grep mcp_server  # Linux/macOS
tasklist | findstr python  # Windows
kill %1  # Linux/macOS
```

### 2. Environment Configuration Test

```bash
# Test with different environment files
python mcp_server.py --env .env.example --transport stdio
python mcp_server.py --env btp_02.env --transport stdio
```

### 3. Remote Directory Test

```bash
# Test from different directory
cd /tmp  # Linux/macOS
cd %TEMP%  # Windows
python /full/path/to/mcp-adt/mcp_server.py --transport stdio
```

### 4. Port Availability Test

```bash
# Check if default port is available
netstat -an | grep :8000  # Linux/macOS
netstat -an | findstr :8000  # Windows

# Test different transports
python mcp_server.py --transport sse &
python mcp_server.py --transport streamable-http &
```

---

## 🔍 Troubleshooting Console Testing

### Common Issues

1. **"session_id is required"**
   - **Cause**: HTTP/SSE transports require session management
   - **Solution**: Use automated test script or proper MCP client

2. **"Not Acceptable: Client must accept..."**
   - **Cause**: Missing required headers
   - **Solution**: Add `Accept: application/json, text/event-stream`

3. **"Connection refused"**
   - **Cause**: Server not running or port conflict
   - **Solution**: Check server status and port availability

4. **"ModuleNotFoundError"**
   - **Cause**: Missing dependencies or wrong Python environment
   - **Solution**: Activate virtual environment and install requirements

### Debugging Commands

```bash
# Check server logs
tail -f mcp_server.log  # Linux/macOS
type mcp_server.log  # Windows

# Check process status
ps aux | grep mcp_server  # Linux/macOS
tasklist | findstr python  # Windows

# Check port usage
lsof -i :8000  # Linux/macOS
netstat -an | findstr :8000  # Windows

# Test Python environment
python -c "import mcp; print('MCP available')"
python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP available')"
```

---

## 📊 Testing Results Interpretation

### Success Indicators

- ✅ **Server starts**: No import errors, shows "Starting MCP ADT Server"
- ✅ **Port binding**: Shows "Uvicorn running on http://127.0.0.1:8000"
- ✅ **Environment loaded**: Shows "[+] Loaded environment from: ..."
- ✅ **Tools registered**: Debug logs show "Registering handler for..."

### Failure Indicators

- ❌ **Import errors**: Missing dependencies
- ❌ **Port conflicts**: "Address already in use"
- ❌ **Environment errors**: "Environment file not found"
- ❌ **SAP connection**: Check .env configuration

---

## 💡 Best Practices for Testing

1. **Use automated test script** for comprehensive testing
2. **Test STDIO transport** for production readiness
3. **Check logs** in `mcp_server.log` for detailed information
4. **Test from different directories** to verify remote connection fix
5. **Verify environment files** before testing SAP connectivity

---

## 🚀 Quick Test Commands

### Full Test Suite
```bash
# Complete automated test
python test_remote_connection.py

# Manual startup test
python mcp_server.py --transport stdio &
sleep 3
kill %1
```

### Environment Test
```bash
# Test environment loading
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
print('SAP_URL:', os.getenv('SAP_URL'))
print('SAP_AUTH_TYPE:', os.getenv('SAP_AUTH_TYPE'))
"
```

### Dependency Test
```bash
# Test all required imports
python -c "
try:
    from mcp.server.fastmcp import FastMCP
    from src.tools.search_objects import get_search_objects
    print('✅ All imports successful')
except ImportError as e:
    print('❌ Import error:', e)
"
```

---

## 📞 Support

If console testing fails:
1. Run the automated test script: `python test_remote_connection.py`
2. Check server logs: `mcp_server.log`
3. Verify environment: `.env` file configuration
4. Review [DEBUG_GUIDE.md](DEBUG_GUIDE.md) for detailed troubleshooting

**Remember**: For actual MCP communication, use proper MCP clients (Claude Desktop, Cline) rather than manual curl commands.
