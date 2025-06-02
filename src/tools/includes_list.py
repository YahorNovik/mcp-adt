# tools/includes_list.py

import re
from typing import Dict, List, Any, Set, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session_with_timeout, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_includes_list_definition = {
    "name": "get_includes_list",
    "description": "📋 INCLUDE INVENTORY: Recursively discover and list ALL include files within an ABAP program or include. Performs code analysis to find include statements and builds a complete hierarchy.",
    "parameters": {
        "type": "object",
        "properties": {
            "object_name": {
                "type": "string",
                "description": "Name of the ABAP program or include to analyze for nested includes"
            },
            "object_type": {
                "type": "string",
                "enum": ["program", "include"],
                "description": "Type of the ABAP object (program or include)"
            }
        },
        "required": ["object_name", "object_type"]
    }
}

async def _fetch_source(name: str, object_type: str) -> Optional[str]:
    """
    Fetch source code for a program or include.
    """
    session = make_session_with_timeout("default")
    base_url = SAP_URL.rstrip('/')
    upper_name = name.upper()
    
    if object_type == 'program':
        url = f"{base_url}/sap/bc/adt/programs/programs/{upper_name}/source/main"
    else:  # 'include'
        url = f"{base_url}/sap/bc/adt/programs/includes/{upper_name}/source/main"
    
    try:
        response = session.get(
            url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "text/plain", "Content-Type": "application/octet-stream"}
        )
        
        if response.status_code == 200 and response.text:
            return response.text
        return None
        
    except HTTPError as e:
        if e.response.status_code == 404:
            # Expected case if include doesn't exist
            return None
        print(f"Failed to fetch source for {object_type} {upper_name}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching source for {object_type} {upper_name}: {e}")
        return None

def _parse_includes(source_code: str) -> List[str]:
    """
    Parse INCLUDE statements from ABAP source code.
    Enhanced parsing logic to handle various INCLUDE statement formats.
    """
    includes = []
    
    # Split code into lines and analyze each line separately
    lines = source_code.split('\n')
    
    for i, line in enumerate(lines):
        # Remove all spaces and tabs for analysis
        clean_line = re.sub(r'\s+', ' ', line).strip().upper()
        
        # Check if line starts with INCLUDE
        if clean_line.startswith('INCLUDE ') and '.' in clean_line:
            # Extract name between INCLUDE and dot
            match = re.match(r'^INCLUDE\s+([A-Z0-9_<>\']+)\s*\.', clean_line)
            if match:
                include_name = match.group(1)
                # Normalize include name: remove <, >, ' symbols
                include_name = re.sub(r'[<>\']', '', include_name)
                if include_name not in includes:
                    includes.append(include_name)
                    print(f"DEBUG: Found include: {include_name} from line {i+1}: {line.strip()}")
    
    return includes

async def _find_includes_recursive(
    object_name: str,
    object_type: str,
    all_found_includes: Set[str],
    visited: Set[str]
) -> None:
    """
    Recursively find all includes within an object.
    """
    upper_object_name = object_name.upper()
    visited_key = f"{object_type}:{upper_object_name}"
    
    if visited_key in visited:
        return  # Already processed or in a processing cycle
    
    visited.add(visited_key)
    
    source_code = await _fetch_source(upper_object_name, object_type)
    if not source_code:
        # If source couldn't be fetched, stop recursion for this path
        return
    
    direct_includes = _parse_includes(source_code)
    for include_name in direct_includes:
        # Add to the global list of found includes
        all_found_includes.add(include_name)
        # Recursively find includes within this newly found include
        # All subsequent includes are of type 'include'
        await _find_includes_recursive(include_name, 'include', all_found_includes, visited)

def get_includes_list(object_name: str, object_type: str) -> Dict[str, Any]:
    """
    Recursively retrieve all includes within a given ABAP program or include.
    
    Args:
        object_name: Name of the ABAP program or include
        object_type: Type of object ('program' or 'include')
        
    Returns:
        Dictionary with includes list and metadata
    """
    print(f"Getting includes list for {object_type}: {object_name}")
    
    if not object_name:
        raise ValueError("object_name is required")
    
    if object_type not in ['program', 'include']:
        raise ValueError("object_type must be either 'program' or 'include'")
    
    try:
        all_found_includes = set()
        visited = set()  # To handle cyclic dependencies and avoid redundant fetches
        
        # Start recursive include search
        import asyncio
        asyncio.run(_find_includes_recursive(object_name, object_type, all_found_includes, visited))
        
        # Create response
        includes_list = sorted(list(all_found_includes))
        
        if includes_list:
            response_text = f"Found {len(includes_list)} includes in {object_type} '{object_name}':\n" + '\n'.join(includes_list)
        else:
            response_text = f"No includes found in {object_type} '{object_name}'."
        
        return {
            "object_name": object_name,
            "object_type": object_type,
            "includes_count": len(includes_list),
            "includes": includes_list,
            "response_text": response_text
        }
        
    except Exception as e:
        raise ConnectionError(f"Error retrieving includes list: {e}") from e
