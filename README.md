# ADT MCP Server

This repository provides a Model Context Protocol (MCP) server for ABAP Development Tools (ADT), exposing various ABAP repository-read tools (program, class, function, include, interface, structure, table, where-used, etc.) over a standardized MCP interface.

**🆕 Now includes SAP BTP (Business Technology Platform) support with JWT authentication and service key utilities!**

**📚 Quick Start**: See [QUICK_START.md](doc/QUICK_START.md) for immediate setup instructions.

**🔌 Client Connections**: See [MCP_CLIENT_CONNECTIONS.md](doc/MCP_CLIENT_CONNECTIONS.md) for connecting to Cline, Claude Desktop, and other MCP clients.

**📖 Documentation**: Complete documentation is available in the [doc/](doc/) folder.

---

## Prerequisites

* **Python 3.9+**
* **pip** (the Python package installer)
* A running SAP ABAP system with ADT services enabled
* A `.env` file in the project root with your SAP connection settings (see below)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-org>/<your-repo>.git
   cd <your-repo>
   ```

   **Note**: The MCP server can now be run from any directory, not just the project directory. See [REMOTE_CONNECTION_GUIDE.md](doc/REMOTE_CONNECTION_GUIDE.md) for details.

   **Transport Options**: The server supports multiple transport protocols: STDIO (default), SSE, and Streamable HTTP.

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   ```text
   pip install mcp "mcp[cli]"
   ```

   Then install:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example `.env.example` to `.env` and fill in your SAP credentials:

   ### For On-Premise Systems (Basic Authentication)
   ```ini
   SAP_AUTH_TYPE=basic
   SAP_URL=https://my.sap.system:443
   SAP_CLIENT=100
   SAP_USER=YOUR_USER
   SAP_PASS=YOUR_PASS
   SAP_VERIFY_SSL=true

   # Optional timeout configuration (in seconds)
   SAP_TIMEOUT_DEFAULT=45                 # Default timeout (45 seconds)
   SAP_TIMEOUT_CSRF=15                    # CSRF token timeout (15 seconds)
   SAP_TIMEOUT_LONG=60                    # Long operations timeout (60 seconds)
   ```

   ### For BTP Systems (JWT Authentication)
   ```ini
   SAP_AUTH_TYPE=jwt
   SAP_URL=https://your-system.abap.region.hana.ondemand.com
   SAP_JWT_TOKEN=eyJhbGciOiJSUzI1NiIsImp...
   SAP_VERIFY_SSL=true

   # Optional timeout configuration (in seconds)
   SAP_TIMEOUT_DEFAULT=45                 # Default timeout (45 seconds)
   SAP_TIMEOUT_CSRF=15                    # CSRF token timeout (15 seconds)
   SAP_TIMEOUT_LONG=60                    # Long operations timeout (60 seconds)
   ```

   **💡 Tip**: Use the included BTP utilities to generate .env files from service keys automatically!

## 🚀 BTP Integration

This server now includes comprehensive SAP BTP support with:

- **JWT Token Authentication** for BTP ABAP systems
- **Service Key Parsing** and analysis
- **Automatic .env Generation** from BTP service keys
- **CLI Utility** for easy configuration management

### Quick BTP Setup

1. **Download your service key** from BTP cockpit
2. **Generate .env file** using the CLI utility:
   ```bash
   python btp_env_generator.py --service-key service-key.json --username your-user@company.com --prompt-password
   ```
3. **Use the generated .env file** in your project

For complete BTP integration details, see [BTP_INTEGRATION_GUIDE.md](doc/BTP_INTEGRATION_GUIDE.md).

### Available Tools

#### ABAP Repository Tools
* `get_program_source_mcp` – Retrieve ABAP program source
* `get_class_source_mcp` – Retrieve ABAP class source
* `get_function_group_source_mcp` – Retrieve function group source
* `get_function_source_mcp` – Retrieve function module source
* `get_include_source_mcp` – Retrieve include source
* `get_interface_source_mcp` – Retrieve interface source
* `get_structure_source_mcp` – Retrieve structure definition
* `get_table_source_mcp` – Retrieve table definition
* `get_table_contents_mcp` – Fetch table data (max rows default 100)
* `get_package_structure_mcp` – Retrieve package metadata
* `get_type_info_mcp` – Retrieve type information
* `get_transaction_properties_mcp` – Retrieve transaction properties
* `get_search_objects_mcp` – Quick search for repository objects
* `get_usage_references_mcp` – Retrieve where‑used references for any object
* `get_cds_source_mcp` – Retrieve CDS view source
* `get_metadata_extension_source_mcp` – Retrieve metadata extension source
* `get_sql_query_mcp` – Execute freestyle SQL queries
* `get_enhancements_mcp` – Discover enhancement implementations

#### 🆕 BTP Tools
* `generate_env_from_service_key_file_mcp` – Generate .env from service key file
* `generate_env_from_service_key_json_mcp` – Generate .env from service key JSON
* `parse_btp_service_key_mcp` – Parse and analyze service keys
* `get_btp_connection_status_mcp` – Check current BTP configuration

## Troubleshooting

### "MCP error -32000: Connection closed" Error

If you get this error when connecting from another directory:

1. **Make sure you use the full path to the server:**
   ```bash
   python /full/path/to/mcp-adt/mcp_server.py
   ```

2. **Check MCP client configuration:**
   ```json
   {
     "mcpServers": {
       "adt-server": {
         "command": "python",
         "args": ["/full/path/to/mcp-adt/mcp_server.py"]
       }
     }
   }
   ```

3. **Run connection test:**
   ```bash
   python /path/to/mcp-adt/test_remote_connection.py
   ```

4. **Check logs:**
   - Log file is created in project directory: `mcp_server.log`
   - Check for import or configuration errors

### Other Common Issues

- **ModuleNotFoundError**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **.env file issues**: File is automatically searched in project directory
- **Permission issues**: On Linux/macOS you may need `chmod +x mcp_server.py`

For detailed information see [REMOTE_CONNECTION_GUIDE.md](doc/REMOTE_CONNECTION_GUIDE.md)

## License

[MIT](LICENSE)
