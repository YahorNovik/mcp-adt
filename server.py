from mcp.server.fastmcp import FastMCP  # Import FastMCP, the quickstart server base

from src.tools.function_group_source import get_function_group_source
from src.tools.cds_source import get_cds_source
from src.tools.class_source import get_class_source
from src.tools.behavior_definition_source import get_behavior_definition_source
from src.tools.function_source import get_function_source
from src.tools.include_source import get_include_source
from src.tools.interface_source import  get_interface_source
from src.tools.package_structure import  get_package_structure
from src.tools.program_source import get_program_source
from src.tools.structure_source import get_structure_source
from src.tools.table_source import get_table_source
from src.tools.transaction_properties import get_transaction_properties
from src.tools.type_info import get_type_info
from src.tools.search_objects import get_search_objects
from src.tools.usage_references import get_usage_references
from src.tools.cds_source import get_cds_source
from src.tools.metadata_extension_source import get_metadata_extension_source

from dotenv import load_dotenv

mcp = FastMCP("ADT Server")  # Initialize an MCP server instance with a descriptive name

@mcp.tool()
def get_function_group_source_mcp(function_group: str) -> list[str]:
   return get_behavior_definition_source(function_group)

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
    return get_function_source(function_group, function_name)
    """ Tool: get_function_source
         Description:
           Retrieve source code lines for an ABAP function module via ADT,
           with XML and text fallback.
         Parameters (object):
           • function_group (string) - Function group name (e.g. ZFUNC_GROUP)
           • function_name  (string) - Function module name (e.g. ZFUNC_MODULE)
        Required:
           [ "function_group", "function_name" ]"""
    

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
    return get_search_objects(query, max_results=10)

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

if __name__ == "__main__":
    load_dotenv()      
    import os

    host = os.getenv("HOST") or "0.0.0.0"
    port = os.getenv("PORT") or "8080"
    print("host:", host)
    print("port:", port)

    mcp.run(transport="http", host=host, port=port)
