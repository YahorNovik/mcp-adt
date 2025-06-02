# MCP ADT Server Quick Start

## Basic Usage

### 1. Run from project directory
```bash
cd mcp-adt
python mcp_server.py
```

### 2. Run from any directory (🆕)
```bash
python /full/path/to/mcp-adt/mcp_server.py
```

### 3. Run with custom environment file
```bash
python mcp_server.py --env btp_02.env
```

## Transport Options

The MCP ADT Server supports multiple transport protocols:

### STDIO Transport (Default)
- **Use case**: Standard MCP client connections (Claude Desktop, etc.)
- **Pros**: Standard MCP protocol, works with all MCP clients
- **Cons**: Harder to debug, binary communication

```bash
python mcp_server.py --transport stdio
# or simply:
python mcp_server.py
```

### SSE Transport
- **Use case**: Web-based MCP clients, browser integration
- **Pros**: Real-time streaming, web-compatible
- **Cons**: Requires web server setup

```bash
python mcp_server.py --transport sse
```

### Streamable HTTP Transport
- **Use case**: HTTP-based MCP clients, API integration
- **Pros**: HTTP-compatible, easy to integrate
- **Cons**: Less efficient than STDIO

```bash
python mcp_server.py --transport streamable-http
```

## MCP Client Configuration

### Cline (VSCode Extension) - SSE Transport

1. **Start the SSE server:**
   ```bash
   python mcp_server.py --transport sse
   # Server will start on http://127.0.0.1:8000
   ```

2. **Configure Cline MCP settings:**
   - Open VSCode
   - Go to Cline extension settings
   - Add MCP server configuration:
   ```json
   {
     "mcpServers": {
       "adt-server": {
         "url": "http://127.0.0.1:8000/messages/",
         "transport": "sse"
       }
     }
   }
   ```

3. **Alternative: Use Cline's MCP Server Manager:**
   - Open Cline chat
   - Click on "MCP" button
   - Add new server:
     - **Name**: `adt-server`
     - **URL**: `http://127.0.0.1:8000/messages/`
     - **Transport**: `SSE`

### Claude Desktop (Windows)
File: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "adt-server": {
      "command": "python",
      "args": ["C:/Users/username/projects/mcp-adt/mcp_server.py"],
      "env": {
        "PYTHONPATH": "C:/Users/username/projects/mcp-adt"
      }
    }
  }
}
```

### Claude Desktop (macOS/Linux)
File: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

## .env File Configuration

### For on-premise SAP systems
```ini
SAP_AUTH_TYPE=basic
SAP_URL=https://your-sap-system:443
SAP_CLIENT=100
SAP_USER=your_username
SAP_PASS=your_password
SAP_VERIFY_SSL=true
SAP_TIMEOUT=30
```

### For BTP systems
```ini
SAP_AUTH_TYPE=jwt
SAP_URL=https://your-system.abap.region.hana.ondemand.com
SAP_JWT_TOKEN=your_jwt_token_here
SAP_VERIFY_SSL=true
SAP_TIMEOUT=30
```

## Connection Testing

### Automated test
```bash
python /path/to/mcp-adt/test_remote_connection.py
```

### Manual test
```bash
# Start the server
python /path/to/mcp-adt/mcp_server.py

# Check logs
cat /path/to/mcp-adt/mcp_server.log
```

## Troubleshooting

### ❌ MCP error -32000: Connection closed
**Solution**: Use full path to mcp_server.py

### ❌ ModuleNotFoundError
**Solution**: 
```bash
cd /path/to/mcp-adt
pip install -r requirements.txt
```

### ❌ Environment file not found
**Solution**: Create `.env` file in mcp-adt directory

### ❌ SAP connection failed
**Solution**: Check settings in `.env` file

## Available Tools

- `get_program_source_mcp` - Get program source code
- `get_class_source_mcp` - Get class source code
- `get_function_source_mcp` - Get function source code
- `get_table_source_mcp` - Get table structure
- `get_table_contents_mcp` - Get table data
- `get_search_objects_mcp` - Search objects
- `get_usage_references_mcp` - Where-used analysis
- `get_sql_query_mcp` - Execute SQL query
- and others...

## Useful Links

- [Detailed documentation](../README.md)
- [Remote connection guide](REMOTE_CONNECTION_GUIDE.md)
- [Debug guide](DEBUG_GUIDE.md)
- [BTP integration](BTP_INTEGRATION_GUIDE.md)
- [Change history](CHANGELOG.md)

## Support

When encountering issues:
1. Run `test_remote_connection.py`
2. Check logs in `mcp_server.log`
3. Review [DEBUG_GUIDE.md](DEBUG_GUIDE.md)
