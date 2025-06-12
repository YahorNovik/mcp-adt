import argparse
import logging
import os
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP  # Import FastMCP, the quickstart server base

destination_config = get_destination_config("S4HANA_E19")
print(destination_config)

# Add the project root to Python path to ensure imports work from any directory
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.tools.function_group_source import get_function_group_source
from src.tools.cds_source import get_cds_source
from src.tools.class_source import get_class_source
from src.tools.behavior_definition_source import get_behavior_definition_source
from src.tools.function_source import get_function_source
from src.tools.include_source import get_include_source
from src.tools.interface_source import get_interface_source
from src.tools.package_structure import get_package_structure
from src.tools.program_source import get_program_source
from src.tools.structure_source import get_structure_source
from src.tools.table_source import get_table_source
from src.tools.transaction_properties import get_transaction_properties
from src.tools.type_info import get_type_info
from src.tools.search_objects import get_search_objects
from src.tools.usage_references import get_usage_references
from src.tools.metadata_extension_source import get_metadata_extension_source
from src.tools.table_contents import get_table_contents
from src.tools.sql_query import get_sql_query
from src.tools.enhancements import get_enhancements
from src.tools.includes_list import get_includes_list
from src.tools.enhancement_by_name import get_enhancement_by_name
from src.tools.btp_tools import (
    generate_env_from_service_key_file,
    generate_env_from_service_key_json,
    parse_btp_service_key,
    get_btp_connection_status
)

from dotenv import load_dotenv

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="MCP ADT Server for SAP ABAP Development Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--env',
        default='.env',
        help='Path to environment file (default: .env)'
    )
    parser.add_argument(
        '--transport',
        default='stdio',
        choices=['stdio', 'sse', 'streamable-http'],
        help='Transport protocol (default: stdio)'
    )
    return parser.parse_args()

# Load environment variables from specified file
def load_environment(env_file_path):
    """Load environment variables from the specified file."""
    # If path is relative, make it relative to project root
    if not os.path.isabs(env_file_path):
        env_file_path = project_root / env_file_path
    
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
        print(f"[+] Loaded environment from: {env_file_path}")
    else:
        print(f"[!] Environment file not found: {env_file_path}")
        print("    Using system environment variables only")

# Setup logging
log_file_path = project_root / 'mcp_server.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path)
    ]
)
logger = logging.getLogger(__name__)

mcp = FastMCP("ADT Server")  # Initialize an MCP server instance with a descriptive name

@mcp.tool()
def get_function_group_source_mcp(function_group: str) -> list[str]:
    logger.info(f"[TOOL] get_function_group_source_mcp called with function_group: {function_group}")
    try:
        result = get_function_group_source(function_group)
        logger.info(f"[TOOL] get_function_group_source_mcp completed successfully - returned {len(result) if result else 0} lines")
        return result
    except Exception as e:
        logger.error(f"[ERROR] Error in get_function_group_source_mcp: {e}")
        raise

@mcp.tool()
def get_cds_source_mcp(cds_name: str) -> list[str]:
    return get_cds_source(cds_name)

@mcp.tool()
def get_class_source_mcp(class_name: str) -> list[str]:
   return get_class_source(class_name)

@mcp.tool()
def get_behavior_definition_source_mcp(behavior_name: str) -> list[str]:
    return get_behavior_definition_source(behavior_name)

@mcp.tool()
def get_function_source_mcp(function_group: str,function_name: str) -> list[str]:
    """ Tool: get_function_source
         Description:
           Retrieve source code lines for an ABAP function module via ADT,
           with XML and text fallback.
         Parameters (object):
           • function_group (string) - Function group name (e.g. ZFUNC_GROUP)
           • function_name  (string) - Function module name (e.g. ZFUNC_MODULE)
        Required:
           [ "function_group", "function_name" ]"""
    return get_function_source(function_group, function_name)
    

@mcp.tool()
def get_include_source_mcp(include_name: str)  -> list[str]:
    return get_include_source(include_name)

@mcp.tool()
def get_interface_source_mcp( interface_name: str) -> list[str]:
    return get_interface_source(interface_name)

@mcp.tool()
def get_package_structure_mcp(package_name: str) -> list[dict]:
    return get_package_structure(package_name)

@mcp.tool()
def get_metadata_extension_source_mcp(extension_name: str) -> list[str]:
    return get_metadata_extension_source(extension_name)

@mcp.tool()
def get_program_source_mcp( program_name: str) -> list[str]:
    return get_program_source(program_name)

@mcp.tool()
def get_search_objects_mcp(query: str, max_results: int = 10) -> list[dict]:
    return get_search_objects(query, max_results=max_results)

@mcp.tool()
def get_structure_source_mcp(structure_name: str) -> list[str]:
    return get_structure_source(structure_name)

@mcp.tool()
def get_table_source_mcp(table_name: str) -> list[str]:
    return get_table_source(table_name)

@mcp.tool()
def get_transaction_properties_mcp(transaction_name: str) -> dict:
    return get_transaction_properties(transaction_name)

@mcp.tool()
def get_type_info_mcp(type_name: str) -> list[str]:
    return get_type_info(type_name)

@mcp.tool()
def get_usage_references_mcp(object_type: str, object_name: str,function_group = None):
    """Tool: get_usage_references
       Description:
         Retrieve where-used references for an ABAP object
         (class, program, include, function_module, interface, table, structure).
         By default, it looks at the very first character of the source.
       Parameters (object):
         object_type (string):
         One of: 'class', 'program', 'include', 'function_module',
         'interface', 'table', 'structure'
        object_name (string):
          The ABAP object name, e.g. 'ZMY_CLASS'
        function_group (string):
          Function group name (required if object_type is 'function_module')
       Required: [ "object_type", "object_name" ]"""
    return get_usage_references(object_type, object_name, function_group)

@mcp.tool()
def get_table_contents_mcp(table_name: str, max_rows: int = 100) -> dict:
    """Tool: get_table_contents
       Description:
         Retrieve table contents via ADT Data Preview API with proper SQL generation.
       Parameters (object):
         table_name (string): Name of the ABAP table (e.g. 'T000')
         max_rows (integer): Maximum number of rows to retrieve (default: 100)
       Required: [ "table_name" ]"""
    return get_table_contents(table_name, max_rows)

@mcp.tool()
def get_sql_query_mcp(sql_query: str, max_rows: int = 100) -> dict:
    """Tool: get_sql_query
       Description:
         Execute freestyle SQL queries via SAP ADT Data Preview API.
       Parameters (object):
         sql_query (string): SQL query to execute (e.g. 'SELECT * FROM T000 WHERE MANDT = 100')
         max_rows (integer): Maximum number of rows to return (default: 100)
       Required: [ "sql_query" ]"""
    return get_sql_query(sql_query, max_rows)

@mcp.tool()
def get_includes_list_mcp(object_name: str, object_type: str) -> dict:
    """Tool: get_includes_list
       Description:
         📋 INCLUDE INVENTORY: Recursively discover and list ALL include files within an ABAP program or include. Performs code analysis to find include statements and builds a complete hierarchy. Use this when you need to understand the program structure or get a list of all includes (without their source code or enhancements).
       Parameters (object):
         object_name (string): Name of the ABAP program or include to analyze for nested includes
         object_type (string): Type of the ABAP object (program or include)
       Required: [ "object_name", "object_type" ]"""
    return get_includes_list(object_name, object_type)

@mcp.tool()
def get_enhancements_mcp(object_name: str, program: str = None, include_nested: bool = False) -> dict:
    """Tool: get_enhancements
       Description:
         🔍 ENHANCEMENT ANALYSIS: Retrieve and analyze enhancement implementations in ABAP programs, includes, or classes. Automatically detects object type and extracts enhancement source code. Use include_nested=true for COMPREHENSIVE RECURSIVE SEARCH across all nested includes.
       Parameters (object):
         object_name (string): Name of the ABAP program, include, or class (e.g. 'RM07DOCS' for program, 'RM07DOCS_F01' for include, 'CL_MY_CLASS' for class)
         program (string): Optional: For includes, manually specify the parent program name if automatic context detection fails (e.g., 'SAPMV45A')
         include_nested (boolean): ⭐ RECURSIVE ENHANCEMENT SEARCH: If true, performs comprehensive analysis - searches for enhancements in the main object AND all nested includes recursively. Perfect for complete enhancement audit of entire program hierarchy. Default is false (single object only).
       Required: [ "object_name" ]"""
    return get_enhancements(object_name, program, include_nested)

@mcp.tool()
def get_enhancement_by_name_mcp(enhancement_spot: str, enhancement_name: str) -> dict:
    """Tool: get_enhancement_by_name
       Description:
         📝 ENHANCEMENT BY NAME: Retrieve source code of a specific enhancement implementation by its name and enhancement spot. Use this when you know the exact enhancement spot and implementation name.
       Parameters (object):
         enhancement_spot (string): Name of the enhancement spot (e.g., 'enhoxhh')
         enhancement_name (string): Name of the specific enhancement implementation (e.g., 'zpartner_update_pai')
       Required: [ "enhancement_spot", "enhancement_name" ]"""
    return get_enhancement_by_name(enhancement_spot, enhancement_name)

@mcp.tool()
def generate_env_from_service_key_file_mcp(
    service_key_file: str,
    username: str,
    password: str,
    output_file: str = "btp_generated.env",
    use_jwt: bool = True,
    verify_ssl: bool = True,
    timeout: int = 30
) -> str:
    """Tool: generate_env_from_service_key_file
       Description:
         Generate .env configuration file from BTP service key file for SAP connection setup.
       Parameters (object):
         service_key_file (string): Path to the BTP service key JSON file
         username (string): BTP username for authentication
         password (string): BTP password for authentication
         output_file (string): Output .env file name (default: btp_generated.env)
         use_jwt (boolean): Use JWT authentication instead of basic auth (default: true)
         verify_ssl (boolean): Verify SSL certificates (default: true)
         timeout (integer): Request timeout in seconds (default: 30)
       Required: [ "service_key_file", "username", "password" ]"""
    return generate_env_from_service_key_file(
        service_key_file, username, password, output_file, use_jwt, verify_ssl, timeout
    )

@mcp.tool()
def generate_env_from_service_key_json_mcp(
    service_key_json: str,
    username: str,
    password: str,
    output_file: str = "btp_generated.env",
    use_jwt: bool = True,
    verify_ssl: bool = True,
    timeout: int = 30
) -> str:
    """Tool: generate_env_from_service_key_json
       Description:
         Generate .env configuration file from BTP service key JSON string for SAP connection setup.
       Parameters (object):
         service_key_json (string): BTP service key as JSON string
         username (string): BTP username for authentication
         password (string): BTP password for authentication
         output_file (string): Output .env file name (default: btp_generated.env)
         use_jwt (boolean): Use JWT authentication instead of basic auth (default: true)
         verify_ssl (boolean): Verify SSL certificates (default: true)
         timeout (integer): Request timeout in seconds (default: 30)
       Required: [ "service_key_json", "username", "password" ]"""
    return generate_env_from_service_key_json(
        service_key_json, username, password, output_file, use_jwt, verify_ssl, timeout
    )

@mcp.tool()
def parse_btp_service_key_mcp(service_key_input: str) -> str:
    """Tool: parse_btp_service_key
       Description:
         Parse and analyze a BTP service key to extract connection information.
       Parameters (object):
         service_key_input (string): Either a file path to service key JSON or the JSON string itself
       Required: [ "service_key_input" ]"""
    return parse_btp_service_key(service_key_input)

@mcp.tool()
def get_btp_connection_status_mcp() -> str:
    """Tool: get_btp_connection_status
       Description:
         Check current BTP connection configuration and authentication status.
       Parameters: None
       Required: []"""
    return get_btp_connection_status()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables from specified file
    load_environment(args.env)
    
    # Log server initialization
    logger.info("[INIT] Initializing MCP ADT Server")
    logger.info(f"[INIT] Transport: {args.transport}")
    logger.info(f"[INIT] Environment file: {args.env}")
    
    # FastMCP doesn't expose _tools directly, so we'll log this after startup
    logger.info("[INIT] Server configured with all tools")
    
    # Run the MCP server
    print(f"[*] Starting MCP ADT Server with transport: {args.transport}")
    logger.info("[INIT] Server starting...")
    
    try:
        mcp.run(transport=args.transport)
    except Exception as e:
        logger.error(f"[ERROR] Server failed to start: {e}")
        raise
