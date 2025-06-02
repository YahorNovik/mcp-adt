# tools/enhancements.py

import base64
import re
from typing import Dict, List, Any, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session_with_timeout, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_enhancements_definition = {
    "name": "get_enhancements",
    "description": "🔍 ENHANCEMENT ANALYSIS: Retrieve and analyze enhancement implementations in ABAP programs or includes. Automatically detects object type and extracts enhancement source code. Use include_nested=true for COMPREHENSIVE RECURSIVE SEARCH across all nested includes.",
    "parameters": {
        "type": "object",
        "properties": {
            "object_name": {
                "type": "string",
                "description": "Name of the ABAP program or include (e.g. 'RM07DOCS' for program, 'RM07DOCS_F01' for include)"
            },
            "program": {
                "type": "string",
                "description": "Optional: For includes, manually specify the parent program name if automatic context detection fails (e.g., 'SAPMV45A')"
            },
            "include_nested": {
                "type": "boolean",
                "description": "⭐ RECURSIVE ENHANCEMENT SEARCH: If true, performs comprehensive analysis - searches for enhancements in the main object AND all nested includes recursively. Perfect for complete enhancement audit of entire program hierarchy. Default is false (single object only)."
            }
        },
        "required": ["object_name"]
    }
}

class EnhancementImplementation:
    """Class representing an enhancement implementation."""
    def __init__(self, name: str, type_: str, source_code: Optional[str] = None, description: Optional[str] = None):
        self.name = name
        self.type = type_
        self.source_code = source_code
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "source_code": self.source_code,
            "description": self.description
        }

def _parse_enhancements_from_xml(xml_data: str) -> List[EnhancementImplementation]:
    """
    Parse enhancement XML to extract enhancement implementations with their source code.
    """
    enhancements = []
    
    try:
        # Extract <enh:source> elements which contain the base64 encoded enhancement source code
        source_regex = r'<enh:source[^>]*>([^<]*)</enh:source>'
        matches = re.finditer(source_regex, xml_data)
        
        index = 0
        for match in matches:
            enhancement = EnhancementImplementation(
                name=f"enhancement_{index + 1}",  # Default name if not found in attributes
                type_="enhancement"
            )
            
            # Try to find enhancement name and type from parent elements or attributes
            source_start = match.start()
            # Look backwards for parent enhancement element with name/type attributes
            before_source = xml_data[:source_start]
            
            name_match = re.search(r'adtcore:name="([^"]*)"[^>]*$', before_source)
            type_match = re.search(r'adtcore:type="([^"]*)"[^>]*$', before_source)
            
            if name_match and name_match.group(1):
                enhancement.name = name_match.group(1)
            
            if type_match and type_match.group(1):
                enhancement.type = type_match.group(1)
            
            # Extract and decode the base64 source code
            base64_source = match.group(1)
            if base64_source:
                try:
                    # Decode base64 source code
                    decoded_source = base64.b64decode(base64_source).decode('utf-8')
                    enhancement.source_code = decoded_source
                except Exception as decode_error:
                    print(f"Failed to decode source code for enhancement {enhancement.name}: {decode_error}")
                    enhancement.source_code = base64_source  # Keep original if decode fails
            
            enhancements.append(enhancement)
            index += 1
        
        print(f"Parsed {len(enhancements)} enhancement implementations")
        return enhancements
        
    except Exception as parse_error:
        print(f"Failed to parse enhancement XML: {parse_error}")
        return []

def _determine_object_type_and_path(object_name: str, manual_program_context: Optional[str] = None, session=None) -> Dict[str, Any]:
    """
    Determine if an object is a program, include, or class and return appropriate URL path.
    """
    base_url = SAP_URL.rstrip('/')
    
    try:
        # First try as a class
        class_url = f"{base_url}/sap/bc/adt/oo/classes/{object_name}"
        try:
            response = session.get(
                class_url,
                params={"sap-client": SAP_CLIENT},
                headers={"Accept": "application/vnd.sap.adt.oo.classes.v4+xml"}
            )
            if response.status_code == 200:
                print(f"{object_name} is a class")
                return {
                    "type": "class",
                    "base_path": f"/sap/bc/adt/oo/classes/{object_name}/source/main/enhancements/elements"
                }
        except Exception as class_error:
            print(f"{object_name} is not a class, trying as program...")
        
        # Try as a program
        program_url = f"{base_url}/sap/bc/adt/programs/programs/{object_name}"
        try:
            response = session.get(
                program_url,
                params={"sap-client": SAP_CLIENT},
                headers={"Accept": "application/vnd.sap.adt.programs.v3+xml"}
            )
            if response.status_code == 200:
                print(f"{object_name} is a program")
                return {
                    "type": "program",
                    "base_path": f"/sap/bc/adt/programs/programs/{object_name}/source/main/enhancements/elements"
                }
        except Exception as program_error:
            print(f"{object_name} is not a program, trying as include...")
        
        # Try as include
        include_url = f"{base_url}/sap/bc/adt/programs/includes/{object_name}"
        response = session.get(
            include_url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "application/vnd.sap.adt.programs.includes.v2+xml"}
        )
        
        if response.status_code == 200:
            print(f"{object_name} is an include")
            
            context = None
            # Use manual program context if provided
            if manual_program_context:
                context = f"/sap/bc/adt/programs/programs/{manual_program_context}"
                print(f"Using manual program context for include {object_name}: {context}")
            else:
                # Auto-determine context from metadata
                xml_data = response.text
                context_match = re.search(r'include:contextRef[^>]+adtcore:uri="([^"]+)"', xml_data)
                if context_match and context_match.group(1):
                    context = context_match.group(1)
                    print(f"Found auto-determined context for include {object_name}: {context}")
                else:
                    raise AdtError(
                        400,
                        f"Could not determine parent program context for include: {object_name}. "
                        f"No contextRef found in metadata. Consider providing the 'program' parameter manually."
                    )
            
            return {
                "type": "include",
                "base_path": f"/sap/bc/adt/programs/includes/{object_name}/source/main/enhancements/elements",
                "context": context
            }
        
        raise AdtError(
            400,
            f"Could not determine object type for: {object_name}. "
            f"Object is neither a valid class, program, nor include."
        )
        
    except Exception as error:
        if isinstance(error, AdtError):
            raise error
        print(f"Failed to determine object type for {object_name}: {error}")
        raise AdtError(
            400,
            f"Failed to determine object type for: {object_name}. {str(error)}"
        )

def _get_enhancements_for_single_object(object_name: str, manual_program_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Gets enhancements for a single object (program or include).
    """
    print(f"Getting enhancements for single object: {object_name}")
    if manual_program_context:
        print(f"With manual program context: {manual_program_context}")
    
    # Use csrf timeout for object type determination
    csrf_session = make_session_with_timeout("csrf")
    
    # Determine object type and get appropriate path and context
    object_info = _determine_object_type_and_path(object_name, manual_program_context, csrf_session)
    
    # Build URL based on object type
    base_url = SAP_URL.rstrip('/')
    url = f"{base_url}{object_info['base_path']}"
    
    # Add context parameter only for includes
    if object_info["type"] == "include" and object_info.get("context"):
        url += f"?context={object_info['context']}"
        print(f"Using context for include: {object_info['context']}")
    
    print(f"Final enhancement URL: {url}")
    
    # Make the request with default timeout
    default_session = make_session_with_timeout("default")
    response = default_session.get(
        url,
        params={"sap-client": SAP_CLIENT},
        headers={"Accept": "application/vnd.sap.adt.enhancement.v1+xml"}
    )
    
    response.raise_for_status()
    
    if response.status_code == 200 and response.text:
        # Parse the XML to extract enhancement implementations
        enhancements = _parse_enhancements_from_xml(response.text)
        
        enhancement_response = {
            "object_name": object_name,
            "object_type": object_info["type"],
            "context": object_info.get("context"),
            "enhancements": [enh.to_dict() for enh in enhancements],
            "enhancement_count": len(enhancements),
            "raw_xml": response.text  # Include raw XML for debugging if needed
        }
        
        return enhancement_response
    else:
        raise AdtError(response.status_code, f"Failed to retrieve enhancements for {object_name}. Status: {response.status_code}")


def get_enhancements(object_name: str, program: Optional[str] = None, include_nested: bool = False) -> Dict[str, Any]:
    """
    Retrieve enhancement implementations for ABAP programs/includes.
    Automatically determines if object is a program or include and handles accordingly.
    
    Args:
        object_name: Name of the ABAP object
        program: Optional manual program context for includes
        include_nested: If true, also searches enhancements in all nested includes recursively
    """
    print(f"Getting enhancements for object: {object_name}")
    if program:
        print(f"With manual program context: {program}")
    print(f"Include nested: {include_nested}")
    
    if not object_name:
        raise ValueError("object_name is required")

    # Use csrf timeout for object type determination
    csrf_session = make_session_with_timeout("csrf")
    
    try:
        # Get enhancements for the main object
        main_enhancement_response = _get_enhancements_for_single_object(object_name, program)
        
        if not include_nested:
            # Return only main object enhancements
            return main_enhancement_response
        
        # If include_nested is true, also get enhancements from all nested includes
        print('Searching for nested includes and their enhancements...')
        
        # Import includes_list function
        from .includes_list import get_includes_list
        
        # Get all includes recursively
        includes_result = get_includes_list(object_name, main_enhancement_response["object_type"])
        includes_list = includes_result.get("includes", [])
        
        print(f"Found {len(includes_list)} nested includes: {includes_list}")
        
        # Collect all enhancement responses
        all_enhancement_responses = [main_enhancement_response]
        
        # Get enhancements for each include
        for include_name in includes_list:
            try:
                print(f"Getting enhancements for nested include: {include_name}")
                include_enhancements = _get_enhancements_for_single_object(include_name, program)
                all_enhancement_responses.append(include_enhancements)
            except Exception as error:
                print(f"Failed to get enhancements for include {include_name}: {error}")
                # Continue with other includes even if one fails
        
        # Create combined response
        total_enhancements = sum(resp["enhancement_count"] for resp in all_enhancement_responses)
        
        combined_response = {
            "main_object": {
                "name": object_name,
                "type": main_enhancement_response["object_type"]
            },
            "include_nested": True,
            "total_objects_analyzed": len(all_enhancement_responses),
            "total_enhancements_found": total_enhancements,
            "objects": all_enhancement_responses
        }
        
        return combined_response
            
    except HTTPError as e:
        if e.response.status_code == 404:
            raise AdtError(404, f"Enhancements not found for object '{object_name}'") from e
        raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error retrieving enhancements: {e}") from e
