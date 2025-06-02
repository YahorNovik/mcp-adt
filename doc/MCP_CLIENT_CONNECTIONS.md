# MCP Client Connection Guide

This guide explains how to connect the MCP ADT Server to different MCP clients using various transport protocols.

## 🔌 Connection Overview

The MCP ADT Server supports three transport protocols:
- **STDIO**: Standard MCP protocol (Claude Desktop, most MCP clients)
- **SSE**: Server-Sent Events (Cline, web-based clients)
- **Streamable HTTP**: HTTP streaming (custom integrations)

---

## 🎯 Cline (VSCode Extension)

### Method 1: SSE Transport (Recommended)

1. **Start the SSE server:**
   ```bash
   python mcp_server.py --transport sse
   ```
   Server will start on: `http://127.0.0.1:8000`

2. **Configure in Cline:**
   
   **Option A: Using Cline UI (Recommended)**
   - Open VSCode with Cline extension
   - Open Cline chat panel
   - Click the "MCP" button (gear icon)
   - Click "Add Server"
   - Fill in:
     - **Server Name**: `mcp-adt-python-sse`
     - **URL**: `http://127.0.0.1:8000/sse`
     - **Transport Type**: `SSE`
   
   **Option B: Direct Configuration File**
   - Edit Cline MCP settings file
   - Add the following configuration:
   ```json
   {
     "mcp-adt-python-sse": {
       "autoApprove": [],
       "disabled": false,
       "timeout": 60,
       "url": "http://127.0.0.1:8000/sse",
       "transportType": "sse"
     }
   }
   ```

3. **Verify connection:**
   - Cline should show "Connected" status
   - Try asking: "What tools are available?"

### Method 2: STDIO Transport (Alternative)

1. **Configure Cline settings:**
   - Open VSCode Settings
   - Search for "Cline MCP"
   - Add server configuration:
   ```json
   {
     "mcpServers": {
       "adt-server": {
         "command": "python",
         "args": ["/full/path/to/mcp-adt/mcp_server.py"],
         "cwd": "/full/path/to/mcp-adt"
       }
     }
   }
   ```

---

## 🤖 Claude Desktop

### STDIO Transport (Standard)

1. **Locate configuration file:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add server configuration:**
   ```json
   {
     "mcpServers": {
       "adt-server": {
         "command": "python",
         "args": ["/full/path/to/mcp-adt/mcp_server.py"],
         "env": {
           "PYTHONPATH": "/full/path/to/mcp-adt"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

---

## 🌐 Web-based MCP Clients

### SSE Transport

1. **Start SSE server:**
   ```bash
   python mcp_server.py --transport sse
   ```

2. **Connect from web client:**
   - **Endpoint**: `http://127.0.0.1:8000/sse`
   - **Protocol**: Server-Sent Events
   - **Content-Type**: `text/event-stream`

3. **Example JavaScript connection:**
   ```javascript
   const eventSource = new EventSource('http://127.0.0.1:8000/sse');
   
   eventSource.onmessage = function(event) {
     const data = JSON.parse(event.data);
     console.log('Received:', data);
   };
   ```

---

## 🔧 Custom Integrations

### Streamable HTTP Transport

1. **Start HTTP server:**
   ```bash
   python mcp_server.py --transport streamable-http
   ```

2. **HTTP endpoints available:**
   - Base URL: `http://127.0.0.1:8000`
   - Protocol: HTTP streaming
   - Content-Type: `application/json`

3. **Note about HTTP testing:**
   ```bash
   # ⚠️ Direct curl testing doesn't work due to MCP protocol complexity
   # Requires session management and proper MCP client implementation
   # Use proper MCP clients instead of manual HTTP requests
   ```

---

## 🚀 Quick Setup Scripts

### For Cline Users

Create `start-for-cline.bat` (Windows) or `start-for-cline.sh` (Linux/macOS):

**Windows:**
```batch
@echo off
echo Starting MCP ADT Server for Cline...
cd /d "%~dp0"
.venv\Scripts\python.exe mcp_server.py --transport sse
pause
```

**Linux/macOS:**
```bash
#!/bin/bash
echo "Starting MCP ADT Server for Cline..."
cd "$(dirname "$0")"
.venv/bin/python mcp_server.py --transport sse
```

### For Claude Desktop Users

Create `start-for-claude.bat` (Windows) or `start-for-claude.sh` (Linux/macOS):

**Windows:**
```batch
@echo off
echo Starting MCP ADT Server for Claude Desktop...
cd /d "%~dp0"
.venv\Scripts\python.exe mcp_server.py --transport stdio
pause
```

**Linux/macOS:**
```bash
#!/bin/bash
echo "Starting MCP ADT Server for Claude Desktop..."
cd "$(dirname "$0")"
.venv/bin/python mcp_server.py --transport stdio
```

---

## 🔍 Troubleshooting

### Cline Connection Issues

1. **Server not starting:**
   ```bash
   # Check if port 8000 is available
   netstat -an | findstr :8000  # Windows
   lsof -i :8000               # Linux/macOS
   ```

2. **Connection refused:**
   - Ensure server is running: `python mcp_server.py --transport sse`
   - Check firewall settings
   - Verify URL: `http://127.0.0.1:8000/sse`

3. **Tools not appearing:**
   - Check Cline MCP status indicator
   - Restart Cline extension
   - Check server logs in `mcp_server.log`

### Claude Desktop Issues

1. **Server not recognized:**
   - Verify JSON syntax in config file
   - Use full absolute paths
   - Restart Claude Desktop

2. **Import errors:**
   - Check Python virtual environment
   - Verify `PYTHONPATH` in configuration
   - Install dependencies: `pip install -r requirements.txt`

### General Issues

1. **Environment file not found:**
   ```bash
   # Create .env file in project directory
   cp .env.example .env
   # Edit with your SAP credentials
   ```

2. **SAP connection failed:**
   - Verify SAP system accessibility
   - Check credentials in `.env` file
   - Test with: `python test_remote_connection.py`

---

## 📊 Transport Comparison

| Feature | STDIO | SSE | Streamable HTTP |
|---------|-------|-----|-----------------|
| **Claude Desktop** | ✅ Native | ❌ Not supported | ❌ Not supported |
| **Cline** | ✅ Supported | ✅ Recommended | ✅ Supported |
| **Web Clients** | ❌ Not compatible | ✅ Native | ✅ Compatible |
| **Custom Apps** | ⚠️ Complex | ✅ Easy | ✅ Easy |
| **Debugging** | ❌ Difficult | ✅ Easy | ✅ Easy |
| **Performance** | ✅ Fastest | ✅ Good | ✅ Good |

---

## 💡 Best Practices

1. **For Production**: Use STDIO transport with Claude Desktop
2. **For Development**: Use SSE transport with Cline for easier debugging
3. **For Testing**: Use automated test script (`python test_remote_connection.py`)
4. **Security**: Only expose servers on localhost (127.0.0.1)
5. **Monitoring**: Always check `mcp_server.log` for issues

⚠️ **Important**: Direct curl testing of SSE/HTTP transports doesn't work due to MCP protocol complexity. Use proper MCP clients or the automated test script.

---

## 📞 Support

If you encounter issues:
1. Check the transport-specific troubleshooting section above
2. Review logs in `mcp_server.log`
3. Run connection test: `python test_remote_connection.py`
4. For console testing: [CONSOLE_TESTING.md](CONSOLE_TESTING.md)
5. Consult [DEBUG_GUIDE.md](DEBUG_GUIDE.md) for detailed debugging
